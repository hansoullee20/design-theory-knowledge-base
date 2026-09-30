#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-04-closeout"
BRANCH = "registry-batch-04-closeout"
BASE = "16d96613fc0f8f8b534205c2701f2ace3061f955"
TARGET = Path("pilot/PILOT_RECORDS.md")
HEADING = "## REGISTRY-BATCH-04-CLOSEOUT"

SECTION = """## REGISTRY-BATCH-04A — MECHANISM CANDIDATE ADJUDICATION

- [x] Shifted Batch 04 from glossary expansion toward mechanism/claim population.
- [x] Adjudicated five candidate mechanisms against existing canonical endpoints and direct source support.
- [x] Marked three claims READY_TO_MINT:
  - claim:contrast-visual-influences-perceived-hierarchy
  - claim:typography-practice-influences-perceived-hierarchy
  - claim:readability-linguistic-influences-reading-speed
- [x] Deferred typeface legibility → reading speed because the available evidence did not justify a clean directional claim for the canonical legibility construct.
- [x] Deferred perceived saturation → figure-ground organization because the available experiment manipulated stimulus/colorimetric saturation rather than the canonical perceived-saturation construct.
- [x] Required no new concepts for the three admitted claims.
- [x] Demonstrated no representation failure and no need to reopen taxonomy architecture.
- [x] Outcome: §PASS_READ_ONLY_ADJUDICATION§.

## REGISTRY-BATCH-04B — EXISTING-ENDPOINT MECHANISM CLAIMS

- [x] Minted claim:contrast-visual-influences-perceived-hierarchy.
- [x] Minted claim:typography-practice-influences-perceived-hierarchy.
- [x] Minted claim:readability-linguistic-influences-reading-speed.
- [x] Added source:nng-2021-visual-hierarchy-ux.
- [x] Reused source:nng-2025-good-visual-design and source:dubay-2004-principles-of-readability.
- [x] Added no concepts.
- [x] Preserved conservative evidence classification and scope qualifications.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 92 records — 45 concepts, 14 claims, 33 sources.
- [x] Canonical checkpoint: e6f2f30.
- [x] Outcome: §PASS§.

## REGISTRY-BATCH-04C — GESTALT GROUPING MECHANISM ADJUDICATION

- [x] Selected three additional mechanism-first grouping relations:
  - visual similarity → perceptual grouping
  - common region → perceptual grouping
  - element connectedness → perceptual grouping
- [x] Determined that each selected mechanism required one new artifact-side concept because the needed endpoint was not already represented.
- [x] New concepts were justified only as required claim endpoints, not as standalone glossary expansion.
- [x] Reused source:wagemans-2012-gestalt-i for all three mechanisms.
- [x] Demonstrated no representation failure and no need to reopen taxonomy architecture.
- [x] Outcome: §PASS_READ_ONLY_ADJUDICATION§.

## REGISTRY-BATCH-04D — GESTALT GROUPING MECHANISMS

- [x] Minted concept:visual-similarity and claim:visual-similarity-increases-perceptual-grouping.
- [x] Minted concept:common-region and claim:common-region-influences-perceptual-grouping.
- [x] Minted concept:element-connectedness and claim:element-connectedness-influences-perceptual-grouping.
- [x] Reused source:wagemans-2012-gestalt-i with exact section locators.
- [x] Added no source records.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 98 records — 48 concepts, 17 claims, 33 sources.
- [x] Canonical checkpoint: 16d9661.
- [x] Outcome: §PASS§.

## REGISTRY-BATCH-04-CLOSEOUT

- [x] Batch 04 tested a mechanism-first population strategy rather than continued glossary-first expansion.
- [x] Batch 04 expanded the canonical corpus from 88 to 98 records.
- [x] Added 6 claims, 3 concepts, and 1 source record.
- [x] The claim/concept ratio increased from 11/45 (0.244) to 17/48 (0.354).
- [x] All three new concepts were introduced only because an admitted mechanism required an otherwise missing canonical endpoint.
- [x] Two weak or mismatched candidate mechanisms were explicitly deferred rather than forced:
  - typeface legibility → reading speed
  - perceived saturation → figure-ground organization
- [x] No representation failure was demonstrated.
- [x] No schema, controlled-vocabulary, predicate, locus, runtime-contract, or Foundation change was required.
- [x] Final Batch-04 corpus: 98 records — 48 concepts, 17 claims, 33 sources.
- [x] Final canonical checkpoint: 16d9661.
- [x] Outcome: §REGISTRY_BATCH_04_MECHANISM_EXPANSION_COMPLETE§.
""".replace("§", chr(96))

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

print("===== REGISTRY-BATCH-04 CLOSEOUT TRIAL =====")

if out(REPO, "git", "branch", "--show-current") != "main":
    fail("canonical repository is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main is dirty")

run(REPO, "git", "fetch", "origin", "main")

if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out(REPO, "git", "rev-parse", "HEAD") != BASE:
    fail("unexpected canonical baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))

WTROOT.mkdir(parents=True, exist_ok=True)

if WT.exists():
    if out(WT, "git", "branch", "--show-current") != BRANCH:
        fail("existing closeout worktree is on wrong branch")
    if out(WT, "git", "status", "--porcelain"):
        fail("existing closeout worktree is dirty")
    if out(WT, "git", "rev-parse", "HEAD") != BASE:
        fail("existing closeout worktree is on wrong baseline")
else:
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
        cwd=REPO,
    ).returncode == 0
    if branch_exists:
        fail("closeout branch exists without expected worktree")
    run(REPO, "git", "worktree", "add", "-b", BRANCH, str(WT), BASE)

target = WT / TARGET
text = target.read_text(encoding="utf-8")

if HEADING in text:
    fail("Batch 04 closeout already exists")

text = text.rstrip("\n") + "\n\n" + SECTION.rstrip("\n") + "\n"
target.write_text(text, encoding="utf-8")

actual = sorted(
    line[2:].lstrip()
    for line in out(WT, "git", "status", "--porcelain=v1").splitlines()
    if line
)
if actual != [TARGET.as_posix()]:
    fail("mutation boundary mismatch: " + repr(actual))

print("===== VALIDATION =====")
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
assert (c+k+src, c, k, src) == (98, 48, 17, 33)

before_ratio = 11 / 45
after_ratio = k / c
print(f"CLAIM/CONCEPT RATIO: {before_ratio:.3f} -> {after_ratio:.3f}")
assert round(before_ratio, 3) == 0.244
assert round(after_ratio, 3) == 0.354

print("===== ZERO-CANONICAL-DATA-MUTATION GATE =====")
for prefix in ("data", "schema", "vocab", "docs/PROJECT_FOUNDATION.md", "docs/PLUGIN_TARGET_ARCHITECTURE.md"):
    if subprocess.run(["git", "diff", "--quiet", "--", prefix], cwd=WT).returncode != 0:
        fail("unexpected closeout mutation under " + prefix)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_04_CLOSEOUT_TRIAL_PASS")
print("Changed files: 1")
print("Canonical data mutation: 0")
print("Batch 04 added: 6 claims, 3 concepts, 1 source")
print("Claim/concept ratio: 0.244 -> 0.354")
print("Deferred mechanism candidates preserved: 2")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
