from itertools import groupby

from flask import redirect, render_template, request, url_for

from app.book import bp
from app.extensions import db
from app.recipes.models import Ingredient, Recipe, RecipeIngredient


@bp.route("/book/")
def book_sample():
    return render_template("bookview.html")


@bp.route("/book/<recipe_slug>/")
def book(recipe_slug):
    recipe = Recipe.query.get_or_404(recipe_slug)
    ingredients = sorted(recipe.recipe_ingredients, key=lambda i: i.list)
    ingredient_lists = ((k, list(v)) for k, v in groupby(ingredients, lambda i: i.list))
    return render_template("bookview.html", **locals())
