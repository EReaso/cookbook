"""Tests for extension initialization."""

from pathlib import Path

import app.extensions as extensions


def test_init_app_initializes_extensions(monkeypatch, tmp_path):
    calls = []

    def fake_db_init(app):
        calls.append(("db", app))

    def fake_migrate_init(app, db):
        calls.append(("migrate", app, db))

    monkeypatch.setattr(extensions.db, "init_app", fake_db_init)
    monkeypatch.setattr(extensions.migrate, "init_app", fake_migrate_init)

    class DummyApp:
        instance_path = str(tmp_path)

    app = DummyApp()

    result = extensions.init_app(app)

    assert result is None
    assert (Path(app.instance_path) / "storage").exists()
    assert app.extensions["storage"] is extensions.storage
    assert calls[0] == ("db", app)
    assert calls[1] == ("migrate", app, extensions.db)
