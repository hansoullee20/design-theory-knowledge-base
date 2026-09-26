#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

TMP_PY="$(mktemp /tmp/pf006-resolution-01.XXXXXX.py)"
trap 'rm -f "$TMP_PY"' EXIT

cat > "$TMP_PY" <<'PY'
from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

EXPECTED = (43, 23, 6, 14)


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8") if p.exists() else None
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
    fail(f"expected branch main, got {branch!r}")

foundation = read("docs/PROJECT_FOUNDATION.md")
if "(rev. 8)" not in foundation:
    fail("expected Foundation rev. 8")

if counts() != EXPECTED:
    fail(f"expected corpus {EXPECTED}, got {counts()}")

failure_log = read("pilot/PILOT_FAILURE_LOG.md")
if "PF-006" not in failure_log or "OPEN" not in failure_log:
    fail("PF-006 OPEN entry not found")

pilot_records = read("pilot/PILOT_RECORDS.md")
if "## WCAG-01" not in pilot_records or "CLAIM_SCHEMA_GAP" not in pilot_records:
    fail("WCAG-01 CLAIM_SCHEMA_GAP record not found")

schema0 = yaml.safe_load(read("schema/claim.schema.yaml"))
pred0 = schema0["properties"]["predicate"]["enum"]
if pred0 != ["increases", "decreases", "influences"]:
    fail(f"unexpected starting predicate enum: {pred0!r}")
if "constraint" in schema0["properties"]:
    fail("constraint already exists in claim schema")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

claim_files = sorted((ROOT / "data/claims").glob("*.yaml"))
if len(claim_files) != 6:
    fail(f"expected 6 existing canonical claims, found {len(claim_files)}")
claim_hashes = {p: digest(p) for p in claim_files}

print("PRECONDITIONS: PASS")

print("\n===== PREDICATE VOCAB =====")

rel = "vocab/predicates.yaml"
text = read(rel)
text = replace_once(
    text,
    """values:
  - increases
  - decreases
  - influences
""",
    """values:
  - increases
  - decreases
  - influences
  - requires
""",
    "predicate vocab",
)
write(rel, text)

print("\n===== CLAIM SCHEMA =====")

rel = "schema/claim.schema.yaml"
text = read(rel)

text = replace_once(
    text,
    """type: object
additionalProperties: false

required:
""",
    """type: object
additionalProperties: false

allOf:
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

required:
""",
    "claim schema conditional",
)

text = replace_once(
    text,
    """  predicate:
    enum:
      - "increases"
      - "decreases"
      - "influences"

  object:
""",
    """  predicate:
    enum:
      - "increases"
      - "decreases"
      - "influences"
      - "requires"

  object:
""",
    "claim schema predicate",
)

text = replace_once(
    text,
    """  object:
    type: string
    pattern: "^concept:[a-z0-9]+(?:-[a-z0-9]+)*$"

  basis:
""",
    """  object:
    type: string
    pattern: "^concept:[a-z0-9]+(?:-[a-z0-9]+)*$"

  constraint:
    type: object
    additionalProperties: false
    required:
      - operator
      - value
      - unit
    properties:
      operator:
        enum:
          - "gte"
          - "lte"
          - "gt"
          - "lt"
          - "eq"
      value:
        type: number
      unit:
        type: string
        minLength: 1

  basis:
""",
    "claim schema constraint",
)

write(rel, text)

print("\n===== CHECKER SELF-TESTS =====")

rel = "scripts/pilot_check.py"
text = read(rel)

text = replace_once(
    text,
    '''    concepts = sorted((root / "data" / "concepts").glob("*.yaml"))
    sources = sorted((root / "data" / "sources").glob("*.yaml"))

    if not concepts or not sources:
        print("SELF-TEST FAIL: requires at least one concept and source record")
        return False

    concept = yaml.safe_load(concepts[0].read_text(encoding="utf-8"))
    source = yaml.safe_load(sources[0].read_text(encoding="utf-8"))

    cases = []
''',
    '''    concepts = sorted((root / "data" / "concepts").glob("*.yaml"))
    claims = sorted((root / "data" / "claims").glob("*.yaml"))
    sources = sorted((root / "data" / "sources").glob("*.yaml"))

    if not concepts or not claims or not sources:
        print(
            "SELF-TEST FAIL: requires at least one concept, claim, and source record"
        )
        return False

    concept = yaml.safe_load(concepts[0].read_text(encoding="utf-8"))
    claim = yaml.safe_load(claims[0].read_text(encoding="utf-8"))
    source = yaml.safe_load(sources[0].read_text(encoding="utf-8"))

    cases = []
''',
    "checker self-test fixtures",
)

marker = '    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")\n'
if text.count(marker) != 1:
    fail(
        "checker injection marker: expected exactly one SELF-TEST RESULT line, "
        f"found {text.count(marker)}"
    )

tests = '''    # PF-006 / rev.9 normative-threshold schema tests.
    req = copy.deepcopy(claim)
    req["id"] = "claim:self-test-requires-constraint"
    req["predicate"] = "requires"
    req["modality"] = "prescriptive"
    req["constraint"] = {
        "operator": "gte",
        "value": 4.5,
        "unit": "ratio",
    }

    if not schema_errors(schemas["claim"], req):
        print("PASS: requires claim with structured constraint accepted")
    else:
        print("FAIL: valid requires claim rejected")
        ok = False

    item = copy.deepcopy(req)
    item.pop("constraint", None)
    if schema_errors(schemas["claim"], item):
        print("PASS: requires claim without constraint rejected")
    else:
        print("FAIL: requires claim without constraint incorrectly accepted")
        ok = False

    item = copy.deepcopy(req)
    item["predicate"] = "influences"
    if schema_errors(schemas["claim"], item):
        print("PASS: constraint on non-requires claim rejected")
    else:
        print("FAIL: constraint on non-requires claim incorrectly accepted")
        ok = False

    item = copy.deepcopy(req)
    item["modality"] = "descriptive"
    if schema_errors(schemas["claim"], item):
        print("PASS: non-prescriptive requires claim rejected")
    else:
        print("FAIL: non-prescriptive requires claim incorrectly accepted")
        ok = False

    item = copy.deepcopy(req)
    item["constraint"]["operator"] = "approximately"
    if schema_errors(schemas["claim"], item):
        print("PASS: invalid constraint operator rejected")
    else:
        print("FAIL: invalid constraint operator incorrectly accepted")
        ok = False

'''

text = text.replace(marker, tests + marker, 1)
write(rel, text)

print("\n===== FOUNDATION REV.9 =====")

rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)

text = replace_once(
    text,
    "**Status:** Working architecture decision record (rev. 8).",
    "**Status:** Working architecture decision record (rev. 9).",
    "foundation revision",
)

text = replace_once(
    text,
    "predicate: increases            # increases | decreases | influences",
    "predicate: increases            # increases | decreases | influences | requires",
    "foundation predicate example",
)

normative = '''### Normative threshold claims

The claim graph remains concept-to-concept: `subject` and `object` remain
concept IDs. A codified quantitative requirement uses `predicate: requires`
with a structured `constraint`.

```yaml
modality: prescriptive
subject: concept:text-contrast
predicate: requires
object: concept:contrast-ratio
constraint:
  operator: gte
  value: 4.5
  unit: ratio
basis: [standard]
```

For Taxonomy v0.1:

- `requires` is valid only with `modality: prescriptive`;
- `requires` must carry `constraint`;
- `constraint` is forbidden on other predicates;
- operators are `gte`, `lte`, `gt`, `lt`, and `eq`;
- `value` is numeric;
- `unit` is a non-empty string;
- `subject` and `object` remain concept IDs;
- operator, value, and unit are proposition-bearing. Changing any of them
  creates a successor claim ID.

This does not create literal claim objects or a units ontology. Exceptions and
applicability conditions remain in `scope` and source-backed statement text.

'''.replace("`", chr(96))

text = replace_once(
    text,
    "### Source\n",
    normative + "### Source\n",
    "foundation normative-threshold section",
)

row8 = (
    "| 8 | 2026-09-26 | PRE-FREEZE-HARDENING-01: clarified direct asserted "
    "`is_a` storage and derived closure; constrained `part_of` transitivity to "
    "compatible constituent senses and excluded collection membership; added "
    "`related`/hierarchy overlap warnings, stronger cycle self-test coverage, "
    "clearer locus-mismatch diagnostics, and documented the directional-edge "
    "review limitation. |"
).replace("`", chr(96))

row9 = (
    row8
    + "\n| 9 | 2026-09-27 | PF-006-RESOLUTION-01: preserved concept-to-concept "
      "claim endpoints and runtime inverse lookup; added `requires` for codified "
      "normative requirements plus predicate-bound structured `constraint` "
      "(`operator`, numeric `value`, `unit`); `requires` is prescriptive and must "
      "carry a constraint; constraints are forbidden on other v0.1 predicates. |"
).replace("`", chr(96))

text = replace_once(text, row8, row9, "foundation decision row 8")
write(rel, text)

print("\n===== RUNTIME CONTRACT =====")

rel = "docs/PLUGIN_TARGET_ARCHITECTURE.md"
text = read(rel)

needle = (
    "What makes this contract possible is §15 of the foundation: IDs name senses, "
    "never move, never encode classification. The contract assumes nothing else about storage."
)

replacement = (
    needle
    + "\n\nNormative `constraint` data is returned with the claim record payload. "
      "It adds no v0.1 retrieval parameter: "
      "`find_claims(subject?, predicate?, object?, modality?, basis?)` remains "
      "unchanged, and `subject` / `object` remain concept IDs."
).replace("`", chr(96))

text = replace_once(text, needle, replacement, "runtime constraint note")
write(rel, text)

print("\n===== SCRATCH WCAG CLAIM =====")

schema = yaml.safe_load(read("schema/claim.schema.yaml"))
Draft202012Validator.check_schema(schema)

scratch = {
    "id": "claim:wcag-contrast-minimum-scratch",
    "kind": "claim",
    "statement": (
        "WCAG 2.2 SC 1.4.3 requires normal text to have a contrast ratio "
        "of at least 4.5:1."
    ),
    "modality": "prescriptive",
    "subject": "concept:text-contrast",
    "predicate": "requires",
    "object": "concept:contrast-ratio",
    "constraint": {
        "operator": "gte",
        "value": 4.5,
        "unit": "ratio",
    },
    "basis": ["standard"],
    "evidence_status": "unassessed",
    "scope": "Scratch representation test only.",
    "sources": ["source:w3c-wcag-2-2"],
    "record_status": "draft",
    "replaced_by": [],
    "notes": "Non-canonical PF-006 representation test.",
    "schema_version": "0.1",
}

errors = list(Draft202012Validator(schema).iter_errors(scratch))
if errors:
    fail("; ".join(e.message for e in errors))

td = Path(tempfile.mkdtemp(prefix="pf006-resolution-01-"))
scratch_path = td / "wcag-threshold-scratch.yaml"
scratch_path.write_text(
    yaml.safe_dump(scratch, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
)
print("SCRATCH:", scratch_path)
print("SCRATCH SCHEMA VALIDATION: PASS")

print("\n===== PILOT RECORD =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)
if "## PF-006-RESOLUTION-01" in text:
    fail("PF-006-RESOLUTION-01 already logged")

block = '''
## PF-006-RESOLUTION-01

- [x] Preserved concept-to-concept claim endpoints.
- [x] Preserved the existing runtime claim lookup signature.
- [x] Added `requires` plus structured `constraint`.
- [x] Bound `requires` to prescriptive modality and mandatory constraint.
- [x] Forbid constraints on other v0.1 predicates.
- [x] Added permanent positive and negative checker self-tests.
- [x] Scratch WCAG threshold claim passed schema validation.
- [x] Six existing canonical claim files remained byte-for-byte unchanged.
- [x] Corpus count remained unchanged.
- [x] Foundation advanced rev. 8 → rev. 9.
- [x] Outcome: `PF-006_RESOLVED`.
'''.replace("`", chr(96))

write(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

print("\n===== FAILURE LOG =====")

rel = "pilot/PILOT_FAILURE_LOG.md"
text = read(rel)

text = replace_once(
    text,
    "**PF-006 — OPEN — normative threshold claim representation.**",
    "**PF-006 — RESOLVED — normative threshold claim representation.**",
    "PF-006 status",
)

write(rel, text)

print("\n===== FINAL VALIDATION =====")

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
for required in (
    "PASS: requires claim with structured constraint accepted",
    "PASS: requires claim without constraint rejected",
    "PASS: constraint on non-requires claim rejected",
    "PASS: non-prescriptive requires claim rejected",
    "PASS: invalid constraint operator rejected",
    "SELF-TEST RESULT: PASS",
):
    if required not in out:
        fail(f"missing expected self-test line: {required}")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")

run("git", "diff", "--check")

if counts() != EXPECTED:
    fail(f"record counts changed unexpectedly: {counts()}")

print("\n===== EXISTING CLAIM IMMUTABILITY =====")
for path, before in claim_hashes.items():
    if digest(path) != before:
        fail(f"existing canonical claim changed: {path.relative_to(ROOT)}")
    print("PASS:", path.relative_to(ROOT))

schema1 = yaml.safe_load(read("schema/claim.schema.yaml"))
if schema1["properties"]["predicate"]["enum"] != [
    "increases",
    "decreases",
    "influences",
    "requires",
]:
    fail("unexpected final predicate enum")

if "(rev. 9)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation did not advance to rev. 9")

if "**PF-006 — RESOLVED" not in read("pilot/PILOT_FAILURE_LOG.md"):
    fail("PF-006 was not marked RESOLVED")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: PF-006_RESOLVED")
print("Foundation: rev. 9")
print("predicate: requires — ACTIVE")
print("constraint: ACTIVE, requires-bound")
print("COUNTS: 43 records — 23 concepts, 6 claims, 14 sources")
print("Existing canonical claims: unchanged")
print("Runtime claim lookup signature: unchanged")
print("No canonical WCAG claim minted.")
print("No commit or push performed.")
PY

python3 "$TMP_PY"
