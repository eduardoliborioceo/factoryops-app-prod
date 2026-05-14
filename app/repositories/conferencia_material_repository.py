from app.extensions import get_db
from psycopg.rows import dict_row


def listar_planos_por_data(data: str) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    p.id, p.data, p.turno, p.setor, p.linha,
                    p.modelo, p.quantidade_planejada, p.status AS status_producao,
                    co.numero_op,
                    cm.id          AS conferencia_id,
                    cm.status      AS status_material,
                    cm.observacao  AS conferencia_obs,
                    cm.conferido_por,
                    cm.conferido_em
                FROM planejamento p
                LEFT JOIN controle_ops co ON co.id = p.op_id
                LEFT JOIN LATERAL (
                    SELECT id, status, observacao, conferido_por, conferido_em
                    FROM conferencia_material
                    WHERE planejamento_id = p.id
                    ORDER BY conferido_em DESC
                    LIMIT 1
                ) cm ON TRUE
                WHERE p.data = %s
                ORDER BY p.turno, p.linha, p.hora_inicio_prevista
            """, (data,))
            return cur.fetchall()


def listar_datas_com_planos() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT data
                FROM planejamento
                WHERE data >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY data DESC
            """)
            return cur.fetchall()


def registrar(planejamento_id: int, status: str, observacao: str | None, conferido_por: str) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conferencia_material (planejamento_id, status, observacao, conferido_por)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (planejamento_id, status, observacao or None, conferido_por))
            return cur.fetchone()[0]


def historico_por_plano(planejamento_id: int) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, status, observacao, conferido_por, conferido_em
                FROM conferencia_material
                WHERE planejamento_id = %s
                ORDER BY conferido_em DESC
            """, (planejamento_id,))
            return cur.fetchall()


def ultimo_status_por_plano(planejamento_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT status, conferido_por, conferido_em
                FROM conferencia_material
                WHERE planejamento_id = %s
                ORDER BY conferido_em DESC
                LIMIT 1
            """, (planejamento_id,))
            return cur.fetchone()
