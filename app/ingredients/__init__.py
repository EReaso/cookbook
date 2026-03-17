from flask import Blueprint

bp = Blueprint("ingredients", __name__, url_prefix="/ingredients")

from . import routes  # noqa: E402, F401
