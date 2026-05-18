#!/bin/bash
set -euo pipefail

PYTHON_PACKAGE_DIR="gh-md"
PYTHON_EGG_DIR="gh_md.egg-info"

run_quiet() {
    out=$(mktemp)
    "$@" >"$out" 2>&1 || cat "$out"
    rm -f "$out"
}

run_quiet uv sync

if [ ! -d $PYTHON_EGG_DIR ]; then
    pip install -e .
fi

gh-md test/README.gh.md --output test/README.md