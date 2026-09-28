#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, yaml
from pathlib import Path

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
OUTDIR = Path(sys.argv[1]) if len(sys.argv)>1 else Path("/tmp/design-theory-parallel")
DRAFT = OUTDIR/"fpattern_02c_draft"
DRAFT.mkdir(parents=True, exist_ok=True)

concept_ids=set()
claim_ids=set()
source_ids=set()
for folder,target in [("data/concepts",concept_ids),("data/claims",claim_ids),("data/sources",source_ids)]:
    for p in (ROOT/folder).glob("*.yaml"):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d,dict) and isinstance(d.get("id"),str):
            target.add(d["id"])

proposed = {
    "data/sources/nielsen-2006-f-pattern.yaml": {
        "id":"source:nielsen-2006-f-pattern","kind":"source",
        "citation":"Nielsen, Jakob. F-Shaped Pattern For Reading Web Content (Original Study). Nielsen Norman Group, 16 April 2006.",
        "source_type":"web","year":2006,"identifier":"",
        "notes":"NN/g summary of the original eyetracking study. Reports 232 users viewing thousands of web pages and describes the recurring F-shaped scanning pattern.",
        "schema_version":"0.1",
    },
    "data/sources/pernice-2017-f-pattern.yaml": {
        "id":"source:pernice-2017-f-pattern","kind":"source",
        "citation":"Pernice, Kara. F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile). Nielsen Norman Group, 12 November 2017.",
        "source_type":"web","year":2017,"identifier":"",
        "notes":"NN/g follow-up and clarification. States that F-shaped scanning is one of several scanning patterns and identifies contextual conditions under which it occurs.",
        "schema_version":"0.1",
    },
    "data/concepts/minimally-formatted-web-text.yaml": {
        "id":"concept:minimally-formatted-web-text","kind":"concept",
        "label":"Minimally formatted web text","aliases":["poorly formatted web text","wall of text"],
        "definition":"Web-page text presented with little or no formatting aids such as subheadings, bullets, or emphasis that support scanning.",
        "definition_sources":["source:pernice-2017-f-pattern"],
        "definition_source_locators":[{
            "source":"source:pernice-2017-f-pattern",
            "selector":{"type":"SectionSelector","value":"Why People Scan in an F-Shaped Pattern"},
        }],
        "locus":["artifact"],"facets":[],"disciplines":[],
        "knowledge_origin":["human-factors"],"traditions":[],
        "is_a":[],"part_of":[],"related":[],
        "record_status":"draft","replaced_by":[],
        "notes":"Artifact-context sense used only to express the empirically observed scanning claim; it does not assert that all minimally formatted text produces one scanning pattern.",
        "schema_version":"0.1",
    },
    "data/concepts/f-shaped-scanning.yaml": {
        "id":"concept:f-shaped-scanning","kind":"concept",
        "label":"F-shaped scanning","aliases":["F-pattern","F-shaped reading pattern"],
        "definition":"A web-content scanning pattern in which gaze is concentrated near the top and left side of the content area, typically forming two horizontal movements followed by a more vertical movement down the left side.",
        "definition_sources":["source:nielsen-2006-f-pattern","source:pernice-2017-f-pattern"],
        "definition_source_locators":[
            {"source":"source:nielsen-2006-f-pattern","selector":{"type":"SectionSelector","value":"F-Shaped Pattern For Reading Web Content"}},
            {"source":"source:pernice-2017-f-pattern","selector":{"type":"SectionSelector","value":"The F-Shaped Pattern"}},
        ],
        "locus":["outcome"],"facets":[],"disciplines":[],
        "knowledge_origin":["human-factors"],"traditions":[],
        "is_a":[],"part_of":[],"related":[],
        "record_status":"draft","replaced_by":[],
        "notes":"Modeled as an episode-level measurable scanning outcome, not a universal reading strategy and not a reusable design-solution pattern record.",
        "schema_version":"0.1",
    },
    "data/claims/minimally-formatted-web-text-influences-f-shaped-scanning.yaml": {
        "id":"claim:minimally-formatted-web-text-influences-f-shaped-scanning","kind":"claim",
        "statement":"Minimally formatted web text can contribute to F-shaped scanning when users are trying to be efficient and are not committed to reading every word.",
        "modality":"descriptive","subject":"concept:minimally-formatted-web-text",
        "predicate":"influences","object":"concept:f-shaped-scanning",
        "basis":["empirical"],"evidence_status":"unassessed",
        "scope":"Applies to scanning of the content area of web pages, not navigation inspection. F-shaped scanning is one of several observed scanning patterns, is rarely a perfect letter F, and is context dependent. The 2017 clarification identifies three co-occurring conditions: little or no web formatting, an efficiency-seeking user goal, and insufficient commitment to read every word. Good formatting can reduce F-shaped scanning; the claim is not universal.",
        "sources":["source:nielsen-2006-f-pattern","source:pernice-2017-f-pattern"],
        "source_locators":[
            {"source":"source:nielsen-2006-f-pattern","selector":{"type":"SectionSelector","value":"F-Shaped Pattern For Reading Web Content"}},
            {"source":"source:pernice-2017-f-pattern","selector":{"type":"SectionSelector","value":"Why People Scan in an F-Shaped Pattern"}},
        ],
        "record_status":"draft","replaced_by":[],
        "notes":"Draft for REGISTRY-BATCH-02C. The artifact condition is represented structurally; user motivation/commitment remain in scope rather than being promoted to concepts solely for this claim.",
        "schema_version":"0.1",
    },
}

for rel,record in proposed.items():
    cid=record["id"]
    existing = cid in concept_ids or cid in claim_ids or cid in source_ids
    if existing:
        print("COLLISION:",cid)
    p=DRAFT/Path(rel).name
    p.write_text(yaml.safe_dump(record,sort_keys=False,allow_unicode=True,width=1000),encoding="utf-8")

memo = [
"# REGISTRY-BATCH-02C F-pattern Adjudication Draft","",
"## Research findings","",
"- NN/g's original 2006 article reports eyetracking of 232 users across thousands of web pages and describes a recurring F-shaped scanning pattern.",
"- NN/g's 2017 follow-up explicitly says scanning does not always form an F and that other common scanning patterns exist.",
"- The 2017 clarification says the F pattern is associated with three conditions: little/no web formatting, an efficiency-seeking task posture, and low commitment to reading every word.",
"- It applies to the content area, not to inspection of navigation controls.",
"- Good formatting can prevent or reduce F-shaped scanning; therefore the F pattern should not be encoded as a universal law or prescriptive design pattern.","",
"## Recommended canonical model","",
"- concept:minimally-formatted-web-text — locus artifact.",
"- concept:f-shaped-scanning — locus outcome because it is an episode-level, measurable gaze/scanning behavior.",
"- claim:minimally-formatted-web-text-influences-f-shaped-scanning — descriptive, empirical, evidence_status unassessed.",
"- User goal and commitment remain in claim scope; they are not minted as concepts solely to satisfy this proposition.",
"- Do not use the reserved pattern record kind: here 'pattern' names an observed scanning outcome, not a reusable problem/forces/solution design pattern.","",
"## Sources","",
"- Nielsen, Jakob. F-Shaped Pattern For Reading Web Content (Original Study). NN/g, 2006. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/",
"- Pernice, Kara. F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile). NN/g, 2017. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/","",
"## Status","",
"- Research/adjudication only.",
"- Draft YAML files are written under this /tmp draft directory, not canonical data.",
"- No repository mutation was performed."
]
memo_path=OUTDIR/"fpattern_02c_adjudication.md"
memo_path.write_text("\n".join(memo)+"\n",encoding="utf-8")

print("OUTCOME: FPATTERN_02C_DRAFT_COMPLETE")
print("MEMO:",memo_path)
print("DRAFT_DIR:",DRAFT)
print("PROPOSED_RECORDS:",len(proposed))
print("REPOSITORY_MUTATION: 0")
