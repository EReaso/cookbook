"""Tests for recipe schemas."""

import pytest

from app.recipes.schemas import CreateRecipe


class TestCreateRecipeSchema:
    def test_to_db_rejects_empty_slug_after_slugify(self, db):
        data = CreateRecipe(
            name="!!!",
            directions="x",
            recipe_ingredients=[{"slug": "flour", "name": "Flour"}],
        )

        with pytest.raises(ValueError, match="non-empty slug"):
            data.to_db(db.session)
