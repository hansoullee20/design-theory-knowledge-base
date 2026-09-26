#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
)

EXPECTED_COUNTS = (40, 22, 6, 12)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(2)


def run(cmd: list[str], capture: bool = False):
    print("$ " + " ".join(cmd))
    return subprocess.run(
        cmd, cwd=ROOT, text=True, capture_output=capture
    )


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def count_records():
    concepts = list((ROOT / "data" / "concepts").glob("*.yaml"))
    claims = list((ROOT / "data" / "claims").glob("*.yaml"))
    sources = list((ROOT / "data" / "sources").glob("*.yaml"))
    return (
        len(concepts) + len(claims) + len(sources),
        len(concepts),
        len(claims),
        len(sources),
    )


def verify_preconditions() -> None:
    print("===== PRECONDITIONS =====")

    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    if branch != "main":
        fail(f"expected branch main, got {branch!r}")

    foundation = read("docs/PROJECT_FOUNDATION.md")
    if "(rev. 7)" not in foundation:
        fail("expected PROJECT_FOUNDATION.md rev. 7")
    if "opposite_of" in read("schema/concept.schema.yaml"):
        fail("FIGURE-GROUND-01 removal incomplete: schema still contains opposite_of")
    if "PF-005" not in read("pilot/PILOT_FAILURE_LOG.md"):
        fail("PF-005 resolution is not recorded")
    if count_records() != EXPECTED_COUNTS:
        fail(f"expected corpus {EXPECTED_COUNTS}, got {count_records()}")

    for cmd in (
        [sys.executable, "scripts/pilot_check.py", "--self-test"],
        [sys.executable, "scripts/pilot_check.py"],
        ["git", "diff", "--check"],
    ):
        p = run(cmd, capture=True)
        print(p.stdout, end="")
        if p.stderr:
            print(p.stderr, end="", file=sys.stderr)
        if p.returncode:
            fail("precondition command failed")

    checker = read("scripts/pilot_check.py")
    if 'STRUCTURAL_RELATIONS = ("is_a", "part_of", "related")' not in checker:
        fail("checker structural-relation tuple is not post-FIGURE-GROUND state")

    print("PRECONDITIONS: PASS")


def patch_foundation() -> None:
    rel = "docs/PROJECT_FOUNDATION.md"
    text = read(rel)

    text = text.replace(
        "Working architecture decision record (rev. 7)",
        "Working architecture decision record (rev. 8)",
        1,
    )

    # Normalize the ENABLES sentence if a renderer artifact became literal.
    text = text.replace(
        "There is **no structural&#x20;****`ENABLES`****&#x20;relation**, and no `AFFECTS`.",
        "There is **no structural `ENABLES` relation**, and no `AFFECTS`.",
    )

    old_is_a = (
        "- `is_a`: on concept A, lists concept B when every instance of A is an "
        "instance of B (subsumption). It is transitive, irreflexive, antisymmetric, "
        "and acyclic. Endpoints must share the same `locus`."
    )
    new_is_a = (
        "- `is_a`: on concept A, lists concept B when every instance of A is an "
        "instance of B (subsumption). It is transitive, irreflexive, antisymmetric, "
        "and acyclic. Endpoints must share the same `locus`. Only direct asserted "
        "edges are stored; transitive closure is derived. A directly stored edge "
        "already implied by another asserted path is redundant and should not be "
        "stored, but is not a v0.1 validation error."
    )
    if old_is_a not in text:
        fail("expected rev. 7 is_a semantics sentence not found")
    text = text.replace(old_is_a, new_is_a, 1)

    old_part = (
        "- `part_of`: on concept A, lists concept B when A is a proper spatial, "
        "temporal, or structural constituent of instances of B. It does not mean "
        "dimension-of, attribute-of, feature-of, role-of, cause-of, or a step that "
        "produces B. It is transitive, irreflexive, and acyclic. Same-locus endpoints "
        "are expected; a cross-locus edge requires review."
    )
    new_part = (
        "- `part_of`: on concept A, lists concept B when A is a proper spatial, "
        "temporal, or structural constituent of instances of B. It does not mean "
        "dimension-of, attribute-of, feature-of, role-of, cause-of, membership in a "
        "collection or set, or a step that produces B. It is irreflexive and acyclic. "
        "Transitive closure is derived only through compatible constituent senses; "
        "no transitive inference is licensed across excluded relation types. Because "
        "v0.1 does not encode meronymy subtypes, such closure is conservative and is "
        "not materialized as asserted edges. Same-locus endpoints are expected; a "
        "cross-locus edge requires review."
    )
    if old_part not in text:
        fail("expected rev. 7 part_of semantics sentence not found")
    text = text.replace(old_part, new_part, 1)

    old_validation = (
        "4. The same concept pair cannot simultaneously be linked by both `is_a` "
        "and `part_of`."
    )
    new_validation = (
        "4. The same concept pair cannot simultaneously be linked by both `is_a` "
        "and `part_of`.\n"
        "5. If a pair linked by `is_a` or `part_of` is also linked by `related`, "
        "the checker emits a review warning because the weaker navigational edge is "
        "probably redundant."
    )
    if old_validation not in text:
        fail("validation invariant 4 not found")
    text = text.replace(old_validation, new_validation, 1)

    # Add semantic-direction limitation after source-discipline paragraph.
    anchor = (
        "`is_a` and `part_of` are ontological assertions and should be supported "
        "by the same source discipline as definitions. `related` is navigational."
    )
    addition = anchor + (
        "\n\nThe checker validates graph structure, not the semantic direction of "
        "an otherwise well-formed edge. For example, `gutter part_of grid` and the "
        "semantically reversed `grid part_of gutter` are both structurally "
        "well-formed; definition and source review must determine which direction is "
        "true."
    )
    if anchor not in text:
        fail("source-discipline anchor not found")
    text = text.replace(anchor, addition, 1)

    # Standards-alignment wording.
    old_mapping = (
        "| `is_a` | exportable as `skos:broader`; exportable as "
        "`rdfs:subClassOf` only when project concepts are modeled as classes |"
    )
    new_mapping = (
        "| `is_a` | direct asserted edges are exportable as `skos:broader`; "
        "derived transitive closure is not emitted as additional `skos:broader` "
        "assertions; exportable as `rdfs:subClassOf` only when project concepts "
        "are modeled as classes |"
    )
    if old_mapping not in text:
        fail("§18 is_a mapping row not found")
    text = text.replace(old_mapping, new_mapping, 1)

    old_dc = "| source metadata | Dublin Core-compatible |"
    new_dc = (
        "| source metadata | Dublin Core terms are the target for a future structured "
        "citation representation; the current free-string `citation` field is "
        "project-native |"
    )
    if old_dc not in text:
        fail("§18 source metadata row not found")
    text = text.replace(old_dc, new_dc, 1)

    row8 = (
        "| 8 | 2026-09-26 | PRE-FREEZE-HARDENING-01: clarified direct asserted "
        "`is_a` storage and derived closure; constrained `part_of` transitivity "
        "to compatible constituent senses and excluded collection membership; added "
        "`related`/hierarchy overlap warnings, stronger cycle self-test coverage, "
        "clearer locus-mismatch diagnostics, and documented the directional-edge "
        "review limitation. |"
    )
    if row8 not in text:
        lines = text.splitlines()
        idx = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("| 7 | 2026-09-26 |")
            ),
            None,
        )
        if idx is None:
            fail("foundation decision-log row 7 not found")
        lines.insert(idx + 1, row8)
        text = "\n".join(lines).rstrip() + "\n"

    write(rel, text)


def patch_plugin() -> None:
    rel = "docs/PLUGIN_TARGET_ARCHITECTURE.md"
    text = read(rel)

    if "foundation rev. 7" not in text:
        fail("runtime contract rev. 7 foundation reference not found")

    text = text.replace("foundation rev. 7", "foundation rev. 8")

    # If the companion line uses "rev. 7" without "foundation rev. 7",
    # reconcile that as well.
    text = re.sub(
        r"(Companion to `docs/PROJECT_FOUNDATION\.md` )rev\. 7",
        r"\1rev. 8",
        text,
        count=1,
    )

    write(rel, text)


def patch_checker() -> None:
    rel = "scripts/pilot_check.py"
    text = read(rel)

    old_locus = '''                errors.append(
                    f"{rid}: is_a endpoint {ref} must share the same locus; "
                    f"{sorted(loci(data))!r} != {sorted(loci(concepts[ref]))!r}"
                )'''
    new_locus = '''                errors.append(
                    "is_a locus mismatch: "
                    f"{rid} locus={sorted(loci(data))!r}; "
                    f"{ref} locus={sorted(loci(concepts[ref]))!r}"
                )'''
    if old_locus not in text:
        fail("checker locus-mismatch block not found")
    text = text.replace(old_locus, new_locus, 1)

    pair_anchor = '''    for pair in sorted(is_a_pairs & part_pairs):
        errors.append(
            f"{pair[0]} / {pair[1]}: pair cannot be both is_a and part_of"
        )
'''
    pair_replacement = pair_anchor + '''
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
'''
    if pair_anchor not in text:
        fail("checker pair-collision anchor not found")
    text = text.replace(pair_anchor, pair_replacement, 1)

    # Existing cross-locus self-test message follows checker diagnostic.
    text = text.replace(
        'if any("must share the same locus" in err for err in relation_errors):',
        'if any("is_a locus mismatch" in err for err in relation_errors):',
        1,
    )

    self_anchor = '''    if any("both is_a and part_of" in err for err in relation_errors):
        print("PASS: is_a/part_of pair collision rejected")
    else:
        print("FAIL: is_a/part_of pair collision incorrectly accepted")
        ok = False
'''
    self_extra = self_anchor + '''
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
'''
    if self_anchor not in text:
        fail("checker self-test insertion anchor not found")
    text = text.replace(self_anchor, self_extra, 1)

    write(rel, text)


def patch_pilot_records() -> None:
    rel = "pilot/PILOT_RECORDS.md"
    text = read(rel)

    block = '''
## PRE-FREEZE-HARDENING-01

- [x] Only direct asserted `is_a` edges are stored; transitive closure is derived.
- [x] Redundant direct `is_a` edges implied by closure are discouraged but are not a v0.1 validation error.
- [x] `part_of` excludes membership in a collection or set.
- [x] `part_of` closure is only licensed through compatible constituent senses; v0.1 does not add a meronymy-subtype field.
- [x] `related` overlapping an `is_a` or `part_of` pair produces a review warning.
- [x] Two-node `is_a` cycle self-test added.
- [x] `is_a` locus-mismatch diagnostics show both endpoint locus sets.
- [x] Directional-edge semantic correctness remains a source/definition-review responsibility; the checker does not infer direction from labels.
- [ ] DEPRECATION-01 must decide whether references to deprecated records warn, fail, or resolve through `replaced_by`; no rule is activated before that pilot.
'''

    if "## PRE-FREEZE-HARDENING-01" not in text:
        text = text.rstrip() + "\n\n" + block.strip() + "\n"

    write(rel, text)


def hygiene_checks() -> None:
    print("\n===== HYGIENE =====")

    p = subprocess.run(
        ["grep", "-rn", "opposite_of", "data/", "schema/", "scripts/"],
        cwd=ROOT, text=True, capture_output=True
    )
    if p.returncode == 0:
        print(p.stdout, end="")
        fail("opposite_of remains under data/, schema/, or scripts/")
    if p.returncode != 1:
        fail("opposite_of grep failed")
    print("PASS: no opposite_of under data/, schema/, scripts/")

    p = subprocess.run(
        ["grep", "-rnE", r"(^|[^A-Za-z_])broader([^A-Za-z_]|$)",
         "data/", "schema/", "scripts/"],
        cwd=ROOT, text=True, capture_output=True
    )
    if p.returncode == 0:
        print(p.stdout, end="")
        fail("legacy broader remains under data/, schema/, or scripts/")
    if p.returncode != 1:
        fail("broader grep failed")
    print("PASS: no legacy broader under data/, schema/, scripts/")

    foundation = read("docs/PROJECT_FOUNDATION.md")
    for line in foundation.splitlines():
        if re.search(r"(?<!skos:)\bbroader\b", line):
            fail(f"unexpected non-SKOS broader in foundation: {line}")

    if "&#x20;" in foundation:
        fail("literal HTML-space entity remains in PROJECT_FOUNDATION.md")

    print("PASS: foundation broader usage limited to skos:broader")
    print("PASS: no literal &#x20; rendering artifact in foundation")


def verify_final() -> None:
    print("\n===== FINAL SELF TEST =====")
    a = run([sys.executable, "scripts/pilot_check.py", "--self-test"], True)
    print(a.stdout, end="")
    if a.stderr:
        print(a.stderr, end="", file=sys.stderr)

    required = (
        "PASS: unknown field tradition rejected",
        "PASS: year as string rejected",
        "PASS: boolean label from YAML typing rejected",
        "PASS: invalid locus artefact rejected",
        "PASS: missing vocabulary is a hard failure",
        "PASS: self-referencing is_a rejected",
        "PASS: cross-locus is_a rejected",
        "PASS: cross-locus part_of warned",
        "PASS: is_a/part_of pair collision rejected",
        "PASS: two-node is_a cycle rejected",
        "PASS: related/is_a overlap warned",
        "PASS: related/part_of overlap warned",
        "SELF-TEST RESULT: PASS",
    )
    missing = [s for s in required if s not in a.stdout]
    if a.returncode or missing:
        fail("self-test failed or missing expected cases: " + repr(missing))

    print("\n===== FINAL CORPUS =====")
    b = run([sys.executable, "scripts/pilot_check.py"], True)
    print(b.stdout, end="")
    if b.stderr:
        print(b.stderr, end="", file=sys.stderr)

    if (
        b.returncode
        or "40 record(s)" not in b.stdout
        or "22 concept(s)" not in b.stdout
        or "6 claim(s)" not in b.stdout
        or "12 source(s)" not in b.stdout
        or "RESULT: PASS (0 warning(s))" not in b.stdout
    ):
        fail("final corpus gate failed")

    print("\n===== DIFF CHECK =====")
    c = run(["git", "diff", "--check"], True)
    print(c.stdout, end="")
    if c.stderr:
        print(c.stderr, end="", file=sys.stderr)
    if c.returncode:
        fail("git diff --check failed")

    if count_records() != EXPECTED_COUNTS:
        fail(f"record counts changed: {count_records()}")

    hygiene_checks()

    print("\n===== DIFF STAT HEAD =====")
    subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

    print("\n===== STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\nRESULT: PRE-FREEZE-HARDENING-01 PASSED.")
    print("Foundation: rev. 8")
    print("Corpus: 40 records — 22 concepts, 6 claims, 12 sources")
    print("Canonical corpus warnings: 0")
    print("Self-test target: 12 cases PASS")
    print("No record/vocabulary additions.")
    print("No commit or push performed.")


def main() -> None:
    verify_preconditions()

    print("\n===== APPLY REV. 8 =====")
    patch_foundation()
    patch_plugin()
    patch_checker()
    patch_pilot_records()

    verify_final()


if __name__ == "__main__":
    main()
