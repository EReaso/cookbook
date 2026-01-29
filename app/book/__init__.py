from flask import Blueprint

bp = Blueprint("book", __name__)

from app.book import routes  # noqa: F401
