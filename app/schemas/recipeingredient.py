from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from app.models.recipeingredient import RecipeIngredient


class RecipeIngredientSchema(SQLAlchemyAutoSchema):
    """Schema for recipe ingredient relationships."""
    # Define ingredient fields explicitly with proper attribute paths
    amount = auto_field()
    unit = auto_field()
    ingredient_name = fields.String(attribute="ingredient.name")
    ingredient_slug = fields.String(attribute="ingredient.slug")

    class Meta:
        model = RecipeIngredient
        load_instance = True
        # Only include these specific fields
        fields = ("amount", "unit", "ingredient_name", "ingredient_slug")
