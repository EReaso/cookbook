"""Test configuration and fixtures."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repository root is on sys.path so `import app` works in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from importlib import import_module

_app = import_module("app")
_create = getattr(_app, "create_app", None)
flask_app = _create() if callable(_create) else getattr(_app, "app")
_db = import_module("app.extensions").db


@pytest.fixture(scope="session")
def app():
    """Create and configure a test Flask application instance."""
    # Create a temporary directory for test database and storage
    db_fd, db_path = tempfile.mkstemp()
    storage_dir = tempfile.mkdtemp()

    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
        }
    )

    # Update storage directory for testing
    from app.extensions import storage

    storage.init_app(flask_app, dir=storage_dir)

    # Create the database and tables
    with flask_app.app_context():
        _db.create_all()

    yield flask_app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    # Clean up storage directory
    import shutil

    shutil.rmtree(storage_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def sample_recipe(db):
    """Create a sample recipe for testing."""
    from app.recipes.models import Recipe, RecipeIngredient

    # Depend on the `sample_ingredient` fixture for a related ingredient
    # (pytest will resolve this dependency automatically)
    # Create the recipe and a linking RecipeIngredient using relationships
    # so SQLAlchemy sets foreign keys correctly.
    recipe = Recipe(slug="test-recipe", name="Test Recipe", directions="1. Do this\n2. Do that")
    db.session.add(recipe)
    db.session.flush()

    # create a minimal RecipeIngredient in tests via relationship assignment
    ri = RecipeIngredient(list="main", amount=1.0, unit="cup", recipe=recipe, ingredient=sample_ingredient(db))
    db.session.add(ri)
    db.session.commit()
    return recipe


@pytest.fixture
def sample_ingredient(db):
    """Create a sample ingredient for testing."""
    from app.recipes.models import Ingredient

    ingredient = Ingredient(slug="test-ingredient", name="Test Ingredient", density=1.0)
    db.session.add(ingredient)
    db.session.commit()
    return ingredient


@pytest.fixture
def sample_recipe_ingredient(db, sample_recipe, sample_ingredient):
    """Create a sample recipe-ingredient relationship for testing."""
    from app.recipes.models import RecipeIngredient

    # Create via relationships to ensure SQLAlchemy handles FK values
    ri = RecipeIngredient(list="main", amount=2.0, unit="cups", recipe=sample_recipe, ingredient=sample_ingredient)
    db.session.add(ri)
    db.session.commit()
    return ri


@pytest.fixture
def storage_dir(tmp_path):
    """Create a temporary storage directory for testing."""
    storage_path = tmp_path / "storage"
    storage_path.mkdir()
    return storage_path
