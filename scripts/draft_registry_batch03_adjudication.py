#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(
    ["git","rev-parse","--show-toplevel"], text=True
).strip())
OUTDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel/batch03")
OUTDIR.mkdir(parents=True, exist_ok=True)

def ids(folder):
    result=set()
    for p in sorted((ROOT/folder).glob("*.yaml")):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d,dict) and isinstance(d.get("id"),str):
            result.add(d["id"])
    return result

concepts=ids("data/concepts")
sources=ids("data/sources")

candidates = [
    {
        "term":"shape",
        "status":"READY_FOR_BOUNDED_TRIAL",
        "recommended_id":"concept:shape-visual",
        "locus":"artifact",
        "rationale":"Use the visible outline/configuration sense, not mathematical shape or perceived-shape experience.",
        "source_candidate":"Getty AAT 300056273 — shape (form attribute)",
        "source_id_candidate":"source:getty-aat-300056273-shape-form-attribute",
        "locator_candidate":"AAT record 300056273, Note (English)",
    },
    {
        "term":"form",
        "status":"SPLIT_REQUIRED",
        "recommended_id":"",
        "locus":"",
        "rationale":"Getty distinguishes a general visible-aspect sense from a composition/formal-concept sense; a bare form ID would collapse distinct senses.",
        "source_candidate":"Getty AAT 300444970 and 300056272",
        "source_id_candidate":"",
        "locator_candidate":"",
    },
    {
        "term":"space",
        "status":"READY_FOR_BOUNDED_TRIAL",
        "recommended_id":"concept:space-compositional",
        "locus":"artifact",
        "rationale":"Use the art/design compositional-area sense, distinct from physical/geometric space and from experienced spaciousness.",
        "source_candidate":"Getty AAT 300068896 — space (composition concept)",
        "source_id_candidate":"source:getty-aat-300068896-space-composition",
        "locator_candidate":"AAT record 300068896, Note (English)",
    },
    {
        "term":"color",
        "status":"SPLIT_REQUIRED",
        "recommended_id":"",
        "locus":"",
        "rationale":"Existing hue/saturation/value records are perceptual senses; generic color can refer to perceived color, encoded/specification color, physical stimulus, or design palette.",
        "source_candidate":"CIE S 017:2020 plus design-practice sources",
        "source_id_candidate":"",
        "locator_candidate":"",
    },
    {
        "term":"balance",
        "status":"SPLIT_REQUIRED",
        "recommended_id":"",
        "locus":"",
        "rationale":"Getty defines balance as an impression of visual equilibrium (experience), while design-practice sources also discuss balancing the distribution of elements (artifact/compositional organization).",
        "source_candidate":"Getty AAT 300056247 plus BCcampus Ch. 3.3 Balance",
        "source_id_candidate":"",
        "locator_candidate":"",
    },
    {
        "term":"typography",
        "status":"SPLIT_REQUIRED",
        "recommended_id":"",
        "locus":"",
        "rationale":"Typography can denote the practice of designing/arranging type and the resulting typographic composition/system; practice and artifact senses should not be merged.",
        "source_candidate":"BCcampus Ch. 3.2 Typography",
        "source_id_candidate":"",
        "locator_candidate":"",
    },
    {
        "term":"feedback",
        "status":"SPLIT_REQUIRED",
        "recommended_id":"",
        "locus":"",
        "rationale":"Norman's feedback is communication of action results. A designed feedback mechanism is artifact-locus, while received feedback in an interaction episode may be outcome/experience; bare feedback is underspecified.",
        "source_candidate":"Norman, The Design of Everyday Things, Feedback section",
        "source_id_candidate":"",
        "locator_candidate":"",
    },
]

md = [
    "# Registry Batch 03 Sense Adjudication",
    "",
    "Repository HEAD: " + subprocess.check_output(
        ["git","rev-parse","--short","HEAD"], cwd=ROOT, text=True
    ).strip(),
    "",
    "## Decision table",
    "",
    "| Term | Status | Recommended ID | Locus |",
    "|---|---|---|---|",
]
for c in candidates:
    md.append(f"| {c['term']} | {c['status']} | {c['recommended_id'] or '—'} | {c['locus'] or '—'} |")

md += [
    "",
    "## Detailed adjudication",
    "",
]
for c in candidates:
    md += [
        f"### {c['term']}",
        f"- Status: {c['status']}",
        f"- Recommended ID: {c['recommended_id'] or 'none yet'}",
        f"- Locus: {c['locus'] or 'not yet fixed'}",
        f"- Rationale: {c['rationale']}",
        f"- Source candidate: {c['source_candidate']}",
    ]
    if c["source_id_candidate"]:
        md.append(f"- Proposed new source ID: {c['source_id_candidate']}")
    if c["locator_candidate"]:
        md.append(f"- Exact locator candidate: {c['locator_candidate']}")
    md.append("")

md += [
    "## Recommended Batch 03 split",
    "",
    "### REGISTRY-BATCH-03A — safe artifact fundamentals",
    "- concept:shape-visual",
    "- concept:space-compositional",
    "- no claims",
    "- source records only as needed",
    "",
    "### REGISTRY-BATCH-03B+ — adjudication required before mutation",
    "- form",
    "- color",
    "- balance",
    "- typography",
    "- feedback",
    "",
    "## Governance conclusion",
    "",
    "- Do not mint bare concept:form, concept:color, concept:balance, concept:typography, or concept:feedback yet.",
    "- Batch 03A can proceed independently after source/locator verification.",
    "- The remaining terms should be split only when a competency question or source-backed sense justifies the specific canonical identity.",
    "- This script performs no canonical mutation.",
]

path = OUTDIR/"registry_batch03_adjudication.md"
path.write_text("\n".join(md)+"\n", encoding="utf-8")

print("OUTCOME: REGISTRY_BATCH03_ADJUDICATION_PASS")
for c in candidates:
    print(f"{c['term']}: {c['status']} {c['recommended_id']}")
print("RECOMMENDED_03A: concept:shape-visual, concept:space-compositional")
print("REPORT:", path)
print("REPOSITORY_MUTATION: 0")
