# Design Theory Knowledge Base — Project Foundation

**Repository:** `hansoullee20/design-theory-knowledge-base`  
**Status:** Canonical project foundation  
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

At this stage, the project should document what these concepts are, how they are conventionally used, and how they relate to other concepts.

It should **not yet treat every basic definition as an empirical scientific claim**.

---

## 4. First methodological step: decompose the subject

The first concrete research action is to break the broad subject of **Design** into a stable category system before accumulating large amounts of material.

The basic hierarchy is expected to resemble:

```text
DESIGN
  ↓
DOMAIN / CATEGORY
  ↓
SUBCATEGORY
  ↓
CONCEPT
  ↓
RELATIONSHIPS
  ↓
THEORY / EVIDENCE
  ↓
APPLICATION / INTERVENTION
```

The taxonomy should initially be frozen as a versioned model, for example `Design Taxonomy v0.1`, rather than treated as final truth.

It may be revised when real structural problems are discovered.

---

## 5. Two independent classification axes

A single folder hierarchy is insufficient because design knowledge has at least two different classification dimensions.

### Axis A — Domain

This answers:

> **What area of design does this belong to?**

Candidate domains include:

- visual design;
- composition;
- typography;
- color;
- perception;
- information design;
- interaction design;
- UX;
- product design;
- service design;
- accessibility;
- behavioral design;
- design systems;
- design history;
- design science.

### Axis B — Knowledge type

This answers:

> **What kind of thing is this?**

Candidate types include:

- element;
- principle;
- concept;
- perceptual concept;
- theory;
- mechanism;
- heuristic;
- method;
- pattern;
- intervention;
- validation method;
- empirical claim;
- case.

This distinction prevents fundamentally different objects such as **contrast**, **Gestalt theory**, **card sorting**, and **dropdown menus** from being represented as equivalent kinds of knowledge.

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

A database server is not required yet.

---

## 7. Fundamental concept record

A basic design concept should eventually use a structured record similar to:

```yaml
id:
name:
aliases:

type:
domain:
level:

definition:

visual_properties: []

functions: []

related_concepts: []

relationships: []

applications: []

common_failure_modes: []

examples: []

notes:

status:
```

The purpose of this initial schema is to document stable conceptual structure without prematurely mixing it with research evidence.

---

## 8. Relationships are first-class knowledge

Definitions alone are insufficient.

The project should explicitly encode relationships between concepts.

Candidate relationship types include:

```text
IS_A
PART_OF
RELATED_TO
CONTRASTS_WITH
ENABLES
AFFECTS
USED_IN
PREREQUISITE_FOR
EXPRESSED_BY
MEASURED_BY
```

Examples:

```text
Contrast
  AFFECTS → Visual Hierarchy

Visual Hierarchy
  AFFECTS → Attention

Proximity
  AFFECTS → Grouping

Grid
  ENABLES → Alignment

Whitespace
  AFFECTS → Grouping
  AFFECTS → Density
```

This relational layer is the beginning of the future Design Theory knowledge graph.

---

## 9. Later evidence layer

After the fundamentals registry is stable enough, concepts can be enriched with a separate research layer.

That later layer may include:

```yaml
evidence:
claims:
mechanisms:
sources:
limitations:
contradictions:
context_dependence:
```

The project should explicitly distinguish:

- empirical findings;
- established theoretical frameworks;
- historical doctrine;
- professional convention;
- heuristics;
- contested claims;
- speculative claims.

A basic design convention should not automatically be presented as an empirically established law.

---

## 10. Later reasoning layer

A further layer will make concepts useful for the canonical project objective.

Candidate fields include:

```yaml
diagnostic_signals:
possible_interventions:
tradeoffs:
validation_methods:
```

The conceptual evolution is therefore:

```text
FUNDAMENTAL CONCEPT
        ↓
EVIDENCE-ENRICHED CONCEPT
        ↓
REASONING-READY CONCEPT
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

Models such as Micropublications, SEPIO, and research knowledge graphs demonstrate the value of separating claims and evidence from the source document itself.

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

This is highly compatible with the project objective because it links what to change, when it applies, why it should work, and what outcome should be observed.

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

This supports comparison rather than simplistic universal recommendations.

These models are relevant to later phases but should **not delay the fundamentals taxonomy and registry**.

---

## 12. Current implementation sequence

The currently preferred order of work is:

```text
1. Define the Design taxonomy
2. Freeze taxonomy v0.1
3. Define the fundamental concept schema
4. Populate the Design Fundamentals Registry
5. Encode relationships among fundamentals
6. Generate human-readable documentation from structured data
7. Add theories and evidence
8. Add mechanisms and contextual limitations
9. Add interventions and trade-offs
10. Add validation methods
11. Build artifact-diagnosis and reasoning workflows
12. Expose the corpus through tools such as MCP if useful
```

The key principle is:

> **Codification first; database infrastructure later.**

---

## 13. Immediate next deliverable

The next deliverable should be:

# Design Taxonomy v0.1

It should define:

1. the top-level domains of design;
2. their major subcategories;
3. the canonical knowledge-object types;
4. naming and identifier rules;
5. initial cross-domain relationship types.

Only after this structure is coherent should the project begin systematically populating the Design Fundamentals Registry.

---

## 14. Decision summary

The project has reached the following working conclusions:

1. The long-term product is a **design reasoning system**, not merely a knowledge archive.
2. The immediate priority is nevertheless **basic Design Theory fundamentals**.
3. The first concrete task is **subject decomposition and taxonomy design**.
4. Design knowledge must be classified by both **domain** and **knowledge type**.
5. Canonical knowledge should be **structured and machine-readable**.
6. YAML + schema + Git is sufficient for the initial implementation.
7. Human-readable pages should eventually be views generated from canonical structured data.
8. Relationships between concepts are as important as definitions.
9. Evidence, mechanisms, interventions, trade-offs, and validation belong in later enrichment layers.
10. The taxonomy should be versioned and revisable rather than treated as immutable truth.
