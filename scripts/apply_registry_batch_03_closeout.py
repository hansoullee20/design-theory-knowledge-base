#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-03-closeout"
BRANCH = "registry-batch-03-closeout"
BASE = "5eac79107c0ef5833ddcc427f76a1789a43a2907"
TARGET = Path("pilot/PILOT_RECORDS.md")
HEADING = "## REGISTRY-BATCH-03-CLOSEOUT"

SECTION = """## REGISTRY-BATCH-03B — DEFERRED FUNDAMENTALS ADJUDICATION

- [x] Adjudicated the deferred lexical candidates form, color, balance, typography, and feedback without canonical mutation.
- [x] Determined that bare form, color, balance, typography, and feedback should not be assumed to identify one unqualified canonical sense.
- [x] Marked concept:form-compositional, concept:visual-balance-perceived, and concept:typography-practice READY_TO_MINT.
- [x] Marked color and feedback SPLIT_REQUIRED.
- [x] Demonstrated no representation failure and no need to reopen taxonomy architecture.
- [x] Outcome: §PASS_READ_ONLY_ADJUDICATION§.

## REGISTRY-BATCH-03C — FORM, BALANCE, AND TYPOGRAPHY

- [x] Minted concept:form-compositional with locus artifact.
- [x] Minted concept:visual-balance-perceived with locus experience.
- [x] Minted concept:typography-practice with locus practice.
- [x] Added Getty AAT sources 300056272, 300056247, and 300195853 with exact Note (English) locators.
- [x] Added no claims.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 85 records — 43 concepts, 11 claims, 31 sources.
- [x] Canonical checkpoint: af3d86b.
- [x] Outcome: §PASS§.

## REGISTRY-BATCH-03D/03E — COLOR AND FEEDBACK SENSE ADJUDICATION

- [x] Adjudicated perceived color separately from psychophysical color.
- [x] Marked concept:color-perceived READY_TO_MINT using CIE S 017:2020 e-ILV term 17-22-040.
- [x] Deferred psychophysical color because no active competency question requires the sense and its locus remains intentionally unforced.
- [x] Adjudicated interaction feedback separately from status-message feedback and evaluative/design-process feedback.
- [x] Marked concept:interaction-feedback READY_TO_MINT with artifact locus.
- [x] Deferred status-message feedback as a narrower future subtype.
- [x] Deferred evaluative/design-process feedback as a distinct practice-level sense.
- [x] Bare concept:color and concept:feedback were not minted.
- [x] Demonstrated no representation failure and no need to reopen taxonomy architecture.
- [x] Outcome: §PASS_READ_ONLY_ADJUDICATION§.

## REGISTRY-BATCH-03F — PERCEIVED COLOR AND INTERACTION FEEDBACK

- [x] Minted concept:color-perceived with locus experience.
- [x] Reused source:cie-s017-2020-ilv with exact term locator 17-22-040 perceived colour.
- [x] Minted concept:interaction-feedback with locus artifact.
- [x] Added source:w3c-coga-provide-feedback with exact section locator More Details.
- [x] Added no claims.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 88 records — 45 concepts, 11 claims, 32 sources.
- [x] Canonical checkpoint: 5eac791.
- [x] Outcome: §PASS§.

## REGISTRY-BATCH-03-CLOSEOUT

- [x] Batch 03 expanded the post-freeze fundamentals registry from 78 to 88 canonical records.
- [x] Added 5 concepts across the deferred-fundamentals sequence: form-compositional, visual-balance-perceived, typography-practice, color-perceived, and interaction-feedback.
- [x] Added 4 source records and reused the existing CIE S 017:2020 source for perceived color.
- [x] Added no claims during Batch 03.
- [x] Sense adjudication prevented bare lexical IDs for form, balance, typography, color, and feedback where ambiguity required qualification.
- [x] Deferred senses remain explicit rather than forced: psychophysical color, status-message feedback, and evaluative/design-process feedback.
- [x] No representation failure was demonstrated.
- [x] No schema, controlled-vocabulary, predicate, locus, runtime-contract, or Foundation change was required.
- [x] Final Batch-03 corpus: 88 records — 45 concepts, 11 claims, 32 sources.
- [x] Final canonical checkpoint: 5eac791.
- [x] Outcome: §REGISTRY_BATCH_03_COMPLETE_WITH_DEFERRED_SENSES§.
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

print("===== REGISTRY-BATCH-03 CLOSEOUT TRIAL =====")

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
    fail("Batch 03 closeout already exists")

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
assert (c+k+src, c, k, src) == (88, 45, 11, 32)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_03_CLOSEOUT_TRIAL_PASS")
print("Changed files: 1")
print("Canonical data mutation: 0")
print("Deferred senses preserved: 3")
print("No commit or push performed")
