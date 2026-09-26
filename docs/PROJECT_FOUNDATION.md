# Design Theory Knowledge Base — Project Foundation

**Repository:** `hansoullee20/design-theory-knowledge-base`  
**Status:** Working architecture decision record (rev. 2). Decisions may be superseded; see §17.
**Taxonomy status:** Not yet frozen  
**Purpose of this document:** Record the conclusions reached before detailed Design Theory collection begins.

---

## 1. Canonical project objective

> **Given any design artifact or design problem, identify the underlying theoretical mechanisms, distinguish evidence from convention, explain trade-offs, propose justified interventions, and specify how the proposed improvement should be validated.**

This objective governs future taxonomy, research, documentation, data structure, and tooling decisions.

The project is therefore not intended to become merely:

- a design-theory encyclopedia;
- a collection of PDFs or links;
- a glossary of design terms;
- a list of design rules;
- a replacement for ordinary design plugins.

The long-term goal is an evidence-aware **design reasoning system**.

---

## 2. Long-term reasoning chain

The target system should eventually support the following chain:

```text
DESIGN ARTIFACT / PROBLEM
        ↓
OBSERVATION
        ↓
DIAGNOSIS
        ↓
THEORETICAL MECHANISM
        ↓
EVIDENCE / CONVENTION STATUS
        ↓
POSSIBLE INTERVENTIONS
        ↓
TRADE-OFFS
        ↓
VALIDATION METHOD
        ↓
RESULT / LEARNING
```

This is the intended endpoint, not the first implementation step.

---

## 3. Immediate conclusion: fundamentals come first

Before attempting advanced evidence synthesis or automated design reasoning, the project must establish a stable representation of the basic vocabulary and structure of design.

The first phase is therefore:

> **Codify the commonly accepted fundamentals of design in a structured, machine-readable form.**

Examples include:

- point;
- line;
- shape;
- form;
- space;
- color;
- contrast;
- balance;
- hierarchy;
- alignment;
- proximity;
- grid;
- whitespace;
- typography;
- legibility;
- affordance;
- feedback.

At this stage, the project should document what these concepts are, how they are conventionally defined, where those definitions come from, and how they relate structurally to other concepts.

It should **not yet treat every basic definition as an empirical scientific claim**. A definition is an attributed stipulation: it is recorded with the source that stipulates it, not asserted as a fact about the world.

"Commonly accepted" is itself tradition-bound. Point–line–shape–form–space descends from the Bauhaus-derived basic-design curriculum; proximity from Gestalt psychology; affordance and feedback from ecological psychology and HCI. The registry records that lineage rather than presenting any single curriculum as neutral.

---

## 4. First methodological step: decompose the subject

The first concrete research action is to decompose Design into a small set of **record kinds**, **controlled classification vocabularies**, and **relation types**, and to test them against pilot records before accumulating material.

The structure is **not a single tree**. Theories, claims, evidence, and interventions are not children of concepts; they are separate records that reference concepts by ID. A single claim typically involves several concepts (for example contrast, perceived hierarchy, and attention).

```text
RECORD KINDS     concept · claim · source          (v0.1)
                 theory · method · pattern · case · observation   (reserved)

CLASSIFICATION   locus · facets · disciplines · knowledge_origin · traditions
                 (fields on records, multi-valued, controlled vocabularies)

STRUCTURE        broader · part_of · related · opposite_of
                 (inside concept records; definitional only)

ASSERTIONS       claim records: subject –predicate→ object,
                 with modality, basis, scope, sources, evidence_status
```

**Design Taxonomy v0.1** means the record kinds, the controlled vocabularies, the relation types, the schemas, and the identifier rules, frozen together only after piloting (§12).

---

## 5. Classification: record kind plus orthogonal fields

### 5.1 Why "Domain × Knowledge type" (rev. 1) was insufficient

The rev. 1 Domain axis mixed disciplines (service design), artifact facets (color, typography — which are also concepts), explanatory sciences (perception), quality attributes (accessibility), and meta-perspectives (design history, design science). The Knowledge-type axis mixed record kind (method), normativity (heuristic), epistemic status (empirical claim), and role (validation method). "Principle" in particular conflated a descriptive regularity with a prescription, which is exactly the distinction the objective requires.

### 5.2 Record kind: which schema a record uses

Kinds are few and stable. Subtypes, roles, and statuses are fields, never kinds.

| Kind | What it is | v0.1 |
|---|---|---|
| `concept` | A term-sense: element, property, relation, structure, perceptual or cognitive construct, outcome construct, quality attribute, UI component | populate |
| `claim` | A proposition: descriptive, explanatory, or prescriptive | pilot |
| `source` | A citable work | populate as needed |
| `theory` | A framework bundling claims and explanatory structure (e.g. Gestalt theory) | reserved |
| `method` | A procedure; `role: generative \| evaluative \| both` | reserved |
| `pattern` | A reusable solution form in context (problem, forces, solution) | reserved |
| `case` | A specific artifact or study instance | reserved |
| `observation` | A measured datum: a variable, a value, a context, a case, a method | reserved (§10) |

**Mechanism is not a record kind in v0.1.** A mechanism is represented as a `claim` with `modality: explanatory`. If piloting shows explanatory claims cannot carry mechanism structure, a `mechanism` kind may be added later; promotion is additive, demotion is not.

### 5.3 Classification fields (orthogonal, multi-valued, controlled vocabularies)

- `locus` (**required**): where the thing exists.
  - `artifact`: specifiable by the designer (spacing, contrast ratio, grid)
  - `experience`: a perceptual, cognitive, or affective construct (grouping, salience, perceived hierarchy)
  - `outcome`: a measurable consequence of use (reading speed, error rate, task completion)
  - `practice`: an activity of designing or evaluating

  `outcome` is strictly a locus value. It names a construct, not a measured result; measured results are `observation` records (§10). A record with more than one locus value must be reviewed for splitting into senses (e.g. specified hierarchy vs. perceived hierarchy).
- `facets`: which aspect of an artifact (e.g. form, color, typography, spatial organization, image, motion, information structure, interaction, language).
- `disciplines`: where it is applied (e.g. communication design, interface and interaction design, information design and visualization, product design, service design, spatial design). Optional for fundamentals.
- `knowledge_origin` (optional): the body of knowledge the concept or claim comes from. Closed vocabulary, kept small: perceptual-science, cognitive-psychology, human-factors, design-practice, standards-body, art-craft.
- `traditions` (optional): the school or lineage of the definition (e.g. bauhaus-basic-design, gestalt, swiss-typography, ecological-psychology, usability-engineering).

`knowledge_origin` and `traditions` are distinct: Gestalt is a tradition whose knowledge origin is perceptual science; Swiss typography is a tradition whose knowledge origin is design practice.

Quality attributes (accessibility, usability, legibility) are **concepts**, not domains. Perception and cognition are reached through `knowledge_origin`, theories, and sources, not as domains. Design history is expressed through `traditions` and sources; design science is this project's methodology.

### 5.4 Mapping from rev. 1 candidate types

| Rev. 1 type | Becomes |
|---|---|
| element, concept, perceptual concept | `concept` with appropriate `locus` |
| principle | `concept` (e.g. balance) + one or more `claim`s |
| heuristic | `claim`, `modality: prescriptive`, `basis: [expert-opinion]` or `[conventional]` |
| empirical claim | `claim`, `basis: [empirical]` |
| theory | `theory` |
| mechanism | `claim`, `modality: explanatory` |
| method, validation method | `method` with `role` |
| pattern | `pattern`; UI components (e.g. dropdown menu) are `concept`s with `locus: artifact` |
| intervention | deferred: an application of a pattern or claim within a case context |
| case | `case` |

---

## 6. Canonical storage principle

The project should not primarily store knowledge as long prose documents.

The current preferred architecture is:

```text
STRUCTURED CANONICAL DATA
        ↓
HUMAN-READABLE DOCUMENTATION
        ↓
RESEARCH / LEARNING VIEWS
        ↓
REASONING TOOLS
```

The reverse approach should be avoided:

```text
LONG PROSE
   ↓
AI must repeatedly rediscover structure
```

For the initial phase, **YAML in Git** is the preferred canonical representation because it is:

- human-readable;
- machine-readable;
- diffable;
- version-controlled;
- easy for AI systems to generate and inspect;
- convertible later into JSON, SQL, RDF, graph databases, or MCP-accessible structures.

A database server is not required yet. Neither is a validator, a documentation generator, a graph database, or RDF infrastructure; none is introduced before the pilot (§12).

Hand-written essays (history, debates, worked examples) are permitted in `docs/`, under one rule: prose may explain a claim, but no claim may exist only in prose.

---

## 7. Record schemas (v0.1)

### Concept

```yaml
id: concept:contrast            # immutable; see §15
kind: concept
label: Contrast
aliases: []
definition: >-
  ...
definition_sources: [source:...] # required, at least one
locus: [artifact]               # required
facets: []
disciplines: []
knowledge_origin: []
traditions: []
broader: []                     # is-a parents (concept IDs)
part_of: []
related: []                     # navigational only; asserts nothing; stored one direction
opposite_of: []
record_status: draft            # draft | reviewed | deprecated
replaced_by: []                 # required when deprecated
notes: ""
schema_version: "0.1"
```

Concepts carry **no** functions, effects, failure modes, evidence, interventions, or trade-offs. Those are claims or later record kinds that reference the concept. Concept records do not grow as later layers are added.

### Claim (piloted in v0.1)

```yaml
id: claim:proximity-perceptual-grouping
kind: claim
statement: Elements placed closer together tend to be perceived as belonging to the same group.
modality: descriptive           # descriptive | explanatory | prescriptive
subject: concept:proximity
predicate: increases            # increases | decreases | influences
object: concept:perceptual-grouping
basis: [empirical]              # empirical | theoretical | conventional | standard | doctrinal | expert-opinion
scope: ""                       # context and limits; free text in v0.1
sources: []
evidence_status: unassessed     # unassessed | assessed  (lifecycle only; see §9)
record_status: draft
schema_version: "0.1"
```

### Source

```yaml
id: source:ching-2015-form-space-order
kind: source
citation: "..."
source_type: textbook           # textbook | paper | standard | book | web
year: 2015
identifier: ""                  # DOI, ISBN, or URL
schema_version: "0.1"
```

---

## 8. Relationships are first-class knowledge

Relations fall into two classes with different storage:

1. **Structural and definitional relations** (`broader`, `part_of`, `related`, `opposite_of`) are stored in the concept record, one direction only. Inverses are derived, never stored.
2. **Assertions** — anything that could be true or false, or that evidence could bear on — are stored as **claim records**, never as bare edges. This includes every causal, functional, or prescriptive link.

There is **no structural `ENABLES` relation**, and no `AFFECTS`. Any link that would have used them is either part of a definition's text or a claim.

The future knowledge graph is derived from both classes; it is not maintained by hand.

Reclassification of the rev. 1 examples:

| Rev. 1 edge | Correct representation |
|---|---|
| Contrast AFFECTS Visual Hierarchy | claim: contrast differences increase perceived hierarchy |
| Visual Hierarchy AFFECTS Attention | claim, `basis: [empirical]`, `evidence_status: unassessed`; attention is `locus: experience` |
| Proximity AFFECTS Grouping | claim: Gestalt proximity, `basis: [empirical]` |
| Whitespace AFFECTS Grouping | claim (probably mediated by proximity) |
| Whitespace AFFECTS Density | claim whose meaning depends on the operational definition of density (element count, occupied area, information content); `density` is expected to need splitting into senses |
| Grid ENABLES Alignment | no edge. "A grid is a system of alignment references" belongs in the definition text of `concept:grid`; "using a grid improves alignment consistency" is a claim |

`operationalized_by` (measurable concept → method) is reserved until `method` records exist (§10).

---

## 9. Epistemic classification

Epistemic classification applies to **claims**, never to concepts, and uses independent fields:

- `modality`: descriptive, explanatory, or prescriptive.
- `basis` (multi-valued): empirical, theoretical, conventional (learned expectation or professional habit), standard (codified by a standards body), doctrinal (asserted by a historical school, e.g. "form follows function"), expert-opinion.
- `evidence_status`: `unassessed` or `assessed`. This is a **lifecycle** marker recording whether evidence has been reviewed. It is not a rating.

**No manually entered evidence-strength rating exists at any layer.** When evidence review begins, an assessed claim gains a reserved `evidence_profile` holding retained dimensions rather than a collapsed score:

```yaml
evidence_profile:               # reserved; not in v0.1 schema
  directness:
  consistency:
  replication:
  effect_estimates:
  uncertainty:
  ecological_validity:
  context_match:
```

Any summary label (strong, moderate, weak, mixed, contested) is **derived** from the profile by a documented rule, never hand-entered. This keeps evidence dimensions recoverable for later quantification.

Convention and evidence are not mutually exclusive: a conventional practice may be empirically effective *because* it is conventional, so `basis` is multi-valued. A basic design convention must not be presented as an empirically established law; `evidence_status` stays `unassessed` until evidence is actually reviewed.

---

## 10. Later layers are new record kinds, not new concept fields

Later phases add record kinds that **reference** existing concepts. Concept records do not grow.

```text
concepts + claims + sources                    (fundamentals registry, v0.1)
   + theories; claims move to evidence_status: assessed with evidence_profile
   + methods (role); operationalized_by
   + patterns, cases, interventions, trade-offs (CIMO / QOC / claims analysis)
   + observations
   → reasoning workflows
```

Trade-offs relate options to criteria in a context; interventions exist relative to a problem and a context. Neither is a property of a concept.

### 10.1 Quantification readiness (reserved architectural commitment)

Fundamentals are not quantified. The architecture must nevertheless allow claims, mechanisms, interventions, and outcomes to connect later to measurable variables, so that the system can eventually distinguish

```text
"more whitespace is preferable"
```

from

```text
"in this context, increasing between-group spacing from X to Y
 changed grouping-recognition accuracy from A to B
 while increasing vertical extent by C"
```

without pretending every design property reduces to a number.

The hooks, all reserved and none implemented in v0.1:

- A **measurable variable** is an `outcome`- or `experience`-locus concept **`operationalized_by`** a `method`. No separate variable kind is needed.
- An **`observation`** record holds a measured datum: which variable, which value, in which `case`, by which `method`, under which context. The word `outcome` is never used for a record kind.
- Claims reference concepts as subject and object, so a claim's object can already be an outcome-locus concept. That is the join point between theory and measurement.
- The future chain is therefore:

```text
CONCEPT → CLAIM (incl. explanatory) → INTERVENTION → MEASURABLE VARIABLE
        → OBSERVATION → TRADE-OFF
```

---

## 11. Research architecture identified so far

Research into scientific-knowledge representation and design rationale suggests several useful models for later phases.

### Scientific evidence representation

Relevant ideas include:

- atomic claims;
- source provenance;
- supporting evidence;
- challenging evidence;
- qualification;
- reproducibility;
- human verification of machine extraction.

Models such as Micropublications, SEPIO, and research knowledge graphs demonstrate the value of separating claims and evidence from the source document itself. The v0.1 decision to give every claim its own identity from day one (§8) exists so that these models can attach later without re-auditing the registry.

### CIMO-style design propositions

For actionable design knowledge:

```text
CONTEXT
   +
INTERVENTION
   ↓
MECHANISM
   ↓
OUTCOME
```

This is highly compatible with the project objective because it links what to change, when it applies, why it should work, and what outcome should be observed. The `scope` field on claims is the v0.1 placeholder for CIMO's Context.

### QOC-style design rationale

Design alternatives can later be represented as:

```text
QUESTION
   ↓
OPTIONS
   ↓
CRITERIA
   ↓
EVIDENCE / TRADE-OFFS
```

This supports comparison rather than simplistic universal recommendations. Carroll and Rosson's claims analysis (artifact features with explicit upsides and downsides) and Alexander's "forces" are related models for trade-offs. Design-rationale systems historically failed on capture cost, so required fields are kept minimal.

These models are relevant to later phases but should **not delay the fundamentals taxonomy and registry**.

---

## 12. Current implementation sequence

```text
1.  Foundation rev. 2 (this document)
2.  Write competency questions the v0.1 structure must answer
3.  Minimal schemas for concept, claim, source; controlled vocabularies; ID rules
4.  Pilot 20–25 stress-test records (§13), by hand, including claims and sources
5.  Revise the structure against every pilot failure
6.  Freeze Design Taxonomy v0.1 (git tag: taxonomy-v0.1)
7.  Populate the Design Fundamentals Registry (concepts with definition sources)
8.  Record structural relations; record any causal or prescriptive link only as a claim
9.  Generate human-readable views (tooling introduced only here)
10. Assess evidence for existing claims; add theories
11. Add methods, operationalized_by, patterns, cases, interventions, trade-offs, observations
12. Build artifact-diagnosis and reasoning workflows
13. Expose the corpus through tools such as MCP if useful
```

No validator, generator, database, or graph infrastructure is built before step 9.

The key principle remains: **codification first; database infrastructure later.**

---

## 13. Immediate next deliverable

The next deliverable should be:

# Design Taxonomy v0.1

It should define:

1. competency questions (e.g. "Which artifact-locus concepts can a designer change to influence perceived grouping, and is each link a sourced claim?", "Which fundamentals belong to a single tradition?", "Which terms have multiple senses across sources?");
2. the record kinds and their schemas;
3. controlled vocabularies: locus, facets, disciplines, knowledge_origin, traditions, structural relation types, claim predicates, modality, basis;
4. naming and identifier rules (§15);
5. a pilot set of stress-test records that the structure handles without forcing bad choices, at minimum:
   point; line; contrast; hue/value/saturation; hierarchy (specified vs. perceived); proximity plus the proximity→grouping claim; figure/ground; whitespace and density (sense-dependent relation); grid and alignment (definition text vs. claim); legibility vs. readability; affordance (ecological vs. perceived) and signifier; feedback; Gestalt theory; card sorting (dual role); dropdown menu (component); the F-pattern (contested claim); left-aligned body text (convention); WCAG 4.5:1 contrast (standard).

Only after the pilot passes should the project begin systematically populating the Design Fundamentals Registry.

---

## 14. Decision summary

The project has reached the following working conclusions:

1. The long-term product is a **design reasoning system**, not merely a knowledge archive.
2. The immediate priority is nevertheless **basic Design Theory fundamentals**.
3. The first concrete task is **subject decomposition and taxonomy design**, piloted before freezing.
4. Knowledge is classified by **record kind** plus orthogonal fields (**locus, facets, disciplines, knowledge_origin, traditions**); claims additionally carry **modality, basis, evidence_status**.
5. Canonical knowledge should be **structured and machine-readable**.
6. YAML + schema + Git is sufficient for the initial implementation.
7. Structured views are generated from canonical data; hand-written essays may explain, but no claim may exist only in prose.
8. Relationships between concepts are as important as definitions; structural relations are definitional only.
9. Evidence, mechanisms, interventions, trade-offs, validation, and observations arrive as **new record kinds referencing concepts**, never as fields added to concepts.
10. The taxonomy should be versioned and revisable rather than treated as immutable truth.
11. Concepts and claims are distinct; any assertion that could be true or false is a claim record with its own ID from day one.
12. IDs name senses, not terms, and never encode taxonomy position.
13. Every definition cites a source.
14. Evidence strength is never hand-entered; it is derived from a retained `evidence_profile`.
15. Quantification readiness is a reserved architectural commitment, implemented through `operationalized_by` and `observation` records only when those layers are reached.

---

## 15. Identifier and file rules

- Format: `<kind>:<slug>`, lowercase kebab-case slug (e.g. `concept:contrast`, `claim:proximity-perceptual-grouping`, `source:ching-2015-form-space-order`).
- The kind prefix is the only structure encoded in an ID. Never encode facet, discipline, locus, level, or hierarchy.
- An ID names a **sense**, not a word. Polysemous terms get one ID per sense (e.g. `concept:affordance-ecological`, `concept:affordance-perceived`); the label and aliases carry the shared word.
- IDs are immutable and never reused. Changing a label never changes the ID.
- Removal means `record_status: deprecated` with `replaced_by`; files are not deleted.
- One record per file, at `data/<kind-plural>/<slug>.yaml`, in a flat directory per kind. Classification lives in fields, never in folders.
- Controlled vocabularies live in `vocab/*.yaml`; schemas in `schema/`.
- YAML: no anchors or aliases; every field typed by schema; `schema_version` on every record.

---

## 16. Superseded decisions (rev. 1 → rev. 2)

Recorded so that earlier reasoning is not silently lost.

- Two classification axes (Domain × Knowledge type) → replaced by record kind plus orthogonal fields (§5).
- Concept record with `functions`, `common_failure_modes`, `applications`, `examples`, `level`, `status` → removed; those are claims, later kinds, or renamed (`record_status`).
- Enrichment by adding `evidence`, `mechanisms`, `possible_interventions`, `tradeoffs`, `validation_methods` to concept records → replaced by additive record kinds (§10).
- Relation types `AFFECTS`, `ENABLES`, `CONTRASTS_WITH`, `USED_IN`, `EXPRESSED_BY`, `PREREQUISITE_FOR`, `MEASURED_BY` → removed; causal/functional links are claims; `MEASURED_BY` becomes reserved `operationalized_by`.
- "Freeze taxonomy, then define schema, then populate" → replaced by pilot-before-freeze (§12).
- Rev. 2 review's proposed `support: strong | moderate | weak | ...` field → rejected; replaced by lifecycle `evidence_status` and reserved `evidence_profile` (§9).
- Rev. 2 review's "Whitespace/Density is a definitional inverse" and "Grid/Alignment is definitional" → rejected as hiding claims inside edges (§8).
- Rev. 2 review's placement of perception and cognition under `tradition` → rejected; separate `knowledge_origin` field (§5.3).

---

## 17. Decision log

| Rev | Date | Decision |
|---|---|---|
| 1 | 2026-09-26 | Initial foundation: Domain × Knowledge-type axes; enrichment by concept fields; freeze before pilot. |
| 2 | 2026-09-26 | Record kinds + orthogonal fields (locus, facets, disciplines, knowledge_origin, traditions); concepts separated from claims; no structural ENABLES/AFFECTS; later layers additive; lifecycle `evidence_status` with reserved `evidence_profile`, no hand-entered strength rating; mechanism as explanatory claim; `outcome` locus only, `observation` for measured data; `operationalized_by` reserved; quantification readiness as reserved commitment; ID and file rules; pilot before freeze. |
