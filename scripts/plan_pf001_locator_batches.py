#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(
    ["git","rev-parse","--show-toplevel"], text=True
).strip())

AUDIT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel/pf001_legacy_locator_audit.csv")
OUTDIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/design-theory-parallel/pf001-batches")
OUTDIR.mkdir(parents=True, exist_ok=True)

if not AUDIT.exists():
    raise SystemExit(f"ERROR: missing locator audit CSV: {AUDIT}")

sources = {}
for p in sorted((ROOT/"data/sources").glob("*.yaml")):
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    sources[d["id"]] = {
        "source_type": d.get("source_type",""),
        "citation": d.get("citation",""),
        "identifier": d.get("identifier",""),
        "notes": d.get("notes",""),
    }

with AUDIT.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

missing = [r for r in rows if r.get("source_locator_status") == "RESEARCH_NEEDED"]
by_source = defaultdict(list)
for r in missing:
    by_source[r["source_id"]].append({
        "record_id": r["record_id"],
        "kind": r["kind"],
        "record_file": r["record_file"],
        "relation_status": r["relation_status"],
        "metadata_locator_hint": r["metadata_locator_hint"],
    })

priority = {"web":0, "standard":0, "vocabulary":0, "textbook":1, "paper":2, "book":3}
ordered = sorted(
    by_source.items(),
    key=lambda kv: (
        priority.get(sources.get(kv[0],{}).get("source_type",""), 4),
        -len(kv[1]),
        kv[0],
    )
)

# Keep each source atomic. Pack up to 4 sources per bounded research batch.
batches = []
batch = []
for sid, edges in ordered:
    item = {
        "source_id": sid,
        "source_type": sources.get(sid,{}).get("source_type",""),
        "citation": sources.get(sid,{}).get("citation",""),
        "identifier": sources.get(sid,{}).get("identifier",""),
        "edges": edges,
    }
    if len(batch) >= 4:
        batches.append(batch)
        batch = []
    batch.append(item)
if batch:
    batches.append(batch)

manifest = {
    "head": subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip(),
    "audit_csv": str(AUDIT),
    "missing_source_edges": len(missing),
    "sources_requiring_research": len(by_source),
    "batch_count": len(batches),
    "batches": [],
}

md = [
    "# PF-001 Locator Retrofit Batch Plan",
    "",
    f"Repository HEAD: {manifest['head'][:7]}",
    f"Missing source edges: {len(missing)}",
    f"Sources requiring locator research: {len(by_source)}",
    f"Planned source-coherent batches: {len(batches)}",
    "",
    "Rules:",
    "- one source stays wholly inside one batch;",
    "- research first, canonical mutation later;",
    "- never invent page/section precision;",
    "- book/paper locators require verification against the actual work;",
    "- each mutation batch must declare its exact record-file surface before editing.",
    "",
]

for i, items in enumerate(batches, 1):
    bid = f"PF001-R{i:02d}"
    manifest["batches"].append({"batch_id": bid, "sources": items})
    md += [f"## {bid}", ""]
    for item in items:
        md.append(f"- {item['source_id']} [{item['source_type'] or 'unknown'}]")
        md.append(f"  - edges: {len(item['edges'])}")
        for edge in item["edges"]:
            md.append(f"  - {edge['record_id']} -> {edge['record_file']}")
    md.append("")

(OUTDIR/"pf001_locator_batch_plan.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
(OUTDIR/"pf001_locator_batch_plan.md").write_text(
    "\n".join(md) + "\n",
    encoding="utf-8",
)

print("OUTCOME: PF001_LOCATOR_BATCH_PLAN_PASS")
print("MISSING_SOURCE_EDGES:", len(missing))
print("SOURCES_REQUIRING_RESEARCH:", len(by_source))
print("BATCH_COUNT:", len(batches))
print("PLAN:", OUTDIR/"pf001_locator_batch_plan.md")
print("MANIFEST:", OUTDIR/"pf001_locator_batch_plan.json")
