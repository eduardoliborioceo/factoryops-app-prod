from app.repositories import rh_ponto_repository as repo


# ── TURNOS ──────────────────────────────────────────────────────────────────

def listar_turnos(apenas_ativos: bool = False) -> list:
    return repo.listar_turnos(ativo=True if apenas_ativos else None)


def salvar_turno(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    hora_entrada = dados.get("hora_entrada", "").strip()
    hora_saida = dados.get("hora_saida", "").strip()
    dias_semana = dados.get("dias_semana") or []
    intervalo_min = int(dados.get("intervalo_min") or 0)

    if not nome:
        raise ValueError("Nome do turno é obrigatório.")
    if not hora_entrada or not hora_saida:
        raise ValueError("Horários de entrada e saída são obrigatórios.")
    if not dias_semana:
        raise ValueError("Selecione pelo menos um dia da semana.")

    turno_id = dados.get("id")
    if turno_id:
        repo.atualizar_turno(
            int(turno_id), nome, hora_entrada, hora_saida,
            dias_semana, intervalo_min,
            ativo=dados.get("ativo", True)
        )
        return {"id": int(turno_id)}

    new_id = repo.criar_turno(nome, hora_entrada, hora_saida, dias_semana, intervalo_min)
    return {"id": new_id}


def excluir_turno(turno_id: int) -> None:
    repo.excluir_turno(turno_id)


# ── ESCALAS ─────────────────────────────────────────────────────────────────

def listar_escalas(mes: int | None = None, ano: int | None = None,
                   employee_code: str | None = None,
                   turno_id: int | None = None) -> list:
    return repo.listar_escalas(mes, ano, employee_code, turno_id)


def atribuir_escala(dados: dict) -> dict:
    employee_code = (dados.get("employee_code") or "").strip()
    turno_id = dados.get("turno_id")
    data_inicio = dados.get("data_inicio", "").strip()
    data_fim = dados.get("data_fim", "").strip()

    if not employee_code:
        raise ValueError("Matrícula do colaborador é obrigatória.")
    if not turno_id:
        raise ValueError("Turno é obrigatório.")
    if not data_inicio or not data_fim:
        raise ValueError("Período de vigência é obrigatório.")
    if data_fim < data_inicio:
        raise ValueError("Data fim deve ser posterior à data de início.")

    new_id = repo.criar_escala(employee_code, int(turno_id), data_inicio, data_fim)
    return {"id": new_id}


def remover_escala(escala_id: int) -> None:
    repo.excluir_escala(escala_id)


def listar_colaboradores_para_escala() -> list:
    return repo.listar_colaboradores_para_escala()


# ── REGISTROS DE PONTO ──────────────────────────────────────────────────────

def listar_registros(data_inicio: str, data_fim: str,
                     employee_code: str | None = None) -> list:
    if not data_inicio or not data_fim:
        raise ValueError("Período é obrigatório.")
    return repo.listar_registros(data_inicio, data_fim, employee_code)


def kpis_registros(data_inicio: str, data_fim: str) -> dict:
    return repo.kpis_registros(data_inicio, data_fim)


def registrar_ponto(dados: dict) -> dict:
    employee_code = (dados.get("employee_code") or "").strip()
    data = (dados.get("data") or "").strip()
    tipo = (dados.get("tipo") or "").strip()
    hora = (dados.get("hora") or "").strip()
    obs = (dados.get("observacao") or "").strip() or None

    if not employee_code:
        raise ValueError("Matrícula é obrigatória.")
    if not data:
        raise ValueError("Data é obrigatória.")
    if tipo not in ("entrada", "saida", "intervalo_saida", "intervalo_retorno"):
        raise ValueError("Tipo de registro inválido.")
    if not hora:
        raise ValueError("Hora é obrigatória.")

    new_id = repo.criar_registro(employee_code, data, tipo, hora, obs)
    return {"id": new_id}


def excluir_registro(registro_id: int) -> None:
    repo.excluir_registro(registro_id)


# ── HORAS EXTRAS ────────────────────────────────────────────────────────────

def listar_horas_extras(status: str | None = None,
                        data_inicio: str | None = None,
                        data_fim: str | None = None,
                        employee_code: str | None = None) -> list:
    return repo.listar_horas_extras(status, data_inicio, data_fim, employee_code)


def kpis_horas_extras() -> dict:
    return repo.kpis_horas_extras()


def solicitar_hora_extra(dados: dict) -> dict:
    employee_code = (dados.get("employee_code") or "").strip()
    data = (dados.get("data") or "").strip()
    horas = dados.get("horas")
    justificativa = (dados.get("justificativa") or "").strip()

    if not employee_code:
        raise ValueError("Matrícula é obrigatória.")
    if not data:
        raise ValueError("Data é obrigatória.")
    if not horas or float(horas) <= 0:
        raise ValueError("Quantidade de horas deve ser maior que zero.")
    if float(horas) > 10:
        raise ValueError("Não é permitido registrar mais de 10 horas extras por dia.")
    if not justificativa:
        raise ValueError("Justificativa é obrigatória.")

    new_id = repo.criar_hora_extra(employee_code, data, float(horas), justificativa)
    return {"id": new_id}


def aprovar_hora_extra(hora_extra_id: int, aprovado_por: str) -> None:
    repo.atualizar_status_hora_extra(hora_extra_id, "aprovado", aprovado_por)


def rejeitar_hora_extra(hora_extra_id: int, aprovado_por: str,
                        motivo: str | None = None) -> None:
    repo.atualizar_status_hora_extra(hora_extra_id, "rejeitado", aprovado_por, motivo)


def excluir_hora_extra(hora_extra_id: int) -> None:
    repo.excluir_hora_extra(hora_extra_id)


# ── AFASTAMENTOS ────────────────────────────────────────────────────────────

TIPOS_AFASTAMENTO = {
    "doenca": "Doença",
    "acidente_trabalho": "Acidente de Trabalho",
    "maternidade": "Licença Maternidade",
    "paternidade": "Licença Paternidade",
    "ferias": "Férias",
    "licenca_remunerada": "Licença Remunerada",
    "licenca_nao_remunerada": "Licença Não Remunerada",
    "inss": "INSS / Afastamento Previdenciário",
    "outros": "Outros",
}


def listar_afastamentos(tipo: str | None = None,
                        status: str | None = None,
                        data_inicio: str | None = None,
                        data_fim: str | None = None,
                        employee_code: str | None = None) -> list:
    rows = repo.listar_afastamentos(tipo, status, data_inicio, data_fim, employee_code)
    for r in rows:
        r["tipo_label"] = TIPOS_AFASTAMENTO.get(r.get("tipo", ""), r.get("tipo", ""))
    return rows


def kpis_afastamentos() -> dict:
    return repo.kpis_afastamentos()


def registrar_afastamento(dados: dict) -> dict:
    employee_code = (dados.get("employee_code") or "").strip()
    tipo = (dados.get("tipo") or "").strip()
    data_inicio = (dados.get("data_inicio") or "").strip()
    data_fim = (dados.get("data_fim") or "").strip() or None
    justificativa = (dados.get("justificativa") or "").strip()
    cid = (dados.get("cid") or "").strip() or None

    if not employee_code:
        raise ValueError("Matrícula é obrigatória.")
    if tipo not in TIPOS_AFASTAMENTO:
        raise ValueError("Tipo de afastamento inválido.")
    if not data_inicio:
        raise ValueError("Data de início é obrigatória.")
    if data_fim and data_fim < data_inicio:
        raise ValueError("Data fim deve ser posterior à data de início.")
    if not justificativa:
        raise ValueError("Justificativa é obrigatória.")

    new_id = repo.criar_afastamento(
        employee_code, tipo, data_inicio, data_fim, justificativa, cid
    )
    return {"id": new_id}


def encerrar_afastamento(afastamento_id: int, data_fim_real: str) -> None:
    if not data_fim_real:
        raise ValueError("Data de encerramento é obrigatória.")
    repo.encerrar_afastamento(afastamento_id, data_fim_real)


def excluir_afastamento(afastamento_id: int) -> None:
    repo.excluir_afastamento(afastamento_id)


def tipos_afastamento() -> dict:
    return TIPOS_AFASTAMENTO
