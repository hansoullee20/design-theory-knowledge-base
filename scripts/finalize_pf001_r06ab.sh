#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WTROOT="$HOME/design-theory-parallel-worktrees"
BASE="b91fa0192e409e1892b4407809637791b2bfafa3"

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

assert len(missing)==8, len(missing)
assert len(by_source)==5, len(by_source)
assert counts.get("COMPLETE",0)==43, counts
assert counts.get("PARTIAL",0)==1, counts
assert counts.get("MISSING_ALL",0)==7, counts

expected={
 "source:legge-bigelow-2011-print-size":{
   "claim:visual-acuity-influences-critical-print-size",
 },
 "source:muller-brockmann-1981-grid-systems":{
   "concept:grid","concept:grid-column","concept:gutter","concept:modular-grid",
 },
 "source:beier-2012-reading-letters":{"concept:legibility-typeface"},
 "source:lupton-2010-thinking-with-type":{"concept:body-text"},
 "source:woodruff-landay-stonebraker-1998-density":{"concept:display-object-density"},
}
actual={sid:set(rids) for sid,rids in by_source.items()}
assert actual==expected, (actual,expected)

print("RESIDUAL_AUDIT: PASS")
PY
  )
}

A="$WTROOT/pf001-r06a"
B="$WTROOT/pf001-r06b"

echo "===== PRECHECK MAIN ====="
test -d "$REPO/.git" || fail "missing repo $REPO"
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" branch --show-current)" = "main" || fail "repo not on main"
test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main differs from origin/main"
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE" || fail "unexpected main baseline"

echo "===== PRECHECK WORKTREES ====="
for pair in "pf001-r06a:$A" "pf001-r06b:$B"; do
  b="${pair%%:*}"
  wt="${pair#*:}"
  test -d "$wt" || fail "missing worktree $wt"
  test "$(git -C "$wt" branch --show-current)" = "$b" || fail "$b wrong branch"
  test "$(git -C "$wt" rev-parse HEAD)" = "$BASE" || fail "$b wrong base"
done

echo "===== VERIFY MUTATION BOUNDARIES ====="
check_boundary "$A" \
  data/concepts/contrast-ratio.yaml \
  data/concepts/visual-presentation-of-text.yaml \
  data/sources/w3c-wcag-2-2.yaml

check_boundary "$B" \
  data/claims/print-size-influences-reading-speed.yaml \
  data/concepts/critical-print-size.yaml \
  data/concepts/legibility-typeface.yaml \
  data/concepts/print-size.yaml \
  data/concepts/reading-speed.yaml \
  data/concepts/visual-acuity.yaml

echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$A"
validate_repo "$B"

echo "===== COMMIT + PUSH R06A ====="
git -C "$A" add \
  data/concepts/contrast-ratio.yaml \
  data/concepts/visual-presentation-of-text.yaml \
  data/sources/w3c-wcag-2-2.yaml
git -C "$A" diff --cached --check
git -C "$A" commit -m "provenance: backfill WCAG locators PF001-R06A"
git -C "$A" push -u origin pf001-r06a

echo "===== COMMIT + PUSH R06B ====="
git -C "$B" add \
  data/claims/print-size-influences-reading-speed.yaml \
  data/concepts/critical-print-size.yaml \
  data/concepts/legibility-typeface.yaml \
  data/concepts/print-size.yaml \
  data/concepts/reading-speed.yaml \
  data/concepts/visual-acuity.yaml
git -C "$B" diff --cached --check
git -C "$B" commit -m "provenance: backfill Legge print-size locators PF001-R06B"
git -C "$B" push -u origin pf001-r06b

echo "===== INTEGRATE R06A ====="
git -C "$REPO" fetch origin main pf001-r06a
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before R06A integration"
git -C "$REPO" merge --ff-only pf001-r06a
validate_repo "$REPO"
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== REBASE + INTEGRATE R06B ====="
OLD_B_REMOTE="$(git -C "$REPO" rev-parse origin/pf001-r06b)"
git -C "$B" fetch origin main
git -C "$B" rebase origin/main
validate_repo "$B"
git -C "$B" push \
  --force-with-lease="refs/heads/pf001-r06b:$OLD_B_REMOTE" \
  origin pf001-r06b

git -C "$REPO" fetch origin main pf001-r06b
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before R06B integration"
git -C "$REPO" merge --ff-only pf001-r06b
validate_repo "$REPO"
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== RESIDUAL PF-001 AUDIT ====="
residual_audit "$REPO"

echo "===== FINAL STATE ====="
git -C "$REPO" log -10 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' || fail "main divergence"

echo
echo "OUTCOME: PF001_R06AB_INTEGRATED"
echo "Corpus: 78 records — 40 concepts, 11 claims, 27 sources"
echo "Integrated: R06A WCAG (2 edges), R06B Legge (6 edges)"
echo "Residual PF-001 backlog: 8 edges across 5 sources"
echo "Held: Legge claim (1); Muller-Brockmann (4); Beier (1); Lupton body-text (1); Woodruff (1)"
echo "No schema/vocabulary/Foundation changes"
