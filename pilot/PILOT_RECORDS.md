# Taxonomy v0.1 Stress-Test Set

## Artifact / fundamental concepts
- [ ] point
- [ ] line
- [ ] contrast
- [ ] hue
- [ ] value
- [ ] saturation
- [ ] whitespace
- [x] density — split into display-object-density / perceived-density
- [ ] grid
- [ ] alignment

## Artifact ↔ experience ambiguity
- [x] hierarchy — specified
- [x] hierarchy — perceived
- [x] proximity
- [x] perceptual grouping
- [ ] figure
- [ ] ground
- [x] legibility — legibility-typeface + print-size, reading-speed
- [x] readability — readability-linguistic

## Polysemy / theory boundary
- [x] affordance — ecological
- [x] affordance — perceived
- [x] signifier

## Method / component / claim boundary
- [ ] card sorting
- [ ] dropdown menu
- [ ] F-pattern

## Convention / standard boundary
- [ ] left-aligned body text
- [ ] WCAG contrast requirement

## Required associated claims
- [x] proximity → perceptual grouping
- [x] print size → reading speed (artifact → outcome, actor-dependence in scope)
- [ ] grid use → alignment consistency
- [ ] F-pattern contextual claim
- [ ] left alignment prescriptive/conventional claim

## ACTOR-LOCUS-IMPLEMENTATION-01

- [x] `concept:visual-acuity` — `locus: [actor]`; conceptual polarity fixed as greater acuity = finer detail resolved.
- [x] `concept:critical-print-size` — `locus: [actor-relative]`.
- [x] `claim:visual-acuity-influences-critical-print-size` — directional association retained in `scope`.
- [ ] Freeze gate: exercise predicate `decreases` with a case whose conceptual polarity is unambiguous. Assigned case: whitespace → perceived density.

## GRID-STRUCTURE-01

- [x] `concept:grid` — artifact-locus whole.
- [x] `concept:grid-column` — `part_of: [concept:grid]`.
- [x] `concept:gutter` — `part_of: [concept:grid]`.
- [x] `concept:modular-grid` — `is_a: [concept:grid]`.
- [x] `source:muller-brockmann-1981-grid-systems` — 1981 edition; ISBN verified against a library-catalog-derived record.
- Result gate: first source-backed `part_of` and `is_a` edges must validate with 0 warnings.

## FIGURE-GROUND-01

- [x] `concept:figure-ground-organization` — experience locus; source `source:wagemans-2012-gestalt-i`.
- [x] `concept:figure` — experience locus; `related: [concept:ground, concept:figure-ground-organization]`.
- [x] `concept:ground` — experience locus; `related: [concept:figure-ground-organization]`.
- [x] Scratch assertion `concept:figure opposite_of concept:ground` tested outside `data/`.
- Outcome: `EXPECTED_FAILURE` — figure and ground are complementary, reversible perceptual roles, not negations; `opposite_of` removed.

## PRE-FREEZE-HARDENING-01

- [x] Only direct asserted `is_a` edges are stored; transitive closure is derived.
- [x] Redundant direct `is_a` edges implied by closure are discouraged but are not a v0.1 validation error.
- [x] `part_of` excludes membership in a collection or set.
- [x] `part_of` closure is only licensed through compatible constituent senses; v0.1 does not add a meronymy-subtype field.
- [x] `related` overlapping an `is_a` or `part_of` pair produces a review warning.
- [x] Two-node `is_a` cycle self-test added.
- [x] `is_a` locus-mismatch diagnostics show both endpoint locus sets.
- [x] Directional-edge semantic correctness remains a source/definition-review responsibility; the checker does not infer direction from labels.
- [x] DEPRECATION-01 later resolved the lifecycle rule: active references to deprecated concepts remain valid with a review warning; replacement integrity is enforced. See `## DEPRECATION-01` below.

## CARD-SORTING-01

- [x] `concept:card-sorting` minted with `locus: [practice]`.
- [x] Definition source: `source:nng-2024-card-sorting` (newly minted).
- [x] Scratch-only `method:card-sorting` candidate tested outside canonical `data/`.
- [x] Scratch candidate uniquely carried procedural steps, inputs, outputs, variants, participant instructions/applicability details, but no existing competency question or active runtime capability requires those details as a separately addressable canonical entity.
- [x] Decision: `KEEP_METHOD_RESERVED`.
- [x] Current competency/runtime inspection found no active capability requiring an independently addressable procedural entity; runtime remains concept/claim/source-oriented and the method layer remains reserved.
- [x] method remains reserved.
- [x] operationalized_by remains reserved.

## WCAG-01

- [x] Competency question tested: represent WCAG contrast requirements as standards rather than empirical laws.
- [x] Normative source: `source:w3c-wcag-2-2` (newly minted).
- [x] `basis: [standard]` is already available.
- [x] `modality: prescriptive` is already available.
- [x] Scratch-only WCAG 2.2 SC 1.4.3 claim tested outside canonical `data/`.
- [x] Current claim predicates are limited to `increases`, `decreases`, and `influences`; none faithfully means a normative requirement such as “must be at least”.
- [x] Current claim object is concept-ID only and cannot structurally represent the numeric threshold `4.5:1`.
- [x] Encoding the normative threshold only in free-text `statement`/`scope` while using an unrelated comparative predicate would make the structured proposition semantically misleading.
- [x] Outcome: `CLAIM_SCHEMA_GAP`.
- [x] No canonical WCAG claim minted.
- [x] No concept minted solely to disguise the numeric threshold as a concept.
- [x] Foundation remains rev. 8 pending bounded resolution.

## PF-006-RESOLUTION-01

- [x] Preserved concept-to-concept claim endpoints.
- [x] Preserved the existing runtime claim lookup signature.
- [x] Added `requires` plus structured `constraint`.
- [x] Bound `requires` to prescriptive modality and mandatory constraint.
- [x] Forbid constraints on other v0.1 predicates.
- [x] Added permanent positive and negative checker self-tests.
- [x] Scratch WCAG threshold claim passed schema validation.
- [x] Six existing canonical claim files remained byte-for-byte unchanged.
- [x] Corpus count remained unchanged.
- [x] Foundation advanced rev. 8 → rev. 9.
- [x] Outcome: `PF-006_RESOLVED`.

## WCAG-01-RETEST

- [x] Retested CQ27 after PF-006-RESOLUTION-01 / Foundation rev. 9.
- [x] Reused `source:w3c-wcag-2-2`; no duplicate source minted.
- [x] Minted `concept:visual-presentation-of-text` with `locus: [artifact]`.
- [x] Minted `concept:contrast-ratio` with `locus: [artifact]`.
- [x] Minted `claim:wcag-text-presentation-requires-minimum-contrast-ratio`.
- [x] Claim uses `modality: prescriptive`, `basis: [standard]`, `predicate: requires`.
- [x] The 4.5:1 threshold is encoded as `constraint: {operator: gte, value: 4.5, unit: ratio}`.
- [x] Large-scale text, incidental text, and logotype qualifications remain explicit in `scope`.
- [x] No threshold value was modeled as a concept.
- [x] Foundation remains rev. 9; no additional architecture change was required.
- [x] Outcome: `PASS`.

## LEFT-ALIGNMENT-01

- [x] Tested the required pilot case `left-aligned body text (convention)`.
- [x] Added `source:lupton-2010-thinking-with-type` as design-practice evidence for typographic familiarity/convention.
- [x] Minted `concept:left-alignment` with `locus: [artifact]`.
- [x] Minted `concept:body-text` with `locus: [artifact]`.
- [x] Confirmed `basis: [conventional]` is available.
- [x] Scratch-only claim tested: in left-to-right Latin typography, left alignment is a familiar convention for long body text.
- [x] `increases` / `decreases` would falsely encode a comparative effect.
- [x] `influences` would falsely encode an effect or association.
- [x] `requires` would falsely turn a convention into a threshold requirement.
- [x] Outcome: `CLAIM_PREDICATE_GAP`.
- [x] No canonical left-alignment convention claim minted.
- [x] Foundation remains rev. 9 pending bounded predicate-resolution design.

## PF-007-RESOLUTION-01 / LEFT-ALIGNMENT-01-RETEST

- [x] Added `conventional_for` as a descriptive concept-to-concept claim predicate.
- [x] Kept `predicate` semantics independent from epistemic `basis`.
- [x] Added permanent self-tests: descriptive use accepted; non-descriptive use rejected; empirical basis remains structurally possible.
- [x] Minted `claim:left-alignment-conventional-for-body-text`.
- [x] Canonical claim uses `modality: descriptive` and `basis: [conventional]`.
- [x] Scope explicitly excludes universal prescription, formal-standard status, and empirical-superiority claims.
- [x] No existing canonical claim was modified.
- [x] Foundation advanced rev. 9 → rev. 10.
- [x] PF-007 outcome: `RESOLVED`.
- [x] LEFT-ALIGNMENT-01 retest outcome: `PASS`.

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

## DEPRECATION-01

- [x] Confirmed there were no canonical deprecated records before the test.
- [x] Reconciled Foundation lifecycle intent with executable schema/checker rules.
- [x] `deprecated` concept/claim records require non-empty `replaced_by`.
- [x] `draft` / `reviewed` records reject non-empty `replaced_by`.
- [x] Missing replacement targets remain hard errors.
- [x] Self-replacement is a hard error.
- [x] Replacement cycles are hard errors.
- [x] Acyclic replacement chains are valid and preserve historical succession.
- [x] Active concept/claim references to deprecated concepts remain valid but warn.
- [x] Deprecated records remain addressable; files are not deleted.
- [x] v0.1 intentionally does not model retirement-without-successor.
- [x] Added permanent lifecycle self-tests.
- [x] Removed stale live `opposite_of: []` from the Foundation Concept example.
- [x] No canonical data record was mutated.
- [x] Foundation advanced rev. 10 → rev. 11.
- [x] Outcome: `PASS`.

## TAXONOMY-v0.1-FREEZE-AUDIT

- [x] Foundation pre-freeze architecture: rev. 11.
- [x] Corpus: 54 records — 28 concepts, 9 claims, 17 sources.
- [x] Permanent self-test suite: 28 PASS.
- [x] Canonical checker: PASS with 0 warnings.
- [x] `git diff --check`: clean.
- [x] No removed structural term remains live under `data/`, `schema/`, `scripts/`, or `vocab/`.
- [x] Required pilot stress-test set is accounted for through the recorded pilot sequence.
- [x] PF-006 and PF-007 are resolved.
- [x] DEPRECATION-01 is resolved and executable lifecycle invariants are active.
- [x] PF-001 is the sole intentionally open pilot finding and is explicitly deferred to the immediate post-freeze provenance/locator phase; it does not change taxonomy semantics.
- [x] No canonical deprecated record exists at the freeze checkpoint.
- [x] No non-empty `replaced_by` exists at the freeze checkpoint.
- [x] Freeze verdict: `PASS`.
- [x] Taxonomy v0.1 is ready for a dedicated checkpoint commit/tag before PF-001 work begins.

## PF-001-RESOLUTION-01

- [x] Started from immutable taxonomy-v0.1 freeze checkpoint.
- [x] Preserved sources and definition_sources source-ID arrays.
- [x] Added optional relation-level source_locators and definition_source_locators.
- [x] Locator sources must occur in the corresponding legacy source array.
- [x] Added Page, Section, Figure, Table, Fragment, and TextQuote selector shapes.
- [x] Added permanent positive and negative locator self-tests.
- [x] Added canonical WCAG 2.2 SC 1.4.3 locator proof case.
- [x] Existing records without locators remain valid; find_claims remains unchanged.
- [x] Locator edits do not change claim proposition identity.
- [x] Full W3C PROV modeling remains deferred.
- [x] Backward-compatible extension retains schema_version 0.1.
- [x] Taxonomy semantics remain frozen; Foundation rev. 12 to rev. 13.
- [x] PF-001 outcome: RESOLVED.

## REGISTRY-BATCH-01A — VISUAL/FORM FUNDAMENTALS

- [x] Population branch starts from post-PF-001 main checkpoint 12171f1.
- [x] Minted concept:point-graphic with locus artifact and an exact Chapter 3.2 > Point locator.
- [x] Minted concept:line-graphic with locus artifact and Getty AAT 300400858 locator.
- [x] Minted concept:contrast-visual with locus artifact and Getty AAT 300260079 locator.
- [x] Kept concept:contrast-visual distinct from existing concept:contrast-ratio.
- [x] Used sense-qualified IDs for point and line rather than overloaded bare lexical IDs.
- [x] Added three source records; no existing canonical source was duplicated.
- [x] Added no claims or structural relations.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] hue, value, and saturation remain deferred to REGISTRY-BATCH-01B for sense/locus adjudication.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 60 records — 31 concepts, 9 claims, 20 sources.
- [x] Outcome: PASS.

## REGISTRY-BATCH-01B — PERCEIVED COLOR FUNDAMENTALS

- [x] Population branch starts from integrated REGISTRY-BATCH-01A checkpoint 8f43a91.
- [x] Adjudicated hue, saturation, and value before minting; no bare lexical IDs were used.
- [x] Minted concept:hue-perceived with locus experience and CIE S 017:2020 e-ILV term 17-22-067 locator.
- [x] Minted concept:saturation-perceived with locus experience and CIE S 017:2020 e-ILV term 17-22-073 locator.
- [x] Minted concept:color-value-perceived with locus experience and Getty AAT 300056176 locator.
- [x] Saturation remains distinct from chroma.
- [x] Color value remains distinct from general brightness and from HSV/HSB numeric value coordinates.
- [x] Artifact/color-space coordinate senses are intentionally not modeled in this batch.
- [x] Added two source records; CIE S 017:2020 is reused by two concept-definition relations with separate locators.
- [x] Added no claims or structural relations.
- [x] Added no schema, vocabulary, predicate, locus, runtime-contract, or Foundation changes.
- [x] Canonical checker and permanent self-tests pass with 0 warnings.
- [x] Corpus after batch: 65 records — 34 concepts, 9 claims, 22 sources.
- [x] Outcome: PASS.
