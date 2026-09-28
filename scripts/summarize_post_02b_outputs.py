#!/usr/bin/env python3
from __future__ import annotations
import csv, re, sys
from collections import Counter
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel")

required = [
    OUT/"pf001_legacy_locator_audit.csv",
    OUT/"pf001_legacy_locator_audit.md",
    OUT/"registry_backlog_reconciliation.md",
    OUT/"fpattern_02c_adjudication.md",
    OUT/"skill_creator_evidence_research.md",
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit("ERROR: missing outputs:\n" + "\n".join(missing))

print("===== POST-02B DECISION SUMMARY =====")

# Locator audit
with (OUT/"pf001_legacy_locator_audit.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
missing_edges = [r for r in rows if r.get("source_locator_status") == "RESEARCH_NEEDED"]
record_status = {}
for r in rows:
    record_status[r["record_id"]] = r["relation_status"]
status_counts = Counter(record_status.values())
source_counts = Counter(r["source_id"] for r in missing_edges)

print("\n[PF-001 LOCATOR RETROFIT]")
print("records_complete=", status_counts.get("COMPLETE",0), sep="")
print("records_partial=", status_counts.get("PARTIAL",0), sep="")
print("records_missing_all=", status_counts.get("MISSING_ALL",0), sep="")
print("missing_source_edges=", len(missing_edges), sep="")
print("top_missing_sources:")
for sid,n in source_counts.most_common(10):
    print(f"  {n:>2}  {sid}")

# Backlog
backlog = (OUT/"registry_backlog_reconciliation.md").read_text(encoding="utf-8")
m = re.search(r"- Open stress items:\s*(\d+)", backlog)
open_count = m.group(1) if m else "UNKNOWN"
m = re.search(r"- Open stress list:\s*(.+)", backlog)
open_list = m.group(1).strip() if m else "UNKNOWN"
print("\n[REGISTRY BACKLOG]")
print("open_stress_items=", open_count, sep="")
print("open_stress_list=", open_list, sep="")
print("next_fundamentals=shape, form, space, color, balance, typography, feedback")

# F-pattern
fp = (OUT/"fpattern_02c_adjudication.md").read_text(encoding="utf-8")
print("\n[F-PATTERN 02C]")
for needle in [
    "concept:minimally-formatted-web-text",
    "concept:f-shaped-scanning",
    "claim:minimally-formatted-web-text-influences-f-shaped-scanning",
]:
    print(("present" if needle in fp else "missing") + ": " + needle)
print("recommended_status=READY_FOR_BOUNDED_CANONICAL_REVIEW")
print("repository_mutation=0")

# Skill/evidence
se = (OUT/"skill_creator_evidence_research.md").read_text(encoding="utf-8")
print("\n[SKILL / EVIDENCE]")
print("skill_creator=DERIVED_BUILD_PIPELINE")
print("canonical_record_kind=NO")
print("evidence_schema_change_now=DEFER")
print("trigger=concrete competency-question failure requiring evidence lines/support/challenge")
print("repository_mutation=0")

print("\n[NEXT EXECUTION ORDER]")
print("1. Review and canonicalize 02C F-pattern.")
print("2. Split PF-001 locator retrofit into source-coherent bounded batches.")
print("3. Start Batch 03 fundamentals after stress-set closure.")
print("4. Keep Skill Creator/evidence-layer work noncanonical until its trigger fires.")
print("\nOUTCOME: POST_02B_DECISION_SUMMARY_PASS")
