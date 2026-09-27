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
BRANCH = "pf001-provenance"
TAG = "taxonomy-v0.1"
WCAG_REL = "data/claims/wcag-text-presentation-requires-minimum-contrast-ratio.yaml"
BT = chr(96)


def fail(msg):
    raise SystemExit("ERROR: " + msg)


def read(rel):
    p = ROOT / rel
    if not p.exists():
        fail("missing required file: " + rel)
    return p.read_text(encoding="utf-8")


def write(rel, text):
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print("UNCHANGED:", rel)
        return
    p.write_text(text, encoding="utf-8")
    print("UPDATED:", rel)


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        fail(label + ": expected exactly 1 match, found " + str(n))
    return text.replace(old, new, 1)


def counts():
    c = list((ROOT / "data/concepts").glob("*.yaml"))
    q = list((ROOT / "data/claims").glob("*.yaml"))
    s = list((ROOT / "data/sources").glob("*.yaml"))
    return (len(c) + len(q) + len(s), len(c), len(q), len(s))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout


LOCATOR_DEFS = """$defs:
  source_selector:
    oneOf:
      - {type: object, additionalProperties: false, required: [type, value], properties: {type: {const: PageSelector}, value: {type: string, minLength: 1}}}
      - {type: object, additionalProperties: false, required: [type, value], properties: {type: {const: SectionSelector}, value: {type: string, minLength: 1}}}
      - {type: object, additionalProperties: false, required: [type, value], properties: {type: {const: FigureSelector}, value: {type: string, minLength: 1}}}
      - {type: object, additionalProperties: false, required: [type, value], properties: {type: {const: TableSelector}, value: {type: string, minLength: 1}}}
      - type: object
        additionalProperties: false
        required: [type, value]
        properties:
          type: {const: FragmentSelector}
          value: {type: string, minLength: 1}
          conforms_to: {type: string, minLength: 1}
      - type: object
        additionalProperties: false
        required: [type, exact]
        properties:
          type: {const: TextQuoteSelector}
          exact: {type: string, minLength: 1}
          prefix: {type: string, minLength: 1}
          suffix: {type: string, minLength: 1}
  source_locator:
    type: object
    additionalProperties: false
    required: [source, selector]
    properties:
      source: {type: string, pattern: "^source:[a-z0-9]+(?:-[a-z0-9]+)*$"}
      selector: {$ref: "#/$defs/source_selector"}

"""


def add_defs(text, label):
    marker = "additionalProperties: false\n\n"
    if text.count(marker) != 1:
        fail(label + ": top-level schema marker mismatch")
    return text.replace(marker, marker + LOCATOR_DEFS, 1)


print("===== PF-001-RESOLUTION-01 =====")
branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != BRANCH:
    fail("expected branch " + BRANCH + ", got " + branch)

if subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=ROOT, text=True
).strip():
    fail("working tree must be clean before PF-001 migration")

freeze = subprocess.check_output(
    ["git", "rev-list", "-n", "1", TAG], cwd=ROOT, text=True
).strip()
head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
).strip()
if head != freeze:
    fail("PF-001 branch must start exactly at taxonomy-v0.1")

if counts() != BASELINE:
    fail("expected frozen corpus " + repr(BASELINE) + ", got " + repr(counts()))

foundation = read("docs/PROJECT_FOUNDATION.md")
if "Taxonomy v0.1 frozen architecture checkpoint (rev. 12)" not in foundation:
    fail("expected Foundation rev.12 frozen baseline")

failure = read("pilot/PILOT_FAILURE_LOG.md")
if "| PF-001 |" not in failure or "| open |" not in failure:
    fail("PF-001 open row missing")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

claim_before = {
    p: sha(p) for p in sorted((ROOT / "data/claims").glob("*.yaml"))
}
concept_before = {
    p: sha(p) for p in sorted((ROOT / "data/concepts").glob("*.yaml"))
}
source_before = {
    p: sha(p) for p in sorted((ROOT / "data/sources").glob("*.yaml"))
}
print("PRECONDITIONS: PASS")

# Add optional locator fields to claim schema.
rel = "schema/claim.schema.yaml"
text = add_defs(read(rel), rel)
old = """  sources:
    type: array
    minItems: 1
    uniqueItems: true
    items:
      type: string
      pattern: "^source:[a-z0-9]+(?:-[a-z0-9]+)*$"

  record_status:
"""
new = """  sources:
    type: array
    minItems: 1
    uniqueItems: true
    items:
      type: string
      pattern: "^source:[a-z0-9]+(?:-[a-z0-9]+)*$"

  source_locators:
    type: array
    uniqueItems: true
    items: {$ref: "#/$defs/source_locator"}
    default: []

  record_status:
"""
write(rel, replace_once(text, old, new, "claim source_locators"))

# Add optional locator fields to concept schema.
rel = "schema/concept.schema.yaml"
text = add_defs(read(rel), rel)
old = """  definition_sources:
    type: array
    minItems: 1
    uniqueItems: true
    items:
      type: string
      pattern: "^source:[a-z0-9]+(?:-[a-z0-9]+)*$"

  locus:
"""
new = """  definition_sources:
    type: array
    minItems: 1
    uniqueItems: true
    items:
      type: string
      pattern: "^source:[a-z0-9]+(?:-[a-z0-9]+)*$"

  definition_source_locators:
    type: array
    uniqueItems: true
    items: {$ref: "#/$defs/source_locator"}
    default: []

  locus:
"""
write(rel, replace_once(text, old, new, "concept definition_source_locators"))

# Checker: locator source must occur in corresponding legacy source array.
rel = "scripts/pilot_check.py"
text = read(rel)
helper = """

def validate_relation_source_locators(
    rel,
    data,
    source_field,
    locator_field,
    errors,
):
    source_ids = set(data.get(source_field, []) or [])
    for index, locator in enumerate(data.get(locator_field, []) or []):
        if not isinstance(locator, dict):
            continue
        source = locator.get("source")
        if isinstance(source, str) and source not in source_ids:
            errors.append(
                f"{rel}: {locator_field}[{index}].source {source} "
                f"must also appear in {source_field}"
            )

"""
text = replace_once(
    text,
    "\ndef main():\n",
    helper + "\ndef main():\n",
    "checker locator helper",
)

old = """        for source in data.get("definition_sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        for field in STRUCTURAL_RELATIONS:
"""
new = """        for source in data.get("definition_sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        validate_relation_source_locators(
            rel,
            data,
            "definition_sources",
            "definition_source_locators",
            errors,
        )

        for field in STRUCTURAL_RELATIONS:
"""
text = replace_once(text, old, new, "concept locator validation")

old = """        for source in data.get("sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        for ref in data.get("replaced_by", []) or []:
"""
new = """        for source in data.get("sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        validate_relation_source_locators(
            rel,
            data,
            "sources",
            "source_locators",
            errors,
        )

        for ref in data.get("replaced_by", []) or []:
"""
text = replace_once(text, old, new, "claim locator validation")

marker = '    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")\n'
tests = """    # PF-001 relation-level locator self-tests.
    selectors = [
        {"type": "PageSelector", "value": "42"},
        {"type": "SectionSelector", "value": "SC 1.4.3"},
        {"type": "FigureSelector", "value": "Figure 2"},
        {"type": "TableSelector", "value": "Table 3"},
        {
            "type": "FragmentSelector",
            "value": "contrast-minimum",
            "conforms_to": "text/html",
        },
        {
            "type": "TextQuoteSelector",
            "exact": "supporting passage",
            "prefix": "before",
            "suffix": "after",
        },
    ]
    bad = []
    for selector in selectors:
        item = copy.deepcopy(claim)
        item["source_locators"] = [
            {"source": item["sources"][0], "selector": selector}
        ]
        bad.extend(schema_errors(schemas["claim"], item))
    if not bad:
        print("PASS: all supported source selector shapes accepted")
    else:
        print("FAIL: valid source selector shape rejected")
        ok = False

    item = copy.deepcopy(claim)
    item["source_locators"] = [
        {
            "source": item["sources"][0],
            "selector": {"type": "UnknownSelector", "value": "x"},
        }
    ]
    if schema_errors(schemas["claim"], item):
        print("PASS: unknown source selector type rejected")
    else:
        print("FAIL: unknown source selector type accepted")
        ok = False

    item = copy.deepcopy(claim)
    item["source_locators"] = [
        {
            "source": item["sources"][0],
            "selector": {"type": "TextQuoteSelector", "exact": ""},
        }
    ]
    if schema_errors(schemas["claim"], item):
        print("PASS: empty text-quote exact value rejected")
    else:
        print("FAIL: empty text-quote exact value accepted")
        ok = False

    item = copy.deepcopy(claim)
    item["source_locators"] = [{"source": item["sources"][0]}]
    if schema_errors(schemas["claim"], item):
        print("PASS: locator without selector rejected")
    else:
        print("FAIL: locator without selector accepted")
        ok = False

    errs = []
    item = copy.deepcopy(claim)
    item["source_locators"] = [
        {
            "source": "source:not-in-claim-sources",
            "selector": {"type": "SectionSelector", "value": "1"},
        }
    ]
    validate_relation_source_locators(
        "self-test", item, "sources", "source_locators", errs
    )
    if any("must also appear in sources" in e for e in errs):
        print("PASS: claim locator source must occur in sources")
    else:
        print("FAIL: claim locator/source mismatch not detected")
        ok = False

    errs = []
    item = copy.deepcopy(concept)
    item["definition_source_locators"] = [
        {
            "source": "source:not-in-definition-sources",
            "selector": {"type": "PageSelector", "value": "9"},
        }
    ]
    validate_relation_source_locators(
        "self-test",
        item,
        "definition_sources",
        "definition_source_locators",
        errs,
    )
    if any("must also appear in definition_sources" in e for e in errs):
        print("PASS: definition locator source must occur in definition_sources")
    else:
        print("FAIL: definition locator/source mismatch not detected")
        ok = False

    item = copy.deepcopy(claim)
    locator = {
        "source": item["sources"][0],
        "selector": {"type": "SectionSelector", "value": "1"},
    }
    item["source_locators"] = [locator, copy.deepcopy(locator)]
    if schema_errors(schemas["claim"], item):
        print("PASS: duplicate identical source locator rejected")
    else:
        print("FAIL: duplicate identical source locator accepted")
        ok = False

    item = copy.deepcopy(claim)
    item.pop("source_locators", None)
    if not schema_errors(schemas["claim"], item):
        print("PASS: legacy claim without source_locators remains valid")
    else:
        print("FAIL: legacy claim without source_locators rejected")
        ok = False

"""
text = replace_once(text, marker, tests + marker, "locator self-tests")
write(rel, text)

# Canonical proof case: only the WCAG claim gains locator metadata.
path = ROOT / WCAG_REL
record = yaml.safe_load(path.read_text(encoding="utf-8"))
if "source_locators" in record:
    fail("WCAG claim already contains source_locators")
if "source:w3c-wcag-2-2" not in (record.get("sources") or []):
    fail("WCAG source prerequisite mismatch")

out = {}
for key, value in record.items():
    out[key] = value
    if key == "sources":
        out["source_locators"] = [
            {
                "source": "source:w3c-wcag-2-2",
                "selector": {
                    "type": "SectionSelector",
                    "value": "Success Criterion 1.4.3 Contrast (Minimum)",
                },
            }
        ]
path.write_text(
    yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000),
    encoding="utf-8",
)
print("UPDATED:", WCAG_REL)

# Foundation rev.13: taxonomy remains frozen; provenance capability is additive.
rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)
text = replace_once(
    text,
    "**Status:** Taxonomy v0.1 frozen architecture checkpoint (rev. 12). Further taxonomy/schema changes require a new post-freeze revision; see §17.",
    "**Status:** Taxonomy v0.1 remains frozen; post-freeze provenance extension (rev. 13). PF-001 adds exact relation-level source locators without changing taxonomy semantics; see §17.",
    "Foundation status",
)

old_identity = (
    "Editing " + BT + "statement" + BT + " wording, "
    + BT + "scope" + BT + ", or " + BT + "sources" + BT
    + " without changing the proposition keeps the ID."
)
new_identity = (
    "Editing " + BT + "statement" + BT + " wording, "
    + BT + "scope" + BT + ", " + BT + "sources" + BT
    + ", or relation-level source locators without changing the proposition keeps the ID."
)
text = replace_once(text, old_identity, new_identity, "claim identity rule")

section = """
### Exact source locators (post-freeze PF-001)

PF-001 preserves sources and definition_sources as frozen v0.1 source-ID arrays.
It adds optional relation-level source_locators and definition_source_locators.
Each locator explicitly names a source that must also appear in the corresponding
legacy source array; array position has no semantics. Locators belong to the
relationship, never globally to the source record.

Supported selector shapes are PageSelector, SectionSelector, FigureSelector,
TableSelector, FragmentSelector, and TextQuoteSelector. Fragment and TextQuote
semantics follow Web Annotation where applicable; page, section, figure, and
table selectors are project-native scholarly-document extensions using the same
source-plus-selector targeting pattern.

Missing locator metadata remains valid during migration. Adding or changing a
locator does not change claim proposition identity. Full W3C PROV entity,
activity, and agent modeling remains deferred until derivation/history
provenance is required.

This is a backward-compatible optional extension. Existing records retain
schema_version 0.1; the repository/Foundation revision identifies the additive
capability. A future breaking record-shape change must advance schema_version.
"""
text = replace_once(
    text,
    "\n### Source\n",
    "\n" + section + "\n### Source\n",
    "Foundation locator section",
)

text = replace_once(
    text,
    "| future source locator | Web Annotation Selector-compatible |",
    "| relation-level source locator | Web Annotation Selector-compatible; PF-001 implemented additively through claim and concept locator fields |",
    "standards locator row",
)

row12 = (
    "| 12 | 2026-09-27 | TAXONOMY-v0.1-FREEZE-AUDIT: all freeze gates passed "
    "at 54 records (28 concepts, 9 claims, 17 sources), 28 permanent self-tests, "
    "checker PASS with 0 warnings, and clean diff hygiene; required pilot cases "
    "were accounted for; PF-001 remains the sole intentionally deferred post-freeze "
    "provenance/locator item; Taxonomy v0.1 declared frozen before any PF-001 mutation. |"
)
row13 = (
    row12
    + "\n| 13 | 2026-09-27 | PF-001-RESOLUTION-01: preserved frozen source-ID arrays "
      "and added optional relation-level source locators for claims and concept definitions; "
      "locator sources must also occur in the corresponding legacy array; WCAG SC 1.4.3 "
      "provides the first canonical locator instance; taxonomy semantics and record counts "
      "remain unchanged. |"
)
text = replace_once(text, row12, row13, "Foundation decision row 12")
write(rel, text)

# Runtime contract: find_claims stays unchanged; trace_sources may enrich edges.
rel = "docs/PLUGIN_TARGET_ARCHITECTURE.md"
text = read(rel)

old = "Foundation baseline: " + BT + "docs/PROJECT_FOUNDATION.md" + BT + " — foundation rev. 8"
new = (
    "Foundation baseline: " + BT + "docs/PROJECT_FOUNDATION.md" + BT
    + " — foundation rev. 13 (Taxonomy v0.1 frozen at tag "
    + BT + "taxonomy-v0.1" + BT + "; PF-001 is a post-freeze provenance extension)"
)
text = replace_once(text, old, new, "runtime Foundation baseline")

old = (
    "**Status:** Working contract (rev. 1). Companion to "
    + BT + "docs/PROJECT_FOUNDATION.md" + BT + " rev. 6."
)
new = (
    "**Status:** Working contract (rev. 2). Companion to "
    + BT + "docs/PROJECT_FOUNDATION.md" + BT + " rev. 13."
)
text = replace_once(text, old, new, "runtime status")

text = replace_once(
    text,
    "trace_sources(claim_id | concept_id)         provenance chain",
    "trace_sources(claim_id | concept_id)         source records + relation-level locators when present",
    "trace_sources contract",
)

anchor = (
    "Normative " + BT + "constraint" + BT + " data is returned with the claim record payload. "
    "It adds no v0.1 retrieval parameter: "
    + BT + "find_claims(subject?, predicate?, object?, modality?, basis?)" + BT
    + " remains unchanged, and " + BT + "subject" + BT + " / "
    + BT + "object" + BT + " remain concept IDs.\n"
)
addition = (
    anchor
    + "\nPF-001 locator data is additive to record payloads. Legacy source-ID arrays "
      "remain unchanged; locator fields are returned when present. find_claims and "
      "existing source-ID lookup behavior remain unchanged, while trace_sources may "
      "enrich source edges with locator metadata.\n"
)
text = replace_once(text, anchor, addition, "runtime PF-001 contract")
write(rel, text)

# Resolve PF-001.
rel = "pilot/PILOT_FAILURE_LOG.md"
text = read(rel)
old = (
    "| PF-001 | Claim/source provenance | " + BT + "sources" + BT
    + " identifies a work but cannot preserve an exact supporting locator such as page, "
      "section, figure, table, or passage. | claim/source schema | Source IDs only | "
      "Add a locator-capable provenance representation after pilot review; do not choose "
      "its final form yet. | open |"
)
new = (
    "| PF-001 | Claim/source provenance | legacy source arrays identify a work but cannot "
      "preserve an exact supporting locator. | claim/concept source-reference schema | "
      "Frozen source-ID arrays retained; optional relation-level locator fields added | "
      "Added source-anchored selector objects while preserving source IDs and runtime "
      "lookup contracts. | resolved |"
)
write(rel, replace_once(text, old, new, "PF-001 failure row"))

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)
if "## PF-001-RESOLUTION-01" in text:
    fail("PF-001 resolution already logged")
block = """
## PF-001-RESOLUTION-01

- [x] Started from immutable taxonomy-v0.1 freeze checkpoint.
- [x] Preserved sources and definition_sources source-ID arrays.
- [x] Added optional relation-level source_locators and definition_source_locators.
- [x] Locator sources must occur in the corresponding legacy source array.
- [x] Added Page, Section, Figure, Table, Fragment, and TextQuote selector shapes.
- [x] Added permanent positive and negative locator self-tests.
- [x] Added canonical WCAG 2.2 SC 1.4.3 locator proof case.
- [x] Existing records without locators remain valid; find_claims remains unchanged.
- [x] Locator edits do not change claim proposition identity.
- [x] Full W3C PROV modeling remains deferred.
- [x] Backward-compatible extension retains schema_version 0.1.
- [x] Taxonomy semantics remain frozen; Foundation rev. 12 to rev. 13.
- [x] PF-001 outcome: RESOLVED.
"""
write(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

# Final validation.
out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
required_lines = [
    "PASS: all supported source selector shapes accepted",
    "PASS: unknown source selector type rejected",
    "PASS: empty text-quote exact value rejected",
    "PASS: locator without selector rejected",
    "PASS: claim locator source must occur in sources",
    "PASS: definition locator source must occur in definition_sources",
    "PASS: duplicate identical source locator rejected",
    "PASS: legacy claim without source_locators remains valid",
    "SELF-TEST RESULT: PASS",
]
for line in required_lines:
    if line not in out:
        fail("missing self-test line: " + line)
if sum(1 for line in out.splitlines() if line.startswith("PASS:")) != 36:
    fail("expected 36 PASS self-tests")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker is not clean")
run("git", "diff", "--check")

if counts() != BASELINE:
    fail("record counts changed")

changed_claims = [
    p.relative_to(ROOT).as_posix()
    for p, before in claim_before.items()
    if sha(p) != before
]
if changed_claims != [WCAG_REL]:
    fail("unexpected canonical claim changes: " + repr(changed_claims))

for collection, label in (
    (concept_before, "concept"),
    (source_before, "source"),
):
    for path, before in collection.items():
        if sha(path) != before:
            fail("unexpected canonical " + label + " change: " + str(path.relative_to(ROOT)))

claim = yaml.safe_load((ROOT / WCAG_REL).read_text(encoding="utf-8"))
expected_locator = [
    {
        "source": "source:w3c-wcag-2-2",
        "selector": {
            "type": "SectionSelector",
            "value": "Success Criterion 1.4.3 Contrast (Minimum)",
        },
    }
]
if claim.get("source_locators") != expected_locator:
    fail("WCAG locator payload mismatch")
if claim.get("schema_version") != "0.1":
    fail("WCAG schema_version changed unexpectedly")

if "post-freeze provenance extension (rev. 13)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation rev.13 marker missing")

pf_rows = [
    line for line in read("pilot/PILOT_FAILURE_LOG.md").splitlines()
    if "| PF-001 |" in line
]
if len(pf_rows) != 1 or "| resolved |" not in pf_rows[0]:
    fail("PF-001 is not uniquely resolved")

if subprocess.check_output(
    ["git", "rev-list", "-n", "1", TAG], cwd=ROOT, text=True
).strip() != freeze:
    fail("taxonomy-v0.1 tag moved")

print("\n===== RESULT =====")
print("OUTCOME: PF-001_RESOLVED")
print("Foundation: rev. 13")
print("Taxonomy v0.1 semantics: FROZEN / UNCHANGED")
print("Legacy source-ID arrays: PRESERVED")
print("source_locators: ACTIVE / OPTIONAL")
print("definition_source_locators: ACTIVE / OPTIONAL")
print("Canonical proof case: WCAG 2.2 SC 1.4.3")
print("schema_version: 0.1 PRESERVED")
print("SELF-TESTS: 36 PASS")
print("CHECKER: PASS (0 warnings)")
print("COUNTS: 54 records — 28 concepts, 9 claims, 17 sources")
print("find_claims signature: UNCHANGED")
print("taxonomy-v0.1 tag: UNCHANGED")
print("No commit or push performed.")
