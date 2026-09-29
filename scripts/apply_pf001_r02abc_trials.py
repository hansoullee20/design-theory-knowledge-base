#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
BASE = "06b7cd9"

BATCHES = {
    "pf001-r02a": {
        "source": "source:wagemans-2012-gestalt-i",
        "targets": {
            "data/concepts/figure-ground-organization.yaml": ("definition_source_locators", "SectionSelector", "5.1 Introduction"),
            "data/concepts/figure.yaml": ("definition_source_locators", "SectionSelector", "5.1 Introduction"),
            "data/concepts/ground.yaml": ("definition_source_locators", "SectionSelector", "5.1 Introduction"),
            "data/concepts/perceptual-grouping.yaml": ("definition_source_locators", "SectionSelector", "3.1 Introduction"),
            "data/concepts/proximity.yaml": ("definition_source_locators", "SectionSelector", "3.1 Introduction"),
            "data/claims/proximity-increases-perceptual-grouping.yaml": ("source_locators", "SectionSelector", "4.2.1 Proximity"),
        },
    },
    "pf001-r02b": {
        "source": "source:saw-gatzke-2024-visual-hierarchy",
        "targets": {
            "data/concepts/hierarchy-perceived.yaml": ("definition_source_locators", "SectionSelector", "Background"),
            "data/concepts/hierarchy-specified.yaml": ("definition_source_locators", "SectionSelector", "Background"),
            "data/claims/specified-hierarchy-influences-perceived-hierarchy.yaml": ("source_locators", "FigureSelector", "Figure 1"),
        },
    },
    "pf001-r02c": {
        "source": "source:schwartz-chassidim-2014-perceived-density",
        "targets": {
            "data/concepts/perceived-density.yaml": ("definition_source_locators", "SectionSelector", "Abstract"),
            "data/claims/display-object-density-influences-perceived-density.yaml": ("source_locators", "SectionSelector", "Abstract"),
        },
    },
}

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(cwd: Path, *args: str) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def run(cwd: Path, *args: str) -> None:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))

def ensure_worktree(branch: str) -> Path:
    wt = WTROOT / branch
    if wt.exists():
        if out(wt, "git", "branch", "--show-current") != branch:
            fail(f"{wt} exists but is on the wrong branch")
        if out(wt, "git", "status", "--porcelain"):
            fail(f"{branch} worktree is dirty")
        if out(wt, "git", "rev-parse", "--short", "HEAD") != BASE:
            fail(f"{branch} worktree is not at baseline {BASE}")
        return wt

    exists = subprocess.run(
        ["git","show-ref","--verify","--quiet",f"refs/heads/{branch}"],
        cwd=REPO
    ).returncode == 0
    if exists:
        fail(f"branch {branch} already exists without expected worktree")

    run(REPO, "git", "worktree", "add", "-b", branch, str(wt), BASE)
    return wt

def add_locator(data: dict, field: str, source: str, selector_type: str, selector_value: str) -> None:
    current = data.get(field, [])
    if current is None:
        current = []
    for item in current:
        if item.get("source") == source and item.get("selector", {}).get("type") == selector_type and item.get("selector", {}).get("value") == selector_value:
            fail(f"duplicate locator already present for {source} {selector_type} {selector_value}")
    current.append({
        "source": source,
        "selector": {
            "type": selector_type,
            "value": selector_value,
        },
    })
    data[field] = current

def apply_batch(branch: str, spec: dict) -> None:
    wt = ensure_worktree(branch)
    print(f"\n===== APPLY {branch.upper()} =====")
    expected = sorted(spec["targets"].keys())

    for rel, (field, selector_type, selector_value) in spec["targets"].items():
        path = wt / rel
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        legacy_field = "definition_sources" if field == "definition_source_locators" else "sources"
        if spec["source"] not in data.get(legacy_field, []):
            fail(f"{rel}: {spec['source']} not present in {legacy_field}")

        add_locator(data, field, spec["source"], selector_type, selector_value)
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
            encoding="utf-8",
        )

    run(wt, sys.executable, "scripts/pilot_check.py", "--self-test")
    run(wt, sys.executable, "scripts/pilot_check.py")
    run(wt, "git", "diff", "--check")

    status_raw = out(wt, "git", "status", "--porcelain=v1")
    actual = sorted(line[2:].lstrip() for line in status_raw.splitlines() if line)
    if actual != expected:
        fail(
            f"{branch}: mutation boundary mismatch\nEXPECTED:\n" +
            "\n".join(expected) +
            "\nACTUAL:\n" +
            "\n".join(actual)
        )

    for forbidden in ("schema","vocab","docs/PROJECT_FOUNDATION.md","docs/PLUGIN_TARGET_ARCHITECTURE.md","pilot/PILOT_RECORDS.md"):
        p = subprocess.run(["git","diff","--quiet","--",forbidden], cwd=wt)
        if p.returncode != 0:
            fail(f"{branch}: forbidden mutation under {forbidden}")

    print(f"OUTCOME: {branch.upper().replace('-','_')}_PASS")
    print("Changed files:", len(actual))
    print("No commit or push performed.")

print("===== PF001-R02A/B/C PARALLEL-READY PREP =====")
if out(REPO, "git", "branch", "--show-current") != "main":
    fail("main repository is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("main repository is dirty")

run(REPO, "git", "fetch", "origin", "main")
if out(REPO, "git", "rev-parse", "--short", "HEAD") != BASE:
    fail("unexpected local main baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))
if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")

WTROOT.mkdir(parents=True, exist_ok=True)

for branch, spec in BATCHES.items():
    apply_batch(branch, spec)

print("\n===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("\n===== WORKTREE STATUS =====")
for branch in BATCHES:
    wt = WTROOT / branch
    print(f"--- {branch}")
    print(out(wt, "git", "status", "--short"))

print("\nOUTCOME: PF001_R02ABC_TRIALS_PASS")
print("R02A: Wagemans locator mutation ready for review")
print("R02B: Saw-Gatzke locator mutation ready for review")
print("R02C: Schwartz-Chassidim locator mutation ready for review")
print("R02D: Legge source remains on hold")
print("main: unchanged at", BASE)
