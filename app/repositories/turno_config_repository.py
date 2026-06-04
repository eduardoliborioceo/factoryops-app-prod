from app.extensions import get_db
from psycopg.rows import dict_row


def listar() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, turno, hora_inicio, hora_fim, ordem
                FROM turno_config
                ORDER BY ordem
            """)
            return cur.fetchall()


def inserir(turno: str, hora_inicio: str, hora_fim: str, ordem: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO turno_config (turno, hora_inicio, hora_fim, ordem)
                VALUES (%s, %s, %s, %s)
            """, (turno, hora_inicio, hora_fim, ordem))


def excluir(id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM turno_config WHERE id = %s", (id,))


def buscar_horario(turno: str) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    (SELECT hora_inicio FROM turno_config WHERE turno = %s ORDER BY ordem ASC  LIMIT 1) AS hora_inicio,
                    (SELECT hora_fim    FROM turno_config WHERE turno = %s ORDER BY ordem DESC LIMIT 1) AS hora_fim
            """, (turno, turno))
            return cur.fetchone()


def listar_nomes_unicos() -> list:
    import re
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT REPLACE(REPLACE(turno, '§', 'º'), '°', 'º') AS turno
                FROM turno_config
                GROUP BY REPLACE(REPLACE(turno, '§', 'º'), '°', 'º')
            """)
            nomes = [r["turno"] for r in cur.fetchall()]

    def _chave(nome):
        m = re.match(r'(\d+)', nome or '')
        return (int(m.group(1)) if m else 999, nome)

    return sorted(nomes, key=_chave)


def listar_por_turno(turno: str) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, turno, hora_inicio, hora_fim, ordem
                FROM turno_config
                WHERE REPLACE(REPLACE(turno, '§', 'º'), '°', 'º') = %s
                ORDER BY ordem
            """, (turno,))
            return cur.fetchall()


def proximo_ordem(turno: str) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(ordem), 0) + 1 AS proximo FROM turno_config WHERE turno = %s",
                (turno,)
            )
            return cur.fetchone()["proximo"]
