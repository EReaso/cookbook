"""Capture screenshots for configured pages.

This script can run against an existing base URL, or boot an in-process Flask
server with a temporary SQLite database and optional seeded data.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from typing import Iterator

import yaml
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field
from werkzeug.serving import BaseWSGIServer, make_server

# Ensure repository root is on sys.path so `import app` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app
from app.extensions import db
from app.recipes.models import Ingredient
from app.recipes.schemas import CreateRecipe, IngredientSchema


class ScreenshotPage(BaseModel):
    path: str
    filename: str | None = None
    exempt: bool = False

    def capture_name(self) -> str:
        if self.filename:
            return self.filename
        slug = re.sub(r"[^a-z0-9]+", "_", self.path.strip("/").lower()).strip("_")
        return slug or "home"


class SeedData(BaseModel):
    ingredients: list[IngredientSchema] = Field(default_factory=list)
    recipes: list[CreateRecipe] = Field(default_factory=list)


class ScreenshotConfig(BaseModel):
    pages: list[ScreenshotPage] = Field(default_factory=list)
    seed_data: SeedData = Field(default_factory=SeedData)


def load_config(config_path: Path) -> ScreenshotConfig:
    with config_path.open("r", encoding="utf-8") as handle:
        raw_data = yaml.safe_load(handle) or {}
    return ScreenshotConfig.model_validate(raw_data)


def seed_database(seed_data: SeedData) -> None:
    for ingredient in seed_data.ingredients:
        if db.session.get(Ingredient, ingredient.slug) is None:
            db.session.add(Ingredient(**ingredient.model_dump(mode="python")))

    for recipe in seed_data.recipes:
        recipe.to_db(db.session)

    db.session.commit()


def _target_url(base_url: str, path: str) -> str:
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{base_url.rstrip('/')}{normalized}"


def take_screenshots(config: ScreenshotConfig, output_dir: Path, base_url: str) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    active_pages = [page for page in config.pages if not page.exempt]
    capture_count = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for target in active_pages:
            url = _target_url(base_url, target.path)
            page.goto(url, wait_until="networkidle")
            destination = output_dir / f"{target.capture_name()}.png"
            page.screenshot(path=str(destination), full_page=True)
            capture_count += 1
        browser.close()

    return capture_count


@contextmanager
def run_server(server_app, host: str = "127.0.0.1", port: int = 0) -> Iterator[str]:
    server: BaseWSGIServer = make_server(host, port, server_app)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture screenshots for cookbook pages.")
    parser.add_argument("--config", default="screenshots.yml", help="Path to screenshot configuration YAML")
    parser.add_argument("--output-dir", default="screenshots", help="Directory where PNG files are written")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Optional externally running app base URL. If omitted, starts an in-process server.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config))

    if args.base_url:
        count = take_screenshots(config=config, output_dir=Path(args.output_dir), base_url=args.base_url)
        print(f"Captured {count} screenshot(s) to {args.output_dir}")
        return 0

    with tempfile.TemporaryDirectory(prefix="cookbook-screenshots-") as tmpdir:
        app.config.update(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{Path(tmpdir) / 'screenshots.db'}",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        )
        with app.app_context():
            db.drop_all()
            db.create_all()
            seed_database(config.seed_data)

        with run_server(app) as base_url:
            count = take_screenshots(config=config, output_dir=Path(args.output_dir), base_url=base_url)

    print(f"Captured {count} screenshot(s) to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
