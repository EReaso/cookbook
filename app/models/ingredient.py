from app.extensions import db


class Ingredient(db.Model):
    slug = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Association with RecipeIngredient
    recipes_link = db.relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

    # View-only convenience relationship to Recipes via association table
    recipes_view = db.relationship(
        "Recipe", secondary="recipe_ingredient", viewonly=True, lazy="dynamic", back_populates="ingredients"
    )
