#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import subprocess

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.")
    sys.exit(2)

def repo_root() -> Path:
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
    except Exception:
        print("ERROR: run inside the repository.")
        sys.exit(2)

def walk(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + (str(k),)
            if k == "locus":
                print("LOCUS_KEY_PATH:", " -> ".join(p))
                print("LOCUS_VALUE:", repr(v))
            if k == "enum":
                vals = v if isinstance(v, list) else []
                if any(x in vals for x in ("artifact", "experience", "outcome", "practice", "actor-relative")):
                    print("ENUM_PATH:", " -> ".join(p))
                    print("ENUM_VALUE:", repr(v))
            yield from walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + (f"[{i}]",))

def main():
    root = repo_root()
    path = root / "schema" / "concept.schema.yaml"
    if not path.exists():
        print(f"ERROR: missing {path}")
        sys.exit(2)

    text = path.read_text(encoding="utf-8")
    print("===== RAW MATCHES =====")
    for n, line in enumerate(text.splitlines(), 1):
        if "locus" in line or "artifact" in line or "experience" in line or "outcome" in line or "practice" in line:
            print(f"{n:4}: {line}")

    print("\n===== YAML STRUCTURE =====")
    try:
        data = yaml.safe_load(text)
    except Exception as e:
        print(f"YAML PARSE ERROR: {e}")
        sys.exit(1)

    found_locus = False

    def visit(obj, path=()):
        nonlocal found_locus
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = path + (str(k),)
                if k == "locus":
                    found_locus = True
                    print("LOCUS_KEY_PATH:", " -> ".join(p))
                    print("LOCUS_VALUE:")
                    print(yaml.safe_dump(v, sort_keys=False).rstrip())
                if k == "enum" and isinstance(v, list) and any(
                    x in v for x in ("artifact", "experience", "outcome", "practice", "actor-relative")
                ):
                    print("RELATED_ENUM_PATH:", " -> ".join(p))
                    print("RELATED_ENUM_VALUE:", v)
                visit(v, p)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                visit(v, path + (f"[{i}]",))

    visit(data)

    if not found_locus:
        print("\nRESULT: no YAML key literally named 'locus' exists in this schema.")
        print("This likely means locus is constrained through a $ref, allOf/oneOf, or another indirection.")
    else:
        print("\nRESULT: locus structure found. No files changed.")

if __name__ == "__main__":
    main()
