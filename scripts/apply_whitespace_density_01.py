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

BASELINE = (50, 27, 8, 15)
EXPECTED = (54, 28, 9, 17)

IXDF_ID = "source:soegaard-2020-white-space"
FORGE_ID = "source:tyler-forge-grid"


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write_new(rel: str, text: str) -> None:
    p = ROOT / rel
    if p.exists():
        fail(f"refusing to overwrite existing file: {rel}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"CREATED: {rel}")


def update(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


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


def source_from_template(record_id: str, citation: str, year: int, notes: str):
    candidates = [
        ROOT / "data/sources/w3c-wcag-2-2.yaml",
        ROOT / "data/sources/lupton-2010-thinking-with-type.yaml",
    ]
    template = next((p for p in candidates if p.exists()), None)
    if template is None:
        existing = sorted((ROOT / "data/sources").glob("*.yaml"))
        if not existing:
            fail("no source template available")
        template = existing[0]

    data = copy.deepcopy(yaml.safe_load(template.read_text(encoding="utf-8")))
    data["id"] = record_id
    data["kind"] = "source"
    data["citation"] = citation
    data["source_type"] = "web"
    data["year"] = year
    data["notes"] = notes

    # Do not inherit source-specific optional identifiers/URLs from template.
    for field in ("identifier", "url"):
        if field in data:
            data[field] = ""

    return data


def concept_from_template(record_id: str, label: str, definition: str):
    candidates = [
        ROOT / "data/concepts/left-alignment.yaml",
        ROOT / "data/concepts/hierarchy-specified.yaml",
    ]
    template = next((p for p in candidates if p.exists()), None)
    if template is None:
        existing = sorted((ROOT / "data/concepts").glob("*.yaml"))
        if not existing:
            fail("no concept template available")
        template = existing[0]

    data = copy.deepcopy(yaml.safe_load(template.read_text(encoding="utf-8")))
    data["id"] = record_id
    data["kind"] = "concept"
    data["label"] = label
    if "aliases" in data:
        data["aliases"] = ["negative space", "white space"]
    data["definition"] = definition
    data["definition_sources"] = [IXDF_ID]
    data["locus"] = ["artifact"]

    if "facets" in data:
        data["facets"] = ["layout"]
    if "disciplines" in data:
        data["disciplines"] = ["interface-interaction-design"]
    if "knowledge_origin" in data:
        data["knowledge_origin"] = ["design-practice"]
    if "traditions" in data:
        data["traditions"] = []

    data["is_a"] = []
    data["part_of"] = []
    data["related"] = ["concept:perceived-density"]

    if "record_status" in data:
        data["record_status"] = "draft"
    if "replaced_by" in data:
        data["replaced_by"] = []
    if "notes" in data:
        data["notes"] = (
            "Whitespace is represented as an artifact-borne spatial property. "
            "Micro/macro subtypes are not introduced in v0.1."
        )

    return data


print("===== PRECONDITIONS =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != "main":
    fail(f"expected main, got {branch!r}")

if "(rev. 10)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("expected Foundation rev. 10")

if counts() != BASELINE:
    fail(f"expected baseline {BASELINE}, got {counts()}")

for rel in (
    "data/sources/soegaard-2020-white-space.yaml",
    "data/sources/tyler-forge-grid.yaml",
    "data/concepts/whitespace.yaml",
    "data/claims/whitespace-decreases-perceived-density.yaml",
):
    if (ROOT / rel).exists():
        fail(f"pilot target already exists: {rel}")

if "## WHITESPACE-DENSITY-01" in read("pilot/PILOT_RECORDS.md"):
    fail("WHITESPACE-DENSITY-01 already logged")

schema = yaml.safe_load(read("schema/claim.schema.yaml"))
predicates = schema["properties"]["predicate"]["enum"]
if "decreases" not in predicates:
    fail("decreases predicate unavailable")

if "concept:perceived-density" not in read("data/concepts/perceived-density.yaml"):
    fail("perceived-density concept prerequisite mismatch")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")

existing_claims = sorted((ROOT / "data/claims").glob("*.yaml"))
claim_hashes = {p: digest(p) for p in existing_claims}

print("PRECONDITIONS: PASS")

print("\n===== SOURCES =====")

ixdf = source_from_template(
    IXDF_ID,
    (
        "Soegaard, Mads. The Power of White Space in Design. "
        "Interaction Design Foundation (IxDF), 10 September 2020."
    ),
    2020,
    (
        "Design-practice source defining white space as the area between and within "
        "design elements and explaining that it can keep pages from looking busy. "
        "Used for the whitespace concept definition and contextual support; not "
        "treated as empirical effect-size evidence."
    ),
)

forge = source_from_template(
    FORGE_ID,
    (
        "Tyler Technologies. Forge Design System, Grid pattern. "
        "Undated live web documentation; accessed 27 September 2026."
    ),
    2026,
    (
        "Design-system guidance explicitly states that white space can lower the "
        "perceived density of content. The page is undated; year 2026 records the "
        "access year under the current v0.1 source metadata limitation. Exact locator "
        "and access-date machinery remain deferred under PF-001."
    ),
)

write_new("data/sources/soegaard-2020-white-space.yaml", dump(ixdf))
write_new("data/sources/tyler-forge-grid.yaml", dump(forge))

print("\n===== WHITESPACE CONCEPT =====")

whitespace = concept_from_template(
    "concept:whitespace",
    "Whitespace",
    (
        "The unmarked area between and within visual design elements; despite the "
        "name, it need not be white."
    ),
)
write_new("data/concepts/whitespace.yaml", dump(whitespace))

print("\n===== DIRECTIONAL CLAIM =====")

claim = {
    "id": "claim:whitespace-decreases-perceived-density",
    "kind": "claim",
    "statement": (
        "Increasing whitespace can decrease the perceived density of content in "
        "a visual layout."
    ),
    "modality": "descriptive",
    "subject": "concept:whitespace",
    "predicate": "decreases",
    "object": "concept:perceived-density",
    "basis": ["expert-opinion"],
    "evidence_status": "unassessed",
    "scope": (
        "Design-practice guidance for visual/interface layouts. The direct source "
        "support is professional design-system guidance that whitespace can lower "
        "perceived content density; this claim is not classified as an empirical law, "
        "does not assert a universal monotonic effect, and carries no effect-size claim. "
        "Context, magnitude, and boundary conditions remain unassessed."
    ),
    "sources": [IXDF_ID, FORGE_ID],
    "record_status": "draft",
    "replaced_by": [],
    "notes": (
        "WHITESPACE-DENSITY-01 tests the existing decreases predicate against the "
        "perceived-density sense. It deliberately does not target display-object-density, "
        "whose definition is an objective count per unit/area and is not automatically "
        "the inverse of whitespace."
    ),
    "schema_version": "0.1",
}

write_new("data/claims/whitespace-decreases-perceived-density.yaml", dump(claim))

print("\n===== PILOT RECORD =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)

block = '''
## WHITESPACE-DENSITY-01

- [x] Tested the required `whitespace and density (sense-dependent relation)` case.
- [x] Minted `concept:whitespace` with `locus: [artifact]`.
- [x] Reused the existing `concept:perceived-density` experience-locus sense.
- [x] Deliberately did **not** target `concept:display-object-density`; objective object-count density is not automatically the inverse of whitespace.
- [x] Added `source:soegaard-2020-white-space` for the whitespace definition/context.
- [x] Added `source:tyler-forge-grid` for the explicit design-practice statement that whitespace can lower perceived content density.
- [x] Minted `claim:whitespace-decreases-perceived-density` using the existing `decreases` predicate.
- [x] Claim uses `modality: descriptive` and `basis: [expert-opinion]`; it is not classified as empirical evidence or a universal rule.
- [x] No schema, predicate, locus, or runtime-contract change was required.
- [x] Foundation remains rev. 10.
- [x] Outcome: `PASS_WITH_QUALIFICATION`.
'''.replace("`", chr(96))

update(rel, text.rstrip() + "\n\n" + block.strip() + "\n")

print("\n===== VALIDATION =====")

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-test failed")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker not clean")

run("git", "diff", "--check")

if counts() != EXPECTED:
    fail(f"expected post-pilot corpus {EXPECTED}, got {counts()}")

print("\n===== EXISTING CLAIM IMMUTABILITY =====")
for path, before in claim_hashes.items():
    if digest(path) != before:
        fail(f"existing canonical claim changed: {path.relative_to(ROOT)}")
    print("PASS:", path.relative_to(ROOT))

loaded = yaml.safe_load(read("data/claims/whitespace-decreases-perceived-density.yaml"))
if loaded.get("predicate") != "decreases":
    fail("whitespace claim predicate mismatch")
if loaded.get("object") != "concept:perceived-density":
    fail("whitespace claim targets wrong density sense")
if loaded.get("basis") != ["expert-opinion"]:
    fail("whitespace claim basis mismatch")

if "(rev. 10)" not in read("docs/PROJECT_FOUNDATION.md"):
    fail("Foundation changed away from rev. 10")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT HEAD =====")
subprocess.run(["git", "diff", "--stat", "HEAD"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: PASS_WITH_QUALIFICATION")
print("PILOT: WHITESPACE-DENSITY-01")
print("Foundation: rev. 10")
print("CONCEPT: concept:whitespace")
print("TARGET SENSE: concept:perceived-density")
print("CLAIM: claim:whitespace-decreases-perceived-density")
print("predicate: decreases")
print("modality: descriptive")
print("basis: expert-opinion")
print("empirical-law status: NOT CLAIMED")
print("display-object-density inverse: NOT CLAIMED")
print("COUNTS: 54 records — 28 concepts, 9 claims, 17 sources")
print("Existing canonical claims: unchanged")
print("No schema or runtime-contract change.")
print("No commit or push performed.")
