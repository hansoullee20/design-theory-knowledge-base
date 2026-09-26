#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

EXPECTED_BASELINE = (42, 23, 6, 13)
SOURCE_ID = "source:w3c-wcag-2-2"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(2)


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    if p.exists() and p.read_text(encoding="utf-8") == text:
        print(f"UNCHANGED: {rel}")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def load_yaml(rel: str):
    try:
        data = yaml.safe_load(read(rel))
    except Exception as exc:
        fail(f"{rel}: YAML parse error: {exc}")
    if not isinstance(data, dict):
        fail(f"{rel}: expected mapping")
    return data


def dump_yaml(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def counts():
    c = list((ROOT / "data" / "concepts").glob("*.yaml"))
    k = list((ROOT / "data" / "claims").glob("*.yaml"))
    s = list((ROOT / "data" / "sources").glob("*.yaml"))
    return (len(c) + len(k) + len(s), len(c), len(k), len(s))


def run(cmd: list[str], capture: bool = False):
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)


def verify_preconditions():
    print("===== PRECONDITIONS =====")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    if branch != "main":
        fail(f"expected main, got {branch!r}")

    if "(rev. 8)" not in read("docs/PROJECT_FOUNDATION.md"):
        fail("foundation is not rev. 8")

    if counts() != EXPECTED_BASELINE:
        fail(f"expected baseline {EXPECTED_BASELINE}, got {counts()}")

    cq = read("docs/COMPETENCY_QUESTIONS.md")
    if not re.search(
        r"WCAG.*contrast.*standard.*empirical|WCAG contrast requirements as standards rather than empirical laws",
        cq,
        re.I | re.S,
    ):
        fail("CQ27 WCAG standards-vs-empirical requirement not found")

    for cmd in (
        [sys.executable, "scripts/pilot_check.py", "--self-test"],
        [sys.executable, "scripts/pilot_check.py"],
        ["git", "diff", "--check"],
    ):
        p = run(cmd, True)
        print(p.stdout, end="")
        if p.stderr:
            print(p.stderr, end="", file=sys.stderr)
        if p.returncode:
            fail("precondition command failed")

    print("PRECONDITIONS: PASS")


def inspect_claim_schema():
    print("\n===== CLAIM SCHEMA TEST =====")
    schema = load_yaml("schema/claim.schema.yaml")
    props = schema.get("properties", {})

    modalities = props.get("modality", {}).get("enum", [])
    basis = (
        props.get("basis", {})
        .get("items", {})
        .get("enum", [])
    )
    predicates = props.get("predicate", {}).get("enum", [])
    object_schema = props.get("object", {})

    print("modalities:", modalities)
    print("basis:", basis)
    print("predicates:", predicates)
    print("object schema:", json.dumps(object_schema, ensure_ascii=False))

    if "prescriptive" not in modalities:
        fail("prescriptive modality is missing")
    if "standard" not in basis:
        fail("standard basis is missing")

    # Predeclared semantic test:
    # A WCAG threshold requirement needs a normative requirement operator and a literal
    # threshold, or another explicit structured constraint representation. None of
    # increases/decreases/influences means 'must be at least', and object is concept-only.
    comparative_only = set(predicates).issubset({"increases", "decreases", "influences"})
    concept_only_object = (
        object_schema.get("type") == "string"
        and isinstance(object_schema.get("pattern"), str)
        and object_schema["pattern"].startswith("^concept:")
    )

    if not comparative_only:
        fail(
            "predicate vocabulary has changed; manual review required before applying "
            "the predeclared WCAG-01 outcome"
        )
    if not concept_only_object:
        fail(
            "claim object schema has changed; manual review required before applying "
            "the predeclared WCAG-01 outcome"
        )

    print("STANDARD AXIS: AVAILABLE")
    print("PRESCRIPTIVE AXIS: AVAILABLE")
    print("NORMATIVE THRESHOLD OPERATOR: NOT AVAILABLE")
    print("LITERAL THRESHOLD OBJECT: NOT AVAILABLE")
    print("SCRATCH OUTCOME: CLAIM_SCHEMA_GAP")


def find_existing_source() -> str | None:
    matches = []
    for p in sorted((ROOT / "data" / "sources").glob("*.yaml")):
        text = p.read_text(encoding="utf-8")
        low = text.lower()
        if "wcag 2.2" in low or "web content accessibility guidelines" in low:
            data = yaml.safe_load(text)
            rid = data.get("id")
            if isinstance(rid, str):
                matches.append((rid, p))

    if not matches:
        return None

    for rid, p in matches:
        print(f"EXISTING WCAG SOURCE: {rid} ({p.relative_to(ROOT)})")

    return matches[0][0]


def mint_source() -> tuple[str, str]:
    existing = find_existing_source()
    if existing:
        return existing, "reused"

    schema = load_yaml("schema/source.schema.yaml")
    props = schema.get("properties", {})
    required = schema.get("required", [])
    enum = props.get("source_type", {}).get("enum", [])
    if "standard" not in enum:
        fail("source_type standard is unavailable")

    template_files = sorted((ROOT / "data" / "sources").glob("*.yaml"))
    if not template_files:
        fail("no canonical source template available")
    template = yaml.safe_load(template_files[0].read_text(encoding="utf-8"))

    values = {
        "id": SOURCE_ID,
        "kind": "source",
        "citation": (
            "World Wide Web Consortium (W3C). Web Content Accessibility Guidelines "
            "(WCAG) 2.2. W3C Recommendation, 12 December 2024."
        ),
        "source_type": "standard",
        "year": 2024,
        "title": "Web Content Accessibility Guidelines (WCAG) 2.2",
        "author": "World Wide Web Consortium (W3C)",
        "authors": ["World Wide Web Consortium (W3C)"],
        "url": "https://www.w3.org/TR/WCAG22/",
        "notes": (
            "Current W3C Recommendation dated 2024-12-12. WCAG 2.2 Success Criterion "
            "1.4.3 Contrast (Minimum), Level AA, requires at least 4.5:1 for text and "
            "images of text, with 3:1 for large text and stated incidental/logotype "
            "exceptions. Exact locator machinery remains deferred under PF-001."
        ),
    }

    if "schema_version" in props and "schema_version" in template:
        values["schema_version"] = template["schema_version"]

    data = {}
    for key in props:
        if key not in values:
            continue
        val = values[key]
        ptype = props.get(key, {}).get("type")
        if key == "year" and ptype == "string":
            val = "2024"
        elif key == "authors" and ptype == "string":
            val = "World Wide Web Consortium (W3C)"
        elif key == "author" and ptype == "array":
            val = ["World Wide Web Consortium (W3C)"]
        data[key] = val

    for key in required:
        if key not in data:
            fail(f"cannot safely mint source; required field {key!r} lacks a value")

    rel = "data/sources/w3c-wcag-2-2.yaml"
    write(rel, dump_yaml(data))
    print(f"NEW SOURCE: {SOURCE_ID}")
    return SOURCE_ID, "newly minted"


def write_scratch(source_id: str):
    td = Path(tempfile.mkdtemp(prefix="wcag-01-"))
    path = td / "claim-wcag-contrast-minimum-scratch.yaml"
    candidate = {
        "id": "claim:wcag-contrast-minimum-scratch",
        "kind": "claim",
        "statement": (
            "For WCAG 2.2 Level AA, normal text and images of text must have a "
            "contrast ratio of at least 4.5:1, subject to the criterion's exceptions."
        ),
        "modality": "prescriptive",
        "subject": "concept:text-background-contrast",
        "predicate": "<NO_FAITHFUL_CURRENT_PREDICATE>",
        "object": "<LITERAL_THRESHOLD_4.5_TO_1_NOT_ALLOWED>",
        "basis": ["standard"],
        "evidence_status": "unassessed",
        "scope": (
            "WCAG 2.2 SC 1.4.3; large text uses 3:1; incidental text and logotypes "
            "are exceptions."
        ),
        "sources": [source_id],
        "record_status": "draft",
        "schema_version": "0.1",
        "canonical": False,
    }
    path.write_text(dump_yaml(candidate), encoding="utf-8")
    print(f"SCRATCH CLAIM: {path}")


def append_pilot(source_id: str, source_status: str):
    rel = "pilot/PILOT_RECORDS.md"
    text = read(rel)
    if "## WCAG-01" in text:
        fail("WCAG-01 already logged")

    block = f"""
## WCAG-01

- [x] Competency question tested: represent WCAG contrast requirements as standards rather than empirical laws.
- [x] Normative source: `{source_id}` ({source_status}).
- [x] `basis: [standard]` is already available.
- [x] `modality: prescriptive` is already available.
- [x] Scratch-only WCAG 2.2 SC 1.4.3 claim tested outside canonical `data/`.
- [x] Current claim predicates are limited to `increases`, `decreases`, and `influences`; none faithfully means a normative requirement such as “must be at least”.
- [x] Current claim object is concept-ID only and cannot structurally represent the numeric threshold `4.5:1`.
- [x] Encoding the normative threshold only in free-text `statement`/`scope` while using an unrelated comparative predicate would make the structured proposition semantically misleading.
- [x] Outcome: `CLAIM_SCHEMA_GAP`.
- [x] No canonical WCAG claim minted.
- [x] No concept minted solely to disguise the numeric threshold as a concept.
- [x] Foundation remains rev. 8 pending bounded resolution.
"""
    write(rel, text.rstrip() + "\n\n" + block.strip() + "\n")


def append_failure():
    rel = "pilot/PILOT_FAILURE_LOG.md"
    text = read(rel)
    if "PF-006" in text:
        print("PF-006 already present")
        return

    entry = """
- **PF-006 — OPEN — normative threshold claim representation.** WCAG-01 confirms that
  `basis: standard` and `modality: prescriptive` are available, but the current
  subject–predicate–object claim model cannot faithfully encode a codified threshold
  requirement such as WCAG 2.2 SC 1.4.3: the predicate vocabulary has only
  `increases|decreases|influences`, while `object` accepts only concept IDs.
  Resolve before Taxonomy v0.1 freeze. Do not model numeric thresholds as fake concepts
  or hide the normative operator solely in free text.
"""
    write(rel, text.rstrip() + "\n" + entry.strip() + "\n")


def final_checks(expected_counts):
    print("\n===== FINAL SELF TEST =====")
    a = run([sys.executable, "scripts/pilot_check.py", "--self-test"], True)
    print(a.stdout, end="")
    if a.stderr:
        print(a.stderr, end="", file=sys.stderr)

    print("\n===== FINAL CORPUS =====")
    b = run([sys.executable, "scripts/pilot_check.py"], True)
    print(b.stdout, end="")
    if b.stderr:
        print(b.stderr, end="", file=sys.stderr)

    print("\n===== DIFF CHECK =====")
    c = run(["git", "diff", "--check"], True)
    print(c.stdout, end="")
    if c.stderr:
        print(c.stderr, end="", file=sys.stderr)

    if a.returncode or "SELF-TEST RESULT: PASS" not in a.stdout:
        fail("self-test failed")
    if b.returncode or "RESULT: PASS (0 warning(s))" not in b.stdout:
        fail("corpus checker failed")
    if c.returncode:
        fail("git diff --check failed")
    if counts() != expected_counts:
        fail(f"expected counts {expected_counts}, got {counts()}")

    print("\n===== STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\n===== DIFF STAT HEAD =====")
    subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

    print("\n===== RESULT =====")
    print("OUTCOME: CLAIM_SCHEMA_GAP")
    print("basis: standard — AVAILABLE")
    print("modality: prescriptive — AVAILABLE")
    print("normative threshold representation — MISSING")
    print(
        f"COUNTS: {expected_counts[0]} records — {expected_counts[1]} concepts, "
        f"{expected_counts[2]} claims, {expected_counts[3]} sources"
    )
    print("PF-006: OPEN")
    print("Foundation remains rev. 8")
    print("No canonical WCAG claim minted.")
    print("No commit or push performed.")


def main():
    verify_preconditions()
    inspect_claim_schema()

    print("\n===== SOURCE =====")
    source_id, source_status = mint_source()

    print("\n===== SCRATCH CLAIM =====")
    write_scratch(source_id)

    print("\n===== PILOT DOCUMENTATION =====")
    append_pilot(source_id, source_status)
    append_failure()

    expected = (43, 23, 6, 14) if source_status == "newly minted" else (42, 23, 6, 13)
    final_checks(expected)


if __name__ == "__main__":
    main()
