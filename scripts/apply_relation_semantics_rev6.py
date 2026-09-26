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

FOUNDATION = ROOT / "docs" / "PROJECT_FOUNDATION.md"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(2)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, old: str, new: str) -> None:
    rel = path.relative_to(ROOT)
    if old == new:
        print(f"UNCHANGED: {rel}")
        return
    path.write_text(new, encoding="utf-8")
    print(f"UPDATED: {rel}")


def patch_foundation() -> None:
    old = read(FOUNDATION)
    text = old

    text = text.replace(
        "**Status:** Working architecture decision record (rev. 5). Decisions may be superseded; see §17.",
        "**Status:** Working architecture decision record (rev. 6). Decisions may be superseded; see §17.",
        1,
    )

    start = re.search(r"(?m)^## 8\..*$", text)
    if not start:
        fail("docs/PROJECT_FOUNDATION.md: §8 heading not found")

    end = re.search(r"(?m)^## 9\..*$", text[start.end():])
    if not end:
        fail("docs/PROJECT_FOUNDATION.md: §9 heading not found")

    sec_start = start.start()
    sec_end = start.end() + end.start()
    section = text[sec_start:sec_end]

    # Amend any old one-direction storage sentence without disturbing the rest of §8.
    lines = section.splitlines()
    amended = False
    new_lines = []
    for line in lines:
        low = line.lower()
        if "stored" in low and "direction" in low and "inverse" in low:
            new_lines.append(
                "Directional relations (`broader`, `part_of`) are stored from subject to target; "
                "inverses are derived. Symmetric relations (`related`, `opposite_of`) may be "
                "stored on either or both endpoints; the derived graph deduplicates them."
            )
            amended = True
        else:
            new_lines.append(line)

    section = "\n".join(new_lines)
    if old[sec_start:sec_end].endswith("\n"):
        section += "\n"

    subsection = """### 8.1 Structural relation semantics

Structural relations are intentionally narrow. They are ontological or navigational assertions, not substitutes for claims.

- `broader`: on concept A, lists concept B when every instance of A is an instance of B (subsumption / is-a). It is transitive, irreflexive, antisymmetric, and acyclic. Endpoints must have the same `locus`.
- `part_of`: on concept A, lists concept B when A is a proper spatial, temporal, or structural constituent of instances of B. It does not mean dimension-of, attribute-of, feature-of, role-of, cause-of, or a step that produces B. It is transitive, irreflexive, and acyclic. Same-locus endpoints are expected; a cross-locus edge requires review.
- `related`: a symmetric, non-transitive navigational relation that asserts no subsumption, mereology, causation, or opposition. It may be used when a stronger structural relation is not justified. Redundancy with claim-derived adjacency is tolerated during the v0.1 pilot and may be pruned later.
- `opposite_of`: a symmetric relation reserved for concepts defined as negations or genuine opposites on the same conceptual dimension and `locus`. Its retention in v0.1 remains subject to the FIGURE-GROUND-01 adversarial test.

Validation invariants before Taxonomy v0.1:

1. All structural relations are irreflexive.
2. `broader` and `part_of` are acyclic.
3. `broader` endpoints must have the same `locus`; cross-locus `part_of` is a warning requiring review.
4. The same concept pair cannot simultaneously be linked by both `broader` and `part_of`.

`broader` and `part_of` are ontological assertions and should be supported by the same source discipline as definitions. `related` is navigational. Relation inverses are derived rather than treated as separate relation types.
"""

    if "### 8.1 Structural relation semantics" not in section:
        section = section.rstrip() + "\n\n" + subsection + "\n"

    # If no old sentence was found, the new subsection still supplies the authoritative storage rule.
    if not amended and "stored from subject to target" not in section:
        fail("could not establish structural-relation storage semantics in §8")

    text = text[:sec_start] + section + text[sec_end:]

    rev6 = (
        "| 6 | 2026-09-26 | Freeze-readiness relation contract: defined narrow semantics "
        "for `broader`, `part_of`, `related`, and provisional `opposite_of`; "
        "added irreflexivity, acyclicity, locus-compatibility, and broader/part-of "
        "exclusivity invariants; symmetric relations may be stored on either or both "
        "endpoints with derived-graph deduplication. |"
    )

    if rev6 not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for line in lines:
            out.append(line)
            if line.startswith("| 5 | 2026-09-26 |"):
                out.append(rev6)
                inserted = True
        if not inserted:
            fail("docs/PROJECT_FOUNDATION.md: rev. 5 decision-log row not found")
        text = "\n".join(out).rstrip() + "\n"

    write_if_changed(FOUNDATION, old, text)


def main() -> None:
    print("===== PRECHECK =====")
    if subprocess.run(
        [sys.executable, "scripts/pilot_check.py"],
        cwd=ROOT,
    ).returncode:
        fail("baseline checker failed")

    patch_foundation()

    print("\n===== SELF TEST =====")
    rc1 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py", "--self-test"],
        cwd=ROOT,
    ).returncode

    print("\n===== REAL CORPUS =====")
    rc2 = subprocess.run(
        [sys.executable, "scripts/pilot_check.py"],
        cwd=ROOT,
    ).returncode

    print("\n===== DIFF CHECK =====")
    rc3 = subprocess.run(
        ["git", "diff", "--check"],
        cwd=ROOT,
    ).returncode

    print("\n===== FOUNDATION RELATION CONTRACT =====")
    text = read(FOUNDATION)
    for needle in (
        "### 8.1 Structural relation semantics",
        "- `broader`:",
        "- `part_of`:",
        "- `related`:",
        "- `opposite_of`:",
        "| 6 | 2026-09-26 |",
    ):
        if needle not in text:
            fail(f"foundation relation contract missing: {needle}")
        print(f"PASS: {needle}")

    print("\n===== GIT STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=ROOT)

    print("\n===== DIFF STAT =====")
    subprocess.run(["git", "diff", "--stat"], cwd=ROOT)

    if rc1 or rc2 or rc3:
        print("\nRESULT: RELATION-SEMANTICS-REV6 FAILED.")
        sys.exit(1)

    print("\nRESULT: RELATION-SEMANTICS-REV6 PASSED.")
    print("No GRID-STRUCTURE-01 or FIGURE-GROUND-01 records were minted.")
    print("No commit was created.")


if __name__ == "__main__":
    main()
