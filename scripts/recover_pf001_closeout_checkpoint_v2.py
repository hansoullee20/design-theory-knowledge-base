#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from collections import Counter, defaultdict
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "pf001-closeout"
BRANCH = "pf001-closeout"
BASE = "e6b129d1af6ce447399f6ec31aa775eb7ae4ab7a"
TARGET = Path("pilot/PILOT_RECORDS.md")
HEADING = "## PF-001-LOCATOR-RETROFIT-CLOSEOUT"

SECTION = """## PF-001-LOCATOR-RETROFIT-CLOSEOUT

- [x] PF-001 relation-level locator architecture was introduced after the immutable taxonomy-v0.1 freeze and retained backward compatibility with legacy source-ID arrays.
- [x] All canonical concept-definition and claim-source relations were re-audited after the post-freeze registry population batches.
- [x] Final canonical corpus at closeout: 79 records — 40 concepts, 11 claims, 28 sources.
- [x] Source-backed canonical records audited for locator coverage: 51.
- [x] Final locator audit: COMPLETE 51 / PARTIAL 0 / MISSING_ALL 0.
- [x] Final missing relation-level source edges: 0.
- [x] Legacy records without locators remain schema-valid by design, but no currently populated canonical concept-definition or claim-source relation remains unlocalized.
- [x] The final unresolved acuity → critical-print-size relation was not forced onto an insufficient locator: its source was corrected from Legge & Bigelow (2011) to Xiong et al. (2022), which directly supports the directional association.
- [x] Locator retrofit work did not alter proposition identity for unchanged claims.
- [x] No schema, controlled-vocabulary, predicate, locus, runtime-contract, or Foundation change was required during the retrofit closeout.
- [x] Permanent self-tests PASS; canonical checker PASS with 0 warnings; git diff --check clean.
- [x] Canonical PF-001 closure checkpoint: e6b129d (provenance: correct acuity-CPS source and close PF-001).
- [x] Outcome: PF001_LOCATOR_RETROFIT_COMPLETE.
"""

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(cwd: Path, *args: str) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def run(cwd: Path, *args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout

def expected_text(base_text: str) -> str:
    # Preserve exactly one blank line before the new heading, and exactly one
    # newline at EOF so git diff --check remains clean.
    base = base_text.rstrip("\n") + "\n\n"
    return (base + SECTION.rstrip("\n") + "\n")

def audit_pf001(root: Path) -> None:
    rows = []
    for directory, source_field, locator_field in [
        ("data/concepts", "definition_sources", "definition_source_locators"),
        ("data/claims", "sources", "source_locators"),
    ]:
        for p in sorted((root / directory).glob("*.yaml")):
            d = yaml.safe_load(p.read_text(encoding="utf-8"))
            sources = list(d.get(source_field) or [])
            if not sources:
                continue
            locators = list(d.get(locator_field) or [])
            located = defaultdict(int)
            for loc in locators:
                if isinstance(loc, dict) and isinstance(loc.get("source"), str):
                    located[loc["source"]] += 1
            n = sum(1 for sid in sources if located.get(sid, 0))
            status = "COMPLETE" if n == len(sources) else ("MISSING_ALL" if n == 0 else "PARTIAL")
            for sid in sources:
                rows.append((d["id"], sid, bool(located.get(sid, 0)), status))

    missing = [r for r in rows if not r[2]]
    record_status = {rid: status for rid, sid, located, status in rows}
    counts = Counter(record_status.values())

    print("PF001_LOCATOR_AUDIT:")
    print("  COMPLETE:", counts.get("COMPLETE", 0))
    print("  PARTIAL:", counts.get("PARTIAL", 0))
    print("  MISSING_ALL:", counts.get("MISSING_ALL", 0))
    print("  MISSING_EDGES:", len(missing))

    assert counts.get("COMPLETE", 0) == 51, counts
    assert counts.get("PARTIAL", 0) == 0, counts
    assert counts.get("MISSING_ALL", 0) == 0, counts
    assert len(missing) == 0, missing

print("===== RECOVER PF-001 CLOSEOUT TRIAL V2 =====")

if out(REPO, "git", "branch", "--show-current") != "main":
    fail("canonical repository is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main is dirty")

run(REPO, "git", "fetch", "origin", "main")
if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out(REPO, "git", "rev-parse", "HEAD") != BASE:
    fail("unexpected canonical baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))

if not WT.exists():
    fail("pf001-closeout worktree is missing; use the original closeout creator first")

if out(WT, "git", "branch", "--show-current") != BRANCH:
    fail("closeout worktree is on the wrong branch")
if out(WT, "git", "rev-parse", "HEAD") != BASE:
    fail("closeout worktree is not at the closure baseline")

staged = out(WT, "git", "diff", "--cached", "--name-only")
if staged:
    fail("closeout worktree has staged changes; refusing automatic recovery")

status = out(WT, "git", "status", "--porcelain=v1")
changed = sorted(line[2:].lstrip() for line in status.splitlines() if line)
if changed != [TARGET.as_posix()]:
    print(out(WT, "git", "status", "--short"))
    fail("dirty worktree contains changes outside the expected closeout file")

base_text = subprocess.check_output(
    ["git", "show", f"HEAD:{TARGET.as_posix()}"],
    cwd=WT,
    text=True,
)
expected = expected_text(base_text)
target = WT / TARGET
current = target.read_text(encoding="utf-8")

# Accept only the exact approved content with either the correct EOF or one
# accidental extra trailing newline from the first helper.
if current == expected:
    print("RECOVERY_STATUS: APPROVED_CLOSEOUT_DIFF_ALREADY_CLEAN")
elif current == expected + "\n":
    target.write_text(expected, encoding="utf-8")
    print("RECOVERY_STATUS: REMOVED_ONE_ACCIDENTAL_EOF_BLANK_LINE")
else:
    print("===== UNEXPECTED CLOSEOUT DIFF =====")
    print(out(WT, "git", "diff", "--", TARGET.as_posix()))
    fail("dirty closeout file differs from the approved content")

print("===== VALIDATE CLOSEOUT WORKTREE =====")
s = run(WT, sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in s:
    fail("self-test failure")

s = run(WT, sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in s:
    fail("checker failure")

run(WT, "git", "diff", "--check")

c = len(list((WT / "data/concepts").glob("*.yaml")))
k = len(list((WT / "data/claims").glob("*.yaml")))
src = len(list((WT / "data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+src} records — {c} concepts, {k} claims, {src} sources")
assert (c+k+src, c, k, src) == (79, 40, 11, 28), (c+k+src, c, k, src)

audit_pf001(WT)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: PF001_CLOSEOUT_RECOVERY_V2_PASS")
print("Changed files: 1")
print("Canonical data mutation: 0")
print("No commit or push performed")
