#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WTROOT="$HOME/design-theory-parallel-worktrees"
BASE="3185887aa4eb3f242a067a0998b3dd3b9b72bbcc"

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

residual_audit() {
  local dir="$1"
  (
    cd "$dir"
    python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import yaml

rows=[]
for kind, directory, src_field, loc_field in [
    ("concept","data/concepts","definition_sources","definition_source_locators"),
    ("claim","data/claims","sources","source_locators"),
]:
    for p in sorted(Path(directory).glob("*.yaml")):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        sources=list(d.get(src_field) or [])
        if not sources:
            continue
        locs=list(d.get(loc_field) or [])
        located=defaultdict(int)
        for loc in locs:
            if isinstance(loc,dict) and isinstance(loc.get("source"),str):
                located[loc["source"]]+=1
        n=sum(1 for sid in sources if located.get(sid,0))
        status="COMPLETE" if n==len(sources) else ("MISSING_ALL" if n==0 else "PARTIAL")
        for sid in sources:
            rows.append((d["id"],sid,bool(located.get(sid,0)),status))

missing=[r for r in rows if not r[2]]
by_source=defaultdict(list)
record_status={}
for rid,sid,located,status in rows:
    record_status[rid]=status
    if not located:
        by_source[sid].append(rid)

print("REMAINING_MISSING_EDGES:", len(missing))
print("REMAINING_SOURCES:", len(by_source))
for sid in sorted(by_source):
    print(sid)
    for rid in sorted(by_source[sid]):
        print("  -", rid)

counts=Counter(record_status.values())
print("RECORD_STATUS_COUNTS:")
for key in ("COMPLETE","PARTIAL","MISSING_ALL"):
    print(f"  {key}: {counts.get(key,0)}")

expected={
 "source:legge-bigelow-2011-print-size":{
   "claim:visual-acuity-influences-critical-print-size",
 }
}
actual={sid:set(rids) for sid,rids in by_source.items()}

assert len(missing)==1, len(missing)
assert len(by_source)==1, len(by_source)
assert actual==expected, (actual,expected)
assert counts.get("COMPLETE",0)==50, counts
assert counts.get("PARTIAL",0)==0, counts
assert counts.get("MISSING_ALL",0)==1, counts

print("RESIDUAL_AUDIT: PASS")
PY
  )
}

declare -a BRANCHES=(
  pf001-r07a
  pf001-r07b
  pf001-r07c
  pf001-r07d
)

commit_message() {
  case "$1" in
    pf001-r07a) echo "provenance: backfill Muller-Brockmann grid locators PF001-R07A" ;;
    pf001-r07b) echo "provenance: backfill Beier legibility locator PF001-R07B" ;;
    pf001-r07c) echo "provenance: backfill Lupton body-text locator PF001-R07C" ;;
    pf001-r07d) echo "provenance: backfill Woodruff density locator PF001-R07D" ;;
    *) fail "unknown branch $1" ;;
  esac
}

stage_branch() {
  local branch="$1"
  local wt="$WTROOT/$branch"
  case "$branch" in
    pf001-r07a)
      git -C "$wt" add \
        data/concepts/grid.yaml \
        data/concepts/grid-column.yaml \
        data/concepts/gutter.yaml \
        data/concepts/modular-grid.yaml
      ;;
    pf001-r07b)
      git -C "$wt" add data/concepts/legibility-typeface.yaml
      ;;
    pf001-r07c)
      git -C "$wt" add data/concepts/body-text.yaml
      ;;
    pf001-r07d)
      git -C "$wt" add data/concepts/display-object-density.yaml
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
check_boundary "$WTROOT/pf001-r07a" \
  data/concepts/grid-column.yaml \
  data/concepts/grid.yaml \
  data/concepts/gutter.yaml \
  data/concepts/modular-grid.yaml

check_boundary "$WTROOT/pf001-r07b" \
  data/concepts/legibility-typeface.yaml

check_boundary "$WTROOT/pf001-r07c" \
  data/concepts/body-text.yaml

check_boundary "$WTROOT/pf001-r07d" \
  data/concepts/display-object-density.yaml

echo "===== PRE-COMMIT VALIDATION ====="
for b in "${BRANCHES[@]}"; do
  echo "--- $b"
  validate_repo "$WTROOT/$b"
done

echo "===== CHECKPOINT ALL R07 BRANCHES ====="
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

echo "===== FINAL RESIDUAL PF-001 AUDIT ====="
residual_audit "$REPO"

echo "===== FINAL STATE ====="
git -C "$REPO" log -12 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' || fail "main divergence"

echo
echo "OUTCOME: PF001_R07ABCD_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "Integrated: Muller-Brockmann (4), Beier (1), Lupton body-text (1), Woodruff (1)"
echo "Residual PF-001 backlog: 1 edge across 1 source"
echo "Held: claim:visual-acuity-influences-critical-print-size -> source:legge-bigelow-2011-print-size"
echo "No schema/vocabulary/Foundation changes"
