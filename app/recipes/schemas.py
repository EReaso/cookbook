import re

from app.extensions import db
from app.recipes.models import Ingredient, Recipe, RecipeIngredient
from pydantic import BaseModel, Field, PositiveInt


class IngredientSchema(BaseModel):
    slug: str = Field(max_length=50)
    name: str = Field(max_length=50)


class RecipeIngredientSchema(BaseModel):
    amount: PositiveInt | None = None
    unit: str | None = Field(max_length=20, default=None)
    list: str | None = Field(max_length=100, default=None)
    ingredient: IngredientSchema


class CreateRecipe(BaseModel):
    recipe_ingredients: list[RecipeIngredientSchema]
    directions: str
    name: str = Field(max_length=100)
    slug: str | None = Field(default=None, max_length=100, exclude=True)
    sidebar: str | None = None

    def to_db(self) -> Recipe:
        # TODO: sanitize input and handle errors
        recipe = Recipe(**self.model_dump(mode="python", exclude={'recipe_ingredients'}, exclude_unset=True))
        recipe.slug = re.sub(recipe.name.lower(), "[^_a-z0-9]/g", "_")

        for i in self.recipe_ingredients:
            if not (ingredient := Ingredient.query.get(i.ingredient.slug)):
                ingredient = Ingredient(**i.ingredient.model_dump(mode="python", exclude_unset=True))
                db.session.add(ingredient)
            recipe_ingredient = RecipeIngredient(
                amount=i.amount,
                unit=i.unit,
                list=i.list,
                ingredient=ingredient,
            )
            db.session.add(recipe_ingredient)
            recipe.recipe_ingredients.append(recipe_ingredient)

        db.session.add(recipe)
        db.session.commit()

        return recipe


class RecipeOut(BaseModel):
    slug: str
    recipe_ingredients: list[RecipeIngredientSchema]
    directions: str
    name: str
    sidebar: str | None = None

    class Config:  # deprecated
        orm_mode = True  # deprecated maybe
