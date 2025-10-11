# from app.extensions import db
# from app.models.recipeingredient import RecipeIngredient
# from app.models.ingredient import Ingredient
#
# class Recipe(db.Model):
#     slug = db.Column(db.String(100), primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     # Add other existing fields here...
#     directions = db.Column(db.Text)
#
#     # Full ingredient relationship
#     recipe_ingredients = db.relationship(
#         "RecipeIngredient",
#         back_populates="recipe",
#         cascade="all, delete-orphan"
#     )
#
#     # Convenient list of ingredients (view-only via association table)
#     ingredients = db.relationship(
#         "Ingredient",
#         secondary="recipe_ingredient",
#         viewonly=True,
#         lazy="dynamic",
#         back_populates="recipes_view"
#     )
