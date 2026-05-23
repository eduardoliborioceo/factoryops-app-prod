from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, request, jsonify, current_app


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if not current_user.is_admin:
            return redirect(url_for("pages.dashboard"))

        return func(*args, **kwargs)
    return wrapper


def api_key_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = current_app.config.get("SYNC_API_KEY", "")
        if not api_key:
            return jsonify({"erro": "Sync não configurado no servidor."}), 503

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"erro": "Token ausente."}), 401

        if auth_header[7:] != api_key:
            return jsonify({"erro": "Token inválido."}), 401

        return func(*args, **kwargs)
    return wrapper
