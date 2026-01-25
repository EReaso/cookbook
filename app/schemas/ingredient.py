from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models.ingredient import Ingredient
from app.schemas.recipeingredient import RecipeIngredientSchema


class IngredientSchema(SQLAlchemyAutoSchema):
    """Schema for displaying ingredient information."""

    # Include the relationship data from RecipeIngredient
    recipes_link = fields.Nested("RecipeIngredientSchema", many=True)

    class Meta:
        model = Ingredient
        load_instance = True
        # Only include specific fields
        fields = ("slug", "name", "recipes_link")
