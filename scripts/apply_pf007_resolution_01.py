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

BASELINE = (49, 27, 7, 15)
EXPECTED = (50, 27, 8, 15)


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


def write_new(rel: str, text: str) -> None:
    p = ROOT / rel
    if p.exists():
        fail(f"refusing to overwrite existing file: {rel}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"CREATED: {rel}")


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


def dump(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


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

failure_log = read("pilot/PILOT_FAILURE_LOG.md")
if "**PF-007 — OPEN — conventional-practice claim predicate.**" not in failure_log:
    fail("PF-007 OPEN entry not found")

pilot_records = read("pilot/PILOT_RECORDS.md")
if "## LEFT-ALIGNMENT-01" not in pilot_records or "CLAIM_PREDICATE_GAP" not in pilot_records:
    fail("LEFT-ALIGNMENT-01 predicate-gap record not found")

for rel in (
    "data/sources/lupton-2010-thinking-with-type.yaml",
    "data/concepts/left-alignment.yaml",
    "data/concepts/body-text.yaml",
):
    if not (ROOT / rel).exists():
        fail(f"missing LEFT-ALIGNMENT-01 prerequisite: {rel}")

claim_rel = "data/claims/left-alignment-conventional-for-body-text.yaml"
if (ROOT / claim_rel).exists():
    fail(f"canonical retest claim already exists: {claim_rel}")

schema0 = yaml.safe_load(read("schema/claim.schema.yaml"))
pred0 = schema0["properties"]["predicate"]["enum"]
if pred0 != ["increases", "decreases", "influences", "requires"]:
    fail(f"unexpected starting predicates: {pred0!r}")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")
print("PRECONDITIONS: PASS")

existing_claims = sorted((ROOT / "data/claims").glob("*.yaml"))
claim_hashes = {p: digest(p) for p in existing_claims}

print("\n===== PREDICATE VOCAB =====")

rel = "vocab/predicates.yaml"
text = read(rel)
text = replace_once(
    text,
    """  - influences
  - requires
""",
    """  - influences
  - requires
  - conventional_for
""",
    "predicate vocab",
)
write(rel, text)

print("\n===== CLAIM SCHEMA =====")

rel = "schema/claim.schema.yaml"
text = read(rel)

text = replace_once(
    text,
    """      - "influences"
      - "requires"

  object:
""",
    """      - "influences"
      - "requires"
      - "conventional_for"

  object:
""",
    "claim predicate enum",
)

old_allof = """allOf:
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
"""

new_allof = """allOf:
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
"""

text = replace_once(text, old_allof, new_allof, "claim modality conditional")
write(rel, text)

print("\n===== CHECKER SELF-TESTS =====")

rel = "scripts/pilot_check.py"
text = read(rel)
marker = '    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")\n'
if text.count(marker) != 1:
    fail(f"expected one SELF-TEST RESULT marker, found {text.count(marker)}")

tests = '''    # PF-007 / rev.10 conventional-practice predicate tests.
    conv = copy.deepcopy(claim)
    conv["id"] = "claim:self-test-conventional-for"
    conv["predicate"] = "conventional_for"
    conv["modality"] = "descriptive"
    conv["basis"] = ["conventional"]
    conv.pop("constraint", None)

    if not schema_errors(schemas["claim"], conv):
        print("PASS: descriptive conventional_for claim accepted")
    else:
        print("FAIL: valid conventional_for claim rejected")
        ok = False

    item = copy.deepcopy(conv)
    item["modality"] = "prescriptive"
    if schema_errors(schemas["claim"], item):
        print("PASS: non-descriptive conventional_for claim rejected")
    else:
        print("FAIL: prescriptive conventional_for claim incorrectly accepted")
        ok = False

    item = copy.deepcopy(conv)
    item["basis"] = ["empirical"]
    if not schema_errors(schemas["claim"], item):
        print("PASS: conventional_for remains independent of evidence basis")
    else:
        print("FAIL: conventional_for incorrectly bound to conventional basis")
        ok = False

'''

text = text.replace(marker, tests + marker, 1)
write(rel, text)

print("\n===== FOUNDATION REV.10 =====")

rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)

text = replace_once(
    text,
    "**Status:** Working architecture decision record (rev. 9).",
    "**Status:** Working architecture decision record (rev. 10).",
    "foundation revision",
)

text = replace_once(
    text,
    "predicate: increases            # increases | decreases | influences | requires",
    "predicate: increases            # increases | decreases | influences | requires | conventional_for",
    "foundation predicate example",
)

section = '''### Conventional-practice claims

`conventional_for` records that the subject is an established or familiar
design practice for the object within the stated scope. It is a descriptive
relation. It does **not** assert causal benefit, empirical superiority, formal
standard status, or universal prescription.

The predicate and epistemic basis remain orthogonal. For example, a claim that
left alignment is conventional for body text may use `basis: [conventional]`
when grounded in learned expectation or professional practice, while an empirical
survey of actual practice could support the same `conventional_for` proposition
with `basis: [empirical]`. The predicate therefore must not be schema-bound
to the `conventional` basis.

'''.replace("`", chr(96))

text = replace_once(
    text,
    "### Normative threshold claims\n",
    section + "### Normative threshold claims\n",
    "foundation conventional-practice section",
)

row9 = (
    "| 9 | 2026-09-27 | PF-006-RESOLUTION-01: preserved concept-to-concept "
    "claim endpoints and runtime inverse lookup; added `requires` for codified "
    "normative requirements plus predicate-bound structured `constraint` "
    "(`operator`, numeric `value`, `unit`); `requires` is prescriptive and must "
    "carry a constraint; constraints are forbidden on other v0.1 predicates. |"
).replace("`", chr(96))

row10 = (
    row9
    + "\n| 10 | 2026-09-27 | PF-007-RESOLUTION-01: added `conventional_for` "
      "for descriptive conventional-practice relations; kept predicate semantics "
      "independent from epistemic `basis` so convention status may be supported by "
      "professional convention or empirical observation without converting the relation "
      "into an effect, standard, or prescription. |"
).replace("`", chr(96))

text = replace_once(text, row9, row10, "foundation decision row 9")
write(rel, text)

print("\n===== CANONICAL LEFT-ALIGNMENT CLAIM =====")

claim = {
    "id": "claim:left-alignment-conventional-for-body-text",
    "kind": "claim",
    "statement": (
        "In left-to-right Latin typography, left alignment is a familiar "
        "convention for long body text."
    ),
    "modality": "descriptive",
    "subject": "concept:left-alignment",
    "predicate": "conventional_for",
    "object": "concept:body-text",
    "basis": ["conventional"],
    "evidence_status": "unassessed",
    "scope": (
        "Left-to-right Latin typography and long-form body text. This records "
        "typographic familiarity and practice, not a universal prescription, "
        "formal standard, or claim of empirical superiority in readability."
    ),
    "sources": ["source:lupton-2010-thinking-with-type"],
    "record_status": "draft",
    "replaced_by": [],
    "notes": (
        "LEFT-ALIGNMENT-01 canonical retest after PF-007 resolution. "
        "Convention is represented as proposition semantics, independently from "
        "the claim's epistemic basis."
    ),
    "schema_version": "0.1",
}
write_new(claim_rel, dump(claim))

print("\n===== PILOT / FAILURE LOG =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)
if "## PF-007-RESOLUTION-01" in text:
    fail("PF-007-RESOLUTION-01 already logged")

block = '''
## PF-007-RESOLUTION-01 / LEFT-ALIGNMENT-01-RETEST

- [x] Added `conventional_for` as a descriptive concept-to-concept claim predicate.
- [x] Kept `predicate` semantics independent from epistemic `basis`.
- [x] Added permanent self-tests: descriptive use accepted; non-descriptive use rejected; empirical basis remains structurally possible.
- [x] Minted `claim:left-alignment-conventional-for-body-text`.
- [x] Canonical claim uses `modality: descriptive` and `basis: [conventional]`.
- [x] Scope explicitly excludes universal prescription, formal-standard status, and empirical-superiority claims.
- [x] No existing canonical claim was modified.
- [x] Foundation advanced rev. 9 → rev. 10.
- [x] PF-007 outcome: `RESOLVED`.
- [x] LEFT-ALIGNMENT-01 retest outcome: `PASS`.
'''.replace("`", chr(96))
write(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

rel = "pilot/PILOT_FAILURE_LOG.md"
text = read(rel)
text = replace_once(
    text,
    "**PF-007 — OPEN — conventional-practice claim predicate.**",
    "**PF-007 — RESOLVED — conventional-practice claim predicate.**",
    "PF-007 status",
)
write(rel, text)

print("\n===== FINAL VALIDATION =====")

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
for expected_line in (
    "PASS: descriptive conventional_for claim accepted",
    "PASS: non-descriptive conventional_for claim rejected",
    "PASS: conventional_for remains independent of evidence basis",
    "SELF-TEST RESULT: PASS",
):
    if expected_line not in out:
        fail(f"missing expected self-test line: {expected_line}")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")

run("git", "diff", "--check")

if counts() != EXPECTED:
    fail(f"expected final counts {EXPECTED}, got {counts()}")

print("\n===== EXISTING CLAIM IMMUTABILITY =====")
for path, before in claim_hashes.items():
    if digest(path) != before:
        fail(f"existing canonical claim changed: {path.relative_to(ROOT)}")
    print("PASS:", path.relative_to(ROOT))

schema1 = yaml.safe_load(read("schema/claim.schema.yaml"))
if schema1["properties"]["predicate"]["enum"] != [
    "increases", "decreases", "influences", "requires", "conventional_for"
]:
    fail("unexpected final predicate enum")

if "(rev. 10)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation did not advance to rev. 10")

if "**PF-007 — RESOLVED" not in read("pilot/PILOT_FAILURE_LOG.md"):
    fail("PF-007 not marked RESOLVED")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: PF-007_RESOLVED")
print("PILOT: LEFT-ALIGNMENT-01-RETEST — PASS")
print("Foundation: rev. 10")
print("predicate: conventional_for — ACTIVE")
print("modality: descriptive")
print("basis independence: PRESERVED")
print("CLAIM: claim:left-alignment-conventional-for-body-text")
print("COUNTS: 50 records — 27 concepts, 8 claims, 15 sources")
print("Existing canonical claims: unchanged")
print("Runtime claim lookup signature: unchanged")
print("No commit or push performed.")
