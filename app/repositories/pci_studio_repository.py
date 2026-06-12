import json
from typing import Optional

from app.extensions import get_db
from psycopg.rows import dict_row


# ── Projetos ──

def listar_projetos() -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT p.id, p.nome, p.codigo, p.descricao,
                       p.comp_mm::FLOAT8, p.larg_mm::FLOAT8, p.esp_mm::FLOAT8, p.cor_placa,
                       p.criado_em, p.atualizado_em,
                       COUNT(b.id) AS total_itens,
                       COUNT(b.id) FILTER (WHERE b.ativo) AS itens_ativos
                FROM pci_projeto p
                LEFT JOIN pci_bom_item b ON b.projeto_id = p.id
                GROUP BY p.id
                ORDER BY p.atualizado_em DESC NULLS LAST
            """)
            return cur.fetchall()


def buscar_projeto(projeto_id: int) -> Optional[dict]:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, nome, codigo, descricao,
                       comp_mm::FLOAT8, larg_mm::FLOAT8, esp_mm::FLOAT8, cor_placa,
                       img_top, img_bottom, docs,
                       criado_em, atualizado_em
                FROM pci_projeto WHERE id = %s
            """, (projeto_id,))
            row = cur.fetchone()
            if row:
                row = dict(row)
                if row.get('docs') is None:
                    row['docs'] = []
            return row


def buscar_projeto_com_bom(projeto_id: int) -> Optional[dict]:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT p.id, p.nome, p.codigo, p.descricao,
                       p.comp_mm::FLOAT8, p.larg_mm::FLOAT8, p.esp_mm::FLOAT8, p.cor_placa,
                       p.img_top, p.img_bottom, p.docs,
                       p.criado_em, p.atualizado_em
                FROM pci_projeto p WHERE p.id = %s
            """, (projeto_id,))
            projeto = cur.fetchone()
            if not projeto:
                return None

            cur.execute("""
                SELECT b.id, b.designator, b.valor, b.part_number,
                       COALESCE(c.package, b.package) AS package,
                       COALESCE(b.descricao, c.descricao) AS descricao,
                       b.tipo,
                       b.pos_x::FLOAT8  AS pos_x,
                       b.pos_y::FLOAT8  AS pos_y,
                       b.angulo::FLOAT8 AS angulo,
                       b.lado, b.ativo,
                       COALESCE(b.comp_mm::FLOAT8, c.comp_mm::FLOAT8, 2.0) AS comp_mm,
                       COALESCE(b.larg_mm::FLOAT8, c.larg_mm::FLOAT8, 2.0) AS larg_mm,
                       COALESCE(c.alt_mm::FLOAT8,  1.0) AS alt_mm,
                       COALESCE(c.cor_hex, '#64748b') AS cor_hex,
                       b.componente_id
                FROM pci_bom_item b
                LEFT JOIN pci_componente c ON c.id = b.componente_id
                WHERE b.projeto_id = %s
                ORDER BY b.designator
            """, (projeto_id,))
            itens = cur.fetchall()

    p = dict(projeto)
    if p.get('docs') is None:
        p['docs'] = []
    return {**p, 'itens': [dict(i) for i in itens]}


def criar_projeto(nome: str, codigo: str, descricao: str,
                  comp_mm: float, larg_mm: float, esp_mm: float,
                  cor_placa: str, criado_por: Optional[int]) -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO pci_projeto
                    (nome, codigo, descricao, comp_mm, larg_mm, esp_mm, cor_placa, criado_por)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id, nome, codigo, descricao,
                          comp_mm::FLOAT8, larg_mm::FLOAT8, esp_mm::FLOAT8, cor_placa, criado_em
            """, (nome, codigo or None, descricao or None,
                  comp_mm, larg_mm, esp_mm, cor_placa, criado_por))
            conn.commit()
            return cur.fetchone()


def atualizar_projeto(projeto_id: int, **kwargs) -> Optional[dict]:
    allowed = {'nome', 'codigo', 'descricao', 'comp_mm', 'larg_mm', 'esp_mm', 'cor_placa',
               'img_top', 'img_bottom', 'docs'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return None
    set_clause = ', '.join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [projeto_id]
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"UPDATE pci_projeto SET {set_clause}, atualizado_em = NOW()"
                f" WHERE id = %s RETURNING id, nome, codigo, comp_mm::FLOAT8, larg_mm::FLOAT8",
                values
            )
            conn.commit()
            return cur.fetchone()


def deletar_projeto(projeto_id: int) -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_projeto WHERE id = %s", (projeto_id,))
            conn.commit()
            return cur.rowcount > 0


def adicionar_doc_projeto(projeto_id: int, doc: dict) -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pci_projeto
                SET docs = COALESCE(docs, '[]'::jsonb) || %s::jsonb,
                    atualizado_em = NOW()
                WHERE id = %s
            """, (json.dumps([doc]), projeto_id))
            conn.commit()
            return cur.rowcount > 0


# ── BOM Items ──

def inserir_bom_items(projeto_id: int, items: list) -> int:
    if not items:
        return 0
    with get_db() as conn:
        with conn.cursor() as cur:
            count = 0
            for item in items:
                cur.execute("""
                    INSERT INTO pci_bom_item
                        (projeto_id, designator, valor, part_number, package,
                         descricao, tipo, pos_x, pos_y, angulo, lado, componente_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, (
                    projeto_id,
                    item.get('designator'),
                    item.get('valor'),
                    item.get('part_number'),
                    item.get('package'),
                    item.get('descricao'),
                    item.get('tipo', 'smd'),
                    item.get('pos_x'),
                    item.get('pos_y'),
                    item.get('angulo', 0),
                    item.get('lado', 'top'),
                    item.get('componente_id'),
                ))
                count += 1
            conn.commit()
    return count


def atualizar_bom_item(item_id: int, **kwargs) -> Optional[dict]:
    allowed = {'ativo', 'pos_x', 'pos_y', 'angulo', 'comp_mm', 'larg_mm',
               'componente_id', 'valor', 'package', 'descricao', 'tipo', 'lado'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return None
    set_clause = ', '.join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [item_id]
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"UPDATE pci_bom_item SET {set_clause} WHERE id = %s"
                f" RETURNING id, designator, ativo, componente_id",
                values
            )
            conn.commit()
            return cur.fetchone()


def deletar_bom_items_projeto(projeto_id: int) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_bom_item WHERE projeto_id = %s", (projeto_id,))
            count = cur.rowcount
            conn.commit()
    return count


# ── Componentes (library) ──

def listar_componentes(tipo: Optional[str] = None) -> list:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if tipo:
                cur.execute("""
                    SELECT id, part_number, descricao, fabricante, tipo, package,
                           comp_mm::FLOAT8, larg_mm::FLOAT8, alt_mm::FLOAT8,
                           cor_hex, datasheet_url, criado_em
                    FROM pci_componente WHERE tipo = %s ORDER BY package, part_number
                """, (tipo,))
            else:
                cur.execute("""
                    SELECT id, part_number, descricao, fabricante, tipo, package,
                           comp_mm::FLOAT8, larg_mm::FLOAT8, alt_mm::FLOAT8,
                           cor_hex, datasheet_url, criado_em
                    FROM pci_componente ORDER BY tipo, package, part_number
                """)
            return cur.fetchall()


def buscar_componentes_por_package(packages: list) -> dict:
    if not packages:
        return {}
    upper_pkgs = [p.upper() for p in packages]
    placeholders = ','.join(['%s'] * len(upper_pkgs))
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"""
                SELECT id, package, tipo, comp_mm::FLOAT8, larg_mm::FLOAT8,
                       alt_mm::FLOAT8, cor_hex
                FROM pci_componente
                WHERE UPPER(package) IN ({placeholders})
            """, upper_pkgs)
            return {r['package'].upper(): dict(r) for r in cur.fetchall()}


def criar_componente(**kwargs) -> dict:
    allowed = {'part_number', 'descricao', 'fabricante', 'tipo', 'package',
               'comp_mm', 'larg_mm', 'alt_mm', 'cor_hex', 'datasheet_url'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    cols = ', '.join(fields.keys())
    placeholders = ', '.join(['%s'] * len(fields))
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"INSERT INTO pci_componente ({cols}) VALUES ({placeholders})"
                f" RETURNING id, part_number, tipo, package, comp_mm::FLOAT8, larg_mm::FLOAT8, alt_mm::FLOAT8, cor_hex",
                list(fields.values())
            )
            conn.commit()
            return cur.fetchone()


def atualizar_componente(comp_id: int, **kwargs) -> Optional[dict]:
    allowed = {'part_number', 'descricao', 'fabricante', 'tipo', 'package',
               'comp_mm', 'larg_mm', 'alt_mm', 'cor_hex', 'datasheet_url'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return None
    set_clause = ', '.join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [comp_id]
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"UPDATE pci_componente SET {set_clause}, atualizado_em = NOW()"
                f" WHERE id = %s RETURNING id, part_number, tipo, package, cor_hex",
                values
            )
            conn.commit()
            return cur.fetchone()


def deletar_componente(comp_id: int) -> bool:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_componente WHERE id = %s", (comp_id,))
            conn.commit()
            return cur.rowcount > 0


def stats_biblioteca() -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE tipo = 'smd')     AS smd,
                    COUNT(*) FILTER (WHERE tipo = 'pth')     AS pth,
                    COUNT(*) FILTER (WHERE tipo = 'conector') AS conector,
                    COUNT(*) FILTER (WHERE tipo = 'outro')   AS outro
                FROM pci_componente
            """)
            return dict(cur.fetchone() or {})
