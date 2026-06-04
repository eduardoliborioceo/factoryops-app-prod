from app.extensions import get_db
from psycopg.rows import dict_row


def listar_motivos() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT codigo, origem, descricao, responsavel
                FROM motivo_parada WHERE ativo = TRUE ORDER BY origem, codigo
            """)
            return cur.fetchall()


def listar_defeitos() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT codigo, descricao, categoria
                FROM codigo_defeito WHERE ativo = TRUE ORDER BY categoria, codigo
            """)
            return cur.fetchall()


def buscar_lancamento(data: str, setor: str, linha: str, turno: str, hora_inicio: str) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT l.*,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', j.id, 'codigo_motivo', j.codigo_motivo,
                            'origem', j.origem, 'descricao', j.descricao,
                            'responsavel', j.responsavel,
                            'justificativa_texto', j.justificativa_texto,
                            'perda_minutos', j.perda_minutos
                        )) FILTER (WHERE j.id IS NOT NULL), '[]'
                    ) AS justificativas,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', d.id, 'codigo_defeito', d.codigo_defeito,
                            'posicao_mecanica', d.posicao_mecanica,
                            'quantidade', d.quantidade
                        )) FILTER (WHERE d.id IS NOT NULL), '[]'
                    ) AS defeitos
                FROM input_lancamento l
                LEFT JOIN input_justificativa j ON j.lancamento_id = l.id
                LEFT JOIN input_defeito d ON d.lancamento_id = l.id
                WHERE l.data = %s AND l.setor = %s AND l.linha = %s
                  AND l.turno = %s AND l.hora_inicio = %s
                GROUP BY l.id
            """, (data, setor, linha, turno, hora_inicio))
            return cur.fetchone()


def listar_historico(data_inicial: str, data_final: str,
                     filial: str = "", setor: str = "", linha: str = "", turno: str = "") -> list:
    filtros = ["l.data BETWEEN %s AND %s"]
    params = [data_inicial, data_final]
    if filial:
        filtros.append("l.filial = %s")
        params.append(filial)
    if setor:
        filtros.append("l.setor = %s")
        params.append(setor)
    if linha:
        filtros.append("l.linha = %s")
        params.append(linha)
    if turno:
        filtros.append("l.turno = %s")
        params.append(turno)
    where = " AND ".join(filtros)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT l.id, l.data, l.filial, l.setor, l.linha, l.turno,
                       l.hora_inicio, l.hora_fim, l.modelo, l.cliente, l.op,
                       l.fase, l.meta_hora, l.producao_real, l.total_defeitos,
                       l.criado_em,
                       COUNT(DISTINCT j.id) AS qtd_justificativas,
                       COUNT(DISTINCT d.id) AS qtd_defeitos
                FROM input_lancamento l
                LEFT JOIN input_justificativa j ON j.lancamento_id = l.id
                LEFT JOIN input_defeito d ON d.lancamento_id = l.id
                WHERE {where}
                GROUP BY l.id
                ORDER BY l.data DESC, l.setor, l.linha, l.hora_inicio
            """, params)
            return cur.fetchall()


def salvar_lancamento(data: dict, justificativas: list, defeitos: list, user_id: int | None) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO input_lancamento (
                    data, filial, setor, linha, turno, hora_inicio, hora_fim,
                    modelo, cliente, op, fase, meta_hora,
                    producao_real, total_defeitos, perda_segundos, planejamento_id, criado_por
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (data, setor, linha, turno, hora_inicio) DO UPDATE SET
                    filial          = EXCLUDED.filial,
                    hora_fim        = EXCLUDED.hora_fim,
                    modelo          = EXCLUDED.modelo,
                    cliente         = EXCLUDED.cliente,
                    op              = EXCLUDED.op,
                    fase            = EXCLUDED.fase,
                    meta_hora       = EXCLUDED.meta_hora,
                    producao_real   = EXCLUDED.producao_real,
                    total_defeitos  = EXCLUDED.total_defeitos,
                    perda_segundos  = EXCLUDED.perda_segundos,
                    planejamento_id = EXCLUDED.planejamento_id,
                    criado_por      = EXCLUDED.criado_por,
                    criado_em       = NOW()
                RETURNING id
            """, (
                data["data"], data["filial"], data["setor"], data["linha"],
                data["turno"], data["hora_inicio"], data["hora_fim"],
                data.get("modelo"), data.get("cliente"), data.get("op"),
                data.get("fase"), data.get("meta_hora"),
                data.get("producao_real", 0),
                sum(d.get("quantidade", 0) for d in defeitos),
                int(data.get("perda_segundos") or 0),
                data.get("planejamento_id"),
                user_id,
            ))
            lancamento_id = cur.fetchone()["id"]

            cur.execute("DELETE FROM input_justificativa WHERE lancamento_id = %s", (lancamento_id,))
            for j in justificativas:
                if not j.get("perda_minutos") and not j.get("justificativa_texto"):
                    continue
                cur.execute("""
                    INSERT INTO input_justificativa
                        (lancamento_id, codigo_motivo, origem, descricao, responsavel,
                         justificativa_texto, perda_minutos)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    lancamento_id,
                    j.get("codigo_motivo") or None,
                    j.get("origem") or None,
                    j.get("descricao") or None,
                    j.get("responsavel") or None,
                    j.get("justificativa_texto") or None,
                    int(j.get("perda_minutos") or 0),
                ))

            cur.execute("DELETE FROM input_defeito WHERE lancamento_id = %s", (lancamento_id,))
            for d in defeitos:
                if not d.get("codigo_defeito") or not d.get("quantidade"):
                    continue
                cur.execute("""
                    INSERT INTO input_defeito (lancamento_id, codigo_defeito, posicao_mecanica, quantidade)
                    VALUES (%s,%s,%s,%s)
                """, (
                    lancamento_id,
                    d["codigo_defeito"],
                    d.get("posicao_mecanica") or None,
                    int(d.get("quantidade") or 1),
                ))

            return lancamento_id


def excluir_lancamento(lancamento_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM input_lancamento WHERE id = %s", (lancamento_id,))
