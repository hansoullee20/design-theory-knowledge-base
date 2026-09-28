#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/apply_registry_batch_01a.py   > /tmp/apply_registry_batch_01a.py

python3 -m py_compile /tmp/apply_registry_batch_01a.py
python3 /tmp/apply_registry_batch_01a.py
