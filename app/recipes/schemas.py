from pydantic import BaseModel, Field, PositiveInt

from app.recipes.models import Ingredient, Recipe  # , RecipeIngredient


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
    sidebar: str | None = None

    def to_db(self):
        recipe = Recipe(**self.model_dump(mode="python", exclude={'recipe_ingredients'}, exclude_unset=True))
        for i in self.recipe_ingredients:
            if not (ingredient := Ingredient.query.get(i.ingredient.slug)):
                # TOOD: handle
                ingredient = Ingredient(**i.ingredient.model_dump(mode="python", exclude_unset=True))


class RecipeOut(BaseModel):
    slug: str
    recipe_ingredients: list[RecipeIngredientSchema]
    directions: str
    name: str
    sidebar: str | None = None

    class Config:  # deprecated
        orm_mode = True  # deprecated maybe
