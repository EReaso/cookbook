from flask import render_template, abort, flash, redirect, url_for
from app.extensions import db

from .models import *
from . import bp


@bp.get("/recipes/")
def get_recipes():
    recipes = Recipe.query.all()
    return render_template("recipes.html", recipes=recipes)

@bp.post("/recipes/")
def post_recipe():
    """
    {


    """
    pass



@bp.get("/recipe/<slug>/")
def get_recipe(slug):
    recipe = Recipe.query.filter_by(slug=slug).first_or_404()
    return render_template("recipe.html", recipe=recipe)
