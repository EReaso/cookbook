from app.recipes.schemas import CreateRecipe


def _stub_recipe_submit(page):
    def handler(route, request):
        if request.method == "POST":
            route.fulfill(status=200, content_type="text/plain", body="ok")
            return
        route.continue_()

    page.route("**/recipes/new*", handler)


def test_new_recipe_submit_posts_expected_json_shape(page, e2e_live_server):
    _stub_recipe_submit(page)
    page.goto(e2e_live_server.url("/recipes/new/"))

    page.fill("#title", "Best Pancakes")
    page.fill("#cook_time", "15")
    page.fill("#prep_time", "5")
    page.fill("#cook_temp", "375")
    page.fill("#servings", "4")

    row = page.locator("#ingredients li.ingredient-row:not(.d-none)").first
    row.locator('input[name="amount"]').fill("1.5")
    row.locator('input[name="unit"]').fill("cup")
    row.locator('input[name="name"]').fill("All Purpose Flour")

    page.once("dialog", lambda dialog: dialog.dismiss())
    with page.expect_request(
        lambda req: req.method == "POST" and req.url.rstrip("/").endswith("recipes/new")
    ) as request_info:
        page.click("#submit")

    payload = request_info.value.post_data_json

    assert set(payload) >= {
        "name",
        "slug",
        "cook_time",
        "prep_time",
        "cook_temp",
        "servings",
        "directions",
        "recipe_ingredients",
    }

    assert payload["name"] == "Best Pancakes"
    assert payload["slug"] == "best_pancakes"
    assert payload["cook_time"] == "15"
    assert payload["prep_time"] == "5"
    assert payload["cook_temp"] == "375"
    assert payload["servings"] == "4"
    assert payload["directions"] == ""

    assert payload["recipe_ingredients"] == [
        {
            "amount": "1.5",
            "unit": "cup",
            "name": "All Purpose Flour",
            "slug": "all_purpose_flour",
        }
    ]

    assert CreateRecipe.model_validate(payload)


def test_new_recipe_submit_filters_blank_ingredient_rows(page, e2e_live_server):
    _stub_recipe_submit(page)
    page.goto(e2e_live_server.url("/recipes/new/"))

    page.fill("#title", "Tomato Soup")

    page.click("#create-ingredient-button")
    visible_rows = page.locator("#ingredients li.ingredient-row:not(.d-none)")

    visible_rows.nth(0).locator('input[name="name"]').fill("Tomato")
    visible_rows.nth(1).locator('input[name="name"]').fill("")

    page.once("dialog", lambda dialog: dialog.dismiss())
    with page.expect_request(
        lambda req: req.method == "POST" and req.url.rstrip("/").endswith("recipes/new")
    ) as request_info:
        page.click("#submit")

    payload = request_info.value.post_data_json

    assert payload["name"] == "Tomato Soup"
    assert payload["slug"] == "tomato_soup"
    assert payload["recipe_ingredients"] == [
        {
            "amount": "",
            "unit": "",
            "name": "Tomato",
            "slug": "tomato",
        }
    ]

    parsed = CreateRecipe.model_validate(payload)
    assert parsed.recipe_ingredients[0].amount is None
    assert parsed.recipe_ingredients[0].unit is None


def test_new_recipe_slug_generation_from_name(page, e2e_live_server):
    _stub_recipe_submit(page)
    page.goto(e2e_live_server.url("/recipes/new/"))

    page.fill("#title", "Great Grandma's Famous Apple Pie!")
    page.once("dialog", lambda dialog: dialog.dismiss())
    with page.expect_request(
        lambda req: req.method == "POST" and req.url.rstrip("/").endswith("recipes/new")
    ) as request_info:
        page.click("#submit")

    payload = request_info.value.post_data_json

    assert payload["name"] == "Great Grandma's Famous Apple Pie!"
    assert payload["slug"] == "great_grandma_s_famous_apple_pie_"
