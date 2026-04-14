from app.recipes.models import Recipe


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
