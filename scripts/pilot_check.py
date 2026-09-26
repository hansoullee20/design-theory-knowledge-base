#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: python3 -m pip install --user pyyaml")
    sys.exit(2)

ID_PATTERNS = {
    "concept": re.compile(r"^concept:[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "claim": re.compile(r"^claim:[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "source": re.compile(r"^source:[a-z0-9]+(?:-[a-z0-9]+)*$"),
}

REQUIRED = {
    "concept": {"id", "kind", "label", "definition", "definition_sources", "locus", "record_status", "schema_version"},
    "claim": {"id", "kind", "statement", "modality", "subject", "predicate", "object", "basis", "evidence_status", "sources", "record_status", "schema_version"},
    "source": {"id", "kind", "citation", "source_type", "schema_version"},
}

VOCAB_FIELDS = {
    "locus": ("vocab/locus.yaml", "locus"),
    "knowledge_origin": ("vocab/knowledge_origin.yaml", "knowledge_origin"),
    "facets": ("vocab/facets.yaml", "facets"),
    "disciplines": ("vocab/disciplines.yaml", "disciplines"),
    "traditions": ("vocab/traditions.yaml", "traditions"),
    "modality": ("vocab/modality.yaml", "modality"),
    "basis": ("vocab/basis.yaml", "basis"),
    "predicate": ("vocab/predicates.yaml", "predicate"),
}

def repo_root() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return Path(out)
    except Exception:
        print("ERROR: run this script inside the repository.")
        sys.exit(2)

def load_yaml(path: Path, errors: list[str]):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{path}: YAML parse error: {e}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: top-level YAML value must be a mapping/object")
        return None
    return data

def load_vocab(root: Path, rel: str, errors: list[str]) -> set[str]:
    path = root / rel
    if not path.exists():
        return set()
    data = load_yaml(path, errors)
    if not data:
        return set()
    vals = data.get("values", [])
    if not isinstance(vals, list):
        errors.append(f"{path}: 'values' must be a list")
        return set()
    return {str(v) for v in vals}

def record_files(root: Path):
    for kind in ("concepts", "claims", "sources"):
        d = root / "data" / kind
        if d.exists():
            yield from sorted(d.glob("*.yaml"))

def check_git_diff(root: Path, errors: list[str]):
    p = subprocess.run(["git", "diff", "--check"], cwd=root, text=True, capture_output=True)
    if p.returncode != 0 or p.stdout.strip():
        msg = p.stdout.strip() or p.stderr.strip()
        errors.append("git diff --check failed:\n" + msg)

def detect_log_contamination(lines: list[str]) -> list[int]:
    bad = []
    for i, line in enumerate(lines, start=1):
        if not line.startswith("|"):
            continue
        first = line.split("|", 2)[1].strip()
        if not first:
            continue
        if first.startswith("====="):
            bad.append(i)
            continue
        if re.match(r"^(A|M|D|R|\?\?)\s+[^|]+", first):
            bad.append(i)
            continue
        if "@" in first and ":" in first and ("$" in first or "~/" in first or "hsl-server" in first):
            bad.append(i)
    return bad

def fix_log(path: Path) -> int:
    if not path.exists():
        return 0
    lines = path.read_text(encoding="utf-8").splitlines()
    bad = set(detect_log_contamination(lines))
    if not bad:
        return 0
    kept = [line for i, line in enumerate(lines, start=1) if i not in bad]
    path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    return len(bad)

def main():
    ap = argparse.ArgumentParser(description="Read-only pilot integrity checks for Design Theory Taxonomy v0.1.")
    ap.add_argument("--fix-log", action="store_true", help="Remove obvious terminal/git-status contamination rows from pilot/PILOT_FAILURE_LOG.md.")
    args = ap.parse_args()

    root = repo_root()
    errors: list[str] = []
    warnings: list[str] = []

    if args.fix_log:
        n = fix_log(root / "pilot" / "PILOT_FAILURE_LOG.md")
        print(f"FIX: removed {n} obvious contamination row(s) from pilot/PILOT_FAILURE_LOG.md")

    check_git_diff(root, errors)

    vocab = {}
    for field, (rel, _) in VOCAB_FIELDS.items():
        vocab[field] = load_vocab(root, rel, errors)

    records = {}
    by_kind = {"concept": {}, "claim": {}, "source": {}}

    for path in record_files(root):
        data = load_yaml(path, errors)
        if not data:
            continue

        kind = data.get("kind")
        rid = data.get("id")
        rel = path.relative_to(root)

        if kind not in REQUIRED:
            errors.append(f"{rel}: unsupported or missing kind: {kind!r}")
            continue

        missing = sorted(REQUIRED[kind] - set(data))
        if missing:
            errors.append(f"{rel}: missing required field(s): {', '.join(missing)}")

        if not isinstance(rid, str) or not ID_PATTERNS[kind].match(rid):
            errors.append(f"{rel}: invalid {kind} id: {rid!r}")
            continue

        expected_slug = rid.split(":", 1)[1] + ".yaml"
        if path.name != expected_slug:
            errors.append(f"{rel}: filename must match ID slug ({expected_slug})")

        if rid in records:
            errors.append(f"{rel}: duplicate id {rid}; already seen in {records[rid]}")
        records[rid] = str(rel)
        by_kind[kind][rid] = data

        if data.get("schema_version") != "0.1":
            errors.append(f"{rel}: schema_version must be '0.1'")

        if kind == "concept":
            ds = data.get("definition_sources")
            if not isinstance(ds, list) or not ds:
                errors.append(f"{rel}: definition_sources must contain at least one source id")

            loci = data.get("locus")
            if not isinstance(loci, list) or not loci:
                errors.append(f"{rel}: locus must contain at least one value")
            elif len(loci) > 1:
                warnings.append(f"{rel}: multiple locus values {loci}; review whether this term should be split into senses")

            for field in ("locus", "knowledge_origin", "facets", "disciplines", "traditions"):
                vals = data.get(field, [])
                if vals is None:
                    vals = []
                if not isinstance(vals, list):
                    errors.append(f"{rel}: {field} must be a list")
                    continue
                allowed = vocab.get(field, set())
                if allowed:
                    bad = [v for v in vals if v not in allowed]
                    if bad:
                        errors.append(f"{rel}: invalid {field} value(s): {bad}")

            for field in ("broader", "part_of", "related", "opposite_of", "replaced_by"):
                vals = data.get(field, [])
                if vals is None:
                    vals = []
                if not isinstance(vals, list):
                    errors.append(f"{rel}: {field} must be a list")
                else:
                    for ref in vals:
                        if not isinstance(ref, str) or not ID_PATTERNS["concept"].match(ref):
                            errors.append(f"{rel}: invalid concept reference in {field}: {ref!r}")

        elif kind == "claim":
            if data.get("modality") not in vocab.get("modality", set()):
                errors.append(f"{rel}: invalid modality {data.get('modality')!r}")
            if data.get("predicate") not in vocab.get("predicate", set()):
                errors.append(f"{rel}: invalid predicate {data.get('predicate')!r}")

            basis = data.get("basis")
            if not isinstance(basis, list) or not basis:
                errors.append(f"{rel}: basis must contain at least one value")
            else:
                bad = [v for v in basis if v not in vocab.get("basis", set())]
                if bad:
                    errors.append(f"{rel}: invalid basis value(s): {bad}")

            if data.get("evidence_status") not in {"unassessed", "assessed"}:
                errors.append(f"{rel}: evidence_status must be unassessed or assessed")

            srcs = data.get("sources")
            if not isinstance(srcs, list) or not srcs:
                errors.append(f"{rel}: sources must contain at least one source id")

            for field in ("subject", "object"):
                ref = data.get(field)
                if not isinstance(ref, str) or not ID_PATTERNS["concept"].match(ref):
                    errors.append(f"{rel}: {field} must be a concept id")

        elif kind == "source":
            st = data.get("source_type")
            allowed = {"paper", "book", "textbook", "standard", "web", "report", "other"}
            if st not in allowed:
                errors.append(f"{rel}: invalid source_type {st!r}")

    # Referential integrity
    for rid, data in by_kind["concept"].items():
        rel = records[rid]
        for src in data.get("definition_sources", []):
            if src not in by_kind["source"]:
                errors.append(f"{rel}: missing referenced source {src}")
        for field in ("broader", "part_of", "related", "opposite_of", "replaced_by"):
            for ref in data.get(field, []) or []:
                if ref not in by_kind["concept"]:
                    errors.append(f"{rel}: missing referenced concept {ref} in {field}")

    for rid, data in by_kind["claim"].items():
        rel = records[rid]
        for field in ("subject", "object"):
            ref = data.get(field)
            if ref not in by_kind["concept"]:
                errors.append(f"{rel}: missing referenced concept {ref} in {field}")
        for src in data.get("sources", []) or []:
            if src not in by_kind["source"]:
                errors.append(f"{rel}: missing referenced source {src}")

    # Pilot log contamination
    log = root / "pilot" / "PILOT_FAILURE_LOG.md"
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        bad_lines = detect_log_contamination(lines)
        if bad_lines:
            errors.append(
                "pilot/PILOT_FAILURE_LOG.md contains likely terminal-output contamination at line(s): "
                + ", ".join(map(str, bad_lines))
                + ". Re-run with --fix-log to remove only obvious contamination rows."
            )

    total = sum(len(v) for v in by_kind.values())
    print(f"Pilot check: {total} record(s) — "
          f"{len(by_kind['concept'])} concept(s), "
          f"{len(by_kind['claim'])} claim(s), "
          f"{len(by_kind['source'])} source(s).")

    if warnings:
        print("\nWARNINGS")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\nERRORS")
        for e in errors:
            print(f"  - {e}")
        print(f"\nRESULT: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        sys.exit(1)

    print(f"\nRESULT: PASS ({len(warnings)} warning(s))")

if __name__ == "__main__":
    main()
