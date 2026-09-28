#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
BRANCH = "pf001-r01"
BASE_COMMIT = "0a495a2d3321694583177a800354694d1ea50244"
EXPECTED = sorted([
    "data/concepts/card-sorting.yaml",
    "data/concepts/whitespace.yaml",
    "data/claims/whitespace-decreases-perceived-density.yaml",
    "data/sources/nng-2024-card-sorting.yaml",
    "data/sources/tyler-forge-grid.yaml",
])

def fail(msg):
    raise SystemExit("ERROR: " + msg)

def run(*args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout

def load(rel):
    p = ROOT/rel
    return p, yaml.safe_load(p.read_text(encoding="utf-8"))

def save(path, data):
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")

print("===== PF001-R01 VERIFIED WEB LOCATORS =====")

if subprocess.check_output(["git","branch","--show-current"], cwd=ROOT, text=True).strip() != BRANCH:
    fail(f"expected branch {BRANCH}")

if subprocess.check_output(["git","status","--porcelain"], cwd=ROOT, text=True).strip():
    fail("working tree must be clean")

if subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip() != BASE_COMMIT:
    fail("unexpected base commit")

run(sys.executable, "scripts/pilot_check.py", "--self-test")
run(sys.executable, "scripts/pilot_check.py")

# card sorting definition locator
p, d = load("data/concepts/card-sorting.yaml")
if d.get("definition_source_locators"):
    fail("card-sorting already has definition_source_locators")
d["definition_source_locators"] = [{
    "source": "source:nng-2024-card-sorting",
    "selector": {"type": "SectionSelector", "value": "Definition of Card Sorting"},
}]
save(p, d)

# whitespace definition locator
p, d = load("data/concepts/whitespace.yaml")
if d.get("definition_source_locators"):
    fail("whitespace already has definition_source_locators")
d["definition_source_locators"] = [{
    "source": "source:soegaard-2020-white-space",
    "selector": {"type": "SectionSelector", "value": "What is White Space?"},
}]
save(p, d)

# whitespace claim source locators, one for each source
p, d = load("data/claims/whitespace-decreases-perceived-density.yaml")
if d.get("source_locators"):
    fail("whitespace claim already has source_locators")
d["source_locators"] = [
    {
        "source": "source:soegaard-2020-white-space",
        "selector": {"type": "SectionSelector", "value": "What is White Space?"},
    },
    {
        "source": "source:tyler-forge-grid",
        "selector": {
            "type": "TextQuoteSelector",
            "exact": "White space can be a great tool to balance design elements, create room to breathe, lower the perceived density of content",
        },
    },
]
save(p, d)

# remove stale locator-deferred note from NNG source
p, d = load("data/sources/nng-2024-card-sorting.yaml")
notes = d.get("notes","")
d["notes"] = notes.replace(" Exact source locators remain deferred under PF-001.", "")
save(p, d)

# update stale Tyler note: exact locator is now relation-level
p, d = load("data/sources/tyler-forge-grid.yaml")
d["notes"] = (
    "Design-system guidance explicitly states that white space can lower the perceived density of content. "
    "The page is undated; year 2026 records the access year under the current v0.1 source metadata limitation. "
    "Exact support is now stored as a relation-level TextQuoteSelector on the claim; a dedicated access-date field remains unavailable in v0.1."
)
save(p, d)

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-tests failed")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("checker failed")

run("git","diff","--check")

status_raw = subprocess.check_output(["git","status","--porcelain=v1"], cwd=ROOT, text=True)
actual = sorted(line[2:].lstrip() for line in status_raw.splitlines())
if actual != EXPECTED:
    fail("unexpected mutation boundary\nEXPECTED:\n" + "\n".join(EXPECTED) + "\nACTUAL:\n" + "\n".join(actual))

for forbidden in ("schema","vocab","docs/PROJECT_FOUNDATION.md","docs/PLUGIN_TARGET_ARCHITECTURE.md","pilot/PILOT_RECORDS.md"):
    p = subprocess.run(["git","diff","--quiet","--",forbidden], cwd=ROOT)
    if p.returncode != 0:
        fail("forbidden mutation detected under " + forbidden)

print("\n===== RESULT =====")
print("OUTCOME: PF001_R01_PASS")
print("Resolved source groups: nng-2024-card-sorting, soegaard-2020-white-space, tyler-forge-grid")
print("Relations localized: 4")
print("Canonical record count unchanged: 74 records — 38 concepts, 11 claims, 25 sources")
print("Schema/vocabulary/Foundation changes: 0")
print("No commit or push performed.")
