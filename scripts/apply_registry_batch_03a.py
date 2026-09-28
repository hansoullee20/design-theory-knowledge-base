#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
BRANCH = "registry-batch-03a"
BASE_COMMIT = "0a495a2d3321694583177a800354694d1ea50244"
BASE_COUNTS = (74, 38, 11, 25)
FINAL_COUNTS = (78, 40, 11, 27)
PILOT_REL = "pilot/PILOT_RECORDS.md"

NEW_FILES = {
    "data/sources/getty-aat-300056273-shape-form-attribute.yaml": {
        "id": "source:getty-aat-300056273-shape-form-attribute",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300056273, shape (form attribute).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300056273",
        "notes": "Getty AAT concept record for shape as the outline, external form, or characteristic configuration of an object. Stable semantic page: http://vocab.getty.edu/page/aat/300056273.",
        "schema_version": "0.1",
    },
    "data/sources/getty-aat-300068896-space-composition.yaml": {
        "id": "source:getty-aat-300068896-space-composition",
        "kind": "source",
        "citation": "Getty Research Institute. Art & Architecture Thesaurus (AAT), record 300068896, space (composition concept).",
        "source_type": "web",
        "year": None,
        "identifier": "AAT 300068896",
        "notes": "Getty AAT concept record for compositional space in art and architecture. Stable semantic page: http://vocab.getty.edu/page/aat/300068896.",
        "schema_version": "0.1",
    },
    "data/concepts/shape-visual.yaml": {
        "id": "concept:shape-visual",
        "kind": "concept",
        "label": "Visual shape",
        "aliases": ["shape"],
        "definition": "The visible outline, external form, or characteristic configuration of an object, including its contours or outer boundary.",
        "definition_sources": ["source:getty-aat-300056273-shape-form-attribute"],
        "definition_source_locators": [{
            "source": "source:getty-aat-300056273-shape-form-attribute",
            "selector": {"type": "SectionSelector", "value": "AAT record 300056273, Note (English)"},
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
        "notes": "Sense-qualified to distinguish the artifact-borne visual/form attribute from mathematical shape and from perceived-shape experience.",
        "schema_version": "0.1",
    },
    "data/concepts/space-compositional.yaml": {
        "id": "concept:space-compositional",
        "kind": "concept",
        "label": "Compositional space",
        "aliases": ["space"],
        "definition": "The two- or three-dimensional areas around, above, below, beside, between, and within objects that function as elements of a visual composition, whether actual or simulated.",
        "definition_sources": ["source:getty-aat-300068896-space-composition"],
        "definition_source_locators": [{
            "source": "source:getty-aat-300068896-space-composition",
            "selector": {"type": "SectionSelector", "value": "AAT record 300068896, Note (English)"},
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
        "notes": "Sense-qualified to distinguish compositional space from physical/geometric space and from experienced spaciousness.",
        "schema_version": "0.1",
    },
}

PILOT_BLOCK = """
## REGISTRY-BATCH-03A — SHAPE AND COMPOSITIONAL SPACE

- [x] Began post-stress fundamentals expansion under the Registry Population Protocol.
- [x] Minted concept:shape-visual with locus artifact.
- [x] Minted concept:space-compositional with locus artifact.
- [x] Used sense-qualified IDs rather than bare shape or space.
- [x] Added Getty AAT record 300056273 with an exact Note (English) locator for visual shape.
- [x] Added Getty AAT record 300068896 with an exact Note (English) locator for compositional space.
- [x] Added no claims or structural relations.
- [x] form, color, balance, typography, and feedback remain deferred for separate sense adjudication.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 78 records — 40 concepts, 11 claims, 27 sources.
- [x] Outcome: PASS.
""".strip()

def fail(msg):
    raise SystemExit("ERROR: " + msg)

def run(*args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout

def counts():
    c = list((ROOT/"data/concepts").glob("*.yaml"))
    k = list((ROOT/"data/claims").glob("*.yaml"))
    s = list((ROOT/"data/sources").glob("*.yaml"))
    return (len(c)+len(k)+len(s), len(c), len(k), len(s))

print("===== REGISTRY-BATCH-03A =====")

branch = subprocess.check_output(["git","branch","--show-current"], cwd=ROOT, text=True).strip()
if branch != BRANCH:
    fail(f"expected branch {BRANCH}, got {branch}")

if subprocess.check_output(["git","status","--porcelain"], cwd=ROOT, text=True).strip():
    fail("working tree must be clean")

head = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
if head != BASE_COMMIT:
    fail(f"expected HEAD {BASE_COMMIT}, got {head}")

if counts() != BASE_COUNTS:
    fail(f"expected baseline counts {BASE_COUNTS}, got {counts()}")

for rel in NEW_FILES:
    if (ROOT/rel).exists():
        fail("target already exists: " + rel)

for rid in [r["id"] for r in NEW_FILES.values()]:
    p = subprocess.run(["grep","-R","-n","-F",rid,"data"], cwd=ROOT, text=True, capture_output=True)
    if p.returncode == 0:
        fail(f"ID collision for {rid}:\n{p.stdout}")
    if p.returncode not in (0,1):
        fail("collision check failed")

pilot = ROOT/PILOT_REL
pilot_text = pilot.read_text(encoding="utf-8")
if "## REGISTRY-BATCH-03A" in pilot_text:
    fail("03A pilot entry already exists")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

for rel, record in NEW_FILES.items():
    path = ROOT/rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    print("CREATED:", rel)

pilot.write_text(pilot_text.rstrip() + "\n\n" + PILOT_BLOCK + "\n", encoding="utf-8")
print("UPDATED:", PILOT_REL)

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-tests did not pass")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("checker did not pass cleanly")

run("git", "diff", "--check")

if counts() != FINAL_COUNTS:
    fail(f"expected final counts {FINAL_COUNTS}, got {counts()}")

expected = sorted(list(NEW_FILES) + [PILOT_REL])
status_raw = subprocess.check_output(["git","status","--porcelain=v1"], cwd=ROOT, text=True)
actual = sorted(line[2:].lstrip() for line in status_raw.splitlines())
if actual != expected:
    fail("unexpected mutation boundary\nEXPECTED:\n" + "\n".join(expected) + "\nACTUAL:\n" + "\n".join(actual))

for forbidden in ("schema","vocab","docs/PROJECT_FOUNDATION.md","docs/PLUGIN_TARGET_ARCHITECTURE.md"):
    p = subprocess.run(["git","diff","--quiet","--",forbidden], cwd=ROOT)
    if p.returncode != 0:
        fail("forbidden mutation detected under " + forbidden)

print("\n===== RESULT =====")
print("OUTCOME: REGISTRY_BATCH_03A_PASS")
print("Added concepts: shape-visual, space-compositional")
print("Added sources: Getty AAT 300056273, 300068896")
print("Claims added: 0")
print("Schema/vocabulary/Foundation changes: 0")
print("COUNTS: 78 records — 40 concepts, 11 claims, 27 sources")
print("No commit or push performed.")
