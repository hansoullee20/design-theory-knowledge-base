#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="/tmp/design-theory-parallel"
mkdir -p "$OUT/logs"

echo "===== FETCH PILOT TOOLS ====="
git fetch origin pilot-tools

echo "===== MATERIALIZE HELPERS ====="
for name in \
  finalize_registry_batch_02b.py \
  audit_pf001_legacy_locators.py \
  audit_registry_backlog.py \
  draft_fpattern_02c.py \
  draft_skill_evidence_research.py
do
  git show "origin/pilot-tools:scripts/$name" > "/tmp/$name"
  python3 -m py_compile "/tmp/$name"
done

echo "===== PHASE A: FINALIZE + INTEGRATE 02B ====="
python3 /tmp/finalize_registry_batch_02b.py

echo "===== CLEAN MAIN GATE ====="
test "$(git branch --show-current)" = "main" \
  || { echo "STOP: finalize did not leave repository on main"; exit 1; }
test -z "$(git status --porcelain)" \
  || { echo "STOP: repository dirty after 02B integration"; git status --short; exit 1; }
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" \
  || { echo "STOP: main not synchronized after 02B integration"; exit 1; }

echo "===== PHASE B-E: PARALLEL READ-ONLY WORK ====="
python3 /tmp/audit_pf001_legacy_locators.py "$OUT" > "$OUT/logs/locator.log" 2>&1 &
P1=$!
python3 /tmp/audit_registry_backlog.py "$OUT" > "$OUT/logs/backlog.log" 2>&1 &
P2=$!
python3 /tmp/draft_fpattern_02c.py "$OUT" > "$OUT/logs/fpattern.log" 2>&1 &
P3=$!
python3 /tmp/draft_skill_evidence_research.py "$OUT" > "$OUT/logs/skill-evidence.log" 2>&1 &
P4=$!

FAIL=0
for spec in "$P1:locator" "$P2:backlog" "$P3:fpattern" "$P4:skill-evidence"; do
  pid="${spec%%:*}"
  name="${spec##*:}"
  if wait "$pid"; then
    echo "PASS: $name"
  else
    echo "FAIL: $name"
    FAIL=1
  fi
done

echo "===== READ-ONLY MUTATION GATE ====="
test -z "$(git status --porcelain)" \
  || { echo "STOP: a read-only audit mutated repository state"; git status --short; exit 1; }

if [ "$FAIL" -ne 0 ]; then
  echo "STOP: one or more parallel tasks failed"
  for log in "$OUT"/logs/*.log; do
    echo "===== $log ====="
    cat "$log"
  done
  exit 1
fi

echo "===== PARALLEL TASK LOGS ====="
for log in "$OUT"/logs/*.log; do
  echo
  echo "----- $(basename "$log") -----"
  cat "$log"
done

echo
echo "===== BACKLOG REPORT ====="
sed -n '1,180p' "$OUT/registry_backlog_reconciliation.md"

echo
echo "===== F-PATTERN 02C DRAFT ====="
cat "$OUT/fpattern_02c_adjudication.md"

echo
echo "===== SKILL / EVIDENCE RESEARCH ====="
cat "$OUT/skill_creator_evidence_research.md"

echo
echo "===== LOCATOR AUDIT SUMMARY ====="
sed -n '1,80p' "$OUT/pf001_legacy_locator_audit.md"

echo
echo "===== ARTIFACTS ====="
find "$OUT" -maxdepth 2 -type f -print | sort

echo
echo "===== FINAL REPOSITORY STATE ====="
git log -5 --oneline --decorate
git status --short
git rev-list --left-right --count origin/main...HEAD

echo
echo "OUTCOME: POST_02B_PARALLEL_BUNDLE_PASS"
echo "Repository writes completed: 02B checkpoint + main integration only"
echo "Parallel research/audit outputs: $OUT"
echo "Canonical mutations by audits/research: 0"
