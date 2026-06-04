from app.repositories import pci_hub_repository as repo


def iniciar_sessao(linha: str, usuario: str, op: str, modelo: str, cliente: str, turno: str) -> dict:
    if not linha or not usuario or not op:
        raise ValueError("Linha, usuário e OP são obrigatórios.")
    return repo.criar_sessao(
        linha=linha.strip(),
        usuario=usuario.strip(),
        op=op.strip().upper(),
        modelo=modelo.strip() or None,
        cliente=cliente.strip() or None,
        turno=turno.strip() or None,
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
