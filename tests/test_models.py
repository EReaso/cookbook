"""Tests for Recipe models."""

from app.recipes.models import Ingredient, Recipe, RecipeIngredient


class TestRecipe:
    """Test suite for Recipe model."""

    def test_create_recipe(self, db):
        """Test creating a recipe."""
        recipe = Recipe(
            slug="chocolate-cake",
            name="Chocolate Cake",
            directions="Mix and bake",
            ingredients="flour, sugar, cocoa",
        )
        db.session.add(recipe)
        db.session.commit()

        assert recipe.slug == "chocolate-cake"
        assert recipe.name == "Chocolate Cake"
        assert recipe.directions == "Mix and bake"

    def test_recipe_image_paths_with_images(self, db):
        """Test image_urls property with images."""
        recipe = Recipe(
            slug="test-recipe",
            name="Test",
            images='["image1.jpg","image2.jpg"]',
        )
        db.session.add(recipe)
        db.session.commit()

        urls = list(recipe.image_paths)
        assert "/images/image1.jpg" in urls
        assert "/images/image2.jpg" in urls

    def test_recipe_image_paths_without_images(self, db):
        """Test image_urls property without images."""
        recipe = Recipe(slug="test-recipe", name="Test")
        db.session.add(recipe)
        db.session.commit()

        urls = list(recipe.image_paths)
        assert urls == []

    def test_parsed_directions_placeholder(self, db):
        recipe = Recipe(slug="directions-recipe", name="Directions", directions="Step 1")
        db.session.add(recipe)
        db.session.commit()
        assert recipe.parsed_directions == "not implemented yet"


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


class TestRecipeIngredient:
    """Test suite for RecipeIngredient model."""

    def test_create_recipe_ingredient(self, db, sample_recipe, sample_ingredient):
        """Test creating a recipe-ingredient relationship."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=2.5,
            unit="cups",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        assert recipe_ingredient.amount == 2.5
        assert recipe_ingredient.unit == "cups"
        assert recipe_ingredient.recipe == sample_recipe
        assert recipe_ingredient.ingredient == sample_ingredient

    def test_pretty_whole_number(self, db, sample_recipe, sample_ingredient):
        """Test pretty property with whole number."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=2.0,
            unit="cups",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        pretty = recipe_ingredient.pretty
        assert "2" in pretty
        assert "cups" in pretty
        assert sample_ingredient.name in pretty

    def test_pretty_fraction(self, db, sample_recipe, sample_ingredient):
        """Test pretty property with fraction."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=0.5,
            unit="cups",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        pretty = recipe_ingredient.pretty
        assert "1/2" in pretty or "0.5" in pretty
        assert "cups" in pretty

    def test_pretty_mixed_number(self, db, sample_recipe, sample_ingredient):
        """Test pretty property with mixed number."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=2.5,
            unit="cups",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        pretty = recipe_ingredient.pretty
        assert "cups" in pretty
        assert sample_ingredient.name in pretty

    def test_pretty_without_unit(self, db, sample_recipe, sample_ingredient):
        """Test pretty property without unit."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=3.0,
            unit=None,
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        pretty = recipe_ingredient.pretty
        assert "3" in pretty
        assert sample_ingredient.name in pretty

    def test_pretty_without_amount(self, db, sample_recipe, sample_ingredient):
        """Test pretty property without amount."""
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=None,
            unit=None,
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        pretty = recipe_ingredient.pretty
        assert sample_ingredient.name in pretty

    def test_weight_with_density(self, db, sample_recipe):
        """Test weight calculation with density."""
        ingredient = Ingredient(
            slug="water",
            name="Water",
            density=1.0,  # 1 g/ml
        )
        db.session.add(ingredient)
        db.session.commit()

        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=250.0,
            unit="ml",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        weight = recipe_ingredient.weight
        assert weight is not None
        assert weight == 250.0

    def test_weight_without_density(self, db, sample_recipe, sample_ingredient):
        """Test weight returns None when ingredient has no density."""
        sample_ingredient.density = None
        db.session.commit()

        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=2.0,
            unit="cups",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        assert recipe_ingredient.weight is None

    def test_pretty_uses_cached_value(self, db, sample_recipe, sample_ingredient):
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=1.0,
            unit="cup",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        recipe_ingredient._pretty = "cached value"
        assert recipe_ingredient.pretty == "cached value"

    def test_weight_uses_cached_value(self, db, sample_recipe, sample_ingredient):
        recipe_ingredient = RecipeIngredient(
            ingredient_list="main",
            amount=1.0,
            unit="cup",
            recipe_slug=sample_recipe.slug,
            ingredient_slug=sample_ingredient.slug,
        )
        recipe_ingredient._weight = 42
        assert recipe_ingredient.weight == 42
