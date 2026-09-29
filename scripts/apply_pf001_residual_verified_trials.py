#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import yaml

REPO = Path.home() / "design-theory-knowledge-base"
WTROOT = Path.home() / "design-theory-parallel-worktrees"
BASE = "b91fa0192e409e1892b4407809637791b2bfafa3"

BATCHES = {
    "pf001-r06a": {
        "source": "source:w3c-wcag-2-2",
        "targets": {
            "data/concepts/contrast-ratio.yaml":
                ("definition_source_locators", "SectionSelector", "contrast ratio"),
            "data/concepts/visual-presentation-of-text.yaml":
                ("definition_source_locators", "SectionSelector", "Success Criterion 1.4.3 Contrast (Minimum)"),
        },
        "extras": {
            "data/sources/w3c-wcag-2-2.yaml": "remove_stale_pf001_note",
        },
    },
    "pf001-r06b": {
        "source": "source:legge-bigelow-2011-print-size",
        "targets": {
            "data/concepts/critical-print-size.yaml":
                ("definition_source_locators", "PageSelector", "6"),
            "data/concepts/legibility-typeface.yaml":
                ("definition_source_locators", "SectionSelector", "Screen type sizes in on-line newspapers"),
            "data/concepts/print-size.yaml":
                ("definition_source_locators", "SectionSelector", "PRINT SIZE METRICS AND TERMINOLOGY"),
            "data/concepts/reading-speed.yaml":
                ("definition_source_locators", "FigureSelector", "Figure 2"),
            "data/concepts/visual-acuity.yaml":
                ("definition_source_locators", "SectionSelector", "PRINT SIZE METRICS AND TERMINOLOGY"),
            "data/claims/print-size-influences-reading-speed.yaml":
                ("source_locators", "FigureSelector", "Figure 2"),
        },
        "extras": {},
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
        fail(f"identical locator already present: {source} {selector_type}={selector_value}")
    locators.append(candidate)
    data[field] = locators

def apply_extra(path: Path, action: str) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if action == "remove_stale_pf001_note":
        notes = str(data.get("notes", ""))
        old = " Exact locator machinery remains deferred under PF-001."
        if old not in notes:
            fail(f"expected stale PF-001 note not found in {path}")
        data["notes"] = notes.replace(old, "")
    else:
        fail("unknown extra action: " + action)
    save(path, data)

def validate(wt: Path) -> None:
    s = run(wt, sys.executable, "scripts/pilot_check.py", "--self-test")
    if "SELF-TEST RESULT: PASS" not in s:
        fail("self-test failure in " + wt.name)
    s = run(wt, sys.executable, "scripts/pilot_check.py")
    if "RESULT: PASS (0 warning(s))" not in s:
        fail("checker failure in " + wt.name)
    run(wt, "git", "diff", "--check")
    c = len(list((wt/"data/concepts").glob("*.yaml")))
    k = len(list((wt/"data/claims").glob("*.yaml")))
    s_count = len(list((wt/"data/sources").glob("*.yaml")))
    if (c+k+s_count,c,k,s_count) != (78,40,11,27):
        fail(f"unexpected counts in {wt.name}: {(c+k+s_count,c,k,s_count)}")

print("===== PF001 RESIDUAL VERIFIED TRIALS =====")

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
    expected = set(spec["targets"]) | set(spec["extras"])

    for rel, (field, selector_type, selector_value) in spec["targets"].items():
        path = wt / rel
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        legacy_field = "definition_sources" if field == "definition_source_locators" else "sources"
        if spec["source"] not in data.get(legacy_field, []):
            fail(f"{rel}: {spec['source']} absent from {legacy_field}")
        add_locator(data, field, spec["source"], selector_type, selector_value)
        save(path, data)

    for rel, action in spec["extras"].items():
        apply_extra(wt / rel, action)

    validate(wt)

    actual = sorted(
        line[2:].lstrip()
        for line in out(wt, "git", "status", "--porcelain=v1").splitlines()
        if line
    )
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
        if subprocess.run(["git","diff","--quiet","--",forbidden], cwd=wt).returncode != 0:
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

print("\nOUTCOME: PF001_RESIDUAL_VERIFIED_TRIALS_PASS")
print("R06A W3C: 2 locator edges ready for review")
print("R06B Legge: 6 locator edges ready for review")
print("Still held:")
print("  - Legge visual-acuity -> critical-print-size claim")
print("  - Muller-Brockmann grid family (4)")
print("  - Beier legibility-typeface")
print("  - Lupton body-text")
print("  - Woodruff display-object-density")
print("main: unchanged at", out(REPO, "git", "rev-parse", "--short", "HEAD"))
