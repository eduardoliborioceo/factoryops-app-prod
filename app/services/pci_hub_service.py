from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from app.repositories import pci_hub_repository as repo

_TZ = ZoneInfo("America/Manaus")


def iniciar_sessao(
    linha: str,
    usuario: str,
    op: str,
    modelo: str,
    cliente: str,
    turno: str,
    meta_hora: int | None,
    qtd_por_caixa: int | None = None,
) -> dict:
    if not linha or not usuario or not op:
        raise ValueError("Linha, usuário e OP são obrigatórios.")
    return repo.criar_sessao(
        linha=linha.strip(),
        usuario=usuario.strip(),
        op=op.strip().upper(),
        modelo=modelo.strip() or None,
        cliente=cliente.strip() or None,
        turno=turno.strip() or None,
        meta_hora=int(meta_hora) if meta_hora else None,
        qtd_por_caixa=int(qtd_por_caixa) if qtd_por_caixa else None,
    )


def processar_scan(sessao_id: int, serial: str) -> tuple[dict, int]:
    serial = (serial or "").strip()
    if not serial:
        raise ValueError("Serial inválido.")
    scan, erro = repo.registrar_scan(sessao_id, serial)
    if erro == "duplicado":
        raise ValueError(f"Serial '{serial}' já foi bipado nesta sessão.")
    total = repo.contar_scans(sessao_id)
    return scan, total


def obter_scans(sessao_id: int) -> list:
    return repo.listar_scans(sessao_id)


def fechar_sessao(sessao_id: int) -> None:
    repo.fechar_sessao(sessao_id)


_CHAR_FIX = str.maketrans({"§": "º", "\xa7": "º", "°": "º"})


def _sanitizar(nome: str) -> str:
    return nome.translate(_CHAR_FIX) if nome else (nome or "")


def _to_time(val):
    """Converte qualquer representação de hora para datetime.time com segurança."""
    from datetime import time as _time
    if isinstance(val, _time):
        return val
    if hasattr(val, "hour"):
        return _time(val.hour, val.minute)
    parts = str(val).split(":")
    return _time(int(parts[0]), int(parts[1]))


def _em_intervalo(hora, ini, fim) -> bool:
    """Verifica se 'hora' está no intervalo [ini, fim), suportando cruzamento de meia-noite."""
    if ini <= fim:
        return ini <= hora < fim
    return hora >= ini or hora < fim


def detectar_turno() -> dict:
    from app.repositories import turno_config_repository as turno_repo

    agora = datetime.now(_TZ)
    hora_atual = agora.time()
    hora_str = agora.strftime("%H:%M")

    todos = turno_repo.listar()  # já ordenado por ordem

    # Consolida: primeira linha define hora_inicio, as demais atualizam hora_fim.
    # Padrão idêntico ao monitor_smd_service._consolidar_turnos (que funciona).
    consolidado: dict[str, dict] = {}
    for row in todos:
        nome = _sanitizar(row["turno"])
        if nome not in consolidado:
            consolidado[nome] = {
                "nome": nome,
                "hora_inicio": _to_time(row["hora_inicio"]),
                "hora_fim":    _to_time(row["hora_fim"]),
            }
        else:
            consolidado[nome]["hora_fim"] = _to_time(row["hora_fim"])

    turno_ativo = None
    for nome, t in consolidado.items():
        if _em_intervalo(hora_atual, t["hora_inicio"], t["hora_fim"]):
            turno_ativo = nome
            break

    intervalos = []
    if turno_ativo:
        intervalos_config = turno_repo.listar_por_turno(turno_ativo)
        for iv in intervalos_config:
            ini = _to_time(iv["hora_inicio"])
            fim = _to_time(iv["hora_fim"])
            intervalos.append({
                "ordem": iv["ordem"],
                "hora_inicio": ini.strftime("%H:%M"),
                "hora_fim":    fim.strftime("%H:%M"),
                "atual": _em_intervalo(hora_atual, ini, fim),
            })

    return {"turno": turno_ativo, "hora_atual": hora_str, "intervalos": intervalos}


def obter_intervalos_sessao(sessao_id: int) -> dict:
    from app.repositories import turno_config_repository as turno_repo

    sessao = repo.buscar_sessao(sessao_id)
    if not sessao:
        raise ValueError("Sessão não encontrada.")

    meta_hora = sessao.get("meta_hora")
    turno = sessao.get("turno")
    data = sessao.get("data")

    if not turno or not data:
        return {"meta_hora": meta_hora, "intervalos": []}

    intervalos_config = turno_repo.listar_por_turno(turno)
    hora_atual = datetime.now(_TZ).time()

    resultado = []
    for iv in intervalos_config:
        hora_ini = _to_time(iv["hora_inicio"])
        hora_fim = _to_time(iv["hora_fim"])
        total = repo.scans_no_intervalo(sessao_id, hora_ini, hora_fim)
        atual = _em_intervalo(hora_atual, hora_ini, hora_fim)
        resultado.append({
            "hora_inicio": hora_ini.strftime("%H:%M"),
            "hora_fim": hora_fim.strftime("%H:%M"),
            "ordem": iv["ordem"],
            "total": total,
            "atual": atual,
        })

    return {"meta_hora": meta_hora, "intervalos": resultado}
