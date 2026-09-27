#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/apply_whitespace_density_01.py > /tmp/apply_whitespace_density_01.py

python3 /tmp/apply_whitespace_density_01.py
