#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-04b"
BRANCH="registry-batch-04b"
BASE="db2c2d4c64b6c7ad4ee8107d57459cd45b7b9153"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

EXPECTED_FILES="$(
  printf '%s
'     data/claims/contrast-visual-influences-perceived-hierarchy.yaml     data/claims/readability-linguistic-influences-reading-speed.yaml     data/claims/typography-practice-influences-perceived-hierarchy.yaml     data/sources/nng-2021-visual-hierarchy-ux.yaml   | sort
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
assert (c+k+s,c,k,s)==(92,45,14,33), (c+k+s,c,k,s)
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
echo "===== PRECHECK 04B WORKTREE ====="

test -d "$WT" || fail "missing worktree $WT"

test "$(git -C "$WT" branch --show-current)" = "$BRANCH"   || fail "04B worktree is on wrong branch"

test "$(git -C "$WT" rev-parse HEAD)" = "$BASE"   || fail "04B worktree is not at required baseline"

test -z "$(git -C "$WT" diff --cached --name-only)"   || fail "04B worktree has staged changes"

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
    fail "04B mutation boundary mismatch"
  }

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"

echo
echo "===== ZERO-NEW-CONCEPT / ARCHITECTURE GATE ====="
if ! git -C "$WT" diff --quiet -- data/concepts; then
  fail "04B unexpectedly mutates concepts"
fi

for forbidden in   schema   vocab   docs/PROJECT_FOUNDATION.md   docs/PLUGIN_TARGET_ARCHITECTURE.md
do
  if ! git -C "$WT" diff --quiet -- "$forbidden"; then
    fail "forbidden mutation under $forbidden"
  fi
done

echo
echo "===== STAGE EXACT 04B FILES ====="
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
echo "===== COMMIT 04B ====="
git -C "$WT" commit -m "registry: add mechanism claims batch 04B"

BATCH_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "BATCH_04B_SHA: $BATCH_SHA"

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
    fail "04B commit mutation boundary mismatch"
  }

printf '%s
' "$COMMITTED_FILES"

echo
echo "===== PUSH 04B BRANCH ====="
git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)"   || fail "main moved before 04B integration"

test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE"   || fail "main baseline changed before 04B integration"

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
    "data/claims/contrast-visual-influences-perceived-hierarchy.yaml":
        "claim:contrast-visual-influences-perceived-hierarchy",
    "data/claims/readability-linguistic-influences-reading-speed.yaml":
        "claim:readability-linguistic-influences-reading-speed",
    "data/claims/typography-practice-influences-perceived-hierarchy.yaml":
        "claim:typography-practice-influences-perceived-hierarchy",
    "data/sources/nng-2021-visual-hierarchy-ux.yaml":
        "source:nng-2021-visual-hierarchy-ux",
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
echo "OUTCOME: REGISTRY_BATCH_04B_INTEGRATED"
echo "Corpus: 92 records — 45 concepts, 14 claims, 33 sources"
echo "Added claims: 3"
echo "Added sources: 1"
echo "New concepts: 0"
echo "Deferred candidates preserved: 2"
echo "Architecture: NO_REOPEN"
echo "No schema/vocabulary/Foundation changes"
