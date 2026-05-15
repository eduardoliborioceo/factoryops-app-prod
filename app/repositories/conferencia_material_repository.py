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
                    cm.conferido_em,
                    ca.id          AS arquivo_id,
                    ca.filename    AS arquivo_nome
                FROM planejamento p
                LEFT JOIN controle_ops co ON co.id = p.op_id
                LEFT JOIN LATERAL (
                    SELECT id, status, observacao, conferido_por, conferido_em
                    FROM conferencia_material
                    WHERE planejamento_id = p.id
                    ORDER BY conferido_em DESC
                    LIMIT 1
                ) cm ON TRUE
                LEFT JOIN LATERAL (
                    SELECT id, filename
                    FROM conferencia_arquivo
                    WHERE planejamento_id = p.id
                    ORDER BY uploaded_em DESC
                    LIMIT 1
                ) ca ON TRUE
                WHERE p.data = %s
                ORDER BY p.turno, p.linha, p.hora_inicio_prevista
            """, (data,))
            return cur.fetchall()


def status_por_data(data: str) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT ON (cm.planejamento_id)
                    cm.planejamento_id,
                    cm.status,
                    cm.observacao,
                    cm.conferido_por,
                    cm.conferido_em,
                    cm.componentes_confirmados
                FROM conferencia_material cm
                JOIN planejamento p ON p.id = cm.planejamento_id
                WHERE p.data = %s
                ORDER BY cm.planejamento_id, cm.conferido_em DESC
            """, (data,))
            return {r["planejamento_id"]: dict(r) for r in cur.fetchall()}


def arquivo_por_plano(planejamento_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, filename, mimetype, componentes, uploaded_por, uploaded_em
                FROM conferencia_arquivo
                WHERE planejamento_id = %s
                ORDER BY uploaded_em DESC
                LIMIT 1
            """, (planejamento_id,))
            return cur.fetchone()


def salvar_arquivo(planejamento_id: int, filename: str, mimetype: str,
                   conteudo: bytes, componentes: list, uploaded_por: str) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conferencia_arquivo
                    (planejamento_id, filename, mimetype, conteudo, componentes, uploaded_por)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                RETURNING id
            """, (planejamento_id, filename, mimetype,
                  conteudo, __import__('json').dumps(componentes), uploaded_por))
            return cur.fetchone()[0]


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


def registrar(planejamento_id: int, status: str, observacao: str | None,
              conferido_por: str, componentes_confirmados: list | None) -> int:
    import json
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conferencia_material
                    (planejamento_id, status, observacao, conferido_por, componentes_confirmados)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                RETURNING id
            """, (planejamento_id, status, observacao or None, conferido_por,
                  json.dumps(componentes_confirmados) if componentes_confirmados is not None else None))
            return cur.fetchone()[0]


def historico_por_plano(planejamento_id: int) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, status, observacao, conferido_por, conferido_em,
                       componentes_confirmados
                FROM conferencia_material
                WHERE planejamento_id = %s
                ORDER BY conferido_em DESC
            """, (planejamento_id,))
            return cur.fetchall()
