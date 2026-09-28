#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BRANCH = "registry-batch-01b"
BASE_COMMIT = "8f43a91b330034917d6bc9020f5876c4eabb2e47"
BASE_COUNTS = (60, 31, 9, 20)
FINAL_COUNTS = (65, 34, 9, 22)

NEW_FILES = {
    "data/sources/cie-s017-2020-ilv.yaml": {
        "id": "source:cie-s017-2020-ilv",
        "kind": "source",
        "citation": "Commission Internationale de l'Éclairage (CIE). CIE S 017:2020 ILV: International Lighting Vocabulary, 2nd edition. Vienna: CIE, 2020.",
        "source_type": "standard",
        "year": 2020,
        "identifier": "CIE S 017:2020",
        "notes": "International Lighting Vocabulary. The CIE e-ILV provides the term-level definitions used here for hue (17-22-067) and saturation (17-22-073). Exact term locators are stored on the concept-source relations.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300056176-value-color-property.yaml": {
        "id": "source:getty-aat-300056176-value-color-property",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300056176, value (color property).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300056176",
        "notes": "Getty AAT concept record for value as a perceived color property, explicitly distinguished from general surface brightness. Stable semantic page: http://vocab.getty.edu/page/aat/300056176.",
        "schema_version": "0.1",
    },
    "data/concepts/hue-perceived.yaml": {
        "id": "concept:hue-perceived",
        "kind": "concept",
        "label": "Perceived hue",
        "aliases": ["hue"],
        "definition": "A perceived color attribute by which an area appears similar to red, yellow, green, blue, or to combinations of adjacent members of that cyclic sequence.",
        "definition_sources": [
            "source:cie-s017-2020-ilv"
        ],
        "definition_source_locators": [
            {
                "source": "source:cie-s017-2020-ilv",
                "selector": {
                    "type": "SectionSelector",
                    "value": "17-22-067 hue",
                },
            }
        ],
        "locus": ["experience"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science", "standards-body"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Perceptual sense only. Numerical hue coordinates used by particular color spaces are not modeled in this batch.",
        "schema_version": "0.1",
    },
    "data/concepts/saturation-perceived.yaml": {
        "id": "concept:saturation-perceived",
        "kind": "concept",
        "label": "Perceived saturation",
        "aliases": ["saturation"],
        "definition": "A perceived color attribute expressing an area's colourfulness relative to its perceived brightness.",
        "definition_sources": [
            "source:cie-s017-2020-ilv"
        ],
        "definition_source_locators": [
            {
                "source": "source:cie-s017-2020-ilv",
                "selector": {
                    "type": "SectionSelector",
                    "value": "17-22-073 saturation",
                },
            }
        ],
        "locus": ["experience"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["perceptual-science", "standards-body"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Perceptual sense only. Saturation is not collapsed into chroma, and numerical saturation coordinates used by particular color spaces are not modeled in this batch.",
        "schema_version": "0.1",
    },
    "data/concepts/color-value-perceived.yaml": {
        "id": "concept:color-value-perceived",
        "kind": "concept",
        "label": "Perceived color value",
        "aliases": ["value", "color value", "colour value"],
        "definition": "The perceived degree of lightness or darkness of a hue, conventionally ranging from white at the lightest end to black at the darkest end.",
        "definition_sources": [
            "source:getty-aat-300056176-value-color-property"
        ],
        "definition_source_locators": [
            {
                "source": "source:getty-aat-300056176-value-color-property",
                "selector": {
                    "type": "SectionSelector",
                    "value": "AAT record 300056176, Note (English)",
                },
            }
        ],
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
        "notes": "Art/design color-value sense. Kept distinct from general brightness, photometric quantities, and HSV/HSB numeric value coordinates.",
        "schema_version": "0.1",
    },
}

PILOT_REL = "pilot/PILOT_RECORDS.md"

PILOT_BLOCK = """
## REGISTRY-BATCH-01B — PERCEIVED COLOR FUNDAMENTALS

- [x] Population branch starts from integrated REGISTRY-BATCH-01A checkpoint 8f43a91.
- [x] Adjudicated hue, saturation, and value before minting; no bare lexical IDs were used.
- [x] Minted concept:hue-perceived with locus experience and CIE S 017:2020 e-ILV term 17-22-067 locator.
- [x] Minted concept:saturation-perceived with locus experience and CIE S 017:2020 e-ILV term 17-22-073 locator.
- [x] Minted concept:color-value-perceived with locus experience and Getty AAT 300056176 locator.
- [x] Saturation remains distinct from chroma.
- [x] Color value remains distinct from general brightness and from HSV/HSB numeric value coordinates.
- [x] Artifact/color-space coordinate senses are intentionally not modeled in this batch.
- [x] Added two source records; CIE S 017:2020 is reused by two concept-definition relations with separate locators.
- [x] Added no claims or structural relations.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 65 records — 34 concepts, 9 claims, 22 sources.
- [x] Outcome: PASS.
""".strip()


def fail(message: str) -> None:
    raise SystemExit("ERROR: " + message)


def run(*args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout


def counts():
    concepts = list((ROOT / "data/concepts").glob("*.yaml"))
    claims = list((ROOT / "data/claims").glob("*.yaml"))
    sources = list((ROOT / "data/sources").glob("*.yaml"))
    return (
        len(concepts) + len(claims) + len(sources),
        len(concepts),
        len(claims),
        len(sources),
    )


print("===== REGISTRY-BATCH-01B =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != BRANCH:
    fail(f"expected branch {BRANCH}, got {branch}")

if subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=ROOT, text=True
).strip():
    fail("working tree must be clean")

head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
).strip()
if head != BASE_COMMIT:
    fail(f"expected HEAD {BASE_COMMIT}, got {head}")

if counts() != BASE_COUNTS:
    fail(f"expected baseline counts {BASE_COUNTS}, got {counts()}")

for rel in NEW_FILES:
    if (ROOT / rel).exists():
        fail("target already exists: " + rel)

for forbidden in (
    "concept:hue-perceived",
    "concept:saturation-perceived",
    "concept:color-value-perceived",
    "source:cie-s017-2020-ilv",
    "source:getty-aat-300056176-value-color-property",
):
    p = subprocess.run(
        ["grep", "-R", "-n", "-F", forbidden, "data"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if p.returncode == 0:
        fail(f"ID collision for {forbidden}:\n{p.stdout}")
    if p.returncode not in (0, 1):
        fail("grep collision check failed")

if "## REGISTRY-BATCH-01B" in (ROOT / PILOT_REL).read_text(encoding="utf-8"):
    fail("batch audit entry already exists")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")
print("PRECONDITIONS: PASS")

for rel, record in NEW_FILES.items():
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            record,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
        ),
        encoding="utf-8",
    )
    print("CREATED:", rel)

pilot = ROOT / PILOT_REL
pilot.write_text(
    pilot.read_text(encoding="utf-8").rstrip()
    + "\n\n"
    + PILOT_BLOCK
    + "\n",
    encoding="utf-8",
)
print("UPDATED:", PILOT_REL)

print("\n===== POST-MUTATION VALIDATION =====")
out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-test suite did not pass")

pass_count = sum(
    1 for line in out.splitlines()
    if line.startswith("PASS:")
)
if pass_count != 36:
    fail(f"expected 36 PASS self-tests, got {pass_count}")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker did not pass cleanly")

run("git", "diff", "--check")

if counts() != FINAL_COUNTS:
    fail(f"expected final counts {FINAL_COUNTS}, got {counts()}")

expected_changed = sorted(list(NEW_FILES.keys()) + [PILOT_REL])
status_lines = subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=ROOT, text=True
).splitlines()
actual_paths = sorted(line[3:] for line in status_lines)

if actual_paths != expected_changed:
    fail(
        "unexpected mutation boundary\nEXPECTED:\n"
        + "\n".join(expected_changed)
        + "\nACTUAL:\n"
        + "\n".join(actual_paths)
    )

for forbidden_path in (
    "schema",
    "vocab",
    "docs/PROJECT_FOUNDATION.md",
    "docs/PLUGIN_TARGET_ARCHITECTURE.md",
    "data/claims",
):
    p = subprocess.run(
        ["git", "diff", "--quiet", "--", forbidden_path],
        cwd=ROOT,
    )
    if p.returncode != 0:
        fail("forbidden change detected under " + forbidden_path)

print("\n===== RESULT =====")
print("OUTCOME: REGISTRY_BATCH_01B_PASS")
print("Added concepts: hue-perceived, saturation-perceived, color-value-perceived")
print("Added sources: CIE S 017:2020 ILV, Getty AAT 300056176")
print("Claims added: 0")
print("Structural relations added: 0")
print("Artifact/color-space coordinate senses added: 0")
print("Schema/vocabulary/Foundation changes: 0")
print("SELF-TESTS: 36 PASS")
print("CHECKER: PASS (0 warnings)")
print("COUNTS: 65 records — 34 concepts, 9 claims, 22 sources")
print("No commit or push performed.")
