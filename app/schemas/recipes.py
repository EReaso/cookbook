from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models.recipe import Recipe
from app.schemas.recipeingredient import RecipeIngredientSchema


class RecipeSchema(SQLAlchemyAutoSchema):
    """Schema for displaying basic recipe information (without ingredients)."""

    class Meta:
        model = Recipe
        load_instance = False
        dump_only = ("slug",)
        fields = ("slug", "name", "directions")


class RecipeDetailSchema(RecipeSchema):
    """Schema for displaying detailed recipe information (including ingredients)."""

    # Use a nested field that properly loads the RecipeIngredientSchema
    recipe_ingredients = fields.List(fields.Nested(RecipeIngredientSchema))

    class Meta:
        model = Recipe
        load_instance = False
        dump_only = ("slug",)
        fields = ("slug", "name", "directions", "recipe_ingredients")
