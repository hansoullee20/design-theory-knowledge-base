#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BASELINE = (54, 28, 9, 17)


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        fail(f"{label}: expected exactly 1 match, found {n}")
    return text.replace(old, new, 1)


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail(f"command failed ({p.returncode}): {' '.join(args)}")
    return p.stdout


print("===== PRECONDITIONS =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != "main":
    fail(f"expected main, got {branch!r}")

if "(rev. 10)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("expected Foundation rev. 10")

if counts() != BASELINE:
    fail(f"expected baseline {BASELINE}, got {counts()}")

if "## DEPRECATION-01" in read("pilot/PILOT_RECORDS.md"):
    fail("DEPRECATION-01 already logged")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

concept_hashes = {
    p: digest(p) for p in sorted((ROOT / "data/concepts").glob("*.yaml"))
}
claim_hashes = {
    p: digest(p) for p in sorted((ROOT / "data/claims").glob("*.yaml"))
}
source_hashes = {
    p: digest(p) for p in sorted((ROOT / "data/sources").glob("*.yaml"))
}

print("PRECONDITIONS: PASS")

print("\n===== CONCEPT LIFECYCLE SCHEMA =====")

rel = "schema/concept.schema.yaml"
text = read(rel)
if "record_status:\n          const: \"deprecated\"" in text:
    fail("concept lifecycle conditional already appears to exist")

concept_lifecycle = '''allOf:
  - if:
      properties:
        record_status:
          const: "deprecated"
      required:
        - record_status
    then:
      required:
        - replaced_by
      properties:
        replaced_by:
          minItems: 1
    else:
      properties:
        replaced_by:
          maxItems: 0

'''

text = replace_once(
    text,
    "required:\n",
    concept_lifecycle + "required:\n",
    "concept lifecycle schema insertion",
)
write(rel, text)

print("\n===== CLAIM LIFECYCLE SCHEMA =====")

rel = "schema/claim.schema.yaml"
text = read(rel)

old_claim_allof = '''allOf:
  - if:
      properties:
        predicate:
          const: "requires"
      required:
        - predicate
    then:
      required:
        - constraint
      properties:
        modality:
          const: "prescriptive"
    else:
      not:
        required:
          - constraint
  - if:
      properties:
        predicate:
          const: "conventional_for"
      required:
        - predicate
    then:
      properties:
        modality:
          const: "descriptive"

required:
'''

new_claim_allof = '''allOf:
  - if:
      properties:
        predicate:
          const: "requires"
      required:
        - predicate
    then:
      required:
        - constraint
      properties:
        modality:
          const: "prescriptive"
    else:
      not:
        required:
          - constraint
  - if:
      properties:
        predicate:
          const: "conventional_for"
      required:
        - predicate
    then:
      properties:
        modality:
          const: "descriptive"
  - if:
      properties:
        record_status:
          const: "deprecated"
      required:
        - record_status
    then:
      required:
        - replaced_by
      properties:
        replaced_by:
          minItems: 1
    else:
      properties:
        replaced_by:
          maxItems: 0

required:
'''

text = replace_once(
    text,
    old_claim_allof,
    new_claim_allof,
    "claim lifecycle schema conditional",
)
write(rel, text)

print("\n===== CHECKER LIFECYCLE HARDENING =====")

rel = "scripts/pilot_check.py"
text = read(rel)

helper_marker = "\ndef main():\n"
if text.count(helper_marker) != 1:
    fail(f"expected one def main marker, found {text.count(helper_marker)}")

helpers = '''

def validate_lifecycle_replacements(kind_name, items, errors):
    """Validate semantic invariants that JSON Schema cannot express."""
    graph = {}

    for rid, data in items.items():
        replacements = data.get("replaced_by", []) or []

        if rid in replacements:
            errors.append(
                f"{rid}: replaced_by must not reference itself"
            )

        graph[rid] = [
            ref for ref in replacements
            if ref in items
        ]

    state = {}
    stack = []
    stack_pos = {}
    reported = set()

    def visit(node):
        state[node] = 1
        stack_pos[node] = len(stack)
        stack.append(node)

        for nxt in graph.get(node, []):
            nxt_state = state.get(nxt, 0)

            if nxt_state == 0:
                visit(nxt)
            elif nxt_state == 1:
                start = stack_pos[nxt]
                cycle = stack[start:] + [nxt]
                key = tuple(sorted(set(cycle[:-1])))
                if key not in reported:
                    reported.add(key)
                    errors.append(
                        f"{kind_name} replacement cycle: "
                        + " -> ".join(cycle)
                    )

        stack.pop()
        stack_pos.pop(node, None)
        state[node] = 2

    for rid in graph:
        if state.get(rid, 0) == 0:
            visit(rid)


def active_deprecated_reference_warning(
    owner_rel,
    owner_data,
    field,
    ref,
    concepts,
):
    """Return a warning for an active record that points at a deprecated concept."""
    if owner_data.get("record_status") == "deprecated":
        return None

    target = concepts.get(ref)
    if target and target.get("record_status") == "deprecated":
        return (
            f"{owner_rel}: active record references deprecated concept "
            f"{ref} in {field}; historical reference remains valid, "
            "but review for successor migration"
        )

    return None

'''

text = text.replace(helper_marker, helpers + helper_marker, 1)

old_structural = '''        for field in STRUCTURAL_RELATIONS:
            for ref in data.get(field, []) or []:
                if ref not in by_kind["concept"]:
                    errors.append(
                        f"{rel}: missing referenced concept {ref} in {field}"
                    )
'''

new_structural = '''        for field in STRUCTURAL_RELATIONS:
            for ref in data.get(field, []) or []:
                if ref not in by_kind["concept"]:
                    errors.append(
                        f"{rel}: missing referenced concept {ref} in {field}"
                    )
                else:
                    warning = active_deprecated_reference_warning(
                        rel,
                        data,
                        field,
                        ref,
                        by_kind["concept"],
                    )
                    if warning:
                        warnings.append(warning)
'''

text = replace_once(
    text,
    old_structural,
    new_structural,
    "concept deprecated-reference warning",
)

old_concept_end = '''        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing replacement concept {ref}"
                )

    validate_structural_relations(
'''

new_concept_end = '''        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing replacement concept {ref}"
                )

    validate_lifecycle_replacements(
        "concept",
        by_kind["concept"],
        errors,
    )

    validate_structural_relations(
'''

text = replace_once(
    text,
    old_concept_end,
    new_concept_end,
    "concept lifecycle validation call",
)

old_claim_refs = '''        for field in ("subject", "object"):
            ref = data.get(field)
            if isinstance(ref, str) and ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing referenced concept {ref} in {field}"
                )
'''

new_claim_refs = '''        for field in ("subject", "object"):
            ref = data.get(field)
            if isinstance(ref, str) and ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing referenced concept {ref} in {field}"
                )
            elif isinstance(ref, str):
                warning = active_deprecated_reference_warning(
                    rel,
                    data,
                    field,
                    ref,
                    by_kind["concept"],
                )
                if warning:
                    warnings.append(warning)
'''

text = replace_once(
    text,
    old_claim_refs,
    new_claim_refs,
    "claim deprecated-reference warning",
)

old_claim_end = '''        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["claim"]:
                errors.append(
                    f"{rel}: missing replacement claim {ref}"
                )

    log = root / "pilot" / "PILOT_FAILURE_LOG.md"
'''

new_claim_end = '''        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["claim"]:
                errors.append(
                    f"{rel}: missing replacement claim {ref}"
                )

    validate_lifecycle_replacements(
        "claim",
        by_kind["claim"],
        errors,
    )

    log = root / "pilot" / "PILOT_FAILURE_LOG.md"
'''

text = replace_once(
    text,
    old_claim_end,
    new_claim_end,
    "claim lifecycle validation call",
)

selftest_marker = '    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")\n'
if text.count(selftest_marker) != 1:
    fail(
        f"expected one SELF-TEST RESULT marker, "
        f"found {text.count(selftest_marker)}"
    )

tests = '''    # DEPRECATION-01 / rev.11 lifecycle tests.
    item = copy.deepcopy(concept)
    item["id"] = "concept:self-test-deprecated-no-successor"
    item["record_status"] = "deprecated"
    item["replaced_by"] = []
    if schema_errors(schemas["concept"], item):
        print("PASS: deprecated concept without replacement rejected")
    else:
        print("FAIL: deprecated concept without replacement accepted")
        ok = False

    item = copy.deepcopy(concept)
    item["id"] = "concept:self-test-active-with-successor"
    item["record_status"] = "draft"
    item["replaced_by"] = ["concept:self-test-successor"]
    if schema_errors(schemas["concept"], item):
        print("PASS: active concept with replaced_by rejected")
    else:
        print("FAIL: active concept with replaced_by accepted")
        ok = False

    item = copy.deepcopy(claim)
    item["id"] = "claim:self-test-deprecated-with-successor"
    item["record_status"] = "deprecated"
    item["replaced_by"] = ["claim:self-test-successor"]
    if not schema_errors(schemas["claim"], item):
        print("PASS: deprecated claim with replacement accepted")
    else:
        print("FAIL: valid deprecated claim rejected")
        ok = False

    item = copy.deepcopy(claim)
    item["id"] = "claim:self-test-active-with-successor"
    item["record_status"] = "reviewed"
    item["replaced_by"] = ["claim:self-test-successor"]
    if schema_errors(schemas["claim"], item):
        print("PASS: active claim with replaced_by rejected")
    else:
        print("FAIL: active claim with replaced_by accepted")
        ok = False

    life_errors = []
    validate_lifecycle_replacements(
        "concept",
        {
            "concept:a": {
                "record_status": "deprecated",
                "replaced_by": ["concept:a"],
            },
        },
        life_errors,
    )
    if any("must not reference itself" in e for e in life_errors):
        print("PASS: self replacement rejected")
    else:
        print("FAIL: self replacement not detected")
        ok = False

    life_errors = []
    validate_lifecycle_replacements(
        "concept",
        {
            "concept:a": {
                "record_status": "deprecated",
                "replaced_by": ["concept:b"],
            },
            "concept:b": {
                "record_status": "deprecated",
                "replaced_by": ["concept:a"],
            },
        },
        life_errors,
    )
    if any("replacement cycle" in e for e in life_errors):
        print("PASS: replacement cycle rejected")
    else:
        print("FAIL: replacement cycle not detected")
        ok = False

    life_errors = []
    validate_lifecycle_replacements(
        "concept",
        {
            "concept:a": {
                "record_status": "deprecated",
                "replaced_by": ["concept:b"],
            },
            "concept:b": {
                "record_status": "deprecated",
                "replaced_by": ["concept:c"],
            },
            "concept:c": {
                "record_status": "reviewed",
                "replaced_by": [],
            },
        },
        life_errors,
    )
    if not life_errors:
        print("PASS: acyclic replacement chain accepted")
    else:
        print("FAIL: valid replacement chain rejected")
        ok = False

    warning = active_deprecated_reference_warning(
        "data/claims/self-test.yaml",
        {"record_status": "draft"},
        "subject",
        "concept:old",
        {
            "concept:old": {
                "record_status": "deprecated",
                "replaced_by": ["concept:new"],
            },
            "concept:new": {
                "record_status": "reviewed",
                "replaced_by": [],
            },
        },
    )
    if warning and "historical reference remains valid" in warning:
        print("PASS: active reference to deprecated concept warned")
    else:
        print("FAIL: deprecated-reference warning not produced")
        ok = False

'''

text = text.replace(selftest_marker, tests + selftest_marker, 1)
write(rel, text)

print("\n===== FOUNDATION REV.11 =====")

rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)

text = replace_once(
    text,
    "**Status:** Working architecture decision record (rev. 10).",
    "**Status:** Working architecture decision record (rev. 11).",
    "foundation revision",
)

text = replace_once(
    text,
    "opposite_of: []\n",
    "",
    "remove stale opposite_of from live concept example",
)

text = replace_once(
    text,
    "replaced_by: []                 # required when deprecated",
    "replaced_by: []                 # non-empty iff deprecated",
    "concept lifecycle example comment",
)

claim_status = '''evidence_status: unassessed     # unassessed | assessed  (lifecycle only; see §9)
record_status: draft
schema_version: "0.1"
'''

claim_status_new = '''evidence_status: unassessed     # unassessed | assessed  (lifecycle only; see §9)
record_status: draft
replaced_by: []
schema_version: "0.1"
'''

text = replace_once(
    text,
    claim_status,
    claim_status_new,
    "claim lifecycle example",
)

lifecycle_section = '''
### Deprecation and replacement

For concept and claim records in v0.1, deprecation means **supersession while
preserving the old ID**, not deletion.

- `record_status: deprecated` requires a non-empty `replaced_by` list.
- `draft` and `reviewed` records must have an empty or absent
  `replaced_by` list.
- replacement targets must exist and must be the same record kind;
- self-replacement and replacement cycles are invalid;
- acyclic replacement chains are valid. If A was replaced by B and B is later
  replaced by C, A may continue to point to B; historical records need not be
  rewritten merely to shortcut the chain;
- deprecated records remain addressable by immutable ID;
- an active concept or claim may still reference a deprecated concept for
  historical traceability, but the checker emits a warning so the dependency can
  be reviewed for migration to an appropriate successor;
- v0.1 has no tombstone-without-successor state. If the project later needs
  retirement with no replacement, that requires an explicit lifecycle extension
  rather than an empty `replaced_by` on a deprecated record.

A material change to a claim proposition still creates a new claim ID as stated
above. Deprecation metadata records the succession; it does not rewrite the old
proposition.

'''.replace("`", chr(96))

section16 = "\n---\n\n## 16. Superseded decisions"
if text.count(section16) != 1:
    fail(
        "foundation lifecycle insertion: expected one Section 16 marker, "
        f"found {text.count(section16)}"
    )
text = text.replace(
    section16,
    "\n" + lifecycle_section.rstrip() + "\n\n---\n\n## 16. Superseded decisions",
    1,
)

row10 = (
    "| 10 | 2026-09-27 | PF-007-RESOLUTION-01: added `conventional_for` "
    "for descriptive conventional-practice relations; kept predicate semantics "
    "independent from epistemic `basis` so convention status may be supported by "
    "professional convention or empirical observation without converting the relation "
    "into an effect, standard, or prescription. |"
).replace("`", chr(96))

row11 = (
    row10
    + "\n| 11 | 2026-09-27 | DEPRECATION-01 lifecycle hardening: deprecated concept/claim "
      "records now require non-empty `replaced_by`; active records may not carry "
      "successors; self-links and replacement cycles are invalid; acyclic replacement "
      "chains remain valid; active references to deprecated concepts remain resolvable "
      "but produce review warnings; removed stale live `opposite_of` from the Concept "
      "example. |"
).replace("`", chr(96))

text = replace_once(
    text,
    row10,
    row11,
    "foundation decision row 10",
)
write(rel, text)

print("\n===== PILOT RECORD =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)

block = '''
## DEPRECATION-01

- [x] Confirmed there were no canonical deprecated records before the test.
- [x] Reconciled Foundation lifecycle intent with executable schema/checker rules.
- [x] `deprecated` concept/claim records require non-empty `replaced_by`.
- [x] `draft` / `reviewed` records reject non-empty `replaced_by`.
- [x] Missing replacement targets remain hard errors.
- [x] Self-replacement is a hard error.
- [x] Replacement cycles are hard errors.
- [x] Acyclic replacement chains are valid and preserve historical succession.
- [x] Active concept/claim references to deprecated concepts remain valid but warn.
- [x] Deprecated records remain addressable; files are not deleted.
- [x] v0.1 intentionally does not model retirement-without-successor.
- [x] Added permanent lifecycle self-tests.
- [x] Removed stale live `opposite_of: []` from the Foundation Concept example.
- [x] No canonical data record was mutated.
- [x] Foundation advanced rev. 10 → rev. 11.
- [x] Outcome: `PASS`.
'''.replace("`", chr(96))

write(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

print("\n===== FINAL VALIDATION =====")

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
for expected in (
    "PASS: deprecated concept without replacement rejected",
    "PASS: active concept with replaced_by rejected",
    "PASS: deprecated claim with replacement accepted",
    "PASS: active claim with replaced_by rejected",
    "PASS: self replacement rejected",
    "PASS: replacement cycle rejected",
    "PASS: acyclic replacement chain accepted",
    "PASS: active reference to deprecated concept warned",
    "SELF-TEST RESULT: PASS",
):
    if expected not in out:
        fail(f"missing expected self-test line: {expected}")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")

run("git", "diff", "--check")

if counts() != BASELINE:
    fail(f"record counts changed: expected {BASELINE}, got {counts()}")

print("\n===== CANONICAL DATA IMMUTABILITY =====")
for collection in (concept_hashes, claim_hashes, source_hashes):
    for path, before in collection.items():
        if digest(path) != before:
            fail(f"canonical data changed: {path.relative_to(ROOT)}")
print("PASS: all 54 canonical records unchanged")

foundation = read("docs/PROJECT_FOUNDATION.md")
if "(rev. 11)" not in foundation:
    fail("Foundation did not advance to rev. 11")
if "opposite_of: []" in foundation:
    fail("stale live opposite_of example remains")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: PASS")
print("PILOT: DEPRECATION-01")
print("Foundation: rev. 11")
print("deprecated + empty replaced_by: REJECTED")
print("active + non-empty replaced_by: REJECTED")
print("missing replacement target: REJECTED")
print("self replacement: REJECTED")
print("replacement cycle: REJECTED")
print("acyclic replacement chain: ALLOWED")
print("active reference to deprecated concept: VALID_WITH_WARNING")
print("deprecated IDs: REMAIN ADDRESSABLE")
print("tombstone without successor: NOT MODELED IN V0.1")
print("COUNTS: 54 records — 28 concepts, 9 claims, 17 sources")
print("Canonical data records: unchanged")
print("No commit or push performed.")
