from app.extensions import get_db
from psycopg.rows import dict_row

_TZ = "America/Manaus"


def criar_sessao(
    linha: str,
    usuario: str,
    op: str,
    modelo: str | None,
    cliente: str | None,
    turno: str | None,
    meta_hora: int | None,
) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                INSERT INTO pci_embalagem_sessao
                    (linha, usuario, op, modelo, cliente, turno, meta_hora)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, linha, usuario, op, modelo, cliente,
                          data::text, turno, meta_hora,
                          (iniciado_em AT TIME ZONE '{_TZ}')::text AS iniciado_em,
                          status
                """,
                (linha, usuario, op, modelo, cliente, turno, meta_hora),
            )
            return cur.fetchone()


def buscar_sessao(sessao_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT id, linha, usuario, op, modelo, cliente,
                       data::text, turno, meta_hora,
                       (iniciado_em AT TIME ZONE '{_TZ}')::text AS iniciado_em,
                       status
                FROM pci_embalagem_sessao WHERE id = %s
                """,
                (sessao_id,),
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
                f"""
                INSERT INTO pci_embalagem_scan (sessao_id, serial)
                VALUES (%s, %s)
                RETURNING id, serial,
                          (scaneado_em AT TIME ZONE '{_TZ}')::text AS scaneado_em,
                          impresso
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


def listar_scans(sessao_id: int, limite: int = 150) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT id, serial,
                       (scaneado_em AT TIME ZONE '{_TZ}')::text AS scaneado_em,
                       impresso
                FROM pci_embalagem_scan
                WHERE sessao_id = %s
                ORDER BY scaneado_em DESC
                LIMIT %s
                """,
                (sessao_id, limite),
            )
            return cur.fetchall()


def scans_no_intervalo(
    sessao_id: int, data_sessao: str, hora_inicio, hora_fim
) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*) FROM pci_embalagem_scan
                WHERE sessao_id = %s
                  AND DATE(scaneado_em AT TIME ZONE '{_TZ}') = %s::date
                  AND (scaneado_em AT TIME ZONE '{_TZ}')::time >= %s
                  AND (scaneado_em AT TIME ZONE '{_TZ}')::time <  %s
                """,
                (sessao_id, data_sessao, hora_inicio, hora_fim),
            )
            return cur.fetchone()[0]


def fechar_sessao(sessao_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pci_embalagem_sessao SET status = 'fechada', finalizado_em = NOW() WHERE id = %s",
                (sessao_id,),
            )
