#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "08d161dce7d1c4ffbf3b8ce30f884ce433a0a60c"

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

def load_dir(name: str) -> dict[str, dict]:
    records = {}
    for p in sorted((REPO / "data" / name).glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or not isinstance(d.get("id"), str):
            fail(f"invalid record in {p}")
        records[d["id"]] = d
    return records

print("===== BATCH 05A RUNTIME COMPETENCY AUDIT =====")

if out("git", "branch", "--show-current") != "main":
    fail("repository is not on main")
if out("git", "status", "--porcelain"):
    fail("main is dirty")

subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO, check=True)

if out("git", "rev-parse", "HEAD") != out("git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out("git", "rev-parse", "HEAD") != BASE:
    fail("unexpected canonical baseline: " + out("git", "rev-parse", "--short", "HEAD"))

cq_text = (REPO / "docs/COMPETENCY_QUESTIONS.md").read_text(encoding="utf-8")
arch_text = (REPO / "docs/PLUGIN_TARGET_ARCHITECTURE.md").read_text(encoding="utf-8")

for marker in ("31.", "32.", "33."):
    if marker not in cq_text:
        fail(f"competency question {marker[:-1]} missing")
for capability in (
    "search_concepts(query)",
    "get_record(id)",
    "find_claims(subject?, predicate?, object?, modality?, basis?)",
    "trace_sources(claim_id | concept_id)",
    "neighbors(concept_id)",
    "validate_record(record)",
):
    if capability not in arch_text:
        fail("runtime contract capability missing: " + capability)

concepts = load_dir("concepts")
claims = load_dir("claims")
sources = load_dir("sources")

print(f"CORPUS: {len(concepts)+len(claims)+len(sources)} records — "
      f"{len(concepts)} concepts, {len(claims)} claims, {len(sources)} sources")
if (len(concepts), len(claims), len(sources)) != (48, 17, 33):
    fail("unexpected corpus counts")

print()
print("===== CQ30 — SOURCE TRACEABILITY =====")

definition_edges = 0
claim_edges = 0

for cid, d in concepts.items():
    srcs = d.get("definition_sources") or []
    locs = d.get("definition_source_locators") or []
    located = {x.get("source") for x in locs if isinstance(x, dict)}
    for sid in srcs:
        definition_edges += 1
        if sid not in sources:
            fail(f"{cid}: unresolved definition source {sid}")
        if sid not in located:
            fail(f"{cid}: missing definition locator for {sid}")

for cid, d in claims.items():
    srcs = d.get("sources") or []
    locs = d.get("source_locators") or []
    located = {x.get("source") for x in locs if isinstance(x, dict)}
    for sid in srcs:
        claim_edges += 1
        if sid not in sources:
            fail(f"{cid}: unresolved claim source {sid}")
        if sid not in located:
            fail(f"{cid}: missing claim locator for {sid}")

print(f"Definition source edges with locators: {definition_edges}")
print(f"Claim source edges with locators: {claim_edges}")
print("CQ30: PASS_CURRENT_CORPUS")

print()
print("===== CQ33 — INVERSE CLAIM LOOKUP =====")

def find_claims(*, subject=None, predicate=None, object=None, modality=None, basis=None):
    result = []
    for d in claims.values():
        if subject is not None and d.get("subject") != subject:
            continue
        if predicate is not None and d.get("predicate") != predicate:
            continue
        if object is not None and d.get("object") != object:
            continue
        if modality is not None and d.get("modality") != modality:
            continue
        if basis is not None and basis not in (d.get("basis") or []):
            continue
        result.append(d)
    return sorted(result, key=lambda x: x["id"])

expected_queries = {
    "concept:perceptual-grouping": {
        "claim:common-region-influences-perceptual-grouping",
        "claim:element-connectedness-influences-perceptual-grouping",
        "claim:proximity-increases-perceptual-grouping",
        "claim:visual-similarity-increases-perceptual-grouping",
    },
    "concept:perceived-hierarchy": {
        "claim:contrast-visual-influences-perceived-hierarchy",
        "claim:specified-hierarchy-influences-perceived-hierarchy",
        "claim:typography-practice-influences-perceived-hierarchy",
    },
    "concept:reading-speed": {
        "claim:print-size-influences-reading-speed",
        "claim:readability-linguistic-influences-reading-speed",
    },
    "concept:perceived-density": {
        "claim:display-object-density-influences-perceived-density",
        "claim:whitespace-decreases-perceived-density",
    },
    "concept:affordance-perceived": {
        "claim:signifier-influences-perceived-affordance",
    },
}

for object_id, expected_ids in expected_queries.items():
    found = find_claims(object=object_id)
    ids = {x["id"] for x in found}
    if ids != expected_ids:
        fail(f"inverse lookup mismatch for {object_id}: {sorted(ids)}")
    print(f"{object_id}: {len(found)} claim(s)")
    for d in found:
        locus = concepts[d["subject"]]["locus"]
        print(f"  {d['id']} | subject={d['subject']} | locus={','.join(locus)}")

pg = find_claims(object="concept:perceptual-grouping")
if not pg or any(concepts[x["subject"]]["locus"] != ["artifact"] for x in pg):
    fail("CQ33 artifact-cause proof case failed for perceptual grouping")

print("CQ33: PASS_DEMONSTRATED")
print("Proof case: inverse lookup for concept:perceptual-grouping returns four artifact-locus candidate causes.")

print()
print("===== CQ31 — USER-LANGUAGE OBSERVATION MAPPING =====")

for cid, d in concepts.items():
    if "diagnostic_signals" in d:
        fail(f"{cid}: diagnostic_signals must not be hard-coded into concepts")

print("Concept diagnostic_signals fields: 0")
print("Canonical concepts correctly contain no hard-coded diagnostic mapping.")
print("No noncanonical observation-to-candidate mapping layer is currently established.")
print("CQ31: NOT_YET_DEMONSTRATED")
print("Classification: EXPECTED_RUNTIME_GAP, not canonical representation failure.")

print()
print("===== CQ32 — BOUNDED STEP RETRIEVAL =====")

claim_files_touched_by_naive_inverse_scan = len(claims)
total_canonical_files = len(concepts) + len(claims) + len(sources)

print(f"Naive inverse claim lookup currently inspects: {claim_files_touched_by_naive_inverse_scan} claim files")
print(f"Total canonical records: {total_canonical_files}")
print("The retrieval contract is specified, and direct YAML lookup is functional at current scale.")
print("No persistent retrieval implementation, retrieval-budget benchmark, or indexed lookup proof is established by canon.")
print("CQ32: NOT_YET_DEMONSTRATED")
print("Classification: RUNTIME_VALIDATION_GAP, not canonical representation failure.")

print()
print("===== BATCH 05A DECISION =====")
print("CQ30: PASS_CURRENT_CORPUS")
print("CQ31: NOT_YET_DEMONSTRATED")
print("CQ32: NOT_YET_DEMONSTRATED")
print("CQ33: PASS_DEMONSTRATED")
print("Canonical schema change required: NO")
print("Registry population required now: NO")
print("Recommended next experiment: build a noncanonical read-only retrieval harness and benchmark CQ32 before considering indexed/MCP retrieval.")
print("Keep CQ31 separate: observation-to-candidate mapping requires its own noncanonical experiment after retrieval behavior is measured.")

print()
print("===== ZERO-MUTATION GATE =====")
if out("git", "status", "--porcelain"):
    fail("audit mutated canonical main")
print(out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))
print("OUTCOME: BATCH_05A_RUNTIME_COMPETENCY_AUDIT_PASS")
print("Architecture: NO_REOPEN")
print("Canonical mutation: 0")
