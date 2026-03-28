#!/usr/bin/env bash
# Pre-commit hook: rebuild SCSS from staged content and stage the CSS output.
#
# Runs when SCSS files are staged OR the compiled CSS output does not yet exist.
# Compiles from a temporary checkout of the staged tree so the output reflects
# exactly what is being committed, not any unstaged working-tree changes.
set -e

CSS_OUT="app/static/css/custom.css"

# Skip if no SCSS files are staged and the CSS output already exists.
if ! git diff --cached --name-only | grep -q '^app/static/scss/' && [ -f "$CSS_OUT" ]; then
    exit 0
fi

HOOK_TMPDIR=$(mktemp -d)
trap 'rm -rf "$HOOK_TMPDIR"' EXIT

# Populate the temp dir with the staged (indexed) tree.
git checkout-index -a --prefix="$HOOK_TMPDIR/"

# Reuse the working-tree node_modules to avoid reinstalling dependencies.
ln -s "$(pwd)/node_modules" "$HOOK_TMPDIR/node_modules"

# Build CSS from within the temporary tree.
(cd "$HOOK_TMPDIR" && pnpm run build)

# Copy the result back to the working tree and stage it.
mkdir -p "$(dirname "$CSS_OUT")"
cp "$HOOK_TMPDIR/$CSS_OUT" "$CSS_OUT"
git add "$CSS_OUT"
