from flask import Blueprint

bp = Blueprint("book", __name__, url_prefix="/book")

from app.book import routes  # noqa: F401,E402
