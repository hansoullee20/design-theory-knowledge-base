#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REQUIRED_ACTOR_RELATIVE = [
    "data/concepts/affordance-ecological.yaml",
    "data/concepts/legibility-typeface.yaml",
    "data/concepts/readability-linguistic.yaml",
]

PF002_ROW = (
    "| PF-002 | Actor-relative locus | The original locus vocabulary could not represent "
    "properties borne by an artifact/environment relative to actor capabilities; confirmed "
    "independently by ecological affordance, typeface legibility, and linguistic readability. | "
    "concept schema / locus vocabulary | Added `actor-relative`; re-filed the three confirmed "
    "records; redefined locus as the bearer of the property using the change test. | Preserve "
    "the additive locus through the remaining pilot; actor characteristics remain tracked "
    "separately as PF-003. | resolved |"
)

def root() -> Path:
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
    except Exception:
        print("ERROR: run inside the design-theory-knowledge-base repository.")
        sys.exit(2)

def read(path: Path) -> str:
    if not path.exists():
        print(f"ERROR: required file missing: {path}")
        sys.exit(2)
    return path.read_text(encoding="utf-8")

def write_if_changed(path: Path, old: str, new: str) -> None:
    if old == new:
        print(f"UNCHANGED: {path}")
        return
    path.write_text(new, encoding="utf-8")
    print(f"UPDATED: {path}")

def verify_foundation(root: Path) -> None:
    path = root / "docs" / "PROJECT_FOUNDATION.md"
    text = read(path)
    required = [
        "- `locus` (**required**): the bearer of the property.",
        "- `actor-relative`: borne by the relation between a designed artifact/environment and an actor's capabilities;",
        "an `outcome`-, `experience`-, or `actor-relative`-locus concept",
        "| 3 | 2026-09-26 | PF-002 resolved",
    ]
    missing = [s for s in required if s not in text]
    if missing:
        print("ERROR: foundation is not in the expected PF-002-resolved state:")
        for s in missing:
            print(f"  missing: {s}")
        sys.exit(2)
    print(f"VERIFIED: {path} already contains the rev. 3 PF-002 resolution")

def verify_vocab_and_schema(root: Path) -> None:
    vocab = read(root / "vocab" / "locus.yaml")
    if not re.search(r"^\s*-\s+actor-relative\s*$", vocab, re.M):
        print("ERROR: vocab/locus.yaml does not contain actor-relative")
        sys.exit(2)
    print("VERIFIED: vocab/locus.yaml contains actor-relative")

    schema = read(root / "schema" / "concept.schema.yaml")
    if not re.search(r'^\s*-\s*["\']?actor-relative["\']?\s*$', schema, re.M):
        print("ERROR: schema/concept.schema.yaml does not contain actor-relative")
        sys.exit(2)
    print("VERIFIED: schema/concept.schema.yaml contains actor-relative")

def verify_records(root: Path) -> None:
    for rel in REQUIRED_ACTOR_RELATIVE:
        path = root / rel
        text = read(path)
        if not re.search(r"^locus:\s*\n\s*-\s+actor-relative\s*$", text, re.M):
            print(f"ERROR: {rel} is not filed as locus: [actor-relative]")
            sys.exit(2)
        print(f"VERIFIED: {rel} -> actor-relative")

def resolve_pf002(root: Path) -> None:
    path = root / "pilot" / "PILOT_FAILURE_LOG.md"
    original = read(path)
    lines = original.splitlines()
    out = []
    found = False

    for line in lines:
        if line.startswith("| PF-002 |"):
            out.append(PF002_ROW)
            found = True
        else:
            out.append(line)

    if not found:
        print("ERROR: PF-002 row not found in pilot/PILOT_FAILURE_LOG.md")
        sys.exit(2)

    # PF-003 must remain present and unresolved.
    if not any(line.startswith("| PF-003 |") for line in out):
        print("ERROR: PF-003 row not found; refusing to finalize PF-002 because the actor-characteristic issue would be lost")
        sys.exit(2)

    text = "\n".join(out).rstrip() + "\n"
    write_if_changed(path, original, text)

def fix_checker_description(root: Path) -> None:
    path = root / "scripts" / "pilot_check.py"
    if not path.exists():
        print("WARN: scripts/pilot_check.py not found; skipping description cleanup")
        return
    original = path.read_text(encoding="utf-8")
    text = original.replace(
        'description="Read-only pilot integrity checks for Design Theory Taxonomy v0.1."',
        'description="Pilot integrity checks for Design Theory Taxonomy v0.1; --fix-log performs bounded log cleanup."',
    )
    write_if_changed(path, original, text)

def run(cmd: list[str], cwd: Path) -> int:
    print("\n$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd).returncode

def main() -> None:
    r = root()

    verify_foundation(r)
    verify_vocab_and_schema(r)
    verify_records(r)
    resolve_pf002(r)
    fix_checker_description(r)

    rc1 = run([sys.executable, "scripts/pilot_check.py"], r)
    rc2 = run(["git", "diff", "--check"], r)

    print("\n===== PF-002 / PF-003 =====")
    log = read(r / "pilot" / "PILOT_FAILURE_LOG.md")
    for line in log.splitlines():
        if line.startswith("| PF-002 |") or line.startswith("| PF-003 |"):
            print(line)

    print("\n===== GIT STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=r)

    print("\n===== DIFF STAT =====")
    subprocess.run(["git", "diff", "--stat"], cwd=r)

    if rc1 or rc2:
        print("\nRESULT: finalization checks FAILED.")
        sys.exit(1)

    print("\nRESULT: PF-002 finalized successfully.")
    print("No commit was created. PF-003 remains open.")

if __name__ == "__main__":
    main()
