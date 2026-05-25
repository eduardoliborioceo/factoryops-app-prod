"""
Sincronizador automático de produção - FactoryOps
Rode com pythonw.exe para operação silenciosa (sem janela):
    pythonw.exe sincronizador.py

Lê configurações do arquivo .env na mesma pasta.
Grava log em sincronizador.log (rotacionado automaticamente).
"""

import os
import time
import json
import socket
import logging
import requests
from datetime import datetime, timezone, timedelta, date
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VENTTOS_API_URL     = os.environ.get("VENTTOS_API_URL", "").rstrip("/")
VENTTOS_MES_API_URL = os.environ.get("VENTTOS_MES_API_URL", "").rstrip("/")
RAILWAY_URL         = os.environ.get("RAILWAY_URL", "").rstrip("/")
SYNC_API_KEY        = os.environ.get("SYNC_API_KEY", "")

MANAUS        = timezone(timedelta(hours=-4))
HORA_INICIO   = (6, 30)
HORA_FIM      = (4, 30)
INTERVALO_MIN = 30

_LOCK_PORT = 47832

_BASE_DIR = Path(__file__).parent
_LOG_PATH = _BASE_DIR / "sincronizador.log"

_handler = RotatingFileHandler(
    _LOG_PATH, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
logging.basicConfig(
    handlers=[_handler],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("sinc")


def _instancia_ja_rodando() -> bool:
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        _lock_socket.bind(("127.0.0.1", _LOCK_PORT))
        _lock_socket.listen(1)
        import atexit
        atexit.register(_lock_socket.close)
        return False
    except OSError:
        return True


def _agora() -> datetime:
    return datetime.now(MANAUS)


def _dentro_do_horario(dt: datetime) -> bool:
    minutos = dt.hour * 60 + dt.minute
    inicio  = HORA_INICIO[0] * 60 + HORA_INICIO[1]
    fim     = HORA_FIM[0]    * 60 + HORA_FIM[1]
    return not (fim <= minutos < inicio)


def _proxima_execucao(dt: datetime) -> datetime:
    if dt.minute < 30:
        return dt.replace(minute=30, second=5, microsecond=0)
    return (dt + timedelta(hours=1)).replace(minute=0, second=5, microsecond=0)


def _extrair_hora(iso: str) -> str:
    return iso[11:16] if iso and len(iso) >= 16 else ""


def _normalizar_coletada(r: dict) -> dict:
    return {
        "id":               r.get("id"),
        "data":             (r.get("data", "")[:10] or None),
        "setor":            r.get("setor", ""),
        "linha":            r.get("linha", ""),
        "turno":            r.get("turno", ""),
        "semana":           r.get("semana"),
        "modelo":           r.get("modelos", ""),
        "familia":          r.get("familia", ""),
        "hora_inicio":      _extrair_hora(r.get("inicio", "")),
        "hora_fim":         _extrair_hora(r.get("final", "")),
        "intervalo":        r.get("intervalo_tempo", ""),
        "producao_real":    r.get("producao_real", 0),
        "qtd_perda":        r.get("qtd_perda", 0),
        "defeitos":         r.get("quantidade_defeitos", 0),
        "parada_seg":       r.get("parada_em_seg"),
        "codigo_parada":    r.get("codigo_de_parada"),
        "descricao_parada": r.get("descricao_da_parada"),
        "observacao":       r.get("observacao"),
    }


def _normalizar_mes(r: dict) -> dict:
    return {
        "id":               r.get("id"),
        "data":             (r.get("data", "")[:10] or None),
        "setor":            r.get("setor", ""),
        "linha":            r.get("linha", ""),
        "turno":            r.get("turno", ""),
        "semana":           r.get("semana"),
        "modelo":           r.get("modelo") or r.get("modelos", ""),
        "familia":          r.get("familia"),
        "hora_inicio":      _extrair_hora(r.get("hora_inicio") or r.get("inicio", "")),
        "hora_fim":         _extrair_hora(r.get("hora_fim")    or r.get("final", "")),
        "intervalo":        r.get("intervalo") or r.get("intervalo_tempo", ""),
        "producao_real":    r.get("producao_real", 0),
        "qtd_perda":        r.get("qtd_perda", 0),
        "defeitos":         r.get("defeitos") or r.get("quantidade_defeitos", 0),
        "meta":             r.get("meta") or r.get("meta_producao") or r.get("producao_programada"),
        "parada_seg":       r.get("parada_seg") or r.get("parada_em_seg"),
        "codigo_parada":    r.get("codigo_parada") or r.get("codigo_de_parada"),
        "descricao_parada": r.get("descricao_parada") or r.get("descricao_da_parada"),
        "observacao":       r.get("observacao"),
    }


def _buscar_coletada(de: str, ate: str) -> list:
    try:
        resp = requests.get(
            VENTTOS_API_URL,
            params={"dataInicial": de, "dataFinal": ate},
            timeout=30,
        )
        resp.raise_for_status()
        return [
            _normalizar_coletada(r)
            for r in resp.json()
            if de <= (r.get("data", "")[:10] or "") <= ate
        ]
    except Exception as e:
        log.error("Erro ao buscar coletada (%s → %s): %s", de, ate, e)
        return []


def _buscar_mes(de: str, ate: str) -> list:
    try:
        resp = requests.get(
            VENTTOS_MES_API_URL,
            params={"dataInicial": de, "dataFinal": ate},
            timeout=30,
        )
        resp.raise_for_status()
        return [_normalizar_mes(r) for r in resp.json()]
    except Exception as e:
        log.error("Erro ao buscar MES (%s → %s): %s", de, ate, e)
        return []


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {SYNC_API_KEY}",
        "Content-Type": "application/json",
    }


def _automatico_habilitado() -> bool:
    try:
        r = requests.get(f"{RAILWAY_URL}/api/sync/config", headers=_headers(), timeout=10)
        return r.json().get("automatico_habilitado", True)
    except Exception:
        return True


def _reportar(tipo: str, status: str, buscados: int, salvos: int, erros: int, mensagem: str = None):
    try:
        requests.post(
            f"{RAILWAY_URL}/api/sync/historico",
            headers=_headers(),
            json={
                "tipo": tipo,
                "status": status,
                "registros_buscados": buscados,
                "salvos": salvos,
                "erros": erros,
                "mensagem": mensagem,
            },
            timeout=10,
        )
    except Exception as e:
        log.warning("Falha ao reportar histórico: %s", e)


def _aguardar_job(rota_progresso: str, job_id: str, timeout_s: int = 120) -> dict:
    inicio = time.time()
    while time.time() - inicio < timeout_s:
        try:
            r = requests.get(
                f"{RAILWAY_URL}{rota_progresso}/{job_id}",
                headers=_headers(),
                timeout=10,
            )
            estado = r.json()
            if estado.get("status") in ("done", "error"):
                return estado
        except Exception:
            pass
        time.sleep(3)
    return {"status": "timeout"}


def _push(endpoint: str, rota_progresso: str, registros: list, tipo: str) -> None:
    if not registros:
        log.info("%s: nenhum registro para enviar.", tipo)
        _reportar(tipo, "skip", 0, 0, 0)
        return
    try:
        r = requests.post(
            f"{RAILWAY_URL}{endpoint}",
            headers=_headers(),
            data=json.dumps(registros, default=str),
            timeout=30,
        )
        if r.status_code != 200:
            msg = f"HTTP {r.status_code}"
            log.error("%s push falhou: %s — %s", tipo, msg, r.text[:200])
            _reportar(tipo, "error", len(registros), 0, 0, msg)
            return

        resposta = r.json()
        if "mensagem" in resposta:
            log.info("%s: %s", tipo, resposta["mensagem"])
            _reportar(tipo, "skip", len(registros), 0, 0)
            return

        job_id = resposta.get("job_id")
        estado = _aguardar_job(rota_progresso, job_id)
        salvos  = estado.get("salvos", 0) or 0
        erros   = estado.get("erros", 0) or 0
        status  = estado.get("status", "error")
        msg_job = estado.get("mensagem")

        log.info("%s: %d salvos, %d erros, status=%s", tipo, salvos, erros, status)
        if msg_job:
            log.error("%s erro do servidor: %s", tipo, msg_job)
        _reportar(tipo, status, len(registros), salvos, erros, msg_job)

    except Exception as e:
        log.error("%s push exception: %s", tipo, e)
        _reportar(tipo, "error", len(registros), 0, 0, str(e))


def _sincronizar():
    agora  = _agora()
    hoje   = str(agora.date())
    ontem  = str((agora - timedelta(days=1)).date())

    log.info("=== Sincronização iniciada ===")

    if VENTTOS_API_URL:
        registros = _buscar_coletada(ontem, hoje)
        log.info("Coletada: %d registros buscados (%s → %s)", len(registros), ontem, hoje)
        _push(
            "/api/sync/producao-coletada",
            "/api/sync/producao-coletada/progresso",
            registros,
            "coletada",
        )
    else:
        log.warning("VENTTOS_API_URL não configurada — coletada ignorada.")
        _reportar("coletada", "skip", 0, 0, 0, "VENTTOS_API_URL não configurada no .env")

    if VENTTOS_MES_API_URL:
        primeiro_dia = str(agora.replace(day=1).date())
        registros_mes = _buscar_mes(primeiro_dia, hoje)
        log.info("MES: %d registros buscados (%s → %s)", len(registros_mes), primeiro_dia, hoje)
        _push(
            "/api/sync/producao-mes",
            "/api/sync/producao-mes/progresso",
            registros_mes,
            "mes",
        )
    else:
        log.warning("VENTTOS_MES_API_URL não configurada — MES ignorado.")
        _reportar("mes", "skip", 0, 0, 0, "VENTTOS_MES_API_URL não configurada no .env")

    log.info("=== Sincronização concluída ===")


def main():
    if _instancia_ja_rodando():
        log.info("Outra instância já está rodando. Encerrando.")
        return

    if not SYNC_API_KEY:
        log.error("SYNC_API_KEY não configurada. Encerrando.")
        return
    if not RAILWAY_URL:
        log.error("RAILWAY_URL não configurada. Encerrando.")
        return
    if not VENTTOS_API_URL and not VENTTOS_MES_API_URL:
        log.error("Nenhuma API de origem configurada. Encerrando.")
        return

    log.info(
        "Sincronizador iniciado — janela %02d:%02d → %02d:%02d (Manaus), intervalo %d min.",
        HORA_INICIO[0], HORA_INICIO[1],
        HORA_FIM[0],    HORA_FIM[1],
        INTERVALO_MIN,
    )

    while True:
        agora   = _agora()
        proximo = _proxima_execucao(agora)
        espera  = max((proximo - agora).total_seconds(), 1)
        time.sleep(espera)

        agora = _agora()
        if not _dentro_do_horario(agora):
            log.debug(
                "Fora da janela (%02d:%02d) — aguardando próximo ciclo.",
                agora.hour, agora.minute,
            )
            continue

        if not _automatico_habilitado():
            log.info("Sincronização automática desabilitada pelo admin — ciclo ignorado.")
            continue

        try:
            _sincronizar()
        except Exception as e:
            log.exception("Erro inesperado na sincronização: %s", e)


if __name__ == "__main__":
    main()
