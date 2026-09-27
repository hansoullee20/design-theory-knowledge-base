# Runtime Target Architecture — Consumer Contract

Foundation baseline: `docs/PROJECT_FOUNDATION.md` — foundation rev. 8


**Status:** Working contract (rev. 1). Companion to `docs/PROJECT_FOUNDATION.md` rev. 6.
**Purpose:** State what the canonical knowledge base must be able to serve at runtime, so the ontology is not designed in isolation from its use. This document decides interfaces and boundaries, not packaging, hosting, or vendor.

---

## 1. Statement

The canonical knowledge base is designed to serve a **design-reasoning skill** and, when triggered, a **read-only retrieval layer**. Both are consumers. Neither is canon.

```text
CANON                      data/  schema/  vocab/  docs/PROJECT_FOUNDATION.md
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          Generated doctrine              Retrieval interface
          for the skill                   (files initially;
                    │                      indexed / MCP if triggered)
                    └──────────────┬──────────────┘
                                   ▼
                       Design-reasoning runtime
                                   │
        observation → candidate concepts → claims / mechanisms
        → evidence status → intervention → trade-offs → validation
```

**Rule:** the repository defines knowledge and governance; the skill defines reasoning workflow; the retrieval layer exposes canonical records; no runtime consumer becomes canonical.

---

## 2. Authority boundary

- `data/`, `schema/`, `vocab/`, and the foundation change only through Git review.
- A runtime may **propose** — candidate concept, candidate claim, candidate evidence link, pilot-failure note — to a `proposals/` path or a branch. It never writes canon.
- The first retrieval layer is **read-only**. Controlled authoring (`propose_record`, `propose_claim`, `log_pilot_failure`) is a later, separately reviewed capability.
- `validate_record` is permitted in the retrieval layer from the start: it is deterministic schema and governance validation (the `scripts/pilot_check.py` logic), not design reasoning.

---

## 3. Retrieval contract

Capabilities, independent of transport. Direct file reading satisfies all of them at current scale.

```text
search_concepts(query)                       labels + aliases → concept IDs
get_record(id)                               any kind, by immutable ID
find_claims(subject?, predicate?, object?, modality?, basis?)
trace_sources(claim_id | concept_id)         provenance chain
neighbors(concept_id)                        is_a / part_of / related,
                                             with derived inverses
validate_record(record)                        schema + vocabulary + referential checks
```

What makes this contract possible is §15 of the foundation: IDs name senses, never move, never encode classification. The contract assumes nothing else about storage.

Normative `constraint` data is returned with the claim record payload. It adds no v0.1 retrieval parameter: `find_claims(subject?, predicate?, object?, modality?, basis?)` remains unchanged, and `subject` / `object` remain concept IDs.

Not in the retrieval layer: `diagnose_design`, `suggest_validation`, or any other step of the reasoning chain. Those are reasoning and live in the skill, where they are versioned and testable against the foundation.

---

## 4. Skill contract

- The doctrinal content of the skill (concept vs. claim, loci, evidence vs. convention, basis and evidence status) is **generated** from `docs/PROJECT_FOUNDATION.md` §5, §8, §9 and from `vocab/`. It is a view, per foundation §6. It is never hand-maintained as a second copy.
- The hand-written part is the **workflow** only: observation → candidate concepts → claims / mechanisms → evidence status → intervention → trade-offs → validation.
- The skill must stop and say so when evidence is insufficient. Operationally: a claim with `evidence_status: unassessed` may be cited as a hypothesis, never as an established finding; a `basis` of `conventional` or `expert-opinion` is reported as such.
- The skill retrieves records by ID as it reasons; it does not load the knowledge base wholesale.

---

## 5. Ontology obligations created by this contract

Recorded as competency questions 31–32 in `docs/COMPETENCY_QUESTIONS.md`:

- A user-language observation ("hard to scan", "looks cluttered") must be mappable to candidate concepts and claims **without** hard-coding diagnoses into concept records. Foundation rev. 2 removed `diagnostic_signals` from concepts deliberately; the mapping layer is a later record kind or view, not a concept field. Its design is deferred.
- A reasoning session must be able to retrieve only what its current step needs, within a bounded retrieval budget. The budget is set by a runtime benchmark, not chosen now.

---

## 6. Build triggers (not phases)

Build an indexed or MCP retrieval layer only when at least one holds:

1. direct file retrieval becomes materially inefficient at knowledge-base scale;
2. a second runtime consumer needs the same interface;
3. structured claim lookup (`find_claims` by subject / object) requires an index.

Until then the skill reads YAML directly, which is also more inspectable.

---

## 7. Non-decisions

Deliberately not decided here: vendor packaging (Claude plugin, OpenAI plugin, other), hosting, authentication, transport, and the form of the symptom-to-concept mapping layer. A private plugin is a **deployment target** of this contract, not the system architecture.

---

## 8. Sequence

```text
NOW       ontology pilot → Taxonomy v0.1 → fundamentals registry
THEN      generated-doctrine skill; test reasoning against repository files
IF        a build trigger fires → read-only retrieval layer
THEN      package as a private plugin for the chosen surface(s)
LATER     controlled authoring via proposals, Git review retained
```

## Canon version and proposal invariants

- `proposals/` is non-canonical. It is excluded from canonical traversal and retrieval, must pass `validate_record(record)` before review, and is never auto-merged into canonical data.
- Retrieval exposes each record's `schema_version`.
- Generated reasoning-skill doctrine records the Git commit or taxonomy tag from which it was generated, so doctrine and retrieved canonical data cannot silently drift across versions.
