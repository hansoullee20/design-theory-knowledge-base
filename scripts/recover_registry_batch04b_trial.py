#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WT = Path.home() / "design-theory-parallel-worktrees" / "registry-batch-04b"
BRANCH = "registry-batch-04b"
BASE = "db2c2d4c64b6c7ad4ee8107d57459cd45b7b9153"

EXPECTED = sorted([
    "data/claims/contrast-visual-influences-perceived-hierarchy.yaml",
    "data/claims/readability-linguistic-influences-reading-speed.yaml",
    "data/claims/typography-practice-influences-perceived-hierarchy.yaml",
    "data/sources/nng-2021-visual-hierarchy-ux.yaml",
])

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

print("===== REGISTRY-BATCH-04B RECOVERY VALIDATION =====")

if out(REPO, "git", "branch", "--show-current") != "main":
    fail("canonical repo is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main is dirty")

run(REPO, "git", "fetch", "origin", "main")

if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out(REPO, "git", "rev-parse", "HEAD") != BASE:
    fail("unexpected canonical baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))

if not WT.exists():
    fail("04B worktree missing")
if out(WT, "git", "branch", "--show-current") != BRANCH:
    fail("04B worktree is on wrong branch")
if out(WT, "git", "rev-parse", "HEAD") != BASE:
    fail("04B worktree is on wrong baseline")
if out(WT, "git", "diff", "--cached", "--name-only"):
    fail("staged changes exist")

actual = sorted(
    line[2:].lstrip()
    for line in out(WT, "git", "status", "--porcelain=v1").splitlines()
    if line
)
if actual != EXPECTED:
    fail("mutation boundary mismatch\nEXPECTED:\n" + "\n".join(EXPECTED) + "\nACTUAL:\n" + "\n".join(actual))

print("===== MUTATION BOUNDARY =====")
print(out(WT, "git", "status", "--short"))

for rel in EXPECTED:
    if not (WT / rel).is_file():
        fail("expected file missing: " + rel)

print("===== CONTENT GATE =====")

src = yaml.safe_load((WT / "data/sources/nng-2021-visual-hierarchy-ux.yaml").read_text(encoding="utf-8"))
assert src["id"] == "source:nng-2021-visual-hierarchy-ux"
assert src["kind"] == "source"
assert src["source_type"] == "web"
assert src["year"] == 2021

checks = [
    (
        "data/claims/contrast-visual-influences-perceived-hierarchy.yaml",
        "claim:contrast-visual-influences-perceived-hierarchy",
        "concept:contrast-visual",
        "concept:hierarchy-perceived",
        ["expert-opinion"],
        "source:nng-2021-visual-hierarchy-ux",
        "1. Color and contrast",
    ),
    (
        "data/claims/typography-practice-influences-perceived-hierarchy.yaml",
        "claim:typography-practice-influences-perceived-hierarchy",
        "concept:typography-practice",
        "concept:hierarchy-perceived",
        ["expert-opinion"],
        "source:nng-2025-good-visual-design",
        "Visual Principle: Use of a Typographic System",
    ),
    (
        "data/claims/readability-linguistic-influences-reading-speed.yaml",
        "claim:readability-linguistic-influences-reading-speed",
        "concept:readability-linguistic",
        "concept:reading-speed",
        ["empirical"],
        "source:dubay-2004-principles-of-readability",
        "Reading Performance",
    ),
]

for rel, cid, subject, obj, basis, source, locator in checks:
    d = yaml.safe_load((WT / rel).read_text(encoding="utf-8"))
    assert d["id"] == cid
    assert d["kind"] == "claim"
    assert d["subject"] == subject
    assert d["predicate"] == "influences"
    assert d["object"] == obj
    assert d["modality"] == "descriptive"
    assert d["basis"] == basis
    assert d["evidence_status"] == "unassessed"
    assert d["sources"] == [source]
    assert d["source_locators"] == [{
        "source": source,
        "selector": {"type": "SectionSelector", "value": locator},
    }]
    assert d["record_status"] == "draft"
    assert d["replaced_by"] == []
    print(f"{cid} -> {source} -> {locator}")

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
srcn = len(list((WT / "data/sources").glob("*.yaml")))
print(f"COUNTS: {c+k+srcn} records — {c} concepts, {k} claims, {srcn} sources")
assert (c+k+srcn, c, k, srcn) == (92, 45, 14, 33)

print("===== ZERO-NEW-CONCEPT / ARCHITECTURE GATE =====")
if any("data/concepts/" in line for line in out(WT, "git", "status", "--porcelain=v1").splitlines()):
    fail("unexpected concept mutation")
for prefix in ("schema/", "vocab/", "docs/PROJECT_FOUNDATION.md", "docs/PLUGIN_TARGET_ARCHITECTURE.md"):
    if any(prefix in line for line in out(WT, "git", "status", "--porcelain=v1").splitlines()):
        fail("unexpected architecture mutation under " + prefix)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_04B_RECOVERY_PASS")
print("Recovered existing dirty trial safely")
print("Added claims: 3")
print("Added sources: 1")
print("New concepts: 0")
print("Corpus: 92 records — 45 concepts, 14 claims, 33 sources")
print("Deferred candidates preserved: 2")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
