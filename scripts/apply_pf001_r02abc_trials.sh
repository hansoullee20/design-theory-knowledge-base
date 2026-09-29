#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/design-theory-knowledge-base"

git fetch origin pilot-tools

git show origin/pilot-tools:scripts/apply_pf001_r02abc_trials.py   > /tmp/apply_pf001_r02abc_trials.py

python3 -m py_compile /tmp/apply_pf001_r02abc_trials.py
python3 /tmp/apply_pf001_r02abc_trials.py
