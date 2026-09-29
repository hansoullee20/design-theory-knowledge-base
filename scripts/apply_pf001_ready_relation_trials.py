#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
BASE = "1c6a211444131e0088fcf3e53c6693ddb0224f32"

BATCHES = {
    "pf001-r03a": {
        "source": "source:kubovy-holcombe-wagemans-1998-proximity",
        "targets": {
            "data/claims/proximity-increases-perceptual-grouping.yaml":
                ("source_locators", "SectionSelector", "Abstract"),
        },
        "extra_mutations": {},
    },
    "pf001-r03b": {
        "source": "source:norman-1999-affordance-conventions-design",
        "targets": {
            "data/concepts/affordance-perceived.yaml":
                ("definition_source_locators", "SectionSelector", "Perceived Affordance"),
        },
        "extra_mutations": {},
    },
    "pf001-r04a": {
        "source": "source:lupton-2010-thinking-with-type",
        "targets": {
            "data/concepts/left-alignment.yaml":
                ("definition_source_locators", "PageSelector", "113"),
            "data/claims/left-alignment-conventional-for-body-text.yaml":
                ("source_locators", "PageSelector", "113"),
        },
        "extra_mutations": {
            "data/sources/lupton-2010-thinking-with-type.yaml":
                "remove_stale_pf001_note",
        },
    },
    "pf001-r04b": {
        "source": "source:norman-2014-design-everyday-things",
        "targets": {
            "data/concepts/signifier.yaml":
                ("definition_source_locators", "PageSelector", "14"),
            "data/claims/signifier-influences-perceived-affordance.yaml":
                ("source_locators", "PageSelector", "13-14"),
        },
        "extra_mutations": {},
    },
    "pf001-r04c": {
        "source": "source:gibson-1979-ecological-approach",
        "targets": {
            "data/concepts/affordance-ecological.yaml":
                ("definition_source_locators", "PageSelector", "127"),
        },
        "extra_mutations": {},
    },
    "pf001-r05a": {
        "source": "source:dubay-2004-principles-of-readability",
        "targets": {
            "data/concepts/readability-linguistic.yaml":
                ("definition_source_locators", "SectionSelector", "What is readability?"),
        },
        "extra_mutations": {},
    },
}

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def out(cwd: Path, *args: str) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def run(cwd: Path, *args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail("command failed: " + " ".join(args))
    return p.stdout

def ensure_worktree(branch: str) -> Path:
    wt = WTROOT / branch

    if wt.exists():
        if out(wt, "git", "branch", "--show-current") != branch:
            fail(f"{wt} exists but is on the wrong branch")
        if out(wt, "git", "status", "--porcelain"):
            fail(f"{branch} worktree is dirty")
        if out(wt, "git", "rev-parse", "HEAD") != BASE:
            fail(f"{branch} worktree is not at required baseline")
        return wt

    exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=REPO,
    ).returncode == 0
    if exists:
        fail(f"branch {branch} already exists without expected worktree")

    run(REPO, "git", "worktree", "add", "-b", branch, str(wt), BASE)
    return wt

def add_locator(data: dict, field: str, source: str, selector_type: str, selector_value: str) -> None:
    locators = list(data.get(field, []) or [])
    candidate = {
        "source": source,
        "selector": {
            "type": selector_type,
            "value": selector_value,
        },
    }
    if candidate in locators:
        fail(f"identical locator already exists for {source}: {selector_type}={selector_value}")
    locators.append(candidate)
    data[field] = locators

def save(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )

def apply_extra(path: Path, action: str) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if action == "remove_stale_pf001_note":
        old = " Exact source locator machinery remains deferred under PF-001."
        notes = data.get("notes", "")
        if old not in notes:
            fail(f"expected stale PF-001 note not found in {path}")
        data["notes"] = notes.replace(old, "")
    else:
        fail(f"unknown extra mutation action: {action}")
    save(path, data)

def validate(wt: Path) -> None:
    s = run(wt, sys.executable, "scripts/pilot_check.py", "--self-test")
    if "SELF-TEST RESULT: PASS" not in s:
        fail(f"self-tests failed in {wt.name}")
    s = run(wt, sys.executable, "scripts/pilot_check.py")
    if "RESULT: PASS (0 warning(s))" not in s:
        fail(f"checker failed in {wt.name}")
    run(wt, "git", "diff", "--check")

    c = len(list((wt / "data/concepts").glob("*.yaml")))
    k = len(list((wt / "data/claims").glob("*.yaml")))
    s_count = len(list((wt / "data/sources").glob("*.yaml")))
    if (c + k + s_count, c, k, s_count) != (78, 40, 11, 27):
        fail(f"unexpected corpus counts in {wt.name}: {(c+k+s_count,c,k,s_count)}")

print("===== PF001 READY RELATION TRIALS =====")

if out(REPO, "git", "branch", "--show-current") != "main":
    fail("main repository is not on main")
if out(REPO, "git", "status", "--porcelain"):
    fail("main repository is dirty")

run(REPO, "git", "fetch", "origin", "main")
if out(REPO, "git", "rev-parse", "HEAD") != out(REPO, "git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")
if out(REPO, "git", "rev-parse", "HEAD") != BASE:
    fail("unexpected main baseline: " + out(REPO, "git", "rev-parse", "--short", "HEAD"))

WTROOT.mkdir(parents=True, exist_ok=True)

for branch, spec in BATCHES.items():
    wt = ensure_worktree(branch)
    print(f"\n===== APPLY {branch.upper()} =====")

    expected = set(spec["targets"].keys()) | set(spec["extra_mutations"].keys())

    for rel, (field, selector_type, selector_value) in spec["targets"].items():
        path = wt / rel
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        legacy_field = "definition_sources" if field == "definition_source_locators" else "sources"
        if spec["source"] not in data.get(legacy_field, []):
            fail(f"{rel}: {spec['source']} not present in {legacy_field}")
        add_locator(data, field, spec["source"], selector_type, selector_value)
        save(path, data)

    for rel, action in spec["extra_mutations"].items():
        apply_extra(wt / rel, action)

    validate(wt)

    status_raw = out(wt, "git", "status", "--porcelain=v1")
    actual = sorted(line[2:].lstrip() for line in status_raw.splitlines() if line)
    expected_sorted = sorted(expected)
    if actual != expected_sorted:
        fail(
            f"{branch}: mutation boundary mismatch\nEXPECTED:\n" +
            "\n".join(expected_sorted) +
            "\nACTUAL:\n" +
            "\n".join(actual)
        )

    for forbidden in (
        "schema",
        "vocab",
        "docs/PROJECT_FOUNDATION.md",
        "docs/PLUGIN_TARGET_ARCHITECTURE.md",
        "pilot/PILOT_RECORDS.md",
    ):
        p = subprocess.run(["git", "diff", "--quiet", "--", forbidden], cwd=wt)
        if p.returncode != 0:
            fail(f"{branch}: forbidden mutation under {forbidden}")

    print("OUTCOME:", branch.upper().replace("-", "_") + "_PASS")
    print("Changed files:", len(actual))
    print("No commit or push performed.")

print("\n===== MAIN IMMUTABILITY GATE =====")
if out(REPO, "git", "status", "--porcelain"):
    fail("main mutated")
print(out(REPO, "git", "rev-list", "--left-right", "--count", "origin/main...HEAD"))

print("\n===== WORKTREE STATUS =====")
for branch in BATCHES:
    wt = WTROOT / branch
    print("---", branch)
    print(out(wt, "git", "status", "--short"))

print("\nOUTCOME: PF001_READY_RELATION_TRIALS_PASS")
print("R03A Kubovy: ready for review")
print("R03B Norman 1999: ready for review")
print("R04A Lupton left-alignment: ready for review")
print("R04B Norman 2014 signifier: ready for review")
print("R04C Gibson: ready for review")
print("R05A DuBay: ready for review")
print("Held relations remain untouched")
print("main: unchanged at", out(REPO, "git", "rev-parse", "--short", "HEAD"))
