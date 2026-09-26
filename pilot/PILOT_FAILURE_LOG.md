# Taxonomy v0.1 Pilot Failure Log

Purpose: record every case where the draft schema or controlled vocabularies force an inaccurate, ambiguous, duplicated, or otherwise undesirable representation.

Do not silently work around a schema problem.

Pilot governance during Taxonomy v0.1:
- `disciplines` is not populated merely because the field exists; leave it empty unless the pilot specifically tests disciplinary classification.
- Canonical `notes` contains record content only. Pilot rationale, temporary workarounds, and migration commentary belong in this failure log.
- A mechanically created `perceived-X` concept requires a source that independently defines or operationalizes the perceived construct; do not create perceived twins by naming convention alone.

| ID | Record / Case | Problem | Schema or Vocabulary Involved | Temporary Representation | Proposed Change | Status |
|---|---|---|---|---|---|---|
| PF-001 | Claim/source provenance | `sources` identifies a work but cannot preserve an exact supporting locator such as page, section, figure, table, or passage. | claim/source schema | Source IDs only | Add a locator-capable provenance representation after pilot review; do not choose its final form yet. | open |
| PF-002 | Actor-relative locus | The original locus vocabulary could not represent properties borne by an artifact/environment relative to actor capabilities; confirmed independently by ecological affordance, typeface legibility, and linguistic readability. | concept schema / locus vocabulary | Added `actor-relative`; re-filed the three confirmed records; redefined locus as the bearer of the property using the change test. | Preserve the additive locus through the remaining pilot; actor characteristics remain tracked separately as PF-003. | resolved |
| PF-003 | Actor-characteristic concepts had no locus | The visual-acuity stress test confirmed that a source-defined actor capability could not be represented honestly by artifact, actor-relative, experience, outcome, or practice. | locus vocabulary | Added `actor`; distinguished actor from experience by elicitation rather than persistence; added actor admission and population-descriptor rules; canonicalized visual acuity as actor and critical print size as actor-relative. | Preserve the elicitation boundary in remaining pilot cases; expertise brought to an episode is actor, learning gain from the episode is outcome. | resolved |
