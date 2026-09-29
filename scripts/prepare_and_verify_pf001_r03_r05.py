#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
OUT = Path("/tmp/design-theory-parallel/pf001-r03-r05-verification.md")
EXPECTED_BASE = "1c6a211"

def fail(msg):
    raise SystemExit("ERROR: " + msg)

def out(cwd, *args):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def run(cwd, *args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="")
    if p.returncode:
        fail("command failed: " + " ".join(args))

if out(REPO, "git", "branch", "--show-current") != "main":
    fail("main repository is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("main repository is dirty")

run(REPO, "git", "fetch", "origin", "main")
if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out(REPO, "git", "rev-parse", "--short", "HEAD") != EXPECTED_BASE:
    fail("unexpected main baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))

for branch in ("pf001-r03","pf001-r04","pf001-r05"):
    wt = WTROOT / branch
    if not wt.exists():
        fail("missing worktree " + str(wt))
    if out(wt, "git", "branch", "--show-current") != branch:
        fail(branch + " worktree is on wrong branch")
    if out(wt, "git", "status", "--porcelain"):
        fail(branch + " worktree is dirty")
    run(wt, "git", "merge", "--ff-only", "origin/main")
    if out(wt, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
        fail(branch + " failed to reach current main")

reviews = [
    ("R03","source:kubovy-holcombe-wagemans-1998-proximity","claim:proximity-increases-perceptual-grouping",
     "READY_WITH_SECTION","SectionSelector","Abstract",
     "Abstract directly reports that grouping strength decreases as relative distance increases."),
    ("R03","source:norman-1999-affordance-conventions-design","concept:affordance-perceived",
     "READY_WITH_SECTION","SectionSelector","Perceived Affordance",
     "Norman explicitly distinguishes perceived affordances from real affordances in this section."),
    ("R03","source:woodruff-landay-stonebraker-1998-density","concept:display-object-density",
     "HOLD_SOURCE_FIT_REVIEW","","",
     "Available source material supports display/information density generally, but the current definition as number of displayed objects relative to a display unit or area needs direct passage verification."),
    ("R03","source:muller-brockmann-1981-grid-systems","concept:grid-column",
     "HOLD_EXACT_LOCATOR_RESEARCH","","",
     "Source fit accepted; exact 1981-edition locator not yet verified."),
    ("R03","source:muller-brockmann-1981-grid-systems","concept:grid",
     "HOLD_EXACT_LOCATOR_RESEARCH","","",
     "Source fit accepted; exact 1981-edition locator not yet verified."),
    ("R03","source:muller-brockmann-1981-grid-systems","concept:gutter",
     "HOLD_EXACT_LOCATOR_RESEARCH","","",
     "Source fit accepted; exact 1981-edition locator not yet verified."),
    ("R03","source:muller-brockmann-1981-grid-systems","concept:modular-grid",
     "HOLD_EXACT_LOCATOR_RESEARCH","","",
     "Source fit accepted; exact 1981-edition locator not yet verified."),

    ("R04","source:lupton-2010-thinking-with-type","concept:body-text",
     "HOLD_SOURCE_FIT_REVIEW","","",
     "The alignment discussion uses long body text but does not directly define the current body-text concept."),
    ("R04","source:lupton-2010-thinking-with-type","concept:left-alignment",
     "READY_WITH_PAGE","PageSelector","113",
     "The alignment spread directly describes flush-left/ragged-right treatment."),
    ("R04","source:lupton-2010-thinking-with-type","claim:left-alignment-conventional-for-body-text",
     "READY_WITH_PAGE","PageSelector","113",
     "The same spread identifies flush-left as the more familiar setting and contrasts it with flush-right for long bodies of text."),
    ("R04","source:norman-2014-design-everyday-things","concept:signifier",
     "READY_WITH_PAGE","PageSelector","14",
     "Norman defines signifier as a perceivable indicator communicating appropriate behavior."),
    ("R04","source:norman-2014-design-everyday-things","claim:signifier-influences-perceived-affordance",
     "READY_WITH_QUALIFICATION","PageSelector","13-14",
     "Pages 13-14 distinguish affordances from signifiers and explain signifiers as communicating where action should take place; the claim remains explanatory and unassessed."),
    ("R04","source:beier-2012-reading-letters","concept:legibility-typeface",
     "HOLD_EXACT_LOCATOR_RESEARCH","","",
     "Book-level source fit is strong, but an exact passage locator for the current definition was not verified."),
    ("R04","source:gibson-1979-ecological-approach","concept:affordance-ecological",
     "READY_WITH_PAGE","PageSelector","127",
     "Chapter 8 states that affordances are what the environment offers the animal and emphasizes animal-environment complementarity."),

    ("R05","source:dubay-2004-principles-of-readability","concept:readability-linguistic",
     "READY_WITH_SECTION","SectionSelector","What is readability?",
     "The section distinguishes readability from legibility and defines readability in terms of ease of understanding/reading for classes of readers."),
]

# Verify record/source relations still exist in current main.
problems = []
for batch, source_id, record_id, status, stype, sval, note in reviews:
    kind, slug = record_id.split(":",1)
    folder = "concepts" if kind == "concept" else "claims"
    p = REPO / "data" / folder / (slug + ".yaml")
    if not p.exists():
        problems.append("missing record: " + record_id)
        continue
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    field = "definition_sources" if kind == "concept" else "sources"
    if source_id not in d.get(field, []):
        problems.append(record_id + " does not cite " + source_id)

if problems:
    fail("\n".join(problems))

ready = [r for r in reviews if r[3].startswith("READY")]
hold = [r for r in reviews if r[3].startswith("HOLD")]

lines = [
    "# PF001 R03-R05 Source Verification",
    "",
    "Baseline: " + EXPECTED_BASE,
    "Relations reviewed: " + str(len(reviews)),
    "Ready/qualified: " + str(len(ready)),
    "Hold: " + str(len(hold)),
    "",
    "## Execution disposition",
    "",
    "- R03 can immediately mutate Kubovy 1998 and Norman 1999; Woodruff and Müller-Brockmann remain held.",
    "- R04 can immediately mutate Lupton left-alignment relations, Norman signifier relations, and Gibson ecological-affordance relation; Lupton body-text and Beier remain held.",
    "- R05 DuBay readability relation is locator-ready.",
    "- Held relations require source-fit or exact-locator research, not schema changes.",
    "",
]

current = None
for row in reviews:
    batch, source_id, record_id, status, stype, sval, note = row
    key = (batch, source_id)
    if key != current:
        current = key
        lines += [f"## {batch} — {source_id}", ""]
    lines.append("- " + record_id)
    lines.append("  - status: " + status)
    if stype:
        lines.append("  - selector: " + stype + " = " + sval)
    lines.append("  - note: " + note)

lines += [
    "",
    "## Recommended next mutation batches",
    "",
    "1. PF001-R03A — Kubovy 1998 proximity claim",
    "2. PF001-R03B — Norman 1999 perceived affordance",
    "3. PF001-R04A — Lupton left-alignment concept + conventional claim",
    "4. PF001-R04B — Norman 2014 signifier concept + explanatory claim",
    "5. PF001-R04C — Gibson 1979 ecological affordance",
    "6. PF001-R05A — DuBay 2004 linguistic readability",
    "",
    "Held:",
    "- R03 Woodruff display-object-density source fit",
    "- R03 Müller-Brockmann exact locators",
    "- R04 Lupton body-text source fit",
    "- R04 Beier exact locator",
    "",
    "Repository mutation performed by this verifier: 0",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("OUTCOME: PF001_R03_R05_SOURCE_VERIFICATION_PASS")
print("BASELINE:", EXPECTED_BASE)
print("RELATIONS_REVIEWED:", len(reviews))
print("READY_OR_QUALIFIED:", len(ready))
print("HOLD:", len(hold))
print("REPORT:", OUT)
print("REPOSITORY_MUTATION: 0")
