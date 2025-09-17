from app.extensions import db
from app.models.recipeingredient import RecipeIngredient
from app.models.ingredient import Ingredient

class Recipe(db.Model):
    slug = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Add other existing fields here...
    directions = db.Column(db.Text)

    # Full ingredient relationship
    recipe_ingredients = db.relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    # Convenient list of ingredients
    ingredients = db.relationship(
        "Ingredient",
        secondary="recipe_ingredient",  # Use the actual table name
        viewonly=True,
        backref=db.backref("recipes", viewonly=True)
    )
