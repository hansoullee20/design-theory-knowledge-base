#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BRANCH = "registry-batch-02b"
BASE_COMMIT = "6702ec5"
BASE_COUNTS = (65, 34, 9, 22)
FINAL_COUNTS = (69, 36, 10, 23)

NEW_FILES = {
    "data/sources/nng-2025-good-visual-design.yaml": {
        "id": "source:nng-2025-good-visual-design",
        "kind": "source",
        "citation": "Gordon, Kelley. Good Visual Design, Explained. Nielsen Norman Group, 14 November 2025.",
        "source_type": "web",
        "year": 2025,
        "identifier": "",
        "notes": "Design-practice guidance. Section 'Visual Principle: Grid Use and Alignment' states that grids help create cohesive layouts and recommends using a grid to keep alignment consistent across different pages and elements. Used as expert-opinion/design-practice support rather than empirical effect-size evidence.",
        "schema_version": "0.1",
    },
    "data/concepts/grid-use.yaml": {
        "id": "concept:grid-use",
        "kind": "concept",
        "label": "Grid use",
        "aliases": ["use of a grid"],
        "definition": "The design practice of organizing and positioning visual elements according to a grid.",
        "definition_sources": ["source:nng-2025-good-visual-design"],
        "definition_source_locators": [{
            "source": "source:nng-2025-good-visual-design",
            "selector": {"type": "SectionSelector", "value": "Visual Principle: Grid Use and Alignment"},
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
        "notes": "Practice sense deliberately separated from concept:grid, which represents the artifact-level organizational system itself.",
        "schema_version": "0.1",
    },
    "data/concepts/alignment-consistency.yaml": {
        "id": "concept:alignment-consistency",
        "kind": "concept",
        "label": "Alignment consistency",
        "aliases": ["consistent alignment"],
        "definition": "The degree to which visual elements maintain consistent alignment relationships across elements or pages of a design.",
        "definition_sources": ["source:nng-2025-good-visual-design"],
        "definition_source_locators": [{
            "source": "source:nng-2025-good-visual-design",
            "selector": {"type": "SectionSelector", "value": "Visual Principle: Grid Use and Alignment"},
        }],
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
        "notes": "Artifact-level consistency property. It is not the same concept as left alignment, which names a specific alignment mode.",
        "schema_version": "0.1",
    },
    "data/claims/grid-use-increases-alignment-consistency.yaml": {
        "id": "claim:grid-use-increases-alignment-consistency",
        "kind": "claim",
        "statement": "Using a grid can increase alignment consistency across different pages and elements in a design.",
        "modality": "descriptive",
        "subject": "concept:grid-use",
        "predicate": "increases",
        "object": "concept:alignment-consistency",
        "basis": ["expert-opinion"],
        "evidence_status": "unassessed",
        "scope": "Design-practice guidance for visual and interface layouts. The cited source explicitly recommends grid use to keep alignment consistent across pages and elements. This record does not assert an empirically quantified causal effect, universal guarantee, or effect size; results depend on how consistently the grid is applied.",
        "sources": ["source:nng-2025-good-visual-design"],
        "source_locators": [{
            "source": "source:nng-2025-good-visual-design",
            "selector": {"type": "SectionSelector", "value": "Visual Principle: Grid Use and Alignment"},
        }],
        "record_status": "draft",
        "replaced_by": [],
        "notes": "REGISTRY-BATCH-02B tests a practice-locus subject and artifact-locus object without conflating concept:grid with the practice of using a grid.",
        "schema_version": "0.1",
    },
}

PILOT_REL = "pilot/PILOT_RECORDS.md"
PILOT_BLOCK = """
## REGISTRY-BATCH-02B — GRID USE AND ALIGNMENT CONSISTENCY

- [x] Tested the required grid use → alignment consistency stress case under the Registry Population Protocol.
- [x] Reused existing concept:grid as the artifact-level grid system but did not misuse it as the practice endpoint.
- [x] Minted concept:grid-use with locus practice.
- [x] Minted concept:alignment-consistency with locus artifact.
- [x] Kept alignment consistency distinct from existing concept:left-alignment, which represents a specific alignment mode.
- [x] Added source:nng-2025-good-visual-design with an exact section locator to Visual Principle: Grid Use and Alignment.
- [x] Minted claim:grid-use-increases-alignment-consistency.
- [x] Claim uses descriptive modality, increases predicate, expert-opinion basis, and unassessed evidence status.
- [x] Scope explicitly excludes an empirically quantified effect, universal guarantee, or effect-size interpretation.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 69 records — 36 concepts, 10 claims, 23 sources.
- [x] Outcome: PASS_WITH_QUALIFICATION.
""".strip()

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

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
    c = list((ROOT / "data/concepts").glob("*.yaml"))
    k = list((ROOT / "data/claims").glob("*.yaml"))
    s = list((ROOT / "data/sources").glob("*.yaml"))
    return (len(c) + len(k) + len(s), len(c), len(k), len(s))

print("===== REGISTRY-BATCH-02B =====")

branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
if branch != BRANCH:
    fail(f"expected branch {BRANCH}, got {branch}")

if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
    fail("working tree must be clean")

head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
base = subprocess.check_output(["git", "rev-parse", BASE_COMMIT], cwd=ROOT, text=True).strip()
if head != base:
    fail(f"expected HEAD {base}, got {head}")

if counts() != BASE_COUNTS:
    fail(f"expected baseline counts {BASE_COUNTS}, got {counts()}")

for rel in NEW_FILES:
    if (ROOT / rel).exists():
        fail("target already exists: " + rel)

for rid in (
    "concept:grid-use",
    "concept:alignment-consistency",
    "claim:grid-use-increases-alignment-consistency",
    "source:nng-2025-good-visual-design",
):
    p = subprocess.run(["grep", "-R", "-n", "-F", rid, "data"], cwd=ROOT, text=True, capture_output=True)
    if p.returncode == 0:
        fail(f"ID collision for {rid}:\n{p.stdout}")
    if p.returncode not in (0, 1):
        fail("collision check failed")

pilot = ROOT / PILOT_REL
pilot_text = pilot.read_text(encoding="utf-8")
if "## REGISTRY-BATCH-02B" in pilot_text:
    fail("02B audit entry already exists")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")
print("PRECONDITIONS: PASS")

for rel, record in NEW_FILES.items():
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    print("CREATED:", rel)

needle = "- [ ] grid use → alignment consistency"
if needle in pilot_text:
    pilot_text = pilot_text.replace(needle, "- [x] grid use → alignment consistency", 1)

pilot.write_text(pilot_text.rstrip() + "\n\n" + PILOT_BLOCK + "\n", encoding="utf-8")
print("UPDATED:", PILOT_REL)

print("\n===== POST-MUTATION VALIDATION =====")
out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-tests did not pass")
if sum(1 for line in out.splitlines() if line.startswith("PASS:")) != 36:
    fail("expected 36 PASS self-tests")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("checker did not pass cleanly")

run("git", "diff", "--check")

if counts() != FINAL_COUNTS:
    fail(f"expected final counts {FINAL_COUNTS}, got {counts()}")

expected = sorted(list(NEW_FILES) + [PILOT_REL])
status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
actual = sorted(line[3:] for line in status)
if actual != expected:
    fail("unexpected mutation boundary\nEXPECTED:\n" + "\n".join(expected) + "\nACTUAL:\n" + "\n".join(actual))

for forbidden in ("schema", "vocab", "docs/PROJECT_FOUNDATION.md", "docs/PLUGIN_TARGET_ARCHITECTURE.md"):
    p = subprocess.run(["git", "diff", "--quiet", "--", forbidden], cwd=ROOT)
    if p.returncode != 0:
        fail("forbidden mutation detected under " + forbidden)

print("\n===== RESULT =====")
print("OUTCOME: REGISTRY_BATCH_02B_PASS")
print("Added concepts: grid-use, alignment-consistency")
print("Added claim: grid-use-increases-alignment-consistency")
print("Added source: nng-2025-good-visual-design")
print("Schema/vocabulary/Foundation changes: 0")
print("SELF-TESTS: 36 PASS")
print("CHECKER: PASS (0 warnings)")
print("COUNTS: 69 records — 36 concepts, 10 claims, 23 sources")
print("No commit or push performed.")
