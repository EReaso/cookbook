from flask import abort, render_template, request

from . import bp
from .models import Recipe


@bp.get("/")
def get_recipes():
    # page = request.args.get("page", 1, type=int)
    # per_page = request.args.get("per_page", 10, type=int)
    # pagination = Recipe.query.paginate(page=page, per_page=per_page, error_out=False)
    # recipes = pagination.items
    return abort(405)
    # return render_template("recipes.html", recipes=recipes, pagination=pagination)


@bp.post("/")
def post_recipe():
    return abort(405)


@bp.get("/<slug>/")
def get_recipe(slug):
    return abort(405)
    # recipe = Recipe.query.filter_by(slug=slug).first_or_404()
    # return render_template("recipe.html", recipe=recipe)
