#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-04d"
BRANCH = "registry-batch-04d"
BASE = "e6f2f3083b620e66f43c416e732aba6f74fa529f"
SOURCE = "source:wagemans-2012-gestalt-i"

CONCEPTS = {
    "data/concepts/visual-similarity.yaml": {
        "id": "concept:visual-similarity",
        "kind": "concept",
        "label": "Visual similarity",
        "aliases": ["similarity"],
        "definition": "The degree to which visual elements are alike in perceptible features such as color, size, or orientation.",
        "definition_sources": [SOURCE],
        "definition_source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.1 Introduction"},
        }],
        "locus": ["artifact"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science"],
        "traditions": ["gestalt"],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Artifact-side similarity relation used in visual perceptual-grouping mechanisms. Distinct from the viewer's resulting grouping experience.",
        "schema_version": "0.1",
    },
    "data/concepts/common-region.yaml": {
        "id": "concept:common-region",
        "kind": "concept",
        "label": "Common region",
        "aliases": [],
        "definition": "An arrangement in which visual elements lie within the same bounded region.",
        "definition_sources": [SOURCE],
        "definition_source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.2.3 Common region"},
        }],
        "locus": ["artifact"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science"],
        "traditions": ["gestalt"],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Artifact-side grouping cue: elements share a bounded visual region. The perceptual grouping that may result remains a separate experience-locus concept.",
        "schema_version": "0.1",
    },
    "data/concepts/element-connectedness.yaml": {
        "id": "concept:element-connectedness",
        "kind": "concept",
        "label": "Element connectedness",
        "aliases": ["connectedness"],
        "definition": "The visual connectedness of otherwise distinct elements through a shared border or explicit connection.",
        "definition_sources": [SOURCE],
        "definition_source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.2.4 Element connectedness"},
        }],
        "locus": ["artifact"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science"],
        "traditions": ["gestalt"],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Artifact-side connectedness cue. Kept distinct from perceptual grouping as the resulting experience.",
        "schema_version": "0.1",
    },
}

CLAIMS = {
    "data/claims/visual-similarity-increases-perceptual-grouping.yaml": {
        "id": "claim:visual-similarity-increases-perceptual-grouping",
        "kind": "claim",
        "statement": "All else equal, greater visual similarity among elements tends to increase their perceptual grouping.",
        "modality": "descriptive",
        "subject": "concept:visual-similarity",
        "predicate": "increases",
        "object": "concept:perceptual-grouping",
        "basis": ["empirical", "theoretical"],
        "evidence_status": "unassessed",
        "scope": "Visual grouping of discrete elements. Similarity may be carried by features such as color, size, or orientation, and its grouping effect can interact with competing grouping cues.",
        "sources": [SOURCE],
        "source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.1 Introduction"},
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04D adds a mechanism-first artifact-to-experience claim using the general Gestalt similarity principle.",
        "schema_version": "0.1",
    },
    "data/claims/common-region-influences-perceptual-grouping.yaml": {
        "id": "claim:common-region-influences-perceptual-grouping",
        "kind": "claim",
        "statement": "Placing visual elements within the same bounded region can influence their perceptual grouping.",
        "modality": "descriptive",
        "subject": "concept:common-region",
        "predicate": "influences",
        "object": "concept:perceptual-grouping",
        "basis": ["empirical", "theoretical"],
        "evidence_status": "unassessed",
        "scope": "Visual elements arranged within bounded regions. The grouping effect can interact with other grouping cues and is not asserted as universal or quantitatively constant.",
        "sources": [SOURCE],
        "source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.2.3 Common region"},
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04D represents common region as an artifact-side grouping cue and perceptual grouping as the experience-side outcome.",
        "schema_version": "0.1",
    },
    "data/claims/element-connectedness-influences-perceptual-grouping.yaml": {
        "id": "claim:element-connectedness-influences-perceptual-grouping",
        "kind": "claim",
        "statement": "Visually connecting otherwise distinct elements can influence their perceptual grouping.",
        "modality": "descriptive",
        "subject": "concept:element-connectedness",
        "predicate": "influences",
        "object": "concept:perceptual-grouping",
        "basis": ["empirical", "theoretical"],
        "evidence_status": "unassessed",
        "scope": "Discrete visual elements connected through shared borders or explicit visual connections. The grouping effect can interact with other cues and is not asserted as universal or quantitatively constant.",
        "sources": [SOURCE],
        "source_locators": [{
            "source": SOURCE,
            "selector": {"type": "SectionSelector", "value": "3.2.4 Element connectedness"},
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04D adds a mechanism-first artifact-to-experience claim for element connectedness.",
        "schema_version": "0.1",
    },
}

EXPECTED = sorted([*CONCEPTS.keys(), *CLAIMS.keys()])

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

def dump(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )

print("===== REGISTRY-BATCH-04D TRIAL =====")

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
        fail("existing 04D worktree is on wrong branch")
    if out(WT, "git", "status", "--porcelain"):
        fail("existing 04D worktree is dirty")
    if out(WT, "git", "rev-parse", "HEAD") != BASE:
        fail("existing 04D worktree is on wrong baseline")
else:
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
        cwd=REPO,
    ).returncode == 0
    if branch_exists:
        fail("04D branch exists without expected worktree")
    run(REPO, "git", "worktree", "add", "-b", BRANCH, str(WT), BASE)

print("===== COLLISION / REUSE GATE =====")

for rel in (
    "data/concepts/perceptual-grouping.yaml",
    "data/sources/wagemans-2012-gestalt-i.yaml",
):
    if not (WT / rel).exists():
        fail("required existing record missing: " + rel)

for rel in EXPECTED:
    if (WT / rel).exists():
        fail("candidate path already exists: " + rel)

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (WT / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

for candidate_id in [*(x["id"] for x in CONCEPTS.values()), *(x["id"] for x in CLAIMS.values())]:
    if candidate_id in existing_ids:
        fail("candidate ID already exists: " + candidate_id)

print("===== APPLY BOUNDED MUTATION =====")

for rel, obj in CONCEPTS.items():
    dump(WT / rel, obj)
for rel, obj in CLAIMS.items():
    dump(WT / rel, obj)

actual = sorted(
    line[2:].lstrip()
    for line in out(WT, "git", "status", "--porcelain=v1").splitlines()
    if line
)
if actual != EXPECTED:
    fail(
        "mutation boundary mismatch\nEXPECTED:\n"
        + "\n".join(EXPECTED)
        + "\nACTUAL:\n"
        + "\n".join(actual)
    )

print("===== MUTATION BOUNDARY =====")
print(out(WT, "git", "status", "--short"))

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
if (c+k+src, c, k, src) != (98, 48, 17, 33):
    fail(f"unexpected corpus counts: {(c+k+src,c,k,src)}")

print("===== SEMANTIC / LOCATOR GATE =====")

concept_checks = [
    ("data/concepts/visual-similarity.yaml", "concept:visual-similarity", "3.1 Introduction"),
    ("data/concepts/common-region.yaml", "concept:common-region", "3.2.3 Common region"),
    ("data/concepts/element-connectedness.yaml", "concept:element-connectedness", "3.2.4 Element connectedness"),
]
for rel, cid, locator in concept_checks:
    d = yaml.safe_load((WT / rel).read_text(encoding="utf-8"))
    assert d["id"] == cid
    assert d["locus"] == ["artifact"]
    assert d["knowledge_origin"] == ["perceptual-science"]
    assert d["traditions"] == ["gestalt"]
    assert d["definition_sources"] == [SOURCE]
    assert d["definition_source_locators"] == [{
        "source": SOURCE,
        "selector": {"type": "SectionSelector", "value": locator},
    }]
    print(f"{cid} -> {SOURCE} -> {locator}")

claim_checks = [
    (
        "data/claims/visual-similarity-increases-perceptual-grouping.yaml",
        "claim:visual-similarity-increases-perceptual-grouping",
        "concept:visual-similarity",
        "increases",
        "3.1 Introduction",
    ),
    (
        "data/claims/common-region-influences-perceptual-grouping.yaml",
        "claim:common-region-influences-perceptual-grouping",
        "concept:common-region",
        "influences",
        "3.2.3 Common region",
    ),
    (
        "data/claims/element-connectedness-influences-perceptual-grouping.yaml",
        "claim:element-connectedness-influences-perceptual-grouping",
        "concept:element-connectedness",
        "influences",
        "3.2.4 Element connectedness",
    ),
]
for rel, cid, subject, predicate, locator in claim_checks:
    d = yaml.safe_load((WT / rel).read_text(encoding="utf-8"))
    assert d["id"] == cid
    assert d["subject"] == subject
    assert d["predicate"] == predicate
    assert d["object"] == "concept:perceptual-grouping"
    assert d["modality"] == "descriptive"
    assert d["basis"] == ["empirical", "theoretical"]
    assert d["evidence_status"] == "unassessed"
    assert d["sources"] == [SOURCE]
    assert d["source_locators"] == [{
        "source": SOURCE,
        "selector": {"type": "SectionSelector", "value": locator},
    }]
    print(f"{cid} -> {SOURCE} -> {locator}")

print("===== ZERO-NEW-SOURCE / ARCHITECTURE GATE =====")
if any("data/sources/" in line for line in out(WT, "git", "status", "--porcelain=v1").splitlines()):
    fail("04D unexpectedly adds source records")
for forbidden in (
    "schema",
    "vocab",
    "docs/PROJECT_FOUNDATION.md",
    "docs/PLUGIN_TARGET_ARCHITECTURE.md",
):
    if subprocess.run(["git", "diff", "--quiet", "--", forbidden], cwd=WT).returncode != 0:
        fail("forbidden mutation under " + forbidden)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_04D_TRIAL_PASS")
print("Added concepts: 3")
print("Added claims: 3")
print("Added sources: 0")
print("Reused sources: 1")
print("Corpus: 98 records — 48 concepts, 17 claims, 33 sources")
print("Representation failure: 0")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
