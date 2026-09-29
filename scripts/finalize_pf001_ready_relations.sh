#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WTROOT="$HOME/design-theory-parallel-worktrees"
BASE="1c6a211444131e0088fcf3e53c6693ddb0224f32"

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

declare -a BRANCHES=(
  pf001-r03a
  pf001-r03b
  pf001-r04a
  pf001-r04b
  pf001-r04c
  pf001-r05a
)

commit_message() {
  case "$1" in
    pf001-r03a) echo "provenance: backfill Kubovy proximity locator PF001-R03A" ;;
    pf001-r03b) echo "provenance: backfill perceived-affordance locator PF001-R03B" ;;
    pf001-r04a) echo "provenance: backfill Lupton alignment locators PF001-R04A" ;;
    pf001-r04b) echo "provenance: backfill Norman signifier locators PF001-R04B" ;;
    pf001-r04c) echo "provenance: backfill Gibson affordance locator PF001-R04C" ;;
    pf001-r05a) echo "provenance: backfill DuBay readability locator PF001-R05A" ;;
    *) fail "unknown branch $1" ;;
  esac
}

stage_branch() {
  local branch="$1"
  local wt="$WTROOT/$branch"

  case "$branch" in
    pf001-r03a)
      git -C "$wt" add data/claims/proximity-increases-perceptual-grouping.yaml
      ;;
    pf001-r03b)
      git -C "$wt" add data/concepts/affordance-perceived.yaml
      ;;
    pf001-r04a)
      git -C "$wt" add \
        data/claims/left-alignment-conventional-for-body-text.yaml \
        data/concepts/left-alignment.yaml \
        data/sources/lupton-2010-thinking-with-type.yaml
      ;;
    pf001-r04b)
      git -C "$wt" add \
        data/claims/signifier-influences-perceived-affordance.yaml \
        data/concepts/signifier.yaml
      ;;
    pf001-r04c)
      git -C "$wt" add data/concepts/affordance-ecological.yaml
      ;;
    pf001-r05a)
      git -C "$wt" add data/concepts/readability-linguistic.yaml
      ;;
  esac
}

echo "===== PRECHECK MAIN ====="
test -d "$REPO/.git" || fail "missing repo $REPO"
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" branch --show-current)" = "main" || fail "repo not on main"
test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main differs from origin/main"
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE" || fail "unexpected main baseline"

for b in "${BRANCHES[@]}"; do
  wt="$WTROOT/$b"
  test -d "$wt" || fail "missing worktree $wt"
  test "$(git -C "$wt" branch --show-current)" = "$b" || fail "$b wrong branch"
  test "$(git -C "$wt" rev-parse HEAD)" = "$BASE" || fail "$b wrong base"
done

echo "===== VERIFY MUTATION BOUNDARIES ====="
check_boundary "$WTROOT/pf001-r03a" \
  data/claims/proximity-increases-perceptual-grouping.yaml

check_boundary "$WTROOT/pf001-r03b" \
  data/concepts/affordance-perceived.yaml

check_boundary "$WTROOT/pf001-r04a" \
  data/claims/left-alignment-conventional-for-body-text.yaml \
  data/concepts/left-alignment.yaml \
  data/sources/lupton-2010-thinking-with-type.yaml

check_boundary "$WTROOT/pf001-r04b" \
  data/claims/signifier-influences-perceived-affordance.yaml \
  data/concepts/signifier.yaml

check_boundary "$WTROOT/pf001-r04c" \
  data/concepts/affordance-ecological.yaml

check_boundary "$WTROOT/pf001-r05a" \
  data/concepts/readability-linguistic.yaml

echo "===== PRE-COMMIT VALIDATION ====="
for b in "${BRANCHES[@]}"; do
  echo "--- $b"
  validate_repo "$WTROOT/$b"
done

echo "===== CHECKPOINT ALL READY BRANCHES ====="
for b in "${BRANCHES[@]}"; do
  wt="$WTROOT/$b"
  echo "--- $b"
  stage_branch "$b"
  git -C "$wt" diff --cached --check
  git -C "$wt" commit -m "$(commit_message "$b")"
  git -C "$wt" push -u origin "$b"
done

echo "===== SERIAL INTEGRATION ====="
FIRST=1
for b in "${BRANCHES[@]}"; do
  wt="$WTROOT/$b"
  echo
  echo "===== INTEGRATE $b ====="

  if [ "$FIRST" -eq 1 ]; then
    FIRST=0
  else
    OLD_REMOTE="$(git -C "$REPO" rev-parse "origin/$b")"
    git -C "$wt" fetch origin main
    git -C "$wt" rebase origin/main
    validate_repo "$wt"
    git -C "$wt" push \
      --force-with-lease="refs/heads/$b:$OLD_REMOTE" \
      origin "$b"
  fi

  git -C "$REPO" fetch origin main "$b"
  test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" \
    || fail "main moved before integrating $b"

  git -C "$REPO" merge --ff-only "$b"
  validate_repo "$REPO"
  git -C "$REPO" push origin main
  git -C "$REPO" fetch origin main
  test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' \
    || fail "main diverged after $b"
done

echo "===== FINAL STATE ====="
git -C "$REPO" log -12 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' || fail "main divergence"

echo
echo "OUTCOME: PF001_READY_RELATIONS_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "Integrated: R03A, R03B, R04A, R04B, R04C, R05A"
echo "Held: R02D Legge; R03 Woodruff; R03 Müller-Brockmann; R04 Lupton body-text; R04 Beier"
echo "No schema/vocabulary/Foundation changes"
