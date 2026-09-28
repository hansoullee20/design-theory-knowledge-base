#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BRANCH = "registry-protocol-01"
BASE_COMMIT = "43b4817f7646958cb90b8c2382921a00430bdd45"
DOC_REL = "docs/REGISTRY_POPULATION_PROTOCOL.md"
PILOT_REL = "pilot/PILOT_RECORDS.md"

PROTOCOL = r"""# Registry Population Protocol

## Status

Operational governance protocol for post-Taxonomy-v0.1 population of the Design Theory canonical knowledge registry.

This protocol governs how candidate knowledge is admitted to the canonical corpus. It does not alter Taxonomy v0.1 semantics.

## Purpose

Registry population must grow the canonical knowledge corpus without allowing routine ingestion to become uncontrolled ontology or schema redesign.

The default rule is:

> Populate the frozen model first. Reopen architecture only when a genuine representation failure has been demonstrated.

## Canonical population cycle

Every bounded population batch follows this sequence:

1. candidate intake;
2. sense adjudication;
3. canonical-ID collision check;
4. source adjudication;
5. provenance and exact-locator capture where support permits;
6. bounded canonical mutation;
7. deterministic validation;
8. semantic review;
9. checkpoint commit;
10. controlled integration into main.

## 1. Candidate intake

A candidate may originate from:

- an explicit registry backlog;
- a competency question;
- a design-theory source;
- a missing concept exposed by an existing claim;
- a bounded population batch approved for execution.

Candidate terms are not canonical merely because they occur in a checklist, source, user query, or design vocabulary.

## 2. Sense adjudication

Canonical identifiers identify senses, not words.

Before minting a concept, determine whether the candidate lexical form has materially different meanings across:

- artifact properties;
- actor properties;
- actor-relative relations;
- perceptual or cognitive experience;
- outcomes;
- practices;
- mathematical or technical representations;
- domain-specific conventions.

If materially different senses exist, use sense-qualified identifiers rather than forcing them into one record.

Examples established by Registry Batch 01 include:

- `concept:point-graphic`;
- `concept:line-graphic`;
- `concept:contrast-visual`;
- `concept:hue-perceived`;
- `concept:saturation-perceived`;
- `concept:color-value-perceived`.

## 3. Canonical-ID collision check

Before mutation:

- verify that the intended ID does not already exist;
- search for semantically adjacent concepts;
- prefer reuse when the existing record represents the same sense;
- do not mint duplicate source or concept identities.

Lexical difference does not prove semantic difference, and lexical identity does not prove semantic identity.

## 4. Source adjudication

Every canonical concept definition and claim must remain source-backed under the applicable schema.

Source selection must distinguish among:

- empirical evidence;
- standards;
- perceptual or cognitive science;
- authoritative terminology;
- design practice;
- art/craft traditions;
- conventional guidance.

A source must not be assigned a stronger evidential role than it supports.

## 5. Provenance and locators

Where an exact supporting location is available, population should use the post-PF-001 relation-level locator mechanism.

The canonical pattern is:

- source identity remains in `definition_sources` or `sources`;
- exact support location belongs in `definition_source_locators` or `source_locators`.

The locator belongs to the source-to-knowledge relation, not globally to the source record.

Missing locators remain valid where exact localization is unavailable, but their absence must not be disguised by fabricated precision.

## 6. Bounded mutation

Every automated or scripted population action must define its expected mutation surface before execution.

Unexpected file changes stop the batch.

Routine population must not modify, unless separately authorized:

- schemas;
- controlled vocabularies;
- predicates;
- locus definitions;
- runtime contracts;
- Foundation architecture.

New claims or structural relations must also be explicitly within the authorized batch scope rather than introduced incidentally.

## 7. Deterministic validation

Before and after mutation, run:

```bash
python3 scripts/pilot_check.py --self-test
python3 scripts/pilot_check.py
git diff --check
```

The expected normal acceptance state is:

- permanent self-tests PASS;
- canonical checker PASS;
- zero warnings unless a warning is explicitly adjudicated;
- `git diff --check` clean;
- expected corpus counts confirmed.

## 8. Semantic review

Schema validity is necessary but not sufficient.

Review must independently check:

- definition meaning;
- locus assignment;
- sense boundaries;
- source fit;
- locator correctness;
- structural relation semantics;
- distinction from adjacent canonical concepts;
- unintended epistemic inflation.

The checker does not infer whether a semantically plausible-looking record is actually correct.

## 9. Defer instead of force

An individual item may be deferred when its sense, evidence, or representation is unresolved.

Deferral of one item must not force unrelated items to stop.

Registry Batch 01 demonstrated this by separating visual/form fundamentals from the later hue/value/saturation sense adjudication.

## 10. Representation failure escalation

A new schema, predicate, record kind, vocabulary value, or runtime contract must not be introduced merely to make an awkward candidate fit.

When the existing canonical model cannot faithfully represent required knowledge:

1. stop the affected item;
2. record the representation failure;
3. identify the competency question that cannot be satisfied;
4. perform a bounded architecture review;
5. modify architecture only after the failure is demonstrated.

The prohibited pattern is:

candidate -> ad-hoc schema change.

The required pattern is:

candidate -> demonstrated failure -> bounded architecture review.

## 11. Checkpoint discipline

A successful population mutation is checkpointed on its working branch before integration.

A checkpoint requires:

- exact mutation-boundary review;
- canonical checker PASS;
- permanent self-tests PASS;
- clean diff check;
- expected corpus counts;
- clean working tree after commit;
- remote branch synchronization.

## 12. Controlled integration

Population branches are integrated into `main` only after checkpoint review.

Fast-forward integration is preferred when the branch is a direct continuation of the accepted canonical state.

After integration, validation is rerun before pushing `main`.

## 13. Canon versus tooling

Scripts, helpers, search indexes, embeddings, MCP interfaces, generated Skills, dashboards, and other consumers are not canonical knowledge merely because they operate on the registry.

The authority boundary remains:

canonical YAML records + schemas + controlled vocabularies + Git history

versus

derived or operational tooling.

## 14. Batch-01 proof case

Registry Batch 01 established the first complete application of this protocol.

Batch 01A admitted:

- `concept:point-graphic`;
- `concept:line-graphic`;
- `concept:contrast-visual`.

Batch 01B admitted:

- `concept:hue-perceived`;
- `concept:saturation-perceived`;
- `concept:color-value-perceived`.

The combined batch increased the corpus from:

- 54 records at Taxonomy-v0.1 freeze;
- 60 records after Batch 01A;
- 65 records after Batch 01B.

Current post-Batch-01 composition:

- 34 concepts;
- 9 claims;
- 22 sources.

No Batch-01 population step required a schema, predicate, vocabulary, locus, runtime-contract, or Foundation change.

## 15. Governing principle

The registry should become larger without becoming less trustworthy.

Growth is successful only when semantic identity, provenance, validation, authority boundaries, and recoverability remain intact.
"""

CLOSEOUT = r"""
## REGISTRY-BATCH-01-CLOSEOUT

- [x] REGISTRY-BATCH-01A integrated into main at commit `8f43a91`.
- [x] REGISTRY-BATCH-01B integrated into main at commit `43b4817`.
- [x] Six initial visual/color fundamentals resolved into six sense-qualified canonical concepts.
- [x] Bare lexical IDs were avoided where semantic ambiguity required qualification.
- [x] Exact source locators were used through the PF-001 relation-level provenance mechanism.
- [x] Batch growth required no schema, predicate, vocabulary, locus, runtime-contract, or Foundation change.
- [x] Canonical corpus after Batch 01: 65 records — 34 concepts, 9 claims, 22 sources.
- [x] Permanent self-tests: 36 PASS.
- [x] Canonical checker: PASS with 0 warnings.
- [x] Registry population workflow consolidated into `docs/REGISTRY_POPULATION_PROTOCOL.md`.
- [x] Outcome: `REGISTRY_POPULATION_MODEL_PROVEN`.
""".strip()


def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)


def run(*args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout


print("===== REGISTRY-PROTOCOL-01 =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip()
if branch != BRANCH:
    fail(f"expected branch {BRANCH}, got {branch}")

if subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=ROOT, text=True
).strip():
    fail("working tree must be clean")

head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
).strip()
if head != BASE_COMMIT:
    fail(f"expected HEAD {BASE_COMMIT}, got {head}")

doc = ROOT / DOC_REL
if doc.exists():
    fail(f"{DOC_REL} already exists")

pilot = ROOT / PILOT_REL
pilot_text = pilot.read_text(encoding="utf-8")
if "## REGISTRY-BATCH-01-CLOSEOUT" in pilot_text:
    fail("Batch-01 closeout already exists")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")
run("git", "diff", "--check")
print("PRECONDITIONS: PASS")

doc.write_text(PROTOCOL.rstrip() + "\n", encoding="utf-8")
pilot.write_text(
    pilot_text.rstrip() + "\n\n" + CLOSEOUT + "\n",
    encoding="utf-8",
)

expected = sorted([DOC_REL, PILOT_REL])
status = subprocess.check_output(
    ["git", "status", "--porcelain"], cwd=ROOT, text=True
).splitlines()
actual = sorted(line[3:] for line in status)

if actual != expected:
    fail(
        "unexpected mutation boundary\nEXPECTED:\n"
        + "\n".join(expected)
        + "\nACTUAL:\n"
        + "\n".join(actual)
    )

for forbidden in (
    "data",
    "schema",
    "vocab",
    "docs/PROJECT_FOUNDATION.md",
    "docs/PLUGIN_TARGET_ARCHITECTURE.md",
):
    p = subprocess.run(["git", "diff", "--quiet", "--", forbidden], cwd=ROOT)
    if p.returncode != 0:
        fail("forbidden mutation detected under " + forbidden)

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-tests did not pass")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("checker did not pass cleanly")

run("git", "diff", "--check")

print("\n===== RESULT =====")
print("OUTCOME: REGISTRY_PROTOCOL_01_PASS")
print("Added: docs/REGISTRY_POPULATION_PROTOCOL.md")
print("Updated: pilot/PILOT_RECORDS.md")
print("Canonical data changes: 0")
print("Schema/vocabulary/Foundation changes: 0")
print("Expected corpus remains: 65 records — 34 concepts, 9 claims, 22 sources")
print("No commit or push performed.")
