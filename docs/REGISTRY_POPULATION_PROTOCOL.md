# Registry Population Protocol

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
