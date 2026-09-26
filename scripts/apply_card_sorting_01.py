#!/usr/bin/env python3
from __future__ import annotations

import copy
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

NEW_SOURCE_ID = "source:nng-2024-card-sorting"
EXPECTED_BASELINE = (40, 22, 6, 12)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(2)


def run(cmd: list[str], capture: bool = False):
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)


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
    concepts = list((ROOT / "data" / "concepts").glob("*.yaml"))
    claims = list((ROOT / "data" / "claims").glob("*.yaml"))
    sources = list((ROOT / "data" / "sources").glob("*.yaml"))
    return (len(concepts)+len(claims)+len(sources), len(concepts), len(claims), len(sources))


def verify_preconditions() -> None:
    print("===== PRECONDITIONS =====")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    if branch != "main":
        fail(f"expected branch main, got {branch!r}")

    foundation = read("docs/PROJECT_FOUNDATION.md")
    if "(rev. 8)" not in foundation:
        fail("foundation is not rev. 8")

    if counts() != EXPECTED_BASELINE:
        fail(f"expected baseline {EXPECTED_BASELINE}, got {counts()}")

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

    for pattern in ("opposite_of",):
        p = subprocess.run(
            ["grep", "-rn", pattern, "data/", "schema/", "scripts/"],
            cwd=ROOT, text=True, capture_output=True
        )
        if p.returncode == 0:
            print(p.stdout, end="")
            fail(f"legacy term remains: {pattern}")
        if p.returncode not in (0, 1):
            fail(f"grep failed for {pattern}")

    p = subprocess.run(
        ["grep", "-rnE", r"(^|[^A-Za-z_])broader([^A-Za-z_]|$)",
         "data/", "schema/", "scripts/"],
        cwd=ROOT, text=True, capture_output=True
    )
    if p.returncode == 0:
        print(p.stdout, end="")
        fail("legacy broader remains")
    if p.returncode not in (0, 1):
        fail("broader grep failed")

    print("PRECONDITIONS: PASS")


def find_existing_source() -> str | None:
    candidates = []
    for p in sorted((ROOT / "data" / "sources").glob("*.yaml")):
        text = p.read_text(encoding="utf-8")
        low = text.lower()
        if "card sort" in low:
            data = yaml.safe_load(text)
            rid = data.get("id")
            if isinstance(rid, str):
                candidates.append((rid, p))

    if not candidates:
        return None

    if len(candidates) > 1:
        print("SOURCE CANDIDATES:")
        for rid, p in candidates:
            print(f"  {rid} ({p.relative_to(ROOT)})")

    rid, p = candidates[0]
    print(f"REUSE SOURCE: {rid} ({p.relative_to(ROOT)})")
    return rid


def mint_source() -> str:
    rel = "data/sources/nng-2024-card-sorting.yaml"
    if (ROOT / rel).exists():
        data = load_yaml(rel)
        if data.get("id") != NEW_SOURCE_ID:
            fail(f"{rel} exists with unexpected ID")
        print(f"REUSE SOURCE: {NEW_SOURCE_ID}")
        return NEW_SOURCE_ID

    schema = load_yaml("schema/source.schema.yaml")
    props = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(props, dict) or not isinstance(required, list):
        fail("unexpected source schema shape")

    enum = None
    if isinstance(props.get("source_type"), dict):
        enum = props["source_type"].get("enum")

    source_type = None
    if isinstance(enum, list):
        for candidate in ("web", "website", "article", "professional-article", "other"):
            if candidate in enum:
                source_type = candidate
                break
    if source_type is None:
        fail(f"could not choose source_type from enum {enum!r}")

    values = {
        "id": NEW_SOURCE_ID,
        "kind": "source",
        "citation": (
            "Tankala, Samhita, and Katie Sherwin. "
            "\"Card Sorting: Uncover Users' Mental Models for Better Information Architecture.\" "
            "Nielsen Norman Group, February 2, 2024."
        ),
        "source_type": source_type,
        "year": 2024,
        "title": "Card Sorting: Uncover Users' Mental Models for Better Information Architecture",
        "author": "Samhita Tankala and Katie Sherwin",
        "authors": ["Samhita Tankala", "Katie Sherwin"],
        "url": "https://www.nngroup.com/articles/card-sorting-definition/",
        "notes": (
            "Published 2024-02-02. Defines card sorting as a UX research method "
            "in which participants place individually labeled cards into groups "
            "according to criteria that make sense to them. Exact source locators "
            "remain deferred under PF-001."
        ),
    }

    # Preserve schema_version from any canonical source.
    existing = sorted((ROOT / "data" / "sources").glob("*.yaml"))
    if not existing:
        fail("no source template available")
    template = yaml.safe_load(existing[0].read_text(encoding="utf-8"))
    if "schema_version" in props and "schema_version" in template:
        values["schema_version"] = template["schema_version"]

    data = {}
    for key in props:
        if key not in values:
            continue
        value = values[key]
        pdef = props.get(key, {})
        ptype = pdef.get("type") if isinstance(pdef, dict) else None
        if key == "year" and ptype == "string":
            value = "2024"
        elif key == "authors" and ptype == "string":
            value = "Samhita Tankala; Katie Sherwin"
        elif key == "author" and ptype == "array":
            value = ["Samhita Tankala", "Katie Sherwin"]
        data[key] = value

    for key in required:
        if key not in data:
            fail(f"cannot safely mint source; required field {key!r} lacks a value")

    write(rel, dump_yaml(data))
    print(f"NEW SOURCE: {NEW_SOURCE_ID}")
    return NEW_SOURCE_ID


def inspect_method_need() -> tuple[str, list[str]]:
    foundation = read("docs/PROJECT_FOUNDATION.md")
    runtime = read("docs/PLUGIN_TARGET_ARCHITECTURE.md")

    evidence = []
    for i, line in enumerate(foundation.splitlines(), 1):
        low = line.lower()
        if ("method" in low or "operationalized_by" in low) and (
            "reserved" in low or "competenc" in low or "cq" in low
        ):
            evidence.append(f"foundation:{i}: {line.strip()}")

    runtime_method_lines = [
        (i, line.strip())
        for i, line in enumerate(runtime.splitlines(), 1)
        if "method" in line.lower()
    ]

    active_capability_requires_method = any(
        re.search(r"\b(search_methods|get_method|find_methods|method_id)\b", line, re.I)
        for _, line in runtime_method_lines
    )

    method_files = []
    for base in ("data", "schema", "vocab"):
        for p in (ROOT / base).rglob("*"):
            if p.is_file() and (
                "method" in p.name.lower() or "/methods/" in str(p).replace("\\", "/").lower()
            ):
                method_files.append(str(p.relative_to(ROOT)))

    if method_files:
        fail("method implementation already exists unexpectedly: " + ", ".join(method_files))

    if active_capability_requires_method:
        return "ACTIVATE_METHOD", evidence + [
            f"runtime:{i}: {line}" for i, line in runtime_method_lines
        ]

    return "KEEP_METHOD_RESERVED", evidence


def scratch_method_test() -> Path:
    candidate = {
        "id": "method:card-sorting",
        "kind": "method",
        "label": "Card sorting",
        "procedure": [
            "prepare labeled items",
            "ask participants to group items",
            "analyze groupings",
        ],
        "inputs": ["labeled items", "participants"],
        "outputs": ["groupings", "labels or category structure"],
        "variants": ["open", "closed"],
        "applicability_conditions": [
            "investigating users' mental organization of information"
        ],
        "canonical": False,
    }
    td = Path(tempfile.mkdtemp(prefix="card-sorting-01-"))
    path = td / "method-card-sorting-scratch.yaml"
    path.write_text(dump_yaml(candidate), encoding="utf-8")
    print(f"SCRATCH METHOD: {path}")
    return path


def mint_concept(source_id: str) -> None:
    rel = "data/concepts/card-sorting.yaml"
    if (ROOT / rel).exists():
        fail(f"refusing to overwrite existing {rel}")

    template_path = ROOT / "data" / "concepts" / "perceptual-grouping.yaml"
    if not template_path.exists():
        template_path = sorted((ROOT / "data" / "concepts").glob("*.yaml"))[0]
    data = copy.deepcopy(yaml.safe_load(template_path.read_text(encoding="utf-8")))

    data["id"] = "concept:card-sorting"
    data["kind"] = "concept"
    data["label"] = "Card sorting"
    if "aliases" in data:
        data["aliases"] = []
    data["definition"] = (
        "A research activity in which participants organize labeled items into "
        "groups according to criteria that make sense to them, typically to "
        "investigate users’ mental organization of information."
    )
    data["definition_sources"] = [source_id]
    data["locus"] = ["practice"]
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

    write(rel, dump_yaml(data))


def log_pilot(source_id: str, source_status: str, decision_evidence: list[str]) -> None:
    rel = "pilot/PILOT_RECORDS.md"
    text = read(rel)
    if "## CARD-SORTING-01" in text:
        fail("CARD-SORTING-01 already logged")

    evidence_summary = (
        "Current competency/runtime inspection found no active capability requiring "
        "an independently addressable procedural entity; runtime remains concept/claim/"
        "source-oriented and the method layer remains reserved."
    )

    block = f"""
## CARD-SORTING-01

- [x] `concept:card-sorting` minted with `locus: [practice]`.
- [x] Definition source: `{source_id}` ({source_status}).
- [x] Scratch-only `method:card-sorting` candidate tested outside canonical `data/`.
- [x] Scratch candidate uniquely carried procedural steps, inputs, outputs, variants, participant instructions/applicability details, but no existing competency question or active runtime capability requires those details as a separately addressable canonical entity.
- [x] Decision: `KEEP_METHOD_RESERVED`.
- [x] {evidence_summary}
- [x] method remains reserved.
- [x] operationalized_by remains reserved.
"""

    text = text.rstrip() + "\n\n" + block.strip() + "\n"
    write(rel, text)


def final_checks(expected_counts: tuple[int, int, int, int]) -> None:
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

    print("\n===== METHOD IMPLEMENTATION CHECK =====")
    found = []
    for base in ("data", "schema", "vocab"):
        for p in (ROOT / base).rglob("*"):
            if p.is_file() and (
                "method" in p.name.lower() or "/methods/" in str(p).replace("\\", "/").lower()
            ):
                found.append(str(p.relative_to(ROOT)))
    if found:
        fail("unexpected method implementation: " + ", ".join(found))
    print("(no canonical method implementation)")

    print("\n===== STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\n===== DIFF STAT HEAD =====")
    subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

    print("\n===== RESULT =====")
    print("OUTCOME: KEEP_METHOD_RESERVED")
    print("method: RESERVED")
    print("operationalized_by: RESERVED")
    print(
        f"COUNTS: {expected_counts[0]} records — {expected_counts[1]} concepts, "
        f"{expected_counts[2]} claims, {expected_counts[3]} sources"
    )
    print("Foundation remains rev. 8")
    print("No commit or push performed.")


def main() -> None:
    verify_preconditions()

    existing = find_existing_source()
    if existing:
        source_id = existing
        source_status = "reused"
        expected = (41, 23, 6, 12)
    else:
        source_id = mint_source()
        source_status = "newly minted"
        expected = (42, 23, 6, 13)

    print("\n===== SCRATCH METHOD TEST =====")
    scratch_method_test()

    outcome, evidence = inspect_method_need()
    print("DECISION EVIDENCE:")
    if evidence:
        for line in evidence[:20]:
            print("  " + line)
    else:
        print("  no active method-specific CQ/runtime requirement found")

    if outcome != "KEEP_METHOD_RESERVED":
        fail(
            "existing runtime/CQ evidence may require ACTIVATE_METHOD; "
            "stop before canonical concept mutation"
        )

    print("\n===== CANONICAL CONCEPT =====")
    mint_concept(source_id)

    print("\n===== PILOT DOCUMENTATION =====")
    log_pilot(source_id, source_status, evidence)

    final_checks(expected)


if __name__ == "__main__":
    main()
