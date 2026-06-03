from datetime import date, timedelta
from app.repositories import producao_coletada_repository as pc_repo
from app.repositories import turno_config_repository as turno_repo
from app.repositories import modelos_repository as mod_repo


_FASES_VALIDAS = {"SMD", "PTH", "IM/PA"}
_SETORES_VALIDOS = {"VTE", "VTT", "SMD"}


def filtros_disponiveis(setor: str = "") -> dict:
    setores = pc_repo.setores_disponiveis() or ["VTE", "VTT"]
    linhas = pc_repo.linhas_disponiveis(setor) if setor else []
    turnos = turno_repo.listar()
    nomes_turnos = sorted({t["turno"] for t in turnos}) if turnos else []
    return {"setores": setores, "linhas": linhas, "turnos": nomes_turnos}


def linhas_do_setor(setor: str) -> list:
    return pc_repo.linhas_disponiveis(setor)


def modelos_autocomplete(termo: str) -> list:
    if not termo or len(termo) < 2:
        return []
    termo_upper = termo.strip().upper()
    todos = mod_repo.listar_modelos()
    return [
        {"codigo": m["codigo"], "fase": m.get("fase") or "", "setor": m.get("setor") or ""}
        for m in todos
        if termo_upper in (m["codigo"] or "").upper()
    ][:20]


def registrar(data_form: dict) -> None:
    data_str = (data_form.get("data") or "").strip()
    setor = (data_form.get("setor") or "").strip().upper()
    linha = (data_form.get("linha") or "").strip()
    turno = (data_form.get("turno") or "").strip()
    modelo = (data_form.get("modelo") or "").strip().upper()
    fase = (data_form.get("fase") or "").strip().upper()
    producao_raw = (data_form.get("producao_real") or "0").strip()
    perda_raw = (data_form.get("qtd_perda") or "0").strip()
    defeitos_raw = (data_form.get("defeitos") or "0").strip()
    observacao = (data_form.get("observacao") or "").strip() or None

    if not data_str:
        raise ValueError("Data é obrigatória.")
    try:
        data_obj = date.fromisoformat(data_str)
    except ValueError:
        raise ValueError("Data inválida.")
    if data_obj > date.today():
        raise ValueError("Não é possível registrar produção para datas futuras.")

    if not setor:
        raise ValueError("Setor é obrigatório.")
    if not linha:
        raise ValueError("Linha é obrigatória.")
    if not turno:
        raise ValueError("Turno é obrigatório.")
    if not modelo:
        raise ValueError("Modelo é obrigatório.")

    try:
        producao_real = int(producao_raw)
        qtd_perda = int(perda_raw) if perda_raw else 0
        defeitos = int(defeitos_raw) if defeitos_raw else 0
    except ValueError:
        raise ValueError("Quantidades devem ser números inteiros.")

    if producao_real < 0:
        raise ValueError("Produção não pode ser negativa.")
    if qtd_perda < 0 or defeitos < 0:
        raise ValueError("Perdas e defeitos não podem ser negativos.")
    if producao_real == 0 and qtd_perda == 0:
        raise ValueError("Informe ao menos a produção ou a quantidade de perda.")

    pc_repo.inserir_manual({
        "data": data_str,
        "setor": setor,
        "linha": linha,
        "turno": turno,
        "modelo": modelo,
        "producao_real": producao_real,
        "qtd_perda": qtd_perda,
        "defeitos": defeitos,
        "observacao": observacao,
    })


def listar_recentes(setor: str = "", linha: str = "", turno: str = "", dias: int = 7) -> list:
    data_final = date.today()
    data_inicial = data_final - timedelta(days=dias - 1)
    registros = pc_repo.listar(
        str(data_inicial), str(data_final),
        setor=setor, linha=linha, turno=turno,
    )
    return [r for r in registros if r.get("origem") == "manual"]


def excluir(registro_id: int) -> None:
    if not registro_id or registro_id <= 0:
        raise ValueError("ID de registro inválido.")
    pc_repo.excluir_manual(registro_id)
