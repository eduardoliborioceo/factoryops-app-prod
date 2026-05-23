from app.repositories import sync_repository as repo


def automatico_habilitado() -> bool:
    valor = repo.get_config("automatico_habilitado")
    return valor != "false"


def toggle_automatico() -> bool:
    habilitado = automatico_habilitado()
    repo.set_config("automatico_habilitado", "false" if habilitado else "true")
    return not habilitado


def registrar_execucao(tipo: str, status: str, buscados: int, salvos: int, erros: int, mensagem: str = None) -> None:
    repo.registrar_historico(tipo, status, buscados, salvos, erros, mensagem)


def listar_historico(limite: int = 50) -> list:
    return repo.listar_historico(limite)


def resumo() -> dict:
    try:
        return repo.resumo()
    except Exception:
        return {
            "total_sucesso": 0,
            "total_erro": 0,
            "total_skip": 0,
            "ultimo_sucesso": None,
            "ultima_execucao": None,
        }
