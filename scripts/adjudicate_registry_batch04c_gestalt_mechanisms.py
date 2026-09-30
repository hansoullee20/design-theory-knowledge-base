#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "e6f2f3083b620e66f43c416e732aba6f74fa529f"

REPORT = """# REGISTRY-BATCH-04C — Gestalt Grouping Mechanism Adjudication

Baseline: §e6f2f30§
Mode: read-only adjudication
Canonical mutation authorized: NO

## Candidate 04C-1 — visual similarity → perceptual grouping

- New concept required: §concept:visual-similarity§
- Candidate sense: the degree to which visual elements are alike in perceptible features such as color, size, or orientation.
- Proposed locus: §artifact§
- Proposed knowledge origin: §perceptual-science§
- Proposed tradition: §gestalt§
- Proposed claim ID: §claim:visual-similarity-increases-perceptual-grouping§
- Subject: §concept:visual-similarity§
- Predicate: §increases§
- Object: §concept:perceptual-grouping§
- Modality: §descriptive§
- Proposed basis: §empirical§ and §theoretical§
- Proposed evidence status: §unassessed§
- Source strategy: reuse §source:wagemans-2012-gestalt-i§.
- Exact locator strategy: §3.1 Introduction§.
- Evidence fit: Wagemans et al. describe the general similarity principle: all else equal, more similar elements in color, size, or orientation tend to be grouped together.
- Scope: visual grouping of discrete elements; grouping strength can interact with competing grouping cues.
- Outcome: §READY_TO_MINT_WITH_NEW_CONCEPT§.

## Candidate 04C-2 — common region → perceptual grouping

- New concept required: §concept:common-region§
- Candidate sense: an arrangement in which visual elements lie within the same bounded region.
- Proposed locus: §artifact§
- Proposed knowledge origin: §perceptual-science§
- Proposed tradition: §gestalt§
- Proposed claim ID: §claim:common-region-influences-perceptual-grouping§
- Subject: §concept:common-region§
- Predicate: §influences§
- Object: §concept:perceptual-grouping§
- Modality: §descriptive§
- Proposed basis: §empirical§ and §theoretical§
- Proposed evidence status: §unassessed§
- Source strategy: reuse §source:wagemans-2012-gestalt-i§.
- Exact locator: §3.2.3 Common region§.
- Evidence fit: the review defines common region as the tendency for elements within the same bounded area to be grouped together and summarizes behavioral evidence using repetition-discrimination tasks.
- Scope: visual elements arranged inside bounded regions; the effect can interact with other grouping cues.
- Outcome: §READY_TO_MINT_WITH_NEW_CONCEPT§.

## Candidate 04C-3 — element connectedness → perceptual grouping

- New concept required: §concept:element-connectedness§
- Candidate sense: the visual connectedness of otherwise distinct elements through a shared border or explicit connection.
- Proposed locus: §artifact§
- Proposed knowledge origin: §perceptual-science§
- Proposed tradition: §gestalt§
- Proposed claim ID: §claim:element-connectedness-influences-perceptual-grouping§
- Subject: §concept:element-connectedness§
- Predicate: §influences§
- Object: §concept:perceptual-grouping§
- Modality: §descriptive§
- Proposed basis: §empirical§ and §theoretical§
- Proposed evidence status: §unassessed§
- Source strategy: reuse §source:wagemans-2012-gestalt-i§.
- Exact locator: §3.2.4 Element connectedness§.
- Evidence fit: the review defines element connectedness as a tendency for connected elements to group and summarizes behavioral and neuropsychological evidence.
- Scope: discrete visual elements connected by borders or explicit visual connections; grouping can interact with other cues.
- Outcome: §READY_TO_MINT_WITH_NEW_CONCEPT§.

## Batch 04C decision

- READY_TO_MINT_WITH_NEW_CONCEPT: 3 mechanisms
  - visual similarity → perceptual grouping
  - common region → perceptual grouping
  - element connectedness → perceptual grouping
- New concepts required: 3
- New claims required: 3
- New source records required: 0
- Existing source records reused: 1
- Representation failure: 0
- Architecture verdict: §NO_REOPEN§
- Canonical mutation: 0

Rationale:
Batch 04 remains mechanism-first. These concepts are introduced only because each selected mechanism requires an artifact-side endpoint that is not currently represented. They are not standalone glossary expansion.

Recommended next action:
§REGISTRY-BATCH-04D§ may prepare a bounded trial containing exactly 3 concepts + 3 claims, reusing §source:wagemans-2012-gestalt-i§ and adding no source, schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
""".replace("§", chr(96))

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

print("===== REGISTRY-BATCH-04C READ-ONLY ADJUDICATION =====")

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
    "data/concepts/perceptual-grouping.yaml",
    "data/concepts/proximity.yaml",
    "data/sources/wagemans-2012-gestalt-i.yaml",
    "data/claims/proximity-increases-perceptual-grouping.yaml",
]
for rel in required:
    if not (REPO / rel).exists():
        fail("required canonical record missing: " + rel)

candidate_paths = [
    "data/concepts/visual-similarity.yaml",
    "data/concepts/common-region.yaml",
    "data/concepts/element-connectedness.yaml",
    "data/claims/visual-similarity-increases-perceptual-grouping.yaml",
    "data/claims/common-region-influences-perceptual-grouping.yaml",
    "data/claims/element-connectedness-influences-perceptual-grouping.yaml",
]
collisions = [rel for rel in candidate_paths if (REPO / rel).exists()]
if collisions:
    fail("candidate path collision detected: " + ", ".join(collisions))

existing_ids = set()
for directory in ("data/concepts", "data/claims", "data/sources"):
    for p in (REPO / directory).glob("*.yaml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            existing_ids.add(d["id"])

candidate_ids = [
    "concept:visual-similarity",
    "concept:common-region",
    "concept:element-connectedness",
    "claim:visual-similarity-increases-perceptual-grouping",
    "claim:common-region-influences-perceptual-grouping",
    "claim:element-connectedness-influences-perceptual-grouping",
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
print("OUTCOME: REGISTRY_BATCH_04C_ADJUDICATION_PASS")
print("READY_TO_MINT_WITH_NEW_CONCEPT: 3")
print("NEW_CONCEPTS_REQUIRED: 3")
print("NEW_CLAIMS_REQUIRED: 3")
print("NEW_SOURCES_REQUIRED: 0")
print("REPRESENTATION_FAILURE: 0")
print("ARCHITECTURE: NO_REOPEN")
print("Canonical mutation: 0")
