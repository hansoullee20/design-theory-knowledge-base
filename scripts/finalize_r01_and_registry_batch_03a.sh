#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WTROOT="$HOME/design-theory-parallel-worktrees"
WT_R01="$WTROOT/pf001-r01"
WT_03A="$WTROOT/registry-batch-03a"

BASE="0a495a2d3321694583177a800354694d1ea50244"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

echo "===== PRECHECK ====="
test -d "$REPO/.git" || fail "missing main repository: $REPO"
test -d "$WT_R01" || fail "missing worktree: $WT_R01"
test -d "$WT_03A" || fail "missing worktree: $WT_03A"

test "$(git -C "$REPO" branch --show-current)" = "main" || fail "main repo is not on main"
test -z "$(git -C "$REPO" status --porcelain)" || fail "main repo is dirty"

git -C "$REPO" fetch origin main

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "local main differs from origin/main"
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE"   || fail "unexpected main baseline"

test "$(git -C "$WT_R01" branch --show-current)" = "pf001-r01"   || fail "R01 worktree is on wrong branch"
test "$(git -C "$WT_03A" branch --show-current)" = "registry-batch-03a"   || fail "03A worktree is on wrong branch"

echo "===== VERIFY MUTATION BOUNDARIES ====="
R01_EXPECTED="$(printf '%s\n'   data/claims/whitespace-decreases-perceived-density.yaml   data/concepts/card-sorting.yaml   data/concepts/whitespace.yaml   data/sources/nng-2024-card-sorting.yaml   data/sources/tyler-forge-grid.yaml | sort)"
R01_ACTUAL="$(git -C "$WT_R01" status --porcelain=v1 | sed 's/^.. //' | sort)"
test "$R01_ACTUAL" = "$R01_EXPECTED" || {
  echo "R01 expected:"; printf '%s\n' "$R01_EXPECTED"
  echo "R01 actual:"; printf '%s\n' "$R01_ACTUAL"
  fail "R01 mutation boundary mismatch"
}

A03_EXPECTED="$(printf '%s\n'   data/concepts/shape-visual.yaml   data/concepts/space-compositional.yaml   data/sources/getty-aat-300056273-shape-form-attribute.yaml   data/sources/getty-aat-300068896-space-composition.yaml   pilot/PILOT_RECORDS.md | sort)"
A03_ACTUAL="$(git -C "$WT_03A" status --porcelain=v1 | sed 's/^.. //' | sort)"
test "$A03_ACTUAL" = "$A03_EXPECTED" || {
  echo "03A expected:"; printf '%s\n' "$A03_EXPECTED"
  echo "03A actual:"; printf '%s\n' "$A03_ACTUAL"
  fail "03A mutation boundary mismatch"
}

echo "===== REVALIDATE R01 ====="
(
  cd "$WT_R01"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
)

echo "===== REVALIDATE 03A ====="
(
  cd "$WT_03A"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
  python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
print(f"03A COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
PY
)

echo "===== CHECKPOINT R01 ====="
git -C "$WT_R01" add   data/claims/whitespace-decreases-perceived-density.yaml   data/concepts/card-sorting.yaml   data/concepts/whitespace.yaml   data/sources/nng-2024-card-sorting.yaml   data/sources/tyler-forge-grid.yaml
git -C "$WT_R01" diff --cached --check
test "$(git -C "$WT_R01" diff --cached --name-only | wc -l)" -eq 5   || fail "R01 expected 5 staged files"
git -C "$WT_R01" commit -m "provenance: backfill PF-001 web locators R01"
git -C "$WT_R01" push -u origin pf001-r01

echo "===== CHECKPOINT 03A ====="
git -C "$WT_03A" add   data/concepts/shape-visual.yaml   data/concepts/space-compositional.yaml   data/sources/getty-aat-300056273-shape-form-attribute.yaml   data/sources/getty-aat-300068896-space-composition.yaml   pilot/PILOT_RECORDS.md
git -C "$WT_03A" diff --cached --check
test "$(git -C "$WT_03A" diff --cached --name-only | wc -l)" -eq 5   || fail "03A expected 5 staged files"
git -C "$WT_03A" commit -m "registry: add shape and compositional space batch 03A"
git -C "$WT_03A" push -u origin registry-batch-03a

echo "===== INTEGRATE R01 FIRST ====="
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE"   || fail "main moved before R01 integration"
git -C "$REPO" merge --ff-only pf001-r01

(
  cd "$REPO"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
)
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "main diverged after R01 push"

R01_MAIN="$(git -C "$REPO" rev-parse HEAD)"
echo "R01 MAIN: $R01_MAIN"

echo "===== REBASE 03A ONTO R01 MAIN ====="
git -C "$WT_03A" fetch origin main
git -C "$WT_03A" rebase origin/main

(
  cd "$WT_03A"
  python3 scripts/pilot_check.py --self-test
  python3 scripts/pilot_check.py
  git diff --check
  python3 - <<'PY'
from pathlib import Path
c=len(list(Path("data/concepts").glob("*.yaml")))
k=len(list(Path("data/claims").glob("*.yaml")))
s=len(list(Path("data/sources").glob("*.yaml")))
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
print(f"POST-REBASE COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
PY
)

git -C "$WT_03A" push --force-with-lease origin registry-batch-03a

echo "===== INTEGRATE 03A ====="
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "main differs from origin before 03A integration"
git -C "$REPO" merge --ff-only registry-batch-03a

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
assert (c+k+s,c,k,s)==(78,40,11,27), (c+k+s,c,k,s)
print(f"FINAL COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
PY
)

git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== FINAL STATE ====="
git -C "$REPO" log -7 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty at final gate"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "final main divergence"

echo
echo "OUTCOME: R01_AND_REGISTRY_BATCH_03A_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "PF001-R01: integrated"
echo "Registry Batch 03A: integrated"
echo "PF001-R02..R05: research worktrees remain clean and available"
