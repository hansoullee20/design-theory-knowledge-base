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

SOURCE_ID = "source:legge-bigelow-2011-print-size"


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
    old = p.read_text(encoding="utf-8") if p.exists() else None
    if old == text:
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
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


def validate_baseline() -> None:
    print("===== BASELINE VALIDATION =====")
    rc1 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py", "--self-test"],
        cwd=ROOT,
    ).returncode
    rc2 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py"],
        cwd=ROOT,
    ).returncode
    rc3 = subprocess.run(
        ["git", "diff", "--check"],
        cwd=ROOT,
    ).returncode
    if rc1 or rc2 or rc3:
        fail("baseline validation failed; no ACTOR-LOCUS mutation attempted")


def insert_yaml_list_value_after(
    rel: str,
    list_key: str,
    after_value: str,
    new_value: str,
) -> None:
    text = read(rel)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        fail(f"{rel}: expected mapping")

    if rel == "vocab/locus.yaml":
        values = data.get(list_key)
    else:
        try:
            values = data["properties"]["locus"]["items"]["enum"]
        except Exception:
            fail(f"{rel}: locus enum path not found")

    if not isinstance(values, list):
        fail(f"{rel}: target list not found")

    if new_value in values:
        print(f"UNCHANGED: {rel} already contains {new_value}")
        return

    if after_value not in values:
        fail(f"{rel}: anchor value {after_value!r} not found")

    lines = text.splitlines(keepends=True)
    candidate_indexes = []
    pattern = re.compile(
        r"^(?P<indent>\s*)-\s*(?P<quote>['\"]?)"
        + re.escape(after_value)
        + r"(?P=quote)\s*$"
    )

    for i, line in enumerate(lines):
        if pattern.match(line.rstrip("\n")):
            candidate_indexes.append(i)

    if len(candidate_indexes) != 1:
        fail(
            f"{rel}: expected exactly one list item for {after_value!r}; "
            f"found {len(candidate_indexes)}"
        )

    i = candidate_indexes[0]
    m = pattern.match(lines[i].rstrip("\n"))
    assert m is not None
    indent = m.group("indent")
    quote = m.group("quote")
    newline = "\n" if lines[i].endswith("\n") else ""
    rendered = f"{indent}- {quote}{new_value}{quote}{newline}"
    lines.insert(i + 1, rendered)
    write(rel, "".join(lines))


def update_locus_vocab() -> None:
    insert_yaml_list_value_after(
        "vocab/locus.yaml",
        "values",
        "artifact",
        "actor",
    )


def update_concept_schema() -> None:
    insert_yaml_list_value_after(
        "schema/concept.schema.yaml",
        "enum",
        "artifact",
        "actor",
    )


def update_foundation() -> None:
    rel = "docs/PROJECT_FOUNDATION.md"
    text = read(rel)

    text = text.replace(
        "**Status:** Working architecture decision record (rev. 4). Decisions may be superseded; see §17.",
        "**Status:** Working architecture decision record (rev. 5). Decisions may be superseded; see §17.",
        1,
    )

    start = text.find("### 5.3 Classification fields")
    end = text.find("### 5.4", start + 1)
    if start < 0 or end < 0:
        fail(f"{rel}: §5.3/§5.4 boundary not found")

    section = text[start:end]
    locus_start = section.find("- `locus`")
    facets_start = section.find("- `facets`", locus_start + 1)
    if locus_start < 0 or facets_start < 0:
        fail(f"{rel}: locus/facets boundary inside §5.3 not found")

    locus_block = """- `locus` (**required**): where a property is borne. For person-borne properties, elicitation distinguishes what the actor brings to an engagement from what the engagement elicits.
  - `artifact`: borne by the designed artifact or environment itself
  - `actor`: borne by the person and brought to the engagement independently of this artifact — a capability, characteristic, or learned capacity (visual acuity, hand size, expertise, familiarity with a convention)
  - `actor-relative`: borne by the relation between artifact/environment and an actor's capabilities (ecological affordance, typeface legibility, critical print size)
  - `experience`: borne by the person and elicited by engagement with the artifact/environment — a perceptual, cognitive, or affective state (grouping, perceived density, perceived affordance)
  - `outcome`: borne by an episode of use, available for measurement
  - `practice`: borne by an activity of designing, researching, or evaluating

  `actor` and `experience` share the person as bearer and are separated by elicitation, not by persistence: if the property changes when the artifact changes, it is `experience`; if it is brought to the engagement, it is `actor`.
  An `actor` concept is admitted only when it is a claim subject or object, or is named in an actor-relative concept's definition. Population descriptors with values ("readers with 20/40 acuity") are claim `scope` now and `observation` records later; they are never concepts.
  The same term may require different senses across loci: expertise brought to an episode is `actor`; a gain in skill produced by an episode is `outcome`.

  `outcome` is strictly a locus value. It names a construct, not a measured result; measured results are `observation` records (§10). A record with more than one locus value must be reviewed for splitting into senses rather than using multiple loci to encode a relation.

  Classify the thing, not its function: an artifact-locus definition may state the artifact element's intended purpose, but it must not define the concept by an achieved effect on an actor; achieved effects are claims.
"""

    section = section[:locus_start] + locus_block + section[facets_start:]
    text = text[:start] + section + text[end:]

    old_patterns = [
        r"- A \*\*measurable variable\*\* is an `outcome`-, `experience`-, or `actor-relative`-locus concept \*\*`operationalized_by`\*\* a `method`\.",
        r"- A \*\*measurable variable\*\* is an `outcome`- or `experience`-locus concept \*\*`operationalized_by`\*\* a `method`\.",
    ]
    replacement = "- Any concept may be **`operationalized_by`** a `method`."
    if replacement not in text:
        replaced = False
        for pat in old_patterns:
            text2, n = re.subn(pat, replacement, text, count=1)
            if n:
                text = text2
                replaced = True
                break
        if not replaced:
            fail(f"{rel}: §10.1 operationalization sentence not found")

    rev5 = (
        "| 5 | 2026-09-26 | PF-003 resolved: added `actor` locus for person-borne "
        "capabilities/characteristics brought to an engagement; distinguished `actor` "
        "from `experience` by elicitation rather than persistence; added actor admission "
        "and population-descriptor rules; generalized `operationalized_by` to any concept. |"
    )
    if rev5 not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for line in lines:
            out.append(line)
            if line.startswith("| 4 | 2026-09-26 |"):
                out.append(rev5)
                inserted = True
        if not inserted:
            fail(f"{rel}: rev. 4 decision-log row not found")
        text = "\n".join(out).rstrip() + "\n"

    write(rel, text)


def clear_relations(data: dict) -> None:
    for key in ("broader", "part_of", "related", "opposite_of", "replaced_by"):
        if key in data:
            data[key] = []


def build_visual_acuity() -> None:
    rel = "data/concepts/visual-acuity.yaml"
    if (ROOT / rel).exists():
        print(f"UNCHANGED: {rel} already exists")
        return

    template = load_yaml("data/concepts/print-size.yaml")
    data = copy.deepcopy(template)
    data["id"] = "concept:visual-acuity"
    data["kind"] = "concept"
    data["label"] = "Visual acuity"
    data["definition"] = (
        "The capacity to resolve fine spatial detail, with greater visual acuity "
        "meaning that finer detail can be resolved."
    )
    data["definition_sources"] = [SOURCE_ID]
    data["locus"] = ["actor"]
    if "aliases" in data:
        data["aliases"] = []
    if "facets" in data:
        data["facets"] = []
    if "disciplines" in data:
        data["disciplines"] = []
    if "knowledge_origin" in data:
        data["knowledge_origin"] = ["perceptual-science"]
    if "traditions" in data:
        data["traditions"] = []
    clear_relations(data)
    if "notes" in data:
        data["notes"] = (
            "Polarity is conceptual rather than tied to a measurement scale: "
            "greater acuity means finer spatial detail resolved. An operationalization "
            "such as logMAR may use an inverse numeric direction."
        )

    write(rel, dump_yaml(data))


def build_critical_print_size() -> None:
    rel = "data/concepts/critical-print-size.yaml"
    if (ROOT / rel).exists():
        print(f"UNCHANGED: {rel} already exists")
        return

    template = load_yaml("data/concepts/legibility-typeface.yaml")
    data = copy.deepcopy(template)
    data["id"] = "concept:critical-print-size"
    data["kind"] = "concept"
    data["label"] = "Critical print size"
    data["definition"] = (
        "The smallest character size at which reading can occur at maximum speed "
        "for a reader under specified conditions."
    )
    data["definition_sources"] = [SOURCE_ID]
    data["locus"] = ["actor-relative"]
    if "aliases" in data:
        data["aliases"] = []
    if "facets" in data:
        data["facets"] = []
    if "disciplines" in data:
        data["disciplines"] = []
    if "knowledge_origin" in data:
        data["knowledge_origin"] = ["perceptual-science"]
    if "traditions" in data:
        data["traditions"] = []
    clear_relations(data)
    if "notes" in data:
        data["notes"] = (
            "Distinct from letter acuity and reading acuity; it is a threshold "
            "defined relative to reading performance for a reader and stimulus conditions."
        )

    write(rel, dump_yaml(data))


def build_claim() -> None:
    rel = "data/claims/visual-acuity-influences-critical-print-size.yaml"
    if (ROOT / rel).exists():
        print(f"UNCHANGED: {rel} already exists")
        return

    template = load_yaml("data/claims/print-size-influences-reading-speed.yaml")
    data = copy.deepcopy(template)
    data["id"] = "claim:visual-acuity-influences-critical-print-size"
    data["kind"] = "claim"
    data["statement"] = "Visual acuity influences critical print size."
    data["subject"] = "concept:visual-acuity"
    data["predicate"] = "influences"
    data["object"] = "concept:critical-print-size"
    if "modality" in data:
        data["modality"] = "descriptive"
    if "basis" in data:
        data["basis"] = ["empirical"]
    if "evidence_status" in data:
        data["evidence_status"] = "unassessed"
    if "scope" in data:
        data["scope"] = (
            "Greater visual acuity is associated with smaller critical print size "
            "(Legge & Bigelow, 2011)."
        )
    data["sources"] = [SOURCE_ID]
    if "replaced_by" in data:
        data["replaced_by"] = []
    if "notes" in data:
        data["notes"] = (
            "The directional association is recorded in scope. The predicate remains "
            "influences rather than decreases because numeric direction belongs to a "
            "specific operationalization; the concept definition itself has explicit polarity."
        )

    write(rel, dump_yaml(data))


def resolve_pf003() -> None:
    rel = "pilot/PILOT_FAILURE_LOG.md"
    text = read(rel)
    replacement = (
        "| PF-003 | Actor-characteristic concepts had no locus | "
        "The visual-acuity stress test confirmed that a source-defined actor capability "
        "could not be represented honestly by artifact, actor-relative, experience, outcome, "
        "or practice. | locus vocabulary | Added `actor`; distinguished actor from experience "
        "by elicitation rather than persistence; added actor admission and population-descriptor "
        "rules; canonicalized visual acuity as actor and critical print size as actor-relative. | "
        "Preserve the elicitation boundary in remaining pilot cases; expertise brought to an "
        "episode is actor, learning gain from the episode is outcome. | resolved |"
    )

    lines = text.splitlines()
    out = []
    found = False
    for line in lines:
        if line.startswith("| PF-003 |"):
            out.append(replacement)
            found = True
        else:
            out.append(line)
    if not found:
        fail(f"{rel}: PF-003 row not found")

    write(rel, "\n".join(out).rstrip() + "\n")


def update_pilot_records() -> None:
    rel = "pilot/PILOT_RECORDS.md"
    text = read(rel)

    section = """## ACTOR-LOCUS-IMPLEMENTATION-01

- [x] `concept:visual-acuity` — `locus: [actor]`; conceptual polarity fixed as greater acuity = finer detail resolved.
- [x] `concept:critical-print-size` — `locus: [actor-relative]`.
- [x] `claim:visual-acuity-influences-critical-print-size` — directional association retained in `scope`.
- [ ] Freeze gate: exercise predicate `decreases` with a case whose conceptual polarity is unambiguous. Assigned case: whitespace → perceived density.
"""

    if "## ACTOR-LOCUS-IMPLEMENTATION-01" not in text:
        text = text.rstrip() + "\n\n" + section
    write(rel, text)


def verify_source() -> None:
    found = False
    for p in (ROOT / "data" / "sources").glob("*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and data.get("id") == SOURCE_ID:
            found = True
            print(f"VERIFIED SOURCE: {p.relative_to(ROOT)}")
            break
    if not found:
        fail(f"source record not found: {SOURCE_ID}")


def main() -> None:
    validate_baseline()
    verify_source()

    print("\n===== ACTOR LOCUS =====")
    update_locus_vocab()
    update_concept_schema()
    update_foundation()

    print("\n===== PF-003 RECORDS =====")
    build_visual_acuity()
    build_critical_print_size()
    build_claim()
    resolve_pf003()
    update_pilot_records()

    print("\n===== FINAL VALIDATION =====")
    rc1 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py", "--self-test"],
        cwd=ROOT,
    ).returncode
    rc2 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py"],
        cwd=ROOT,
    ).returncode
    rc3 = subprocess.run(
        ["git", "diff", "--check"],
        cwd=ROOT,
    ).returncode

    vocab = load_yaml("vocab/locus.yaml")["values"]
    schema = load_yaml("schema/concept.schema.yaml")["properties"]["locus"]["items"]["enum"]

    print("\n===== LOCUS ENUM SYNC =====")
    print("vocab :", vocab)
    print("schema:", schema)
    if vocab != schema:
        fail("schema locus enum != vocab locus values")

    print("\n===== PF-003 ROW =====")
    for line in read("pilot/PILOT_FAILURE_LOG.md").splitlines():
        if line.startswith("| PF-003 |"):
            print(line)

    print("\n===== DECREASES FREEZE GATE =====")
    if "whitespace → perceived density" not in read("pilot/PILOT_RECORDS.md"):
        fail("decreases freeze-gate assignment missing")
    print("PASS: decreases assigned to whitespace → perceived density")

    print("\n===== GIT STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\n===== DIFF STAT =====")
    subprocess.run(["git", "diff", "--stat"], cwd=ROOT)

    if rc1 or rc2 or rc3:
        print("\nRESULT: ACTOR-LOCUS-IMPLEMENTATION-01 FAILED.")
        sys.exit(1)

    print("\nRESULT: ACTOR-LOCUS-IMPLEMENTATION-01 PASSED.")
    print("Expected corpus: 32 records — 15 concepts, 6 claims, 11 sources.")
    print("PF-003 resolved.")
    print("Predicate decreases remains intentionally untested and assigned to whitespace → perceived density.")
    print("No commit was created.")


if __name__ == "__main__":
    main()
