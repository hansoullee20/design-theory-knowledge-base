#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

SCHEMA_FILES = {
    "concept": "schema/concept.schema.yaml",
    "claim": "schema/claim.schema.yaml",
    "source": "schema/source.schema.yaml",
}

VOCAB_FILES = {
    "locus": "vocab/locus.yaml",
    "knowledge_origin": "vocab/knowledge_origin.yaml",
    "facets": "vocab/facets.yaml",
    "disciplines": "vocab/disciplines.yaml",
    "traditions": "vocab/traditions.yaml",
    "modality": "vocab/modality.yaml",
    "basis": "vocab/basis.yaml",
    "predicate": "vocab/predicates.yaml",
}

SHARED_ENUM_PATHS = {
    "locus": ("concept", ("properties", "locus", "items", "enum")),
    "knowledge_origin": (
        "concept",
        ("properties", "knowledge_origin", "items", "enum"),
    ),
    "modality": ("claim", ("properties", "modality", "enum")),
    "basis": ("claim", ("properties", "basis", "items", "enum")),
    "predicate": ("claim", ("properties", "predicate", "enum")),
}


def repo_root() -> Path:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                text=True,
            ).strip()
        )
    except Exception:
        print("ERROR: run inside the repository.")
        sys.exit(2)


def load_yaml(path: Path, errors: list[str]):
    if not path.exists():
        errors.append(f"{path}: required file is missing")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: YAML parse error: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: top-level YAML value must be a mapping/object")
        return None
    return data


def load_vocab_path(path: Path, errors: list[str]):
    if not path.exists():
        errors.append(f"{path}: required vocabulary file is missing")
        return None
    data = load_yaml(path, errors)
    if data is None:
        return None
    values = data.get("values")
    if not isinstance(values, list) or not values:
        errors.append(f"{path}: 'values' must be a non-empty list")
        return None
    if not all(isinstance(v, str) for v in values):
        errors.append(f"{path}: all vocabulary values must be strings")
        return None
    if len(values) != len(set(values)):
        errors.append(f"{path}: duplicate vocabulary values")
    return values


def load_schemas(root: Path, errors: list[str]):
    schemas = {}
    for kind, rel in SCHEMA_FILES.items():
        schema = load_yaml(root / rel, errors)
        if schema is None:
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(f"{rel}: invalid JSON Schema: {exc}")
            continue
        schemas[kind] = schema
    return schemas


def get_path(obj, path):
    cur = obj
    for part in path:
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(part)
        cur = cur[part]
    return cur


def check_schema_vocab_sync(schemas, vocabs, errors):
    for vocab_name, (kind, path) in SHARED_ENUM_PATHS.items():
        if kind not in schemas or vocabs.get(vocab_name) is None:
            continue
        try:
            enum = get_path(schemas[kind], path)
        except KeyError:
            errors.append(
                f"{SCHEMA_FILES[kind]}: cannot find enum path for "
                f"vocabulary '{vocab_name}'"
            )
            continue
        if not isinstance(enum, list):
            errors.append(
                f"{SCHEMA_FILES[kind]}: enum for {vocab_name} is not a list"
            )
            continue
        if enum != vocabs[vocab_name]:
            errors.append(
                f"{vocab_name}: schema enum and vocabulary differ; "
                f"schema={enum!r}, vocab={vocabs[vocab_name]!r}"
            )


def record_files(root: Path):
    for directory in ("concepts", "claims", "sources"):
        path = root / "data" / directory
        if path.exists():
            yield from sorted(path.glob("*.yaml"))


def format_schema_path(parts):
    if not parts:
        return "<record>"
    out = ""
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            if out:
                out += "."
            out += str(part)
    return out


def schema_errors(schema, instance):
    validator = Draft202012Validator(schema)
    failures = []
    for err in sorted(
        validator.iter_errors(instance),
        key=lambda e: (list(e.absolute_path), list(e.absolute_schema_path)),
    ):
        failures.append(
            f"{format_schema_path(err.absolute_path)}: {err.message}"
        )
    return failures


def validate_vocab_only_fields(rel, data, vocabs, errors):
    if data.get("kind") != "concept":
        return
    for field in ("facets", "disciplines", "traditions"):
        values = data.get(field, [])
        if not isinstance(values, list):
            continue
        allowed = vocabs.get(field)
        if allowed is None:
            continue
        invalid = [value for value in values if value not in allowed]
        if invalid:
            errors.append(
                f"{rel}: invalid {field} value(s): {invalid!r}"
            )


def detect_log_contamination(lines: list[str]) -> list[int]:
    bad = []
    for number, line in enumerate(lines, 1):
        if not line.startswith("|"):
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        first = parts[1].strip()
        if first.startswith("====="):
            bad.append(number)
        elif re.match(r"^(A|M|D|R|\?\?)\s+[^|]+", first):
            bad.append(number)
        elif (
            "@" in first
            and ":" in first
            and ("$" in first or "~/" in first or "hsl-server" in first)
        ):
            bad.append(number)
    return bad


def fix_log(path: Path) -> int:
    if not path.exists():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    bad = set(detect_log_contamination(lines))
    if not bad:
        return 0
    kept = [
        line
        for number, line in enumerate(lines, 1)
        if number not in bad
    ]
    path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    return len(bad)


def find_broader_cycles(concepts):
    graph = {
        rid: [
            ref
            for ref in (data.get("broader") or [])
            if ref in concepts
        ]
        for rid, data in concepts.items()
    }
    state = {}
    stack = []
    cycles = []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt, 0) == 0:
                visit(nxt)
            elif state.get(nxt) == 1:
                idx = stack.index(nxt)
                cycles.append(stack[idx:] + [nxt])
        stack.pop()
        state[node] = 2

    for node in graph:
        if state.get(node, 0) == 0:
            visit(node)

    unique = []
    seen = set()
    for cycle in cycles:
        key = tuple(cycle)
        if key not in seen:
            seen.add(key)
            unique.append(cycle)
    return unique


def run_self_test(root, schemas):
    print("===== SELF TEST =====")
    concepts = sorted((root / "data" / "concepts").glob("*.yaml"))
    sources = sorted((root / "data" / "sources").glob("*.yaml"))

    if not concepts or not sources:
        print("SELF-TEST FAIL: requires at least one concept and source record")
        return False

    concept = yaml.safe_load(concepts[0].read_text(encoding="utf-8"))
    source = yaml.safe_load(sources[0].read_text(encoding="utf-8"))

    cases = []

    item = copy.deepcopy(concept)
    item["tradition"] = "should-fail"
    cases.append(("unknown field tradition", "concept", item))

    item = copy.deepcopy(source)
    item["year"] = "2011"
    cases.append(("year as string", "source", item))

    item = copy.deepcopy(concept)
    item["label"] = False
    cases.append(("boolean label from YAML typing", "concept", item))

    item = copy.deepcopy(concept)
    item["locus"] = ["artefact"]
    cases.append(("invalid locus artefact", "concept", item))

    ok = True
    for name, kind, record in cases:
        failures = schema_errors(schemas[kind], record)
        if failures:
            print(f"PASS: {name} rejected")
        else:
            print(f"FAIL: {name} incorrectly accepted")
            ok = False

    missing_errors = []
    load_vocab_path(
        root / "vocab" / "__definitely_missing_self_test__.yaml",
        missing_errors,
    )
    if missing_errors:
        print("PASS: missing vocabulary is a hard failure")
    else:
        print("FAIL: missing vocabulary incorrectly accepted")
        ok = False

    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")
    print()
    return ok


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Pilot integrity checks for Design Theory Taxonomy v0.1; "
            "--fix-log performs bounded log cleanup."
        )
    )
    parser.add_argument(
        "--fix-log",
        action="store_true",
        help=(
            "Remove obvious terminal/git-status contamination rows from "
            "pilot/PILOT_FAILURE_LOG.md."
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run rejection tests before validating the real corpus.",
    )
    args = parser.parse_args()

    root = repo_root()
    errors = []
    warnings = []

    if args.fix_log:
        removed = fix_log(root / "pilot" / "PILOT_FAILURE_LOG.md")
        print(
            f"FIX: removed {removed} obvious contamination row(s) "
            "from pilot/PILOT_FAILURE_LOG.md"
        )

    schemas = load_schemas(root, errors)

    vocabs = {}
    for name, rel in VOCAB_FILES.items():
        vocabs[name] = load_vocab_path(root / rel, errors)

    check_schema_vocab_sync(schemas, vocabs, errors)

    if errors:
        print("PRELOAD ERRORS")
        for error in errors:
            print(f"  - {error}")
        print(f"\nRESULT: FAIL ({len(errors)} error(s))")
        sys.exit(1)

    if args.self_test and not run_self_test(root, schemas):
        sys.exit(1)

    records = {}
    by_kind = {"concept": {}, "claim": {}, "source": {}}

    for path in record_files(root):
        rel = path.relative_to(root)
        data = load_yaml(path, errors)
        if data is None:
            continue

        kind = data.get("kind")
        if kind not in schemas:
            errors.append(
                f"{rel}: unsupported or missing kind: {kind!r}"
            )
            continue

        for failure in schema_errors(schemas[kind], data):
            errors.append(f"{rel}: schema validation: {failure}")

        validate_vocab_only_fields(rel, data, vocabs, errors)

        rid = data.get("id")
        if not isinstance(rid, str):
            continue

        expected_name = rid.split(":", 1)[-1] + ".yaml"
        if path.name != expected_name:
            errors.append(
                f"{rel}: filename must match ID slug ({expected_name})"
            )

        if rid in records:
            errors.append(
                f"{rel}: duplicate id {rid}; "
                f"already seen in {records[rid]}"
            )

        records[rid] = str(rel)
        by_kind[kind][rid] = data

        loci = data.get("locus")
        if (
            kind == "concept"
            and isinstance(loci, list)
            and len(loci) > 1
        ):
            warnings.append(
                f"{rel}: multiple locus values {loci}; "
                "review whether this term should be split into senses"
            )

    for rid, data in by_kind["concept"].items():
        rel = records[rid]

        for source in data.get("definition_sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        for field in ("broader", "part_of", "related", "opposite_of"):
            for ref in data.get(field, []) or []:
                if ref not in by_kind["concept"]:
                    errors.append(
                        f"{rel}: missing referenced concept {ref} in {field}"
                    )

        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing replacement concept {ref}"
                )

    for rid, data in by_kind["claim"].items():
        rel = records[rid]

        for field in ("subject", "object"):
            ref = data.get(field)
            if isinstance(ref, str) and ref not in by_kind["concept"]:
                errors.append(
                    f"{rel}: missing referenced concept {ref} in {field}"
                )

        for source in data.get("sources", []) or []:
            if source not in by_kind["source"]:
                errors.append(
                    f"{rel}: missing referenced source {source}"
                )

        for ref in data.get("replaced_by", []) or []:
            if ref not in by_kind["claim"]:
                errors.append(
                    f"{rel}: missing replacement claim {ref}"
                )

    for cycle in find_broader_cycles(by_kind["concept"]):
        errors.append("broader cycle: " + " -> ".join(cycle))

    log = root / "pilot" / "PILOT_FAILURE_LOG.md"
    if log.exists():
        bad = detect_log_contamination(
            log.read_text(encoding="utf-8").splitlines()
        )
        if bad:
            errors.append(
                "pilot/PILOT_FAILURE_LOG.md contains likely terminal-output "
                "contamination at line(s): "
                + ", ".join(map(str, bad))
                + ". Re-run with --fix-log for bounded cleanup."
            )

    total = sum(len(group) for group in by_kind.values())
    print(
        f"Pilot check: {total} record(s) — "
        f"{len(by_kind['concept'])} concept(s), "
        f"{len(by_kind['claim'])} claim(s), "
        f"{len(by_kind['source'])} source(s)."
    )

    if warnings:
        print("\nWARNINGS")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\nERRORS")
        for error in errors:
            print(f"  - {error}")
        print(
            f"\nRESULT: FAIL "
            f"({len(errors)} error(s), {len(warnings)} warning(s))"
        )
        sys.exit(1)

    print(f"\nRESULT: PASS ({len(warnings)} warning(s))")


if __name__ == "__main__":
    main()
