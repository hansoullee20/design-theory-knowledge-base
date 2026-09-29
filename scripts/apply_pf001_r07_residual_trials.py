#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
BASE = "3185887aa4eb3f242a067a0998b3dd3b9b72bbcc"

BATCHES = {
    "pf001-r07a": {
        "source": "source:muller-brockmann-1981-grid-systems",
        "targets": {
            "data/concepts/grid.yaml": [
                ("definition_source_locators", "SectionSelector", "The typographic grid"),
            ],
            "data/concepts/grid-column.yaml": [
                ("definition_source_locators", "SectionSelector", "Construction of the grid"),
            ],
            "data/concepts/gutter.yaml": [
                ("definition_source_locators", "SectionSelector", "The typographic grid"),
                ("definition_source_locators", "SectionSelector", "Construction of the grid"),
            ],
            "data/concepts/modular-grid.yaml": [
                ("definition_source_locators", "SectionSelector", "Construction of the grid"),
            ],
        },
    },
    "pf001-r07b": {
        "source": "source:beier-2012-reading-letters",
        "targets": {
            "data/concepts/legibility-typeface.yaml": [
                ("definition_source_locators", "SectionSelector", "Test methods"),
                ("definition_source_locators", "SectionSelector", "Visual accuracy threshold"),
            ],
        },
    },
    "pf001-r07c": {
        "source": "source:lupton-2010-thinking-with-type",
        "targets": {
            "data/concepts/body-text.yaml": [
                ("definition_source_locators", "PageSelector", "87"),
            ],
        },
    },
    "pf001-r07d": {
        "source": "source:woodruff-landay-stonebraker-1998-density",
        "targets": {
            "data/concepts/display-object-density.yaml": [
                (
                    "definition_source_locators",
                    "TextQuoteSelector",
                    "This principle states that the number of objects per display unit should be constant.",
                ),
                (
                    "definition_source_locators",
                    "TextQuoteSelector",
                    "As mentioned above, our system currently determines density according to the number of objects.",
                ),
            ],
        },
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
            fail(f"{wt} exists but is on wrong branch")
        if out(wt, "git", "status", "--porcelain"):
            fail(f"{branch} worktree is dirty")
        if out(wt, "git", "rev-parse", "HEAD") != BASE:
            fail(f"{branch} is not at required baseline")
        return wt

    exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=REPO,
    ).returncode == 0
    if exists:
        fail(f"branch {branch} already exists without expected worktree")

    run(REPO, "git", "worktree", "add", "-b", branch, str(wt), BASE)
    return wt

def save(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )

def add_locator(
    data: dict,
    field: str,
    source: str,
    selector_type: str,
    selector_value: str,
) -> None:
    locators = list(data.get(field, []) or [])
    selector = {"type": selector_type}
    if selector_type == "TextQuoteSelector":
        selector["exact"] = selector_value
    else:
        selector["value"] = selector_value

    candidate = {"source": source, "selector": selector}
    if candidate in locators:
        fail(
            f"identical locator already present: "
            f"{source} {selector_type}={selector_value}"
        )
    locators.append(candidate)
    data[field] = locators

def validate(wt: Path) -> None:
    s = run(wt, sys.executable, "scripts/pilot_check.py", "--self-test")
    if "SELF-TEST RESULT: PASS" not in s:
        fail("self-test failure in " + wt.name)

    s = run(wt, sys.executable, "scripts/pilot_check.py")
    if "RESULT: PASS (0 warning(s))" not in s:
        fail("checker failure in " + wt.name)

    run(wt, "git", "diff", "--check")

    c = len(list((wt / "data/concepts").glob("*.yaml")))
    k = len(list((wt / "data/claims").glob("*.yaml")))
    s_count = len(list((wt / "data/sources").glob("*.yaml")))
    if (c + k + s_count, c, k, s_count) != (78, 40, 11, 27):
        fail(
            f"unexpected corpus counts in {wt.name}: "
            f"{(c+k+s_count,c,k,s_count)}"
        )

print("===== PF001 R07 RESIDUAL TRIALS =====")

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
    expected = sorted(spec["targets"].keys())

    for rel, locator_specs in spec["targets"].items():
        path = wt / rel
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        legacy_field = "definition_sources"
        if spec["source"] not in data.get(legacy_field, []):
            fail(f"{rel}: {spec['source']} absent from {legacy_field}")

        for field, selector_type, selector_value in locator_specs:
            add_locator(
                data,
                field,
                spec["source"],
                selector_type,
                selector_value,
            )

        save(path, data)

    validate(wt)

    actual = sorted(
        line[2:].lstrip()
        for line in out(wt, "git", "status", "--porcelain=v1").splitlines()
        if line
    )
    if actual != expected:
        fail(
            f"{branch}: mutation boundary mismatch\nEXPECTED:\n" +
            "\n".join(expected) +
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
        if subprocess.run(
            ["git", "diff", "--quiet", "--", forbidden],
            cwd=wt,
        ).returncode != 0:
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

print("\nOUTCOME: PF001_R07_RESIDUAL_TRIALS_PASS")
print("R07A Muller-Brockmann: 4 source edges ready for review")
print("R07B Beier: 1 source edge ready for review")
print("R07C Lupton body-text: 1 source edge ready for review")
print("R07D Woodruff density: 1 source edge ready for review")
print("Still held:")
print("  - Legge visual-acuity -> critical-print-size claim")
print("Expected residual after integration: 1 source edge")
print("main: unchanged at", out(REPO, "git", "rev-parse", "--short", "HEAD"))
