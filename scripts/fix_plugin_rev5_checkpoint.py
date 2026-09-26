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

path = ROOT / "docs" / "PLUGIN_TARGET_ARCHITECTURE.md"
if not path.exists():
    print("ERROR: docs/PLUGIN_TARGET_ARCHITECTURE.md not found")
    sys.exit(2)

text = path.read_text(encoding="utf-8")

if re.search(r"\brev\.\s*5\b", text, re.I):
    print("UNCHANGED: plugin architecture already references rev. 5")
elif re.search(r"\brev\.\s*4\b", text, re.I):
    text, n = re.subn(r"\brev\.\s*4\b", "rev. 5", text, count=1, flags=re.I)
    if n != 1:
        print("ERROR: could not update exactly one rev. 4 reference")
        sys.exit(2)
    path.write_text(text, encoding="utf-8")
    print("UPDATED: docs/PLUGIN_TARGET_ARCHITECTURE.md rev. 4 -> rev. 5")
else:
    print("ERROR: neither rev. 4 nor rev. 5 reference found")
    sys.exit(2)

# Verify checkpoint boundary.
plugin = path.read_text(encoding="utf-8")
foundation = (ROOT / "docs" / "PROJECT_FOUNDATION.md").read_text(encoding="utf-8")

if not re.search(r"\brev\.\s*5\b", plugin, re.I):
    print("ERROR: plugin architecture still does not reference rev. 5")
    sys.exit(1)

if "rev. 6" in foundation or "### 8.1 Structural relation semantics" in foundation:
    print("ERROR: next-phase rev. 6 relation-semantics work is present; do not checkpoint")
    sys.exit(1)

commands = [
    [sys.executable, "scripts/pilot_check.py", "--self-test"],
    [sys.executable, "scripts/pilot_check.py"],
    ["git", "diff", "--check"],
]

for cmd in commands:
    print("\n$ " + " ".join(cmd))
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc:
        print("RESULT: CHECKPOINT FIX FAILED")
        sys.exit(rc)

print("\nRESULT: CHECKPOINT REV-5 SYNC PASSED.")
print("No commit or push was performed.")
