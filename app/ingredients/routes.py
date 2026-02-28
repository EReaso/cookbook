from flask import request
from sqlalchemy import or_

from app.extensions import db

from ..recipes.models import Ingredient
from ..recipes.schemas import IngredientSchema
from . import bp


@bp.get("/datalist-options/")
def datalist_options():
    query = request.args.get("q", "")
    results = (
        db.session.execute(
            db.select(Ingredient).where(
                or_(
                    Ingredient.slug.icontains(query, autoescape=True), Ingredient.name.icontains(query, autoescape=True)
                )
            )
        )
        .scalars()
        .all()
    )
    return [IngredientSchema.model_validate(i.__dict__).model_dump() for i in results]
