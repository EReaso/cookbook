# from .schemas import IngredientSchema

# @bp.get("/datalist-options/")
# def datalist_options():
#     query = request.args.get("q", "").strip()
#     if not query:
#         return []
#     results = (
#         db.session.execute(
#             db.select(Ingredient).where(
#                 or_(
#                     Ingredient.slug.icontains(query, autoescape=True), Ingredient.name.icontains(query, autoescape=True)
#                 )
#             )
#         )
#         .scalars()
#         .all()
#     )
#     return [IngredientSchema.model_validate(i, from_attributes=True).model_dump() for i in results]
