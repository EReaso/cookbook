from uuid import uuid4

from app.recipes.models import Recipe


def _random_slug() -> str:
    return f"test_slug_{uuid4().hex[:8]}"


class TestRecipeCreation:
    def test_create_recipe(self, client, db):
        payload = {
            "name": "Test Recipe",
            "slug": _random_slug(),
            "directions": "Test directions",
            "recipe_ingredients": [
                {
                    "amount": 1,
                    "unit": "cup",
                    "slug": "flour",
                    "name": "Flour",
                },
                {
                    "amount": 1,
                    "slug": "egg",
                    "name": "Egg",
                },
                {"slug": "salt", "name": "Salt"},
            ],
        }

        response = client.post("/recipes/new/", json=payload)
        assert response.status_code == 201
        assert len(db.session.get(Recipe, payload["slug"]).recipe_ingredients) == 3

    def test_create_recipe_invalid_payload(self, client):
        payload = {
            "name": "Test Recipe",
            # Missing directions and recipe_ingredients
        }

        response = client.post("/recipes/new/", json=payload)
        assert response.status_code == 400

    def test_create_recipe_empty_optional_fields_parse_as_null(self, client, db):
        payload = {
            "name": "Nullables Recipe",
            "slug": _random_slug(),
            "cook_time": "",
            "prep_time": "",
            "cook_temp": "",
            "servings": "",
            "sidebar": "",
            "directions": "Test directions",
            "recipe_ingredients": [
                {
                    "amount": "",
                    "unit": "",
                    "slug": "oil",
                    "name": "Oil",
                }
            ],
        }

        response = client.post("/recipes/new/", json=payload)
        assert response.status_code == 201

        recipe = db.session.get(Recipe, payload["slug"])
        assert recipe is not None
        assert recipe.cook_time is None
        assert recipe.prep_time is None
        assert recipe.cook_temp is None
        assert recipe.servings is None
        assert recipe.sidebar is None
        assert len(recipe.recipe_ingredients) == 1
        assert recipe.recipe_ingredients[0].amount is None
        assert recipe.recipe_ingredients[0].unit is None

    def test_duplicate_recipe_slugs_are_rejected(self, client):
        payload = {
            "name": _random_slug(),
            "slug": _random_slug(),
            "directions": "Test directions",
            "recipe_ingredients": [
                {
                    "amount": 1,
                    "slug": "flour",
                    "name": "Flour",
                }
            ],
        }

        first = client.post("/recipes/new/", json=payload)
        assert first.status_code == 201
        second = client.post("/recipes/new/", json=payload)
        assert second.status_code == 400
