from app.extensions import get_db
from psycopg.rows import dict_row


def listar(ativo: bool = True) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT p.id, p.nome, p.modelo, p.cliente, p.familia,
                       p.qtd_por_caixa, p.meta_hora, p.ativo,
                       p.roteiro_id, r.nome AS roteiro_nome,
                       p.criado_em::text
                FROM pci_modelo_padrao p
                LEFT JOIN roteiros r ON r.id = p.roteiro_id
                WHERE p.ativo = %s
                ORDER BY p.nome
                """,
                (ativo,),
            )
            return cur.fetchall()


def buscar_por_id(modelo_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT p.*, p.criado_em::text,
                       r.nome AS roteiro_nome
                FROM pci_modelo_padrao p
                LEFT JOIN roteiros r ON r.id = p.roteiro_id
                WHERE p.id = %s
                """,
                (modelo_id,),
            )
            return cur.fetchone()


def buscar_por_modelo(modelo: str) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, nome, modelo, cliente, familia,
                       qtd_por_caixa, meta_hora, mascara_etiqueta
                FROM pci_modelo_padrao
                WHERE modelo ILIKE %s AND ativo = TRUE
                ORDER BY criado_em DESC
                LIMIT 1
                """,
                (modelo,),
            )
            return cur.fetchone()


def criar(dados: dict) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pci_modelo_padrao
                    (nome, modelo, cliente, familia, qtd_por_caixa,
                     meta_hora, mascara_etiqueta, roteiro_id)
                VALUES (%(nome)s, %(modelo)s, %(cliente)s, %(familia)s,
                        %(qtd_por_caixa)s, %(meta_hora)s,
                        %(mascara_etiqueta)s, %(roteiro_id)s)
                RETURNING id
                """,
                dados,
            )
            return cur.fetchone()[0]


def atualizar(modelo_id: int, dados: dict) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pci_modelo_padrao SET
                    nome=%(nome)s, modelo=%(modelo)s, cliente=%(cliente)s,
                    familia=%(familia)s, qtd_por_caixa=%(qtd_por_caixa)s,
                    meta_hora=%(meta_hora)s, mascara_etiqueta=%(mascara_etiqueta)s,
                    roteiro_id=%(roteiro_id)s, ativo=%(ativo)s
                WHERE id=%(id)s
                """,
                {**dados, "id": modelo_id},
            )


def excluir(modelo_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pci_modelo_padrao SET ativo = FALSE WHERE id = %s",
                (modelo_id,),
            )
