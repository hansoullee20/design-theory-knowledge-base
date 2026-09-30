#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/registry-batch-04-closeout"
BRANCH="registry-batch-04-closeout"
BASE="16d96613fc0f8f8b534205c2701f2ace3061f955"
TARGET="pilot/PILOT_RECORDS.md"
HEADING="## REGISTRY-BATCH-04-CLOSEOUT"
MESSAGE="governance: record Registry Batch 04 closeout"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

validate_corpus() {
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

verify_closeout_commit() {
  local sha="$1"

  test "$(git -C "$REPO" rev-parse "$sha^")" = "$BASE"     || fail "closeout parent is not Batch 04D checkpoint"

  local files
  files="$(git -C "$REPO" diff-tree --no-commit-id --name-only -r "$sha" | sort)"
  test "$files" = "$TARGET"     || {
      echo "ACTUAL CLOSEOUT FILES:"
      printf '%s\n' "$files"
      fail "closeout mutation boundary is not exactly $TARGET"
    }

  test "$(git -C "$REPO" show -s --format=%s "$sha")" = "$MESSAGE"     || fail "unexpected closeout commit message"

  git -C "$REPO" show "$sha:$TARGET" | grep -Fq "$HEADING"     || fail "closeout heading absent from committed pilot record"
}

echo "===== FETCH CURRENT STATE ====="
git -C "$REPO" fetch origin main

REMOTE_CLOSEOUT="$(
  git -C "$REPO" ls-remote --heads origin "$BRANCH" |
  awk '{print $1}'
)"

test "$(git -C "$REPO" branch --show-current)" = "main"   || fail "canonical repository is not on main"

test -z "$(git -C "$REPO" status --porcelain)"   || {
    git -C "$REPO" status --short
    fail "canonical main is dirty"
  }

ORIGIN_MAIN="$(git -C "$REPO" rev-parse origin/main)"
LOCAL_MAIN="$(git -C "$REPO" rev-parse HEAD)"

echo "local main:  $LOCAL_MAIN"
echo "origin/main: $ORIGIN_MAIN"
if [ -n "$REMOTE_CLOSEOUT" ]; then
  echo "origin/closeout: $REMOTE_CLOSEOUT"
else
  echo "origin/closeout: <absent>"
fi

echo
echo "===== IDEMPOTENT ALREADY-INTEGRATED CHECK ====="

if [ "$ORIGIN_MAIN" != "$BASE" ]; then
  if [ -n "$REMOTE_CLOSEOUT" ] && [ "$ORIGIN_MAIN" = "$REMOTE_CLOSEOUT" ]; then
    git -C "$REPO" fetch origin "$BRANCH"
    verify_closeout_commit "$ORIGIN_MAIN"

    if [ "$LOCAL_MAIN" = "$BASE" ]; then
      git -C "$REPO" merge --ff-only origin/main
    elif [ "$LOCAL_MAIN" != "$ORIGIN_MAIN" ]; then
      fail "local main is neither baseline nor integrated closeout"
    fi

    validate_corpus "$REPO"

    echo
    echo "===== FINAL STATE ====="
    git -C "$REPO" log -7 --oneline --decorate
    git -C "$REPO" status --short
    git -C "$REPO" rev-list --left-right --count origin/main...HEAD

    test -z "$(git -C "$REPO" status --porcelain)"       || fail "main is dirty"
    test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'       || fail "main divergence"

    echo
    echo "OUTCOME: REGISTRY_BATCH_04_CLOSEOUT_CONFIRMED_INTEGRATED"
    echo "Corpus: 98 records — 48 concepts, 17 claims, 33 sources"
    echo "Closeout mutation boundary: $TARGET only"
    echo "Batch 04 added: 6 claims, 3 concepts, 1 source"
    echo "Claim/concept ratio: 0.244 -> 0.354"
    echo "Deferred mechanism candidates preserved: 2"
    echo "Architecture: NO_REOPEN"
    exit 0
  fi

  fail "unexpected canonical baseline and no matching integrated closeout"
fi

test "$LOCAL_MAIN" = "$BASE"   || fail "local main differs from expected baseline"

test -z "$REMOTE_CLOSEOUT"   || fail "remote closeout branch already exists while main remains at baseline"

echo
echo "===== PRECHECK CLOSEOUT WORKTREE ====="

test -d "$WT" || fail "missing closeout worktree $WT"

test "$(git -C "$WT" branch --show-current)" = "$BRANCH"   || fail "closeout worktree is on wrong branch"

test "$(git -C "$WT" rev-parse HEAD)" = "$BASE"   || fail "closeout worktree is on wrong baseline"

test -z "$(git -C "$WT" diff --cached --name-only)"   || fail "closeout worktree has staged changes"

ACTUAL="$(
  git -C "$WT" status --porcelain=v1 |
  sed 's/^.. //' |
  sort
)"

test "$ACTUAL" = "$TARGET"   || {
    echo "ACTUAL:"
    printf '%s\n' "$ACTUAL"
    fail "closeout trial mutation boundary mismatch"
  }

grep -Fq "$HEADING" "$WT/$TARGET"   || fail "Batch 04 closeout heading missing from trial file"

echo "Mutation boundary: $TARGET"

echo
echo "===== PRE-COMMIT VALIDATION ====="
validate_corpus "$WT"

echo
echo "===== ZERO CANONICAL DATA / ARCHITECTURE MUTATION ====="

for forbidden in   data   schema   vocab   docs/PROJECT_FOUNDATION.md   docs/PLUGIN_TARGET_ARCHITECTURE.md
do
  if ! git -C "$WT" diff --quiet -- "$forbidden"; then
    fail "unexpected closeout mutation under $forbidden"
  fi
done

echo
echo "===== STAGE AND COMMIT CLOSEOUT ====="

git -C "$WT" add "$TARGET"

test "$(git -C "$WT" diff --cached --name-only)" = "$TARGET"   || fail "staged mutation boundary mismatch"

git -C "$WT" diff --cached --check
git -C "$WT" commit -m "$MESSAGE"

CLOSEOUT_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "CLOSEOUT_SHA: $CLOSEOUT_SHA"

echo
echo "===== VERIFY CLOSEOUT COMMIT ====="

test "$(git -C "$WT" rev-parse "$CLOSEOUT_SHA^")" = "$BASE"   || fail "unexpected closeout parent"

test "$(git -C "$WT" diff-tree --no-commit-id --name-only -r "$CLOSEOUT_SHA")" = "$TARGET"   || fail "closeout commit changed more than $TARGET"

grep -Fq "$HEADING" "$WT/$TARGET"   || fail "closeout heading missing after commit"

echo
echo "===== PUSH CLOSEOUT BRANCH ====="
git -C "$WT" push -u origin "$BRANCH"

echo
echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse origin/main)" = "$BASE"   || fail "origin/main moved before closeout integration"

test "$(git -C "$REPO" rev-parse origin/"$BRANCH")" = "$CLOSEOUT_SHA"   || fail "remote closeout branch does not match local closeout commit"

git -C "$REPO" merge --ff-only "$BRANCH"

echo
echo "===== FINAL CANONICAL VALIDATION ====="
validate_corpus "$REPO"

grep -Fq "$HEADING" "$REPO/$TARGET"   || fail "closeout heading missing on integrated main"

echo
echo "===== PUSH MAIN ====="
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main "$BRANCH"

test "$(git -C "$REPO" rev-parse HEAD)" = "$CLOSEOUT_SHA"   || fail "local main is not closeout commit"

test "$(git -C "$REPO" rev-parse origin/main)" = "$CLOSEOUT_SHA"   || fail "origin/main is not closeout commit"

test "$(git -C "$REPO" rev-parse origin/"$BRANCH")" = "$CLOSEOUT_SHA"   || fail "origin closeout branch is not closeout commit"

echo
echo "===== FINAL STATE ====="
git -C "$REPO" log -7 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)"   || fail "main is dirty"

test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0'   || fail "main divergence"

echo
echo "OUTCOME: REGISTRY_BATCH_04_CLOSEOUT_INTEGRATED"
echo "Corpus: 98 records — 48 concepts, 17 claims, 33 sources"
echo "Closeout mutation boundary: $TARGET only"
echo "Batch 04 added: 6 claims, 3 concepts, 1 source"
echo "Claim/concept ratio: 0.244 -> 0.354"
echo "Deferred mechanism candidates preserved: 2"
echo "Architecture: NO_REOPEN"
