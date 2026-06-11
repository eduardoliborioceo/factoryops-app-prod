import io
import logging
import os
import zipfile
from datetime import date
from typing import Optional

import pandas as pd
import requests

from app.repositories import rh_transporte_repository as repo

logger = logging.getLogger(__name__)

_UA = "FactoryOps-ANP/1.0 (rh@venttos.com.br)"
_CKAN_API = "https://dados.gov.br/api/3/action/package_show"
_DATASET_ID = "serie-historica-de-precos-de-combustiveis-e-de-glp"
_ANP_BASE = (
    "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia"
    "/precos/precos-revenda-e-de-distribuicao-combustiveis"
    "/serie-historica-do-levantamento-de-precos"
)

_PRODUCT_MAP = {
    "GASOLINA COMUM":     "gasolina",
    "GASOLINA ADITIVADA": "gasolina",
    "OLEO DIESEL":        "diesel",
    "OLEO DIESEL S10":    "diesel_s10",
    "ETANOL HIDRATADO":   "etanol",
    "ETANOL":             "etanol",
}

_TIPO_TO_PRODUTOS: dict = {}
for _prod, _tipo in _PRODUCT_MAP.items():
    _TIPO_TO_PRODUTOS.setdefault(_tipo, []).append(_prod)


def _discover_urls(ano: int) -> dict:
    # Env var overrides take priority
    overrides = {
        "gasolina_etanol": os.environ.get("ANP_GASOLINA_URL", ""),
        "diesel":          os.environ.get("ANP_DIESEL_URL", ""),
    }
    if all(overrides.values()):
        return overrides

    # Try dados.gov.br CKAN API
    try:
        r = requests.get(
            _CKAN_API,
            params={"id": _DATASET_ID},
            headers={"User-Agent": _UA},
            timeout=12,
        )
        if r.ok:
            resources = r.json().get("result", {}).get("resources", [])
            found: dict = {}
            for res in resources:
                name = res.get("name", "").lower()
                url = res.get("url", "")
                if not url or str(ano) not in name:
                    continue
                if ("gasolina" in name or "etanol" in name) and "gasolina_etanol" not in found:
                    found["gasolina_etanol"] = url
                if "diesel" in name and "gasolina" not in name and "diesel" not in found:
                    found["diesel"] = url
            if found:
                return found
    except Exception as exc:
        logger.warning("CKAN API indisponível: %s", exc)

    # Direct URL construction fallback
    return {
        "gasolina_etanol": f"{_ANP_BASE}/gasolina-e-etanol-{ano}.zip",
        "diesel":          f"{_ANP_BASE}/diesel-{ano}.zip",
    }


def _download(url: str) -> io.BytesIO:
    r = requests.get(url, headers={"User-Agent": _UA}, timeout=180, stream=True)
    r.raise_for_status()
    content = io.BytesIO(r.content)

    is_zip = (
        url.lower().endswith(".zip")
        or "application/zip" in r.headers.get("content-type", "")
        or "application/octet-stream" in r.headers.get("content-type", "")
    )
    if is_zip:
        with zipfile.ZipFile(content) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError("ZIP da ANP não contém CSV")
            return io.BytesIO(zf.read(csv_names[0]))

    return content


def _normalize(series: "pd.Series") -> "pd.Series":
    return (
        series.str.strip()
        .str.upper()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("ascii")
    )


def _parse_anp_csv(stream: io.BytesIO) -> "pd.DataFrame":
    chunks = []
    for chunk in pd.read_csv(
        stream,
        sep=";",
        encoding="latin-1",
        dtype=str,
        chunksize=30_000,
        on_bad_lines="skip",
    ):
        chunk.columns = chunk.columns.str.strip()
        estado_col = next((c for c in chunk.columns if "estado" in c.lower() and "sigla" in c.lower()), None)
        mun_col    = next((c for c in chunk.columns if "municipio" in c.lower()), None)
        prod_col   = next((c for c in chunk.columns if "produto" in c.lower()), None)
        data_col   = next((c for c in chunk.columns if "data" in c.lower() and "coleta" in c.lower()), None)
        venda_col  = next((c for c in chunk.columns if "valor" in c.lower() and "venda" in c.lower()), None)

        if not all([estado_col, mun_col, prod_col, data_col, venda_col]):
            continue

        mask = (
            (chunk[estado_col].str.strip() == "AM") &
            (chunk[mun_col].str.strip().str.upper() == "MANAUS")
        )
        filtered = chunk[mask][[prod_col, data_col, venda_col]].copy()
        filtered.columns = ["Produto", "Data", "Valor"]
        if not filtered.empty:
            chunks.append(filtered)

    if not chunks:
        return pd.DataFrame(columns=["Produto", "Data", "Valor"])

    df = pd.concat(chunks, ignore_index=True)
    df["Produto_norm"] = _normalize(df["Produto"])
    df["Valor"] = pd.to_numeric(
        df["Valor"].str.replace(",", ".", regex=False), errors="coerce"
    )
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
    return df.dropna(subset=["Valor", "Data"])


def buscar_precos_manaus(ano: Optional[int] = None) -> dict:
    """
    Downloads and parses the ANP weekly fuel price data for Manaus/AM.
    Returns {tipo: preco_mediano, 'semana': date, 'fonte_url': str}.
    Raises RuntimeError if data cannot be obtained.
    """
    if ano is None:
        ano = date.today().year

    urls = _discover_urls(ano)
    result: dict = {}
    semana_ref: Optional[date] = None
    fonte_url = ""

    for key, url in urls.items():
        if not url:
            continue
        try:
            csv_bytes = _download(url)
            df = _parse_anp_csv(csv_bytes)
            if df.empty:
                continue

            fonte_url = url
            semana_max = df["Data"].max()
            df_semana = df[df["Data"] >= semana_max - pd.Timedelta(days=6)]

            if semana_ref is None or semana_max.date() > semana_ref:
                semana_ref = semana_max.date()

            for tipo, produtos in _TIPO_TO_PRODUTOS.items():
                subset = df_semana[df_semana["Produto_norm"].isin(produtos)]
                if subset.empty or tipo in result:
                    continue
                result[tipo] = round(float(subset["Valor"].median()), 3)

        except Exception as exc:
            logger.warning("Falha ao processar ANP URL %s: %s", url, exc)
            continue

    if not result:
        raise RuntimeError(
            "Nenhum dado de Manaus/AM encontrado. "
            "Verifique ANP_GASOLINA_URL e ANP_DIESEL_URL ou tente novamente mais tarde."
        )

    result["semana"] = semana_ref
    result["fonte_url"] = fonte_url
    return result


def sincronizar_precos_anp(ano: Optional[int] = None) -> dict:
    """
    Downloads ANP data, updates rh_combustivel_config, and records a sync log entry.
    Returns a summary dict with precos_atualizados, semana_referencia, tipos.
    """
    try:
        precos = buscar_precos_manaus(ano)
    except Exception as exc:
        repo.criar_anp_sync_log(
            status="erro",
            precos_atualizados=0,
            semana_referencia=None,
            fonte_url=None,
            erro=str(exc),
        )
        raise

    semana = precos.pop("semana", None)
    fonte_url = precos.pop("fonte_url", "anp")
    atualizados = 0

    for tipo, preco in precos.items():
        repo.upsert_preco_combustivel(
            tipo=tipo,
            preco_litro=preco,
            fonte=f"anp_sicom",
            data_referencia=semana,
        )
        atualizados += 1

    repo.criar_anp_sync_log(
        status="sucesso",
        precos_atualizados=atualizados,
        semana_referencia=semana,
        fonte_url=fonte_url[:500] if fonte_url else None,
        erro=None,
    )

    return {
        "precos_atualizados": atualizados,
        "semana_referencia":  str(semana) if semana else None,
        "tipos":              list(precos.keys()),
    }
