#!/usr/bin/env python3
from __future__ import annotations

import copy
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
)

SOURCE_ID = "source:muller-brockmann-1981-grid-systems"
SOURCE_FILE = "data/sources/muller-brockmann-1981-grid-systems.yaml"

EXPECTED_COUNTS = (37, 19, 6, 12)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(2)


def run(cmd: list[str]) -> int:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
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
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


def verify_rev6_baseline() -> None:
    print("===== REV. 6 BASELINE =====")

    foundation = read("docs/PROJECT_FOUNDATION.md")
    if "(rev. 6)" not in foundation:
        fail("PROJECT_FOUNDATION.md is not rev. 6")
    if "### 8.1 Structural relation semantics" not in foundation:
        fail("rev. 6 structural relation contract is missing")

    plugin = read("docs/PLUGIN_TARGET_ARCHITECTURE.md")
    if "foundation rev. 6" not in plugin:
        fail("PLUGIN_TARGET_ARCHITECTURE.md does not carry the rev. 6 baseline line")

    if run([sys.executable, "scripts/pilot_check.py", "--self-test"]):
        fail("rev. 6 self-test failed")
    if run([sys.executable, "scripts/pilot_check.py"]):
        fail("rev. 6 corpus validation failed")
    if run(["git", "diff", "--check"]):
        fail("rev. 6 diff check failed")


def fix_plugin_stale_lines() -> None:
    rel = "docs/PLUGIN_TARGET_ARCHITECTURE.md"
    text = read(rel)

    # Finish broader -> is_a in the neighbors capability description.
    text2 = re.sub(
        r"(?i)\bbroader\s*/\s*part_of\b",
        "is_a / part_of",
        text,
    )
    text2 = re.sub(
        r"(?i)\bbroader\b(?=\s*,\s*part_of\b)",
        "is_a",
        text2,
    )

    # Reconcile stale companion header wording with the already-authoritative
    # foundation-baseline line. Only header-area occurrences are changed.
    lines = text2.splitlines()
    for i, line in enumerate(lines[:20]):
        if re.search(r"(?i)companion.*rev\.\s*2", line):
            lines[i] = re.sub(r"(?i)rev\.\s*2", "rev. 6", line)

    text2 = "\n".join(lines)
    if text.endswith("\n"):
        text2 += "\n"

    if re.search(r"(?i)neighbors\([^\n]*\bbroader\b", text2):
        fail("could not remove stale broader reference from neighbors()")
    if any(
        re.search(r"(?i)companion.*rev\.\s*2", line)
        for line in text2.splitlines()[:20]
    ):
        fail("could not reconcile stale Companion rev. 2 header")

    write(rel, text2)


def make_source() -> None:
    rel = SOURCE_FILE
    if (ROOT / rel).exists():
        print(f"UNCHANGED: {rel} already exists")
        return

    schema = load_yaml("schema/source.schema.yaml")
    props = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(props, dict) or not isinstance(required, list):
        fail("source schema has unexpected shape")

    template = load_yaml("data/sources/gibson-1979-ecological-approach.yaml")

    source_type_enum = (
        props.get("source_type", {}).get("enum")
        if isinstance(props.get("source_type"), dict)
        else None
    )
    if source_type_enum is not None and "book" not in source_type_enum:
        fail(f"source_type 'book' unavailable; allowed={source_type_enum!r}")

    citation = (
        "Müller-Brockmann, Josef. Grid Systems in Graphic Design: "
        "A Visual Communication Manual for Graphic Designers, Typographers "
        "and Three Dimensional Designers. 1981. ISBN 0-8038-2711-3."
    )

    overrides = {
        "id": SOURCE_ID,
        "kind": "source",
        "citation": citation,
        "source_type": "book",
        "year": 1981,
        "title": "Grid Systems in Graphic Design",
        "author": "Josef Müller-Brockmann",
        "authors": ["Josef Müller-Brockmann"],
        "publisher": "Verlag Arthur Niggli / Hastings House Publishers",
        "isbn": "0803827113",
        "url": "https://openlibrary.org/books/OL22409122M/Grid_systems_in_graphic_design",
        "notes": (
            "1981 edition metadata and ISBN 0-8038-2711-3 verified against "
            "library-catalog-derived records."
        ),
    }

    data = {}
    # Preserve the existing schema_version from a canonical source template.
    if "schema_version" in props and "schema_version" in template:
        overrides["schema_version"] = template["schema_version"]

    # Construct only schema-declared fields; do not inherit Gibson-specific data.
    for key in props:
        if key in overrides:
            value = overrides[key]
            prop_schema = props.get(key, {})
            expected_type = prop_schema.get("type") if isinstance(prop_schema, dict) else None

            # Adapt author/publisher/url/isbn shapes conservatively when schemas differ.
            if key == "authors" and expected_type == "string":
                value = "Josef Müller-Brockmann"
            elif key == "author" and expected_type == "array":
                value = ["Josef Müller-Brockmann"]
            elif key == "year" and expected_type == "string":
                value = "1981"

            data[key] = value

    for key in required:
        if key not in data:
            if key in template and key == "schema_version":
                data[key] = template[key]
            else:
                fail(
                    f"cannot safely construct source record: required field {key!r} "
                    "has no grid-source value"
                )

    write(rel, dump_yaml(data))


def concept_template() -> dict:
    data = copy.deepcopy(load_yaml("data/concepts/print-size.yaml"))
    if "is_a" not in data:
        fail("concept records do not yet use rev. 6 is_a field")
    return data


def make_concept(
    slug: str,
    label: str,
    definition: str,
    *,
    is_a: list[str] | None = None,
    part_of: list[str] | None = None,
) -> None:
    rel = f"data/concepts/{slug}.yaml"
    if (ROOT / rel).exists():
        print(f"UNCHANGED: {rel} already exists")
        return

    data = concept_template()
    data["id"] = f"concept:{slug}"
    data["kind"] = "concept"
    data["label"] = label
    data["definition"] = definition
    data["definition_sources"] = [SOURCE_ID]
    data["locus"] = ["artifact"]

    for key in ("aliases", "facets", "disciplines", "traditions", "related", "opposite_of", "replaced_by"):
        if key in data:
            data[key] = []

    if "knowledge_origin" in data:
        data["knowledge_origin"] = ["design-practice"]

    data["is_a"] = list(is_a or [])
    data["part_of"] = list(part_of or [])

    if "notes" in data:
        data["notes"] = ""

    write(rel, dump_yaml(data))


def make_grid_records() -> None:
    make_concept(
        "grid",
        "Grid",
        (
            "A system of horizontal and vertical divisions that organizes a format "
            "into columns, fields, gutters, margins, or modules for positioning visual content."
        ),
    )
    make_concept(
        "grid-column",
        "Grid column",
        (
            "A vertical structural constituent of a layout grid within which visual "
            "content can be positioned and aligned."
        ),
        part_of=["concept:grid"],
    )
    make_concept(
        "gutter",
        "Gutter",
        (
            "The interval that separates adjacent columns or fields within a layout grid."
        ),
        part_of=["concept:grid"],
    )
    make_concept(
        "modular-grid",
        "Modular grid",
        (
            "A grid in which columns are divided horizontally to form repeated modules "
            "or fields for organizing content."
        ),
        is_a=["concept:grid"],
    )


def update_pilot_records() -> None:
    rel = "pilot/PILOT_RECORDS.md"
    text = read(rel)

    block = """## GRID-STRUCTURE-01

- [x] `concept:grid` — artifact-locus whole.
- [x] `concept:grid-column` — `part_of: [concept:grid]`.
- [x] `concept:gutter` — `part_of: [concept:grid]`.
- [x] `concept:modular-grid` — `is_a: [concept:grid]`.
- [x] `source:muller-brockmann-1981-grid-systems` — 1981 edition; ISBN verified against a library-catalog-derived record.
- Result gate: first source-backed `part_of` and `is_a` edges must validate with 0 warnings.
"""

    if "## GRID-STRUCTURE-01" not in text:
        text = text.rstrip() + "\n\n" + block
    write(rel, text)


def verify_counts() -> None:
    concepts = list((ROOT / "data" / "concepts").glob("*.yaml"))
    claims = list((ROOT / "data" / "claims").glob("*.yaml"))
    sources = list((ROOT / "data" / "sources").glob("*.yaml"))
    total = len(concepts) + len(claims) + len(sources)

    actual = (total, len(concepts), len(claims), len(sources))
    if actual != EXPECTED_COUNTS:
        fail(f"unexpected corpus counts: expected {EXPECTED_COUNTS}, got {actual}")
    print(
        f"VERIFIED COUNTS: {total} records — {len(concepts)} concepts, "
        f"{len(claims)} claims, {len(sources)} sources"
    )


def main() -> None:
    verify_rev6_baseline()

    print("\n===== BLOCKING CONSISTENCY FIX =====")
    fix_plugin_stale_lines()

    print("\n===== GRID-STRUCTURE-01 =====")
    make_source()
    make_grid_records()
    update_pilot_records()

    print("\n===== FINAL SELF TEST =====")
    rc1 = run([sys.executable, "scripts/pilot_check.py", "--self-test"])

    print("\n===== FINAL CORPUS =====")
    rc2 = run([sys.executable, "scripts/pilot_check.py"])

    print("\n===== DIFF CHECK =====")
    rc3 = run(["git", "diff", "--check"])

    verify_counts()

    plugin = read("docs/PLUGIN_TARGET_ARCHITECTURE.md")
    if re.search(r"(?i)neighbors\([^\n]*\bbroader\b", plugin):
        fail("stale broader remains in neighbors()")
    if any(
        re.search(r"(?i)companion.*rev\.\s*2", line)
        for line in plugin.splitlines()[:20]
    ):
        fail("stale Companion rev. 2 remains")

    print("\n===== GRID EDGES =====")
    for rel in (
        "data/concepts/grid-column.yaml",
        "data/concepts/gutter.yaml",
        "data/concepts/modular-grid.yaml",
    ):
        data = load_yaml(rel)
        print(
            f"{data['id']}: is_a={data.get('is_a', [])} "
            f"part_of={data.get('part_of', [])}"
        )

    print("\n===== STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\n===== DIFF STAT =====")
    subprocess.run(["git", "diff", "--stat"], cwd=ROOT)

    if rc1 or rc2 or rc3:
        print("\nRESULT: GRID-STRUCTURE-01 FAILED.")
        sys.exit(1)

    print("\nRESULT: GRID-STRUCTURE-01 PASSED.")
    print("Expected corpus: 37 records — 19 concepts, 6 claims, 12 sources.")
    print("PLUGIN_TARGET_ARCHITECTURE stale rev/broader references corrected.")
    print("No FIGURE-GROUND-01 records were minted.")
    print("No commit or push was performed.")


if __name__ == "__main__":
    main()
