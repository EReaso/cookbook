#!/usr/bin/env bash
# Pre-commit hook: generate screenshots and stage them.
set -e

python scripts/take_screenshots.py
git add screenshots/
