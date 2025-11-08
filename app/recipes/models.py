from fractions import Fraction
from pint import Quantity as Q_, UnitRegistry

from app.extensions import db

ureg = UnitRegistry()


class Recipe(db.Model):
	slug = db.Column(db.String(100), primary_key=True)

	name = db.Column(db.String(100), nullable=False)

	# TODO: Add Users
	directions = db.Column(db.Text)

	images = db.Column(db.Text, nullable=True)

	@property
	def image_urls(self):
		if self.images:
			for image in self.images.split(","):
				yield f"/images/{image}"
		else:
			yield None

	sidebar = db.Column(db.Text, nullable=True)

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

	density = db.Column(db.Float, nullable=True)  # Use density in g/ml


class RecipeIngredient(db.Model):
	list = db.Column(db.String(100), primary_key=True)

	amount = db.Column(db.Float)
	unit = db.Column(db.String(20))

	recipe_slug = db.Column(db.String(100), db.ForeignKey('recipe.slug'), primary_key=True)
	ingredient_slug = db.Column(db.String(50), db.ForeignKey('ingredient.slug'), primary_key=True)

	recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
	ingredient = db.relationship('Ingredient', back_populates='recipes')

	_pretty = None

	@property
	def pretty(self):
		if self._pretty:
			return self._pretty

		amount = self.amount

		# Handle fractions and mixed numbers
		if amount is not None and amount % 1 != 0:
			amount = Fraction(self.amount)
			if amount.numerator // amount.denominator >= 1:
				amount = f"{amount.numerator // amount.denominator} {amount.numerator % amount.denominator}/{amount.denominator}"
			else:
				amount = str(amount)
		else:
			amount = str(int(amount)) if amount else None
		# Handle whole items and non-measured ingredients
		if self.unit:
			output = amount, self.unit, self.ingredient.name
		elif amount:
			output = amount, self.ingredient.name
		else:
			output = [self.ingredient.name]

		r = " ".join(output)
		self._pretty = r
		return r

	_weight = None

	def amount_in_unit(self, unit: str):
		# TODO: see if there's a way to do
		return Q_(self.amount, self.unit).to(unit).magnitude

	@property
	def weight(self):
		if self._weight:
			return self._weight if self._weight != 0 else None
		elif self.ingredient.density is None:
			self._weight = 0
			return None
		else:
			weight = self.ingredient.density * self.amount_in_unit("ml")
			output = int(weight) + round(weight - int(weight), 2)
			return output if int(output) != output else int(output)
