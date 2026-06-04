import json
from app.extensions import get_db
from psycopg.rows import dict_row

_TZ = "America/Manaus"

_SLOTS = [
    (1,  "07:00", "08:00"), (2,  "08:00", "09:00"), (3,  "09:00", "10:00"),
    (4,  "10:00", "11:00"), (5,  "11:00", "12:00"), (6,  "12:00", "13:00"),
    (7,  "13:00", "14:00"), (8,  "14:00", "15:00"), (9,  "15:00", "16:00"),
    (10, "16:00", "17:00"), (11, "17:00", "18:00"), (12, "18:00", "19:00"),
    (13, "19:00", "20:00"), (14, "20:00", "21:00"), (15, "21:00", "22:00"),
    (16, "22:00", "23:00"), (17, "23:00", "00:00"), (18, "00:00", "01:00"),
    (19, "01:00", "02:00"), (20, "02:00", "03:00"),
]


def slots_padrao() -> list[dict]:
    return [{"slot_ordem": o, "hora_ini": hi, "hora_fim": hf} for o, hi, hf in _SLOTS]


def criar_relatorio(dados: dict) -> int:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pci_revisao_relatorio (
                    cliente, produto, setor, linha, posto, turno,
                    tipo_revisao, identificacao, meta, op, data, revisor, criado_por,
                    proc_top, proc_bot, proc_topbot, proc_lado01, proc_lado02, proc_aoi,
                    proc_pre_forno, proc_pos_forno, proc_pre_maq, proc_pos_maq,
                    proc_adesivo, proc_spi,
                    total_produzido, total_defeitos, total_scrap, status
                ) VALUES (
                    %(cliente)s, %(produto)s, %(setor)s, %(linha)s, %(posto)s, %(turno)s,
                    %(tipo_revisao)s, %(identificacao)s, %(meta)s, %(op)s, %(data)s,
                    %(revisor)s, %(criado_por)s,
                    %(proc_top)s, %(proc_bot)s, %(proc_topbot)s, %(proc_lado01)s,
                    %(proc_lado02)s, %(proc_aoi)s, %(proc_pre_forno)s, %(proc_pos_forno)s,
                    %(proc_pre_maq)s, %(proc_pos_maq)s, %(proc_adesivo)s, %(proc_spi)s,
                    %(total_produzido)s, %(total_defeitos)s, %(total_scrap)s, %(status)s
                )
                RETURNING id
                """,
                dados,
            )
            rel_id = cur.fetchone()[0]
        return rel_id


def salvar_horas(relatorio_id: int, horas: list[dict]) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_revisao_hora WHERE relatorio_id = %s", (relatorio_id,))
            for h in horas:
                cur.execute(
                    """
                    INSERT INTO pci_revisao_hora (
                        relatorio_id, slot_ordem, hora_ini, hora_fim,
                        selecionado, aprovados, reprovados, defeitos_max,
                        modelo, qtd_produzida, placa_hh, fase, revisora, observacao
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        relatorio_id, h["slot_ordem"], h["hora_ini"], h["hora_fim"],
                        h.get("selecionado", False),
                        h.get("aprovados"), h.get("reprovados"), h.get("defeitos_max"),
                        h.get("modelo"), h.get("qtd_produzida"),
                        h.get("placa_hh"), h.get("fase"),
                        h.get("revisora"), h.get("observacao"),
                    ),
                )


def salvar_defeitos(relatorio_id: int, defeitos: list[dict]) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_revisao_defeito WHERE relatorio_id = %s", (relatorio_id,))
            for d in defeitos:
                cur.execute(
                    """
                    INSERT INTO pci_revisao_defeito (
                        relatorio_id, linha_ordem, codigo_defeito,
                        posicao_mecanica, lado, qtd_por_hora, observacao
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        relatorio_id, d["linha_ordem"],
                        d.get("codigo_defeito"), d.get("posicao_mecanica"),
                        d.get("lado"), json.dumps(d.get("qtd_por_hora", {})),
                        d.get("observacao"),
                    ),
                )


def atualizar_cabecalho(relatorio_id: int, dados: dict) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pci_revisao_relatorio SET
                    cliente=%(cliente)s, produto=%(produto)s, setor=%(setor)s,
                    linha=%(linha)s, posto=%(posto)s, turno=%(turno)s,
                    tipo_revisao=%(tipo_revisao)s, identificacao=%(identificacao)s,
                    meta=%(meta)s, op=%(op)s, data=%(data)s, revisor=%(revisor)s,
                    proc_top=%(proc_top)s, proc_bot=%(proc_bot)s, proc_topbot=%(proc_topbot)s,
                    proc_lado01=%(proc_lado01)s, proc_lado02=%(proc_lado02)s, proc_aoi=%(proc_aoi)s,
                    proc_pre_forno=%(proc_pre_forno)s, proc_pos_forno=%(proc_pos_forno)s,
                    proc_pre_maq=%(proc_pre_maq)s, proc_pos_maq=%(proc_pos_maq)s,
                    proc_adesivo=%(proc_adesivo)s, proc_spi=%(proc_spi)s,
                    total_produzido=%(total_produzido)s, total_defeitos=%(total_defeitos)s,
                    total_scrap=%(total_scrap)s, status=%(status)s
                WHERE id = %(id)s
                """,
                {**dados, "id": relatorio_id},
            )


def buscar_relatorio(relatorio_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT *, data::text,
                       (criado_em AT TIME ZONE '{_TZ}')::text AS criado_em_local
                FROM pci_revisao_relatorio WHERE id = %s
                """,
                (relatorio_id,),
            )
            rel = cur.fetchone()
            if not rel:
                return None
            cur.execute(
                "SELECT * FROM pci_revisao_hora WHERE relatorio_id = %s ORDER BY slot_ordem",
                (relatorio_id,),
            )
            rel["horas"] = cur.fetchall()
            cur.execute(
                "SELECT * FROM pci_revisao_defeito WHERE relatorio_id = %s ORDER BY linha_ordem",
                (relatorio_id,),
            )
            rel["defeitos"] = cur.fetchall()
            return rel


def listar_relatorios(linha: str = "", data_ini: str = "", data_fim: str = "") -> list:
    filtros = ["1=1"]
    params: list = []
    if linha:
        filtros.append("linha ILIKE %s")
        params.append(f"%{linha}%")
    if data_ini:
        filtros.append("data >= %s::date")
        params.append(data_ini)
    if data_fim:
        filtros.append("data <= %s::date")
        params.append(data_fim)
    where = " AND ".join(filtros)
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT id, cliente, produto, setor, linha, op, data::text,
                       revisor, turno, tipo_revisao, status,
                       total_produzido, total_defeitos,
                       (criado_em AT TIME ZONE '{_TZ}')::text AS criado_em_local
                FROM pci_revisao_relatorio
                WHERE {where}
                ORDER BY data DESC, criado_em DESC
                LIMIT 200
                """,
                params,
            )
            return cur.fetchall()


def excluir_relatorio(relatorio_id: int) -> None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pci_revisao_relatorio WHERE id = %s", (relatorio_id,))
