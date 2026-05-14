from app.extensions import get_db
from psycopg.rows import dict_row


def listar(data: str, turno: str = "", setor: str = "", linha: str = "") -> list:
    filtros = ["p.data = %s"]
    params  = [data]

    if turno:
        filtros.append("p.turno = %s")
        params.append(turno)
    if setor:
        filtros.append("p.setor = %s")
        params.append(setor)
    if linha:
        filtros.append("p.linha = %s")
        params.append(linha)

    where = " AND ".join(filtros)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT
                    p.id, p.data, p.turno, p.setor, p.linha,
                    p.op_id, p.modelo, p.quantidade_planejada, p.taxa_horaria,
                    p.setup_min,
                    p.hora_inicio_prevista, p.hora_fim_prevista,
                    p.status, p.observacao, p.criado_por, p.criado_em,
                    co.numero_op,
                    co.descricao AS descricao_op,
                    (co.quantidade - co.produzido) AS saldo_op,
                    cm.status      AS status_material,
                    cm.conferido_por AS material_conferido_por,
                    cm.conferido_em  AS material_conferido_em
                FROM planejamento p
                LEFT JOIN controle_ops co ON co.id = p.op_id
                LEFT JOIN LATERAL (
                    SELECT status, conferido_por, conferido_em
                    FROM conferencia_material
                    WHERE planejamento_id = p.id
                    ORDER BY conferido_em DESC
                    LIMIT 1
                ) cm ON TRUE
                WHERE {where}
                ORDER BY p.turno, p.linha, p.hora_inicio_prevista
            """, params)
            return cur.fetchall()


def buscar_por_id(planejamento_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT p.*, co.numero_op,
                       (co.quantidade - co.produzido) AS saldo_op
                FROM planejamento p
                LEFT JOIN controle_ops co ON co.id = p.op_id
                WHERE p.id = %s
            """, (planejamento_id,))
            return cur.fetchone()


def inserir(data: dict) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO planejamento (
                    data, turno, setor, linha, op_id, modelo, fase,
                    quantidade_planejada, taxa_horaria, setup_min,
                    hora_inicio_prevista, hora_fim_prevista,
                    status, observacao, criado_por
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PLANEJADO',%s,%s)
                RETURNING id
            """, (
                data["data"],
                data["turno"],
                data["setor"],
                data["linha"],
                data.get("op_id") or None,
                data["modelo"],
                data.get("fase") or None,
                data["quantidade_planejada"],
                data["taxa_horaria"],
                data.get("setup_min", 0),
                data["hora_inicio_prevista"],
                data.get("hora_fim_prevista") or None,
                data.get("observacao") or None,
                data.get("criado_por") or None,
            ))
            return cur.fetchone()["id"]


def atualizar(planejamento_id: int, data: dict) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE planejamento SET
                    op_id                = %s,
                    modelo               = %s,
                    quantidade_planejada = %s,
                    taxa_horaria         = %s,
                    setup_min            = %s,
                    hora_inicio_prevista = %s,
                    hora_fim_prevista    = %s,
                    observacao           = %s
                WHERE id = %s
            """, (
                data.get("op_id") or None,
                data["modelo"],
                data["quantidade_planejada"],
                data["taxa_horaria"],
                data.get("setup_min", 0),
                data["hora_inicio_prevista"],
                data.get("hora_fim_prevista") or None,
                data.get("observacao") or None,
                planejamento_id,
            ))


def atualizar_status(planejamento_id: int, status: str) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE planejamento SET status = %s WHERE id = %s",
                (status, planejamento_id),
            )


def atualizar_observacao(planejamento_id: int, observacao: str | None) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE planejamento SET observacao = %s WHERE id = %s",
                (observacao or None, planejamento_id),
            )


def excluir(planejamento_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM planejamento WHERE id = %s", (planejamento_id,))


def listar_plano_de_voo(data: str, turno: str = "", setor: str = "", linha: str = "") -> list:
    filtros = ["p.data = %s"]
    params  = [data]
    if turno:
        filtros.append("p.turno = %s")
        params.append(turno)
    if setor:
        filtros.append("p.setor = %s")
        params.append(setor)
    if linha:
        filtros.append("p.linha = %s")
        params.append(linha)

    where = " AND ".join(filtros)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT p.id, p.linha, p.setor, p.turno, p.modelo, p.op_id,
                       co.numero_op, p.fase,
                       (co.quantidade - co.produzido) AS saldo_op,
                       p.quantidade_planejada, p.taxa_horaria, p.setup_min,
                       p.hora_inicio_prevista, p.hora_fim_prevista, p.status
                FROM planejamento p
                LEFT JOIN controle_ops co ON co.id = p.op_id
                WHERE {where}
                ORDER BY p.linha, p.hora_inicio_prevista
            """, params)
            return cur.fetchall()


def familia_por_modelo(modelo: str) -> str | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT familia FROM producao_coletada WHERE modelo = %s AND familia IS NOT NULL AND familia <> '' LIMIT 1",
                (modelo,)
            )
            row = cur.fetchone()
            return row["familia"] if row else None


def cliente_por_modelo(modelo: str) -> str | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cliente FROM modelos WHERE UPPER(TRIM(codigo)) = UPPER(TRIM(%s)) AND cliente IS NOT NULL AND cliente <> '' LIMIT 1",
                (modelo,)
            )
            row = cur.fetchone()
            return row["cliente"] if row else None


def ops_abertas(setor: str = "") -> list:
    params = []
    setor_where = ""
    if setor:
        setor_where = "AND (co.setor = %s OR co.setor IS NULL)"
        params.append(setor)

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT id, numero_op, produto, filial, setor, saldo
                FROM (
                    SELECT
                        co.id, co.numero_op, co.produto, co.filial, co.setor,
                        co.quantidade, co.produzido,
                        mp.manual_total,
                        CASE WHEN co.fase_modelo = 'AMBAS' THEN
                            co.quantidade - LEAST(
                                COALESCE(SUM(CASE WHEN a.fase = 'TOP'    THEN a.quantidade ELSE 0 END), 0),
                                COALESCE(SUM(CASE WHEN a.fase = 'BOTTOM' THEN a.quantidade ELSE 0 END), 0)
                            )
                        ELSE GREATEST(0, co.quantidade - co.produzido - mp.manual_total)
                        END AS saldo
                    FROM controle_ops co
                    LEFT JOIN apontamento a ON a.op_id = co.id
                    LEFT JOIN LATERAL (
                        SELECT COALESCE(SUM(pc.producao_real), 0) AS manual_total
                        FROM producao_coletada pc
                        WHERE pc.modelo = co.produto
                          AND pc.setor  = co.setor
                          AND pc.origem = 'manual'
                          AND pc.producao_real > 0
                          AND NOT EXISTS (
                              SELECT 1 FROM apontamento av
                              WHERE av.data   = pc.data
                                AND av.turno  = pc.turno
                                AND av.modelo = pc.modelo
                                AND av.linha  = pc.linha
                                AND av.fase  IS NULL
                                AND av.op_id  = co.id
                          )
                    ) mp ON TRUE
                    WHERE 1=1 {setor_where}
                    GROUP BY co.id, co.numero_op, co.produto, co.filial, co.setor,
                             co.fase_modelo, co.quantidade, co.produzido, mp.manual_total
                ) sub
                WHERE saldo > 0
                ORDER BY numero_op
            """, params)
            return cur.fetchall()


def turno_intervalos(turno: str) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT hora_inicio, hora_fim
                FROM turno_config
                WHERE turno = %s
                ORDER BY ordem
            """, (turno,))
            return cur.fetchall()


def paradas_da_linha(setor: str, linha: str) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT hora_inicio, duracao_min, tipo, frequencia_dias
                FROM parada_config
                WHERE hora_inicio IS NOT NULL
                  AND (setor = %s OR setor IS NULL)
                  AND (linha = %s OR linha IS NULL)
                ORDER BY hora_inicio
            """, (setor, linha))
            return cur.fetchall()
