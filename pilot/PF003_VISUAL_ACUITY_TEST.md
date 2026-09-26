# PF-003 Visual-Acuity Stress Test

Date: 2026-09-26

## Purpose

Test whether an actor-characteristic construct can be represented honestly by
the current `locus` vocabulary without first adding an `actor` value.

The vocabulary was held fixed during the test:

- `artifact`
- `actor-relative`
- `experience`
- `outcome`
- `practice`

## Source used

Canonical source record: `source:legge-bigelow-2011-print-size`

Local source record: `data/sources/legge-bigelow-2011-print-size.yaml`

Legge & Bigelow (2011), *Does print size matter for reading? A review of
findings from vision science and typography*, Journal of Vision 11(5):8.

Relevant source passage is on article pp. 6–7. The paper distinguishes critical
print size from letter acuity and reading acuity. It defines critical print size
as the smallest character size for which reading can occur at maximum speed,
defines letter acuity by the smallest angular size for identifying unrelated
letters with unconstrained viewing time, and reports that critical print size
is at least twice acuity-letter size for normally sighted readers, with a larger
difference often observed in low vision.

## Candidate classification

### visual acuity

Bearer/change-test result:

- not `artifact`: it is not borne by the designed artifact/environment;
- not `actor-relative`: the construct is an actor capability itself, not a
  property borne by the artifact–actor relation;
- not `experience`: under rev. 4, experience covers perceptual, cognitive,
  or affective state, whereas visual acuity is being represented here as a
  relatively stable visual capability/trait;
- not `outcome`: the construct is not an episode or consequence of use;
- not `practice`: it is not an activity of designing, researching, or
  evaluating.

Result: **no current locus fits without semantic distortion.**

### critical print size

Critical print size is defined relative to reading performance for a reader and
a text stimulus. Changing relevant reader capability or stimulus conditions can
change the threshold. Under the current bearer definition this is a defensible
`actor-relative` construct.

## Claim test

The originally proposed claim
`visual-acuity-influences-critical-print-size` was **not minted**.

Reason: the Legge–Bigelow review clearly distinguishes and quantitatively relates
acuity size and critical print size, but this pilot source alone does not justify
silently converting that relationship into the project's causal-looking
`influences` predicate. Likewise, `decreases` would be ambiguous until
the acuity measure and numeric direction are fixed.

This is an evidence/proposition issue, not an ontology workaround.

## Result

**PF-003 CONFIRMED.**

The test exposes a genuine representation gap for actor-characteristic concepts.
No change was made to `vocab/locus.yaml`, and no knowingly misclassified
canonical record was created.

The next ontology decision is whether to add an `actor` locus or represent
actor-characteristic constructs through another explicit structure while
preserving the bearer semantics of `locus`.
