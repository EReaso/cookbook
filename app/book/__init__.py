from flask_smorest import Blueprint

bp = Blueprint("book", __name__)

from app.book import routes
