#!/usr/bin/env bash
# Pre-commit hook: rebuild SCSS and stage the compiled CSS output.
set -e

pnpm run build
git add app/static/css/custom.css
