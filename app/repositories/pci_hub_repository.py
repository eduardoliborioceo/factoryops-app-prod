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
    qtd_por_caixa: int | None = None,
) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                INSERT INTO pci_embalagem_sessao
                    (linha, usuario, op, modelo, cliente, turno, meta_hora, qtd_por_caixa)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, linha, usuario, op, modelo, cliente,
                          data::text, turno, meta_hora, qtd_por_caixa,
                          (iniciado_em AT TIME ZONE '{_TZ}')::text AS iniciado_em,
                          status
                """,
                (linha, usuario, op, modelo, cliente, turno, meta_hora, qtd_por_caixa),
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


def scans_no_intervalo(sessao_id: int, hora_inicio, hora_fim) -> int:
    """Conta scans no intervalo de tempo, suportando intervalos que cruzam meia-noite."""
    from datetime import time as _t
    spans = isinstance(hora_inicio, _t) and hora_inicio > hora_fim
    with get_db() as conn:
        with conn.cursor() as cur:
            if spans:
                cur.execute(
                    f"""
                    SELECT COUNT(*) FROM pci_embalagem_scan
                    WHERE sessao_id = %s
                      AND (
                            (scaneado_em AT TIME ZONE '{_TZ}')::time >= %s
                         OR (scaneado_em AT TIME ZONE '{_TZ}')::time <  %s
                      )
                    """,
                    (sessao_id, hora_inicio, hora_fim),
                )
            else:
                cur.execute(
                    f"""
                    SELECT COUNT(*) FROM pci_embalagem_scan
                    WHERE sessao_id = %s
                      AND (scaneado_em AT TIME ZONE '{_TZ}')::time >= %s
                      AND (scaneado_em AT TIME ZONE '{_TZ}')::time <  %s
                    """,
                    (sessao_id, hora_inicio, hora_fim),
                )
            return cur.fetchone()[0]


def listar_sessoes_filtradas(
    filial: str = "",
    setor: str = "",
    linha: str = "",
    data_inicial: str = "",
    data_final: str = "",
    limite: int = 300,
) -> list:
    filtros = ["1=1"]
    params: list = []

    if linha:
        filtros.append("s.linha ILIKE %s")
        params.append(f"%{linha}%")
    if data_inicial:
        filtros.append("s.data >= %s::date")
        params.append(data_inicial)
    if data_final:
        filtros.append("s.data <= %s::date")
        params.append(data_final)
    if filial:
        filtros.append("COALESCE(lc.filial, '') ILIKE %s")
        params.append(f"%{filial}%")
    if setor:
        filtros.append("COALESCE(lc.setor, '') ILIKE %s")
        params.append(f"%{setor}%")

    where = " AND ".join(filtros)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT s.id, s.linha, s.usuario, s.op, s.modelo, s.turno,
                       s.meta_hora, s.data::text, s.status,
                       (s.iniciado_em  AT TIME ZONE '{_TZ}')::text AS iniciado_em,
                       (s.finalizado_em AT TIME ZONE '{_TZ}')::text AS finalizado_em,
                       COALESCE(lc.filial, '') AS filial,
                       COALESCE(lc.setor,  '') AS setor,
                       COUNT(sc.id) AS total_scans
                FROM pci_embalagem_sessao s
                LEFT JOIN linha_config lc ON lc.linha = s.linha
                LEFT JOIN pci_embalagem_scan sc ON sc.sessao_id = s.id
                WHERE {where}
                GROUP BY s.id, s.linha, s.usuario, s.op, s.modelo, s.turno,
                         s.meta_hora, s.data, s.status,
                         s.iniciado_em, s.finalizado_em,
                         lc.filial, lc.setor
                ORDER BY s.iniciado_em DESC
                LIMIT %s
                """,
                params + [limite],
            )
            return cur.fetchall()


def listar_sessoes_abertas() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT id, linha, usuario, op, modelo, cliente,
                       data::text, turno, meta_hora, qtd_por_caixa,
                       (iniciado_em AT TIME ZONE '{_TZ}')::text AS iniciado_em,
                       status
                FROM pci_embalagem_sessao
                WHERE status = 'aberta'
                  AND data >= CURRENT_DATE - INTERVAL '1 day'
                ORDER BY iniciado_em DESC
                LIMIT 5
                """
            )
            return cur.fetchall()


def fechar_sessao(sessao_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pci_embalagem_sessao SET status = 'fechada', finalizado_em = NOW() WHERE id = %s",
                (sessao_id,),
            )
