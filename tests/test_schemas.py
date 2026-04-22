"""Tests for schemas."""

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.recipes.schemas import CreateRecipe, slugify
from app.tags.models import Tag


class TestCreateRecipeSchema:
    def test_to_db_rejects_empty_slug_after_slugify(self):
        with pytest.raises(ValidationError, match="non-empty slug"):
            CreateRecipe(
                name="!!!",
                directions="x",
                recipe_ingredients=[{"slug": "flour", "name": "Flour"}],  # type: ignore
            )

    def test_to_db_creates_recipe_tag_associations(self, db):
        data = CreateRecipe(
            name="Tagged recipe",
            directions="mix",
            tags=["Dinner", "Quick"],
            recipe_ingredients=[{"slug": "flour", "name": "Flour"}],
        )

        recipe = data.to_db(db.session)
        db.session.commit()

        assert sorted(tag.name for tag in recipe.tags) == ["Dinner", "Quick"]

    def test_to_db_reuses_existing_tag_rows(self, db):
        db.session.add(Tag(name="Dinner"))
        db.session.commit()

        data = CreateRecipe(
            name="Pasta",
            directions="mix",
            tags=["Dinner"],
            recipe_ingredients=[{"slug": "flour", "name": "Flour"}],  # type: ignore
        )

        data.to_db(db.session)
        db.session.commit()

        total_dinner_tags = db.session.execute(
            select(func.count()).select_from(Tag).where(Tag.name == "Dinner")
        ).scalar_one()
        assert total_dinner_tags == 1

    def test_to_db_allows_omitting_tags(self, db):
        data = CreateRecipe(
            name="No tags",
            directions="mix",
            recipe_ingredients=[{"slug": "flour", "name": "Flour"}],  # type: ignore
        )

        recipe = data.to_db(db.session)
        db.session.commit()

        assert recipe.tags == []

    def test_slug_generation_on_init(self):
        data = CreateRecipe(
            name="Boston Baked Beans: a classic!",
            directions="mix",
            recipe_ingredients=[],
        )
        assert data.slug == slugify(data.name)

    def test_slugify(self):
        assert slugify("Boston Baked Beans: a classic!") == "boston_baked_beans_a_classic"
