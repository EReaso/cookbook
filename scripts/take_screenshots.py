#!/usr/bin/env python3
"""Take automated screenshots of frontend pages using Playwright.

Reads page configuration from ``screenshots.yml`` and captures a screenshot
for every page not marked as ``exempt``.  Captures are saved to the directory
specified by ``--output-dir`` (default: ``screenshots/``).

Usage::

    python scripts/take_screenshots.py
    python scripts/take_screenshots.py --config screenshots.yml --output-dir screenshots
    python scripts/take_screenshots.py --base-url http://localhost:5000
"""

import argparse
import sys
import tempfile
import threading
import time
from pathlib import Path

import yaml


def _path_to_filename(path: str) -> str:
    """Derive a screenshot filename from a URL path.

    Examples::

        /recipes/      -> recipes
        /recipes/new/  -> recipes_new
        /book/test/    -> book_test
        /              -> index
    """
    parts = [p for p in path.strip("/").split("/") if p]
    return "_".join(parts) if parts else "index"


def _load_config(config_path: Path) -> list[dict]:
    """Load and return the list of page configs from the YAML file."""
    with config_path.open() as fh:
        data = yaml.safe_load(fh)
    return data.get("pages", []) if data else []


def _seed_test_data(db) -> None:
    """Populate the test database with sample recipes and ingredients.

    Must be called from within an active Flask application context.
    """
    from app.recipes.models import Ingredient, Recipe, RecipeIngredient

    flour = Ingredient(slug="all_purpose_flour", name="All Purpose Flour", density=0.53)
    eggs = Ingredient(slug="eggs", name="Eggs", density=None)
    milk = Ingredient(slug="milk", name="Milk", density=1.03)
    butter = Ingredient(slug="butter", name="Butter", density=0.91)
    sugar = Ingredient(slug="sugar", name="Sugar", density=0.85)
    tomatoes = Ingredient(slug="tomatoes", name="Tomatoes", density=None)
    db.session.add_all([flour, eggs, milk, butter, sugar, tomatoes])

    pancakes = Recipe(
        slug="classic_pancakes",
        name="Classic Pancakes",
        prep_time=5,
        cook_time=15,
        servings=4,
        directions="1. Mix dry ingredients.\n2. Whisk in wet ingredients.\n3. Cook on griddle.",
    )
    db.session.add(pancakes)
    db.session.flush()

    db.session.add_all(
        [
            RecipeIngredient(ingredient_list="main", amount=1.5, unit="cup", recipe=pancakes, ingredient=flour),
            RecipeIngredient(ingredient_list="main", amount=2.0, unit=None, recipe=pancakes, ingredient=eggs),
            RecipeIngredient(ingredient_list="main", amount=1.0, unit="cup", recipe=pancakes, ingredient=milk),
            RecipeIngredient(ingredient_list="main", amount=2.0, unit="tbsp", recipe=pancakes, ingredient=butter),
        ]
    )

    soup = Recipe(
        slug="tomato_soup",
        name="Tomato Soup",
        prep_time=10,
        cook_time=30,
        servings=2,
        directions="1. Sauté tomatoes.\n2. Blend smooth.\n3. Season to taste.",
    )
    db.session.add(soup)
    db.session.flush()

    db.session.add(RecipeIngredient(ingredient_list="main", amount=6.0, unit=None, recipe=soup, ingredient=tomatoes))

    cake = Recipe(
        slug="simple_cake",
        name="Simple Cake",
        prep_time=20,
        cook_time=35,
        cook_temp=350,
        servings=8,
        directions="1. Cream butter and sugar.\n2. Add eggs and flour.\n3. Bake until done.",
    )
    db.session.add(cake)
    db.session.flush()

    db.session.add_all(
        [
            RecipeIngredient(ingredient_list="main", amount=2.0, unit="cup", recipe=cake, ingredient=flour),
            RecipeIngredient(ingredient_list="main", amount=1.0, unit="cup", recipe=cake, ingredient=sugar),
            RecipeIngredient(ingredient_list="main", amount=0.5, unit="cup", recipe=cake, ingredient=butter),
            RecipeIngredient(ingredient_list="main", amount=3.0, unit=None, recipe=cake, ingredient=eggs),
        ]
    )

    db.session.commit()


def _start_test_server(host: str = "127.0.0.1", port: int = 5001) -> tuple:
    """Create a Flask test app and start a Werkzeug server in a background thread.

    Returns ``(server, base_url)``.
    """
    from werkzeug.serving import make_server

    # Ensure the repository root is importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from app import app as flask_app
    from app.extensions import db, storage

    storage_dir = tempfile.mkdtemp()
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
        }
    )
    storage.init_app(flask_app, dir=storage_dir)

    # Dispose any previously created engine so the updated URI takes effect,
    # then create tables and seed sample data in a single app context to ensure
    # all operations share the same in-memory SQLite connection.
    with flask_app.app_context():
        db.engine.dispose()
        db.drop_all()
        db.create_all()
        _seed_test_data(db)

    server = make_server(host, port, flask_app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Give the server a moment to start accepting connections
    time.sleep(0.5)
    return server, f"http://{host}:{port}"


def take_screenshots(
    config_path: Path,
    output_dir: Path,
    base_url: str | None = None,
) -> None:
    """Read config and take screenshots for all non-exempt pages."""
    from playwright.sync_api import sync_playwright

    pages = _load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    server = None
    if base_url is None:
        server, base_url = _start_test_server()

    exempted = [p for p in pages if p.get("exempt", False)]
    to_capture = [p for p in pages if not p.get("exempt", False)]

    if exempted:
        print(f"Skipping {len(exempted)} exempt page(s): {[p['path'] for p in exempted]}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 720})

        for entry in to_capture:
            path = entry["path"]
            filename = entry.get("filename") or _path_to_filename(path)
            url = base_url.rstrip("/") + "/" + path.lstrip("/")
            pg = context.new_page()
            try:
                pg.goto(url, wait_until="networkidle")
                screenshot_path = output_dir / f"{filename}.png"
                pg.screenshot(path=str(screenshot_path), full_page=True)
                print(f"  Captured: {path!r} -> {screenshot_path}")
            finally:
                pg.close()

        browser.close()

    if server is not None:
        server.shutdown()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=repo_root / "screenshots.yml",
        help="Path to the screenshots YAML config (default: screenshots.yml)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "screenshots",
        help="Directory to save screenshots (default: screenshots/)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL of a running server (default: starts an in-process test server)",
    )
    args = parser.parse_args()

    print(f"Reading config: {args.config}")
    print(f"Output directory: {args.output_dir}")
    take_screenshots(args.config, args.output_dir, args.base_url)
    print("Done.")


if __name__ == "__main__":
    main()
