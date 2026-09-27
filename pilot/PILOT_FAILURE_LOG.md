# Taxonomy v0.1 Pilot Failure Log

Purpose: record every case where the draft schema or controlled vocabularies force an inaccurate, ambiguous, duplicated, or otherwise undesirable representation.

Do not silently work around a schema problem.

Pilot governance during Taxonomy v0.1:
- `disciplines` is not populated merely because the field exists; leave it empty unless the pilot specifically tests disciplinary classification.
- Canonical `notes` contains record content only. Pilot rationale, temporary workarounds, and migration commentary belong in this failure log.
- A mechanically created `perceived-X` concept requires a source that independently defines or operationalizes the perceived construct; do not create perceived twins by naming convention alone.

| ID | Record / Case | Problem | Schema or Vocabulary Involved | Temporary Representation | Proposed Change | Status |
|---|---|---|---|---|---|---|
| PF-001 | Claim/source provenance | legacy source arrays identify a work but cannot preserve an exact supporting locator. | claim/concept source-reference schema | Frozen source-ID arrays retained; optional relation-level locator fields added | Added source-anchored selector objects while preserving source IDs and runtime lookup contracts. | resolved |
| PF-002 | Actor-relative locus | The original locus vocabulary could not represent properties borne by an artifact/environment relative to actor capabilities; confirmed independently by ecological affordance, typeface legibility, and linguistic readability. | concept schema / locus vocabulary | Added `actor-relative`; re-filed the three confirmed records; redefined locus as the bearer of the property using the change test. | Preserve the additive locus through the remaining pilot; actor characteristics remain tracked separately as PF-003. | resolved |
| PF-003 | Actor-characteristic concepts had no locus | The visual-acuity stress test confirmed that a source-defined actor capability could not be represented honestly by artifact, actor-relative, experience, outcome, or practice. | locus vocabulary | Added `actor`; distinguished actor from experience by elicitation rather than persistence; added actor admission and population-descriptor rules; canonicalized visual acuity as actor and critical print size as actor-relative. | Preserve the elicitation boundary in remaining pilot cases; expertise brought to an episode is actor, learning gain from the episode is outcome. | resolved |
| PF-005 | `opposite_of` had no valid instance under its stated negation/opposition semantics | FIGURE-GROUND-01 showed figure/ground are complementary, reversible perceptual roles rather than negations; `opposite_of` removed from Taxonomy v0.1. | resolved (removed) |
- **PF-006 — RESOLVED — normative threshold claim representation.** WCAG-01 confirms that
  `basis: standard` and `modality: prescriptive` are available, but the current
  subject–predicate–object claim model cannot faithfully encode a codified threshold
  requirement such as WCAG 2.2 SC 1.4.3: the predicate vocabulary has only
  `increases|decreases|influences`, while `object` accepts only concept IDs.
  Resolve before Taxonomy v0.1 freeze. Do not model numeric thresholds as fake concepts
  or hide the normative operator solely in free text.
- **PF-007 — RESOLVED — conventional-practice claim predicate.** LEFT-ALIGNMENT-01
  confirms that `basis: conventional` can classify the epistemic basis of a claim,
  but the current predicate vocabulary cannot faithfully express a proposition such
  as “left alignment is a familiar convention for body text.” `increases`,
  `decreases`, and `influences` encode effects; `requires` is a
  prescriptive threshold predicate. Resolve before Taxonomy v0.1 freeze without
  turning a convention into an empirical law, formal standard, or universal prescription.
