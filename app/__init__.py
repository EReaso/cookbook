from flask import Flask
from app.extensions import *
from app.book import bp as recipe_bp

app = Flask(__name__)

app.config.from_object("app.config.Config")

# api.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(recipe_bp)
