#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

TMP_PY="$(mktemp /tmp/wcag-01-retest.XXXXXX.py)"
trap 'rm -f "$TMP_PY"' EXIT

cat > "$TMP_PY" <<'PY'
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BASELINE = (43, 23, 6, 14)
EXPECTED = (46, 25, 7, 14)
SOURCE_ID = "source:w3c-wcag-2-2"


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write_new(rel: str, text: str) -> None:
    p = ROOT / rel
    if p.exists():
        fail(f"refusing to overwrite existing file: {rel}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"CREATED: {rel}")


def update(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


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


def run(*args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail(f"command failed ({p.returncode}): {' '.join(args)}")
    return p.stdout


def dump(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def concept_from_template(record_id: str, label: str, definition: str):
    candidates = [
        ROOT / "data/concepts/card-sorting.yaml",
        ROOT / "data/concepts/hierarchy-specified.yaml",
    ]
    template_path = next((p for p in candidates if p.exists()), None)
    if template_path is None:
        existing = sorted((ROOT / "data/concepts").glob("*.yaml"))
        if not existing:
            fail("no concept template available")
        template_path = existing[0]

    data = copy.deepcopy(yaml.safe_load(
        template_path.read_text(encoding="utf-8")
    ))

    data["id"] = record_id
    data["kind"] = "concept"
    data["label"] = label

    if "aliases" in data:
        data["aliases"] = []

    data["definition"] = definition
    data["definition_sources"] = [SOURCE_ID]
    data["locus"] = ["artifact"]

    if "facets" in data:
        data["facets"] = []
    if "disciplines" in data:
        data["disciplines"] = []
    if "knowledge_origin" in data:
        data["knowledge_origin"] = ["standards-body"]
    if "traditions" in data:
        data["traditions"] = ["accessibility-standards"]

    data["is_a"] = []
    data["part_of"] = []
    data["related"] = []

    if "record_status" in data:
        data["record_status"] = "draft"
    if "replaced_by" in data:
        data["replaced_by"] = []
    if "notes" in data:
        data["notes"] = ""

    return data


print("===== PRECONDITIONS =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != "main":
    fail(f"expected main, got {branch!r}")

if "(rev. 9)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("expected Foundation rev. 9")

if counts() != BASELINE:
    fail(f"expected baseline {BASELINE}, got {counts()}")

source = yaml.safe_load(read("data/sources/w3c-wcag-2-2.yaml"))
if source.get("id") != SOURCE_ID:
    fail("canonical WCAG 2.2 source ID mismatch")

failure_log = read("pilot/PILOT_FAILURE_LOG.md")
if "**PF-006 — RESOLVED" not in failure_log:
    fail("PF-006 is not recorded as RESOLVED")

schema = yaml.safe_load(read("schema/claim.schema.yaml"))
predicates = schema["properties"]["predicate"]["enum"]
if predicates != ["increases", "decreases", "influences", "requires"]:
    fail(f"unexpected predicate vocabulary in schema: {predicates!r}")
if "constraint" not in schema["properties"]:
    fail("rev.9 constraint schema not present")

for rel in (
    "data/concepts/visual-presentation-of-text.yaml",
    "data/concepts/contrast-ratio.yaml",
    "data/claims/wcag-text-presentation-requires-minimum-contrast-ratio.yaml",
):
    if (ROOT / rel).exists():
        fail(f"retest target already exists: {rel}")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

print("PRECONDITIONS: PASS")

print("\n===== CONCEPTS =====")

visual = concept_from_template(
    "concept:visual-presentation-of-text",
    "Visual presentation of text",
    (
        "The rendered visual presentation of text or images of text in an artifact, "
        "including the foreground/background presentation for which visual contrast "
        "can be assessed."
    ),
)

ratio = concept_from_template(
    "concept:contrast-ratio",
    "Contrast ratio",
    (
        "A dimensionless ratio derived from the relative luminance of the lighter "
        "and darker colors in a visual presentation, used to quantify visual contrast."
    ),
)

write_new(
    "data/concepts/visual-presentation-of-text.yaml",
    dump(visual),
)
write_new(
    "data/concepts/contrast-ratio.yaml",
    dump(ratio),
)

print("\n===== CANONICAL WCAG CLAIM =====")

claim = {
    "id": "claim:wcag-text-presentation-requires-minimum-contrast-ratio",
    "kind": "claim",
    "statement": (
        "Under WCAG 2.2 Success Criterion 1.4.3 (Level AA), the visual presentation "
        "of text and images of text requires a contrast ratio of at least 4.5:1, "
        "except where the criterion specifies a different requirement or exemption."
    ),
    "modality": "prescriptive",
    "subject": "concept:visual-presentation-of-text",
    "predicate": "requires",
    "object": "concept:contrast-ratio",
    "constraint": {
        "operator": "gte",
        "value": 4.5,
        "unit": "ratio",
    },
    "basis": ["standard"],
    "evidence_status": "unassessed",
    "scope": (
        "WCAG 2.2 SC 1.4.3 Contrast (Minimum), Level AA. Large-scale text and "
        "images of large-scale text require at least 3:1. Incidental text and "
        "logotypes are exempt under this criterion. This claim encodes the "
        "general 4.5:1 threshold only."
    ),
    "sources": [SOURCE_ID],
    "record_status": "draft",
    "replaced_by": [],
    "notes": (
        "WCAG-01 canonical retest after PF-006 resolution. The threshold is encoded "
        "structurally in constraint rather than only in free text."
    ),
    "schema_version": "0.1",
}

write_new(
    "data/claims/wcag-text-presentation-requires-minimum-contrast-ratio.yaml",
    dump(claim),
)

print("\n===== PILOT RECORD =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)
if "## WCAG-01-RETEST" in text:
    fail("WCAG-01-RETEST already logged")

block = '''
## WCAG-01-RETEST

- [x] Retested CQ27 after PF-006-RESOLUTION-01 / Foundation rev. 9.
- [x] Reused `source:w3c-wcag-2-2`; no duplicate source minted.
- [x] Minted `concept:visual-presentation-of-text` with `locus: [artifact]`.
- [x] Minted `concept:contrast-ratio` with `locus: [artifact]`.
- [x] Minted `claim:wcag-text-presentation-requires-minimum-contrast-ratio`.
- [x] Claim uses `modality: prescriptive`, `basis: [standard]`, `predicate: requires`.
- [x] The 4.5:1 threshold is encoded as `constraint: {operator: gte, value: 4.5, unit: ratio}`.
- [x] Large-scale text, incidental text, and logotype qualifications remain explicit in `scope`.
- [x] No threshold value was modeled as a concept.
- [x] Foundation remains rev. 9; no additional architecture change was required.
- [x] Outcome: `PASS`.
'''.replace("`", chr(96))

update(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

print("\n===== VALIDATION =====")

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-test failed")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")

run("git", "diff", "--check")

if counts() != EXPECTED:
    fail(f"expected post-retest corpus {EXPECTED}, got {counts()}")

loaded_claim = yaml.safe_load(read(
    "data/claims/wcag-text-presentation-requires-minimum-contrast-ratio.yaml"
))
if loaded_claim.get("predicate") != "requires":
    fail("canonical WCAG claim predicate mismatch")
if loaded_claim.get("modality") != "prescriptive":
    fail("canonical WCAG claim modality mismatch")
if loaded_claim.get("basis") != ["standard"]:
    fail("canonical WCAG claim basis mismatch")
if loaded_claim.get("constraint") != {
    "operator": "gte",
    "value": 4.5,
    "unit": "ratio",
}:
    fail("canonical WCAG claim constraint mismatch")

if "(rev. 9)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation changed away from rev. 9")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: PASS")
print("PILOT: WCAG-01-RETEST")
print("Foundation: rev. 9")
print("SOURCE: source:w3c-wcag-2-2 — REUSED")
print("CONCEPTS: concept:visual-presentation-of-text, concept:contrast-ratio")
print("CLAIM: claim:wcag-text-presentation-requires-minimum-contrast-ratio")
print("modality: prescriptive")
print("basis: standard")
print("predicate: requires")
print("constraint: gte 4.5 ratio")
print("COUNTS: 46 records — 25 concepts, 7 claims, 14 sources")
print("No commit or push performed.")
PY

python3 "$TMP_PY"
