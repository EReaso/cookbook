from flask import Blueprint

bp = Blueprint("images", __name__, url_prefix="/images")

from app.images import routes  # noqa: F401,E402
