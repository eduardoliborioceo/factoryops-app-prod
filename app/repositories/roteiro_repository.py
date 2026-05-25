from app.extensions import get_db
from psycopg.rows import dict_row

_ETAPAS_SQL = """
    COALESCE(
        (SELECT json_agg(sub ORDER BY sub.ordem)
         FROM (
             SELECT e.id, e.setor, e.ordem, e.observacao,
                    COALESCE(
                        (SELECT json_agg(rl ORDER BY rl.ordem)
                         FROM (
                             SELECT linha, ordem
                             FROM roteiro_etapa_linhas
                             WHERE etapa_id = e.id
                             ORDER BY ordem
                         ) rl),
                        '[]'::json
                    ) AS linhas
             FROM roteiro_etapas e
             WHERE e.roteiro_id = r.id
             ORDER BY e.ordem
         ) sub),
        '[]'::json
    ) AS etapas
"""


def listar(cliente: str = "") -> list:
    params = []
    where = ""
    if cliente:
        where = "WHERE r.cliente = %s"
        params.append(cliente)

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT
                    r.id, r.nome, r.cliente, r.filial, r.descricao, r.ativo, r.criado_em,
                    {_ETAPAS_SQL},
                    (SELECT COUNT(*) FROM roteiro_modelos m WHERE m.roteiro_id = r.id) AS total_modelos
                FROM roteiros r
                {where}
                ORDER BY r.cliente, r.nome
            """, params)
            return cur.fetchall() or []


def buscar_por_id(roteiro_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT r.id, r.nome, r.cliente, r.filial, r.descricao, r.ativo, r.criado_em,
                       {_ETAPAS_SQL}
                FROM roteiros r
                WHERE r.id = %s
            """, (roteiro_id,))
            return cur.fetchone()


def listar_clientes() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT cliente FROM roteiros
                WHERE cliente IS NOT NULL AND cliente <> ''
                ORDER BY cliente
            """)
            return [r["cliente"] for r in cur.fetchall()]


def listar_clientes_modelos() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT cliente FROM modelos
                WHERE cliente IS NOT NULL AND cliente <> ''
                ORDER BY cliente
            """)
            return [r["cliente"] for r in cur.fetchall()]


def listar_codigos_por_cliente(cliente: str) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT codigo FROM modelos
                WHERE cliente = %s
                ORDER BY codigo
            """, (cliente,))
            return [r["codigo"] for r in cur.fetchall()]


def inserir(dados: dict) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO roteiros (nome, cliente, filial, descricao)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (dados["nome"], dados["cliente"], dados.get("filial") or "VTE", dados.get("descricao") or None))
            roteiro_id = cur.fetchone()["id"]
            _salvar_etapas(cur, roteiro_id, dados.get("etapas", []))
            return roteiro_id


def atualizar(roteiro_id: int, dados: dict) -> None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                UPDATE roteiros
                SET nome = %s, cliente = %s, filial = %s, descricao = %s
                WHERE id = %s
            """, (dados["nome"], dados["cliente"], dados.get("filial") or "VTE", dados.get("descricao") or None, roteiro_id))
            cur.execute("DELETE FROM roteiro_etapas WHERE roteiro_id = %s", (roteiro_id,))
            _salvar_etapas(cur, roteiro_id, dados.get("etapas", []))


def excluir(roteiro_id: int) -> None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("DELETE FROM roteiros WHERE id = %s", (roteiro_id,))


def setores_do_modelo(modelo_codigo: str) -> list[str]:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT re.setor
                FROM roteiro_etapas re
                JOIN roteiro_modelos rm ON rm.roteiro_id = re.roteiro_id
                JOIN roteiros r ON r.id = rm.roteiro_id
                WHERE (rm.modelo_codigo = %s OR %s LIKE rm.modelo_codigo || ' %%')
                  AND r.ativo = TRUE
                ORDER BY re.ordem
            """, (modelo_codigo, modelo_codigo))
            return [row["setor"] for row in cur.fetchall()]


def vincular_modelo(roteiro_id: int, modelo_codigo: str) -> None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO roteiro_modelos (roteiro_id, modelo_codigo)
                VALUES (%s, %s)
                ON CONFLICT (roteiro_id, modelo_codigo) DO NOTHING
            """, (roteiro_id, modelo_codigo))


def desvincular_modelo(roteiro_id: int, modelo_codigo: str) -> None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                DELETE FROM roteiro_modelos
                WHERE roteiro_id = %s AND modelo_codigo = %s
            """, (roteiro_id, modelo_codigo))


def modelos_do_roteiro(roteiro_id: int) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT rm.modelo_codigo, m.cliente, m.setor, m.fase
                FROM roteiro_modelos rm
                LEFT JOIN modelos m ON m.codigo = rm.modelo_codigo
                WHERE rm.roteiro_id = %s
                ORDER BY rm.modelo_codigo
            """, (roteiro_id,))
            return cur.fetchall() or []


def _salvar_etapas(cur, roteiro_id: int, etapas: list) -> None:
    for i, etapa in enumerate(etapas, start=1):
        setor = (etapa.get("setor") or "").strip()
        if not setor:
            continue
        cur.execute("""
            INSERT INTO roteiro_etapas (roteiro_id, setor, ordem, observacao)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (roteiro_id, setor, i, etapa.get("observacao") or None))
        etapa_id = cur.fetchone()["id"]

        for j, linha_item in enumerate(etapa.get("linhas") or [], start=1):
            linha_nome = (linha_item.get("linha") or "").strip()
            if not linha_nome:
                continue
            cur.execute("""
                INSERT INTO roteiro_etapa_linhas (etapa_id, linha, ordem)
                VALUES (%s, %s, %s)
            """, (etapa_id, linha_nome, j))
