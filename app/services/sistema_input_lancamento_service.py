from datetime import date, timedelta
from app.repositories import sistema_input_lancamento_repository as repo


def catalogos() -> dict:
    return {
        "motivos": repo.listar_motivos(),
        "defeitos": repo.listar_defeitos(),
    }


def slots_do_turno(data_str: str, setor: str, linha: str, turno: str) -> list:
    from app.repositories import planejamento_repository as plan_repo
    from app.services import planejamento_service as plan_svc

    planos = [dict(p) for p in plan_repo.listar_plano_de_voo(data_str, turno=turno, setor=setor, linha=linha)]
    intervalos = [dict(i) for i in plan_repo.turno_intervalos(turno)]
    paradas = [dict(p) for p in plan_repo.paradas_da_linha(setor, linha)]

    if intervalos and planos:
        slots = plan_svc.gerar_plano_hora_a_hora(planos, intervalos, paradas, data_str)
    else:
        slots = _gerar_slots_vazios(intervalos, data_str)

    resultado = []
    for slot in slots:
        # gerar_plano_hora_a_hora → strings "HH:MM"
        # _gerar_slots_vazios → inteiros slot_inicio / slot_fim
        if "hora_inicio" in slot and isinstance(slot["hora_inicio"], str):
            hora_inicio = slot["hora_inicio"]
            hora_fim = slot["hora_fim"]
        else:
            hora_inicio = _min_to_hhmm(slot.get("slot_inicio") or 0)
            hora_fim = _min_to_hhmm(slot.get("slot_fim") or 0)

        existente = repo.buscar_lancamento(data_str, setor, linha, turno, hora_inicio)

        meta_hora = slot.get("meta_hora") or slot.get("taxa_horaria") or 0

        resultado.append({
            "hora_inicio": hora_inicio,
            "hora_fim": hora_fim,
            "modelo": slot.get("modelo") or "",
            "cliente": slot.get("cliente") or "",
            "op": slot.get("numero_op") or "",
            "fase": slot.get("fase") or "",
            "meta_hora": int(meta_hora) if meta_hora else 0,
            "planejamento_id": slot.get("planejamento_id"),
            "lancamento": dict(existente) if existente else None,
        })

    return resultado


def _gerar_slots_vazios(intervalos: list, data_str: str) -> list:
    if not intervalos:
        return []
    slots = []
    for iv in intervalos:
        inicio = _hhmm_to_min(str(iv["hora_inicio"]))
        fim = _hhmm_to_min(str(iv["hora_fim"]))
        if fim <= inicio:
            fim += 24 * 60
        cursor = inicio
        while cursor + 60 <= fim:
            slots.append({"slot_inicio": cursor, "slot_fim": cursor + 60})
            cursor += 60
        if cursor < fim:
            slots.append({"slot_inicio": cursor, "slot_fim": fim})
    return slots


def _hhmm_to_min(valor: str) -> int:
    if not valor:
        return 0
    partes = str(valor).replace(":", " ").split()
    h = int(partes[0]) if partes else 0
    m = int(partes[1]) if len(partes) > 1 else 0
    return h * 60 + m


def _min_to_hhmm(minutos: int) -> str:
    minutos = minutos % (24 * 60)
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def calcular_perda_minutos(meta_hora: int, producao_real: int, duracao_slot_min: int = 60) -> int:
    if not meta_hora or meta_hora <= 0:
        return 0
    if producao_real >= meta_hora:
        return 0
    return int(round(((meta_hora - producao_real) / meta_hora) * duracao_slot_min))


def salvar(payload: dict, user_id: int | None) -> int:
    dados = payload.get("lancamento", {})
    justificativas = payload.get("justificativas", [])
    defeitos = payload.get("defeitos", [])

    if not dados.get("data"):
        raise ValueError("Data é obrigatória.")
    if not dados.get("setor"):
        raise ValueError("Setor é obrigatório.")
    if not dados.get("linha"):
        raise ValueError("Linha é obrigatória.")
    if not dados.get("turno"):
        raise ValueError("Turno é obrigatório.")
    if not dados.get("hora_inicio"):
        raise ValueError("Hora de início é obrigatória.")

    try:
        producao_real = int(dados.get("producao_real") or 0)
    except (ValueError, TypeError):
        raise ValueError("Produção real deve ser um número inteiro.")

    dados["producao_real"] = producao_real

    for j in justificativas:
        try:
            j["perda_minutos"] = int(j.get("perda_minutos") or 0)
        except (ValueError, TypeError):
            j["perda_minutos"] = 0

    for d in defeitos:
        try:
            d["quantidade"] = int(d.get("quantidade") or 1)
        except (ValueError, TypeError):
            d["quantidade"] = 1

    return repo.salvar_lancamento(dados, justificativas, defeitos, user_id)


def historico(setor: str = "", linha: str = "", turno: str = "", dias: int = 7) -> list:
    data_final = date.today()
    data_inicial = data_final - timedelta(days=dias - 1)
    return repo.listar_historico(str(data_inicial), str(data_final), setor, linha, turno)


def excluir(lancamento_id: int) -> None:
    if not lancamento_id or lancamento_id <= 0:
        raise ValueError("ID inválido.")
    repo.excluir_lancamento(lancamento_id)
