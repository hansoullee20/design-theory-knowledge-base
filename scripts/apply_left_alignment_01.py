#!/usr/bin/env python3
from __future__ import annotations
import copy, subprocess, sys, tempfile
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
BASELINE = (46,25,7,14)
EXPECTED = (49,27,7,15)
SOURCE_ID = "source:lupton-2010-thinking-with-type"

def fail(msg):
    raise SystemExit(f"ERROR: {msg}")

def read(rel):
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")

def write_new(rel, text):
    p = ROOT / rel
    if p.exists():
        fail(f"refusing to overwrite existing file: {rel}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"CREATED: {rel}")

def update(rel, text):
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")

def counts():
    c = list((ROOT/"data/concepts").glob("*.yaml"))
    q = list((ROOT/"data/claims").glob("*.yaml"))
    s = list((ROOT/"data/sources").glob("*.yaml"))
    return (len(c)+len(q)+len(s), len(c), len(q), len(s))

def run(*args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail(f"command failed ({p.returncode}): {' '.join(args)}")
    return p.stdout

def dump(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)

def concept_from_template(record_id, label, definition):
    candidates = [
        ROOT/"data/concepts/card-sorting.yaml",
        ROOT/"data/concepts/hierarchy-specified.yaml",
    ]
    template = next((p for p in candidates if p.exists()), None)
    if template is None:
        existing = sorted((ROOT/"data/concepts").glob("*.yaml"))
        if not existing:
            fail("no concept template available")
        template = existing[0]
    data = copy.deepcopy(yaml.safe_load(template.read_text(encoding="utf-8")))
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
        data["knowledge_origin"] = ["design-practice"]
    if "traditions" in data:
        data["traditions"] = []
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
branch = subprocess.check_output(["git","branch","--show-current"], cwd=ROOT, text=True).strip()
if branch != "main":
    fail(f"expected main, got {branch!r}")
if "(rev. 9)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("expected Foundation rev. 9")
if counts() != BASELINE:
    fail(f"expected baseline {BASELINE}, got {counts()}")
for rel in (
    "data/sources/lupton-2010-thinking-with-type.yaml",
    "data/concepts/left-alignment.yaml",
    "data/concepts/body-text.yaml",
):
    if (ROOT/rel).exists():
        fail(f"pilot target already exists: {rel}")
if "## LEFT-ALIGNMENT-01" in read("pilot/PILOT_RECORDS.md"):
    fail("LEFT-ALIGNMENT-01 already logged")

schema = yaml.safe_load(read("schema/claim.schema.yaml"))
predicates = schema["properties"]["predicate"]["enum"]
if predicates != ["increases","decreases","influences","requires"]:
    fail(f"unexpected predicate vocabulary: {predicates!r}")
basis_values = yaml.safe_load(read("vocab/basis.yaml"))["values"]
if "conventional" not in basis_values:
    fail("conventional basis unavailable")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git","diff","--check")
print("PRECONDITIONS: PASS")

print("\n===== SOURCE =====")
source = {
    "id": SOURCE_ID,
    "kind": "source",
    "citation": "Lupton, Ellen. Thinking with Type: A Critical Guide for Designers, Writers, Editors, & Students. 2nd rev. and expanded ed. Princeton Architectural Press, 2010. ISBN 9781568989693.",
    "source_type": "book",
    "year": 2010,
    "notes": "Alignment section treats flush-left/ragged-right as the more familiar setting in Latin typography and notes flush-right is rarely used for long bodies of text. It also questions the common readability rationale, making it suitable for testing convention without treating familiarity as an empirical law. Exact source locator machinery remains deferred under PF-001.",
    "schema_version": "0.1",
}
write_new("data/sources/lupton-2010-thinking-with-type.yaml", dump(source))

print("\n===== CONCEPTS =====")
left_alignment = concept_from_template(
    "concept:left-alignment",
    "Left alignment",
    "A text-alignment treatment in which successive lines share a common left edge while the right edge remains uneven or ragged.",
)
body_text = concept_from_template(
    "concept:body-text",
    "Body text",
    "Extended running text intended to carry the main continuous written content of a document, page, or interface rather than a heading, caption, or marginal note.",
)
write_new("data/concepts/left-alignment.yaml", dump(left_alignment))
write_new("data/concepts/body-text.yaml", dump(body_text))

print("\n===== SCRATCH CONVENTION CLAIM TEST =====")
scratch = {
    "id": "claim:left-alignment-conventional-for-body-text-scratch",
    "kind": "claim",
    "statement": "In left-to-right Latin typography, left alignment is a familiar convention for long body text.",
    "modality": "descriptive",
    "subject": "concept:left-alignment",
    "predicate": "<NO_FAITHFUL_CURRENT_PREDICATE>",
    "object": "concept:body-text",
    "basis": ["conventional"],
    "evidence_status": "unassessed",
    "scope": "Left-to-right Latin typography and long-form body text. This does not assert that left alignment is universally required or empirically superior.",
    "sources": [SOURCE_ID],
    "record_status": "draft",
    "replaced_by": [],
    "notes": "Scratch-only LEFT-ALIGNMENT-01 claim.",
    "schema_version": "0.1",
    "canonical": False,
}
td = Path(tempfile.mkdtemp(prefix="left-alignment-01-"))
sp = td/"left-alignment-convention-scratch.yaml"
sp.write_text(dump(scratch), encoding="utf-8")
print("SCRATCH CLAIM:", sp)
print("AVAILABLE PREDICATES:", ", ".join(predicates))
print("increases/decreases: comparative effect; not convention")
print("influences: causal/associational effect; not convention")
print("requires: prescriptive threshold predicate; not convention")
print("SCRATCH OUTCOME: CLAIM_PREDICATE_GAP")

print("\n===== PILOT RECORD =====")
rel = "pilot/PILOT_RECORDS.md"
text = read(rel)
block = '''
## LEFT-ALIGNMENT-01

- [x] Tested the required pilot case `left-aligned body text (convention)`.
- [x] Added `source:lupton-2010-thinking-with-type` as design-practice evidence for typographic familiarity/convention.
- [x] Minted `concept:left-alignment` with `locus: [artifact]`.
- [x] Minted `concept:body-text` with `locus: [artifact]`.
- [x] Confirmed `basis: [conventional]` is available.
- [x] Scratch-only claim tested: in left-to-right Latin typography, left alignment is a familiar convention for long body text.
- [x] `increases` / `decreases` would falsely encode a comparative effect.
- [x] `influences` would falsely encode an effect or association.
- [x] `requires` would falsely turn a convention into a threshold requirement.
- [x] Outcome: `CLAIM_PREDICATE_GAP`.
- [x] No canonical left-alignment convention claim minted.
- [x] Foundation remains rev. 9 pending bounded predicate-resolution design.
'''.replace("`", chr(96))
update(rel, text.rstrip()+"\n\n"+block.strip()+"\n")

print("\n===== FAILURE LOG =====")
rel = "pilot/PILOT_FAILURE_LOG.md"
text = read(rel)
if "PF-007" in text:
    fail("PF-007 already exists")
entry = '''
- **PF-007 — OPEN — conventional-practice claim predicate.** LEFT-ALIGNMENT-01
  confirms that `basis: conventional` can classify the epistemic basis of a claim,
  but the current predicate vocabulary cannot faithfully express a proposition such
  as “left alignment is a familiar convention for body text.” `increases`,
  `decreases`, and `influences` encode effects; `requires` is a
  prescriptive threshold predicate. Resolve before Taxonomy v0.1 freeze without
  turning a convention into an empirical law, formal standard, or universal prescription.
'''.replace("`", chr(96))
update(rel, text.rstrip()+"\n"+entry.strip()+"\n")

print("\n===== VALIDATION =====")
out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-test failed")
out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")
run("git","diff","--check")
if counts() != EXPECTED:
    fail(f"expected post-pilot corpus {EXPECTED}, got {counts()}")
if "(rev. 9)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation changed away from rev. 9")

print("\n===== STATUS =====")
subprocess.run(["git","status","--short"], cwd=ROOT)
print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git","diff","--stat","HEAD"], cwd=ROOT)
print("\n===== RESULT =====")
print("OUTCOME: CLAIM_PREDICATE_GAP")
print("PILOT: LEFT-ALIGNMENT-01")
print("Foundation: rev. 9")
print("SOURCE: source:lupton-2010-thinking-with-type — NEW")
print("CONCEPTS: concept:left-alignment, concept:body-text")
print("basis: conventional — AVAILABLE")
print("faithful convention predicate: MISSING")
print("PF-007: OPEN")
print("COUNTS: 49 records — 27 concepts, 7 claims, 15 sources")
print("No canonical left-alignment convention claim minted.")
print("No commit or push performed.")
