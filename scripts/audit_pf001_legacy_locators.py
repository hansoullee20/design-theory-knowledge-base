#!/usr/bin/env python3
from __future__ import annotations
import csv, re, subprocess, sys, yaml
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
OUTDIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel")
OUTDIR.mkdir(parents=True, exist_ok=True)

def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

sources = {}
for path in sorted((ROOT/"data/sources").glob("*.yaml")):
    d = load(path)
    sources[d["id"]] = d

rows = []
for kind, directory, source_field, locator_field in [
    ("concept","data/concepts","definition_sources","definition_source_locators"),
    ("claim","data/claims","sources","source_locators"),
]:
    for path in sorted((ROOT/directory).glob("*.yaml")):
        d = load(path)
        ids = list(d.get(source_field) or [])
        if not ids:
            continue
        locators = list(d.get(locator_field) or [])
        located = defaultdict(int)
        for loc in locators:
            if isinstance(loc, dict) and isinstance(loc.get("source"), str):
                located[loc["source"]] += 1
        n_located = sum(1 for sid in ids if located.get(sid,0))
        status = "COMPLETE" if n_located == len(ids) else ("MISSING_ALL" if n_located == 0 else "PARTIAL")
        for sid in ids:
            src = sources.get(sid,{})
            citation = str(src.get("citation",""))
            notes = str(src.get("notes",""))
            hint = bool(re.search(r"\b(page|pages|pp\.?|chapter|section|success criterion|figure|table|article|record|term)\b|§", citation+" "+notes, re.I))
            rows.append({
                "record_id": d.get("id",""),
                "kind": kind,
                "record_file": str(path.relative_to(ROOT)),
                "source_id": sid,
                "locator_count": located.get(sid,0),
                "relation_status": status,
                "source_locator_status": "LOCATED" if located.get(sid,0) else "RESEARCH_NEEDED",
                "metadata_locator_hint": "YES" if hint else "NO",
                "citation": citation,
            })

fields = ["record_id","kind","record_file","source_id","locator_count","relation_status","source_locator_status","metadata_locator_hint","citation"]
csv_path = OUTDIR/"pf001_legacy_locator_audit.csv"
with csv_path.open("w",encoding="utf-8",newline="") as f:
    w = csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

by_record = {}
for row in rows:
    by_record[row["record_id"]] = row["relation_status"]
counts = Counter(by_record.values())
missing_edges = [r for r in rows if r["source_locator_status"] == "RESEARCH_NEEDED"]
missing_by_source = Counter(r["source_id"] for r in missing_edges)

md = [
    "# PF-001 Legacy Locator Retrofit Audit","",
    "Repository HEAD: "+subprocess.check_output(["git","rev-parse","--short","HEAD"],cwd=ROOT,text=True).strip(),"",
    "## Summary","",
    f"- Records with source relations audited: {len(by_record)}",
    f"- COMPLETE: {counts.get('COMPLETE',0)}",
    f"- PARTIAL: {counts.get('PARTIAL',0)}",
    f"- MISSING_ALL: {counts.get('MISSING_ALL',0)}",
    f"- Individual source edges needing locator research: {len(missing_edges)}","",
    "## Priority retrofit sources","",
    "| Missing edges | Source ID |","|---:|---|"
]
for sid,n in missing_by_source.most_common():
    md.append(f"| {n} | {sid} |")
md += ["","## Missing / partial records","","| Record | Kind | Status | Missing sources | Metadata hint |","|---|---|---|---|---|"]
grouped = defaultdict(list)
for r in missing_edges:
    grouped[r["record_id"]].append(r)
for rid in sorted(grouped):
    rs = grouped[rid]
    md.append(f"| {rid} | {rs[0]['kind']} | {by_record[rid]} | {', '.join(r['source_id'] for r in rs)} | {', '.join(sorted(set(r['metadata_locator_hint'] for r in rs)))} |")
md += [
    "","## Interpretation","",
    "- COMPLETE means every referenced source on that record has at least one relation-level locator.",
    "- PARTIAL means at least one source is located and at least one still needs research.",
    "- MISSING_ALL means the record is valid under PF-001 but has no exact locator yet.",
    "- Metadata hint is only triage; it does not prove locator correctness.",
    "- This audit does not mutate canonical data."
]
report_path = OUTDIR/"pf001_legacy_locator_audit.md"
report_path.write_text("\n".join(md)+"\n",encoding="utf-8")

print("OUTCOME: PF001_LOCATOR_AUDIT_COMPLETE")
print("REPORT:", report_path)
print("CSV:", csv_path)
print("COMPLETE:", counts.get("COMPLETE",0))
print("PARTIAL:", counts.get("PARTIAL",0))
print("MISSING_ALL:", counts.get("MISSING_ALL",0))
print("MISSING_SOURCE_EDGES:", len(missing_edges))
