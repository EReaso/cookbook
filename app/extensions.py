from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.storage import Storage

db = SQLAlchemy()
migrate = Migrate()
storage = Storage
