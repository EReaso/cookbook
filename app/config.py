import os
import secrets


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Auto-generate SECRET_KEY if not provided for security
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
