#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
WT = WTROOT / "registry-batch-03f"
BRANCH = "registry-batch-03f"
BASE = "af3d86b55e5edaac5c7c8cecaf74409b1a1b524a"

SOURCE_PATH = "data/sources/w3c-coga-provide-feedback.yaml"
SOURCE = {
    "id": "source:w3c-coga-provide-feedback",
    "kind": "source",
    "citation": "World Wide Web Consortium (W3C), Web Accessibility Initiative (WAI). Cognitive Accessibility Design Pattern: Provide Feedback. Supplemental Guidance to WCAG 2. Content first published 29 April 2021.",
    "source_type": "web",
    "year": 2021,
    "identifier": "",
    "notes": "W3C supplemental cognitive-accessibility guidance for providing rapid, recognizable feedback after user actions. This is supplemental guidance, not a WCAG conformance requirement.",
    "schema_version": "0.1",
}

CONCEPTS = {
    "data/concepts/color-perceived.yaml": {
        "id": "concept:color-perceived",
        "kind": "concept",
        "label": "Perceived color",
        "aliases": ["color", "colour", "perceived colour"],
        "definition": "A characteristic of visual perception describable by attributes including hue, brightness or lightness, and colourfulness, saturation, or chroma.",
        "definition_sources": ["source:cie-s017-2020-ilv"],
        "definition_source_locators": [{
            "source": "source:cie-s017-2020-ilv",
            "selector": {
                "type": "SectionSelector",
                "value": "17-22-040 perceived colour",
            },
        }],
        "locus": ["experience"],
        "facets": ["color"],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science", "standards-body"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [
            "concept:hue-perceived",
            "concept:saturation-perceived",
            "concept:color-value-perceived",
        ],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Perceptual sense only. Kept distinct from psychophysical color and from numerical coordinates in particular color spaces.",
        "schema_version": "0.1",
    },
    "data/concepts/interaction-feedback.yaml": {
        "id": "concept:interaction-feedback",
        "kind": "concept",
        "label": "Interaction feedback",
        "aliases": ["user-action feedback"],
        "definition": "Information presented by an interactive system in response to a user-initiated action to indicate the action's status, success or failure, result, or resulting state.",
        "definition_sources": ["source:w3c-coga-provide-feedback"],
        "definition_source_locators": [{
            "source": "source:w3c-coga-provide-feedback",
            "selector": {
                "type": "SectionSelector",
                "value": "More Details",
            },
        }],
        "locus": ["artifact"],
        "facets": ["interaction"],
        "disciplines": ["interface-interaction-design"],
        "knowledge_origin": ["standards-body", "design-practice"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [
            "concept:signifier",
            "concept:affordance-perceived",
        ],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "System-response sense only. Status messages are a narrower future subtype; evaluative or design-process feedback is a different practice-level sense.",
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

print("===== REGISTRY-BATCH-03F TRIAL =====")

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
        fail("existing 03F worktree is on wrong branch")
    if out(WT, "git", "status", "--porcelain"):
        fail("existing 03F worktree is dirty")
    if out(WT, "git", "rev-parse", "HEAD") != BASE:
        fail("existing 03F worktree is on wrong baseline")
else:
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"],
        cwd=REPO,
    ).returncode == 0
    if branch_exists:
        fail("03F branch exists without expected worktree")
    run(REPO, "git", "worktree", "add", "-b", BRANCH, str(WT), BASE)

print("===== COLLISION / REUSE GATE =====")

required_existing = [
    "data/sources/cie-s017-2020-ilv.yaml",
    "data/concepts/hue-perceived.yaml",
    "data/concepts/saturation-perceived.yaml",
    "data/concepts/color-value-perceived.yaml",
    "data/concepts/signifier.yaml",
    "data/concepts/affordance-perceived.yaml",
]

for rel in required_existing:
    if not (WT / rel).exists():
        fail("required existing record missing: " + rel)

for rel in [SOURCE_PATH, *CONCEPTS.keys()]:
    if (WT / rel).exists():
        fail("candidate path already exists: " + rel)

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (WT / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

for candidate_id in [
    SOURCE["id"],
    CONCEPTS["data/concepts/color-perceived.yaml"]["id"],
    CONCEPTS["data/concepts/interaction-feedback.yaml"]["id"],
]:
    if candidate_id in existing_ids:
        fail("candidate ID already exists: " + candidate_id)

print("===== APPLY BOUNDED MUTATION =====")

dump(WT / SOURCE_PATH, SOURCE)
for rel, obj in CONCEPTS.items():
    dump(WT / rel, obj)

expected = sorted([SOURCE_PATH, *CONCEPTS.keys()])
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
if (c+k+src, c, k, src) != (88, 45, 11, 32):
    fail(f"unexpected corpus counts: {(c+k+src,c,k,src)}")

print("===== SEMANTIC / LOCATOR GATE =====")

color = yaml.safe_load((WT / "data/concepts/color-perceived.yaml").read_text(encoding="utf-8"))
feedback = yaml.safe_load((WT / "data/concepts/interaction-feedback.yaml").read_text(encoding="utf-8"))

assert color["locus"] == ["experience"]
assert color["definition_sources"] == ["source:cie-s017-2020-ilv"]
assert color["definition_source_locators"][0]["selector"]["value"] == "17-22-040 perceived colour"

assert feedback["locus"] == ["artifact"]
assert feedback["definition_sources"] == ["source:w3c-coga-provide-feedback"]
assert feedback["definition_source_locators"][0]["selector"]["value"] == "More Details"

print("concept:color-perceived -> source:cie-s017-2020-ilv -> 17-22-040 perceived colour")
print("concept:interaction-feedback -> source:w3c-coga-provide-feedback -> More Details")

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

print("OUTCOME: REGISTRY_BATCH_03F_TRIAL_PASS")
print("Added concepts: 2")
print("Added sources: 1")
print("Reused sources: 1")
print("Claims added: 0")
print("Corpus: 88 records — 45 concepts, 11 claims, 32 sources")
print("Psychophysical color: DEFER_SCOPE_AND_LOCUS")
print("Status-message feedback: DEFER_SUBTYPE")
print("Evaluative/design-process feedback: DEFER_SCOPE")
print("Architecture: NO_REOPEN")
print("No commit or push performed")
