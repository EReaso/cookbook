import re

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.orm.scoping import scoped_session as Session

from app.recipes.models import Ingredient, Recipe, RecipeIngredient
from app.tags.models import RecipeTag, Tag


class ReStr(str):
    """Subclass of `str` that adds a method wrapping re.sub for better syntax"""

    def sub(self, pattern: str, repl: str, count: int = 0, flags: int | re.RegexFlag = 0) -> "ReStr":
        """Wrapper for `re.sub` with same parameters, with the string to search through omitted as `self`"""

        return ReStr(re.sub(pattern, repl, self, count, flags))


def slugify(text: str) -> str:
    slug = ReStr(text.lower()).sub(r"[^a-z0-9]+", "_").sub("^_+|_+$", "")
    return str(slug)


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

    tags: list[str] | None = None

    @field_validator("images", mode="after")
    @classmethod
    def empty_list_to_none(cls, value):
        if isinstance(value, list) and len(value) == 0:
            return None
        return value

    @field_validator("slug", "cook_time", "prep_time", "cook_temp", "servings", "sidebar", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def _set_slug_on_init(self):
        self.slug = slugify(self.slug or self.name)
        if not self.slug:
            raise ValueError("Recipe name must produce a non-empty slug")

        return self

    def to_db(self, session: Session) -> Recipe:
        if not self.slug:
            raise ValueError("Recipe name must produce a non-empty slug")

        recipe = Recipe(**self.model_dump(mode="python", exclude={"recipe_ingredients", "tags"}, exclude_unset=True))

        for i in self.tags or []:
            if not (tag := session.execute(select(Tag).where(Tag.name == i)).scalar_one_or_none()):
                tag = Tag(name=i)
                session.add(tag)
            session.add(RecipeTag(recipe=recipe, tag=tag))

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
