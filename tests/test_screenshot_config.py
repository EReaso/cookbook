from pathlib import Path

import pytest
from pydantic import ValidationError

from app.recipes.models import Ingredient, Recipe
from scripts.take_screenshots import ScreenshotConfig, ScreenshotPage, SeedData, load_config, seed_database


def test_capture_name_uses_explicit_filename():
    page = ScreenshotPage(path="/recipes/new/", filename="custom_name")
    assert page.capture_name() == "custom_name"


def test_capture_name_derives_from_path():
    page = ScreenshotPage(path="/recipes/new/")
    assert page.capture_name() == "recipes_new"


def test_capture_name_for_home_path():
    page = ScreenshotPage(path="/")
    assert page.capture_name() == "home"


def test_load_config_parses_yaml_file(tmp_path: Path):
    config_path = tmp_path / "screenshots.yml"
    config_path.write_text(
        "\n".join(
            [
                "pages:",
                "  - path: /recipes/",
                "    exempt: true",
                "seed_data:",
                "  ingredients:",
                "    - slug: flour",
                "      name: Flour",
                "  recipes:",
                "    - slug: biscuits",
                "      name: Biscuits",
                "      directions: mix and bake",
                "      recipe_ingredients:",
                "        - slug: flour",
                "          name: Flour",
                "",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert isinstance(config, ScreenshotConfig)
    assert config.pages[0].path == "/recipes/"
    assert config.pages[0].exempt is True
    assert config.seed_data.ingredients[0].slug == "flour"
    assert config.seed_data.recipes[0].slug == "biscuits"


def test_seed_data_rejects_non_schema_recipe_ingredient_shape():
    with pytest.raises(ValidationError):
        SeedData.model_validate(
            {
                "recipes": [
                    {
                        "name": "Bad Recipe",
                        "directions": "x",
                        "recipe_ingredients": [
                            {"ingredient_slug": "flour", "amount": 1.0},
                        ],
                    }
                ]
            }
        )


def test_seed_database_inserts_configured_records(db):
    seed = SeedData.model_validate(
        {
            "ingredients": [{"slug": "flour", "name": "Flour"}],
            "recipes": [
                {
                    "slug": "bread",
                    "name": "Bread",
                    "directions": "mix and bake",
                    "recipe_ingredients": [
                        {
                            "slug": "flour",
                            "name": "Flour",
                            "amount": 2.0,
                            "unit": "cup",
                        }
                    ],
                }
            ],
        }
    )

    seed_database(seed)

    flour = db.session.get(Ingredient, "flour")
    bread = db.session.get(Recipe, "bread")

    assert flour is not None
    assert bread is not None
    assert bread.name == "Bread"
    assert len(bread.recipe_ingredients) == 1
    assert bread.recipe_ingredients[0].ingredient_slug == "flour"
