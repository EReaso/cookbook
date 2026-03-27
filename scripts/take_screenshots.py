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
    with flask_app.app_context():
        db.create_all()

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
