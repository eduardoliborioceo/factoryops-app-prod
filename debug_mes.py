"""
Debug do pipeline MES automatico — FactoryOps

Uso:
    python debug_mes.py                          (testa hoje)
    python debug_mes.py --data 2026-05-25        (data especifica)
    python debug_mes.py --mes                    (todo o mes corrente)
    python debug_mes.py --push                   (envia para Railway apos coletar)
    python debug_mes.py --log                    (exibe ultimas linhas do sincronizador.log)

Saida: imprime cada etapa do pipeline exatamente como o sincronizador executa.
"""

import os
import re
import sys
import json
import hashlib
import requests
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MES_URL      = os.environ.get("MES_URL", "http://192.168.1.32").rstrip("/")
RAILWAY_URL  = os.environ.get("RAILWAY_URL", "").rstrip("/")
SYNC_API_KEY = os.environ.get("SYNC_API_KEY", "")

FILIAIS_VALIDAS = {"VTE", "VTT"}
_MES_API_URL    = f"{MES_URL}/sfc-back/api/relatorio"
_MES_REFERER    = f"{MES_URL}/sfc/relatorios/linha"

_SEP = "─" * 60


def _titulo(texto: str) -> None:
    print(f"\n{_SEP}")
    print(f"  {texto}")
    print(_SEP)


def _ok(msg: str)   -> None: print(f"  [OK]  {msg}")
def _err(msg: str)  -> None: print(f"  [ERR] {msg}")
def _info(msg: str) -> None: print(f"  [   ] {msg}")


# ─── Helpers (identicos ao sincronizador) ─────────────────────────────────────

def _gerar_id_mes(data: str, linha: str, turno: str, produto: str) -> int:
    key    = f"mes-sum|{data}|{linha}|{turno}|{produto}"
    digest = hashlib.md5(key.encode()).hexdigest()
    return int(digest[:8], 16) % 1_000_000_000 + 1_000_000_001


def _calcular_semana(data_iso: str):
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").isocalendar()[1]
    except Exception:
        return None


def _to_int(s) -> int:
    try:
        return int(float(str(s).replace(",", ".").strip()))
    except (ValueError, AttributeError):
        return 0


def _extrair_turno_mes(turno_str: str) -> str:
    m = re.search(r"(\d)T", turno_str, re.IGNORECASE)
    if m:
        return f"{m.group(1)}º Turno"
    t = turno_str.upper()
    if re.search(r"3[°º]?\s*T", t): return "3º Turno"
    if re.search(r"2[°º]?\s*T", t): return "2º Turno"
    if re.search(r"1[°º]?\s*T", t): return "1º Turno"
    return ""


def _extrair_filial_linha(texto: str):
    texto = texto.strip()
    if " - " in texto:
        partes = texto.split(" - ", 1)
        filial = partes[0].strip()
        linha  = partes[1].strip()
    else:
        for f in FILIAIS_VALIDAS:
            if texto.startswith(f + "-"):
                filial = f
                linha  = texto[len(f) + 1:]
                break
        else:
            return None
    if filial not in FILIAIS_VALIDAS:
        return None
    return filial, linha


def _normalizar_modelo_mes(codigo: str):
    s = re.sub(r'^\d{2}-', '', codigo.strip())
    s = re.sub(r'[A-Z]{2,5}$', '', s)
    return s.strip() or None


# ─── Etapa 1: variaveis de ambiente ───────────────────────────────────────────

def checar_env() -> bool:
    _titulo("ETAPA 1 — Variaveis de ambiente")
    ok = True

    if MES_URL:
        _ok(f"MES_URL = {MES_URL}")
    else:
        _err("MES_URL nao configurada")
        ok = False

    if RAILWAY_URL:
        _ok(f"RAILWAY_URL = {RAILWAY_URL}")
    else:
        _err("RAILWAY_URL nao configurada")
        ok = False

    if SYNC_API_KEY:
        _ok(f"SYNC_API_KEY = {SYNC_API_KEY[:6]}...{SYNC_API_KEY[-4:]} ({len(SYNC_API_KEY)} chars)")
    else:
        _err("SYNC_API_KEY nao configurada")
        ok = False

    return ok


# ─── Etapa 2: conectividade MES ───────────────────────────────────────────────

def checar_conectividade_mes() -> bool:
    _titulo("ETAPA 2 — Conectividade com MES")
    base = MES_URL

    _info(f"Tentando GET {base} (timeout 10s)...")
    try:
        r = requests.get(base, timeout=10)
        _ok(f"GET {base} → HTTP {r.status_code}")
    except requests.exceptions.ConnectionError as e:
        _err(f"Conexao recusada ou host inacessivel: {e}")
        _info("Verifique se esta maquina tem acesso a rede do MES (192.168.1.x).")
        return False
    except requests.exceptions.Timeout:
        _err(f"Timeout ao conectar em {base}")
        _info("O servidor MES pode estar desligado ou firewall bloqueando.")
        return False
    except Exception as e:
        _err(f"Erro inesperado: {e}")
        return False

    _info(f"Tentando POST {_MES_API_URL} (endpoint real)...")
    hoje_fmt = datetime.today().strftime("%Y%m%d")
    payload  = {
        "procedure": "indicadores.listagem_linhas",
        "parametros": {
            "dataInicial": f"{hoje_fmt} 00:00:00",
            "dataFinal":   f"{hoje_fmt} 23:59:59",
        },
    }
    try:
        r = requests.post(
            _MES_API_URL,
            json=payload,
            headers={"Content-Type": "application/json;charset=UTF-8", "Referer": _MES_REFERER},
            timeout=15,
        )
        _ok(f"POST {_MES_API_URL} → HTTP {r.status_code}")
        return r.status_code == 200
    except requests.exceptions.ConnectionError as e:
        _err(f"Conexao recusada no endpoint da API: {e}")
        return False
    except requests.exceptions.Timeout:
        _err("Timeout no endpoint da API")
        return False
    except Exception as e:
        _err(f"Erro inesperado no endpoint: {e}")
        return False


# ─── Etapa 3: resposta bruta da API ───────────────────────────────────────────

def buscar_bruto(data_iso: str) -> list | None:
    _titulo(f"ETAPA 3 — Resposta bruta da API MES para {data_iso}")
    data_fmt = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%Y%m%d")
    payload  = {
        "procedure": "indicadores.listagem_linhas",
        "parametros": {
            "dataInicial": f"{data_fmt} 00:00:00",
            "dataFinal":   f"{data_fmt} 23:59:59",
        },
    }
    _info(f"POST {_MES_API_URL}")
    _info(f"Payload: {json.dumps(payload)}")

    try:
        resp = requests.post(
            _MES_API_URL,
            json=payload,
            headers={"Content-Type": "application/json;charset=UTF-8", "Referer": _MES_REFERER},
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as e:
        _err(f"Falha na requisicao: {e}")
        return None

    try:
        dados = resp.json()
    except Exception:
        _err(f"Resposta nao e JSON. Primeiros 500 chars:\n{resp.text[:500]}")
        return None

    _ok(f"Recebidos {len(dados)} itens brutos da API")

    if not dados:
        _err("API retornou lista vazia. O MES pode nao ter dados para esta data.")
        return dados

    print()
    print("  Primeiros 5 itens brutos:")
    for i, r in enumerate(dados[:5]):
        descricao = r.get("Descricao", "N/A")
        turno     = r.get("Turno", "N/A")
        produto   = r.get("CodProduto", "N/A")
        ok_val    = r.get("OK", "N/A")
        prog      = r.get("Programado", "N/A")
        print(f"  [{i}] Descricao={descricao!r:35} Turno={turno!r:30} Produto={produto!r:20} OK={ok_val} Prog={prog}")

    chaves = set()
    for r in dados:
        chaves.update(r.keys())
    _info(f"Chaves presentes na resposta: {sorted(chaves)}")

    return dados


# ─── Etapa 4: filtro e normalizacao ───────────────────────────────────────────

def filtrar_e_normalizar(dados_brutos: list, data_iso: str) -> list:
    _titulo(f"ETAPA 4 — Filtro e normalizacao ({data_iso})")

    descartados = []
    registros   = []

    for r in dados_brutos:
        descricao = r.get("Descricao", "")
        result    = _extrair_filial_linha(descricao)
        if not result:
            descartados.append(descricao)
            continue

        filial, linha = result
        turno   = _extrair_turno_mes(r.get("Turno", ""))
        modelo  = _normalizar_modelo_mes((r.get("CodProduto") or "").strip())

        registros.append({
            "id":            _gerar_id_mes(data_iso, linha, turno, modelo or ""),
            "data":          data_iso,
            "setor":         "",
            "linha":         linha,
            "turno":         turno,
            "semana":        _calcular_semana(data_iso),
            "modelo":        modelo,
            "familia":       None,
            "hora_inicio":   None,
            "hora_fim":      None,
            "intervalo":     None,
            "producao_real": _to_int(r.get("OK", 0)),
            "qtd_perda":     _to_int(r.get("FFALSA", 0)),
            "defeitos":      _to_int(r.get("NOK", 0)),
            "meta":          _to_int(r.get("Programado", 0)),
            "parada_seg":    None,
            "codigo_parada": None,
            "descricao_parada": None,
            "observacao":    None,
        })

    _ok(f"{len(registros)} registros aprovados no filtro")

    if descartados:
        _err(f"{len(descartados)} registros descartados pelo filtro de filial")
        print(f"  Filiais validas: {FILIAIS_VALIDAS}")
        print(f"  Exemplos descartados:")
        for d in list(set(descartados))[:10]:
            print(f"    {d!r}")
    else:
        _ok("Nenhum registro descartado pelo filtro")

    if registros:
        print()
        print(f"  Primeiros 5 registros normalizados:")
        for r in registros[:5]:
            print(f"  linha={r['linha']:20} turno={r['turno']:12} modelo={str(r['modelo'])[:20]:20} meta={r['meta']:5} prod={r['producao_real']:5} id={r['id']}")

    return registros


# ─── Etapa 5: push para Railway ───────────────────────────────────────────────

def push_railway(registros: list) -> None:
    _titulo("ETAPA 5 — Push para Railway")

    if not RAILWAY_URL or not SYNC_API_KEY:
        _err("RAILWAY_URL ou SYNC_API_KEY ausentes — push ignorado.")
        return

    headers = {
        "Authorization": f"Bearer {SYNC_API_KEY}",
        "Content-Type":  "application/json",
    }

    _info(f"POST {RAILWAY_URL}/api/sync/producao-mes com {len(registros)} registros...")
    try:
        r = requests.post(
            f"{RAILWAY_URL}/api/sync/producao-mes",
            headers=headers,
            data=json.dumps(registros, default=str),
            timeout=30,
        )
        _info(f"HTTP {r.status_code}")
        _info(f"Resposta: {r.text[:300]}")

        if r.status_code != 200:
            _err(f"Push falhou com HTTP {r.status_code}")
            return

        resposta = r.json()

        if "mensagem" in resposta:
            _ok(f"Railway disse: {resposta['mensagem']}")
            return

        job_id = resposta.get("job_id")
        if not job_id:
            _err(f"job_id ausente na resposta: {resposta}")
            return

        _ok(f"job_id={job_id} — aguardando conclusao...")

        import time
        inicio = time.time()
        while time.time() - inicio < 120:
            prog = requests.get(
                f"{RAILWAY_URL}/api/sync/producao-mes/progresso/{job_id}",
                headers=headers,
                timeout=10,
            )
            estado = prog.json()
            status = estado.get("status")
            _info(f"  status={status} salvos={estado.get('salvos',0)} erros={estado.get('erros',0)}")
            if status in ("done", "error"):
                if status == "done":
                    _ok(f"Import concluido: {estado.get('salvos',0)} salvos, {estado.get('erros',0)} erros")
                else:
                    _err(f"Import com erro: {estado.get('mensagem','?')}")
                break
            time.sleep(3)
        else:
            _err("Timeout aguardando job")

    except Exception as e:
        _err(f"Excecao no push: {e}")


# ─── Etapa 6: verificar Railway (GET config) ──────────────────────────────────

def checar_railway() -> None:
    _titulo("ETAPA 6 — Conectividade com Railway")

    if not RAILWAY_URL or not SYNC_API_KEY:
        _err("RAILWAY_URL ou SYNC_API_KEY ausentes — verificacao ignorada.")
        return

    headers = {"Authorization": f"Bearer {SYNC_API_KEY}"}
    try:
        r = requests.get(f"{RAILWAY_URL}/api/sync/config", headers=headers, timeout=10)
        _ok(f"GET /api/sync/config → HTTP {r.status_code}")
        _info(f"Resposta: {r.text[:200]}")
        cfg = r.json()
        if cfg.get("automatico_habilitado"):
            _ok("Sync automatico HABILITADO no Railway")
        else:
            _err("Sync automatico DESABILITADO no Railway — ciclos serao ignorados pelo sincronizador")
    except Exception as e:
        _err(f"Falha ao checar Railway: {e}")


# ─── Log do sincronizador ─────────────────────────────────────────────────────

def exibir_log(linhas: int = 50) -> None:
    _titulo(f"LOG — ultimas {linhas} linhas do sincronizador.log")
    log_path = Path(__file__).parent / "sincronizador.log"
    if not log_path.exists():
        _err(f"Arquivo nao encontrado: {log_path}")
        _info("O sincronizador ainda nao rodou nesta maquina.")
        return
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        todas = f.readlines()
    ultimas = todas[-linhas:] if len(todas) > linhas else todas
    for linha in ultimas:
        print(f"  {linha}", end="")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args  = sys.argv[1:]
    push  = "--push" in args
    mes   = "--mes"  in args
    exlog = "--log"  in args

    if "--data" in args:
        data_alvo = args[args.index("--data") + 1]
    else:
        data_alvo = str(date.today())

    print()
    print("=" * 60)
    print("  DEBUG — Pipeline MES automatico (FactoryOps)")
    print("=" * 60)

    if exlog:
        exibir_log(60)

    env_ok = checar_env()
    if not env_ok:
        print("\n  Corrija o .env e rode novamente.")
        sys.exit(1)

    mes_ok = checar_conectividade_mes()
    checar_railway()

    if not mes_ok:
        print("\n  MES inacessivel — impossivel continuar com a coleta.")
        sys.exit(1)

    if mes:
        hoje   = date.today()
        inicio = hoje.replace(day=1)
        datas  = []
        d = inicio
        while d <= hoje:
            datas.append(str(d))
            d += timedelta(days=1)
    else:
        datas = [data_alvo]

    todos_registros = []
    for data_iso in datas:
        dados_brutos = buscar_bruto(data_iso)
        if dados_brutos is None:
            continue
        registros = filtrar_e_normalizar(dados_brutos, data_iso)
        todos_registros.extend(registros)

    _titulo("RESUMO FINAL")
    _info(f"Datas processadas : {len(datas)}")
    _ok  (f"Total de registros: {len(todos_registros)}")

    if push and todos_registros:
        push_railway(todos_registros)
    elif push and not todos_registros:
        _err("Nenhum registro para enviar ao Railway.")

    if not push and todos_registros:
        _info("Use --push para enviar os registros ao Railway.")

    print()


if __name__ == "__main__":
    main()
