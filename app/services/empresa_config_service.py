from app.repositories import empresa_config_repository as repo

_GRUPOS_VALIDOS = {"funcionalidades", "producao", "engenharia", "pcp", "logistica", "configuracoes"}
_FILIAIS_VALIDAS = {"VTE", "VTT", "SMD"}
_SETORES_VALIDOS = {"SMD", "PTH", "IM/PA"}


def get_config() -> dict:
    try:
        return repo.get_config()
    except Exception:
        return repo._DEFAULTS.copy()


def update_config(form: dict) -> None:
    nome_empresa = (form.get("nome_empresa") or "").strip()
    if not nome_empresa:
        raise ValueError("Nome da empresa é obrigatório.")
    if len(nome_empresa) > 200:
        raise ValueError("Nome da empresa muito longo (máx. 200 caracteres).")

    filiais = [f for f in form.getlist("filiais") if f in _FILIAIS_VALIDAS]
    if not filiais:
        raise ValueError("Selecione ao menos uma filial ativa.")

    menu_visivel = {g: (g in form.getlist("menu_visivel")) for g in _GRUPOS_VALIDOS}

    setores_por_filial = {}
    for filial in filiais:
        setores = [s for s in form.getlist(f"setores_{filial}") if s in _SETORES_VALIDOS]
        setores_por_filial[filial] = setores

    repo.update_config({
        "nome_empresa": nome_empresa,
        "nome_exibicao": (form.get("nome_exibicao") or "").strip() or None,
        "cnpj": (form.get("cnpj") or "").strip() or None,
        "filiais": filiais,
        "menu_visivel": menu_visivel,
        "setores_por_filial": setores_por_filial,
    })


def upload_logo(file) -> str:
    import cloudinary
    import cloudinary.uploader
    from flask import current_app

    if not file or file.filename == "":
        raise ValueError("Nenhum arquivo enviado.")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in {"png", "jpg", "jpeg", "webp", "svg"}:
        raise ValueError("Formato de imagem não suportado. Use PNG, JPG, WEBP ou SVG.")

    cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME")
    api_key = current_app.config.get("CLOUDINARY_API_KEY")
    api_secret = current_app.config.get("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise ValueError("Serviço de upload de imagem (Cloudinary) não configurado.")

    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
    result = cloudinary.uploader.upload(
        file,
        public_id="factoryops/empresa/logo",
        overwrite=True,
        resource_type="image",
        transformation={"width": 400, "height": 200, "crop": "fit", "background": "transparent"},
    )
    logo_url = result["secure_url"]
    repo.update_logo(logo_url)
    return logo_url


def remove_logo() -> None:
    repo.update_logo(None)
