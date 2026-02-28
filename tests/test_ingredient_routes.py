"""Tests for ingredient routes."""

import pytest

from app.recipes.models import Ingredient


class TestIngredientRoutes:
    """Test suite for ingredient routes."""

    @pytest.fixture(autouse=True)
    def setup_ingredients(self, db):
        """Setup test ingredients for all tests in this class."""
        self.flour = Ingredient(slug="all-purpose-flour", name="All-Purpose Flour", density=0.593)
        self.bread_flour = Ingredient(slug="bread-flour", name="Bread Flour", density=0.593)
        self.sugar = Ingredient(slug="sugar", name="Granulated Sugar", density=0.845)
        self.brown_sugar = Ingredient(slug="brown-sugar", name="Brown Sugar", density=0.721)
        self.vanilla = Ingredient(slug="vanilla", name="Vanilla Extract", density=0.879)
        self.salt = Ingredient(slug="salt", name="Table Salt", density=2.16)
        self.choc_chips = Ingredient(slug="choc-chips", name="Chocolate Chips", density=0.6)
        self.cocoa = Ingredient(slug="cocoa", name="Cocoa Powder", density=0.5)
        self.butter = Ingredient(slug="butter", name="Unsalted Butter", density=0.911)

        db.session.add_all(
            [
                self.flour,
                self.bread_flour,
                self.sugar,
                self.brown_sugar,
                self.vanilla,
                self.salt,
                self.choc_chips,
                self.cocoa,
                self.butter,
            ]
        )
        db.session.commit()

    def test_datalist_options_empty_query(self, client, db):
        """Test datalist options endpoint with no query parameter."""
        response = client.get("/ingredients/datalist-options/")
        assert response.status_code == 200
        # Should return empty list when no query or no matching results
        data = response.get_json()
        assert isinstance(data, list)

    def test_datalist_options_with_query(self, client, db):
        """Test datalist options endpoint with query parameter."""
        # Search by name
        response = client.get("/ingredients/datalist-options/?q=sugar")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2  # Should find both sugar and brown-sugar

        # Verify structure of returned data
        slugs = [item['slug'] for item in data]
        assert 'sugar' in slugs
        assert 'brown-sugar' in slugs

    def test_datalist_options_search_by_slug(self, client, db):
        """Test datalist options searching by slug."""
        response = client.get("/ingredients/datalist-options/?q=flour")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2  # all-purpose-flour and bread-flour

    def test_datalist_options_case_insensitive(self, client, db):
        """Test that search is case insensitive."""
        # Search with different case
        response = client.get("/ingredients/datalist-options/?q=VANILLA")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['slug'] == 'vanilla'

    def test_datalist_options_no_match(self, client, db):
        """Test datalist options with no matching ingredients."""
        response = client.get("/ingredients/datalist-options/?q=nonexistent")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 0

    def test_datalist_options_partial_match(self, client, db):
        """Test partial matching in search."""
        response = client.get("/ingredients/datalist-options/?q=choc")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['slug'] == 'choc-chips'

    def test_datalist_options_returns_correct_fields(self, client, db):
        """Test that datalist options returns the correct fields."""
        response = client.get("/ingredients/datalist-options/?q=butter")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1

        # Verify the structure matches the schema
        item = data[0]
        assert 'slug' in item
        assert 'name' in item
        assert item['slug'] == 'butter'
        assert item['name'] == 'Unsalted Butter'

    def test_datalist_options_multiple_results(self, client, db):
        """Test that multiple results are returned for broad search."""
        response = client.get("/ingredients/datalist-options/?q=flour")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2  # all-purpose-flour and bread-flour

    def test_datalist_options_search_by_name_partial(self, client, db):
        """Test searching by partial name match."""
        response = client.get("/ingredients/datalist-options/?q=Chocolate")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['slug'] == 'choc-chips'
