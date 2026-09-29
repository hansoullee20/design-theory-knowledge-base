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

patch_id() {
  git -C "$WT" show --pretty=format: --no-ext-diff "$1" | git patch-id --stable | awk '{print $1}'
}

echo "===== RESOLVE LOCAL 03A STATE ====="
test -d "$REPO/.git" || fail "missing repo: $REPO"
test -d "$WT" || fail "missing 03A worktree: $WT"

git -C "$REPO" fetch origin main registry-batch-03a

MAIN_REMOTE="$(git -C "$REPO" rev-parse origin/main)"
REMOTE_03A="$(git -C "$REPO" rev-parse origin/registry-batch-03a)"
LOCAL_03A="$(git -C "$WT" rev-parse HEAD)"
LOCAL_BRANCH="$(git -C "$WT" branch --show-current)"

echo "origin/main:              $MAIN_REMOTE"
echo "origin/registry-batch-03a: $REMOTE_03A"
echo "local registry-batch-03a:  $LOCAL_03A"
echo "local branch:              $LOCAL_BRANCH"

test "$MAIN_REMOTE" = "$R01_MAIN" || fail "origin/main is not the expected R01 checkpoint"
test "$LOCAL_BRANCH" = "registry-batch-03a" || fail "03A worktree is on wrong branch"
test -z "$(git -C "$WT" status --porcelain)" || {
  git -C "$WT" status --short
  fail "03A worktree is dirty"
}

echo "===== CLASSIFY LOCAL/REMOTE RELATION ====="

if git -C "$REPO" merge-base --is-ancestor origin/registry-batch-03a origin/main; then
  echo "REMOTE_03A_STATUS=ALREADY_IN_MAIN"
  git -C "$REPO" switch main
  git -C "$REPO" pull --ff-only origin main
else
  if [ "$LOCAL_03A" = "$REMOTE_03A" ]; then
    echo "LOCAL_03A_STATUS=MATCHES_REMOTE_PRE_REBASE"
    echo "===== REBASE 03A ONTO R01 MAIN ====="
    git -C "$WT" rebase origin/main
    LOCAL_03A="$(git -C "$WT" rev-parse HEAD)"
  else
    echo "LOCAL_03A_STATUS=DIFFERS_FROM_REMOTE"

    if git -C "$WT" merge-base --is-ancestor origin/main "$LOCAL_03A"; then
      AHEAD="$(git -C "$WT" rev-list --count origin/main.."$LOCAL_03A")"
      echo "local commits ahead of origin/main: $AHEAD"

      if [ "$AHEAD" = "1" ]; then
        LOCAL_PID="$(patch_id "$LOCAL_03A")"
        REMOTE_PID="$(patch_id "$REMOTE_03A")"
        echo "local patch-id:  $LOCAL_PID"
        echo "remote patch-id: $REMOTE_PID"

        if [ "$LOCAL_PID" = "$REMOTE_PID" ]; then
          echo "LOCAL_03A_STATUS=VALID_REBASED_EQUIVALENT"
        else
          fail "local 03A is on current main but its patch differs from remote 03A"
        fi
      else
        fail "local 03A is based on current main but has $AHEAD commits; expected exactly 1"
      fi
    else
      echo "===== DIAGNOSTIC GRAPH ====="
      git -C "$REPO" log --graph --oneline --decorate --all -12
      fail "local 03A differs from remote and is not a descendant of current main"
    fi
  fi

  echo "===== VALIDATE REBASED 03A ====="
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

  LOCAL_03A="$(git -C "$WT" rev-parse HEAD)"

  echo "===== UPDATE REMOTE 03A WITH EXPLICIT LEASE ====="
  git -C "$WT" push     --force-with-lease="refs/heads/registry-batch-03a:$REMOTE_03A"     origin     registry-batch-03a

  echo "===== FAST-FORWARD MAIN ====="
  git -C "$REPO" fetch origin main registry-batch-03a

  test "$(git -C "$REPO" branch --show-current)" = "main" || fail "main repo is not on main"
  test -z "$(git -C "$REPO" status --porcelain)" || fail "main repo is dirty"
  test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"     || fail "local main differs from origin/main"

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

  git -C "$REPO" push origin main
fi

echo "===== FINAL STATE ====="
git -C "$REPO" fetch origin main registry-batch-03a
git -C "$REPO" log -7 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_03A_RECOVERED_AND_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "PF001-R01 preserved on main"
echo "PF001-R02..R05 untouched"
