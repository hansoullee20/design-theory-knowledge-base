#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

OUT="/tmp/design-theory-parallel"
mkdir -p "$OUT/logs"

echo "===== BASELINE ====="
test "$(git branch --show-current)" = "main" \
  || { echo "STOP: expected main"; exit 1; }

test -z "$(git status --porcelain)" \
  || { echo "STOP: dirty working tree"; git status --short; exit 1; }

git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" \
  || { echo "STOP: local main differs from origin/main"; exit 1; }

echo "===== FETCH PLANNING HELPERS ====="
git fetch origin pilot-tools

for name in \
  plan_pf001_locator_batches.py \
  draft_registry_batch03_adjudication.py
do
  git show "origin/pilot-tools:scripts/$name" > "/tmp/$name"
  python3 -m py_compile "/tmp/$name"
done

echo "===== RUN PARALLEL PLANNING ====="
python3 /tmp/plan_pf001_locator_batches.py \
  "$OUT/pf001_legacy_locator_audit.csv" \
  "$OUT/pf001-batches" \
  > "$OUT/logs/pf001-plan.log" 2>&1 &
P1=$!

python3 /tmp/draft_registry_batch03_adjudication.py \
  "$OUT/batch03" \
  > "$OUT/logs/batch03.log" 2>&1 &
P2=$!

FAIL=0
wait "$P1" || FAIL=1
wait "$P2" || FAIL=1

if [ "$FAIL" -ne 0 ]; then
  echo "STOP: one or more planning tasks failed"
  for log in "$OUT"/logs/pf001-plan.log "$OUT"/logs/batch03.log; do
    echo "===== $log ====="
    cat "$log"
  done
  exit 1
fi

echo "===== READ-ONLY GATE ====="
test -z "$(git status --porcelain)" \
  || { echo "STOP: planning task mutated repository"; git status --short; exit 1; }

echo "===== PF-001 PLAN ====="
cat "$OUT/logs/pf001-plan.log"
sed -n '1,220p' "$OUT/pf001-batches/pf001_locator_batch_plan.md"

echo
echo "===== BATCH 03 ADJUDICATION ====="
cat "$OUT/logs/batch03.log"
cat "$OUT/batch03/registry_batch03_adjudication.md"

echo
echo "===== FINAL STATE ====="
git status --short
git rev-list --left-right --count origin/main...HEAD

echo
echo "OUTCOME: POST_02C_PARALLEL_PLANNING_PASS"
echo "Canonical mutations: 0"
echo "PF-001 plan: $OUT/pf001-batches/pf001_locator_batch_plan.md"
echo "Batch03 adjudication: $OUT/batch03/registry_batch03_adjudication.md"
