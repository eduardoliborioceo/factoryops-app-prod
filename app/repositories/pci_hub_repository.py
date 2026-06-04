from app.extensions import get_db
from psycopg.rows import dict_row


def criar_sessao(linha: str, usuario: str, op: str, modelo: str | None, cliente: str | None, turno: str | None) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO pci_embalagem_sessao (linha, usuario, op, modelo, cliente, turno)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, linha, usuario, op, modelo, cliente,
                          data::text, turno, iniciado_em::text, status
                """,
                (linha, usuario, op, modelo, cliente, turno),
            )
            return cur.fetchone()


def registrar_scan(sessao_id: int, serial: str) -> tuple[dict | None, str | None]:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id FROM pci_embalagem_scan WHERE sessao_id = %s AND serial = %s",
                (sessao_id, serial),
            )
            if cur.fetchone():
                return None, "duplicado"
            cur.execute(
                """
                INSERT INTO pci_embalagem_scan (sessao_id, serial)
                VALUES (%s, %s)
                RETURNING id, serial, scaneado_em::text, impresso
                """,
                (sessao_id, serial),
            )
            return cur.fetchone(), None


def contar_scans(sessao_id: int) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM pci_embalagem_scan WHERE sessao_id = %s",
                (sessao_id,),
            )
            return cur.fetchone()[0]


def listar_scans(sessao_id: int, limite: int = 100) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, serial, scaneado_em::text, impresso
                FROM pci_embalagem_scan
                WHERE sessao_id = %s
                ORDER BY scaneado_em DESC
                LIMIT %s
                """,
                (sessao_id, limite),
            )
            return cur.fetchall()


def fechar_sessao(sessao_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pci_embalagem_sessao SET status = 'fechada', finalizado_em = NOW() WHERE id = %s",
                (sessao_id,),
            )
