from sqlalchemy.orm import validates

from app.extensions import db


class Tag(db.Model):
    name = db.Column(db.String(100), unique=True, primary_key=True)

    recipes = db.relationship("Recipe", secondary="recipe_tag", back_populates="tags")
    ingredients = db.relationship("Ingredient", secondary="ingredient_tag", back_populates="tags")

    @validates("name")
    def uppercase_name(self, key, name):
        return name.lower()


class RecipeTag(db.Model):
    recipe_slug = db.Column(db.String(100), db.ForeignKey("recipe.slug"), primary_key=True)
    tag_name = db.Column(db.String(100), db.ForeignKey("tag.name"), primary_key=True)

    recipe = db.relationship("Recipe", backref="recipe_tags")
    tag = db.relationship("Tag", backref="recipe_tags")


class IngredientTag(db.Model):
    ingredient_slug = db.Column(db.String(50), db.ForeignKey("ingredient.slug"), primary_key=True)
    tag_name = db.Column(db.String(100), db.ForeignKey("tag.name"), primary_key=True)

    ingredient = db.relationship("Ingredient", backref="ingredient_tags")
    tag = db.relationship("Tag", backref="ingredient_tags")
