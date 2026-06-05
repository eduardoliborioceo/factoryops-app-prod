from app.repositories import pci_modelo_padrao_repository as repo


def listar() -> list:
    return repo.listar(ativo=True)


def obter(modelo_id: int) -> dict:
    m = repo.buscar_por_id(modelo_id)
    if not m:
        raise ValueError("Configuração não encontrada.")
    return m


def buscar_por_modelo(modelo: str) -> dict | None:
    return repo.buscar_por_modelo(modelo)


def criar(dados: dict) -> int:
    if not dados.get("nome"):
        raise ValueError("Nome é obrigatório.")
    return repo.criar(_preparar(dados))


def atualizar(modelo_id: int, dados: dict) -> None:
    if not dados.get("nome"):
        raise ValueError("Nome é obrigatório.")
    repo.atualizar(modelo_id, {**_preparar(dados), "ativo": dados.get("ativo", True)})


def excluir(modelo_id: int) -> None:
    repo.excluir(modelo_id)


def _preparar(dados: dict) -> dict:
    return {
        "nome":             (dados.get("nome") or "").strip(),
        "modelo":           (dados.get("modelo") or "").strip() or None,
        "cliente":          (dados.get("cliente") or "").strip() or None,
        "familia":          (dados.get("familia") or "").strip() or None,
        "qtd_por_caixa":    int(dados["qtd_por_caixa"]) if dados.get("qtd_por_caixa") else None,
        "meta_hora":        int(dados["meta_hora"])        if dados.get("meta_hora") else None,
        "mascara_etiqueta": (dados.get("mascara_etiqueta") or "").strip() or None,
        "roteiro_id":       int(dados["roteiro_id"])      if dados.get("roteiro_id") else None,
    }
