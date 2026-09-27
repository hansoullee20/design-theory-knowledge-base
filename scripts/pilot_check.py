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

STRUCTURAL_RELATIONS = ("is_a", "part_of", "related")


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


def find_cycles(concepts, field):
    graph = {
        rid: [
            ref
            for ref in (data.get(field) or [])
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


def loci(data):
    value = data.get("locus") or []
    return set(value) if isinstance(value, list) else set()


def unordered_pair(a, b):
    return tuple(sorted((a, b)))


def validate_structural_relations(concepts, errors, warnings):
    # All structural relations are irreflexive.
    for rid, data in concepts.items():
        for field in STRUCTURAL_RELATIONS:
            if rid in (data.get(field) or []):
                errors.append(f"{rid}: {field} is irreflexive; self-reference is invalid")

    # is_a and part_of are acyclic.
    for field in ("is_a", "part_of"):
        for cycle in find_cycles(concepts, field):
            errors.append(f"{field} cycle: " + " -> ".join(cycle))

    # is_a is subsumption: endpoints must have the same locus classification.
    for rid, data in concepts.items():
        for ref in data.get("is_a", []) or []:
            if ref not in concepts:
                continue
            if loci(data) != loci(concepts[ref]):
                errors.append(
                    "is_a locus mismatch: "
                    f"{rid} locus={sorted(loci(data))!r}; "
                    f"{ref} locus={sorted(loci(concepts[ref]))!r}"
                )

    # part_of should ordinarily stay within a locus; cross-locus is suspicious, not impossible.
    for rid, data in concepts.items():
        for ref in data.get("part_of", []) or []:
            if ref not in concepts:
                continue
            if not (loci(data) & loci(concepts[ref])):
                warnings.append(
                    f"{rid}: part_of endpoint {ref} shares no locus; "
                    "review whether this is genuine mereology rather than another relation"
                )

    # The same unordered pair cannot simultaneously assert subsumption and mereology.
    is_a_pairs = set()
    part_pairs = set()
    for rid, data in concepts.items():
        for ref in data.get("is_a", []) or []:
            if ref in concepts:
                is_a_pairs.add(unordered_pair(rid, ref))
        for ref in data.get("part_of", []) or []:
            if ref in concepts:
                part_pairs.add(unordered_pair(rid, ref))

    for pair in sorted(is_a_pairs & part_pairs):
        errors.append(
            f"{pair[0]} / {pair[1]}: pair cannot be both is_a and part_of"
        )

    # related is weaker than is_a/part_of; overlapping pairs are probably redundant.
    related_pairs = set()
    for rid, data in concepts.items():
        for ref in data.get("related", []) or []:
            if ref in concepts:
                related_pairs.add(unordered_pair(rid, ref))

    for pair in sorted(related_pairs & is_a_pairs):
        warnings.append(
            f"{pair[0]} / {pair[1]}: pair is both related and is_a; "
            "review redundant related edge"
        )

    for pair in sorted(related_pairs & part_pairs):
        warnings.append(
            f"{pair[0]} / {pair[1]}: pair is both related and part_of; "
            "review redundant related edge"
        )


def run_self_test(root, schemas):
    print("===== SELF TEST =====")
    concepts = sorted((root / "data" / "concepts").glob("*.yaml"))
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

    # Relation invariant tests operate on in-memory concepts only.
    base_a = copy.deepcopy(concept)
    base_b = copy.deepcopy(concept)
    base_a["id"] = "concept:self-test-a"
    base_b["id"] = "concept:self-test-b"
    base_a["locus"] = ["artifact"]
    base_b["locus"] = ["experience"]
    for record in (base_a, base_b):
        for field in STRUCTURAL_RELATIONS:
            record[field] = []

    relation_errors = []
    relation_warnings = []
    base_a["is_a"] = [base_a["id"]]
    validate_structural_relations(
        {base_a["id"]: base_a},
        relation_errors,
        relation_warnings,
    )
    if any("irreflexive" in err for err in relation_errors):
        print("PASS: self-referencing is_a rejected")
    else:
        print("FAIL: self-referencing is_a incorrectly accepted")
        ok = False

    base_a["is_a"] = [base_b["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {base_a["id"]: base_a, base_b["id"]: base_b},
        relation_errors,
        relation_warnings,
    )
    if any("is_a locus mismatch" in err for err in relation_errors):
        print("PASS: cross-locus is_a rejected")
    else:
        print("FAIL: cross-locus is_a incorrectly accepted")
        ok = False

    base_a["is_a"] = []
    base_a["part_of"] = [base_b["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {base_a["id"]: base_a, base_b["id"]: base_b},
        relation_errors,
        relation_warnings,
    )
    if any("shares no locus" in warning for warning in relation_warnings):
        print("PASS: cross-locus part_of warned")
    else:
        print("FAIL: cross-locus part_of produced no warning")
        ok = False

    base_a["locus"] = ["artifact"]
    base_b["locus"] = ["artifact"]
    base_a["is_a"] = [base_b["id"]]
    base_a["part_of"] = [base_b["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {base_a["id"]: base_a, base_b["id"]: base_b},
        relation_errors,
        relation_warnings,
    )
    if any("both is_a and part_of" in err for err in relation_errors):
        print("PASS: is_a/part_of pair collision rejected")
    else:
        print("FAIL: is_a/part_of pair collision incorrectly accepted")
        ok = False

    # Two-node cycle proves graph traversal, not merely self-loop rejection.
    cycle_a = copy.deepcopy(base_a)
    cycle_b = copy.deepcopy(base_b)
    cycle_a["locus"] = ["artifact"]
    cycle_b["locus"] = ["artifact"]
    for record in (cycle_a, cycle_b):
        for field in STRUCTURAL_RELATIONS:
            record[field] = []
    cycle_a["is_a"] = [cycle_b["id"]]
    cycle_b["is_a"] = [cycle_a["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {cycle_a["id"]: cycle_a, cycle_b["id"]: cycle_b},
        relation_errors,
        relation_warnings,
    )
    if any("is_a cycle:" in err for err in relation_errors):
        print("PASS: two-node is_a cycle rejected")
    else:
        print("FAIL: two-node is_a cycle incorrectly accepted")
        ok = False

    # Stronger hierarchy + related on the same pair should warn.
    rel_a = copy.deepcopy(base_a)
    rel_b = copy.deepcopy(base_b)
    rel_a["locus"] = ["artifact"]
    rel_b["locus"] = ["artifact"]
    for record in (rel_a, rel_b):
        for field in STRUCTURAL_RELATIONS:
            record[field] = []
    rel_a["is_a"] = [rel_b["id"]]
    rel_a["related"] = [rel_b["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {rel_a["id"]: rel_a, rel_b["id"]: rel_b},
        relation_errors,
        relation_warnings,
    )
    if any("both related and is_a" in warning for warning in relation_warnings):
        print("PASS: related/is_a overlap warned")
    else:
        print("FAIL: related/is_a overlap produced no warning")
        ok = False

    rel_a["is_a"] = []
    rel_a["part_of"] = [rel_b["id"]]
    rel_a["related"] = [rel_b["id"]]
    relation_errors = []
    relation_warnings = []
    validate_structural_relations(
        {rel_a["id"]: rel_a, rel_b["id"]: rel_b},
        relation_errors,
        relation_warnings,
    )
    if any("both related and part_of" in warning for warning in relation_warnings):
        print("PASS: related/part_of overlap warned")
    else:
        print("FAIL: related/part_of overlap produced no warning")
        ok = False

    # PF-006 / rev.9 normative-threshold schema tests.
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

    # PF-007 / rev.10 conventional-practice predicate tests.
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

    # DEPRECATION-01 / rev.11 lifecycle tests.
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

    # PF-001 relation-level locator self-tests.
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

    print("SELF-TEST RESULT:", "PASS" if ok else "FAIL")
    print()
    return ok



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

        locus_values = data.get("locus")
        if (
            kind == "concept"
            and isinstance(locus_values, list)
            and len(locus_values) > 1
        ):
            warnings.append(
                f"{rel}: multiple locus values {locus_values}; "
                "review whether this term should be split into senses"
            )

    for rid, data in by_kind["concept"].items():
        rel = records[rid]

        for source in data.get("definition_sources", []) or []:
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

        for ref in data.get("replaced_by", []) or []:
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
        by_kind["concept"],
        errors,
        warnings,
    )

    for rid, data in by_kind["claim"].items():
        rel = records[rid]

        for field in ("subject", "object"):
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

        for source in data.get("sources", []) or []:
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
