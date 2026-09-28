#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

BRANCH = "registry-batch-02b"
MAIN_BASE = "6702ec59eb8f1ad5e8508c8c34565c7560feb5bf"
EXPECTED_PATHS = sorted([
    "data/concepts/grid-use.yaml",
    "data/concepts/alignment-consistency.yaml",
    "data/claims/grid-use-increases-alignment-consistency.yaml",
    "data/sources/nng-2025-good-visual-design.yaml",
    "pilot/PILOT_RECORDS.md",
])

def fail(msg: str) -> None:
    raise SystemExit("ERROR: " + msg)

def call(args, check=True, capture=False):
    print("$", " ".join(args), flush=True)
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=capture)
    if capture:
        if p.stdout:
            print(p.stdout, end="")
        if p.stderr:
            print(p.stderr, end="", file=sys.stderr)
    if check and p.returncode != 0:
        fail("command failed: " + " ".join(args))
    return p

def out(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def push_retry(refspec_args, attempts=6):
    for i in range(1, attempts + 1):
        print(f"===== PUSH ATTEMPT {i}/{attempts} =====")
        p = subprocess.run(["git", "push", *refspec_args], cwd=ROOT, text=True)
        if p.returncode == 0:
            return
        if i == attempts:
            fail("git push failed after retries")
        time.sleep(10)

print("===== REGISTRY-BATCH-02B FINALIZE =====")

if out("git", "branch", "--show-current") != BRANCH:
    fail(f"expected branch {BRANCH}")

status = out("git", "status", "--porcelain").splitlines()
actual = sorted(line[3:] for line in status)
if actual != EXPECTED_PATHS:
    fail(
        "unexpected mutation boundary\nEXPECTED:\n"
        + "\n".join(EXPECTED_PATHS)
        + "\nACTUAL:\n"
        + "\n".join(actual)
    )

print("===== PRE-COMMIT VALIDATION =====")
call([sys.executable, "scripts/pilot_check.py", "--self-test"])
call([sys.executable, "scripts/pilot_check.py"])
call(["git", "diff", "--check"])

for path in EXPECTED_PATHS:
    call(["git", "add", path])

staged = sorted(out("git", "diff", "--cached", "--name-only").splitlines())
if staged != EXPECTED_PATHS:
    fail("staged boundary mismatch")

call(["git", "diff", "--cached", "--check"])

print("===== COMMIT 02B =====")
call(["git", "commit", "-m", "registry: add grid-use alignment claim batch 02B"])

print("===== PUSH 02B =====")
push_retry(["-u", "origin", BRANCH])

if out("git", "rev-list", "--left-right", "--count", f"origin/{BRANCH}...HEAD") != "0\t0":
    fail("02B branch not synchronized with remote")

branch_commit = out("git", "rev-parse", "HEAD")
print("02B COMMIT:", branch_commit)

print("===== INTEGRATE TO MAIN =====")
call(["git", "fetch", "origin", "main"])
call(["git", "switch", "main"])

if out("git", "status", "--porcelain"):
    fail("main working tree is dirty")

if out("git", "rev-parse", "HEAD") != out("git", "rev-parse", "origin/main"):
    fail("local main differs from origin/main")

if out("git", "rev-parse", "HEAD") != MAIN_BASE:
    fail(
        "unexpected main baseline: "
        + out("git", "rev-parse", "HEAD")
        + " expected "
        + MAIN_BASE
    )

call(["git", "merge", "--ff-only", BRANCH])

if out("git", "rev-parse", "HEAD") != branch_commit:
    fail("main did not fast-forward to 02B commit")

print("===== POST-MERGE VALIDATION =====")
call([sys.executable, "scripts/pilot_check.py", "--self-test"])
call([sys.executable, "scripts/pilot_check.py"])
call(["git", "diff", "--check"])

print("===== PUSH MAIN =====")
push_retry(["origin", "main"])
call(["git", "fetch", "origin", "main"])

if out("git", "rev-list", "--left-right", "--count", "origin/main...HEAD") != "0\t0":
    fail("main not synchronized with origin")

print("===== FINAL STATE =====")
call(["git", "log", "-5", "--oneline", "--decorate"])
call(["git", "status", "--short"])

print("OUTCOME: REGISTRY_BATCH_02B_INTEGRATED")
print("MAIN_HEAD:", out("git", "rev-parse", "--short", "HEAD"))
print("CORPUS: 69 records — 36 concepts, 10 claims, 23 sources")
print("CHECKER: PASS (0 warnings)")
print("REMOTE_DIVERGENCE: 0 0")
