from app.repositories import pci_revisao_repository as repo


def novo_relatorio(dados: dict, horas: list, defeitos: list) -> int:
    rel_id = repo.criar_relatorio(dados)
    repo.salvar_horas(rel_id, horas)
    repo.salvar_defeitos(rel_id, defeitos)
    return rel_id


def atualizar_relatorio(relatorio_id: int, dados: dict, horas: list, defeitos: list) -> None:
    repo.atualizar_cabecalho(relatorio_id, dados)
    repo.salvar_horas(relatorio_id, horas)
    repo.salvar_defeitos(relatorio_id, defeitos)


def obter_relatorio(relatorio_id: int) -> dict:
    rel = repo.buscar_relatorio(relatorio_id)
    if not rel:
        raise ValueError("Relatório não encontrado.")
    return rel


def listar(linha: str = "", data_ini: str = "", data_fim: str = "") -> list:
    return repo.listar_relatorios(linha, data_ini, data_fim)


def excluir(relatorio_id: int) -> None:
    repo.excluir_relatorio(relatorio_id)


def slots_padrao() -> list:
    return repo.slots_padrao()
