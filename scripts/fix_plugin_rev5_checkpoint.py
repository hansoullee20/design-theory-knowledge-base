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


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(2)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


foundation = read(FOUNDATION)
plugin = read(PLUGIN)

# Check the authoritative foundation revision first.
m = re.search(
    r"\*\*Status:\*\*\s*Working architecture decision record\s*\(rev\.\s*(\d+)\)",
    foundation,
    flags=re.I,
)
if not m:
    fail("could not determine PROJECT_FOUNDATION.md revision from its Status line")

foundation_rev = int(m.group(1))
if foundation_rev != 5:
    fail(
        f"checkpoint requires foundation rev. 5, but local foundation is rev. {foundation_rev}"
    )

original = plugin
lines = plugin.splitlines()
changed = False

# 1) Prefer an existing line explicitly mentioning PROJECT_FOUNDATION.md or
#    "foundation" near the document header. Replace/add a revision there.
candidate_indexes = []
for i, line in enumerate(lines[:80]):
    low = line.lower()
    if "project_foundation.md" in low or "project foundation" in low:
        candidate_indexes.append(i)

if candidate_indexes:
    i = candidate_indexes[0]
    line = lines[i]

    if re.search(r"\brev\.?\s*\d+\b", line, flags=re.I):
        new_line = re.sub(
            r"\brev\.?\s*\d+\b",
            "rev. 5",
            line,
            count=1,
            flags=re.I,
        )
    else:
        suffix = " — foundation rev. 5"
        new_line = line.rstrip() + suffix

    if new_line != line:
        lines[i] = new_line
        changed = True

else:
    # 2) No explicit foundation reference exists. Add one directly after the
    #    first Markdown H1, preserving the rest of the document exactly.
    insert_at = None
    for i, line in enumerate(lines):
        if re.match(r"^#\s+\S", line):
            insert_at = i + 1
            break

    if insert_at is None:
        fail(
            "PLUGIN_TARGET_ARCHITECTURE.md has neither a foundation reference "
            "nor a Markdown H1; refusing to guess an insertion point"
        )

    reference = (
        "Foundation baseline: `docs/PROJECT_FOUNDATION.md` — foundation rev. 5"
    )
    lines.insert(insert_at, "")
    lines.insert(insert_at + 1, reference)
    changed = True

plugin_new = "\n".join(lines)
if plugin.endswith("\n"):
    plugin_new += "\n"

# Verify the resulting document actually ties itself to rev. 5.
if not re.search(
    r"(?is)(project_foundation\.md|project foundation).*?rev\.\s*5",
    plugin_new,
):
    fail("could not establish a verifiable foundation rev. 5 reference")

if changed:
    PLUGIN.write_text(plugin_new, encoding="utf-8")
    print("UPDATED: docs/PLUGIN_TARGET_ARCHITECTURE.md now references foundation rev. 5")
else:
    print("UNCHANGED: docs/PLUGIN_TARGET_ARCHITECTURE.md already references foundation rev. 5")

print("\n===== FOUNDATION REFERENCES =====")
for i, line in enumerate(plugin_new.splitlines(), 1):
    low = line.lower()
    if "project_foundation.md" in low or "project foundation" in low:
        print(f"{i}: {line}")

# The checkpoint explicitly excludes rev. 6 relation-semantics work.
if re.search(r"\brev\.\s*6\b", foundation, flags=re.I) or (
    "### 8.1 Structural relation semantics" in foundation
):
    fail("next-phase rev. 6 relation-semantics work is present; do not checkpoint")

print("\n===== CHECKPOINT GATES =====")
for cmd in (
    [sys.executable, "scripts/pilot_check.py", "--self-test"],
    [sys.executable, "scripts/pilot_check.py"],
    ["git", "diff", "--check"],
):
    print("$ " + " ".join(cmd))
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc:
        print("RESULT: CHECKPOINT FIX FAILED")
        sys.exit(rc)

print("\nRESULT: CHECKPOINT REV-5 SYNC PASSED.")
print("No commit or push was performed.")
