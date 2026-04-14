from flask import Blueprint

bp = Blueprint("tags", __name__, url_prefix="/tags")

from . import routes  # noqa: E402, F401
