from flask import abort, redirect, render_template, request

from . import bp
from .models import Recipe
from .schemas import CreateRecipe


@bp.get("/")
def get_recipes():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    pagination = Recipe.query.paginate(page=page, per_page=per_page, error_out=False)
    recipes = pagination.items
    return render_template("recipes.html", recipes=recipes, pagination=pagination)


@bp.get("/new/")
def new_recipe():
    return render_template("new_recipe.html")


@bp.post("/new/")
def post_recipe():
    try:
        data = CreateRecipe().model_validate_json(request.get_json())
    except ValidationError:
        return abort(400, "Invalid input")

    recipe = data.to_db()

    return redirect(url_for("recipes.get_recipe", slug=recipe.slug))


@bp.get("/get/<slug>/")
def get_recipe(slug):
    return abort(405)
    # recipe = Recipe.query.filter_by(slug=slug).first_or_404()
    # return render_template("recipe.html", recipe=recipe)
