#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BRANCH = "registry-batch-01"
BASE_COMMIT = "12171f1"
BASE_COUNTS = (54, 28, 9, 17)
FINAL_COUNTS = (60, 31, 9, 20)

NEW_FILES = {
    "data/sources/graphic-communications-open-textbook-collective-2015-graphic-design.yaml": {
        "id": "source:graphic-communications-open-textbook-collective-2015-graphic-design",
        "kind": "source",
        "citation": "Graphic Communications Open Textbook Collective. Graphic Design and Print Production Fundamentals. Victoria, BC: BCcampus, 2015.",
        "source_type": "textbook",
        "year": 2015,
        "identifier": "Ebook ISBN 978-1-989623-67-1",
        "notes": "Open textbook published by BCcampus. Chapter 3.2, authored by Alex Hass, is used here for the graphic-point sense. Exact support location is stored on the concept-source relation.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300400858-lines-artistic-concept.yaml": {
        "id": "source:getty-aat-300400858-lines-artistic-concept",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300400858, lines (artistic concept).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300400858",
        "notes": "Getty AAT concept record for the artistic/graphic line sense. Stable semantic page: http://vocab.getty.edu/page/aat/300400858.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300260079-contrast.yaml": {
        "id": "source:getty-aat-300260079-contrast",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300260079, contrast.",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300260079",
        "notes": "Getty AAT concept record for contrast as a formal/artistic concept. Stable semantic page: http://vocab.getty.edu/page/aat/300260079.",
        "schema_version": "0.1",
    },
    "data/concepts/point-graphic.yaml": {
        "id": "concept:point-graphic",
        "kind": "concept",
        "label": "Graphic point",
        "aliases": ["point"],
        "definition": "A visible dot or localized mark used as a basic visual element in a composition.",
        "definition_sources": [
            "source:graphic-communications-open-textbook-collective-2015-graphic-design"
        ],
        "definition_source_locators": [
            {
                "source": "source:graphic-communications-open-textbook-collective-2015-graphic-design",
                "selector": {
                    "type": "SectionSelector",
                    "value": "Chapter 3.2, Point",
                },
            }
        ],
        "locus": ["artifact"],
        "facets": [],
        "disciplines": [],
        "knowledge_origin": ["design-practice"],
        "traditions": [],
        "is_a": [],
        "part_of": [],
        "related": [],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "Sense-qualified to distinguish the graphic/design element from mathematical point and focal-point senses.",
        "schema_version": "0.1",
    },
    "data/concepts/line-graphic.yaml": {
        "id": "concept:line-graphic",
        "kind": "concept",
        "label": "Graphic line",
        "aliases": ["line"],
        "definition": "A visible or implied elongated mark or linear form in a composition, long in proportion to its breadth and traceable on a surface or inferable through the joining of points.",
        "definition_sources": [
            "source:getty-aat-300400858-lines-artistic-concept"
        ],
        "definition_source_locators": [
            {
                "source": "source:getty-aat-300400858-lines-artistic-concept",
                "selector": {
                    "type": "SectionSelector",
                    "value": "AAT record 300400858, Note (English)",
                },
            }
        ],
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
        "notes": "Sense-qualified to distinguish the graphic/artistic line from mathematical, textual-line, contour, and other line senses.",
        "schema_version": "0.1",
    },
    "data/concepts/contrast-visual.yaml": {
        "id": "concept:contrast-visual",
        "kind": "concept",
        "label": "Visual contrast",
        "aliases": ["contrast"],
        "definition": "The juxtaposition of dissimilar visual elements, properties, or qualities in a work such that their differences are revealed through comparison.",
        "definition_sources": [
            "source:getty-aat-300260079-contrast"
        ],
        "definition_source_locators": [
            {
                "source": "source:getty-aat-300260079-contrast",
                "selector": {
                    "type": "SectionSelector",
                    "value": "AAT record 300260079, Note (English)",
                },
            }
        ],
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
        "notes": "Formal visual concept distinct from concept:contrast-ratio, which is a quantitative luminance-ratio construct.",
        "schema_version": "0.1",
    },
}

PILOT_REL = "pilot/PILOT_RECORDS.md"

PILOT_BLOCK = """
## REGISTRY-BATCH-01A — VISUAL/FORM FUNDAMENTALS

- [x] Population branch starts from post-PF-001 main checkpoint 12171f1.
- [x] Minted concept:point-graphic with locus artifact and an exact Chapter 3.2 > Point locator.
- [x] Minted concept:line-graphic with locus artifact and Getty AAT 300400858 locator.
- [x] Minted concept:contrast-visual with locus artifact and Getty AAT 300260079 locator.
- [x] Kept concept:contrast-visual distinct from existing concept:contrast-ratio.
- [x] Used sense-qualified IDs for point and line rather than overloaded bare lexical IDs.
- [x] Added three source records; no existing canonical source was duplicated.
- [x] Added no claims or structural relations.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] hue, value, and saturation remain deferred to REGISTRY-BATCH-01B for sense/locus adjudication.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 60 records — 31 concepts, 9 claims, 20 sources.
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


print("===== REGISTRY-BATCH-01A =====")

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
expected_head = subprocess.check_output(
    ["git", "rev-parse", BASE_COMMIT], cwd=ROOT, text=True
).strip()
if head != expected_head:
    fail(f"expected HEAD {expected_head}, got {head}")

if counts() != BASE_COUNTS:
    fail(f"expected baseline counts {BASE_COUNTS}, got {counts()}")

for rel in NEW_FILES:
    if (ROOT / rel).exists():
        fail("target already exists: " + rel)

for forbidden in (
    "concept:point-graphic",
    "concept:line-graphic",
    "concept:contrast-visual",
    "source:graphic-communications-open-textbook-collective-2015-graphic-design",
    "source:getty-aat-300400858-lines-artistic-concept",
    "source:getty-aat-300260079-contrast",
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

if "## REGISTRY-BATCH-01A" in (ROOT / PILOT_REL).read_text(encoding="utf-8"):
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
actual_changed = sorted(
    subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).splitlines()
)

actual_paths = []
for line in actual_changed:
    path = line[3:]
    actual_paths.append(path)

if sorted(actual_paths) != expected_changed:
    fail(
        "unexpected mutation boundary\nEXPECTED:\n"
        + "\n".join(expected_changed)
        + "\nACTUAL:\n"
        + "\n".join(sorted(actual_paths))
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
print("OUTCOME: REGISTRY_BATCH_01A_PASS")
print("Added concepts: point-graphic, line-graphic, contrast-visual")
print("Added sources: BCcampus 2015 textbook, Getty AAT 300400858, Getty AAT 300260079")
print("Claims added: 0")
print("Structural relations added: 0")
print("Schema/vocabulary/Foundation changes: 0")
print("SELF-TESTS: 36 PASS")
print("CHECKER: PASS (0 warnings)")
print("COUNTS: 60 records — 31 concepts, 9 claims, 20 sources")
print("Batch-01B: hue/value/saturation DEFERRED for sense/locus adjudication")
print("No commit or push performed.")
