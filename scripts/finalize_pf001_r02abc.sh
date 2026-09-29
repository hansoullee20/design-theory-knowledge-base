#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WTROOT="$HOME/design-theory-parallel-worktrees"
BASE="06b7cd9"

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
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
PY
  )
}

check_boundary() {
  local wt="$1"
  shift
  local expected actual
  expected="$(printf '%s\n' "$@" | sort)"
  actual="$(git -C "$wt" status --porcelain=v1 | sed 's/^.. //' | sort)"
  test "$actual" = "$expected" || {
    echo "EXPECTED:"
    printf '%s\n' "$expected"
    echo "ACTUAL:"
    printf '%s\n' "$actual"
    fail "mutation boundary mismatch for $wt"
  }
}

echo "===== PRECHECK MAIN ====="
test -d "$REPO/.git" || fail "missing repo $REPO"
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" branch --show-current)" = "main" || fail "repo not on main"
test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main differs from origin/main"
test "$(git -C "$REPO" rev-parse --short HEAD)" = "$BASE" || fail "unexpected main baseline"

A="$WTROOT/pf001-r02a"
B="$WTROOT/pf001-r02b"
C="$WTROOT/pf001-r02c"

for wt in "$A" "$B" "$C"; do
  test -d "$wt" || fail "missing worktree $wt"
done

test "$(git -C "$A" branch --show-current)" = "pf001-r02a" || fail "R02A wrong branch"
test "$(git -C "$B" branch --show-current)" = "pf001-r02b" || fail "R02B wrong branch"
test "$(git -C "$C" branch --show-current)" = "pf001-r02c" || fail "R02C wrong branch"

test "$(git -C "$A" rev-parse --short HEAD)" = "$BASE" || fail "R02A wrong base"
test "$(git -C "$B" rev-parse --short HEAD)" = "$BASE" || fail "R02B wrong base"
test "$(git -C "$C" rev-parse --short HEAD)" = "$BASE" || fail "R02C wrong base"

echo "===== MUTATION BOUNDARIES ====="
check_boundary "$A"   data/claims/proximity-increases-perceptual-grouping.yaml   data/concepts/figure-ground-organization.yaml   data/concepts/figure.yaml   data/concepts/ground.yaml   data/concepts/perceptual-grouping.yaml   data/concepts/proximity.yaml

check_boundary "$B"   data/claims/specified-hierarchy-influences-perceived-hierarchy.yaml   data/concepts/hierarchy-perceived.yaml   data/concepts/hierarchy-specified.yaml

check_boundary "$C"   data/claims/display-object-density-influences-perceived-density.yaml   data/concepts/perceived-density.yaml

echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$A"
validate_repo "$B"
validate_repo "$C"

echo "===== COMMIT + PUSH R02A ====="
git -C "$A" add   data/claims/proximity-increases-perceptual-grouping.yaml   data/concepts/figure-ground-organization.yaml   data/concepts/figure.yaml   data/concepts/ground.yaml   data/concepts/perceptual-grouping.yaml   data/concepts/proximity.yaml
git -C "$A" diff --cached --check
git -C "$A" commit -m "provenance: backfill Wagemans locators PF001-R02A"
git -C "$A" push -u origin pf001-r02a

echo "===== COMMIT + PUSH R02B ====="
git -C "$B" add   data/claims/specified-hierarchy-influences-perceived-hierarchy.yaml   data/concepts/hierarchy-perceived.yaml   data/concepts/hierarchy-specified.yaml
git -C "$B" diff --cached --check
git -C "$B" commit -m "provenance: backfill visual hierarchy locators PF001-R02B"
git -C "$B" push -u origin pf001-r02b

echo "===== COMMIT + PUSH R02C ====="
git -C "$C" add   data/claims/display-object-density-influences-perceived-density.yaml   data/concepts/perceived-density.yaml
git -C "$C" diff --cached --check
git -C "$C" commit -m "provenance: backfill perceived-density locators PF001-R02C"
git -C "$C" push -u origin pf001-r02c

echo "===== INTEGRATE R02A ====="
git -C "$REPO" merge --ff-only pf001-r02a
validate_repo "$REPO"
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== REBASE + INTEGRATE R02B ====="
OLD_B_REMOTE="$(git -C "$REPO" rev-parse origin/pf001-r02b)"
git -C "$B" fetch origin main
git -C "$B" rebase origin/main
validate_repo "$B"
git -C "$B" push --force-with-lease="refs/heads/pf001-r02b:$OLD_B_REMOTE" origin pf001-r02b
git -C "$REPO" fetch origin main pf001-r02b
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before R02B integration"
git -C "$REPO" merge --ff-only pf001-r02b
validate_repo "$REPO"
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== REBASE + INTEGRATE R02C ====="
OLD_C_REMOTE="$(git -C "$REPO" rev-parse origin/pf001-r02c)"
git -C "$C" fetch origin main
git -C "$C" rebase origin/main
validate_repo "$C"
git -C "$C" push --force-with-lease="refs/heads/pf001-r02c:$OLD_C_REMOTE" origin pf001-r02c
git -C "$REPO" fetch origin main pf001-r02c
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before R02C integration"
git -C "$REPO" merge --ff-only pf001-r02c
validate_repo "$REPO"
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== FINAL STATE ====="
git -C "$REPO" log -8 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' || fail "main diverged"

echo
echo "OUTCOME: PF001_R02ABC_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "R02A Wagemans: integrated"
echo "R02B Saw-Gatzke: integrated"
echo "R02C Schwartz-Chassidim: integrated"
echo "R02D Legge: still on hold"
echo "R03-R05: untouched"
