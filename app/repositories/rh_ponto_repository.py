from app.extensions import get_db
from psycopg.rows import dict_row


# ── TURNOS ──────────────────────────────────────────────────────────────────

def listar_turnos(ativo: bool | None = None) -> list:
    where = "" if ativo is None else "WHERE ativo = %s"
    params = () if ativo is None else (ativo,)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT id, nome, hora_entrada, hora_saida, dias_semana,
                       intervalo_min, ativo, criado_em
                FROM rh_turno
                {where}
                ORDER BY hora_entrada, nome
            """, params)
            return cur.fetchall()


def buscar_turno(turno_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM rh_turno WHERE id = %s", (turno_id,)
            )
            return cur.fetchone()


def criar_turno(nome: str, hora_entrada: str, hora_saida: str,
                dias_semana: list, intervalo_min: int) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_turno (nome, hora_entrada, hora_saida, dias_semana, intervalo_min)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (nome, hora_entrada, hora_saida, dias_semana, intervalo_min))
            return cur.fetchone()["id"]


def atualizar_turno(turno_id: int, nome: str, hora_entrada: str,
                    hora_saida: str, dias_semana: list,
                    intervalo_min: int, ativo: bool) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE rh_turno
                SET nome=%s, hora_entrada=%s, hora_saida=%s,
                    dias_semana=%s, intervalo_min=%s, ativo=%s
                WHERE id=%s
            """, (nome, hora_entrada, hora_saida,
                  dias_semana, intervalo_min, ativo, turno_id))


def excluir_turno(turno_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_turno WHERE id = %s", (turno_id,))


# ── ESCALAS ─────────────────────────────────────────────────────────────────

def listar_escalas(mes: int | None = None, ano: int | None = None,
                   employee_code: str | None = None,
                   turno_id: int | None = None) -> list:
    conditions = []
    params = []
    if mes and ano:
        conditions.append(
            "(e.data_inicio <= make_date(%s, %s, 1) + INTERVAL '1 month - 1 day' "
            "AND e.data_fim >= make_date(%s, %s, 1))"
        )
        params += [ano, mes, ano, mes]
    if employee_code:
        conditions.append("e.employee_code = %s")
        params.append(employee_code)
    if turno_id:
        conditions.append("e.turno_id = %s")
        params.append(turno_id)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT e.id, e.employee_code, e.turno_id, e.data_inicio, e.data_fim, e.ativo,
                       t.nome AS turno_nome, t.hora_entrada, t.hora_saida,
                       COALESCE(emp.full_name, u.full_name) AS nome_colaborador
                FROM rh_escala e
                JOIN rh_turno t ON t.id = e.turno_id
                LEFT JOIN employees emp ON emp.employee_code = e.employee_code
                LEFT JOIN users u ON u.matricula = e.employee_code
                {where}
                ORDER BY e.data_inicio DESC, nome_colaborador
            """, params)
            return cur.fetchall()


def criar_escala(employee_code: str, turno_id: int,
                 data_inicio: str, data_fim: str) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_escala (employee_code, turno_id, data_inicio, data_fim)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (employee_code, turno_id, data_inicio, data_fim))
            return cur.fetchone()["id"]


def excluir_escala(escala_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_escala WHERE id = %s", (escala_id,))


def listar_colaboradores_para_escala() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT employee_code AS codigo, full_name AS nome
                FROM employees
                WHERE employee_code IS NOT NULL AND full_name IS NOT NULL
                ORDER BY full_name
            """)
            return cur.fetchall()


# ── REGISTROS DE PONTO ──────────────────────────────────────────────────────

def listar_registros(data_inicio: str, data_fim: str,
                     employee_code: str | None = None) -> list:
    conditions = ["r.data BETWEEN %s AND %s"]
    params: list = [data_inicio, data_fim]
    if employee_code:
        conditions.append("r.employee_code = %s")
        params.append(employee_code)
    where = "WHERE " + " AND ".join(conditions)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT r.id, r.employee_code, r.data, r.tipo, r.hora, r.observacao, r.criado_em,
                       COALESCE(emp.full_name, u.full_name) AS nome_colaborador
                FROM rh_registro_ponto r
                LEFT JOIN employees emp ON emp.employee_code = r.employee_code
                LEFT JOIN users u ON u.matricula = r.employee_code
                {where}
                ORDER BY r.data DESC, r.employee_code, r.hora
            """, params)
            return cur.fetchall()


def kpis_registros(data_inicio: str, data_fim: str) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    COUNT(*)                                          AS total_registros,
                    COUNT(DISTINCT employee_code)                     AS colaboradores,
                    COUNT(*) FILTER (WHERE tipo = 'entrada')         AS entradas,
                    COUNT(*) FILTER (WHERE tipo = 'saida')           AS saidas
                FROM rh_registro_ponto
                WHERE data BETWEEN %s AND %s
            """, (data_inicio, data_fim))
            return cur.fetchone() or {}


def criar_registro(employee_code: str, data: str, tipo: str,
                   hora: str, observacao: str | None = None) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_registro_ponto (employee_code, data, tipo, hora, observacao)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (employee_code, data, tipo, hora, observacao))
            return cur.fetchone()["id"]


def excluir_registro(registro_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_registro_ponto WHERE id = %s", (registro_id,))


# ── HORAS EXTRAS ────────────────────────────────────────────────────────────

def listar_horas_extras(status: str | None = None,
                        data_inicio: str | None = None,
                        data_fim: str | None = None,
                        employee_code: str | None = None) -> list:
    conditions = []
    params: list = []
    if status:
        conditions.append("h.status = %s")
        params.append(status)
    if data_inicio:
        conditions.append("h.data >= %s")
        params.append(data_inicio)
    if data_fim:
        conditions.append("h.data <= %s")
        params.append(data_fim)
    if employee_code:
        conditions.append("h.employee_code = %s")
        params.append(employee_code)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT h.id, h.employee_code, h.data, h.horas, h.justificativa,
                       h.status, h.aprovado_por, h.motivo_rejeicao, h.criado_em,
                       COALESCE(emp.full_name, u.full_name) AS nome_colaborador
                FROM rh_hora_extra h
                LEFT JOIN employees emp ON emp.employee_code = h.employee_code
                LEFT JOIN users u ON u.matricula = h.employee_code
                {where}
                ORDER BY h.data DESC, h.criado_em DESC
            """, params)
            return cur.fetchall()


def kpis_horas_extras() -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'pendente')     AS pendentes,
                    COUNT(*) FILTER (WHERE status = 'aprovado')     AS aprovadas,
                    COUNT(*) FILTER (WHERE status = 'rejeitado')    AS rejeitadas,
                    COALESCE(SUM(horas) FILTER (WHERE status = 'aprovado'), 0) AS horas_aprovadas
                FROM rh_hora_extra
            """)
            return cur.fetchone() or {}


def criar_hora_extra(employee_code: str, data: str,
                     horas: float, justificativa: str) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_hora_extra (employee_code, data, horas, justificativa)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (employee_code, data, horas, justificativa))
            return cur.fetchone()["id"]


def atualizar_status_hora_extra(hora_extra_id: int, status: str,
                                aprovado_por: str,
                                motivo_rejeicao: str | None = None) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE rh_hora_extra
                SET status = %s, aprovado_por = %s, motivo_rejeicao = %s
                WHERE id = %s
            """, (status, aprovado_por, motivo_rejeicao, hora_extra_id))


def excluir_hora_extra(hora_extra_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_hora_extra WHERE id = %s", (hora_extra_id,))


# ── AFASTAMENTOS ────────────────────────────────────────────────────────────

def listar_afastamentos(tipo: str | None = None,
                        status: str | None = None,
                        data_inicio: str | None = None,
                        data_fim: str | None = None,
                        employee_code: str | None = None) -> list:
    conditions = []
    params: list = []
    if tipo:
        conditions.append("a.tipo = %s")
        params.append(tipo)
    if status:
        conditions.append("a.status = %s")
        params.append(status)
    if data_inicio:
        conditions.append("a.data_inicio >= %s")
        params.append(data_inicio)
    if data_fim:
        conditions.append("a.data_inicio <= %s")
        params.append(data_fim)
    if employee_code:
        conditions.append("a.employee_code = %s")
        params.append(employee_code)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT a.id, a.employee_code, a.tipo, a.data_inicio, a.data_fim,
                       a.data_fim_real, a.justificativa, a.cid, a.status,
                       a.dias_corridos, a.criado_em,
                       COALESCE(emp.full_name, u.full_name) AS nome_colaborador
                FROM rh_afastamento a
                LEFT JOIN employees emp ON emp.employee_code = a.employee_code
                LEFT JOIN users u ON u.matricula = a.employee_code
                {where}
                ORDER BY a.data_inicio DESC
            """, params)
            return cur.fetchall()


def kpis_afastamentos() -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'ativo')          AS ativos,
                    COUNT(*) FILTER (WHERE status = 'encerrado')       AS encerrados,
                    COUNT(*) FILTER (WHERE tipo = 'doenca')            AS por_doenca,
                    COUNT(*) FILTER (WHERE tipo = 'acidente_trabalho') AS por_acidente,
                    COUNT(*) FILTER (WHERE tipo = 'maternidade')       AS maternidade,
                    COALESCE(SUM(dias_corridos) FILTER (WHERE status = 'ativo'), 0) AS dias_em_aberto
                FROM rh_afastamento
            """)
            return cur.fetchone() or {}


def criar_afastamento(employee_code: str, tipo: str,
                      data_inicio: str, data_fim: str | None,
                      justificativa: str, cid: str | None = None) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_afastamento
                    (employee_code, tipo, data_inicio, data_fim, justificativa, cid, dias_corridos)
                VALUES (%s, %s, %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL
                         THEN (%s::date - %s::date + 1)
                         ELSE NULL END)
                RETURNING id
            """, (employee_code, tipo, data_inicio, data_fim,
                  justificativa, cid,
                  data_fim, data_fim, data_inicio))
            return cur.fetchone()["id"]


def encerrar_afastamento(afastamento_id: int, data_fim_real: str) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE rh_afastamento
                SET status = 'encerrado',
                    data_fim_real = %s,
                    dias_corridos = (%s::date - data_inicio + 1)
                WHERE id = %s
            """, (data_fim_real, data_fim_real, afastamento_id))


def excluir_afastamento(afastamento_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_afastamento WHERE id = %s", (afastamento_id,))
