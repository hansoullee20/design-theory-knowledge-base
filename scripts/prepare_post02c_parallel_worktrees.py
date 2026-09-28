#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
BASE = "0a495a2d3321694583177a800354694d1ea50244"
PLAN = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/design-theory-parallel/pf001-batches/pf001_locator_batch_plan.json")
WTROOT = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else Path("~/design-theory-parallel-worktrees").expanduser()
MANROOT = Path("/tmp/design-theory-pf001-manifests")

def run(*args):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True)
    if p.returncode:
        raise SystemExit("ERROR: command failed: " + " ".join(args))

def out(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

if out("git","branch","--show-current") != "main":
    raise SystemExit("ERROR: run from main")

if out("git","status","--porcelain"):
    raise SystemExit("ERROR: working tree must be clean")

run("git","fetch","origin","main")
if out("git","rev-parse","HEAD") != out("git","rev-parse","origin/main"):
    raise SystemExit("ERROR: local main differs from origin/main")
if out("git","rev-parse","HEAD") != BASE:
    raise SystemExit("ERROR: unexpected main baseline " + out("git","rev-parse","--short","HEAD"))

if not PLAN.exists():
    raise SystemExit(f"ERROR: missing plan {PLAN}")

data = json.loads(PLAN.read_text(encoding="utf-8"))
WTROOT.mkdir(parents=True, exist_ok=True)
MANROOT.mkdir(parents=True, exist_ok=True)

targets = [("registry-batch-03a", "registry-batch-03a")]
for b in data["batches"]:
    bid = b["batch_id"].lower().replace("pf001-","pf001-")
    branch = bid
    dirname = bid
    targets.append((branch, dirname))

for branch, dirname in targets:
    wt = WTROOT / dirname
    if wt.exists():
        raise SystemExit(f"ERROR: worktree path already exists: {wt}")
    exists = subprocess.run(
        ["git","show-ref","--verify","--quiet",f"refs/heads/{branch}"],
        cwd=ROOT
    ).returncode == 0
    if exists:
        raise SystemExit(f"ERROR: branch already exists: {branch}")
    run("git","worktree","add","-b",branch,str(wt),BASE)

for b in data["batches"]:
    bid = b["batch_id"]
    branch = bid.lower()
    wt = WTROOT / branch
    lines = [
        f"# {bid} locator research manifest",
        "",
        f"Base commit: {BASE}",
        f"Worktree: {wt}",
        f"Branch: {branch}",
        "",
        "Research rule: verify every locator against the actual source; do not infer page/section precision from citation metadata.",
        "",
    ]
    for src in b["sources"]:
        lines += [
            f"## {src['source_id']}",
            f"source_type: {src.get('source_type','')}",
            f"citation: {src.get('citation','')}",
            "",
            "Target relations:",
        ]
        for edge in src["edges"]:
            lines.append(f"- {edge['record_id']} -> {edge['record_file']}")
        lines.append("")
    (MANROOT/f"{bid}.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

print("\n===== WORKTREES =====")
run("git","worktree","list")
print("\nOUTCOME: POST_02C_WORKTREES_PREPARED")
print("03A_WORKTREE:", WTROOT/"registry-batch-03a")
print("PF001_MANIFEST_ROOT:", MANROOT)
for b in data["batches"]:
    print(b["batch_id"] + "_WORKTREE:", WTROOT/b["batch_id"].lower())
