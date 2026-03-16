"""Tests for book view routes."""

from app.recipes.models import Ingredient, RecipeIngredient


class TestBookRoutes:
    def test_book_view_renders_grouped_ingredients(self, client, db, sample_recipe):
        flour = Ingredient(slug="flour-book", name="Flour")
        salt = Ingredient(slug="salt-book", name="Salt")
        db.session.add_all([flour, salt])

        db.session.add(
            RecipeIngredient(
                ingredient_list="Dry",
                amount=1.0,
                unit="cup",
                recipe=sample_recipe,
                ingredient=flour,
            )
        )
        db.session.add(
            RecipeIngredient(
                ingredient_list="Seasoning",
                amount=0.5,
                unit="tsp",
                recipe=sample_recipe,
                ingredient=salt,
            )
        )
        db.session.commit()

        response = client.get(f"/book/{sample_recipe.slug}/")

        assert response.status_code == 200
        assert b"Dry" in response.data
        assert b"Seasoning" in response.data
        assert b"Flour" in response.data
        assert b"Salt" in response.data

    def test_book_view_missing_recipe_returns_404(self, client):
        response = client.get("/book/does-not-exist/")
        assert response.status_code == 404
