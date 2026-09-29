#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-03c"
BRANCH = "registry-batch-03c"
BASE = "fd06323986719c7b51c61ba64364bd3d08f0a484"

SOURCES = {
    "data/sources/getty-aat-300056272-form-composition.yaml": {
        "id": "source:getty-aat-300056272-form-composition",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300056272, form (composition concepts).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300056272",
        "notes": "Getty AAT concept record for form as a composition concept concerning the design of visual elements in works of art and architecture. Stable semantic page: http://vocab.getty.edu/page/aat/300056272.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300056247-balance-composition.yaml": {
        "id": "source:getty-aat-300056247-balance-composition",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300056247, balance (composition concept).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300056247",
        "notes": "Getty AAT concept record for balance as the impression of visual equilibrium in a composition. Stable semantic page: http://vocab.getty.edu/page/aat/300056247.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300195853-typography.yaml": {
        "id": "source:getty-aat-300195853-typography",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300195853, typography.",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300195853",
        "notes": "Getty AAT concept record for typography as processes performed with type and typefaces, including setting type and creating layouts with type for printing. Stable semantic page: http://vocab.getty.edu/page/aat/300195853.",
        "schema_version": "0.1",
    },
}

CONCEPTS = {
    "data/concepts/form-compositional.yaml": {
        "id": "concept:form-compositional",
        "kind": "concept",
        "label": "Compositional form",
        "aliases": ["form"],
        "definition": "The design or organization of visual elements such as line, mass, shape, or color within a work of art or architecture.",
        "definition_sources": ["source:getty-aat-300056272-form-composition"],
        "definition_source_locators": [{
            "source": "source:getty-aat-300056272-form-composition",
            "selector": {
                "type": "SectionSelector",
                "value": "AAT record 300056272, Note (English)",
            },
        }],
        "locus": ["artifact"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["art-craft"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Sense-qualified to distinguish compositional form from visual shape, physical three-dimensional form, form as document structure, and other uses of the lexical term.",
        "schema_version": "0.1",
    },
    "data/concepts/visual-balance-perceived.yaml": {
        "id": "concept:visual-balance-perceived",
        "kind": "concept",
        "label": "Perceived visual balance",
        "aliases": ["visual balance", "balance"],
        "definition": "The perceived visual equilibrium of elements within a composition.",
        "definition_sources": ["source:getty-aat-300056247-balance-composition"],
        "definition_source_locators": [{
            "source": "source:getty-aat-300056247-balance-composition",
            "selector": {
                "type": "SectionSelector",
                "value": "AAT record 300056247, Note (English)",
            },
        }],
        "locus": ["experience"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["art-craft"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Sense-qualified because the AAT scope note characterizes balance as an impression of visual equilibrium; this record therefore represents experienced balance rather than an unqualified artifact-side metric.",
        "schema_version": "0.1",
    },
    "data/concepts/typography-practice.yaml": {
        "id": "concept:typography-practice",
        "kind": "concept",
        "label": "Typography practice",
        "aliases": ["typography"],
        "definition": "A design and production practice involving processes performed with type and typefaces, including setting type and arranging type in layouts for printing.",
        "definition_sources": ["source:getty-aat-300195853-typography"],
        "definition_source_locators": [{
            "source": "source:getty-aat-300195853-typography",
            "selector": {
                "type": "SectionSelector",
                "value": "AAT record 300195853, Note (English)",
            },
        }],
        "locus": ["practice"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["design-practice"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Practice sense only. Artifact-side typographic treatment and type design remain separate senses; Getty AAT explicitly distinguishes typography from type design.",
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

print("===== REGISTRY-BATCH-03C TRIAL =====")

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
        fail(f"{WT} exists on the wrong branch")
    if out(WT, "git", "status", "--porcelain"):
        fail(f"{BRANCH} worktree is dirty")
    if out(WT, "git", "rev-parse", "HEAD") != BASE:
        fail(f"{BRANCH} is not at required baseline")
else:
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
        cwd=REPO,
    ).returncode == 0
    if branch_exists:
        fail(f"branch {BRANCH} exists without the expected worktree")
    run(REPO, "git", "worktree", "add", "-b", BRANCH, str(WT), BASE)

print("===== COLLISION GATE =====")
for rel in list(SOURCES) + list(CONCEPTS):
    if (WT / rel).exists():
        fail(f"candidate path already exists: {rel}")

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (WT / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

for spec in list(SOURCES.values()) + list(CONCEPTS.values()):
    if spec["id"] in existing_ids:
        fail(f"candidate ID already exists: {spec['id']}")

print("===== APPLY BOUNDED MUTATION =====")
for rel, obj in SOURCES.items():
    dump(WT / rel, obj)
for rel, obj in CONCEPTS.items():
    dump(WT / rel, obj)

expected = sorted(list(SOURCES) + list(CONCEPTS))
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
if (c+k+src, c, k, src) != (85, 43, 11, 31):
    fail(f"unexpected corpus counts: {(c+k+src,c,k,src)}")

print("===== LOCATOR CHECK =====")
for rel, obj in CONCEPTS.items():
    source_id = obj["definition_sources"][0]
    locs = obj.get("definition_source_locators") or []
    if len(locs) != 1:
        fail(f"{rel}: expected exactly one definition locator")
    if locs[0].get("source") != source_id:
        fail(f"{rel}: locator/source mismatch")
    selector = locs[0].get("selector") or {}
    if selector.get("type") != "SectionSelector":
        fail(f"{rel}: unexpected selector type")
    print(obj["id"], "->", source_id, "->", selector.get("value"))

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
        fail(f"forbidden mutation under {forbidden}")

print("===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("canonical main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_03C_TRIAL_PASS")
print("Added concepts: 3")
print("Added sources: 3")
print("Claims added: 0")
print("Corpus: 85 records — 43 concepts, 11 claims, 31 sources")
print("Color: remains SPLIT_REQUIRED")
print("Feedback: remains SPLIT_REQUIRED")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
