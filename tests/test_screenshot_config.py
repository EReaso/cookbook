"""Tests for screenshot configuration parsing and filename utilities."""

import sys
import textwrap
from pathlib import Path

# Make the scripts/ directory importable without requiring __init__.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from take_screenshots import _load_config, _path_to_filename, _seed_from_config


class TestPathToFilename:
    def test_simple_path(self):
        assert _path_to_filename("/recipes/") == "recipes"

    def test_nested_path(self):
        assert _path_to_filename("/recipes/new/") == "recipes_new"

    def test_deep_path(self):
        assert _path_to_filename("/book/my-recipe/") == "book_my-recipe"

    def test_root_path(self):
        assert _path_to_filename("/") == "index"

    def test_no_trailing_slash(self):
        assert _path_to_filename("/recipes") == "recipes"

    def test_no_leading_slash(self):
        assert _path_to_filename("recipes/") == "recipes"


class TestLoadConfig:
    def test_loads_pages(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                    filename: recipes
                  - path: /recipes/new/
                    filename: new_recipe
                    exempt: true
                """
            )
        )
        config = _load_config(config_file)
        pages = config["pages"]
        assert len(pages) == 2
        assert pages[0]["path"] == "/recipes/"
        assert pages[0]["filename"] == "recipes"
        assert pages[0].get("exempt", False) is False
        assert pages[1]["path"] == "/recipes/new/"
        assert pages[1]["exempt"] is True

    def test_empty_pages_list(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("pages: []\n")
        assert _load_config(config_file)["pages"] == []

    def test_missing_pages_key(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("{}\n")
        assert _load_config(config_file)["pages"] == []

    def test_empty_file(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("")
        assert _load_config(config_file)["pages"] == []

    def test_filename_optional(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                """
            )
        )
        pages = _load_config(config_file)["pages"]
        assert pages[0].get("filename") is None

    def test_exempt_defaults_to_false(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                    filename: recipes
                """
            )
        )
        pages = _load_config(config_file)["pages"]
        assert pages[0].get("exempt", False) is False

    def test_seed_data_returned(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages: []
                seed_data:
                  ingredients:
                    - slug: flour
                      name: Flour
                  recipes: []
                """
            )
        )
        config = _load_config(config_file)
        assert config["seed_data"]["ingredients"][0]["slug"] == "flour"
        assert config["seed_data"]["recipes"] == []

    def test_seed_data_defaults_to_empty_dict(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("pages: []\n")
        assert _load_config(config_file)["seed_data"] == {}

    def test_real_config_file_is_valid(self):
        """The screenshots.yml in the repo root must be parseable and well-formed."""
        repo_root = Path(__file__).resolve().parents[1]
        config_file = repo_root / "screenshots.yml"
        config = _load_config(config_file)
        pages = config["pages"]
        assert isinstance(pages, list)
        for entry in pages:
            assert "path" in entry, "Each page entry must have a 'path' key"
            assert entry["path"].startswith("/"), "Page paths must start with '/'"

    def test_real_config_seed_data_is_valid(self):
        """The screenshots.yml seed_data must be well-formed."""
        repo_root = Path(__file__).resolve().parents[1]
        config_file = repo_root / "screenshots.yml"
        seed_data = _load_config(config_file)["seed_data"]
        for ing in seed_data.get("ingredients", []):
            assert "slug" in ing
            assert "name" in ing
        for recipe in seed_data.get("recipes", []):
            assert "slug" in recipe
            assert "name" in recipe
            for ri in recipe.get("recipe_ingredients", []):
                assert "ingredient_slug" in ri
                assert "ingredient_list" in ri


class TestSeedFromConfig:
    def test_seeds_ingredients(self, app, db):
        from app.recipes.models import Ingredient

        seed_data = {
            "ingredients": [
                {"slug": "flour", "name": "Flour", "density": 0.53},
                {"slug": "sugar", "name": "Sugar"},
            ]
        }
        _seed_from_config(db, seed_data)

        assert db.session.get(Ingredient, "flour").name == "Flour"
        assert db.session.get(Ingredient, "flour").density == 0.53
        assert db.session.get(Ingredient, "sugar").density is None

    def test_seeds_recipes_with_ingredients(self, app, db):
        from app.recipes.models import Recipe, RecipeIngredient

        seed_data = {
            "ingredients": [{"slug": "eggs", "name": "Eggs"}],
            "recipes": [
                {
                    "slug": "omelette",
                    "name": "Omelette",
                    "servings": 1,
                    "directions": "Beat and cook.",
                    "recipe_ingredients": [{"ingredient_list": "main", "amount": 2.0, "ingredient_slug": "eggs"}],
                }
            ],
        }
        _seed_from_config(db, seed_data)

        recipe = db.session.get(Recipe, "omelette")
        assert recipe is not None
        assert recipe.name == "Omelette"
        assert recipe.servings == 1
        ri = db.session.get(RecipeIngredient, ("main", "omelette", "eggs"))
        assert ri is not None
        assert ri.amount == 2.0

    def test_empty_seed_data_is_noop(self, app, db):
        from app.recipes.models import Ingredient, Recipe

        _seed_from_config(db, {})

        assert db.session.query(Recipe).count() == 0
        assert db.session.query(Ingredient).count() == 0
