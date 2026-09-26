#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
)

PLUGIN = ROOT / "docs" / "PLUGIN_TARGET_ARCHITECTURE.md"
FOUNDATION = ROOT / "docs" / "PROJECT_FOUNDATION.md"

CANONICAL_LINE = (
    "Foundation baseline: `docs/PROJECT_FOUNDATION.md` — foundation rev. 5"
)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(2)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


foundation = read(FOUNDATION)
plugin = read(PLUGIN)

# Authoritative checkpoint boundary: foundation must be rev. 5.
m = re.search(
    r"\*\*Status:\*\*\s*Working architecture decision record\s*\(rev\.\s*(\d+)\)",
    foundation,
    flags=re.I,
)
if not m:
    fail("could not determine PROJECT_FOUNDATION.md revision from Status line")

foundation_rev = int(m.group(1))
if foundation_rev != 5:
    fail(
        f"checkpoint requires foundation rev. 5, but local foundation is rev. {foundation_rev}"
    )

if "### 8.1 Structural relation semantics" in foundation or re.search(
    r"(?m)^\|\s*6\s*\|",
    foundation,
):
    fail("next-phase rev. 6 relation-semantics work is present; do not checkpoint")

lines = plugin.splitlines()

# Remove prior helper-generated Foundation baseline lines only.
lines = [
    line for line in lines
    if not re.match(r"^Foundation baseline:\s*", line, flags=re.I)
]

# Find first H1 and insert the exact canonical line immediately after it.
h1 = next(
    (i for i, line in enumerate(lines) if re.match(r"^#\s+\S", line)),
    None,
)
if h1 is None:
    fail("PLUGIN_TARGET_ARCHITECTURE.md has no Markdown H1")

insert_at = h1 + 1
lines[insert_at:insert_at] = ["", CANONICAL_LINE]

plugin_new = "\n".join(lines).rstrip() + "\n"

if CANONICAL_LINE not in plugin_new:
    fail("internal error: canonical foundation line was not inserted")

PLUGIN.write_text(plugin_new, encoding="utf-8")
print("UPDATED: docs/PLUGIN_TARGET_ARCHITECTURE.md")
print(CANONICAL_LINE)

print("\n===== CHECKPOINT GATES =====")
commands = (
    [sys.executable, "scripts/pilot_check.py", "--self-test"],
    [sys.executable, "scripts/pilot_check.py"],
    ["git", "diff", "--check"],
)

for cmd in commands:
    print("$ " + " ".join(cmd))
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc:
        print("RESULT: CHECKPOINT FIX FAILED")
        sys.exit(rc)

print("\n===== EXACT REVISION REFERENCE =====")
for i, line in enumerate(
    PLUGIN.read_text(encoding="utf-8").splitlines(),
    1,
):
    if line == CANONICAL_LINE:
        print(f"{i}: {line}")

print("\nRESULT: CHECKPOINT REV-5 SYNC PASSED.")
print("No commit or push was performed.")
