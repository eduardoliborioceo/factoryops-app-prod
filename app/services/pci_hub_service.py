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

    todos = turno_repo.listar()

    por_turno: dict[str, list] = defaultdict(list)
    for row in todos:
        nome = row["turno"].replace("§", "º").replace("°", "º")
        por_turno[nome].append(row)

    turno_ativo = None
    for nome, intervals in por_turno.items():
        # Usar o primeiro e último intervalo por ordem — não min/max dos horários,
        # pois turnos que cruzam meia-noite têm hora_inicio=00:xx < hora_inicio=16:xx
        sorted_ivs = sorted(intervals, key=lambda x: x["ordem"])
        inicio = sorted_ivs[0]["hora_inicio"]
        fim    = sorted_ivs[-1]["hora_fim"]
        if _em_intervalo(hora_atual, inicio, fim):
            turno_ativo = nome
            break

    intervalos = []
    if turno_ativo:
        for iv in sorted(por_turno[turno_ativo], key=lambda x: x["ordem"]):
            intervalos.append({
                "ordem": iv["ordem"],
                "hora_inicio": iv["hora_inicio"].strftime("%H:%M"),
                "hora_fim": iv["hora_fim"].strftime("%H:%M"),
                "atual": _em_intervalo(hora_atual, iv["hora_inicio"], iv["hora_fim"]),
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
        hora_ini = iv["hora_inicio"]
        hora_fim = iv["hora_fim"]
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
