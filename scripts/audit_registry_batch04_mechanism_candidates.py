#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
BASE = "db2c2d4c64b6c7ad4ee8107d57459cd45b7b9153"

RECENT_BATCH03 = {
    "concept:form-compositional",
    "concept:visual-balance-perceived",
    "concept:typography-practice",
    "concept:color-perceived",
    "concept:interaction-feedback",
}

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

print("===== REGISTRY BATCH 04 — MECHANISM COVERAGE AUDIT =====")

if out("git", "branch", "--show-current") != "main":
    fail("repository is not on main")
if out("git", "status", "--porcelain"):
    fail("main is dirty")

subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO, check=True)

if out("git", "rev-parse", "HEAD") != out("git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out("git", "rev-parse", "HEAD") != BASE:
    fail("unexpected baseline: " + out("git", "rev-parse", "--short", "HEAD"))

concepts = {}
for p in sorted((REPO / "data/concepts").glob("*.yaml")):
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    concepts[d["id"]] = d

claims = {}
claim_degree = Counter()
claim_roles = defaultdict(list)

for p in sorted((REPO / "data/claims").glob("*.yaml")):
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    claims[d["id"]] = d
    s, o = d.get("subject"), d.get("object")
    if s in concepts:
        claim_degree[s] += 1
        claim_roles[s].append(("subject", d["id"]))
    if o in concepts:
        claim_degree[o] += 1
        claim_roles[o].append(("object", d["id"]))

structural_degree = Counter()
for cid, d in concepts.items():
    for field in ("is_a", "part_of", "related"):
        for other in d.get(field) or []:
            if other in concepts:
                structural_degree[cid] += 1
                structural_degree[other] += 1

facet_counts = Counter()
locus_counts = Counter()
for d in concepts.values():
    facet_counts.update(d.get("facets") or [])
    locus_counts.update(d.get("locus") or [])

claim_connected = sorted(cid for cid in concepts if claim_degree[cid] > 0)
claim_unconnected = sorted(cid for cid in concepts if claim_degree[cid] == 0)
fully_isolated = sorted(
    cid for cid in concepts
    if claim_degree[cid] == 0 and structural_degree[cid] == 0
)

print()
print("===== CORPUS =====")
print(f"concepts: {len(concepts)}")
print(f"claims: {len(claims)}")
print(f"claim/concept ratio: {len(claims)/len(concepts):.3f}")
print(f"claim-connected concepts: {len(claim_connected)}")
print(f"claim-unconnected concepts: {len(claim_unconnected)}")
print(f"fully isolated concepts: {len(fully_isolated)}")

print()
print("===== LOCUS COVERAGE =====")
for k, v in sorted(locus_counts.items()):
    print(f"{k}: {v}")

print()
print("===== FACET COVERAGE =====")
all_facets = [
    "form", "color", "typography", "layout", "image",
    "motion", "information-structure", "interaction", "language"
]
for facet in all_facets:
    print(f"{facet}: {facet_counts.get(facet, 0)}")

print()
print("===== BATCH 03 CONNECTIVITY =====")
for cid in sorted(RECENT_BATCH03):
    d = concepts.get(cid)
    if d is None:
        fail("expected Batch 03 concept missing: " + cid)
    print(
        f"{cid}: claim_degree={claim_degree[cid]}, "
        f"structural_degree={structural_degree[cid]}, "
        f"locus={','.join(d.get('locus') or [])}, "
        f"facets={','.join(d.get('facets') or []) or '-'}"
    )

print()
print("===== CLAIM-UNCONNECTED CONCEPTS =====")
for cid in claim_unconnected:
    d = concepts[cid]
    print(
        f"{cid} | locus={','.join(d.get('locus') or [])} "
        f"| facets={','.join(d.get('facets') or []) or '-'} "
        f"| structural_degree={structural_degree[cid]}"
    )

print()
print("===== BATCH 04 SELECTION RULE =====")
print("1. Prefer mechanism/claim population over further glossary expansion.")
print("2. Prefer claims whose subject and object already exist canonically.")
print("3. Require direct source support and exact locators before minting.")
print("4. Keep evidence status/basis conservative; do not infer causal strength.")
print("5. Mint a new concept only when a selected mechanism cannot be represented with existing endpoints.")
print("6. Reopen architecture only on demonstrated representation failure.")

print()
print("===== ZERO-MUTATION GATE =====")
if out("git", "status", "--porcelain"):
    fail("audit mutated canonical main")
print(out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("OUTCOME: REGISTRY_BATCH_04_MECHANISM_AUDIT_PASS")
print("Canonical mutation: 0")
print("Next: adjudicate 3–5 mechanism candidates from the existing concept graph.")
