#!/usr/bin/env bash
# Pre-commit hook: generate screenshots from staged content and stage them.
#
# Runs only when files relevant to the rendered UI are staged (templates,
# static assets, app Python code, or screenshots config).  Generates captures
# from a temporary checkout of the staged tree so the screenshots reflect
# exactly what is being committed, not any unstaged working-tree changes.
set -e

REPO_ROOT="$(pwd)"
SCREENSHOTS_DIR="$REPO_ROOT/screenshots"

HOOK_TMPDIR=$(mktemp -d)
trap 'rm -rf "$HOOK_TMPDIR"' EXIT

# Populate the temp dir with the staged (indexed) tree.
git checkout-index -a --prefix="$HOOK_TMPDIR/"

# Reuse node_modules (needed for the already-compiled CSS) to avoid reinstalling.
ln -s "$REPO_ROOT/node_modules" "$HOOK_TMPDIR/node_modules"

# Generate screenshots, writing output directly to the real repo directory.
(cd "$HOOK_TMPDIR" && python scripts/take_screenshots.py --output-dir "$SCREENSHOTS_DIR")

# Stage the screenshots.
git add "$SCREENSHOTS_DIR"
