from app.repositories import conferencia_material_repository as repo

STATUS_LABEL = {
    "CONFIRMADO":    "Confirmado",
    "SEM_MATERIAL":  "Sem Material",
    "PARCIAL":       "Parcial",
}

STATUS_COR = {
    "CONFIRMADO":   "success",
    "SEM_MATERIAL": "danger",
    "PARCIAL":      "warning",
}

STATUSES_VALIDOS = list(STATUS_LABEL.keys())


def listar_planos_por_data(data: str) -> list:
    return repo.listar_planos_por_data(data)


def listar_datas() -> list:
    return repo.listar_datas_com_planos()


def confirmar(planejamento_id: int, status: str, observacao: str | None, conferido_por: str) -> int:
    if status not in STATUSES_VALIDOS:
        raise ValueError(f"Status inválido: {status}")
    if not conferido_por or not conferido_por.strip():
        raise ValueError("Conferido por é obrigatório")
    return repo.registrar(planejamento_id, status, observacao, conferido_por.strip())


def historico_por_plano(planejamento_id: int) -> list:
    return repo.historico_por_plano(planejamento_id)
