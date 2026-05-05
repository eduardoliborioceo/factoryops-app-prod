from app.repositories import linha_lider_repository as repo

TURNOS_VALIDOS = ["1º Turno", "2º Turno", "3º Turno"]


def listar_por_setor() -> dict:
    registros = repo.listar()
    agrupado: dict = {}
    for r in registros:
        agrupado.setdefault(r["setor"], []).append(r)
    return agrupado


def listar_por_filial_setor() -> dict:
    registros = repo.listar_com_filial()
    resultado: dict = {}
    for r in registros:
        filial = r.get("filial") or "Geral"
        resultado.setdefault(filial, {}).setdefault(r["setor"], []).append(dict(r))
    return resultado


def buscar(setor: str, linha: str, turno: str) -> dict | None:
    return repo.buscar(setor, linha, turno)


def salvar(form_data: dict) -> None:
    setor = (form_data.get("setor") or "").strip()
    linha = (form_data.get("linha") or "").strip()
    turno = (form_data.get("turno") or "").strip()
    lider = (form_data.get("lider") or "").strip()

    if not setor or not linha or not turno:
        raise ValueError("Setor, linha e turno são obrigatórios.")

    if turno not in TURNOS_VALIDOS:
        raise ValueError(f"Turno inválido: {turno}")

    try:
        hc = int(form_data.get("hc") or 0)
        if hc < 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("HC deve ser um número inteiro não negativo.")

    repo.salvar(setor, linha, turno, lider, hc)


def excluir(setor: str, linha: str, turno: str) -> None:
    if not setor or not linha or not turno:
        raise ValueError("Setor, linha e turno são obrigatórios.")
    repo.excluir(setor, linha, turno)
