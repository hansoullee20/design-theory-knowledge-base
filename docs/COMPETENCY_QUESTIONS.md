# Taxonomy v0.1 Competency Questions

These questions define what the Design Theory v0.1 model must be able to represent before the taxonomy is frozen.

## Core distinctions

1. Can the model distinguish a design concept from a claim about that concept?
2. Can it distinguish artifact-level properties from human perceptual/cognitive constructs and measurable outcomes?
3. Can one term have multiple stable senses without breaking references?
4. Can a claim reference several concepts without duplicating those concepts?
5. Can a claim exist while its evidence remains unassessed?
6. Can definitions carry provenance without being treated as empirical claims?
7. Can conventions, standards, empirical findings, theories, and expert opinion remain distinguishable?
8. Can the same concept apply across multiple disciplines without changing its identifier or file location?
9. Can structural/definitional relationships remain separate from assertions that can be true or false?

## Evidence readiness

10. Can a claim distinguish modality from evidence basis?
11. Can evidence assessment later be added without changing the concept schema?
12. Can evidence strength eventually be derived from an evidence profile rather than manually entered?
13. Can contradictory or qualifying evidence later attach to the same claim?
14. Can claims preserve context and applicability limits?

## Theory and mechanism readiness

15. Can an explanatory mechanism initially be represented as an explanatory claim?
16. Can a theory later group multiple concepts and claims without changing their identifiers?
17. Can artifact → experience → outcome reasoning be represented without conflating those loci?

## Quantification readiness

18. Can an experience- or outcome-locus concept later be operationalized by a method?
19. Can a future observation record store value, unit, uncertainty, context, method, case, and provenance without modifying the concept?
20. Can quantitative findings coexist with qualitative or non-quantifiable design knowledge?

## Stress cases

21. Can the model distinguish multiple senses of `density`?
22. Can it distinguish specified hierarchy from perceived hierarchy?
23. Can it distinguish ecological affordance, perceived affordance, and signifier?
24. Can it distinguish legibility from readability without forcing one arbitrary definition?
25. Can it represent proximity as a concept separately from the claim that proximity influences grouping?
26. Can it represent grid as a concept without encoding "grid improves alignment" as a structural relation?
27. Can it represent WCAG contrast requirements as standards rather than empirical laws?
28. Can it represent the F-pattern as a claim whose `scope` states its contextual limits? (Contested status is an evidence-phase property.)
29. Can it represent left-aligned body text as convention without automatically asserting universal superiority?
30. Can it trace every non-trivial definition and claim to a source?

## Runtime consumer readiness

See `docs/PLUGIN_TARGET_ARCHITECTURE.md`.

31. Can a user-language observation ("hard to scan", "looks cluttered") be mapped
    to candidate concepts and claims without hard-coding diagnoses into concept records?
32. Can a reasoning session retrieve only the records relevant to its current reasoning step within a bounded retrieval budget, without loading the knowledge base wholesale? (Post-freeze runtime verification; no runtime exists in v0.1.)

33. Can candidate artifact-level causes of an experience- or outcome-locus concept be retrieved by inverse claim lookup (claims whose object is that concept), without any diagnosis field on the concept?
