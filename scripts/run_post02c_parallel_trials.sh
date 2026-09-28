#!/usr/bin/env bash
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

WTROOT="$HOME/design-theory-parallel-worktrees"
OUT="/tmp/design-theory-parallel"
mkdir -p "$OUT/logs"

echo "===== BASELINE ====="
test "$(git branch --show-current)" = "main"   || { echo "STOP: expected main"; exit 1; }
test -z "$(git status --porcelain)"   || { echo "STOP: dirty main"; git status --short; exit 1; }

git fetch origin main pilot-tools
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"   || { echo "STOP: local main differs from origin/main"; exit 1; }
test "$(git rev-parse --short HEAD)" = "0a495a2"   || { echo "STOP: unexpected main baseline"; exit 1; }

echo "===== MATERIALIZE HELPERS ====="
for name in   prepare_post02c_parallel_worktrees.py   apply_registry_batch_03a.py   apply_pf001_r01.py
do
  git show "origin/pilot-tools:scripts/$name" > "/tmp/$name"
  python3 -m py_compile "/tmp/$name"
done

echo "===== PREPARE PARALLEL WORKTREES ====="
python3 /tmp/prepare_post02c_parallel_worktrees.py   "$OUT/pf001-batches/pf001_locator_batch_plan.json"   "$WTROOT"

echo "===== RUN 03A + PF001-R01 IN PARALLEL ====="
(
  cd "$WTROOT/registry-batch-03a"
  python3 /tmp/apply_registry_batch_03a.py
) > "$OUT/logs/03a.log" 2>&1 &
P1=$!

(
  cd "$WTROOT/pf001-r01"
  python3 /tmp/apply_pf001_r01.py
) > "$OUT/logs/pf001-r01.log" 2>&1 &
P2=$!

FAIL=0
wait "$P1" || FAIL=1
wait "$P2" || FAIL=1

if [ "$FAIL" -ne 0 ]; then
  echo "STOP: one or more mutation trials failed"
  echo "===== 03A LOG ====="
  cat "$OUT/logs/03a.log"
  echo "===== PF001-R01 LOG ====="
  cat "$OUT/logs/pf001-r01.log"
  exit 1
fi

echo "===== 03A RESULT ====="
cat "$OUT/logs/03a.log"

echo "===== PF001-R01 RESULT ====="
cat "$OUT/logs/pf001-r01.log"

echo "===== WORKTREE STATUS ====="
git -C "$WTROOT/registry-batch-03a" status --short
git -C "$WTROOT/pf001-r01" status --short

echo "===== MAIN IMMUTABILITY GATE ====="
test -z "$(git status --porcelain)"   || { echo "STOP: main mutated"; git status --short; exit 1; }
git rev-list --left-right --count origin/main...HEAD

echo "===== PREPARED RESEARCH WORKTREES ====="
for n in pf001-r02 pf001-r03 pf001-r04 pf001-r05; do
  echo "--- $n"
  git -C "$WTROOT/$n" status --short
done

echo
echo "OUTCOME: POST_02C_PARALLEL_TRIALS_PASS"
echo "03A: trial mutation ready for semantic review; no commit"
echo "PF001-R01: verified web-locator mutation ready for review; no commit"
echo "PF001-R02..R05: clean research worktrees prepared"
echo "main: unchanged at 0a495a2"
