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
