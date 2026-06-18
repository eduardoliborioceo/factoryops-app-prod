from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.auth.decorators import admin_required
from app.services import time_studies_service


bp = Blueprint("pages", __name__)


@bp.route("/")
@login_required
def inicio():
    return render_template("inicio.html", active_menu="inicio")


@bp.route("/dashboard")
@login_required
def dashboard():
    filtros = {
        "data_inicial": "",
        "data_final": "",
        "turno": "",
        "filial": "",
    }

    kpis = {
        "absenteismo": 0,
        "linhas": 0,
    }

    return render_template(
        "dashboard.html",
        active_menu="dashboard",
        filtros=filtros,
        kpis=kpis,
        ranking_extras=[],
        ranking_objetivos=[],
        ranking_clientes=[],
        ranking_tipos_provisao=[],
    )


@bp.route("/powerbi")
@login_required
def powerbi():
    return render_template("powerbi.html", active_menu="powerbi")


@bp.route("/smt")
@login_required
def smt_home():
    return render_template("inicio.html", active_menu="inicio")


@bp.route("/smt/dashboard")
@login_required
def smt_dashboard():
    return render_template("inicio.html", active_menu="inicio")


@bp.route("/smt/modelos")
@login_required
def smt_modelos():
    return render_template("funcionalidades/modelos_smt.html", active_menu="smt_modelos")


@bp.route("/smt/cadastro")
@login_required
def smt_cadastro():
    return render_template("funcionalidades/cadastro.html", active_menu="smt_cadastro")


@bp.route("/smt/calcular")
@login_required
def smt_calcular():
    return render_template("funcionalidades/calcular.html", active_menu="smt_calcular")


@bp.route("/smt/estudo-tempo")
@login_required
def smt_estudo_tempo():
    return render_template("engenharia/estudo_tempo.html", active_menu="smt_estudo_tempo")


@bp.route("/smt/mais")
@login_required
def smt_mais():
    return render_template("mais.html", active_menu="smt_more")


@bp.route("/smt/estudo-tempo/print/<int:study_id>")
@login_required
def smt_estudo_tempo_print(study_id: int):
    detail = time_studies_service.get_study_detail(study_id)
    if not detail:
        return render_template(
            "engenharia/estudo_tempo_print.html",
            active_menu="smt_estudo_tempo",
            study=None,
            operations=[],
            totals={},
            not_found=True,
        )

    return render_template(
        "engenharia/estudo_tempo_print.html",
        active_menu="smt_estudo_tempo",
        study=detail.get("study"),
        operations=detail.get("operations") or [],
        totals=detail.get("totals") or {},
        not_found=False,
    )


# ─── Funcionalidades ────────────────────────────────────────────────────────

@bp.route("/funcionalidades/im-pa")
@login_required
def funcionalidades_im_pa():
    return render_template("funcionalidades/im_pa.html", active_menu="funcionalidades_im_pa")


@bp.route("/funcionalidades/pth")
@login_required
def funcionalidades_pth():
    return render_template("funcionalidades/pth.html", active_menu="funcionalidades_pth")


@bp.route("/funcionalidades/vtt")
@login_required
def funcionalidades_vtt():
    return render_template("funcionalidades/vtt.html", active_menu="funcionalidades_vtt")


# ─── Produção ────────────────────────────────────────────────────────────────

@bp.route("/producao/medicao-pasta-solda")
@login_required
def producao_medicao_pasta():
    return render_template("producao/medicao_pasta_solda.html", active_menu="producao_medicao_pasta")


@bp.route("/producao/checklist-verificacao-linha")
@login_required
def producao_checklist_linha():
    return render_template("producao/checklist_linha.html", active_menu="producao_checklist_linha")


@bp.route("/producao/checklist-verificacao-linha/<int:sessao_id>")
@login_required
def producao_checklist_detalhe(sessao_id: int):
    from app.services import checklist_service
    sessao = checklist_service.get_sessao_detail(sessao_id)
    return render_template(
        "producao/checklist_detalhe.html",
        active_menu="producao_checklist_linha",
        sessao=sessao,
    )


@bp.route("/producao/limpeza-stencil")
@login_required
def producao_limpeza_stencil():
    return render_template("producao/limpeza_stencil.html", active_menu="producao_limpeza_stencil")


@bp.route("/smd/monitor-tv")
@login_required
def smd_monitor_tv():
    from app.services import monitor_smd_service as svc
    try:
        dados = svc.get_status_atual()
        erro  = None
    except Exception as e:
        dados = {"linhas": [], "turno_nome": "—", "slots": [], "hoje": "", "atualizado_em": "", "tem_turno": False}
        erro  = str(e)
    return render_template(
        "producao/monitor_smd_tv.html",
        active_menu="smd_monitor_tv",
        dados=dados,
        erro=erro,
    )


# ─── Engenharia ──────────────────────────────────────────────────────────────

@bp.route("/engenharia/folha-cronometragem")
@login_required
def engenharia_folha_crono():
    return render_template("engenharia/folha_cronometragem.html", active_menu="engenharia_folha_crono")


# ─── PCP ─────────────────────────────────────────────────────────────────────

@bp.route("/pcp/lancamento-producao", methods=["GET"])
@login_required
@admin_required
def pcp_lancamento_producao():
    from flask import request
    from app.services import producao_manual_service as svc

    data_inicial_pad, data_final_pad = svc.data_padrao()

    data_inicial = request.args.get("dataInicial", data_inicial_pad)
    data_final   = request.args.get("dataFinal",   data_final_pad)
    setor        = request.args.get("setor",  "")
    linha        = request.args.get("linha",  "")
    turno        = request.args.get("turno",  "")

    try:
        registros = svc.listar(data_inicial, data_final, setor, linha, turno)
        filtros   = svc.filtros_disponiveis()
        erro      = None
    except Exception as e:
        registros = []
        filtros   = {"setores": [], "linhas_por_setor": {}}
        erro      = str(e)

    return render_template(
        "pcp/lancamento_producao.html",
        active_menu="pcp_lancamento_producao",
        data_inicial=data_inicial,
        data_final=data_final,
        setor=setor,
        linha=linha,
        turno=turno,
        registros=registros,
        filtros=filtros,
        erro=erro,
    )


@bp.route("/pcp/lancamento-producao/inserir", methods=["POST"])
@login_required
@admin_required
def pcp_lancamento_producao_inserir():
    from flask import request, redirect, url_for, flash
    from app.services import producao_manual_service as svc

    try:
        svc.inserir(request.form)
        flash("Produção lançada com sucesso.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Erro inesperado ao salvar o lançamento.", "danger")

    return redirect(url_for("pages.pcp_lancamento_producao"))


@bp.route("/pcp/lancamento-producao/excluir", methods=["POST"])
@login_required
@admin_required
def pcp_lancamento_producao_excluir():
    from flask import request, redirect, url_for, flash
    from app.services import producao_manual_service as svc

    try:
        registro_id = int(request.form.get("registro_id", 0))
        svc.excluir(registro_id)
        flash("Lançamento excluído.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Erro inesperado ao excluir o lançamento.", "danger")

    return redirect(url_for("pages.pcp_lancamento_producao"))


@bp.route("/pcp/etiquetas-manuais")
@login_required
def pcp_etiquetas_manuais():
    return render_template("pcp/etiquetas_manuais.html", active_menu="pcp_etiquetas_manuais")


@bp.route("/pcp/roteiros")
@login_required
@admin_required
def pcp_roteiros():
    from flask import request
    from app.services import roteiro_service as svc
    from app.repositories import linha_config_repository as lc_repo

    cliente = request.args.get("cliente", "")

    try:
        roteiros          = svc.listar(cliente)
        clientes_roteiros = svc.clientes_roteiros()
        clientes_modelos  = svc.clientes_modelos()
        linhas_config     = lc_repo.listar_por_filial_setor()
        erro              = None
    except Exception as e:
        roteiros          = []
        clientes_roteiros = []
        clientes_modelos  = []
        linhas_config     = {}
        erro              = str(e)

    return render_template(
        "pcp/roteiros.html",
        active_menu="pcp_roteiros",
        cliente=cliente,
        roteiros=roteiros,
        clientes_roteiros=clientes_roteiros,
        clientes_modelos=clientes_modelos,
        linhas_config=linhas_config,
        erro=erro,
    )


@bp.route("/pcp/roteiros/criar", methods=["POST"])
@login_required
@admin_required
def pcp_roteiros_criar():
    from flask import request, jsonify
    from app.services import roteiro_service as svc
    import json

    try:
        dados = request.get_json(force=True)
        roteiro_id = svc.criar(dados)
        return jsonify({"ok": True, "id": roteiro_id})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro inesperado ao criar roteiro."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/editar", methods=["POST"])
@login_required
@admin_required
def pcp_roteiros_editar(roteiro_id):
    from flask import request, jsonify
    from app.services import roteiro_service as svc

    try:
        dados = request.get_json(force=True)
        svc.editar(roteiro_id, dados)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro inesperado ao editar roteiro."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/excluir", methods=["POST"])
@login_required
@admin_required
def pcp_roteiros_excluir(roteiro_id):
    from flask import jsonify
    from app.services import roteiro_service as svc

    try:
        svc.excluir(roteiro_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro inesperado ao excluir roteiro."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/modelos", methods=["GET"])
@login_required
@admin_required
def pcp_roteiros_modelos(roteiro_id):
    from flask import jsonify
    from app.services import roteiro_service as svc

    try:
        modelos = svc.modelos_do_roteiro(roteiro_id)
        return jsonify({"ok": True, "modelos": modelos})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao carregar modelos."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/vincular-modelo", methods=["POST"])
@login_required
@admin_required
def pcp_roteiros_vincular_modelo(roteiro_id):
    from flask import request, jsonify
    from app.services import roteiro_service as svc

    try:
        dados = request.get_json(force=True)
        svc.vincular_modelo(roteiro_id, dados.get("codigo", ""))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao vincular modelo."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/desvincular-modelo", methods=["POST"])
@login_required
@admin_required
def pcp_roteiros_desvincular_modelo(roteiro_id):
    from flask import request, jsonify
    from app.services import roteiro_service as svc

    try:
        dados = request.get_json(force=True)
        svc.desvincular_modelo(roteiro_id, dados.get("codigo", ""))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao desvincular modelo."}), 500


@bp.route("/pcp/roteiros/<int:roteiro_id>/codigos-cliente")
@login_required
@admin_required
def pcp_roteiros_codigos_cliente(roteiro_id):
    from flask import jsonify
    from app.services import roteiro_service as svc

    try:
        roteiro = svc.buscar(roteiro_id)
        codigos = svc.codigos_por_cliente(roteiro["cliente"])
        return jsonify({"ok": True, "codigos": codigos})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 404
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao carregar códigos."}), 500


@bp.route("/pcp/producao-coletada")
@login_required
@admin_required
def pcp_producao_coletada():
    from flask import request
    from app.services import producao_coletada_service as svc

    data_inicial_pad, data_final_pad = svc.data_padrao()

    data_inicial = request.args.get("dataInicial", data_inicial_pad)
    data_final   = request.args.get("dataFinal",   data_final_pad)
    setor        = request.args.get("setor",  "")
    linha        = request.args.get("linha",  "")
    turno        = request.args.get("turno",  "")

    try:
        registros = svc.listar(data_inicial, data_final, setor, linha, turno)
        kpis      = svc.totais(data_inicial, data_final, setor, linha, turno)
        filtros   = svc.filtros_disponiveis(setor)
        erro      = None
    except Exception as e:
        registros = []
        kpis      = {}
        filtros   = {"setores": [], "linhas": []}
        erro      = str(e)

    return render_template(
        "pcp/producao_coletada.html",
        active_menu="pcp_producao_coletada",
        data_inicial=data_inicial,
        data_final=data_final,
        setor=setor,
        linha=linha,
        turno=turno,
        registros=registros,
        kpis=kpis,
        filtros=filtros,
        erro=erro,
    )


@bp.route("/pcp/producao-coletada/importar", methods=["POST"])
@login_required
@admin_required
def pcp_producao_coletada_importar():
    from flask import request, jsonify
    from app.services import producao_coletada_service as svc

    arquivo = request.files.get("arquivo_json")
    if not arquivo or not arquivo.filename:
        return jsonify({"erro": "Nenhum arquivo enviado."}), 400

    if not arquivo.filename.endswith(".json"):
        return jsonify({"erro": "Somente arquivos .json são aceitos."}), 400

    try:
        job_id = svc.iniciar_importacao(arquivo.read())
        return jsonify({"job_id": job_id})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception:
        return jsonify({"erro": "Erro inesperado ao processar o arquivo."}), 500


@bp.route("/pcp/producao-coletada/importar/progresso/<job_id>")
@login_required
@admin_required
def pcp_producao_coletada_progresso(job_id):
    from flask import jsonify
    from app.services import producao_coletada_service as svc

    return jsonify(svc.status_importacao(job_id))


@bp.route("/pcp/producao-mes")
@login_required
@admin_required
def pcp_producao_mes():
    from flask import request
    from app.services import producao_mes_service as svc

    data_inicial_pad, data_final_pad = svc.data_padrao()

    data_inicial = request.args.get("dataInicial", data_inicial_pad)
    data_final   = request.args.get("dataFinal",   data_final_pad)
    setor        = request.args.get("setor", "")
    linha        = request.args.get("linha", "")
    turno        = request.args.get("turno", "")

    try:
        registros = svc.listar(data_inicial, data_final, setor, linha, turno)
        kpis      = svc.totais(data_inicial, data_final, setor, linha, turno)
        filtros   = svc.filtros_disponiveis(setor)
        erro      = None
    except Exception as e:
        registros = []
        kpis      = {}
        filtros   = {"setores": [], "linhas": []}
        erro      = str(e)

    return render_template(
        "pcp/producao_mes.html",
        active_menu="pcp_producao_mes",
        data_inicial=data_inicial,
        data_final=data_final,
        setor=setor,
        linha=linha,
        turno=turno,
        registros=registros,
        kpis=kpis,
        filtros=filtros,
        erro=erro,
    )


@bp.route("/pcp/producao-mes/importar", methods=["POST"])
@login_required
@admin_required
def pcp_producao_mes_importar():
    from flask import request, jsonify
    from app.services import producao_mes_service as svc

    arquivo = request.files.get("arquivo_json")
    if not arquivo or not arquivo.filename:
        return jsonify({"erro": "Nenhum arquivo enviado."}), 400

    if not arquivo.filename.endswith(".json"):
        return jsonify({"erro": "Somente arquivos .json são aceitos."}), 400

    try:
        job_id = svc.iniciar_importacao(arquivo.read())
        return jsonify({"job_id": job_id})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception:
        return jsonify({"erro": "Erro inesperado ao processar o arquivo."}), 500


@bp.route("/pcp/producao-mes/importar/progresso/<job_id>")
@login_required
@admin_required
def pcp_producao_mes_progresso(job_id):
    from flask import jsonify
    from app.services import producao_mes_service as svc

    return jsonify(svc.status_importacao(job_id))


# ─── SYNC ADMIN ──────────────────────────────────────────────────────────────

@bp.route("/admin/sync", methods=["GET", "POST"])
@login_required
@admin_required
def admin_sync():
    from flask import request, flash, redirect, url_for
    from app.services import sync_service as svc

    if request.method == "POST" and request.form.get("action") == "toggle":
        habilitado = svc.toggle_automatico()
        flash(
            "Sincronização automática habilitada." if habilitado else "Sincronização automática desabilitada.",
            "success",
        )
        return redirect(url_for("pages.admin_sync"))

    habilitado = svc.automatico_habilitado()
    historico  = svc.listar_historico(50)
    resumo     = svc.resumo()

    return render_template(
        "admin/sync.html",
        active_menu="admin_sync",
        habilitado=habilitado,
        historico=historico,
        resumo=resumo,
    )


# ─── CONFIGURAÇÕES DO SISTEMA ────────────────────────────────────────────────

@bp.route("/pcp/turnos")
@login_required
@admin_required
def pcp_turnos():
    from flask import redirect, url_for
    return redirect(url_for("pages.config_turnos"))


@bp.route("/config/turnos", methods=["GET", "POST"])
@login_required
@admin_required
def config_turnos():
    from flask import request, flash, redirect, url_for
    from app.services import turno_config_service as svc

    erro   = None
    turnos = {}

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "adicionar":
            try:
                svc.adicionar(
                    request.form.get("turno", ""),
                    request.form.get("hora_inicio", ""),
                    request.form.get("hora_fim", ""),
                )
                flash("Intervalo adicionado.", "success")
            except ValueError as e:
                flash(str(e), "danger")
            except Exception as e:
                flash(str(e), "danger")
        elif acao == "excluir":
            try:
                svc.excluir(int(request.form.get("id")))
                flash("Intervalo removido.", "success")
            except Exception as e:
                flash(str(e), "danger")
        return redirect(url_for("pages.config_turnos"))

    try:
        turnos = svc.listar_por_turno()
    except Exception as e:
        erro = str(e)

    return render_template(
        "config/turnos.html",
        active_menu="config_turnos",
        turnos=turnos,
        erro=erro,
    )


@bp.route("/config/linhas")
@login_required
@admin_required
def config_linhas():
    from app.services import linha_config_service as svc

    erro   = None
    setores = {}
    linhas  = []

    try:
        setores = svc.listar_por_setor()
        linhas  = svc.listar_linhas_producao()
    except Exception as e:
        erro = str(e)

    return render_template(
        "config/linhas.html",
        active_menu="config_linhas",
        setores=setores,
        linhas=linhas,
        erro=erro,
    )


@bp.route("/config/linhas/atribuir", methods=["POST"])
@login_required
@admin_required
def config_linhas_atribuir():
    from flask import request, jsonify
    from app.services import linha_config_service as svc

    data   = request.get_json(silent=True) or {}
    filial = data.get("filial", "")
    setor  = data.get("setor", "")
    linha  = data.get("linha", "")

    try:
        new_id = svc.atribuir(filial, setor, linha)
        return jsonify({"ok": True, "id": new_id})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/config/linhas/remover", methods=["POST"])
@login_required
@admin_required
def config_linhas_remover():
    from flask import request, jsonify
    from app.services import linha_config_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.remover(int(data.get("id")))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/config/paradas", methods=["GET", "POST"])
@login_required
@admin_required
def config_paradas():
    from flask import request, flash, redirect, url_for
    from app.services import parada_config_service as svc
    from app.services import linha_lider_service as lider_svc

    erro    = None
    paradas = {}
    opcoes  = {}

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "adicionar":
            try:
                svc.adicionar(request.form)
                flash("Parada adicionada.", "success")
            except ValueError as e:
                flash(str(e), "danger")
            except Exception as e:
                flash(str(e), "danger")
        elif acao == "excluir":
            try:
                svc.excluir(int(request.form.get("id")))
                flash("Parada removida.", "success")
            except Exception as e:
                flash(str(e), "danger")
        elif acao == "salvar_lider":
            try:
                lider_svc.salvar(request.form)
                flash("Responsável/HC salvo.", "success")
            except ValueError as e:
                flash(str(e), "danger")
            except Exception as e:
                flash(str(e), "danger")
        elif acao == "excluir_lider":
            try:
                lider_svc.excluir(
                    request.form.get("setor", ""),
                    request.form.get("linha", ""),
                    request.form.get("turno", ""),
                )
                flash("Responsável/HC removido.", "success")
            except Exception as e:
                flash(str(e), "danger")
        return redirect(url_for("pages.config_paradas"))

    try:
        paradas = svc.listar_por_filial_setor()
        opcoes  = svc.opcoes_linha()
    except Exception as e:
        erro = str(e)

    lideres = {}
    try:
        lideres = lider_svc.listar_por_filial_setor()
    except Exception:
        pass

    return render_template(
        "config/paradas.html",
        active_menu="config_paradas",
        paradas=paradas,
        opcoes=opcoes,
        tipos=["INTERVALO_1", "INTERVALO_2", "GINASTICA", "DDS", "REFEICAO", "SETUP", "SMD_5S", "OUTROS"],
        lideres=lideres,
        erro=erro,
    )


@bp.route("/config/manual")
@login_required
def config_manual():
    return render_template("config/manual.html", active_menu="config_manual")


# ─── PCP ─────────────────────────────────────────────────────────────────────

@bp.route("/pcp/controle-ops", methods=["GET", "POST"])
@login_required
def pcp_controle_ops():
    from flask import request, flash, redirect, url_for
    from app.services import controle_ops_service as svc
    from app.services import roteiro_service as roteiro_svc

    erro     = None
    ops      = []
    filiais  = []
    roteiros = []
    filial   = request.args.get("filial", "")
    status   = request.args.get("status", "")
    setor    = request.args.get("setor",  "")

    if request.method == "POST":
        try:
            result = svc.cadastrar(request.form)
            if result["tipo"] == "roteiro":
                flash(f"{result['n_ops']} OPs criadas pelo roteiro \"{result['nome']}\".", "success")
            elif result["tipo"] == "roteiro_padrao":
                flash("Roteiro criado: 3 OPs cadastradas (PTH, IM, SMD).", "success")
            else:
                flash("OP cadastrada com sucesso.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("Erro ao cadastrar. Verifique se a tabela foi criada.", "danger")
        return redirect(url_for("pages.pcp_controle_ops"))

    try:
        ops      = svc.listar(filial, status, setor)
        filiais  = svc.filiais_disponiveis()
        roteiros = roteiro_svc.listar()
    except Exception as e:
        erro = str(e)

    return render_template(
        "pcp/controle_ops.html",
        active_menu="pcp_controle_ops",
        ops=ops,
        filiais=filiais,
        roteiros=roteiros,
        filial=filial,
        status=status,
        setor=setor,
        erro=erro,
    )


@bp.route("/pcp/controle-ops/<int:op_id>/editar", methods=["POST"])
@login_required
def pcp_controle_ops_editar(op_id):
    from flask import request, flash, redirect, url_for
    from app.services import controle_ops_service as svc

    try:
        svc.atualizar(op_id, request.form)
        flash("OP atualizada com sucesso.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Erro ao atualizar a OP.", "danger")
    return redirect(url_for("pages.pcp_controle_ops"))


@bp.route("/pcp/controle-ops/<int:op_id>/excluir", methods=["POST"])
@login_required
def pcp_controle_ops_excluir(op_id):
    from flask import flash, redirect, url_for
    from app.services import controle_ops_service as svc

    try:
        svc.excluir(op_id)
        flash("OP excluída.", "success")
    except Exception:
        flash("Erro ao excluir a OP.", "danger")
    return redirect(url_for("pages.pcp_controle_ops"))


@bp.route("/pcp/apontamento")
@login_required
def pcp_apontamento():
    from flask import request
    from app.services import apontamento_service as svc
    from app.services import producao_coletada_service as pc_svc

    data_inicial_pad, data_final_pad = svc.data_padrao()
    data_inicial = request.args.get("dataInicial", data_inicial_pad)
    data_final   = request.args.get("dataFinal",   data_final_pad)
    setor        = request.args.get("setor",   "")
    linha        = request.args.get("linha",   "")
    turno        = request.args.get("turno",   "")
    sistema      = request.args.get("sistema", "")

    try:
        apontamentos   = svc.listar_agrupado(data_inicial, data_final, setor, linha, turno, sistema=sistema)
        ops            = svc.ops_abertas("")
        filtros        = pc_svc.filtros_disponiveis(setor)
        producao_total = sum(ap["producao_total"] or 0 for ap in apontamentos)
        erro           = None
    except Exception as e:
        apontamentos   = []
        ops            = []
        filtros        = {"setores": [], "linhas": []}
        producao_total = 0
        erro           = str(e)

    return render_template(
        "pcp/apontamento.html",
        active_menu="pcp_apontamento",
        data_inicial=data_inicial,
        data_final=data_final,
        setor=setor,
        linha=linha,
        turno=turno,
        sistema=sistema,
        apontamentos=apontamentos,
        ops=ops,
        filtros=filtros,
        producao_total=producao_total,
        erro=erro,
    )


@bp.route("/pcp/apontamento/vincular", methods=["POST"])
@login_required
def pcp_apontamento_vincular():
    from flask import request, jsonify
    from app.services import apontamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.vincular(
            data.get("data", ""),
            data.get("turno", ""),
            data.get("modelo", ""),
            data.get("linha", ""),
            int(data.get("op_id", 0)),
            int(data.get("quantidade", 0)),
            setor=data.get("setor", ""),
            fase=data.get("fase") or None,
            lote=data.get("lote") or None,
        )
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/apontamento/desvincular", methods=["POST"])
@login_required
def pcp_apontamento_desvincular():
    from flask import request, jsonify
    from app.services import apontamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.desvincular(int(data.get("apontamento_id", 0)))
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/apontamento/corrigir-modelo", methods=["POST"])
@login_required
def pcp_apontamento_corrigir_modelo():
    from flask import request, jsonify
    from app.services import apontamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.corrigir_modelo(
            data.get("data", ""),
            data.get("turno", ""),
            data.get("setor", ""),
            data.get("linha", ""),
            data.get("modelo_atual", ""),
            data.get("modelo_novo", ""),
        )
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/planejamento")
@login_required
def pcp_planejamento():
    from flask import request
    from app.services import planejamento_service as svc
    from app.services import producao_coletada_service as pc_svc
    from app.services import apontamento_service as ap_svc
    from datetime import date

    data_str = request.args.get("data",  str(date.today()))
    turno    = request.args.get("turno", "")
    setor    = request.args.get("setor", "")
    linha    = request.args.get("linha", "")
    erro     = None
    planos   = []
    ops      = []
    filtros  = {"setores": [], "linhas": []}
    opcoes   = {}
    fila_smd = []

    planos_agrupados = []
    resumo           = []

    try:
        planos           = svc.listar(data_str, turno, setor, linha)
        ops              = svc.ops_disponiveis()
        filtros          = pc_svc.filtros_disponiveis(setor)
        opcoes           = svc.opcoes_linha()
        fila_smd         = ap_svc.fila_producao()
        planos_agrupados = svc.planos_agrupados_por_linha(data_str)
        resumo           = svc.resumo_producao(data_str, turno)
    except Exception as e:
        erro = str(e)

    return render_template(
        "pcp/planejamento.html",
        active_menu="pcp_planejamento",
        data_selecionada=data_str,
        turno=turno,
        setor=setor,
        linha=linha,
        planos=planos,
        ops=ops,
        filtros=filtros,
        opcoes=opcoes,
        fila_smd=fila_smd,
        planos_agrupados=planos_agrupados,
        resumo=resumo,
        erro=erro,
    )


@bp.route("/pcp/planejamento/criar", methods=["POST"])
@login_required
def pcp_planejamento_criar():
    from flask import request, jsonify
    from flask_login import current_user
    from app.services import planejamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        resultado = svc.criar(data, username=current_user.username)
        return jsonify({"ok": True, **resultado})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/criar-lote", methods=["POST"])
@login_required
def pcp_planejamento_criar_lote():
    from flask import request, jsonify
    from flask_login import current_user
    from app.services import planejamento_service as svc

    body = request.get_json(silent=True) or {}
    try:
        resultados = svc.criar_lote(
            header=body.get("header", {}),
            modelos=body.get("modelos", []),
            username=current_user.username,
        )
        return jsonify({"ok": True, "resultados": resultados})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/<int:plan_id>/editar", methods=["POST"])
@login_required
def pcp_planejamento_editar(plan_id):
    from flask import request, jsonify
    from app.services import planejamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        resultado = svc.atualizar(plan_id, data)
        return jsonify({"ok": True, **resultado})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/<int:plan_id>/status", methods=["POST"])
@login_required
def pcp_planejamento_status(plan_id):
    from flask import request, jsonify
    from app.services import planejamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.atualizar_status(plan_id, data.get("status", ""))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/<int:plan_id>/observacao", methods=["POST"])
@login_required
def pcp_planejamento_observacao(plan_id):
    from flask import request, jsonify
    from app.services import planejamento_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.atualizar_observacao(plan_id, data.get("observacao") or None)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/<int:plan_id>/excluir", methods=["POST"])
@login_required
def pcp_planejamento_excluir(plan_id):
    from flask import jsonify
    from app.services import planejamento_service as svc

    try:
        svc.excluir(plan_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/plano-de-voo")
@login_required
def pcp_planejamento_plano_de_voo():
    from flask import request, jsonify
    from app.services import planejamento_service as svc
    from datetime import date

    data_str = request.args.get("data", str(date.today()))
    try:
        agrupado = svc.plano_de_voo(data_str)
        serializado = {
            linha: [
                {k: (str(v) if hasattr(v, "strftime") else v) for k, v in item.items()}
                for item in itens
            ]
            for linha, itens in agrupado.items()
        }
        return jsonify(serializado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/buscar-meta")
@login_required
def pcp_planejamento_buscar_meta():
    from flask import request, jsonify, current_app
    from app.repositories import modelos_repository as mr
    from app.services import planejamento_service as svc

    codigo = request.args.get("codigo", "").strip().upper()
    setor  = request.args.get("setor",  "").strip().upper()
    linha  = request.args.get("linha",  "").strip().upper()
    fase   = request.args.get("fase",   "").strip().upper()

    try:
        result_meta = mr.buscar_meta_com_fase(codigo, setor, fase) if codigo else {"meta": None, "fase_encontrada": None}
        meta = result_meta["meta"]
        fase_encontrada = result_meta["fase_encontrada"]
        setup = svc.setup_sugerido(setor, linha)
        result = {"meta": meta, "setup_sugerido": setup}
        if fase_encontrada:
            result["fase_encontrada"] = fase_encontrada
        if meta is None and codigo:
            result["_debug"] = mr.buscar_candidatos_diagnostico(codigo)
        return jsonify(result)
    except Exception as e:
        current_app.logger.exception(
            "buscar_meta falhou: codigo=%s setor=%s fase=%s", codigo, setor, fase
        )
        return jsonify({"meta": None, "setup_sugerido": 0, "_erro": str(e)}), 500


@bp.route("/pcp/planejamento/plano-detalhado")
@login_required
def pcp_planejamento_plano_detalhado():
    from flask import request, jsonify
    from app.services import planejamento_service as svc
    from app.repositories import planejamento_repository as repo_plan

    data_str = request.args.get("data",  "")
    turno    = request.args.get("turno", "")
    setor    = request.args.get("setor", "")
    linha    = request.args.get("linha", "")

    if not data_str or not turno or not linha:
        return jsonify({"erro": "data, turno e linha são obrigatórios"}), 400

    try:
        planos     = repo_plan.listar_plano_de_voo(data_str, turno=turno, setor=setor, linha=linha)
        intervalos = repo_plan.turno_intervalos(turno)
        paradas    = repo_plan.paradas_da_linha(setor, linha)
        slots      = svc.gerar_plano_hora_a_hora(
            [dict(p) for p in planos],
            [dict(i) for i in intervalos],
            [dict(p) for p in paradas],
            data_str,
        )
        return jsonify({"slots": slots})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@bp.route("/pcp/planejamento/plano-de-voo/imprimir")
@login_required
def pcp_planejamento_plano_voo_imprimir():
    from flask import request
    from app.services import planejamento_service as svc
    from datetime import date

    data_str = request.args.get("data",  str(date.today()))
    turno    = request.args.get("turno", "")
    setor    = request.args.get("setor", "")
    linha    = request.args.get("linha", "")

    try:
        dados = svc.dados_impressao_plano_voo(data_str, turno, setor, linha)
    except Exception as e:
        dados = {"slots": [], "data": data_str, "info": {}, "erro": str(e)}

    return render_template("pcp/plano_voo_print.html", **dados)


@bp.route("/pcp/planejamento/plano-de-voo/imprimir-todos")
@login_required
def pcp_planejamento_plano_voo_imprimir_todos():
    from flask import request
    from app.services import planejamento_service as svc
    from datetime import date

    data_str     = request.args.get("data",  str(date.today()))
    turno_filtro = request.args.get("turno", "")

    grupos = svc.planos_agrupados_por_linha(data_str)
    todos = []
    for g in grupos:
        if turno_filtro and g["turno"] != turno_filtro:
            continue
        try:
            dados = svc.dados_impressao_plano_voo(data_str, g["turno"], g["setor"], g["linha"])
            todos.append(dados)
        except Exception:
            pass

    return render_template("pcp/plano_voo_print_todos.html", planos=todos, data=data_str)


@bp.route("/pcp/planejamento/resumo/imprimir")
@login_required
def pcp_planejamento_resumo_imprimir():
    from flask import request
    from app.services import planejamento_service as svc
    from datetime import date, datetime

    data_str     = request.args.get("data",  str(date.today()))
    turno        = request.args.get("turno", "")
    setor_filtro = request.args.get("setor", "")

    try:
        resumo = svc.resumo_producao(data_str, turno, setor_filtro)
    except Exception as e:
        resumo = []

    dias_semana = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira",
                   "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
    try:
        dt         = datetime.strptime(data_str, "%Y-%m-%d")
        dia_semana = dias_semana[dt.weekday()]
        data_fmt   = dt.strftime("%d/%m/%Y")
    except ValueError:
        dia_semana = ""
        data_fmt   = data_str

    return render_template(
        "pcp/resumo_producao_print.html",
        resumo=resumo,
        data=data_str,
        data_fmt=data_fmt,
        dia_semana=dia_semana,
        turno=turno,
        setor_filtro=setor_filtro,
    )


@bp.route("/pcp/entregas")
@login_required
def pcp_entregas():
    import calendar
    from datetime import date
    from flask import request
    from app.services import entregas_service as svc

    hoje = date.today()
    ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
    default_inicial = hoje.replace(day=1).strftime("%Y-%m-%d")
    default_final   = hoje.replace(day=ultimo_dia).strftime("%Y-%m-%d")

    tab          = request.args.get("tab", "pedido")
    status       = request.args.get("status", "")
    data_inicial = request.args.get("dataInicial", default_inicial)
    data_final   = request.args.get("dataFinal", default_final)
    data_hoje    = svc.data_padrao()

    try:
        pedidos   = svc.listar_pedidos(status, "", data_inicial, data_final)
        entregas  = svc.listar_entregas()
        equipe    = svc.listar_equipe()
        erro      = None
    except Exception as e:
        pedidos  = []
        entregas = []
        equipe   = []
        erro     = str(e)

    return render_template(
        "pcp/entregas.html",
        active_menu="logistica_entregas" if tab == "logistica" else "pcp_entregas",
        tab=tab,
        pedidos=pedidos,
        entregas=entregas,
        equipe=equipe,
        data_hoje=data_hoje,
        status_label=svc.STATUS_LABEL,
        status_cor=svc.STATUS_COR,
        status_filter=status,
        data_inicial=data_inicial,
        data_final=data_final,
        erro=erro,
    )


@bp.route("/pcp/entregas/buscar-clientes")
@login_required
def pcp_entregas_buscar_clientes():
    from flask import request, jsonify
    from app.extensions import get_db
    from psycopg.rows import dict_row

    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"ok": True, "resultados": []})

    termo = f"%{q}%"
    try:
        with get_db() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT nome, endereco FROM (
                        SELECT DISTINCT cliente AS nome, endereco
                        FROM local_entrega
                        WHERE ativo = TRUE AND cliente ILIKE %s AND cliente IS NOT NULL
                        UNION
                        SELECT DISTINCT produto AS nome, NULL AS endereco
                        FROM controle_ops
                        WHERE produto ILIKE %s AND produto IS NOT NULL
                    ) sub
                    ORDER BY nome
                    LIMIT 12
                """, (termo, termo))
                rows = cur.fetchall()
        return jsonify({"ok": True, "resultados": [dict(r) for r in rows]})
    except Exception:
        return jsonify({"ok": False, "resultados": []})


@bp.route("/pcp/entregas/locais", methods=["GET"])
@login_required
def pcp_entregas_locais():
    from flask import request, jsonify
    from app.services import locais_entrega_service as svc

    cliente = request.args.get("cliente", "")
    locais = svc.listar_locais(cliente)
    return jsonify({"ok": True, "locais": [dict(l) for l in locais]})


@bp.route("/pcp/entregas/locais/novo", methods=["POST"])
@login_required
def pcp_entregas_locais_novo():
    from flask import request, jsonify
    from app.services import locais_entrega_service as svc

    data = request.get_json(silent=True) or {}
    try:
        local_id = svc.criar_local(
            data.get("cliente", ""),
            data.get("nome_local", ""),
            data.get("endereco", ""),
            float(data["lat"]) if data.get("lat") else None,
            float(data["lng"]) if data.get("lng") else None,
        )
        return jsonify({"ok": True, "id": local_id})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/locais/<int:local_id>/editar", methods=["POST"])
@login_required
def pcp_entregas_locais_editar(local_id):
    from flask import request, jsonify
    from app.services import locais_entrega_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.atualizar_local(
            local_id,
            data.get("cliente", ""),
            data.get("nome_local", ""),
            data.get("endereco", ""),
            float(data["lat"]) if data.get("lat") else None,
            float(data["lng"]) if data.get("lng") else None,
        )
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/locais/<int:local_id>/excluir", methods=["POST"])
@login_required
def pcp_entregas_locais_excluir(local_id):
    from flask import jsonify
    from app.services import locais_entrega_service as svc

    try:
        svc.excluir_local(local_id)
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/pedido/novo", methods=["POST"])
@login_required
def pcp_entregas_pedido_novo():
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        local_id = int(data["local_entrega_id"]) if data.get("local_entrega_id") else None
        pedido_id = svc.criar_pedido(
            data.get("numero_pedido", ""),
            data.get("cliente", ""),
            data.get("modelo", ""),
            data.get("familia", ""),
            int(data.get("quantidade", 0)),
            data.get("data_pedido", ""),
            data.get("data_entrega", ""),
            data.get("observacao", ""),
            local_id,
        )
        return jsonify({"ok": True, "id": pedido_id})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/pedido/<int:pedido_id>/editar", methods=["POST"])
@login_required
def pcp_entregas_pedido_editar(pedido_id):
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        local_id = int(data["local_entrega_id"]) if data.get("local_entrega_id") else None
        svc.atualizar_pedido(
            pedido_id,
            data.get("numero_pedido", ""),
            data.get("cliente", ""),
            data.get("modelo", ""),
            data.get("familia", ""),
            int(data.get("quantidade", 0)),
            data.get("data_pedido", ""),
            data.get("data_entrega", ""),
            data.get("observacao", ""),
            local_id,
        )
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/pedido/<int:pedido_id>/excluir", methods=["POST"])
@login_required
def pcp_entregas_pedido_excluir(pedido_id):
    from flask import jsonify
    from app.services import entregas_service as svc

    try:
        svc.excluir_pedido(pedido_id)
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/pedido/<int:pedido_id>/remessas", methods=["GET"])
@login_required
def pcp_entregas_pedido_remessas(pedido_id):
    from flask import jsonify
    from app.services import entregas_service as svc

    try:
        remessas = svc.listar_remessas_pedido(pedido_id)
        return jsonify({"ok": True, "remessas": [dict(r) for r in remessas]})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/entrega/nova", methods=["POST"])
@login_required
def pcp_entregas_entrega_nova():
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        entrega_id = svc.criar_entrega(
            int(data.get("pedido_id", 0)),
            int(data.get("quantidade", 0)),
            data.get("nota_fiscal", ""),
        )
        return jsonify({"ok": True, "id": entrega_id})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/entrega/<int:entrega_id>/status", methods=["POST"])
@login_required
def pcp_entregas_entrega_status(entrega_id):
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        motorista_id = int(data["motorista_id"]) if data.get("motorista_id") else None
        svc.atualizar_status_entrega(
            entrega_id,
            data.get("status", ""),
            data.get("nota_fiscal"),
            motorista_id,
        )
        membro_ids = [int(x) for x in data.get("membro_ids", []) if x]
        if membro_ids:
            svc.sincronizar_equipe_entrega(entrega_id, membro_ids)
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/entrega/<int:entrega_id>/posicao", methods=["GET"])
@login_required
def pcp_entregas_entrega_posicao(entrega_id):
    from flask import jsonify
    from app.services import entregas_service as svc

    entrega = svc.buscar_entrega(entrega_id)
    if not entrega:
        return jsonify({"erro": "Não encontrado"}), 404
    return jsonify({
        "ok": True,
        "lat": float(entrega["lat"]) if entrega["lat"] else None,
        "lng": float(entrega["lng"]) if entrega["lng"] else None,
        "localizacao_em": entrega["localizacao_em"].strftime("%d/%m/%Y %H:%M") if entrega["localizacao_em"] else None,
    })


@bp.route("/pcp/entregas/entrega/<int:entrega_id>/localizacao", methods=["POST"])
@login_required
def pcp_entregas_entrega_localizacao(entrega_id):
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        svc.atualizar_localizacao(
            entrega_id,
            float(data.get("lat", 0)),
            float(data.get("lng", 0)),
        )
        return jsonify({"ok": True})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/pcp/entregas/mapeamento")
@login_required
def pcp_entregas_mapeamento():
    from app.services import entregas_service as svc
    entregas = svc.posicoes_ativas()
    return render_template(
        "pcp/mapeamento_entregas.html",
        active_menu="logistica_entregas",
        entregas=entregas,
    )


@bp.route("/pcp/entregas/mapeamento/posicoes")
@login_required
def pcp_entregas_mapeamento_posicoes():
    from flask import jsonify
    from app.services import entregas_service as svc

    result = []
    for r in svc.posicoes_ativas():
        result.append({
            "id":                 r["id"],
            "status":             r["status"],
            "motorista_nome":     r["motorista_nome"] or "—",
            "motorista_telefone": r["motorista_telefone"] or "",
            "motorista_lat":      float(r["motorista_lat"])  if r["motorista_lat"]  is not None else None,
            "motorista_lng":      float(r["motorista_lng"])  if r["motorista_lng"]  is not None else None,
            "localizacao_em":     r["localizacao_em"].strftime("%d/%m %H:%M") if r["localizacao_em"] else None,
            "numero_pedido":      r["numero_pedido"],
            "cliente":            r["cliente"],
            "modelo":             r["modelo"],
            "local_nome":         r["local_nome"]    or "",
            "local_endereco":     r["local_endereco"] or "",
            "destino_lat":        float(r["destino_lat"]) if r["destino_lat"] is not None else None,
            "destino_lng":        float(r["destino_lng"]) if r["destino_lng"] is not None else None,
        })
    return jsonify({"ok": True, "entregas": result})


@bp.route("/logistica")
@login_required
def logistica_resumo():
    from datetime import datetime
    from flask import request
    from app.services import entregas_service as svc

    data   = request.args.get("data", svc.data_padrao())
    resumo = svc.resumo_apontamento_logistica(data)
    equipe = svc.listar_equipe()
    entregas_pendentes = [e for e in svc.listar_entregas() if e["status"] != "entregue"]

    try:
        data_fmt = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        data_fmt = data

    return render_template(
        "logistica/resumo.html",
        active_menu="logistica_resumo",
        data=data,
        data_fmt=data_fmt,
        resumo=resumo,
        equipe=equipe,
        entregas_pendentes=entregas_pendentes,
        status_label=svc.STATUS_LABEL,
        status_cor=svc.STATUS_COR,
    )


@bp.route("/logistica/equipe/novo", methods=["POST"])
@login_required
def logistica_equipe_novo():
    from flask import request, jsonify
    from app.services import entregas_service as svc

    data = request.get_json(silent=True) or {}
    try:
        membro_id = svc.criar_membro_equipe(
            data.get("nome", ""),
            data.get("tipo", ""),
            data.get("telefone", ""),
        )
        return jsonify({"ok": True, "id": membro_id})
    except (ValueError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/logistica/equipe/<int:membro_id>/excluir", methods=["POST"])
@login_required
def logistica_equipe_excluir(membro_id):
    from flask import jsonify
    from app.services import entregas_service as svc

    try:
        svc.desativar_membro_equipe(membro_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/logistica/rastrear/<int:entrega_id>")
@login_required
def logistica_rastrear(entrega_id):
    from flask import abort
    from app.services import entregas_service as svc

    entrega = svc.buscar_entrega(entrega_id)
    if not entrega:
        abort(404)

    return render_template(
        "logistica/rastrear.html",
        active_menu="logistica_resumo",
        entrega=entrega,
    )



@bp.route("/logistica/conferencia-material")
@login_required
def logistica_conferencia_material():
    from flask import request
    from datetime import date
    from app.services import conferencia_material_service as svc
    from app.services import planejamento_service as plan_svc

    data = request.args.get("data", str(date.today()))

    planos_base   = plan_svc.listar(data)
    conferencias  = svc.status_por_data(data)
    datas         = svc.listar_datas()

    planos = []
    for p in planos_base:
        p = dict(p)
        conf = conferencias.get(p["id"])
        p["status_material"]  = conf["status"]       if conf else None
        p["conferido_por"]    = conf["conferido_por"] if conf else None
        p["conferido_em"]     = conf["conferido_em"]  if conf else None
        p["conferencia_obs"]  = conf["observacao"]    if conf else None
        p["arquivo_id"]       = None
        p["arquivo_nome"]     = None
        arq = svc.arquivo_por_plano(p["id"])
        if arq:
            p["arquivo_id"]   = arq["id"]
            p["arquivo_nome"] = arq["filename"]
        planos.append(p)

    return render_template(
        "logistica/conferencia_material.html",
        active_menu="logistica_conferencia_material",
        data=data,
        planos=planos,
        datas=datas,
        status_label=svc.STATUS_LABEL,
        status_cor=svc.STATUS_COR,
        statuses=svc.STATUSES_VALIDOS,
    )


@bp.route("/logistica/conferencia-material/confirmar", methods=["POST"])
@login_required
def logistica_conferencia_material_confirmar():
    from flask import request, jsonify
    from app.services import conferencia_material_service as svc

    data = request.get_json(silent=True) or {}
    try:
        conferencia_id = svc.confirmar(
            planejamento_id=int(data["planejamento_id"]),
            status=data["status"],
            observacao=data.get("observacao"),
            conferido_por=current_user.username,
            componentes_confirmados=data.get("componentes_confirmados"),
        )
        return jsonify({"ok": True, "id": conferencia_id})
    except (ValueError, KeyError, Exception) as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/logistica/conferencia-material/historico/<int:planejamento_id>")
@login_required
def logistica_conferencia_material_historico(planejamento_id):
    from flask import jsonify
    from zoneinfo import ZoneInfo
    from app.services import conferencia_material_service as svc

    MANAUS = ZoneInfo("America/Manaus")
    historico = svc.historico_por_plano(planejamento_id)
    result = []
    for h in historico:
        dt = h["conferido_em"]
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            dt_fmt = dt.astimezone(MANAUS).strftime("%d/%m/%Y %H:%M")
        else:
            dt_fmt = None
        result.append({
            "id":                      h["id"],
            "status":                  h["status"],
            "observacao":              h["observacao"],
            "conferido_por":           h["conferido_por"],
            "conferido_em":            dt_fmt,
            "componentes_confirmados": h["componentes_confirmados"],
        })
    return jsonify({"ok": True, "historico": result})


@bp.route("/logistica/conferencia-material/upload/<int:planejamento_id>", methods=["POST"])
@login_required
def logistica_conferencia_material_upload(planejamento_id):
    from flask import request, jsonify
    from app.services import conferencia_material_service as svc

    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        return jsonify({"erro": "Nenhum arquivo enviado."}), 400
    try:
        resultado = svc.upload_arquivo(planejamento_id, arquivo, current_user.username)
        return jsonify({"ok": True, "componentes": resultado["componentes"]})
    except Exception as e:
        import traceback
        traceback.print_exc()
        erro_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
        return jsonify({"erro": erro_msg}), 400


@bp.route("/logistica/conferencia-material/componentes/<int:planejamento_id>")
@login_required
def logistica_conferencia_material_componentes(planejamento_id):
    from flask import jsonify
    from app.services import conferencia_material_service as svc

    arq = svc.arquivo_por_plano(planejamento_id)
    if not arq or not arq["componentes"]:
        return jsonify({"ok": True, "componentes": []})
    return jsonify({"ok": True, "componentes": arq["componentes"]})


# ─── Suporte ─────────────────────────────────────────────────────────────────

@bp.route("/suporte/centro-conhecimento")
@login_required
def suporte_centro_conhecimento():
    try:
        from app.repositories.suporte_repository import list_faq_items
        faqs = list_faq_items()
    except Exception:
        faqs = []
    return render_template(
        "suporte/centro_conhecimento.html",
        active_menu="suporte_centro_conhecimento",
        faqs=faqs,
    )


@bp.route("/suporte/ouvidoria", methods=["GET", "POST"])
@login_required
def suporte_ouvidoria():
    from flask import request, flash, redirect, url_for
    from app.repositories.suporte_repository import create_ouvidoria_message

    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        mensagem = request.form.get("mensagem", "").strip()
        nome_contato = request.form.get("nome_contato", "").strip()

        if not tipo or not mensagem:
            flash("Preencha o tipo e a mensagem.", "danger")
        else:
            try:
                create_ouvidoria_message({
                    "tipo": tipo,
                    "mensagem": mensagem,
                    "nome_contato": nome_contato,
                    "user_id": current_user.id,
                })
                flash("Mensagem enviada com sucesso. Obrigado pelo seu contato.", "success")
            except Exception:
                flash("Erro ao enviar mensagem. Execute a migração 002 no banco.", "danger")
            return redirect(url_for("pages.suporte_ouvidoria"))

    return render_template("suporte/ouvidoria.html", active_menu="suporte_ouvidoria")


@bp.route("/suporte/suporte-especializado", methods=["GET", "POST"])
@login_required
def suporte_especializado():
    from flask import request, flash, redirect, url_for

    try:
        from app.repositories.suporte_repository import (
            get_or_create_ticket,
            list_ticket_messages,
            create_ticket_message,
        )
        ticket = get_or_create_ticket(current_user.id)
    except Exception:
        return render_template(
            "suporte/suporte_especializado.html",
            active_menu="suporte_especializado",
            ticket=None,
            messages=[],
        )

    if request.method == "POST":
        mensagem = request.form.get("mensagem", "").strip()
        if mensagem:
            try:
                create_ticket_message({
                    "ticket_id": ticket["id"],
                    "user_id": current_user.id,
                    "is_support": False,
                    "mensagem": mensagem,
                })
            except Exception:
                flash("Erro ao enviar mensagem.", "danger")
        return redirect(url_for("pages.suporte_especializado"))

    try:
        messages = list_ticket_messages(ticket["id"])
    except Exception:
        messages = []

    return render_template(
        "suporte/suporte_especializado.html",
        active_menu="suporte_especializado",
        ticket=ticket,
        messages=messages,
    )


# ─── Admin ────────────────────────────────────────────────────────────────────

@bp.route("/admin/chamados", methods=["GET"])
@login_required
@admin_required
def admin_chamados():
    from flask import request
    from app.repositories.suporte_repository import list_all_tickets, get_ticket_by_id, list_ticket_messages

    ticket_id = request.args.get("ticket_id", type=int)
    tickets = list_all_tickets()
    selected_ticket = None
    selected_messages = []

    if ticket_id:
        selected_ticket = get_ticket_by_id(ticket_id)
        if selected_ticket:
            selected_messages = list_ticket_messages(ticket_id)

    return render_template(
        "admin/chamados.html",
        active_menu="admin_chamados",
        tickets=tickets,
        selected_ticket=selected_ticket,
        selected_messages=selected_messages,
    )


@bp.route("/admin/chamados/<int:ticket_id>/responder", methods=["POST"])
@login_required
@admin_required
def admin_chamados_responder(ticket_id):
    from flask import request, redirect, url_for
    from app.repositories.suporte_repository import get_ticket_by_id, create_ticket_message

    mensagem = request.form.get("mensagem", "").strip()
    if mensagem and get_ticket_by_id(ticket_id):
        create_ticket_message({
            "ticket_id": ticket_id,
            "user_id": current_user.id,
            "is_support": True,
            "mensagem": mensagem,
        })
    return redirect(url_for("pages.admin_chamados", ticket_id=ticket_id))


@bp.route("/admin/chamados/<int:ticket_id>/fechar", methods=["POST"])
@login_required
@admin_required
def admin_chamados_fechar(ticket_id):
    from flask import redirect, url_for
    from app.repositories.suporte_repository import close_ticket

    close_ticket(ticket_id)
    return redirect(url_for("pages.admin_chamados"))


@bp.route("/admin/backup", methods=["GET", "POST"])
@login_required
@admin_required
def admin_backup():
    from flask import request, flash, redirect, url_for

    try:
        from app.repositories.backup_repository import (
            get_backup_config,
            upsert_backup_config,
            list_backup_logs,
        )
        from app.services.backup_service import trigger_manual_backup
        config = get_backup_config()
        logs = list_backup_logs(limit=50)
    except Exception:
        config = None
        logs = []
        upsert_backup_config = None
        trigger_manual_backup = None

    if request.method == "POST":
        action = request.form.get("action")

        if upsert_backup_config is None or trigger_manual_backup is None:
            flash("Execute a migração 002 no banco antes de usar esta funcionalidade.", "danger")
            return redirect(url_for("pages.admin_backup"))

        if action == "save_config":
            upsert_backup_config({
                "database_url": request.form.get("database_url", "").strip(),
                "frequency": request.form.get("frequency", "daily"),
                "execution_hour": int(request.form.get("execution_hour", 2)),
                "execution_minute": int(request.form.get("execution_minute", 0)),
                "retention_days": int(request.form.get("retention_days", 30)),
                "is_active": request.form.get("is_active") == "1",
            })
            flash("Configuração salva com sucesso.", "success")
            return redirect(url_for("pages.admin_backup"))

        if action == "run_now":
            trigger_manual_backup()
            flash("Backup iniciado em segundo plano.", "info")
            return redirect(url_for("pages.admin_backup"))

    return render_template(
        "admin/backups.html",
        active_menu="admin_backup",
        config=config,
        logs=logs,
    )


# ─── PWA / Legal ─────────────────────────────────────────────────────────────

@bp.route("/privacy-policy")
def privacy_policy():
    return render_template("legal/privacy.html")


@bp.route("/cookie-policy")
def cookie_policy():
    return render_template("legal/cookies.html")


@bp.route("/offline", endpoint="offline_page")
def offline():
    return render_template("offline.html")


@bp.route("/manifest.webmanifest", endpoint="pwa_manifest")
def manifest():
    from flask import current_app, send_from_directory, make_response
    import os

    static_dir = os.path.join(current_app.root_path, "static")
    resp = make_response(send_from_directory(static_dir, "manifest.webmanifest"))
    resp.headers["Content-Type"] = "application/manifest+json; charset=utf-8"
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


@bp.route("/config/empresa", methods=["GET", "POST"])
@login_required
@admin_required
def config_empresa():
    from flask import request, jsonify
    from app.services import empresa_config_service as svc

    if request.method == "POST" and request.content_type and "multipart" in request.content_type:
        action = request.form.get("action", "")
        if action == "remove_logo":
            try:
                svc.remove_logo()
                from flask import redirect, url_for
                return redirect(url_for("pages.config_empresa"))
            except Exception as e:
                config = svc.get_config()
                return render_template("config/empresa.html", active_menu="config_empresa",
                                       config=config, erro=str(e), sucesso=None)
        if action == "upload_logo":
            try:
                svc.upload_logo(request.files.get("logo"))
                from flask import redirect, url_for
                return redirect(url_for("pages.config_empresa"))
            except (ValueError, Exception) as e:
                config = svc.get_config()
                return render_template("config/empresa.html", active_menu="config_empresa",
                                       config=config, erro=str(e), sucesso=None)

    erro = None
    sucesso = None

    if request.method == "POST":
        try:
            svc.update_config(request.form)
            sucesso = "Configurações salvas com sucesso."
        except ValueError as e:
            erro = str(e)
        except Exception:
            erro = "Erro ao salvar configurações. Tente novamente."

    config = svc.get_config()

    return render_template(
        "config/empresa.html",
        active_menu="config_empresa",
        config=config,
        erro=erro,
        sucesso=sucesso,
    )


@bp.route("/funcionalidades/sistemas/input/lancamento", methods=["GET"])
@login_required
def funcionalidades_sistema_input_lancamento():
    from flask import request
    from app.services import sistema_input_lancamento_service as svc
    from app.services import producao_coletada_service as pc_svc
    from app.repositories import turno_config_repository as turno_repo

    setor = request.args.get("setor", "")
    linha = request.args.get("linha", "")
    turno = request.args.get("turno", "")

    try:
        catalogos = svc.catalogos()
        filtros = pc_svc.filtros_disponiveis(setor)
        turnos = turno_repo.listar_nomes_unicos()
    except Exception:
        catalogos = {"motivos": [], "defeitos": []}
        filtros = {"setores": [], "linhas": []}
        turnos = []

    return render_template(
        "funcionalidades/sistema_input_lancamento.html",
        active_menu="funcionalidades_sistema_input",
        setor=setor,
        linha=linha,
        turno=turno,
        catalogos=catalogos,
        filtros=filtros,
        turnos=turnos,
    )


@bp.route("/funcionalidades/sistemas/input/lancamento/slots")
@login_required
def funcionalidades_sistema_input_slots():
    from flask import request, jsonify
    from app.services import sistema_input_lancamento_service as svc

    data_str = request.args.get("data", "")
    setor = request.args.get("setor", "")
    linha = request.args.get("linha", "")
    turno = request.args.get("turno", "")

    if not all([data_str, setor, linha, turno]):
        return jsonify({"ok": False, "erro": "data, setor, linha e turno são obrigatórios"}), 400

    try:
        slots = svc.slots_do_turno(data_str, setor, linha, turno)
        return jsonify({"ok": True, "slots": slots})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@bp.route("/funcionalidades/sistemas/input/lancamento/salvar", methods=["POST"])
@login_required
def funcionalidades_sistema_input_salvar():
    from flask import request, jsonify
    from app.services import sistema_input_lancamento_service as svc

    payload = request.get_json(silent=True) or {}
    try:
        lancamento_id = svc.salvar(payload, current_user.id)
        return jsonify({"ok": True, "id": lancamento_id})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "erro": "Erro ao salvar lançamento."}), 500


@bp.route("/funcionalidades/sistemas/input/lancamento/historico")
@login_required
def funcionalidades_sistema_input_historico():
    from flask import request, jsonify
    from app.services import sistema_input_lancamento_service as svc

    filial       = request.args.get("filial", "")
    setor        = request.args.get("setor", "")
    linha        = request.args.get("linha", "")
    turno        = request.args.get("turno", "")
    data_inicial = request.args.get("data_inicial", "")
    data_final   = request.args.get("data_final", "")

    try:
        registros = svc.historico(
            filial=filial, setor=setor, linha=linha, turno=turno,
            data_inicial=data_inicial, data_final=data_final,
        )
        return jsonify({"ok": True, "registros": [dict(r) for r in registros]})
    except Exception:
        return jsonify({"ok": False, "registros": []})


@bp.route("/funcionalidades/sistemas/input/lancamento/<int:lancamento_id>/excluir", methods=["POST"])
@login_required
def funcionalidades_sistema_input_lancamento_excluir(lancamento_id):
    from flask import jsonify
    from app.services import sistema_input_lancamento_service as svc

    try:
        svc.excluir(lancamento_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao excluir."}), 500


@bp.route("/funcionalidades/sistemas/input", methods=["GET", "POST"])
@login_required
def funcionalidades_sistema_input():
    from flask import request
    from app.services import sistema_input_lancamento_service as lsvc
    from app.repositories import turno_config_repository as turno_repo
    from app.repositories import producao_coletada_repository as pc_repo

    setor = request.args.get("setor", "")

    try:
        catalogos = lsvc.catalogos()
        setores = pc_repo.setores_disponiveis() or []
        turnos = turno_repo.listar_nomes_unicos()
    except Exception:
        catalogos = {"motivos": [], "defeitos": []}
        setores = []
        turnos = []

    return render_template(
        "funcionalidades/sistema_input.html",
        active_menu="funcionalidades_sistema_input",
        setor=setor,
        catalogos=catalogos,
        setores=setores,
        turnos=turnos,
    )


@bp.route("/funcionalidades/sistemas/input/linhas")
@login_required
def funcionalidades_sistema_input_linhas():
    from flask import request, jsonify
    from app.services import sistema_input_service as svc

    setor = request.args.get("setor", "").strip()
    try:
        linhas = svc.linhas_do_setor(setor)
        return jsonify({"ok": True, "linhas": linhas})
    except Exception:
        return jsonify({"ok": False, "linhas": []})


@bp.route("/funcionalidades/sistemas/input/buscar-linha")
@login_required
def funcionalidades_sistema_input_buscar_linha():
    from flask import request, jsonify
    from app.repositories import linha_config_repository as lc_repo

    termo = request.args.get("q", "").strip()
    if len(termo) < 1:
        return jsonify({"ok": True, "resultados": []})
    try:
        rows = lc_repo.buscar_por_termo(termo)
        return jsonify({"ok": True, "resultados": [dict(r) for r in rows]})
    except Exception:
        return jsonify({"ok": False, "resultados": []})


@bp.route("/funcionalidades/sistemas/input/modelos")
@login_required
def funcionalidades_sistema_input_modelos():
    from flask import request, jsonify
    from app.services import sistema_input_service as svc

    termo = request.args.get("q", "").strip()
    try:
        modelos = svc.modelos_autocomplete(termo)
        return jsonify({"ok": True, "modelos": modelos})
    except Exception:
        return jsonify({"ok": False, "modelos": []})


@bp.route("/funcionalidades/sistemas/input/<int:registro_id>/excluir", methods=["POST"])
@login_required
def funcionalidades_sistema_input_excluir(registro_id):
    from flask import jsonify
    from app.services import sistema_input_service as svc

    try:
        svc.excluir(registro_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao excluir registro."}), 500


# ─────────────────────────────────────────────────────────────────────────────
# SISTEMA PCI HUB
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/funcionalidades/sistemas/pci-hub", methods=["GET"])
@login_required
def funcionalidades_pci_hub():
    return render_template(
        "funcionalidades/pci_hub.html",
        active_menu="funcionalidades_pci_hub",
    )


@bp.route("/funcionalidades/sistemas/pci-hub/hora-a-hora", methods=["GET"])
@login_required
def funcionalidades_pci_hub_hora_a_hora():
    from flask import request as req
    from datetime import date
    from app.repositories import turno_config_repository as turno_repo
    from app.repositories import producao_coletada_repository as pc_repo
    from app.services import sistema_input_lancamento_service as svc

    try:
        turnos = [str(t) for t in turno_repo.listar_turnos()]
    except Exception:
        turnos = []
    try:
        setores = sorted(list(pc_repo.setores_disponiveis()))
    except Exception:
        setores = ["SMD", "PTH", "IM/PA"]

    hoje = str(date.today())
    f_data   = req.args.get("data",   hoje)
    f_turno  = req.args.get("turno",  "")
    f_filial = req.args.get("filial", "")
    f_setor  = req.args.get("setor",  "")

    try:
        registros_raw = svc.historico(
            filial=f_filial, setor=f_setor, linha="",
            turno=f_turno,
            data_inicial=f_data, data_final=f_data,
        )
        registros = [dict(r) for r in registros_raw]
    except Exception:
        registros = []

    linha_map = {}
    for r in registros:
        key = (r.get("filial", ""), r.get("setor", ""), r.get("linha", ""))
        if key not in linha_map:
            linha_map[key] = {"filial": key[0], "setor": key[1], "linha": key[2], "slots": []}
        linha_map[key]["slots"].append(r)

    linhas = sorted(linha_map.values(), key=lambda x: (x["filial"], x["setor"], x["linha"]))

    total_prod = sum(s.get("producao_real") or 0 for l in linhas for s in l["slots"])
    total_meta = sum(s.get("meta_hora") or 0 for l in linhas for s in l["slots"])
    ef_global  = round(min(100, total_prod / total_meta * 100)) if total_meta > 0 else None

    return render_template(
        "funcionalidades/pci_hub_hora_a_hora.html",
        active_menu="funcionalidades_pci_hub",
        turnos=turnos,
        setores=setores,
        linhas=linhas,
        total_prod=total_prod,
        total_meta=total_meta,
        ef_global=ef_global,
        f_data=f_data,
        f_turno=f_turno,
        f_filial=f_filial,
        f_setor=f_setor,
    )


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem():
    return render_template(
        "funcionalidades/pci_hub_embalagem.html",
        active_menu="funcionalidades_pci_hub",
    )


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/sessao", methods=["GET", "POST"])
@login_required
def funcionalidades_pci_hub_embalagem_sessao():
    from flask import request, jsonify
    from app.services import pci_hub_service as svc

    if request.method == "GET":
        try:
            return jsonify({"ok": True, "sessoes": svc.sessoes_abertas()})
        except Exception:
            return jsonify({"ok": True, "sessoes": []})

    try:
        data = request.get_json(force=True) or {}
        sessao = svc.iniciar_sessao(
            linha=data.get("linha", ""),
            usuario=data.get("usuario", ""),
            op=data.get("op", ""),
            modelo=data.get("modelo", ""),
            cliente=data.get("cliente", ""),
            turno=data.get("turno", ""),
            meta_hora=data.get("meta_hora"),
            qtd_por_caixa=data.get("qtd_por_caixa"),
        )
        return jsonify({"ok": True, "sessao": sessao})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao criar sessão."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/scan", methods=["POST"])
@login_required
def funcionalidades_pci_hub_embalagem_scan():
    from flask import request, jsonify
    from app.services import pci_hub_service as svc

    try:
        data = request.get_json(force=True) or {}
        sessao_id = int(data.get("sessao_id", 0))
        serial = data.get("serial", "")
        scan, total = svc.processar_scan(sessao_id, serial)
        return jsonify({
            "ok": True,
            "scan": {
                "id": scan["id"],
                "serial": scan["serial"],
                "scaneado_em": str(scan["scaneado_em"])[-8:],
                "impresso": scan["impresso"],
            },
            "total": total,
        })
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao registrar scan."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/sessao/<int:sessao_id>/scans", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem_scans(sessao_id):
    from flask import jsonify
    from app.services import pci_hub_service as svc

    try:
        scans = svc.obter_scans(sessao_id)
        return jsonify({"ok": True, "scans": [
            {
                "id": s["id"],
                "serial": s["serial"],
                "scaneado_em": str(s["scaneado_em"])[-8:],
                "impresso": s["impresso"],
            }
            for s in scans
        ]})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao listar scans."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/sessao/<int:sessao_id>/fechar", methods=["POST"])
@login_required
def funcionalidades_pci_hub_embalagem_fechar(sessao_id):
    from flask import jsonify
    from app.services import pci_hub_service as svc

    try:
        svc.fechar_sessao(sessao_id)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao fechar sessão."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/consultar-embalagem", methods=["GET"])
@login_required
def funcionalidades_pci_hub_consultar_embalagem():
    return render_template(
        "funcionalidades/pci_hub_consultar_embalagem.html",
        active_menu="funcionalidades_pci_hub",
    )


@bp.route("/funcionalidades/sistemas/pci-hub/consultar-embalagem/dados", methods=["GET"])
@login_required
def funcionalidades_pci_hub_consultar_embalagem_dados():
    from flask import request, jsonify
    from app.repositories import pci_hub_repository as repo

    try:
        filial       = (request.args.get("filial")       or "").strip()
        setor        = (request.args.get("setor")        or "").strip()
        linha        = (request.args.get("linha")        or "").strip()
        data_inicial = (request.args.get("data_inicial") or "").strip()
        data_final   = (request.args.get("data_final")   or "").strip()
        sessoes = repo.listar_sessoes_filtradas(filial, setor, linha, data_inicial, data_final)
        return jsonify({"ok": True, "sessoes": sessoes})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao consultar."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/consultar-embalagem/sessao/<int:sessao_id>/scans", methods=["GET"])
@login_required
def funcionalidades_pci_hub_consultar_scans(sessao_id):
    from flask import jsonify
    from app.repositories import pci_hub_repository as repo

    try:
        scans = repo.listar_scans(sessao_id, limite=500)
        return jsonify({"ok": True, "scans": scans})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao carregar scans."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/buscar-op", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem_buscar_op():
    from flask import request, jsonify
    from app.repositories import controle_ops_repository as ops_repo

    q = (request.args.get("q") or "").strip()
    if len(q) < 1:
        return jsonify({"ok": True, "resultados": []})
    try:
        rows = ops_repo.buscar_por_termo(q)
        return jsonify({"ok": True, "resultados": [
            {
                "numero_op": r["numero_op"],
                "produto": r["produto"] or "",
                "quantidade": r["quantidade"] or 0,
                "filial": r["filial"] or "",
                "setor": r["setor"] or "",
            }
            for r in rows
        ]})
    except Exception:
        return jsonify({"ok": False, "resultados": []}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/turno-atual", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem_turno_atual():
    from flask import jsonify
    from app.services import pci_hub_service as svc

    try:
        return jsonify({"ok": True, **svc.detectar_turno()})
    except Exception as _exc:
        import traceback, logging
        logging.getLogger(__name__).error("detectar_turno falhou: %s\n%s", _exc, traceback.format_exc())
        return jsonify({"ok": False, "turno": None, "hora_atual": "", "intervalos": [], "erro": str(_exc)})


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/sessao/<int:sessao_id>/intervalos", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem_intervalos(sessao_id):
    from flask import jsonify
    from app.services import pci_hub_service as svc

    try:
        return jsonify({"ok": True, **svc.obter_intervalos_sessao(sessao_id)})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 404
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao calcular intervalos."}), 500


# ─────────────────────────────────────────────────────────────────────────────
# PADRÃO DO MODELO
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/funcionalidades/sistemas/pci-hub/padrao-modelo", methods=["GET"])
@login_required
def funcionalidades_pci_hub_padrao_modelo():
    from app.services import pci_modelo_padrao_service as svc

    try:
        modelos = svc.listar()
    except Exception:
        modelos = []
    return render_template(
        "funcionalidades/pci_hub_padrao_modelo.html",
        active_menu="funcionalidades_pci_hub",
        modelos=modelos,
    )


@bp.route("/funcionalidades/sistemas/pci-hub/padrao-modelo/salvar", methods=["POST"])
@login_required
def funcionalidades_pci_hub_padrao_modelo_salvar():
    from flask import request, jsonify
    from app.services import pci_modelo_padrao_service as svc

    try:
        body = request.get_json(force=True) or {}
        mid = body.get("id")
        if mid:
            svc.atualizar(int(mid), body)
            return jsonify({"ok": True, "id": int(mid)})
        else:
            novo_id = svc.criar(body)
            return jsonify({"ok": True, "id": novo_id})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao salvar."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/padrao-modelo/<int:mid>", methods=["GET"])
@login_required
def funcionalidades_pci_hub_padrao_modelo_carregar(mid):
    from flask import jsonify
    from app.services import pci_modelo_padrao_service as svc

    try:
        return jsonify({"ok": True, "modelo": svc.obter(mid)})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 404
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao carregar."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/padrao-modelo/<int:mid>/excluir", methods=["POST"])
@login_required
def funcionalidades_pci_hub_padrao_modelo_excluir(mid):
    from flask import jsonify
    from app.services import pci_modelo_padrao_service as svc

    try:
        svc.excluir(mid)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao excluir."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/padrao-modelo/buscar-roteiro", methods=["GET"])
@login_required
def funcionalidades_pci_hub_padrao_modelo_buscar_roteiro():
    from flask import request, jsonify
    from app.repositories import roteiro_repository as repo

    q = (request.args.get("q") or "").strip()
    if len(q) < 1:
        return jsonify({"ok": True, "resultados": []})
    try:
        todos = repo.listar()
        q_lower = q.lower()
        filtrados = [
            {"id": r["id"], "nome": r["nome"], "cliente": r["cliente"] or ""}
            for r in todos
            if q_lower in (r["nome"] or "").lower() or q_lower in (r["cliente"] or "").lower()
        ][:10]
        return jsonify({"ok": True, "resultados": filtrados})
    except Exception:
        return jsonify({"ok": False, "resultados": []}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/embalagem/modelo-padrao", methods=["GET"])
@login_required
def funcionalidades_pci_hub_embalagem_modelo_padrao():
    """Retorna qtd_por_caixa e meta_hora de um modelo configurado (para auto-fill no setup)."""
    from flask import request, jsonify
    from app.services import pci_modelo_padrao_service as svc

    modelo = (request.args.get("modelo") or "").strip()
    if not modelo:
        return jsonify({"ok": True, "config": None})
    try:
        config = svc.buscar_por_modelo(modelo)
        return jsonify({"ok": True, "config": config})
    except Exception:
        return jsonify({"ok": True, "config": None})


# ─────────────────────────────────────────────────────────────────────────────
# POSTO DE REVISÃO
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/funcionalidades/sistemas/pci-hub/revisao", methods=["GET"])
@login_required
def funcionalidades_pci_hub_posto_revisao():
    from flask import request
    from app.services import pci_revisao_service as svc
    from app.repositories import turno_config_repository as turno_repo
    from app.repositories import sistema_input_lancamento_repository as catalog_repo

    linha    = (request.args.get("linha")    or "").strip()
    data_ini = (request.args.get("data_ini") or "").strip()
    data_fim = (request.args.get("data_fim") or "").strip()
    try:
        relatorios = svc.listar(linha, data_ini, data_fim)
    except Exception:
        relatorios = []
    try:
        turnos = turno_repo.listar_nomes_unicos()
    except Exception:
        turnos = []
    try:
        defeitos_cat = catalog_repo.listar_defeitos()
    except Exception:
        defeitos_cat = []
    return render_template(
        "funcionalidades/pci_hub_revisao.html",
        active_menu="funcionalidades_pci_hub",
        relatorios=relatorios,
        slots=svc.slots_padrao(),
        turnos=turnos,
        defeitos_cat=defeitos_cat,
    )


@bp.route("/funcionalidades/sistemas/pci-hub/revisao/salvar", methods=["POST"])
@login_required
def funcionalidades_pci_hub_revisao_salvar():
    from flask import request, jsonify
    from app.services import pci_revisao_service as svc

    try:
        body = request.get_json(force=True) or {}
        cabecalho = body.get("cabecalho", {})
        horas     = body.get("horas", [])
        defeitos  = body.get("defeitos", [])
        rel_id    = body.get("id")

        cabecalho["criado_por"] = current_user.username

        if rel_id:
            svc.atualizar_relatorio(int(rel_id), cabecalho, horas, defeitos)
            return jsonify({"ok": True, "id": int(rel_id)})
        else:
            novo_id = svc.novo_relatorio(cabecalho, horas, defeitos)
            return jsonify({"ok": True, "id": novo_id})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    except Exception as e:
        import traceback
        return jsonify({"ok": False, "erro": traceback.format_exc()}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/revisao/<int:rel_id>", methods=["GET"])
@login_required
def funcionalidades_pci_hub_revisao_carregar(rel_id):
    from flask import jsonify
    from app.services import pci_revisao_service as svc

    try:
        rel = svc.obter_relatorio(rel_id)
        return jsonify({"ok": True, "relatorio": rel})
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 404
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao carregar."}), 500


@bp.route("/funcionalidades/sistemas/pci-hub/revisao/<int:rel_id>/excluir", methods=["POST"])
@login_required
def funcionalidades_pci_hub_revisao_excluir(rel_id):
    from flask import jsonify
    from app.services import pci_revisao_service as svc

    try:
        svc.excluir(rel_id)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False, "erro": "Erro ao excluir."}), 500


# PCI Hub — Cadastro
@bp.route("/funcionalidades/sistemas/pci-hub/cadastro/motivos")
@login_required
def funcionalidades_pci_hub_cadastro_motivos():
    from app.repositories import sistema_input_lancamento_repository as input_repo
    motivos = input_repo.listar_motivos()
    return render_template(
        "funcionalidades/pci_hub_cadastro_motivos.html",
        active_menu="funcionalidades_pci_hub",
        motivos=motivos,
    )


@bp.route("/funcionalidades/sistemas/pci-hub/cadastro/defeitos")
@login_required
def funcionalidades_pci_hub_cadastro_defeitos():
    from app.repositories import sistema_input_lancamento_repository as input_repo
    defeitos = input_repo.listar_defeitos()
    return render_template(
        "funcionalidades/pci_hub_cadastro_defeitos.html",
        active_menu="funcionalidades_pci_hub",
        defeitos=defeitos,
    )


@bp.route("/funcionalidades/sistemas/pci-hub/cadastro/linhas")
@login_required
def funcionalidades_pci_hub_cadastro_linhas():
    from app.repositories import linha_config_repository as linha_repo
    linhas = linha_repo.listar_todas()
    return render_template(
        "funcionalidades/pci_hub_cadastro_linhas.html",
        active_menu="funcionalidades_pci_hub",
        linhas=linhas,
    )


# PCI Hub — Relatório
@bp.route("/funcionalidades/sistemas/pci-hub/relatorio/producao")
@login_required
def funcionalidades_pci_hub_relatorio_producao():
    return render_template(
        "funcionalidades/pci_hub_relatorio_producao.html",
        active_menu="funcionalidades_pci_hub",
    )


@bp.route("/funcionalidades/sistemas/pci-hub/relatorio/qualidade")
@login_required
def funcionalidades_pci_hub_relatorio_qualidade():
    return render_template(
        "funcionalidades/pci_hub_relatorio_qualidade.html",
        active_menu="funcionalidades_pci_hub",
    )


@bp.route("/funcionalidades/sistemas/pci-hub/relatorio/rastreabilidade")
@login_required
def funcionalidades_pci_hub_relatorio_rastreabilidade():
    return render_template(
        "funcionalidades/pci_hub_relatorio_rastreabilidade.html",
        active_menu="funcionalidades_pci_hub",
    )


# ─────────────────────────────────────────────────────────────────────────────
# REPARO HUB
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/funcionalidades/sistemas/reparo-hub", methods=["GET"])
@login_required
def funcionalidades_reparo_hub():
    return render_template(
        "funcionalidades/reparo_hub.html",
        active_menu="funcionalidades_reparo_hub",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RH OPS
# ─────────────────────────────────────────────────────────────────────────────


@bp.route("/funcionalidades/sistemas/rh-ops", methods=["GET"])
@login_required
def rh_ops_hub():
    return render_template("rh_ops/rh_hub.html", active_menu="rh_ops_hub")


@bp.route("/rh-ops/meu-rh", methods=["GET"])
@login_required
def rh_meu_rh():
    return render_template("rh_ops/meu_rh.html", active_menu="rh_meu_rh")


# ── Colaboradores ──

@bp.route("/rh-ops/colaboradores", methods=["GET"])
@login_required
def rh_colaboradores_lista():
    return render_template("rh_ops/colaboradores/lista.html", active_menu="rh_colaboradores_lista")


@bp.route("/rh-ops/colaboradores/cadastrar", methods=["GET"])
@login_required
def rh_colaboradores_cadastrar():
    return render_template("rh_ops/colaboradores/cadastrar.html", active_menu="rh_colaboradores_cadastrar")


@bp.route("/rh-ops/colaboradores/<int:colaborador_id>/perfil", methods=["GET"])
@login_required
def rh_colaboradores_perfil(colaborador_id):
    return render_template("rh_ops/colaboradores/perfil.html", active_menu="rh_colaboradores_lista", colaborador_id=colaborador_id)


@bp.route("/rh-ops/colaboradores/documentos", methods=["GET"])
@login_required
def rh_colaboradores_documentos():
    return render_template("rh_ops/colaboradores/documentos.html", active_menu="rh_colaboradores_documentos")


@bp.route("/rh-ops/colaboradores/historico", methods=["GET"])
@login_required
def rh_colaboradores_historico():
    return render_template("rh_ops/colaboradores/historico.html", active_menu="rh_colaboradores_historico")


# ── Estrutura Organizacional ──

@bp.route("/rh-ops/organizacional/filiais", methods=["GET"])
@login_required
def rh_org_filiais():
    return render_template("rh_ops/organizacional/filiais.html", active_menu="rh_org_filiais")


@bp.route("/rh-ops/organizacional/departamentos", methods=["GET"])
@login_required
def rh_org_departamentos():
    return render_template("rh_ops/organizacional/departamentos.html", active_menu="rh_org_departamentos")


@bp.route("/rh-ops/organizacional/cargos", methods=["GET"])
@login_required
def rh_org_cargos():
    return render_template("rh_ops/organizacional/cargos.html", active_menu="rh_org_cargos")


@bp.route("/rh-ops/organizacional/organograma", methods=["GET"])
@login_required
def rh_org_organograma():
    return render_template("rh_ops/organizacional/organograma.html", active_menu="rh_org_organograma")


# ── Ponto & Frequência ──

@bp.route("/rh-ops/ponto/turnos", methods=["GET"])
@login_required
def rh_ponto_turnos():
    return render_template("rh_ops/ponto/turnos.html", active_menu="rh_ponto_turnos")


@bp.route("/rh-ops/ponto/escalas", methods=["GET"])
@login_required
def rh_ponto_escalas():
    return render_template("rh_ops/ponto/escalas.html", active_menu="rh_ponto_escalas")


@bp.route("/rh-ops/ponto/registros", methods=["GET"])
@login_required
def rh_ponto_registros():
    return render_template("rh_ops/ponto/registros.html", active_menu="rh_ponto_registros")


@bp.route("/rh-ops/ponto/horas-extras", methods=["GET"])
@login_required
def rh_ponto_horas_extras():
    return render_template("rh_ops/ponto/horas_extras.html", active_menu="rh_ponto_horas_extras")


@bp.route("/rh-ops/ponto/afastamentos", methods=["GET"])
@login_required
def rh_ponto_afastamentos():
    return render_template("rh_ops/ponto/afastamentos.html", active_menu="rh_ponto_afastamentos")


# ── Recrutamento & Admissão ──

@bp.route("/rh-ops/recrutamento/vagas", methods=["GET"])
@login_required
def rh_recrutamento_vagas():
    return render_template("rh_ops/recrutamento/vagas.html", active_menu="rh_recrutamento_vagas")


@bp.route("/rh-ops/recrutamento/candidatos", methods=["GET"])
@login_required
def rh_recrutamento_candidatos():
    return render_template("rh_ops/recrutamento/candidatos.html", active_menu="rh_recrutamento_candidatos")


@bp.route("/rh-ops/recrutamento/processo", methods=["GET"])
@login_required
def rh_recrutamento_processo():
    return render_template("rh_ops/recrutamento/processo.html", active_menu="rh_recrutamento_processo")


@bp.route("/rh-ops/recrutamento/onboarding", methods=["GET"])
@login_required
def rh_recrutamento_onboarding():
    return render_template("rh_ops/recrutamento/onboarding.html", active_menu="rh_recrutamento_onboarding")


# ── Treinamento & Desenvolvimento ──

@bp.route("/rh-ops/treinamento/catalogo", methods=["GET"])
@login_required
def rh_treinamento_catalogo():
    return render_template("rh_ops/treinamento/catalogo.html", active_menu="rh_treinamento_catalogo")


@bp.route("/rh-ops/treinamento/realizados", methods=["GET"])
@login_required
def rh_treinamento_realizados():
    return render_template("rh_ops/treinamento/realizados.html", active_menu="rh_treinamento_realizados")


@bp.route("/rh-ops/treinamento/certificacoes", methods=["GET"])
@login_required
def rh_treinamento_certificacoes():
    return render_template("rh_ops/treinamento/certificacoes.html", active_menu="rh_treinamento_certificacoes")


@bp.route("/rh-ops/treinamento/pdi", methods=["GET"])
@login_required
def rh_treinamento_pdi():
    return render_template("rh_ops/treinamento/pdi.html", active_menu="rh_treinamento_pdi")


# ── Saúde Ocupacional ──

@bp.route("/rh-ops/saude/aso", methods=["GET"])
@login_required
def rh_saude_aso():
    return render_template("rh_ops/saude/aso.html", active_menu="rh_saude_aso")


@bp.route("/rh-ops/saude/afastamentos", methods=["GET"])
@login_required
def rh_saude_afastamentos():
    return render_template("rh_ops/saude/afastamentos.html", active_menu="rh_saude_afastamentos")


@bp.route("/rh-ops/saude/epi", methods=["GET"])
@login_required
def rh_saude_epi():
    return render_template("rh_ops/saude/epi.html", active_menu="rh_saude_epi")


@bp.route("/rh-ops/saude/cipa", methods=["GET"])
@login_required
def rh_saude_cipa():
    return render_template("rh_ops/saude/cipa.html", active_menu="rh_saude_cipa")


# ── Transporte & Rotas ──

@bp.route("/rh-ops/transporte/dashboard", methods=["GET"])
@login_required
def rh_transporte_dashboard():
    from app.repositories import rh_transporte_repository as repo
    from app.services import rh_transporte_service as svc
    stats = repo.get_dashboard_stats()
    custos_rotas = svc.calcular_custos_rotas()
    precos = repo.listar_precos_combustivel()
    custo_total_dia = round(sum(c['custo_est'] for c in custos_rotas), 2)
    return render_template(
        "rh_ops/transporte/dashboard.html",
        active_menu="rh_transporte_dashboard",
        stats=stats,
        custos_rotas=custos_rotas,
        precos=precos,
        custo_total_dia=custo_total_dia,
    )


@bp.route("/rh-ops/transporte/rotas", methods=["GET"])
@login_required
def rh_transporte_rotas():
    from app.repositories import rh_transporte_repository as repo
    rotas = repo.listar_rotas()
    return render_template("rh_ops/transporte/rotas.html",
                           active_menu="rh_transporte_rotas", rotas=rotas)


@bp.route("/rh-ops/transporte/rotas/<int:rota_id>", methods=["GET"])
@login_required
def rh_transporte_rota_detalhe(rota_id):
    import os
    from flask import abort
    from app.repositories import rh_transporte_repository as repo
    from app.services import rh_transporte_service as svc
    rota = repo.buscar_rota(rota_id)
    if not rota:
        abort(404)
    colaboradores = repo.listar_colaboradores_rota(rota_id)
    ors_disponivel = bool(os.environ.get("ORS_API_KEY"))
    custos = svc.calcular_custos_rotas()
    custo_rota = next((c for c in custos if c['id'] == rota_id), None)
    precos = repo.listar_precos_combustivel()
    turno_configs = repo.listar_turno_configs()
    hora_saida_default = next(
        (t['horario_saida'] for t in turno_configs if t['turno'] == rota['turno']),
        '06:00'
    )
    return render_template(
        "rh_ops/transporte/rota_detalhe.html",
        active_menu="rh_transporte_rotas",
        rota=rota,
        colaboradores=colaboradores,
        ors_disponivel=ors_disponivel,
        custo_rota=custo_rota,
        precos=precos,
        hora_saida_default=hora_saida_default,
    )


# ── Transporte API ──

@bp.route("/rh-ops/api/transporte/rotas", methods=["POST"])
@login_required
def rh_api_criar_rota():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    try:
        rota = repo.criar_rota(
            codigo=d.get("codigo", "").strip(),
            nome=d.get("nome", "").strip(),
            filial=d.get("filial", ""),
            turno=d.get("turno", "1"),
            sentido=d.get("sentido", "ambos"),
            regra_descida=d.get("regra_descida", "agrupado"),
            veiculo=d.get("veiculo", ""),
            motorista=d.get("motorista", ""),
            cor=d.get("cor", "#0d6efd"),
            partida_nome=d.get("partida_nome", "Venttos — Polo Industrial de Manaus"),
            partida_lat=d.get("partida_lat"),
            partida_lng=d.get("partida_lng"),
        )
        return jsonify({"ok": True, "rota": dict(rota)})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>", methods=["PUT"])
@login_required
def rh_api_atualizar_rota(rota_id):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    rota = repo.atualizar_rota(rota_id, **d)
    if rota is None:
        return jsonify({"ok": False, "erro": "Rota não encontrada ou sem campos válidos"}), 404
    return jsonify({"ok": True, "rota": dict(rota)})


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>", methods=["DELETE"])
@login_required
def rh_api_deletar_rota(rota_id):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    ok = repo.deletar_rota(rota_id)
    return jsonify({"ok": ok})


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/colaboradores", methods=["GET"])
@login_required
def rh_api_listar_colaboradores(rota_id):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    colabs = repo.listar_colaboradores_rota(rota_id)
    return jsonify([dict(c) for c in colabs])


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/colaboradores", methods=["POST"])
@login_required
def rh_api_adicionar_colaborador(rota_id):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    try:
        colab = repo.adicionar_colaborador(
            rota_id=rota_id,
            employee_id=d.get("employee_id"),
            nome=d.get("nome", "").strip(),
            rua=d.get("endereco_rua", ""),
            numero=d.get("endereco_numero", ""),
            bairro=d.get("endereco_bairro", ""),
            cidade=d.get("endereco_cidade", "Manaus"),
            estado=d.get("endereco_estado", "AM"),
            tipo_parada=d.get("tipo_parada", "embarque_descida"),
            observacao=d.get("observacao", ""),
        )
        return jsonify({"ok": True, "colaborador": dict(colab)})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@bp.route("/rh-ops/api/transporte/colaboradores/<int:colab_id>", methods=["PUT"])
@login_required
def rh_api_atualizar_colaborador(colab_id):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    colab = repo.atualizar_colaborador(colab_id, **d)
    if colab is None:
        return jsonify({"ok": False, "erro": "Colaborador não encontrado"}), 404
    return jsonify({"ok": True, "colaborador": dict(colab)})


@bp.route("/rh-ops/api/transporte/colaboradores/<int:colab_id>", methods=["DELETE"])
@login_required
def rh_api_remover_colaborador(colab_id):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    ok = repo.remover_colaborador(colab_id)
    return jsonify({"ok": ok})


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/ordem", methods=["POST"])
@login_required
def rh_api_atualizar_ordem(rota_id):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    ids = d.get("ordem", [])
    if not isinstance(ids, list):
        return jsonify({"ok": False, "erro": "Formato inválido"}), 400
    repo.atualizar_ordem(rota_id, ids)
    return jsonify({"ok": True})


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/otimizar", methods=["POST"])
@login_required
def rh_api_otimizar_rota(rota_id):
    from flask import jsonify
    from app.services import rh_transporte_service as svc
    ordem = svc.otimizar_rota(rota_id)
    if ordem is None:
        return jsonify({"ok": False, "erro": "Otimização indisponível. Verifique ORS_API_KEY e geocodificação."}), 400
    return jsonify({"ok": True, "ordem": ordem})


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/trajeto", methods=["POST"])
@login_required
def rh_api_calcular_trajeto(rota_id):
    from flask import jsonify
    from app.services import rh_transporte_service as svc
    geojson = svc.calcular_trajeto(rota_id)
    if geojson is None:
        return jsonify({"ok": False, "erro": "Trajeto indisponível. Verifique ORS_API_KEY e geocodificação."}), 400
    return jsonify({"ok": True, "geojson": geojson})


@bp.route("/rh-ops/api/transporte/geocode", methods=["GET"])
@login_required
def rh_api_geocode():
    from flask import request, jsonify
    from app.services import rh_transporte_service as svc
    q = request.args.get("q", "").strip()
    cidade = request.args.get("cidade", "Manaus")
    estado = request.args.get("estado", "AM")
    if not q:
        return jsonify({"ok": False, "erro": "Endereço vazio"}), 400
    result = svc.geocodificar(q, cidade, estado)
    if result:
        return jsonify({"ok": True, **result})
    return jsonify({"ok": False, "erro": "Endereço não encontrado"}), 404


@bp.route("/rh-ops/api/transporte/employees/buscar", methods=["GET"])
@login_required
def rh_api_buscar_employees():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    employees = repo.buscar_employees(q)
    return jsonify([dict(e) for e in employees])


@bp.route("/rh-ops/transporte/veiculos", methods=["GET"])
@login_required
def rh_transporte_veiculos():
    from app.repositories import rh_transporte_repository as repo
    veiculos = repo.listar_veiculos()
    motoristas = repo.listar_motoristas()
    precos = repo.listar_precos_combustivel()
    return render_template("rh_ops/transporte/veiculos.html",
                           active_menu="rh_transporte_veiculos",
                           veiculos=veiculos, motoristas=motoristas,
                           precos=precos)


# ── Frota API ──

@bp.route("/rh-ops/api/transporte/veiculos", methods=["GET"])
@login_required
def rh_api_listar_veiculos():
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    return jsonify([dict(v) for v in repo.listar_veiculos()])


@bp.route("/rh-ops/api/transporte/veiculos", methods=["POST"])
@login_required
def rh_api_criar_veiculo():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    try:
        v = repo.criar_veiculo(
            placa=d.get("placa", "").strip().upper(),
            modelo=d.get("modelo", ""),
            ano=d.get("ano"),
            capacidade=int(d.get("capacidade") or 40),
            filial=d.get("filial", ""),
            status=d.get("status", "ativo"),
            observacao=d.get("observacao", ""),
            consumo_km_l=float(d["consumo_km_l"]) if d.get("consumo_km_l") else None,
            tipo_combustivel=d.get("tipo_combustivel", "diesel"),
        )
        return jsonify({"ok": True, "veiculo": dict(v)})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@bp.route("/rh-ops/api/transporte/veiculos/<int:vid>", methods=["PUT"])
@login_required
def rh_api_atualizar_veiculo(vid):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    if "placa" in d:
        d["placa"] = d["placa"].strip().upper()
    v = repo.atualizar_veiculo(vid, **d)
    if v is None:
        return jsonify({"ok": False, "erro": "Veículo não encontrado"}), 404
    return jsonify({"ok": True, "veiculo": dict(v)})


@bp.route("/rh-ops/api/transporte/veiculos/<int:vid>", methods=["DELETE"])
@login_required
def rh_api_deletar_veiculo(vid):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    ok = repo.deletar_veiculo(vid)
    return jsonify({"ok": ok})


@bp.route("/rh-ops/api/transporte/motoristas", methods=["GET"])
@login_required
def rh_api_listar_motoristas():
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    return jsonify([dict(m) for m in repo.listar_motoristas()])


@bp.route("/rh-ops/api/transporte/motoristas", methods=["POST"])
@login_required
def rh_api_criar_motorista():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    try:
        m = repo.criar_motorista(
            nome=d.get("nome", "").strip(),
            cnh=d.get("cnh", ""),
            categoria_cnh=d.get("categoria_cnh", ""),
            validade_cnh=d.get("validade_cnh") or None,
            telefone=d.get("telefone", ""),
            filial=d.get("filial", ""),
            status=d.get("status", "ativo"),
            observacao=d.get("observacao", ""),
        )
        return jsonify({"ok": True, "motorista": dict(m)})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@bp.route("/rh-ops/api/transporte/motoristas/<int:mid>", methods=["PUT"])
@login_required
def rh_api_atualizar_motorista(mid):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    m = repo.atualizar_motorista(mid, **d)
    if m is None:
        return jsonify({"ok": False, "erro": "Motorista não encontrado"}), 404
    return jsonify({"ok": True, "motorista": dict(m)})


@bp.route("/rh-ops/api/transporte/motoristas/<int:mid>", methods=["DELETE"])
@login_required
def rh_api_deletar_motorista(mid):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    ok = repo.deletar_motorista(mid)
    return jsonify({"ok": ok})


# ── Combustível API ──

@bp.route("/rh-ops/api/transporte/combustivel/precos", methods=["GET"])
@login_required
def rh_api_listar_precos_combustivel():
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    return jsonify({"ok": True, "precos": [dict(p) for p in repo.listar_precos_combustivel()]})


@bp.route("/rh-ops/api/transporte/combustivel/precos", methods=["POST"])
@login_required
def rh_api_upsert_preco_combustivel():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    tipo = (d.get("tipo") or "").strip().lower()
    preco_raw = d.get("preco_litro")
    if not tipo or preco_raw is None:
        return jsonify({"ok": False, "erro": "tipo e preco_litro são obrigatórios"}), 400
    try:
        preco = float(preco_raw)
        if preco <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"ok": False, "erro": "preco_litro inválido"}), 400
    config = repo.upsert_preco_combustivel(tipo=tipo, preco_litro=preco, fonte="manual")
    return jsonify({"ok": True, "config": dict(config)})


@bp.route("/rh-ops/api/transporte/combustivel/buscar-cotacao", methods=["GET"])
@login_required
def rh_api_buscar_cotacao_combustivel():
    from flask import jsonify
    from app.services import rh_transporte_service as svc
    resultado = svc.buscar_preco_externo()
    if resultado:
        return jsonify({"ok": True, "precos": resultado})
    return jsonify({"ok": False, "erro": "Fonte externa indisponível. Configure FUEL_PRICE_URL."}), 404


@bp.route("/rh-ops/api/transporte/combustivel/custos", methods=["GET"])
@login_required
def rh_api_custos_combustivel():
    from flask import jsonify
    from app.services import rh_transporte_service as svc
    custos = svc.calcular_custos_rotas()
    total = round(sum(c['custo_est'] for c in custos), 2)
    return jsonify({"ok": True, "custos": custos, "custo_total": total})


@bp.route("/rh-ops/api/transporte/combustivel/sincronizar-anp", methods=["POST"])
@login_required
def rh_api_sincronizar_anp():
    from flask import jsonify
    from app.services import anp_combustivel_service as anp_svc
    try:
        resultado = anp_svc.sincronizar_precos_anp()
        return jsonify({"ok": True, **resultado})
    except Exception as exc:
        return jsonify({"ok": False, "erro": str(exc)}), 500


@bp.route("/rh-ops/api/transporte/combustivel/anp-log", methods=["GET"])
@login_required
def rh_api_anp_log():
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    logs = repo.listar_anp_sync_log(limit=10)
    return jsonify([dict(l) for l in logs])


@bp.route("/rh-ops/api/transporte/rotas/<int:rota_id>/tempo", methods=["POST"])
@login_required
def rh_api_tempo_rota(rota_id):
    from flask import request, jsonify
    from app.services import rh_transporte_service as svc
    d = request.get_json(force=True) or {}
    hora_saida = (d.get("hora_saida") or "").strip()
    if not hora_saida:
        return jsonify({"ok": False, "erro": "hora_saida obrigatório (HH:MM)"}), 400
    resultado = svc.calcular_tempo_rota(rota_id, hora_saida)
    if resultado is None:
        return jsonify({"ok": False, "erro": "Rota não encontrada ou hora inválida"}), 404
    return jsonify({"ok": True, **resultado})


@bp.route("/rh-ops/transporte/alocacao", methods=["GET"])
@login_required
def rh_transporte_alocacao():
    from flask import request
    from app.repositories import rh_transporte_repository as repo
    turno = request.args.get("turno", "").strip() or None
    busca = request.args.get("busca", "").strip() or None
    rotas = repo.get_alocacao_view(turno=turno, busca=busca)
    total_colabs = sum(len(r['colaboradores']) for r in rotas)
    return render_template("rh_ops/transporte/alocacao.html",
                           active_menu="rh_transporte_alocacao",
                           rotas=rotas,
                           total_colabs=total_colabs,
                           filtro_turno=turno or "",
                           filtro_busca=busca or "")


@bp.route("/rh-ops/transporte/distribuidor", methods=["GET"])
@login_required
def rh_transporte_distribuidor():
    from app.repositories import rh_transporte_repository as repo
    rotas = repo.listar_rotas(ativo=True)
    departamentos = repo.listar_departamentos_employees()
    return render_template("rh_ops/transporte/distribuidor.html",
                           active_menu="rh_transporte_distribuidor",
                           rotas=rotas,
                           departamentos=departamentos)


@bp.route("/rh-ops/api/transporte/distribuidor/employees", methods=["GET"])
@login_required
def rh_api_distribuidor_employees():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    dept = request.args.get("departamento", "").strip() or None
    apenas_sem_rota = request.args.get("apenas_sem_rota", "").lower() in ("1", "true")
    employees = repo.listar_employees_para_distribuidor(departamento=dept, apenas_sem_rota=apenas_sem_rota)
    return jsonify([dict(e) for e in employees])


@bp.route("/rh-ops/api/transporte/distribuidor/preview", methods=["POST"])
@login_required
def rh_api_distribuidor_preview():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    from app.services import rh_transporte_service as svc
    d = request.get_json(force=True) or {}

    try:
        employee_ids = set(int(x) for x in (d.get("employee_ids") or []))
        rota_ids = set(int(x) for x in (d.get("rota_ids") or []))
    except (TypeError, ValueError):
        return jsonify({"error": "Parâmetros inválidos."}), 400

    criterio = (d.get("criterio") or "equilibrado").strip()

    if not employee_ids or not rota_ids:
        return jsonify({"error": "Selecione pelo menos um colaborador e uma rota."}), 400

    employees = [dict(e) for e in repo.listar_employees_para_distribuidor()
                 if e['id'] in employee_ids]
    rotas = [dict(r) for r in repo.listar_rotas()
             if r['id'] in rota_ids]

    distribuicao = svc.calcular_distribuicao(employees, rotas, criterio)

    resultado = []
    for rota in rotas:
        emps = distribuicao.get(rota['id'], [])
        resultado.append({
            'rota_id': rota['id'],
            'codigo': rota['codigo'],
            'nome': rota['nome'],
            'turno': rota['turno'],
            'cor': rota['cor'],
            'colaboradores': [
                {
                    'id': e['id'],
                    'full_name': e['full_name'],
                    'department': e['department'],
                    'employee_code': e['employee_code'],
                    'geocodificado': bool(e.get('geocodificado')),
                }
                for e in emps
            ],
            'total': len(emps),
        })

    return jsonify({'ok': True, 'rotas': resultado, 'total_colaboradores': len(employee_ids)})


@bp.route("/rh-ops/api/transporte/distribuidor/aplicar", methods=["POST"])
@login_required
def rh_api_distribuidor_aplicar():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}

    distribuicao = d.get("distribuicao") or []
    limpar_anterior = bool(d.get("limpar_anterior", False))

    rota_ids_afetados = [int(item['rota_id']) for item in distribuicao if item.get('rota_id')]

    if limpar_anterior and rota_ids_afetados:
        repo.limpar_colaboradores_rotas(rota_ids_afetados)

    employee_map = {e['id']: e for e in repo.listar_employees_para_distribuidor()}

    alocacoes = []
    for item in distribuicao:
        rota_id = int(item['rota_id'])
        for emp_id in (item.get('employee_ids') or []):
            emp = employee_map.get(int(emp_id))
            if not emp:
                continue
            alocacoes.append({
                'rota_id': rota_id,
                'employee_id': emp['id'],
                'nome': emp['full_name'],
                'endereco_rua': emp.get('endereco_rua'),
                'endereco_numero': emp.get('endereco_numero'),
                'endereco_bairro': emp.get('endereco_bairro'),
                'endereco_cidade': emp.get('endereco_cidade') or 'Manaus',
                'endereco_estado': emp.get('endereco_estado') or 'AM',
            })

    count = repo.distribuicao_em_massa(alocacoes)
    return jsonify({'ok': True, 'alocados': count})


@bp.route("/rh-ops/transporte/otimizador", methods=["GET"])
@login_required
def rh_transporte_otimizador():
    import os
    from app.repositories import rh_transporte_repository as repo
    rotas = repo.listar_rotas(ativo=True)
    ors_disponivel = bool(os.environ.get("ORS_API_KEY"))
    return render_template("rh_ops/transporte/otimizador.html",
                           active_menu="rh_transporte_otimizador",
                           rotas=rotas,
                           ors_disponivel=ors_disponivel)


@bp.route("/rh-ops/transporte/configuracoes", methods=["GET"])
@login_required
def rh_transporte_config_turno():
    from app.repositories import rh_transporte_repository as repo
    configs = repo.listar_turno_configs()
    return render_template("rh_ops/transporte/config_turno.html",
                           active_menu="rh_transporte_config_turno", configs=configs)


# ── Config Turno API ──

@bp.route("/rh-ops/api/transporte/config-turno", methods=["POST"])
@login_required
def rh_api_criar_turno_config():
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    try:
        c = repo.criar_turno_config(
            turno=d.get("turno", "").strip(),
            filial=d.get("filial", "VTT").strip(),
            tipo_descida=d.get("tipo_descida", "agrupado"),
            raio_embarque_m=int(d.get("raio_embarque_m") or 500),
            tolerancia_min=int(d.get("tolerancia_min") or 10),
            horario_saida=d.get("horario_saida") or None,
            observacao=d.get("observacao", ""),
        )
        return jsonify({"ok": True, "config": dict(c)})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@bp.route("/rh-ops/api/transporte/config-turno/<int:config_id>", methods=["PUT"])
@login_required
def rh_api_atualizar_turno_config(config_id):
    from flask import request, jsonify
    from app.repositories import rh_transporte_repository as repo
    d = request.get_json(force=True) or {}
    c = repo.atualizar_turno_config(config_id, **d)
    if c is None:
        return jsonify({"ok": False, "erro": "Configuração não encontrada"}), 404
    return jsonify({"ok": True, "config": dict(c)})


@bp.route("/rh-ops/api/transporte/config-turno/<int:config_id>", methods=["DELETE"])
@login_required
def rh_api_deletar_turno_config(config_id):
    from flask import jsonify
    from app.repositories import rh_transporte_repository as repo
    ok = repo.deletar_turno_config(config_id)
    return jsonify({"ok": ok})


# ── Relatórios & Indicadores ──

@bp.route("/rh-ops/relatorios/headcount", methods=["GET"])
@login_required
def rh_relatorios_headcount():
    return render_template("rh_ops/relatorios/headcount.html", active_menu="rh_relatorios_headcount")


@bp.route("/rh-ops/relatorios/turnover", methods=["GET"])
@login_required
def rh_relatorios_turnover():
    return render_template("rh_ops/relatorios/turnover.html", active_menu="rh_relatorios_turnover")


@bp.route("/rh-ops/relatorios/absenteismo", methods=["GET"])
@login_required
def rh_relatorios_absenteismo():
    return render_template("rh_ops/relatorios/absenteismo.html", active_menu="rh_relatorios_absenteismo")


@bp.route("/rh-ops/relatorios/custo-pessoal", methods=["GET"])
@login_required
def rh_relatorios_custo_pessoal():
    return render_template("rh_ops/relatorios/custo_pessoal.html", active_menu="rh_relatorios_custo_pessoal")


@bp.route("/rh-ops/relatorios/transporte", methods=["GET"])
@login_required
def rh_relatorios_transporte():
    return render_template("rh_ops/relatorios/transporte.html", active_menu="rh_relatorios_transporte")


# ENGENHARIA HUB


@bp.route("/funcionalidades/sistemas/engenharia-hub", methods=["GET"])
@login_required
def eng_hub():
    return render_template("engenharia/eng_hub.html", active_menu="eng_hub")


# Engenharia de Processo

@bp.route("/engenharia/processo/fluxo", methods=["GET"])
@login_required
def eng_processo_fluxo():
    return render_template("engenharia/processo/fluxo.html", active_menu="eng_hub")


@bp.route("/engenharia/processo/balanceamento", methods=["GET"])
@login_required
def eng_processo_balanceamento():
    return render_template("engenharia/processo/balanceamento.html", active_menu="eng_hub")


@bp.route("/engenharia/processo/desperdicios", methods=["GET"])
@login_required
def eng_processo_desperdicios():
    return render_template("engenharia/processo/desperdicios.html", active_menu="eng_hub")


@bp.route("/engenharia/processo/pdca", methods=["GET"])
@login_required
def eng_processo_pdca():
    return render_template("engenharia/processo/pdca.html", active_menu="eng_hub")


# Engenharia Industrial

@bp.route("/engenharia/industrial/layout", methods=["GET"])
@login_required
def eng_ind_layout():
    return render_template("engenharia/industrial/layout.html", active_menu="eng_hub")


@bp.route("/engenharia/industrial/capacidade", methods=["GET"])
@login_required
def eng_ind_capacidade():
    return render_template("engenharia/industrial/capacidade.html", active_menu="eng_hub")


@bp.route("/engenharia/industrial/custos", methods=["GET"])
@login_required
def eng_ind_custos():
    return render_template("engenharia/industrial/custos.html", active_menu="eng_hub")


@bp.route("/engenharia/industrial/produtividade", methods=["GET"])
@login_required
def eng_ind_produtividade():
    return render_template("engenharia/industrial/produtividade.html", active_menu="eng_hub")


@bp.route("/engenharia/industrial/logistica", methods=["GET"])
@login_required
def eng_ind_logistica():
    return render_template("engenharia/industrial/logistica.html", active_menu="eng_hub")


# Engenharia de Manufatura

@bp.route("/engenharia/manufatura/npi", methods=["GET"])
@login_required
def eng_man_npi():
    return render_template("engenharia/manufatura/npi.html", active_menu="eng_hub")


@bp.route("/engenharia/manufatura/ferramentas", methods=["GET"])
@login_required
def eng_man_ferramentas():
    return render_template("engenharia/manufatura/ferramentas.html", active_menu="eng_hub")


@bp.route("/engenharia/manufatura/documentacao", methods=["GET"])
@login_required
def eng_man_documentacao():
    return render_template("engenharia/manufatura/documentacao.html", active_menu="eng_hub")


@bp.route("/engenharia/manufatura/jigs", methods=["GET"])
@login_required
def eng_man_jigs():
    return render_template("engenharia/manufatura/jigs.html", active_menu="eng_hub")


# Melhoria Contínua

@bp.route("/engenharia/melhoria/lean", methods=["GET"])
@login_required
def eng_mc_lean():
    return render_template("engenharia/melhoria/lean.html", active_menu="eng_hub")


@bp.route("/engenharia/melhoria/kaizen", methods=["GET"])
@login_required
def eng_mc_kaizen():
    return render_template("engenharia/melhoria/kaizen.html", active_menu="eng_hub")


@bp.route("/engenharia/melhoria/six-sigma", methods=["GET"])
@login_required
def eng_mc_six_sigma():
    return render_template("engenharia/melhoria/six_sigma.html", active_menu="eng_hub")


@bp.route("/engenharia/melhoria/projetos", methods=["GET"])
@login_required
def eng_mc_projetos():
    return render_template("engenharia/melhoria/projetos.html", active_menu="eng_hub")


# Engenharia de Teste

@bp.route("/engenharia/teste/bancadas", methods=["GET"])
@login_required
def eng_teste_bancadas():
    return render_template("engenharia/teste/bancadas.html", active_menu="eng_hub")


@bp.route("/engenharia/teste/programas", methods=["GET"])
@login_required
def eng_teste_programas():
    return render_template("engenharia/teste/programas.html", active_menu="eng_hub")


@bp.route("/engenharia/teste/analise-falhas", methods=["GET"])
@login_required
def eng_teste_analise_falhas():
    return render_template("engenharia/teste/analise_falhas.html", active_menu="eng_hub")


@bp.route("/engenharia/teste/validacao", methods=["GET"])
@login_required
def eng_teste_validacao():
    return render_template("engenharia/teste/validacao.html", active_menu="eng_hub")


# Engenharia de Desenvolvimento de Testes

@bp.route("/engenharia/dev-testes/hardware", methods=["GET"])
@login_required
def eng_dev_hardware():
    return render_template("engenharia/dev_testes/hardware.html", active_menu="eng_hub")


@bp.route("/engenharia/dev-testes/software", methods=["GET"])
@login_required
def eng_dev_software():
    return render_template("engenharia/dev_testes/software.html", active_menu="eng_hub")


@bp.route("/engenharia/dev-testes/jigs", methods=["GET"])
@login_required
def eng_dev_jigs():
    return render_template("engenharia/dev_testes/jigs.html", active_menu="eng_hub")


@bp.route("/engenharia/dev-testes/automaticos", methods=["GET"])
@login_required
def eng_dev_automaticos():
    return render_template("engenharia/dev_testes/automaticos.html", active_menu="eng_hub")


# Engenharia de Confiabilidade

@bp.route("/engenharia/confiabilidade/vida-util", methods=["GET"])
@login_required
def eng_conf_vida_util():
    return render_template("engenharia/confiabilidade/vida_util.html", active_menu="eng_hub")


@bp.route("/engenharia/confiabilidade/ensaios", methods=["GET"])
@login_required
def eng_conf_ensaios():
    return render_template("engenharia/confiabilidade/ensaios.html", active_menu="eng_hub")


@bp.route("/engenharia/confiabilidade/estatistica", methods=["GET"])
@login_required
def eng_conf_estatistica():
    return render_template("engenharia/confiabilidade/estatistica.html", active_menu="eng_hub")


@bp.route("/engenharia/confiabilidade/mtbf", methods=["GET"])
@login_required
def eng_conf_mtbf():
    return render_template("engenharia/confiabilidade/mtbf.html", active_menu="eng_hub")


# Engenharia de Qualidade

@bp.route("/engenharia/qualidade/auditorias", methods=["GET"])
@login_required
def eng_qual_auditorias():
    return render_template("engenharia/qualidade/auditorias.html", active_menu="eng_hub")


@bp.route("/engenharia/qualidade/fmea", methods=["GET"])
@login_required
def eng_qual_fmea():
    return render_template("engenharia/qualidade/fmea.html", active_menu="eng_hub")


@bp.route("/engenharia/qualidade/cep", methods=["GET"])
@login_required
def eng_qual_cep():
    return render_template("engenharia/qualidade/cep.html", active_menu="eng_hub")


@bp.route("/engenharia/qualidade/nao-conformidades", methods=["GET"])
@login_required
def eng_qual_nao_conformidades():
    return render_template("engenharia/qualidade/nao_conformidades.html", active_menu="eng_hub")


@bp.route("/engenharia/qualidade/indicadores", methods=["GET"])
@login_required
def eng_qual_indicadores():
    return render_template("engenharia/qualidade/indicadores.html", active_menu="eng_hub")


# Engenharia de Produto

@bp.route("/engenharia/produto/desenvolvimento", methods=["GET"])
@login_required
def eng_produto_desenvolvimento():
    return render_template("engenharia/produto/desenvolvimento.html", active_menu="eng_hub")


@bp.route("/engenharia/produto/modificacoes", methods=["GET"])
@login_required
def eng_produto_modificacoes():
    return render_template("engenharia/produto/modificacoes.html", active_menu="eng_hub")


@bp.route("/engenharia/produto/especificacoes", methods=["GET"])
@login_required
def eng_produto_especificacoes():
    return render_template("engenharia/produto/especificacoes.html", active_menu="eng_hub")


@bp.route("/engenharia/produto/homologacao", methods=["GET"])
@login_required
def eng_produto_homologacao():
    return render_template("engenharia/produto/homologacao.html", active_menu="eng_hub")


@bp.route("/engenharia/produto/modelos-cliente", methods=["GET"])
@login_required
def eng_produto_modelos_cliente():
    return render_template("engenharia/produto/modelos_cliente.html", active_menu="eng_hub")


# Engenharia de Automação

@bp.route("/engenharia/automacao/clps", methods=["GET"])
@login_required
def eng_aut_clps():
    return render_template("engenharia/automacao/clps.html", active_menu="eng_hub")


@bp.route("/engenharia/automacao/robotica", methods=["GET"])
@login_required
def eng_aut_robotica():
    return render_template("engenharia/automacao/robotica.html", active_menu="eng_hub")


@bp.route("/engenharia/automacao/sensores", methods=["GET"])
@login_required
def eng_aut_sensores():
    return render_template("engenharia/automacao/sensores.html", active_menu="eng_hub")


@bp.route("/engenharia/automacao/ihm", methods=["GET"])
@login_required
def eng_aut_ihm():
    return render_template("engenharia/automacao/ihm.html", active_menu="eng_hub")


@bp.route("/engenharia/automacao/redes", methods=["GET"])
@login_required
def eng_aut_redes():
    return render_template("engenharia/automacao/redes.html", active_menu="eng_hub")


# PCI Studio

@bp.route("/engenharia/pci-studio", methods=["GET"])
@login_required
def eng_pci_studio_hub():
    from app.repositories import pci_studio_repository as repo
    projetos = repo.listar_projetos()
    stats = repo.stats_biblioteca()
    return render_template(
        "engenharia/pci_studio/hub.html",
        active_menu="eng_pci_studio_hub",
        projetos=projetos,
        stats=stats,
    )


@bp.route("/engenharia/pci-studio/projetos/<int:projeto_id>", methods=["GET"])
@login_required
def eng_pci_studio_detalhe(projeto_id):
    from flask import abort
    from app.repositories import pci_studio_repository as repo
    projeto = repo.buscar_projeto_com_bom(projeto_id)
    if not projeto:
        abort(404)
    return render_template(
        "engenharia/pci_studio/projeto_detalhe.html",
        active_menu="eng_pci_studio_hub",
        projeto=projeto,
    )


@bp.route("/engenharia/pci-studio/componentes", methods=["GET"])
@login_required
def eng_pci_studio_componentes():
    from app.repositories import pci_studio_repository as repo
    componentes = repo.listar_componentes()
    stats = repo.stats_biblioteca()
    return render_template(
        "engenharia/pci_studio/componentes.html",
        active_menu="eng_pci_studio_componentes",
        componentes=componentes,
        stats=stats,
    )


@bp.route("/engenharia/api/pci-studio/projetos", methods=["POST"])
@login_required
def eng_api_pci_criar_projeto():
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    data = request.get_json(force=True) or {}
    try:
        projeto = repo.criar_projeto(
            nome=data.get("nome", "").strip(),
            codigo=data.get("codigo", "").strip(),
            descricao=data.get("descricao", "").strip(),
            comp_mm=float(data.get("comp_mm", 100)),
            larg_mm=float(data.get("larg_mm", 80)),
            esp_mm=float(data.get("esp_mm", 1.6)),
            cor_placa=data.get("cor_placa", "#1d4f2a"),
            criado_por=current_user.id,
        )
        return jsonify({"ok": True, "projeto": dict(projeto)}), 201
    except Exception as exc:
        return jsonify({"ok": False, "erro": str(exc)}), 400


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>", methods=["PUT"])
@login_required
def eng_api_pci_atualizar_projeto(projeto_id):
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    data = request.get_json(force=True) or {}
    result = repo.atualizar_projeto(projeto_id, **data)
    if not result:
        return jsonify({"ok": False, "erro": "Projeto não encontrado"}), 404
    return jsonify({"ok": True, "projeto": dict(result)})


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>", methods=["DELETE"])
@login_required
def eng_api_pci_deletar_projeto(projeto_id):
    from flask import jsonify
    from app.repositories import pci_studio_repository as repo
    ok = repo.deletar_projeto(projeto_id)
    return jsonify({"ok": ok})


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>/upload", methods=["POST"])
@login_required
def eng_api_pci_upload(projeto_id):
    import os, uuid
    from flask import request, jsonify, current_app
    from werkzeug.utils import secure_filename
    from app.repositories import pci_studio_repository as repo

    ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}
    f    = request.files.get('arquivo')
    tipo = request.form.get('tipo', 'doc')

    if not f or not f.filename:
        return jsonify({'ok': False, 'erro': 'Nenhum arquivo enviado'}), 400

    ext = os.path.splitext(f.filename.lower())[1]
    if ext not in ALLOWED_EXT:
        return jsonify({'ok': False, 'erro': 'Tipo de arquivo não permitido'}), 400

    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'pci_studio', str(projeto_id))
    os.makedirs(upload_dir, exist_ok=True)

    filename = f'{uuid.uuid4().hex}{ext}'
    f.save(os.path.join(upload_dir, filename))
    url = f'/static/uploads/pci_studio/{projeto_id}/{filename}'

    if tipo == 'top':
        repo.atualizar_projeto(projeto_id, img_top=url)
    elif tipo == 'bottom':
        repo.atualizar_projeto(projeto_id, img_bottom=url)
    else:
        nome_orig = secure_filename(f.filename) or filename
        repo.adicionar_doc_projeto(projeto_id, {'nome': nome_orig, 'url': url, 'tipo': ext.lstrip('.')})

    return jsonify({'ok': True, 'url': url})


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>/bom/detectar-colunas", methods=["POST"])
@login_required
def eng_api_pci_detectar_colunas(projeto_id):
    from flask import request, jsonify
    from app.services import pci_studio_service as svc
    f = request.files.get("arquivo")
    if not f:
        return jsonify({"ok": False, "erro": "Arquivo não enviado"}), 400
    f_bytes = f.read()
    filename = f.filename or 'bom.csv'
    try:
        header, _ = svc.extrair_header_e_rows(f_bytes, filename)
    except Exception as e:
        return jsonify({"ok": False, "erro": f"Erro ao processar arquivo: {e}"}), 400
    if not header:
        return jsonify({"ok": False, "erro": "Arquivo vazio ou sem colunas reconhecíveis"}), 400
    mapa = svc.detectar_colunas(header)
    return jsonify({"ok": True, "header": header, "mapa": mapa})


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>/bom/importar", methods=["POST"])
@login_required
def eng_api_pci_importar_bom(projeto_id):
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    from app.services import pci_studio_service as svc
    import json as _json
    f = request.files.get("arquivo")
    mapa_raw = request.form.get("mapa", "{}")
    if not f:
        return jsonify({"ok": False, "erro": "Arquivo não enviado"}), 400
    try:
        mapa = _json.loads(mapa_raw)
    except ValueError:
        mapa = {}
    f_bytes = f.read()
    filename = f.filename or 'bom.csv'
    projeto = repo.buscar_projeto(projeto_id)
    if not projeto:
        return jsonify({"ok": False, "erro": "Projeto não encontrado"}), 404
    try:
        items = svc.parse_bom_arquivo(f_bytes, filename, mapa)
    except Exception as e:
        return jsonify({"ok": False, "erro": f"Erro ao processar arquivo: {e}"}), 400
    items, matched = svc.auto_match_componentes(items)
    items = svc.gerar_posicoes_automaticas(items, projeto["comp_mm"], projeto["larg_mm"])
    if request.form.get("substituir") == "1":
        repo.deletar_bom_items_projeto(projeto_id)
    count = repo.inserir_bom_items(projeto_id, items)
    return jsonify({"ok": True, "inseridos": count, "matched": matched})


@bp.route("/engenharia/api/pci-studio/projetos/<int:projeto_id>/bom", methods=["GET"])
@login_required
def eng_api_pci_bom_json(projeto_id):
    from flask import jsonify, abort
    from app.repositories import pci_studio_repository as repo
    projeto = repo.buscar_projeto_com_bom(projeto_id)
    if not projeto:
        abort(404)
    return jsonify(projeto)


@bp.route("/engenharia/api/pci-studio/bom/<int:item_id>", methods=["PATCH"])
@login_required
def eng_api_pci_atualizar_bom_item(item_id):
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    data = request.get_json(force=True) or {}
    result = repo.atualizar_bom_item(item_id, **data)
    if not result:
        return jsonify({"ok": False, "erro": "Item não encontrado"}), 404
    return jsonify({"ok": True, "item": dict(result)})


@bp.route("/engenharia/api/pci-studio/componentes", methods=["GET"])
@login_required
def eng_api_pci_listar_componentes():
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    tipo = request.args.get("tipo")
    componentes = repo.listar_componentes(tipo)
    return jsonify([dict(c) for c in componentes])


@bp.route("/engenharia/api/pci-studio/componentes", methods=["POST"])
@login_required
def eng_api_pci_criar_componente():
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    data = request.get_json(force=True) or {}
    try:
        comp = repo.criar_componente(**data)
        return jsonify({"ok": True, "componente": dict(comp)}), 201
    except Exception as exc:
        return jsonify({"ok": False, "erro": str(exc)}), 400


@bp.route("/engenharia/api/pci-studio/componentes/<int:comp_id>", methods=["PUT"])
@login_required
def eng_api_pci_atualizar_componente(comp_id):
    from flask import request, jsonify
    from app.repositories import pci_studio_repository as repo
    data = request.get_json(force=True) or {}
    result = repo.atualizar_componente(comp_id, **data)
    if not result:
        return jsonify({"ok": False, "erro": "Componente não encontrado"}), 404
    return jsonify({"ok": True, "componente": dict(result)})


@bp.route("/engenharia/api/pci-studio/componentes/<int:comp_id>", methods=["DELETE"])
@login_required
def eng_api_pci_deletar_componente(comp_id):
    from flask import jsonify
    from app.repositories import pci_studio_repository as repo
    ok = repo.deletar_componente(comp_id)
    return jsonify({"ok": ok})


# Engenharia de Manutenção

@bp.route("/engenharia/manutencao/preventiva", methods=["GET"])
@login_required
def eng_mnt_preventiva():
    return render_template("engenharia/manutencao/preventiva.html", active_menu="eng_hub")


@bp.route("/engenharia/manutencao/preditiva", methods=["GET"])
@login_required
def eng_mnt_preditiva():
    return render_template("engenharia/manutencao/preditiva.html", active_menu="eng_hub")


@bp.route("/engenharia/manutencao/corretiva", methods=["GET"])
@login_required
def eng_mnt_corretiva():
    return render_template("engenharia/manutencao/corretiva.html", active_menu="eng_hub")


@bp.route("/engenharia/manutencao/plano", methods=["GET"])
@login_required
def eng_mnt_plano():
    return render_template("engenharia/manutencao/plano.html", active_menu="eng_hub")


@bp.route("/engenharia/manutencao/indicadores", methods=["GET"])
@login_required
def eng_mnt_indicadores():
    return render_template("engenharia/manutencao/indicadores.html", active_menu="eng_hub")


@bp.route("/engenharia/smd/maquinas-virtuais", methods=["GET"])
@login_required
def eng_smd_maquinas_virtuais():
    return render_template("engenharia/smd/maquinas_virtuais.html", active_menu="eng_hub")


@bp.route("/sw.js", endpoint="pwa_sw")
def service_worker():
    from flask import current_app, make_response, render_template

    app_version = current_app.config.get("APP_VERSION", "dev")
    content = render_template("pwa/sw.js", app_version=app_version)
    resp = make_response(content)
    resp.headers["Content-Type"] = "application/javascript; charset=utf-8"
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp
