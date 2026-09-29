#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "af3d86b55e5edaac5c7c8cecaf74409b1a1b524a"

REPORT = """# REGISTRY-BATCH-03D/03E — Color and Feedback Sense Adjudication

Baseline: §af3d86b§
Mode: read-only adjudication
Canonical mutation authorized: NO

## REGISTRY-BATCH-03D — COLOR SENSES

### 03D-1 — perceived color

- Lexical candidate: §color§
- Candidate sense: perceived color as a characteristic of visual perception.
- Candidate canonical ID: §concept:color-perceived§
- Candidate definition: A characteristic of visual perception describable by attributes including hue, brightness or lightness, and colourfulness, saturation, or chroma.
- Proposed locus: §experience§
- Adjacent canonical records:
  - §concept:hue-perceived§
  - §concept:saturation-perceived§
  - §concept:color-value-perceived§
  - §concept:contrast-visual§
- Reuse/collision result: no same-sense generic perceived-color concept exists.
- Polysemy result: bare §concept:color§ remains prohibited because CIE distinguishes perceptual and psychophysical senses.
- Proposed source: reuse §source:cie-s017-2020-ilv§.
- Exact locator: CIE e-ILV term §17-22-040§.
- Claim required now?: NO.
- Existing schema fit: YES.
- Representation failure demonstrated?: NO.
- Outcome: §READY_TO_MINT§.

### 03D-2 — psychophysical color

- Candidate sense: specification of a color stimulus in operationally defined values such as tristimulus values.
- Candidate canonical ID: §concept:color-psychophysical§ (candidate only; not frozen).
- Proposed source: reuse §source:cie-s017-2020-ilv§.
- Exact locator: CIE e-ILV term §17-23-001§.
- Current need: no active competency question presently requires a separately addressable psychophysical-color entity.
- Locus issue: the sense is a technical stimulus specification and should not be forced into §artifact§ merely to make it fit.
- Existing schema fit: not yet adjudicated strongly enough to mint.
- Representation failure demonstrated?: NO — lack of current need/locus adjudication is not a demonstrated schema failure.
- Outcome: §DEFER_SCOPE_AND_LOCUS§.
- Next action: revisit only when a competency question requires technical color-stimulus specification.

### 03D decision

- §READY_TO_MINT§: §concept:color-perceived§
- §DEFER_SCOPE_AND_LOCUS§: psychophysical-color sense
- Bare §concept:color§: DO NOT MINT
- Architecture verdict: §NO_REOPEN§

## REGISTRY-BATCH-03E — FEEDBACK SENSES

### 03E-1 — interaction feedback

- Lexical candidate: §feedback§
- Candidate sense: feedback presented by an interactive system in response to a user-initiated action, indicating success, failure, result, or changed state.
- Candidate canonical ID: §concept:interaction-feedback§
- Proposed locus: §artifact§
- Rationale for locus: the canonical sense is the response/state information implemented by the interactive artifact, not the user's subjective experience of receiving it.
- Adjacent canonical records:
  - §concept:signifier§
  - §concept:affordance-perceived§
  - §concept:visual-presentation-of-text§
- Reuse/collision result: no same-sense feedback concept exists; signifiers and affordances are not substitutes for post-action response.
- Polysemy result: bare §concept:feedback§ remains prohibited.
- Proposed source strategy:
  - W3C WAI Cognitive Accessibility Design Pattern, §Provide Feedback§, for the broad interaction-feedback sense.
  - WCAG status-message material remains a narrower subtype/example, not the definition of all feedback.
- Exact-locator strategy: W3C §Provide Feedback§ section §More Details§; status-message material may be linked later only for a narrower status-message concept or claim.
- Claim required now?: NO.
- Existing schema fit: YES as an artifact-locus concept.
- Representation failure demonstrated?: NO.
- Outcome: §READY_TO_MINT§.

### 03E-2 — status-message feedback

- Candidate sense: a change in content that communicates success/results, waiting state, progress, or errors without changing context.
- Candidate canonical ID: §concept:status-message§ (future candidate).
- Proposed source: W3C WCAG Understanding 4.1.3 Status Messages.
- Current need: narrower subtype is useful but not required to admit the broader interaction-feedback concept.
- Outcome: §DEFER_SUBTYPE§.

### 03E-3 — evaluative/design-process feedback

- Candidate sense: critique or evaluative information exchanged during a design process.
- Proposed locus: likely §practice§, but this is distinct from interaction feedback.
- Current need: no active competency question requires it.
- Outcome: §DEFER_SCOPE§.

### 03E decision

- §READY_TO_MINT§: §concept:interaction-feedback§
- §DEFER_SUBTYPE§: §concept:status-message§
- §DEFER_SCOPE§: evaluative/design-process feedback
- Bare §concept:feedback§: DO NOT MINT
- Architecture verdict: §NO_REOPEN§

## Combined decision

- READY_TO_MINT: 2
  - §concept:color-perceived§
  - §concept:interaction-feedback§
- DEFERRED SENSES: 3
  - psychophysical color
  - status-message feedback
  - evaluative/design-process feedback
- REPRESENTATION_FAILURE: 0
- Architecture: §NO_REOPEN§
- Canonical mutation: 0

Recommended next action:
§REGISTRY-BATCH-03F§ may prepare a bounded minting trial for only §concept:color-perceived§ and §concept:interaction-feedback§, with exact source records/locators and no claims.
""".replace("§", chr(96))

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

print("===== REGISTRY-BATCH-03D/03E READ-ONLY ADJUDICATION =====")

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
    "data/concepts/hue-perceived.yaml",
    "data/concepts/saturation-perceived.yaml",
    "data/concepts/color-value-perceived.yaml",
    "data/concepts/contrast-visual.yaml",
    "data/concepts/signifier.yaml",
    "data/concepts/affordance-perceived.yaml",
    "data/concepts/visual-presentation-of-text.yaml",
    "data/sources/cie-s017-2020-ilv.yaml",
    "data/sources/w3c-wcag-2-2.yaml",
]

for rel in required:
    if not (REPO / rel).exists():
        fail("required canonical record missing: " + rel)

candidate_paths = [
    "data/concepts/color.yaml",
    "data/concepts/color-perceived.yaml",
    "data/concepts/color-psychophysical.yaml",
    "data/concepts/feedback.yaml",
    "data/concepts/interaction-feedback.yaml",
    "data/concepts/status-message.yaml",
]

collisions = [rel for rel in candidate_paths if (REPO / rel).exists()]
if collisions:
    fail("candidate collision detected: " + ", ".join(collisions))

before = out("git", "status", "--porcelain")

print()
print(REPORT.rstrip())

after = out("git", "status", "--porcelain")
if before != after or after:
    fail("read-only adjudication mutated canonical main")

print()
print("===== ZERO-MUTATION GATE =====")
print(out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))
print("OUTCOME: REGISTRY_BATCH_03D_03E_ADJUDICATION_PASS")
print("READY_TO_MINT: 2")
print("DEFERRED_SENSES: 3")
print("REPRESENTATION_FAILURE: 0")
print("ARCHITECTURE: NO_REOPEN")
print("Canonical mutation: 0")
