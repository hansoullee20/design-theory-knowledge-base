#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/finalize_registry_batch_02b.py   > /tmp/finalize_registry_batch_02b.py

python3 -m py_compile /tmp/finalize_registry_batch_02b.py
python3 /tmp/finalize_registry_batch_02b.py
