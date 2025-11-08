from flask import Flask
from app.extensions import *
from app.book import bp as recipe_bp
from app.images import bp as images_bp

app = Flask(__name__)

app.config.from_object("app.config.Config")

storage.__init__(dir=app.instance_path)

# api.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(recipe_bp)
app.register_blueprint(images_bp)
