from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.storage import Storage

db = SQLAlchemy()
migrate = Migrate()
# Create a Storage instance without an app; `init_app` will finish initialization
storage = Storage()


def init_app(app):
    """Initialize all extensions with the provided Flask app.

    This follows the Flask extension pattern where extensions are created at
    import time and bound to the app in an `init_app` call.
    """
    # initialize storage with the app (will register in app.extensions)
    storage.init_app(app)

    # initialize database and migration extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return None
