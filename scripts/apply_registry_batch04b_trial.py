#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-04b"
BRANCH = "registry-batch-04b"
BASE = "db2c2d4c64b6c7ad4ee8107d57459cd45b7b9153"

SOURCE_PATH = "data/sources/nng-2021-visual-hierarchy-ux.yaml"
SOURCE = {
    "id": "source:nng-2021-visual-hierarchy-ux",
    "kind": "source",
    "citation": "Gordon, Kelley. Visual Hierarchy in UX: Definition. Nielsen Norman Group, 17 January 2021.",
    "source_type": "web",
    "year": 2021,
    "identifier": "",
    "notes": "Design-practice guidance describing how color and contrast, scale, and grouping can create visual hierarchy. Used as expert-opinion support rather than quantified empirical effect-size evidence.",
    "schema_version": "0.1",
}

CLAIMS = {
    "data/claims/contrast-visual-influences-perceived-hierarchy.yaml": {
        "id": "claim:contrast-visual-influences-perceived-hierarchy",
        "kind": "claim",
        "statement": "Differences in visual contrast can influence the visual hierarchy that viewers perceive in a two-dimensional design.",
        "modality": "descriptive",
        "subject": "concept:contrast-visual",
        "predicate": "influences",
        "object": "concept:hierarchy-perceived",
        "basis": ["expert-opinion"],
        "evidence_status": "unassessed",
        "scope": "Design-practice guidance for two-dimensional interface, graphic, and print layouts. The cited source describes color and contrast as means of creating hierarchy and directing attention. This claim does not assert a quantified effect size, universal causal law, or equivalence between all forms of contrast.",
        "sources": ["source:nng-2021-visual-hierarchy-ux"],
        "source_locators": [{
            "source": "source:nng-2021-visual-hierarchy-ux",
            "selector": {
                "type": "SectionSelector",
                "value": "1. Color and contrast",
            },
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04B connects an existing artifact-locus contrast concept to an existing experience-locus hierarchy concept without introducing a new hierarchy construct.",
        "schema_version": "0.1",
    },
    "data/claims/typography-practice-influences-perceived-hierarchy.yaml": {
        "id": "claim:typography-practice-influences-perceived-hierarchy",
        "kind": "claim",
        "statement": "Typographic choices made in typography practice, including relative size and weight, can influence the visual hierarchy that viewers perceive.",
        "modality": "descriptive",
        "subject": "concept:typography-practice",
        "predicate": "influences",
        "object": "concept:hierarchy-perceived",
        "basis": ["expert-opinion"],
        "evidence_status": "unassessed",
        "scope": "Design-practice guidance for typographic choices in visual and interface layouts. The cited source describes a typographic system as establishing visual hierarchy through choices such as size and weight. The claim is not a universal effect of every typography practice and does not assert a quantified causal magnitude.",
        "sources": ["source:nng-2025-good-visual-design"],
        "source_locators": [{
            "source": "source:nng-2025-good-visual-design",
            "selector": {
                "type": "SectionSelector",
                "value": "Visual Principle: Use of a Typographic System",
            },
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04B adds a practice-to-experience mechanism claim using existing endpoints; artifact-side typographic properties remain separate concepts.",
        "schema_version": "0.1",
    },
    "data/claims/readability-linguistic-influences-reading-speed.yaml": {
        "id": "claim:readability-linguistic-influences-reading-speed",
        "kind": "claim",
        "statement": "Differences in linguistic readability can influence reading speed under specified reading conditions.",
        "modality": "descriptive",
        "subject": "concept:readability-linguistic",
        "predicate": "influences",
        "object": "concept:reading-speed",
        "basis": ["empirical"],
        "evidence_status": "unassessed",
        "scope": "Applies to specified reader populations, texts, and reading tasks reviewed in the cited source. Reading performance also depends on reader ability, prior knowledge, interest, motivation, and other text variables. This claim does not assert a universal monotonic relationship or a single effect size across populations and tasks.",
        "sources": ["source:dubay-2004-principles-of-readability"],
        "source_locators": [{
            "source": "source:dubay-2004-principles-of-readability",
            "selector": {
                "type": "SectionSelector",
                "value": "Reading Performance",
            },
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-04B connects the canonical reader-relative linguistic-readability construct to the existing reading-speed outcome while preserving contextual dependence in scope.",
        "schema_version": "0.1",
    },
}

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

print("===== REGISTRY-BATCH-04B TRIAL =====")

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
        fail("existing 04B worktree is on wrong branch")
    if out(WT, "git", "status", "--porcelain"):
        fail("existing 04B worktree is dirty")
    if out(WT, "git", "rev-parse", "HEAD") != BASE:
        fail("existing 04B worktree is on wrong baseline")
else:
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
        cwd=REPO,
    ).returncode == 0
    if branch_exists:
        fail("04B branch exists without expected worktree")
    run(REPO, "git", "worktree", "add", "-b", BRANCH, str(WT), BASE)

print("===== COLLISION / REUSE GATE =====")

required_existing = [
    "data/concepts/contrast-visual.yaml",
    "data/concepts/hierarchy-perceived.yaml",
    "data/concepts/typography-practice.yaml",
    "data/concepts/readability-linguistic.yaml",
    "data/concepts/reading-speed.yaml",
    "data/sources/nng-2025-good-visual-design.yaml",
    "data/sources/dubay-2004-principles-of-readability.yaml",
]

for rel in required_existing:
    if not (WT / rel).exists():
        fail("required existing record missing: " + rel)

for rel in [SOURCE_PATH, *CLAIMS.keys()]:
    if (WT / rel).exists():
        fail("candidate path already exists: " + rel)

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (WT / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

for candidate_id in [SOURCE["id"], *(obj["id"] for obj in CLAIMS.values())]:
    if candidate_id in existing_ids:
        fail("candidate ID already exists: " + candidate_id)

print("===== APPLY BOUNDED MUTATION =====")

dump(WT / SOURCE_PATH, SOURCE)
for rel, obj in CLAIMS.items():
    dump(WT / rel, obj)

expected = sorted([SOURCE_PATH, *CLAIMS.keys()])
actual = sorted(
    line[2:].lstrip()
    for line in out(WT, "git", "status", "--porcelain=v1").splitlines()
    if line
)

if actual != expected:
    fail(
        "mutation boundary mismatch\nEXPECTED:\n"
        + "\n".join(expected)
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
if (c+k+src, c, k, src) != (92, 45, 14, 33):
    fail(f"unexpected corpus counts: {(c+k+src,c,k,src)}")

print("===== SEMANTIC / LOCATOR GATE =====")

checks = [
    (
        "data/claims/contrast-visual-influences-perceived-hierarchy.yaml",
        "concept:contrast-visual",
        "concept:hierarchy-perceived",
        "expert-opinion",
        "source:nng-2021-visual-hierarchy-ux",
        "1. Color and contrast",
    ),
    (
        "data/claims/typography-practice-influences-perceived-hierarchy.yaml",
        "concept:typography-practice",
        "concept:hierarchy-perceived",
        "expert-opinion",
        "source:nng-2025-good-visual-design",
        "Visual Principle: Use of a Typographic System",
    ),
    (
        "data/claims/readability-linguistic-influences-reading-speed.yaml",
        "concept:readability-linguistic",
        "concept:reading-speed",
        "empirical",
        "source:dubay-2004-principles-of-readability",
        "Reading Performance",
    ),
]

for rel, subject, obj, basis, source, locator in checks:
    d = yaml.safe_load((WT / rel).read_text(encoding="utf-8"))
    assert d["subject"] == subject
    assert d["predicate"] == "influences"
    assert d["object"] == obj
    assert d["modality"] == "descriptive"
    assert d["basis"] == [basis]
    assert d["evidence_status"] == "unassessed"
    assert d["sources"] == [source]
    assert d["source_locators"][0]["source"] == source
    assert d["source_locators"][0]["selector"]["type"] == "SectionSelector"
    assert d["source_locators"][0]["selector"]["value"] == locator
    print(f"{d['id']} -> {source} -> {locator}")

print("===== ZERO-NEW-CONCEPT GATE =====")
new_concepts = [
    line for line in out(WT, "git", "status", "--porcelain=v1").splitlines()
    if "data/concepts/" in line
]
if new_concepts:
    fail("04B unexpectedly adds concept records: " + repr(new_concepts))
print("NEW_CONCEPTS: 0")

print("===== ZERO-ARCHITECTURE-CHANGE GATE =====")
for forbidden in (
    "schema",
    "vocab",
    "docs/PROJECT_FOUNDATION.md",
    "docs/PLUGIN_TARGET_ARCHITECTURE.md",
):
    if subprocess.run(
        ["git", "diff", "--quiet", "--", forbidden],
        cwd=WT,
    ).returncode != 0:
        fail("forbidden mutation under " + forbidden)

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_04B_TRIAL_PASS")
print("Added claims: 3")
print("Added sources: 1")
print("New concepts: 0")
print("Corpus: 92 records — 45 concepts, 14 claims, 33 sources")
print("Deferred candidates preserved: 2")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
