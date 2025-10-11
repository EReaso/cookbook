from flask import Blueprint

bp = Blueprint("recipes", __name__)

from app.recipes import routes
