from app.extensions import get_db
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def listar() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, nome, dados FROM etiqueta_modelo ORDER BY nome"
            )
            return cur.fetchall()


def salvar(nome: str, dados: dict) -> int:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO etiqueta_modelo (nome, dados)
                VALUES (%s, %s)
                ON CONFLICT (nome)
                DO UPDATE SET dados = EXCLUDED.dados, atualizado_em = NOW()
                RETURNING id
                """,
                (nome, Jsonb(dados)),
            )
            return cur.fetchone()["id"]


def excluir(modelo_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM etiqueta_modelo WHERE id = %s", (modelo_id,))
