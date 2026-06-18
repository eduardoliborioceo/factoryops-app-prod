import json
from app.extensions import get_db
from psycopg.rows import dict_row


_DEFAULTS = {
    "nome_empresa": "Venttos Electronics",
    "nome_exibicao": "",
    "cnpj": "",
    "logo_url": None,
    "filiais": ["VTE", "VTT"],
    "filiais_extra": "",
    "endereco": {},
    "menu_visivel": {
        "funcionalidades": True,
        "producao": True,
        "engenharia": True,
        "pcp": True,
        "logistica": True,
        "configuracoes": True,
    },
    "setores_por_filial": {
        "VTE": ["SMD", "PTH", "IM/PA"],
        "VTT": ["SMD"],
    },
}


def get_config() -> dict:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM empresa_config WHERE id = 1")
            row = cur.fetchone()
    if not row:
        return dict(_DEFAULTS)
    result = dict(_DEFAULTS)
    result.update({k: v for k, v in dict(row).items() if v is not None})
    if isinstance(result.get("filiais"), str):
        result["filiais"] = json.loads(result["filiais"])
    if isinstance(result.get("menu_visivel"), str):
        result["menu_visivel"] = json.loads(result["menu_visivel"])
    if isinstance(result.get("setores_por_filial"), str):
        result["setores_por_filial"] = json.loads(result["setores_por_filial"])
    if isinstance(result.get("endereco"), str):
        result["endereco"] = json.loads(result["endereco"])
    if not isinstance(result.get("endereco"), dict):
        result["endereco"] = {}
    return result


def update_config(data: dict) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO empresa_config (id, nome_empresa, nome_exibicao, cnpj,
                    filiais, filiais_extra, endereco, menu_visivel, setores_por_filial, atualizado_em)
                VALUES (1, %s, %s, %s, %s::jsonb, %s, %s::jsonb, %s::jsonb, %s::jsonb, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    nome_empresa        = EXCLUDED.nome_empresa,
                    nome_exibicao       = EXCLUDED.nome_exibicao,
                    cnpj                = EXCLUDED.cnpj,
                    filiais             = EXCLUDED.filiais,
                    filiais_extra       = EXCLUDED.filiais_extra,
                    endereco            = EXCLUDED.endereco,
                    menu_visivel        = EXCLUDED.menu_visivel,
                    setores_por_filial  = EXCLUDED.setores_por_filial,
                    atualizado_em       = NOW()
            """, (
                data.get("nome_empresa", "Venttos Electronics"),
                data.get("nome_exibicao") or None,
                data.get("cnpj") or None,
                json.dumps(data.get("filiais", ["VTE", "VTT"])),
                data.get("filiais_extra") or None,
                json.dumps(data.get("endereco") or {}),
                json.dumps(data.get("menu_visivel", _DEFAULTS["menu_visivel"])),
                json.dumps(data.get("setores_por_filial", _DEFAULTS["setores_por_filial"])),
            ))


def update_logo(logo_url: str | None) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO empresa_config (id, logo_url, atualizado_em)
                VALUES (1, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    logo_url = EXCLUDED.logo_url,
                    atualizado_em = NOW()
            """, (logo_url,))
