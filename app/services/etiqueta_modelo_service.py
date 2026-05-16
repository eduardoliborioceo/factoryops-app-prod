from app.repositories import etiqueta_modelo_repository as repo


def listar_modelos() -> list:
    return repo.listar()


def salvar_modelo(nome: str, dados: dict) -> int:
    nome = nome.strip()
    if not nome:
        raise ValueError("Nome do modelo é obrigatório.")
    if len(nome) > 60:
        raise ValueError("Nome do modelo deve ter no máximo 60 caracteres.")
    return repo.salvar(nome, dados)


def excluir_modelo(modelo_id: int) -> None:
    repo.excluir(modelo_id)
