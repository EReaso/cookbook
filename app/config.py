import os
import secrets


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Auto-generate SECRET_KEY if not provided for security
    # WARNING: This generates a NEW key on each startup, invalidating sessions
    # Set SECRET_KEY environment variable for persistent sessions
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
