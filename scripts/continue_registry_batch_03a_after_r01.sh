#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-03a"

R01_MAIN="3854d4868fa9210816f7a276ee9aa7b6643f39e1"
OLD_03A="ec7c97c47e4758ccfe87e9c76e13c6cc8c2413ae"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

echo "===== CONTINUE 03A AFTER R01 ====="
test -d "$REPO/.git" || fail "missing repo: $REPO"
test -d "$WT" || fail "missing 03A worktree: $WT"

git -C "$REPO" fetch origin main registry-batch-03a

echo "===== REMOTE STATE ====="
echo "origin/main:              $(git -C "$REPO" rev-parse origin/main)"
echo "origin/registry-batch-03a: $(git -C "$REPO" rev-parse origin/registry-batch-03a)"

# Idempotent completion path: if 03A is already contained in main, just verify.
if git -C "$REPO" merge-base --is-ancestor origin/registry-batch-03a origin/main; then
  echo "03A already contained in main; running final validation only."
  git -C "$REPO" switch main
  git -C "$REPO" reset --ff-only origin/main 2>/dev/null || true
  (
    cd "$REPO"
    python3 scripts/pilot_check.py --self-test
    python3 scripts/pilot_check.py
    git diff --check
    python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
PY
  )
  echo "OUTCOME: REGISTRY_BATCH_03A_ALREADY_INTEGRATED"
  exit 0
fi

test "$(git -C "$REPO" rev-parse origin/main)" = "$R01_MAIN"   || fail "origin/main is not the expected R01 checkpoint"

test "$(git -C "$REPO" branch --show-current)" = "main"   || fail "main repo is not on main"
test -z "$(git -C "$REPO" status --porcelain)"   || fail "main repo is dirty"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "local main differs from origin/main"

test "$(git -C "$WT" branch --show-current)" = "registry-batch-03a"   || fail "03A worktree is on wrong branch"
test -z "$(git -C "$WT" status --porcelain)"   || { git -C "$WT" status --short; fail "03A worktree is dirty"; }

LOCAL_03A="$(git -C "$WT" rev-parse HEAD)"
REMOTE_03A="$(git -C "$REPO" rev-parse origin/registry-batch-03a)"
test "$LOCAL_03A" = "$REMOTE_03A"   || fail "local 03A does not match origin/registry-batch-03a"

if [ "$REMOTE_03A" != "$OLD_03A" ]; then
  echo "NOTICE: 03A remote is not the original pre-rebase commit."
  echo "Proceeding only if it is already based on current main."
  git -C "$WT" merge-base --is-ancestor origin/main HEAD     || fail "03A remote changed unexpectedly and is not based on current main"
else
  echo "===== REBASE 03A ONTO R01 MAIN ====="
  git -C "$WT" rebase origin/main
fi

echo "===== POST-REBASE VALIDATION ====="
(
  cd "$WT"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
  python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
PY
)

echo "===== UPDATE 03A REMOTE ====="
git -C "$WT" push --force-with-lease origin registry-batch-03a

echo "===== FAST-FORWARD MAIN ====="
git -C "$REPO" fetch origin main registry-batch-03a
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "main moved before integration"
git -C "$REPO" merge --ff-only registry-batch-03a

echo "===== FINAL VALIDATION ====="
(
  cd "$REPO"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
  python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
print(f"FINAL COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
PY
)

echo "===== PUSH MAIN ====="
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== FINAL STATE ====="
git -C "$REPO" log -6 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_03A_INTEGRATED_AFTER_R01"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "PF001-R01 main checkpoint preserved"
echo "PF001-R02..R05 worktrees remain untouched"
