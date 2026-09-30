#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "db2c2d4c64b6c7ad4ee8107d57459cd45b7b9153"

REPORT = """# REGISTRY-BATCH-04A — Mechanism Candidate Adjudication

Baseline: §db2c2d4§
Mode: read-only adjudication
Canonical mutation authorized: NO

## Candidate 04A-1 — visual contrast → perceived hierarchy

- Proposed claim ID: §claim:contrast-visual-influences-perceived-hierarchy§
- Subject: §concept:contrast-visual§
- Predicate: §influences§
- Object: §concept:hierarchy-perceived§
- Modality: §descriptive§
- Proposed basis: §expert-opinion§
- Proposed evidence status: §unassessed§
- Source strategy: add §source:nng-2021-visual-hierarchy-ux§.
- Exact locator: section §1. Color and contrast§.
- Evidence fit: direct design-practice guidance states that color/contrast can create visual hierarchy and that contrast in value/saturation affects what draws attention.
- Scope: 2D interface/graphic layouts where visual contrast is intentionally used to differentiate importance.
- Outcome: §READY_TO_MINT§.

## Candidate 04A-2 — typography practice → perceived hierarchy

- Proposed claim ID: §claim:typography-practice-influences-perceived-hierarchy§
- Subject: §concept:typography-practice§
- Predicate: §influences§
- Object: §concept:hierarchy-perceived§
- Modality: §descriptive§
- Proposed basis: §expert-opinion§
- Proposed evidence status: §unassessed§
- Source strategy: reuse §source:nng-2025-good-visual-design§.
- Exact locator: section §Visual Principle: Use of a Typographic System§.
- Evidence fit: the source describes type-size/style choices as establishing a visual hierarchy.
- Scope: typographic choices such as relative size and weight in 2D layouts; not a universal effect of every typography practice.
- Outcome: §READY_TO_MINT§.

## Candidate 04A-3 — linguistic readability → reading speed

- Proposed claim ID: §claim:readability-linguistic-influences-reading-speed§
- Subject: §concept:readability-linguistic§
- Predicate: §influences§
- Object: §concept:reading-speed§
- Modality: §descriptive§
- Proposed basis: §empirical§
- Proposed evidence status: §unassessed§
- Source strategy: reuse §source:dubay-2004-principles-of-readability§.
- Exact locator: section §Reading Performance§.
- Evidence fit: DuBay reviews empirical work on readability effects on reading efficiency/speed and reports easier text improving reading efficiency under studied conditions.
- Scope: specified reader populations and reading tasks; effects depend on reader ability, prior knowledge, interest, motivation, and other text variables.
- Outcome: §READY_TO_MINT§.

## Candidate 04A-4 — typeface legibility → reading speed

- Candidate claim: §concept:legibility-typeface influences concept:reading-speed§.
- Source strategy considered: §source:beier-2012-reading-letters§.
- Evidence issue: Beier explicitly cautions that faster reading should not automatically be equated with higher legibility; highly legible text may reduce effort without increasing reading speed, and font effects on speed can be nonsignificant.
- Semantic issue: the current §legibility-typeface§ concept is a reader-relative disposition, while many studies manipulate typeface features and measure speed as a separate outcome.
- Outcome: §DEFER_EVIDENCE_AND_DIRECTION§.
- Next action: require a source that directly operationalizes the relationship between the canonical legibility construct and reading speed before minting.

## Candidate 04A-5 — perceived saturation → figure-ground organization

- Candidate claim: §concept:saturation-perceived influences concept:figure-ground-organization§.
- Source strategy considered: Dresp-Langley & Reeves (2014), Effects of saturation and contrast polarity on the figure-ground organization of color on gray.
- Evidence fit at phenomenon level: strong empirical evidence that manipulated saturation levels affect figure-ground judgments.
- Endpoint issue: the experiment operationalizes saturation as a controlled stimulus/colorimetric variable, whereas §concept:saturation-perceived§ explicitly denotes a perceived attribute and excludes numerical color-space coordinates.
- Outcome: §DEFER_ENDPOINT_SENSE_MISMATCH§.
- Next action: do not force the claim onto §saturation-perceived§; revisit only if a psychophysical/stimulus-side color-saturation concept is independently justified.

## Batch 04A decision

- READY_TO_MINT: 3
  - §claim:contrast-visual-influences-perceived-hierarchy§
  - §claim:typography-practice-influences-perceived-hierarchy§
  - §claim:readability-linguistic-influences-reading-speed§
- DEFER_EVIDENCE_AND_DIRECTION: 1
  - typeface legibility → reading speed
- DEFER_ENDPOINT_SENSE_MISMATCH: 1
  - perceived saturation → figure-ground organization
- New concepts required now: 0
- New source records required now: 1
- Existing source records reused: 2
- Representation failure: 0
- Architecture verdict: §NO_REOPEN§
- Canonical mutation: 0

Recommended next action:
§REGISTRY-BATCH-04B§ may prepare a bounded trial for the three READY_TO_MINT claims plus the single new NN/g source record. The two deferred candidates remain noncanonical.
""".replace("§", chr(96))

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

print("===== REGISTRY-BATCH-04A READ-ONLY ADJUDICATION =====")

if out("git", "branch", "--show-current") != "main":
    fail("repository is not on main")
if out("git", "status", "--porcelain"):
    fail("main is dirty")

subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO, check=True)

if out("git", "rev-parse", "HEAD") != out("git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out("git", "rev-parse", "HEAD") != BASE:
    fail("unexpected baseline: " + out("git", "rev-parse", "--short", "HEAD"))

required = [
    "data/concepts/contrast-visual.yaml",
    "data/concepts/hierarchy-perceived.yaml",
    "data/concepts/typography-practice.yaml",
    "data/concepts/readability-linguistic.yaml",
    "data/concepts/reading-speed.yaml",
    "data/concepts/legibility-typeface.yaml",
    "data/concepts/saturation-perceived.yaml",
    "data/concepts/figure-ground-organization.yaml",
    "data/sources/nng-2025-good-visual-design.yaml",
    "data/sources/dubay-2004-principles-of-readability.yaml",
    "data/sources/beier-2012-reading-letters.yaml",
]

for rel in required:
    if not (REPO / rel).exists():
        fail("required canonical record missing: " + rel)

candidate_claim_paths = [
    "data/claims/contrast-visual-influences-perceived-hierarchy.yaml",
    "data/claims/typography-practice-influences-perceived-hierarchy.yaml",
    "data/claims/readability-linguistic-influences-reading-speed.yaml",
]
candidate_source_path = "data/sources/nng-2021-visual-hierarchy-ux.yaml"

collisions = [
    rel for rel in candidate_claim_paths + [candidate_source_path]
    if (REPO / rel).exists()
]
if collisions:
    fail("candidate path collision detected: " + ", ".join(collisions))

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (REPO / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

candidate_ids = [
    "claim:contrast-visual-influences-perceived-hierarchy",
    "claim:typography-practice-influences-perceived-hierarchy",
    "claim:readability-linguistic-influences-reading-speed",
    "source:nng-2021-visual-hierarchy-ux",
]

dupes = [x for x in candidate_ids if x in existing_ids]
if dupes:
    fail("candidate ID collision detected: " + ", ".join(dupes))

before = out("git", "status", "--porcelain")

print()
print(REPORT.rstrip())

after = out("git", "status", "--porcelain")
if before != after or after:
    fail("read-only adjudication mutated canonical main")

print()
print("===== ZERO-MUTATION GATE =====")
print(out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))
print("OUTCOME: REGISTRY_BATCH_04A_ADJUDICATION_PASS")
print("READY_TO_MINT: 3")
print("DEFERRED: 2")
print("NEW_CONCEPTS_REQUIRED: 0")
print("NEW_SOURCES_REQUIRED: 1")
print("REPRESENTATION_FAILURE: 0")
print("ARCHITECTURE: NO_REOPEN")
print("Canonical mutation: 0")
