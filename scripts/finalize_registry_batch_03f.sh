#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-03f"
BRANCH="registry-batch-03f"
BASE="af3d86b55e5edaac5c7c8cecaf74409b1a1b524a"

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

EXPECTED_FILES="$(
  printf '%s
'     data/concepts/color-perceived.yaml     data/concepts/interaction-feedback.yaml     data/sources/w3c-coga-provide-feedback.yaml   | sort
)"

echo "===== PRECHECK MAIN ====="
git -C "$REPO" fetch origin main

test "$(git -C "$REPO" branch --show-current)" = "main" || fail "canonical repo is not on main"
test -z "$(git -C "$REPO" status --porcelain)" || {
  git -C "$REPO" status --short
  fail "canonical main is dirty"
}
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "local main differs from origin/main"
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE" || fail "unexpected canonical baseline"

echo "MAIN: $(git -C "$REPO" rev-parse --short HEAD)"

echo
echo "===== PRECHECK REGISTRY-BATCH-03F ====="

test -d "$WT" || fail "missing worktree $WT"
test "$(git -C "$WT" branch --show-current)" = "$BRANCH" || fail "03F worktree is on wrong branch"
test "$(git -C "$WT" rev-parse HEAD)" = "$BASE" || fail "03F worktree is not at required baseline"
test -z "$(git -C "$WT" diff --cached --name-only)" || fail "03F worktree has staged changes"

ACTUAL_FILES="$(
  git -C "$WT" status --porcelain=v1 |
  sed 's/^.. //' |
  sort
)"

test "$ACTUAL_FILES" = "$EXPECTED_FILES" || {
  echo "EXPECTED:"
  printf '%s
' "$EXPECTED_FILES"
  echo "ACTUAL:"
  printf '%s
' "$ACTUAL_FILES"
  fail "03F mutation boundary mismatch"
}

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"

echo
echo "===== ZERO-ARCHITECTURE-CHANGE GATE ====="
for forbidden in   schema   vocab   docs/PROJECT_FOUNDATION.md   docs/PLUGIN_TARGET_ARCHITECTURE.md
do
  if ! git -C "$WT" diff --quiet -- "$forbidden"; then
    fail "forbidden mutation under $forbidden"
  fi
done

echo
echo "===== COMMIT REGISTRY-BATCH-03F ====="
while IFS= read -r f; do
  git -C "$WT" add "$f"
done <<< "$EXPECTED_FILES"

git -C "$WT" diff --cached --check
git -C "$WT" commit -m "registry: add perceived color and interaction feedback batch 03F"

BATCH_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "BATCH_03F_SHA: $BATCH_SHA"

echo
echo "===== PUSH REGISTRY-BATCH-03F ====="
git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before 03F integration"

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
    "data/concepts/color-perceived.yaml": "concept:color-perceived",
    "data/concepts/interaction-feedback.yaml": "concept:interaction-feedback",
    "data/sources/w3c-coga-provide-feedback.yaml": "source:w3c-coga-provide-feedback",
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

test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0	0' || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_03F_INTEGRATED"
echo "Corpus: 88 records — 45 concepts, 11 claims, 32 sources"
echo "Added concepts: color-perceived, interaction-feedback"
echo "Added sources: 1 W3C COGA source"
echo "Reused sources: 1 CIE source"
echo "Claims added: 0"
echo "Psychophysical color: DEFER_SCOPE_AND_LOCUS"
echo "Status-message feedback: DEFER_SUBTYPE"
echo "Evaluative/design-process feedback: DEFER_SCOPE"
echo "Architecture: NO_REOPEN"
echo "No schema/vocabulary/Foundation changes"
