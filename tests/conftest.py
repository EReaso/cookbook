"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import pytest

from app import app as flask_app
from app.extensions import db as _db


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
    from app.recipes.models import Recipe

    recipe = Recipe(
        slug="test-recipe",
        name="Test Recipe",
        directions="1. Do this\n2. Do that",
        ingredients="2 cups flour\n1 cup sugar",
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe


@pytest.fixture
def sample_ingredient(db):
    """Create a sample ingredient for testing."""
    from app.recipes.models import Ingredient

    ingredient = Ingredient(
        slug="test-ingredient",
        name="Test Ingredient",
        density=1.0,
    )
    db.session.add(ingredient)
    db.session.commit()
    return ingredient


@pytest.fixture
def sample_recipe_ingredient(db, sample_recipe, sample_ingredient):
    """Create a sample recipe-ingredient relationship for testing."""
    from app.recipes.models import RecipeIngredient

    recipe_ingredient = RecipeIngredient(
        list="main",
        amount=2.0,
        unit="cups",
        recipe_slug=sample_recipe.slug,
        ingredient_slug=sample_ingredient.slug,
    )
    db.session.add(recipe_ingredient)
    db.session.commit()
    return recipe_ingredient


@pytest.fixture
def storage_dir(tmp_path):
    """Create a temporary storage directory for testing."""
    storage_path = tmp_path / "storage"
    storage_path.mkdir()
    return storage_path
