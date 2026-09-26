#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def repo_root() -> Path:
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
    except Exception:
        print("ERROR: run inside the repository.")
        sys.exit(2)

def main() -> None:
    root = repo_root()
    path = root / "docs" / "PROJECT_FOUNDATION.md"
    if not path.exists():
        print(f"ERROR: missing {path}")
        sys.exit(2)

    lines = path.read_text(encoding="utf-8").splitlines()

    print("===== HEADINGS AROUND SECTION 5 =====")
    for i, line in enumerate(lines, 1):
        if line.startswith("## 5.") or line.startswith("### 5."):
            print(f"{i:4}: {line}")

    print("\n===== SECTION 5.3 EXACT TEXT =====")
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.startswith("### 5.3"):
            start = i
            continue
        if start is not None and i > start and line.startswith("### 5.4"):
            end = i
            break

    if start is None:
        print("ERROR: section 5.3 heading not found.")
        sys.exit(1)

    if end is None:
        end = len(lines)

    for i in range(start, end):
        print(f"{i+1:4}: {lines[i]}")

    print("\n===== LOCUS-LIKE LINES WITH repr() =====")
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if "locus" in low or "artifact" in low or "experience" in low or "actor-relative" in low:
            print(f"{i:4}: {line!r}")

    print("\nRESULT: diagnostic only; no files changed.")

if __name__ == "__main__":
    main()
