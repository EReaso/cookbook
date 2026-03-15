from flask import abort, render_template, request, url_for
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db

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


@bp.route("/new/", methods=["GET", "POST"])
def new_recipe():
    if request.method == "GET":
        return render_template("new_recipe.html")

    try:
        json_data = request.get_json(silent=True)
        if json_data is None:
            return abort(400, "Invalid or missing JSON payload")

        data = CreateRecipe.model_validate(json_data)
        recipe = data.to_db(db.session)
        db.session.commit()
    except (ValidationError, ValueError):
        db.session.rollback()
        return abort(400)
    except IntegrityError:
        db.session.rollback()
        return abort(400)

    return {"slug": recipe.slug}, 201


@bp.get("/get/<slug>/")
def get_recipe(slug):
    return abort(405)
