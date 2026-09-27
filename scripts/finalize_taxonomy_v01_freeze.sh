#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/finalize_taxonomy_v01_freeze.py > /tmp/finalize_taxonomy_v01_freeze.py

python3 /tmp/finalize_taxonomy_v01_freeze.py
