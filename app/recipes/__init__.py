from flask import Blueprint

bp = Blueprint("recipes", __name__, url_prefix="/recipes/")

from app.recipes import routes  # noqa: F401
