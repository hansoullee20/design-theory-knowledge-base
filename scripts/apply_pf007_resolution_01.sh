#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/apply_pf007_resolution_01.py > /tmp/apply_pf007_resolution_01.py

python3 /tmp/apply_pf007_resolution_01.py
