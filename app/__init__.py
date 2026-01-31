from flask import Flask

from app.book import bp as book_bp
from app.extensions import db, migrate, storage
from app.images import bp as images_bp
from app.recipes import bp as recipe_bp

app = Flask(__name__)

app.config.from_object("app.config.Config")
storage.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(recipe_bp)
app.register_blueprint(images_bp)
app.register_blueprint(book_bp)
