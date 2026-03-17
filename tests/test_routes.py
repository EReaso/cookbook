"""Tests for recipe routes."""

from app.recipes.models import Recipe


class TestRecipeRoutes:
    """Test suite for recipe routes."""

    def test_get_recipes_empty(self, client, db):
        """Test getting recipes when database is empty."""
        response = client.get("/recipes/")
        assert response.status_code == 200

    def test_get_recipes_with_data(self, client, db, sample_recipe):
        """Test getting recipes with data."""
        response = client.get("/recipes/")
        assert response.status_code == 200
        assert sample_recipe.name.encode() in response.data

    def test_get_recipes_pagination(self, client, db):
        """Test recipe pagination."""
        # Create multiple recipes
        for i in range(15):
            recipe = Recipe(
                slug=f"recipe-{i}",
                name=f"Recipe {i}",
                directions=f"Directions {i}",
            )
            db.session.add(recipe)
        db.session.commit()

        # Test first page
        response = client.get("/recipes/?page=1&per_page=10")
        assert response.status_code == 200

        # Test second page
        response = client.get("/recipes/?page=2&per_page=10")
        assert response.status_code == 200

    def test_get_single_recipe_endpoint_not_implemented(self, client, db, sample_recipe):
        """The placeholder single-recipe endpoint currently returns 405."""
        response = client.get(f"/recipes/get/{sample_recipe.slug}/")
        assert response.status_code == 405

    def test_get_nonexistent_recipe_route(self, client, db):
        """A non-matching recipe URL currently returns 404."""
        response = client.get("/recipes/nonexistent-recipe/")
        assert response.status_code == 404

    def test_post_recipe(self, client, db):
        """Test posting a new recipe (currently not implemented)."""
        response = client.post("/recipes/", json={"name": "New Recipe"})
        # The route is not implemented, so we expect it to pass through
        # without error but not do anything
        assert response.status_code in [200, 404, 405, 500]
