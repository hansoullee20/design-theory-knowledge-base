#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-03-closeout"
BRANCH="registry-batch-03-closeout"
BASE="5eac79107c0ef5833ddcc427f76a1789a43a2907"
TARGET="pilot/PILOT_RECORDS.md"
HEADING="## REGISTRY-BATCH-03-CLOSEOUT"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

validate_repo() {
  local dir="$1"
  (
    cd "$dir"
    python3 scripts/pilot_check.py --self-test
    python3 scripts/pilot_check.py
    git diff --check
    python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
assert (c+k+s,c,k,s)==(88,45,11,32), (c+k+s,c,k,s)
PY
  )
}

echo "===== PRECHECK MAIN ====="
git -C "$REPO" fetch origin main

test "$(git -C "$REPO" branch --show-current)" = "main"   || fail "canonical repo is not on main"

test -z "$(git -C "$REPO" status --porcelain)"   || {
    git -C "$REPO" status --short
    fail "canonical main is dirty"
  }

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "local main differs from origin/main"

test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE"   || fail "unexpected canonical baseline"

echo "MAIN: $(git -C "$REPO" rev-parse --short HEAD)"

echo
echo "===== PRECHECK BATCH-03 CLOSEOUT WORKTREE ====="

test -d "$WT" || fail "missing worktree $WT"

test "$(git -C "$WT" branch --show-current)" = "$BRANCH"   || fail "closeout worktree is on wrong branch"

test "$(git -C "$WT" rev-parse HEAD)" = "$BASE"   || fail "closeout worktree is not at required baseline"

test -z "$(git -C "$WT" diff --cached --name-only)"   || fail "closeout worktree has staged changes"

ACTUAL="$(
  git -C "$WT" status --porcelain=v1 |
  sed 's/^.. //' |
  sort
)"

test "$ACTUAL" = "$TARGET"   || {
    echo "ACTUAL:"
    printf '%s\n' "$ACTUAL"
    fail "closeout mutation boundary mismatch"
  }

grep -Fqx "$HEADING" "$WT/$TARGET"   || fail "Batch 03 closeout heading missing"

COUNT="$(grep -Fxc "$HEADING" "$WT/$TARGET")"
test "$COUNT" = "1"   || fail "Batch 03 closeout heading duplicated"

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"

echo
echo "===== VERIFY NO CANONICAL DATA MUTATION ====="
if ! git -C "$WT" diff --quiet -- data schema vocab; then
  fail "closeout unexpectedly mutates canonical data/schema/vocab"
fi

echo
echo "===== COMMIT BATCH-03 CLOSEOUT ====="
git -C "$WT" add "$TARGET"
git -C "$WT" diff --cached --check

git -C "$WT" commit   -m "governance: record Registry Batch 03 closeout"

CLOSEOUT_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "BATCH_03_CLOSEOUT_SHA: $CLOSEOUT_SHA"

echo
echo "===== PUSH CLOSEOUT BRANCH ====="
git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "main moved before closeout integration"

git -C "$REPO" merge --ff-only "$BRANCH"

echo
echo "===== FINAL CANONICAL VALIDATION ====="
validate_repo "$REPO"

grep -Fqx "$HEADING" "$REPO/$TARGET"   || fail "closeout heading missing after integration"

echo
echo "===== PUSH MAIN ====="
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo
echo "===== FINAL STATE ====="
git -C "$REPO" log -8 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)"   || fail "main is dirty"

test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_03_CLOSEOUT_INTEGRATED"
echo "Corpus: 88 records — 45 concepts, 11 claims, 32 sources"
echo "Batch 03 governance closeout recorded in pilot/PILOT_RECORDS.md"
echo "Canonical data mutation in closeout commit: 0"
echo "Deferred senses preserved: 3"
echo "Architecture: NO_REOPEN"
echo "No schema/vocabulary/Foundation changes"
