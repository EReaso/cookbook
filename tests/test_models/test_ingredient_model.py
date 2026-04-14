from app.recipes.models import Ingredient


class TestIngredient:
    """Test suite for Ingredient model."""

    def test_create_ingredient(self, db):
        """Test creating an ingredient."""
        ingredient = Ingredient(
            slug="flour",
            name="All-Purpose Flour",
            density=0.593,
        )
        db.session.add(ingredient)
        db.session.commit()

        assert ingredient.slug == "flour"
        assert ingredient.name == "All-Purpose Flour"
        assert ingredient.density == 0.593

    def test_ingredient_without_density(self, db):
        """Test creating an ingredient without density."""
        ingredient = Ingredient(slug="salt", name="Table Salt")
        db.session.add(ingredient)
        db.session.commit()

        assert ingredient.slug == "salt"
        assert ingredient.density is None
