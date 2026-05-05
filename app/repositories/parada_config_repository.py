from app.extensions import get_db
from psycopg.rows import dict_row


def listar() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT pc.id, pc.setor, pc.linha, pc.tipo, pc.turno,
                       pc.hora_inicio, pc.duracao_min, pc.frequencia_dias,
                       lc.filial
                FROM parada_config pc
                LEFT JOIN linha_config lc ON lc.linha = pc.linha
                ORDER BY pc.setor, pc.linha, pc.hora_inicio NULLS LAST, pc.turno
            """)
            return cur.fetchall()


def inserir(data: dict) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO parada_config (setor, linha, tipo, turno, hora_inicio, duracao_min, frequencia_dias)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("setor") or None,
                data.get("linha") or None,
                data["tipo"],
                data.get("turno") or None,
                data.get("hora_inicio") or None,
                data["duracao_min"],
                data.get("frequencia_dias") or None,
            ))


def excluir(parada_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM parada_config WHERE id = %s", (parada_id,))
