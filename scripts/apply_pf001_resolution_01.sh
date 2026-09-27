#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git fetch origin pilot-tools

B64=/tmp/pf001_resolution_01.b64
PY=/tmp/apply_pf001_resolution_01.py

: > "$B64"
for n in 1 2 3 4; do
  git show "origin/pilot-tools:scripts/pf001_resolution_01.py.b64.part$n" >> "$B64"
done

base64 -d "$B64" > "$PY"

echo "107553e088a058edf218a39c6a182d504bb6d07317fb63b301c9491dff1814c1  $PY"   | sha256sum -c -

python3 -m py_compile "$PY"
python3 "$PY"
