import re

from app.recipes.models import Ingredient, Recipe, RecipeIngredient
from pydantic import BaseModel, ConfigDict, Field, PositiveFloat, field_validator
from sqlalchemy.orm.scoping import scoped_session as Session


class IngredientSchema(BaseModel):
    slug: str = Field(max_length=50)
    name: str = Field(max_length=50)


class RecipeIngredientSchema(BaseModel):
    amount: PositiveFloat | None = None
    unit: str | None = Field(max_length=20, default=None)
    ingredient_list: str = Field(max_length=100, default="Ingredients")
    slug: str = Field(max_length=50)
    name: str = Field(max_length=50)

    @field_validator("amount", "unit", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


class CreateRecipe(BaseModel):
    slug: str | None = Field(default=None, max_length=100)

    name: str = Field(min_length=1, max_length=100)

    cook_time: float | None = None
    prep_time: float | None = None

    cook_temp: float | None = None

    servings: int | None = None

    directions: str

    sidebar: str | None = None

    recipe_ingredients: list[RecipeIngredientSchema]

    images: list[str] | None = None

    @field_validator("images", mode="after")
    @classmethod
    def empty_list_to_none(cls, value):
        if isinstance(value, list) and len(value) == 0:
            return None

    @field_validator("slug", "cook_time", "prep_time", "cook_temp", "servings", "sidebar", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    def to_db(self, session: Session) -> Recipe:
        recipe = Recipe(**self.model_dump(mode="python", exclude={"recipe_ingredients"}, exclude_unset=True))
        slug = re.sub(r"_+", "_", re.sub(r"[^_a-z0-9]+", "_", (recipe.slug or recipe.name).lower())).strip("_")
        if not slug:
            raise ValueError("Recipe name must produce a non-empty slug")
        recipe.slug = slug

        for i in self.recipe_ingredients:
            if (ingredient := session.get(Ingredient, i.slug)) is None:
                ingredient = Ingredient(**i.model_dump(mode="python", exclude_unset=True, include={"slug", "name"}))
                session.add(ingredient)

            recipe_ingredient = RecipeIngredient(
                amount=i.amount, unit=i.unit, ingredient_list=i.ingredient_list, ingredient=ingredient
            )
            recipe.recipe_ingredients.append(recipe_ingredient)
            session.add(recipe_ingredient)

        session.add(recipe)
        # Flush to assign relationship FKs and surface DB errors before commit.
        session.flush()
        return recipe


class RecipeOut(BaseModel):
    slug: str
    recipe_ingredients: list[RecipeIngredientSchema]
    directions: str
    name: str
    sidebar: str | None = None

    model_config = ConfigDict(from_attributes=True)
