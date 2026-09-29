#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
import yaml

WT = Path.home() / "design-theory-parallel-worktrees" / "pf001-r02"
OUT = Path("/tmp/design-theory-parallel/pf001-r02-verification.md")
BASE = "06b7cd9"

def fail(msg):
    raise SystemExit("ERROR: " + msg)

def sh(*args):
    return subprocess.check_output(args, cwd=WT, text=True).strip()

if not WT.exists():
    fail("missing worktree: " + str(WT))
if sh("git","branch","--show-current") != "pf001-r02":
    fail("pf001-r02 worktree is on the wrong branch")
if sh("git","rev-parse","--short","HEAD") != BASE:
    fail("unexpected pf001-r02 baseline: " + sh("git","rev-parse","--short","HEAD"))
if sh("git","status","--porcelain"):
    fail("pf001-r02 worktree is not clean")

targets = [
    ("source:legge-bigelow-2011-print-size","concept:critical-print-size","READY_WITH_EXACT_QUOTE","TextQuoteSelector","There is a smallest print size below which reading speed begins to decline sharply, termed the critical print size (CPS).","Direct definition of CPS."),
    ("source:legge-bigelow-2011-print-size","concept:legibility-typeface","READY_WITH_SECTION","SectionSelector","INTRODUCTION","Section states that size and shape of printed symbols are crucial to print legibility; Beier remains co-source."),
    ("source:legge-bigelow-2011-print-size","concept:print-size","READY_WITH_SECTION","SectionSelector","Digital Screens","Section distinguishes physical print size from angular size and discusses x-height as the working metric."),
    ("source:legge-bigelow-2011-print-size","concept:reading-speed","READY_WITH_FIGURE","FigureSelector","Figure 2","Figure explicitly plots reading speed in words/minute against print size."),
    ("source:legge-bigelow-2011-print-size","concept:visual-acuity","READY_WITH_SECTION","SectionSelector","INTRODUCTION","Section distinguishes letter acuity, reading acuity, and critical print size; adequate for this source relation."),
    ("source:legge-bigelow-2011-print-size","claim:print-size-influences-reading-speed","READY_WITH_FIGURE","FigureSelector","Figure 2","Direct empirical synthesis of reading-speed curves over print size."),
    ("source:legge-bigelow-2011-print-size","claim:visual-acuity-influences-critical-print-size","HOLD_SOURCE_FIT_REVIEW","","","The paper clearly distinguishes acuity from CPS and discusses low vision, but the current directional claim requires stronger direct support than the reviewed passage provides."),
    ("source:wagemans-2012-gestalt-i","concept:figure-ground-organization","READY_WITH_SECTION","SectionSelector","5.1 Introduction","Direct definition/description of figure-ground organization."),
    ("source:wagemans-2012-gestalt-i","concept:figure","READY_WITH_SECTION","SectionSelector","5.1 Introduction","Defines the occluding/shaped region as figure."),
    ("source:wagemans-2012-gestalt-i","concept:ground","READY_WITH_SECTION","SectionSelector","5.1 Introduction","Defines adjoining region continuing behind as background/ground."),
    ("source:wagemans-2012-gestalt-i","concept:perceptual-grouping","READY_WITH_SECTION","SectionSelector","3.1 Introduction","Directly characterizes grouping as elements perceived as going together."),
    ("source:wagemans-2012-gestalt-i","concept:proximity","READY_WITH_SECTION","SectionSelector","3.1 Introduction","Introduces proximity as relative spatial distance producing grouping."),
    ("source:wagemans-2012-gestalt-i","claim:proximity-increases-perceptual-grouping","READY_WITH_SECTION","SectionSelector","4.2.1 Proximity","Explicitly addresses how grouping strength varies as separation changes."),
    ("source:saw-gatzke-2024-visual-hierarchy","concept:hierarchy-perceived","READY_WITH_QUALIFICATION","SectionSelector","Background","Background frames visual hierarchy in terms of distinguishing relative importance and directing attention; record remains a pilot operational sense."),
    ("source:saw-gatzke-2024-visual-hierarchy","concept:hierarchy-specified","READY_WITH_SECTION","SectionSelector","Background","Describes assigning visual elements and principles to mirror information importance."),
    ("source:saw-gatzke-2024-visual-hierarchy","claim:specified-hierarchy-influences-perceived-hierarchy","READY_WITH_QUALIFICATION","FigureSelector","Figure 1","Figure and surrounding discussion show visual treatment used to establish hierarchy and alter reading/comprehension; evidence status remains unassessed."),
    ("source:schwartz-chassidim-2014-perceived-density","concept:perceived-density","READY_WITH_SECTION","SectionSelector","Abstract","Abstract describes participant ratings of perceived density of road maps."),
    ("source:schwartz-chassidim-2014-perceived-density","claim:display-object-density-influences-perceived-density","READY_WITH_SECTION","SectionSelector","Abstract","Abstract reports prediction of perceived density from displayed map properties including road/junction counts and road length."),
]

problems = []
for source_id, record_id, status, seltype, selvalue, note in targets:
    kind, slug = record_id.split(":",1)
    folder = {"concept":"concepts","claim":"claims"}[kind]
    p = WT / "data" / folder / (slug + ".yaml")
    if not p.exists():
        problems.append("missing record: " + record_id)
        continue
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    rel = d.get("definition_sources",[]) if kind == "concept" else d.get("sources",[])
    if source_id not in rel:
        problems.append(record_id + " does not cite " + source_id)

if problems:
    fail("\n".join(problems))

ready = [x for x in targets if not x[2].startswith("HOLD")]
hold = [x for x in targets if x[2].startswith("HOLD")]

lines = [
    "# PF001-R02 Source Verification",
    "",
    "Baseline: " + BASE,
    "Relations reviewed: " + str(len(targets)),
    "Ready/qualified: " + str(len(ready)),
    "Hold: " + str(len(hold)),
    "",
    "## Governance disposition",
    "",
    "- Do not bulk-mutate all R02 relations yet.",
    "- Wagemans 2012, Saw & Gatzke 2024, and Schwartz-Chassidim 2014 are ready for bounded locator mutation.",
    "- Legge & Bigelow 2011 has six locator-ready relations and one source-fit hold.",
    "- Preserve source coherence by treating the Legge source as a separate sub-batch until the held directional claim is adjudicated.",
    "- No schema, vocabulary, Foundation, or proposition-ID change is implied by locator work.",
    "",
    "## Relation review",
    "",
]

current_source = None
for source_id, record_id, status, seltype, selvalue, note in targets:
    if source_id != current_source:
        current_source = source_id
        lines += ["### " + source_id, ""]
    lines.append("- " + record_id)
    lines.append("  - status: " + status)
    if seltype:
        lines.append("  - selector: " + seltype + " = " + selvalue)
    lines.append("  - note: " + note)

lines += [
    "",
    "## Recommended execution split",
    "",
    "1. PF001-R02A — Wagemans 2012 (6 relations)",
    "2. PF001-R02B — Saw & Gatzke 2024 (3 relations)",
    "3. PF001-R02C — Schwartz-Chassidim 2014 (2 relations)",
    "4. PF001-R02D — Legge & Bigelow 2011 (hold pending source-fit adjudication of visual-acuity-influences-critical-print-size)",
    "",
    "Repository mutation performed by this verification script: 0",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("OUTCOME: PF001_R02_SOURCE_VERIFICATION_PASS")
print("RELATIONS_REVIEWED:", len(targets))
print("READY_OR_QUALIFIED:", len(ready))
print("HOLD:", len(hold))
print("HOLD_RECORD: claim:visual-acuity-influences-critical-print-size")
print("RECOMMENDED_SPLIT: R02A Wagemans / R02B Saw-Gatzke / R02C Schwartz-Chassidim / R02D Legge")
print("REPORT:", OUT)
print("REPOSITORY_MUTATION: 0")
