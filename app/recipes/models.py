from app.extensions import db


class Recipe(db.Model):
    slug = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # TODO: Add Users
    directions = db.Column(db.Text)

    sidebar = db.Column(db.Text)

    ingredients = db.Column(db.Text)

    recipe_ingredients = db.relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    @property
    def parsed_directions(self):
        return

class Ingredient(db.Model):
    slug = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    recipes = db.relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

    # recipe_ingredients_association = db.relationship("Recipe", back_populates="ingredients")



class RecipeIngredient(db.Model):
    list = db.Column(db.String(100), primary_key=True)

    amount = db.Column(db.String(50))
    unit = db.Column(db.String(20))

    recipe_slug = db.Column(db.String(100), db.ForeignKey('recipe.slug'), primary_key=True)
    ingredient_slug = db.Column(db.String(50), db.ForeignKey('ingredient.slug'), primary_key=True)

    recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes')

    @property
    def pretty(self):
        if self.unit:
            output =  self.amount, self.unit, self.ingredient.name
        elif self.amount:
            output = self.amount, self.ingredient.name
        else:
            output = [self.ingredient.name]

        return " ".join(output)
