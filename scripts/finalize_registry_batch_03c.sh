#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-03c"
BRANCH="registry-batch-03c"
BASE="fd06323986719c7b51c61ba64364bd3d08f0a484"

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
c = len(list(Path("data/concepts").glob("*.yaml")))
k = len(list(Path("data/claims").glob("*.yaml")))
s = len(list(Path("data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+s} records — {c} concepts, {k} claims, {s} sources")
assert (c+k+s, c, k, s) == (85, 43, 11, 31), (c+k+s, c, k, s)
PY
  )
}

EXPECTED_FILES="$(
  printf '%s\n' \
    data/concepts/form-compositional.yaml \
    data/concepts/typography-practice.yaml \
    data/concepts/visual-balance-perceived.yaml \
    data/sources/getty-aat-300056247-balance-composition.yaml \
    data/sources/getty-aat-300056272-form-composition.yaml \
    data/sources/getty-aat-300195853-typography.yaml \
  | sort
)"

echo "===== PRECHECK MAIN ====="
git -C "$REPO" fetch origin main

test "$(git -C "$REPO" branch --show-current)" = "main" \
  || fail "canonical repo is not on main"

test -z "$(git -C "$REPO" status --porcelain)" \
  || {
    git -C "$REPO" status --short
    fail "canonical main is dirty"
  }

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" \
  || fail "local main differs from origin/main"

test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE" \
  || fail "unexpected canonical baseline"

echo "MAIN: $(git -C "$REPO" rev-parse --short HEAD)"

echo
echo "===== PRECHECK REGISTRY-BATCH-03C ====="

test -d "$WT" || fail "missing worktree $WT"

test "$(git -C "$WT" branch --show-current)" = "$BRANCH" \
  || fail "03C worktree is on wrong branch"

test "$(git -C "$WT" rev-parse HEAD)" = "$BASE" \
  || fail "03C worktree is not at required baseline"

test -z "$(git -C "$WT" diff --cached --name-only)" \
  || fail "03C worktree has staged changes"

ACTUAL_FILES="$(
  git -C "$WT" status --porcelain=v1 \
  | sed 's/^.. //' \
  | sort
)"

test "$ACTUAL_FILES" = "$EXPECTED_FILES" \
  || {
    echo "EXPECTED:"
    printf '%s\n' "$EXPECTED_FILES"
    echo "ACTUAL:"
    printf '%s\n' "$ACTUAL_FILES"
    fail "03C mutation boundary mismatch"
  }

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"

echo
echo "===== ZERO-ARCHITECTURE-CHANGE GATE ====="
for forbidden in \
  schema \
  vocab \
  docs/PROJECT_FOUNDATION.md \
  docs/PLUGIN_TARGET_ARCHITECTURE.md
do
  if ! git -C "$WT" diff --quiet -- "$forbidden"; then
    fail "forbidden mutation under $forbidden"
  fi
done

echo
echo "===== COMMIT REGISTRY-BATCH-03C ====="

while IFS= read -r f; do
  git -C "$WT" add "$f"
done <<< "$EXPECTED_FILES"

git -C "$WT" diff --cached --check

git -C "$WT" commit \
  -m "registry: add deferred fundamentals batch 03C"

BATCH_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "BATCH_03C_SHA: $BATCH_SHA"

echo
echo "===== PUSH REGISTRY-BATCH-03C ====="
git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" \
  || fail "main moved before 03C integration"

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
    "data/concepts/form-compositional.yaml": "concept:form-compositional",
    "data/concepts/visual-balance-perceived.yaml": "concept:visual-balance-perceived",
    "data/concepts/typography-practice.yaml": "concept:typography-practice",
    "data/sources/getty-aat-300056272-form-composition.yaml": "source:getty-aat-300056272-form-composition",
    "data/sources/getty-aat-300056247-balance-composition.yaml": "source:getty-aat-300056247-balance-composition",
    "data/sources/getty-aat-300195853-typography.yaml": "source:getty-aat-300195853-typography",
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

test -z "$(git -C "$REPO" status --porcelain)" \
  || fail "main is dirty"

test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' \
  || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_03C_INTEGRATED"
echo "Corpus: 85 records — 43 concepts, 11 claims, 31 sources"
echo "Added concepts: form-compositional, visual-balance-perceived, typography-practice"
echo "Added sources: 3 Getty AAT records"
echo "Claims added: 0"
echo "Color: SPLIT_REQUIRED"
echo "Feedback: SPLIT_REQUIRED"
echo "Architecture: NO_REOPEN"
echo "No schema/vocabulary/Foundation changes"
