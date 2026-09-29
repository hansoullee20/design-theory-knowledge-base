#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "fd06323986719c7b51c61ba64364bd3d08f0a484"

TEMPLATE = """# Registry Candidate Adjudication Template

- Batch item:
- Lexical candidate:
- Competency question / intended use:
- Candidate sense:
- Candidate canonical ID:
- Candidate definition:
- Proposed locus:
- Adjacent canonical records:
- Canonical-ID collision / reuse result:
- Polysemy test:
- Proposed source strategy:
- Exact-locator strategy:
- Claim required now?:
- Existing schema fit:
- Representation failure demonstrated?:
- Outcome:
- Next action:
"""

REPORT = """# REGISTRY-BATCH-03B — Deferred Fundamentals Adjudication

Baseline: §fd06323§
Mode: read-only adjudication
Canonical mutation authorized: NO
Candidates: form / color / balance / typography / feedback

## 03B-1 — form

- Lexical candidate: §form§
- Competency question / intended use: represent form as a fundamental visual/compositional concept without collapsing it into shape.
- Candidate sense: form as a compositional/formal property concerned with the organization/design of visual elements in a work.
- Candidate canonical ID: §concept:form-compositional§
- Proposed locus: §artifact§
- Adjacent canonical records: §concept:shape-visual§, §concept:space-compositional§, §concept:point-graphic§, §concept:line-graphic§, §concept:contrast-visual§.
- Canonical-ID collision / reuse result: no same-sense canonical record; §shape-visual§ is narrower and must not be reused as generic form.
- Polysemy test: bare §form§ is unsafe; the selected composition sense must be qualified.
- Proposed source strategy: Getty AAT 300056272, §form (composition concepts)§.
- Exact-locator strategy: AAT record 300056272, Note (English).
- Claim required now?: NO.
- Existing schema fit: YES — ordinary concept record; no new predicate/kind/locus required.
- Representation failure demonstrated?: NO.
- Outcome: §READY_TO_MINT§
- Next action: admit only the qualified compositional sense in a later bounded population batch.

## 03B-2 — color

- Lexical candidate: §color§
- Competency question / intended use: represent color as a design fundamental without conflating perceptual color with technical color-stimulus specification.
- Candidate senses:
  - perceived color — a characteristic of visual perception;
  - psychophysical color — operational specification of a color stimulus, e.g. tristimulus values.
- Candidate canonical IDs: not frozen in this adjudication; likely §concept:color-perceived§ for the first sense if demanded.
- Proposed locus:
  - perceived color → §experience§;
  - psychophysical color → requires separate locus/sense review before minting.
- Adjacent canonical records: §concept:hue-perceived§, §concept:saturation-perceived§, §concept:color-value-perceived§, §concept:contrast-visual§.
- Canonical-ID collision / reuse result: no generic color concept exists; existing records are attributes or a different visual relation.
- Polysemy test: FAILED for bare §color§; CIE explicitly distinguishes perceived and psychophysical meanings.
- Proposed source strategy: CIE S 017:2020 e-ILV term 17-22-040 for perceived colour and 17-23-001 for psychophysical colour.
- Exact-locator strategy: the CIE term numbers themselves.
- Claim required now?: NO.
- Existing schema fit: perceived-color sense fits; psychophysical-color locus/application should be adjudicated separately.
- Representation failure demonstrated?: NO.
- Outcome: §SPLIT_REQUIRED§
- Next action: do not mint §concept:color§; open a bounded color-sense sub-batch before canonical admission.

## 03B-3 — balance

- Lexical candidate: §balance§
- Competency question / intended use: represent perceived visual equilibrium in a composition.
- Candidate sense: impression of visual equilibrium in a composition.
- Candidate canonical ID: §concept:visual-balance-perceived§
- Proposed locus: §experience§
- Adjacent canonical records: §concept:space-compositional§, §concept:hierarchy-perceived§, §concept:perceived-density§, §concept:figure-ground-organization§.
- Canonical-ID collision / reuse result: no same-sense canonical record found.
- Polysemy test: bare §balance§ is broader than the intended visual-composition sense; use a qualified ID.
- Proposed source strategy: Getty AAT 300056247, §balance (composition concept)§.
- Exact-locator strategy: AAT record 300056247, Note (English).
- Claim required now?: NO.
- Existing schema fit: YES — experience-locus concept.
- Representation failure demonstrated?: NO.
- Outcome: §READY_TO_MINT§
- Next action: admit the qualified perceived-visual-balance sense in a later bounded population batch.

## 03B-4 — typography

- Lexical candidate: §typography§
- Competency question / intended use: represent typography as a design/production practice rather than as a bundle of type properties.
- Candidate sense: processes performed with type/typefaces, including setting type and arranging type in layouts.
- Candidate canonical ID: §concept:typography-practice§
- Proposed locus: §practice§
- Adjacent canonical records: §concept:body-text§, §concept:left-alignment§, §concept:print-size§, §concept:legibility-typeface§, §concept:visual-presentation-of-text§.
- Canonical-ID collision / reuse result: no practice-level typography concept exists; adjacent records describe artifacts or actor-relative outcomes.
- Polysemy test: typography can denote both practice and resulting typographic treatment; the selected practice sense must be qualified.
- Proposed source strategy: Getty AAT 300195853, §typography§.
- Exact-locator strategy: AAT record 300195853, Note (English).
- Claim required now?: NO.
- Existing schema fit: YES — practice-locus concept.
- Representation failure demonstrated?: NO.
- Outcome: §READY_TO_MINT§
- Next action: admit only the practice sense; keep artifact-side typographic treatment/properties separate.

## 03B-5 — feedback

- Lexical candidate: §feedback§
- Competency question / intended use: represent feedback in interaction design without conflating system response, status messages, sensory feedback, evaluative feedback, and design-process critique.
- Candidate senses under consideration:
  - interaction feedback following a user action;
  - system/status feedback communicating success, result, progress, waiting state, or errors;
  - sensory/state feedback;
  - evaluative/design-process feedback.
- Candidate canonical ID: not frozen.
- Proposed locus: depends on selected sense; system-produced feedback may be artifact-side while the user-relative information relation may require actor-relative treatment.
- Adjacent canonical records: §concept:signifier§, §concept:affordance-perceived§, §concept:visual-presentation-of-text§.
- Canonical-ID collision / reuse result: no generic feedback concept exists; adjacent concepts are not substitutes.
- Polysemy test: FAILED for bare §feedback§.
- Proposed source strategy: ISO 9241-110 interaction-principle framework plus W3C/WAI feedback/status-message guidance for concrete UI-feedback senses.
- Exact-locator strategy: defer until one interaction-feedback sense is frozen.
- Claim required now?: NO.
- Existing schema fit: likely YES for a bounded sense, but locus must be fixed first.
- Representation failure demonstrated?: NO.
- Outcome: §SPLIT_REQUIRED§
- Next action: open a bounded interaction-feedback sense adjudication; do not mint §concept:feedback§.

## Batch decision

- §READY_TO_MINT§: 3
  - §concept:form-compositional§
  - §concept:visual-balance-perceived§
  - §concept:typography-practice§
- §SPLIT_REQUIRED§: 2
  - color
  - feedback
- §REUSE_EXISTING§: 0
- §DEFER_EVIDENCE§: 0
- §REPRESENTATION_FAILURE§: 0
- §OUT_OF_SCOPE§: 0

Architecture verdict: §NO_REOPEN§
Canonical mutation in 03B: §0§

Recommended next population action:
§REGISTRY-BATCH-03C§ may mint only the three READY_TO_MINT senses after exact source-record and locator preparation. Color and feedback remain separate adjudication tasks.
""".replace("§", chr(96))

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

print("===== REGISTRY-BATCH-03B READ-ONLY ADJUDICATION =====")

if out("git", "branch", "--show-current") != "main":
    fail("repository is not on main")
if out("git", "status", "--porcelain"):
    fail("main is dirty")

subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO, check=True)

if out("git", "rev-parse", "HEAD") != out("git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out("git", "rev-parse", "HEAD") != BASE:
    fail("unexpected baseline: " + out("git", "rev-parse", "--short", "HEAD"))

concept_dir = REPO / "data/concepts"

required_existing = [
    "shape-visual.yaml",
    "space-compositional.yaml",
    "point-graphic.yaml",
    "line-graphic.yaml",
    "contrast-visual.yaml",
    "hue-perceived.yaml",
    "saturation-perceived.yaml",
    "color-value-perceived.yaml",
    "hierarchy-perceived.yaml",
    "perceived-density.yaml",
    "figure-ground-organization.yaml",
    "body-text.yaml",
    "left-alignment.yaml",
    "print-size.yaml",
    "legibility-typeface.yaml",
    "visual-presentation-of-text.yaml",
    "signifier.yaml",
    "affordance-perceived.yaml",
]

missing = [name for name in required_existing if not (concept_dir / name).exists()]
if missing:
    fail("expected adjacent canonical records missing: " + ", ".join(missing))

proposed_absent = [
    "form-compositional.yaml",
    "color.yaml",
    "color-perceived.yaml",
    "visual-balance-perceived.yaml",
    "typography-practice.yaml",
    "feedback.yaml",
    "interaction-feedback.yaml",
]
collisions = [name for name in proposed_absent if (concept_dir / name).exists()]
if collisions:
    fail("candidate collision detected: " + ", ".join(collisions))

before = out("git", "status", "--porcelain")

print()
print(TEMPLATE.rstrip())
print()
print(REPORT.rstrip())

after = out("git", "status", "--porcelain")
if before != after or after:
    fail("read-only adjudication mutated canonical main")

print()
print("===== ZERO-MUTATION GATE =====")
print(out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))
print("OUTCOME: REGISTRY_BATCH_03B_ADJUDICATION_PASS")
print("READY_TO_MINT: 3")
print("SPLIT_REQUIRED: 2")
print("REPRESENTATION_FAILURE: 0")
print("ARCHITECTURE: NO_REOPEN")
print("Canonical mutation: 0")
