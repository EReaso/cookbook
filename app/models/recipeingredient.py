from app.extensions import db

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'

    recipe_slug = db.Column(db.String(100), db.ForeignKey('recipe.slug'), primary_key=True)
    ingredient_slug = db.Column(db.String(100), db.ForeignKey('ingredient.slug'), primary_key=True)
    list = db.Column(db.String(100), primary_key=True)

    amount = db.Column(db.String(50))
    unit = db.Column(db.String(20))

    recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes_link')
