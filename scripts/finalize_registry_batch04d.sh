#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-04d"
BRANCH="registry-batch-04d"
BASE="e6f2f3083b620e66f43c416e732aba6f74fa529f"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

EXPECTED_FILES="$(
  printf '%s
'     data/claims/common-region-influences-perceptual-grouping.yaml     data/claims/element-connectedness-influences-perceptual-grouping.yaml     data/claims/visual-similarity-increases-perceptual-grouping.yaml     data/concepts/common-region.yaml     data/concepts/element-connectedness.yaml     data/concepts/visual-similarity.yaml   | sort
)"

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
assert (c+k+s,c,k,s)==(98,48,17,33), (c+k+s,c,k,s)
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
echo "===== PRECHECK 04D WORKTREE ====="

test -d "$WT" || fail "missing worktree $WT"

test "$(git -C "$WT" branch --show-current)" = "$BRANCH"   || fail "04D worktree is on wrong branch"

test "$(git -C "$WT" rev-parse HEAD)" = "$BASE"   || fail "04D worktree is not at required baseline"

test -z "$(git -C "$WT" diff --cached --name-only)"   || fail "04D worktree has staged changes"

ACTUAL_FILES="$(
  git -C "$WT" status --porcelain=v1 |
  sed 's/^.. //' |
  sort
)"

test "$ACTUAL_FILES" = "$EXPECTED_FILES"   || {
    echo "EXPECTED:"
    printf '%s
' "$EXPECTED_FILES"
    echo "ACTUAL:"
    printf '%s
' "$ACTUAL_FILES"
    fail "04D mutation boundary mismatch"
  }

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"

echo
echo "===== ZERO-NEW-SOURCE / ARCHITECTURE GATE ====="

if ! git -C "$WT" diff --quiet -- data/sources; then
  fail "04D unexpectedly mutates source records"
fi

for forbidden in   schema   vocab   docs/PROJECT_FOUNDATION.md   docs/PLUGIN_TARGET_ARCHITECTURE.md
do
  if ! git -C "$WT" diff --quiet -- "$forbidden"; then
    fail "forbidden mutation under $forbidden"
  fi
done

echo
echo "===== STAGE EXACT 04D FILES ====="

while IFS= read -r f; do
  git -C "$WT" add "$f"
done <<< "$EXPECTED_FILES"

STAGED="$(
  git -C "$WT" diff --cached --name-only |
  sort
)"

test "$STAGED" = "$EXPECTED_FILES"   || {
    echo "STAGED:"
    printf '%s
' "$STAGED"
    fail "staged mutation boundary mismatch"
  }

git -C "$WT" diff --cached --check

echo
echo "===== COMMIT 04D ====="

git -C "$WT" commit -m "registry: add Gestalt grouping mechanisms batch 04D"

BATCH_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "BATCH_04D_SHA: $BATCH_SHA"

echo
echo "===== VERIFY COMMIT MUTATION ====="

COMMITTED_FILES="$(
  git -C "$WT" diff-tree --no-commit-id --name-only -r "$BATCH_SHA" |
  sort
)"

test "$COMMITTED_FILES" = "$EXPECTED_FILES"   || {
    echo "COMMITTED:"
    printf '%s
' "$COMMITTED_FILES"
    fail "04D commit mutation boundary mismatch"
  }

printf '%s
' "$COMMITTED_FILES"

echo
echo "===== PUSH 04D BRANCH ====="

git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="

git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "main moved before 04D integration"

test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE"   || fail "main baseline changed before 04D integration"

git -C "$REPO" merge --ff-only "$BRANCH"

echo
echo "===== FINAL CANONICAL VALIDATION ====="

validate_repo "$REPO"

echo
echo "===== VERIFY ADDED IDS ====="

python3 - <<'PY'
from pathlib import Path
import yaml

repo = Path.home() / "design-theory-knowledge-base"
expected = {
    "data/concepts/visual-similarity.yaml":
        "concept:visual-similarity",
    "data/concepts/common-region.yaml":
        "concept:common-region",
    "data/concepts/element-connectedness.yaml":
        "concept:element-connectedness",
    "data/claims/visual-similarity-increases-perceptual-grouping.yaml":
        "claim:visual-similarity-increases-perceptual-grouping",
    "data/claims/common-region-influences-perceptual-grouping.yaml":
        "claim:common-region-influences-perceptual-grouping",
    "data/claims/element-connectedness-influences-perceptual-grouping.yaml":
        "claim:element-connectedness-influences-perceptual-grouping",
}

for rel, expected_id in expected.items():
    p = repo / rel
    assert p.exists(), rel
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert d["id"] == expected_id, (rel, d.get("id"), expected_id)
    print(expected_id)
PY

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
echo "OUTCOME: REGISTRY_BATCH_04D_INTEGRATED"
echo "Corpus: 98 records — 48 concepts, 17 claims, 33 sources"
echo "Added concepts: 3"
echo "Added claims: 3"
echo "Added sources: 0"
echo "Reused sources: 1"
echo "Representation failure: 0"
echo "Architecture: NO_REOPEN"
echo "No schema/vocabulary/Foundation changes"
