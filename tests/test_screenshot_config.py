"""Tests for screenshot configuration parsing and filename utilities."""

import sys
import textwrap
from pathlib import Path

# Make the scripts/ directory importable without requiring __init__.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from take_screenshots import _load_config, _path_to_filename


class TestPathToFilename:
    def test_simple_path(self):
        assert _path_to_filename("/recipes/") == "recipes"

    def test_nested_path(self):
        assert _path_to_filename("/recipes/new/") == "recipes_new"

    def test_deep_path(self):
        assert _path_to_filename("/book/my-recipe/") == "book_my-recipe"

    def test_root_path(self):
        assert _path_to_filename("/") == "index"

    def test_no_trailing_slash(self):
        assert _path_to_filename("/recipes") == "recipes"

    def test_no_leading_slash(self):
        assert _path_to_filename("recipes/") == "recipes"


class TestLoadConfig:
    def test_loads_pages(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                    filename: recipes
                  - path: /recipes/new/
                    filename: new_recipe
                    exempt: true
                """
            )
        )
        pages = _load_config(config_file)
        assert len(pages) == 2
        assert pages[0]["path"] == "/recipes/"
        assert pages[0]["filename"] == "recipes"
        assert pages[0].get("exempt", False) is False
        assert pages[1]["path"] == "/recipes/new/"
        assert pages[1]["exempt"] is True

    def test_empty_pages_list(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("pages: []\n")
        assert _load_config(config_file) == []

    def test_missing_pages_key(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("{}\n")
        assert _load_config(config_file) == []

    def test_empty_file(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text("")
        assert _load_config(config_file) == []

    def test_filename_optional(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                """
            )
        )
        pages = _load_config(config_file)
        assert pages[0].get("filename") is None

    def test_exempt_defaults_to_false(self, tmp_path):
        config_file = tmp_path / "screenshots.yml"
        config_file.write_text(
            textwrap.dedent(
                """
                pages:
                  - path: /recipes/
                    filename: recipes
                """
            )
        )
        pages = _load_config(config_file)
        assert pages[0].get("exempt", False) is False

    def test_real_config_file_is_valid(self):
        """The screenshots.yml in the repo root must be parseable and well-formed."""
        repo_root = Path(__file__).resolve().parents[1]
        config_file = repo_root / "screenshots.yml"
        pages = _load_config(config_file)
        assert isinstance(pages, list)
        for entry in pages:
            assert "path" in entry, "Each page entry must have a 'path' key"
            assert entry["path"].startswith("/"), "Page paths must start with '/'"
