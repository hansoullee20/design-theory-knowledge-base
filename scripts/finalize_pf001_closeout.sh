#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/design-theory-knowledge-base"
WT="$HOME/design-theory-parallel-worktrees/pf001-closeout"
BRANCH="pf001-closeout"
BASE="e6b129d1af6ce447399f6ec31aa775eb7ae4ab7a"
TARGET="pilot/PILOT_RECORDS.md"
HEADING="## PF-001-LOCATOR-RETROFIT-CLOSEOUT"

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
assert (c+k+s,c,k,s)==(79,40,11,28), (c+k+s,c,k,s)
PY
  )
}

audit_pf001() {
  local dir="$1"
  (
    cd "$dir"
    python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import yaml

rows=[]
for directory, source_field, locator_field in [
    ("data/concepts","definition_sources","definition_source_locators"),
    ("data/claims","sources","source_locators"),
]:
    for p in sorted(Path(directory).glob("*.yaml")):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        sources=list(d.get(source_field) or [])
        if not sources:
            continue
        locators=list(d.get(locator_field) or [])
        located=defaultdict(int)
        for loc in locators:
            if isinstance(loc,dict) and isinstance(loc.get("source"),str):
                located[loc["source"]]+=1
        n=sum(1 for sid in sources if located.get(sid,0))
        status="COMPLETE" if n==len(sources) else ("MISSING_ALL" if n==0 else "PARTIAL")
        for sid in sources:
            rows.append((d["id"],sid,bool(located.get(sid,0)),status))

missing=[r for r in rows if not r[2]]
record_status={rid:status for rid,sid,located,status in rows}
counts=Counter(record_status.values())

print("PF001_LOCATOR_AUDIT:")
print("  COMPLETE:", counts.get("COMPLETE",0))
print("  PARTIAL:", counts.get("PARTIAL",0))
print("  MISSING_ALL:", counts.get("MISSING_ALL",0))
print("  MISSING_EDGES:", len(missing))

assert counts.get("COMPLETE",0)==51, counts
assert counts.get("PARTIAL",0)==0, counts
assert counts.get("MISSING_ALL",0)==0, counts
assert len(missing)==0, missing

print("PF001_LOCATOR_COVERAGE: COMPLETE")
PY
  )
}

echo "===== PRECHECK MAIN ====="
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" branch --show-current)" = "main" || fail "canonical repo not on main"
test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "local main differs from origin/main"
test "$(git -C "$REPO" rev-parse HEAD)" = "$BASE" || fail "unexpected main baseline"

echo "===== PRECHECK CLOSEOUT WORKTREE ====="
test -d "$WT" || fail "missing closeout worktree"
test "$(git -C "$WT" branch --show-current)" = "$BRANCH" || fail "closeout worktree on wrong branch"
test "$(git -C "$WT" rev-parse HEAD)" = "$BASE" || fail "closeout worktree on wrong baseline"
test -z "$(git -C "$WT" diff --cached --name-only)" || fail "unexpected staged changes"

ACTUAL="$(git -C "$WT" status --porcelain=v1 | sed 's/^.. //' | sort)"
test "$ACTUAL" = "$TARGET" || {
  echo "ACTUAL:"
  printf '%s\n' "$ACTUAL"
  fail "closeout mutation boundary mismatch"
}

grep -Fqx "$HEADING" "$WT/$TARGET" || fail "closeout heading missing"

COUNT="$(grep -Fxc "$HEADING" "$WT/$TARGET")"
test "$COUNT" = "1" || fail "closeout heading duplicated"

echo "===== PRE-COMMIT VALIDATION ====="
validate_repo "$WT"
audit_pf001 "$WT"

echo "===== COMMIT CLOSEOUT ====="
git -C "$WT" add "$TARGET"
git -C "$WT" diff --cached --check

git -C "$WT" commit -m "governance: record PF-001 locator retrofit closeout"

CLOSEOUT_SHA="$(git -C "$WT" rev-parse HEAD)"
echo "CLOSEOUT_SHA: $CLOSEOUT_SHA"

echo "===== PUSH CLOSEOUT BRANCH ====="
git -C "$WT" push -u origin "$BRANCH"

echo "===== INTEGRATE INTO MAIN ====="
git -C "$REPO" fetch origin main "$BRANCH"
test "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" || fail "main moved before closeout integration"

git -C "$REPO" merge --ff-only "$BRANCH"

echo "===== FINAL CANONICAL VALIDATION ====="
validate_repo "$REPO"
audit_pf001 "$REPO"

echo "===== PUSH MAIN ====="
git -C "$REPO" push origin main
git -C "$REPO" fetch origin main

echo "===== FINAL STATE ====="
git -C "$REPO" log -8 --oneline --decorate
git -C "$REPO" status --short
git -C "$REPO" rev-list --left-right --count origin/main...HEAD

test -z "$(git -C "$REPO" status --porcelain)" || fail "main is dirty"
test "$(git -C "$REPO" rev-list --left-right --count origin/main...HEAD)" = $'0\t0' || fail "main divergence"

echo
echo "OUTCOME: PF001_CLOSEOUT_INTEGRATED"
echo "Corpus: 79 records — 40 concepts, 11 claims, 28 sources"
echo "PF-001 locator coverage: COMPLETE"
echo "Governance closeout recorded in pilot/PILOT_RECORDS.md"
echo "Canonical data mutation in closeout commit: 0"
echo "No schema/vocabulary/Foundation changes"
