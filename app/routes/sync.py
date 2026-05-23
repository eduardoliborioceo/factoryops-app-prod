from flask import Blueprint, request, jsonify
from app.auth.decorators import api_key_required
from app.services import producao_coletada_service as pc_svc
from app.services import producao_mes_service as mes_svc

bp = Blueprint("sync", __name__)


@bp.route("/producao-coletada", methods=["POST"])
@api_key_required
def sync_producao_coletada():
    registros = request.get_json(force=True, silent=True)
    if not isinstance(registros, list):
        return jsonify({"erro": "Corpo deve ser uma lista JSON."}), 400
    if not registros:
        return jsonify({"ok": True, "salvos": 0, "mensagem": "Nenhum registro enviado."})

    try:
        job_id = pc_svc.iniciar_importacao_lista(registros)
        return jsonify({"job_id": job_id})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/producao-coletada/progresso/<job_id>")
@api_key_required
def sync_producao_coletada_progresso(job_id):
    return jsonify(pc_svc.status_importacao(job_id))


@bp.route("/producao-mes", methods=["POST"])
@api_key_required
def sync_producao_mes():
    registros = request.get_json(force=True, silent=True)
    if not isinstance(registros, list):
        return jsonify({"erro": "Corpo deve ser uma lista JSON."}), 400
    if not registros:
        return jsonify({"ok": True, "salvos": 0, "mensagem": "Nenhum registro enviado."})

    try:
        job_id = mes_svc.iniciar_importacao_lista(registros)
        return jsonify({"job_id": job_id})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@bp.route("/producao-mes/progresso/<job_id>")
@api_key_required
def sync_producao_mes_progresso(job_id):
    return jsonify(mes_svc.status_importacao(job_id))
