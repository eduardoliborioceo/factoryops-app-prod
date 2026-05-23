from app.extensions import get_db


def get_config(chave: str) -> str | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT valor FROM sync_config WHERE chave = %s", (chave,))
            row = cur.fetchone()
            return row["valor"] if row else None


def set_config(chave: str, valor: str) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_config (chave, valor, atualizado_em)
                VALUES (%s, %s, NOW())
                ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()
            """, (chave, valor))


def registrar_historico(tipo: str, status: str, buscados: int, salvos: int, erros: int, mensagem: str = None) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_historico (tipo, status, registros_buscados, salvos, erros, mensagem)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, status, buscados, salvos, erros, mensagem))


def listar_historico(limite: int = 50) -> list:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, executado_em, tipo, status, registros_buscados, salvos, erros, mensagem
                FROM sync_historico
                ORDER BY executado_em DESC
                LIMIT %s
            """, (limite,))
            return [dict(r) for r in cur.fetchall()]


def resumo() -> dict:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'done')  AS total_sucesso,
                    COUNT(*) FILTER (WHERE status = 'error') AS total_erro,
                    COUNT(*) FILTER (WHERE status = 'skip')  AS total_skip,
                    MAX(executado_em) FILTER (WHERE status = 'done') AS ultimo_sucesso,
                    MAX(executado_em) AS ultima_execucao
                FROM sync_historico
                WHERE executado_em >= NOW() - INTERVAL '7 days'
            """)
            return dict(cur.fetchone())
