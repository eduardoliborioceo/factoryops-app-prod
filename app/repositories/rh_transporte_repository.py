from typing import Optional

from app.extensions import get_db
from psycopg.rows import dict_row


def listar_rotas(ativo: bool = True) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT r.id, r.codigo, r.nome, r.filial, r.turno, r.sentido,
                       r.regra_descida, r.veiculo, r.motorista, r.cor, r.ativo,
                       r.partida_nome,
                       r.partida_lat::FLOAT8  AS partida_lat,
                       r.partida_lng::FLOAT8  AS partida_lng,
                       r.criado_em, r.atualizado_em,
                       COUNT(c.id) AS total_colaboradores
                FROM rh_rota r
                LEFT JOIN rh_rota_colaborador c ON c.rota_id = r.id
                WHERE r.ativo = %s
                GROUP BY r.id
                ORDER BY r.turno, r.codigo
            """, (ativo,))
            return cur.fetchall()


def buscar_rota(rota_id: int) -> Optional[dict]:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, codigo, nome, filial, turno, sentido,
                       regra_descida, veiculo, motorista, cor, ativo,
                       partida_nome,
                       partida_lat::FLOAT8 AS partida_lat,
                       partida_lng::FLOAT8 AS partida_lng,
                       criado_em, atualizado_em
                FROM rh_rota
                WHERE id = %s
            """, (rota_id,))
            return cur.fetchone()


def criar_rota(codigo: str, nome: str, filial: str, turno: str, sentido: str,
               regra_descida: str, veiculo: str, motorista: str, cor: str,
               partida_nome: str, partida_lat: Optional[float],
               partida_lng: Optional[float]) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO rh_rota
                    (codigo, nome, filial, turno, sentido, regra_descida,
                     veiculo, motorista, cor, partida_nome, partida_lat, partida_lng)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id, codigo, nome, filial, turno, sentido,
                          regra_descida, veiculo, motorista, cor,
                          partida_nome,
                          partida_lat::FLOAT8 AS partida_lat,
                          partida_lng::FLOAT8 AS partida_lng,
                          ativo, criado_em
            """, (codigo, nome, filial or None, turno, sentido, regra_descida,
                  veiculo or None, motorista or None, cor,
                  partida_nome, partida_lat, partida_lng))
            conn.commit()
            return cur.fetchone()


def atualizar_rota(rota_id: int, **kwargs) -> Optional[dict]:
    allowed = {
        'nome', 'filial', 'turno', 'sentido', 'regra_descida',
        'veiculo', 'motorista', 'cor', 'ativo',
        'partida_nome', 'partida_lat', 'partida_lng'
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return None
    set_clause = ', '.join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [rota_id]
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""UPDATE rh_rota
                    SET {set_clause}, atualizado_em = NOW()
                    WHERE id = %s
                    RETURNING id, codigo, nome, filial, turno, sentido,
                              regra_descida, veiculo, motorista, cor, ativo,
                              partida_nome,
                              partida_lat::FLOAT8 AS partida_lat,
                              partida_lng::FLOAT8 AS partida_lng""",
                values
            )
            conn.commit()
            return cur.fetchone()


def deletar_rota(rota_id: int) -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_rota WHERE id = %s", (rota_id,))
            conn.commit()
            return cur.rowcount > 0


def listar_colaboradores_rota(rota_id: int) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT c.id, c.rota_id, c.employee_id, c.nome,
                       c.endereco_rua, c.endereco_numero, c.endereco_bairro,
                       c.endereco_cidade, c.endereco_estado,
                       c.lat::FLOAT8  AS lat,
                       c.lng::FLOAT8  AS lng,
                       c.geocodificado, c.ordem, c.tipo_parada, c.observacao,
                       c.criado_em,
                       e.employee_code, e.job_title, e.department
                FROM rh_rota_colaborador c
                LEFT JOIN employees e ON e.id = c.employee_id
                WHERE c.rota_id = %s
                ORDER BY c.ordem, c.id
            """, (rota_id,))
            return cur.fetchall()


def adicionar_colaborador(rota_id: int, employee_id: Optional[int], nome: str,
                          rua: str, numero: str, bairro: str,
                          cidade: str, estado: str,
                          tipo_parada: str, observacao: str) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT COALESCE(MAX(ordem), 0) + 1 FROM rh_rota_colaborador WHERE rota_id = %s",
                (rota_id,)
            )
            ordem = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO rh_rota_colaborador
                    (rota_id, employee_id, nome, endereco_rua, endereco_numero,
                     endereco_bairro, endereco_cidade, endereco_estado,
                     tipo_parada, observacao, ordem)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id, rota_id, employee_id, nome,
                          endereco_rua, endereco_numero, endereco_bairro,
                          endereco_cidade, endereco_estado,
                          lat::FLOAT8 AS lat, lng::FLOAT8 AS lng,
                          geocodificado, ordem, tipo_parada, observacao
            """, (rota_id, employee_id, nome, rua or None, numero or None,
                  bairro or None, cidade or 'Manaus', estado or 'AM',
                  tipo_parada, observacao or None, ordem))
            conn.commit()
            return cur.fetchone()


def atualizar_colaborador(colab_id: int, **kwargs) -> Optional[dict]:
    allowed = {
        'nome', 'endereco_rua', 'endereco_numero', 'endereco_bairro',
        'endereco_cidade', 'endereco_estado',
        'lat', 'lng', 'geocodificado', 'ordem', 'tipo_parada', 'observacao'
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return None
    set_clause = ', '.join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [colab_id]
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""UPDATE rh_rota_colaborador
                    SET {set_clause}
                    WHERE id = %s
                    RETURNING id, nome, endereco_bairro, endereco_cidade,
                              lat::FLOAT8 AS lat, lng::FLOAT8 AS lng, geocodificado""",
                values
            )
            conn.commit()
            return cur.fetchone()


def remover_colaborador(colab_id: int) -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rh_rota_colaborador WHERE id = %s", (colab_id,))
            conn.commit()
            return cur.rowcount > 0


def atualizar_ordem(rota_id: int, ids_ordenados: list) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            for i, colab_id in enumerate(ids_ordenados):
                cur.execute(
                    "UPDATE rh_rota_colaborador SET ordem = %s WHERE id = %s AND rota_id = %s",
                    (i + 1, colab_id, rota_id)
                )
        conn.commit()


def buscar_employees(termo: str, limit: int = 10) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            like = f"%{termo}%"
            cur.execute("""
                SELECT id, employee_code, full_name, job_title, department, branch_name
                FROM employees
                WHERE status = 'ACTIVE'
                  AND (LOWER(full_name) LIKE LOWER(%s) OR employee_code LIKE %s)
                ORDER BY full_name
                LIMIT %s
            """, (like, like, limit))
            return cur.fetchall()
