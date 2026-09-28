#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, yaml
from pathlib import Path

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
OUTDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel")
OUTDIR.mkdir(parents=True, exist_ok=True)

def ids(path):
    out=set()
    for p in sorted((ROOT/path).glob("*.yaml")):
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        if isinstance(d,dict) and isinstance(d.get("id"),str):
            out.add(d["id"])
    return out

concepts=ids("data/concepts")
claims=ids("data/claims")
pilot=(ROOT/"pilot/PILOT_RECORDS.md").read_text(encoding="utf-8")

checks = [
    ("point","COMPLETE","concept:point-graphic" in concepts,"concept:point-graphic"),
    ("line","COMPLETE","concept:line-graphic" in concepts,"concept:line-graphic"),
    ("contrast","COMPLETE","concept:contrast-visual" in concepts,"concept:contrast-visual"),
    ("hue","COMPLETE","concept:hue-perceived" in concepts,"concept:hue-perceived"),
    ("value","COMPLETE","concept:color-value-perceived" in concepts,"concept:color-value-perceived"),
    ("saturation","COMPLETE","concept:saturation-perceived" in concepts,"concept:saturation-perceived"),
    ("whitespace","COMPLETE","concept:whitespace" in concepts,"concept:whitespace"),
    ("density","COMPLETE",{"concept:display-object-density","concept:perceived-density"} <= concepts,"split senses"),
    ("grid","COMPLETE","concept:grid" in concepts,"concept:grid"),
    ("alignment","PARTIAL_NEIGHBORS",("concept:left-alignment" in concepts and "concept:alignment-consistency" in concepts),"specific senses exist; bare alignment not required yet"),
    ("hierarchy specified/perceived","COMPLETE",{"concept:hierarchy-specified","concept:hierarchy-perceived"} <= concepts,"two senses"),
    ("figure/ground","COMPLETE",{"concept:figure","concept:ground","concept:figure-ground-organization"} <= concepts,"perceptual roles"),
    ("card sorting","COMPLETE","concept:card-sorting" in concepts,"method kind remains reserved"),
    ("dropdown menu","DEFERRED_SPLIT_REQUIRED","LEXICAL_AMBIGUITY_SPLIT_REQUIRED" in pilot,"02A adjudication"),
    ("WCAG contrast requirement","COMPLETE","claim:wcag-text-presentation-requires-minimum-contrast-ratio" in claims,"normative threshold claim"),
    ("left alignment convention","COMPLETE","claim:left-alignment-conventional-for-body-text" in claims,"conventional_for claim"),
    ("grid use -> alignment consistency","COMPLETE","claim:grid-use-increases-alignment-consistency" in claims,"02B claim"),
    ("F-pattern contextual claim","OPEN","claim:f-pattern-contextual" in claims or "claim:low-formatting-web-text-influences-f-shaped-scanning" in claims,"CQ28 / 02C"),
]

md=["# Registry Backlog Reconciliation","",
    "Repository HEAD: "+subprocess.check_output(["git","rev-parse","--short","HEAD"],cwd=ROOT,text=True).strip(),"",
    "## Stress-set reconciliation","",
    "| Item | Expected status | Observed | Evidence |","|---|---|---|---|"]
open_items=[]
for item,expected,observed,evidence in checks:
    if expected=="OPEN":
        status="COMPLETE" if observed else "OPEN"
    elif expected=="DEFERRED_SPLIT_REQUIRED":
        status="DEFERRED_SPLIT_REQUIRED" if observed else "NOT_RECORDED"
    elif expected=="PARTIAL_NEIGHBORS":
        status="PARTIAL_NEIGHBORS" if observed else "OPEN"
    else:
        status="COMPLETE" if observed else "OPEN"
    md.append(f"| {item} | {expected} | {status} | {evidence} |")
    if status=="OPEN":
        open_items.append(item)

foundation_candidates = [
    ("shape","concept:shape"),
    ("form","concept:form"),
    ("space","concept:space"),
    ("color","concept:color"),
    ("balance","concept:balance"),
    ("typography","concept:typography"),
    ("feedback","concept:feedback"),
]
md += ["","## Post-stress fundamental expansion candidates","",
       "| Candidate | Canonical ID present? |","|---|---|"]
for label,cid in foundation_candidates:
    md.append(f"| {label} | {'YES' if cid in concepts else 'NO'} |")

md += ["","## Recommended next sequence","",
       "1. Close the remaining stress-set item: F-pattern contextual claim (02C).",
       "2. Do not mint bare alignment solely to satisfy the stale checklist; specific alignment senses already exist.",
       "3. Keep dropdown terminology deferred until a competency question demands one of the split UI senses.",
       "4. After stress-set closure, start Batch 03 from the unpopulated Foundation fundamentals: shape, form, space, color, balance, typography, feedback.",
       "5. Run PF-001 locator retrofit as a separate maintenance stream, not mixed into semantic population batches.","",
       "## Machine summary","",
       f"- Open stress items: {len(open_items)}",
       f"- Open stress list: {', '.join(open_items) if open_items else 'none'}",
       f"- Concepts: {len(concepts)}",
       f"- Claims: {len(claims)}",
       "- This audit does not mutate canonical data."
]

path=OUTDIR/"registry_backlog_reconciliation.md"
path.write_text("\n".join(md)+"\n",encoding="utf-8")
print("OUTCOME: REGISTRY_BACKLOG_AUDIT_COMPLETE")
print("REPORT:",path)
print("OPEN_STRESS_ITEMS:",len(open_items))
print("OPEN_STRESS_LIST:",", ".join(open_items) if open_items else "none")
