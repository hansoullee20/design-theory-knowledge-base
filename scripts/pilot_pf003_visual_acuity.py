#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
)

EXPECTED_UNTRACKED_EXACT = {
    "docs/PLUGIN_TARGET_ARCHITECTURE.md",
    "scripts/pilot_check.py",
}
EXPECTED_UNTRACKED_PREFIXES = (
    "data/",
    "pilot/",
)

SOURCE_ID = "source:legge-bigelow-2011-print-size"
EXPECTED_LOCI = {
    "artifact",
    "actor-relative",
    "experience",
    "outcome",
    "practice",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(2)


def run(cmd: list[str], **kwargs):
    return subprocess.run(cmd, cwd=ROOT, **kwargs)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def get_untracked() -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    )
    return sorted(
        item.decode("utf-8")
        for item in out.split(b"\0")
        if item
    )


def untracked_allowed(path: str) -> bool:
    if path in EXPECTED_UNTRACKED_EXACT:
        return True
    return any(path.startswith(prefix) for prefix in EXPECTED_UNTRACKED_PREFIXES)


def audit_untracked() -> None:
    print("===== UNTRACKED AUDIT =====")
    paths = get_untracked()

    if not paths:
        print("(none)")
    else:
        for path in paths:
            print(path)

    unexpected = [path for path in paths if not untracked_allowed(path)]
    unsafe = []

    for rel in paths:
        path = ROOT / rel
        if path.is_symlink():
            unsafe.append(f"{rel}: symlink")
            continue
        if path.is_file() and path.stat().st_size > 2_000_000:
            unsafe.append(f"{rel}: larger than 2 MB")

    if unexpected:
        print("\nUNEXPECTED UNTRACKED PATHS:")
        for path in unexpected:
            print(f"  - {path}")

    if unsafe:
        print("\nUNSAFE UNTRACKED PATHS:")
        for item in unsafe:
            print(f"  - {item}")

    if unexpected or unsafe:
        fail("untracked audit failed; PF-003 was not touched")

    print(
        f"PASS: {len(paths)} untracked file(s), all inside the expected pilot tree."
    )


def find_source() -> tuple[str, dict]:
    source_dir = ROOT / "data" / "sources"
    candidates = []

    for path in sorted(source_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        rid = data.get("id")
        if rid == SOURCE_ID:
            return str(path.relative_to(ROOT)), data

        if isinstance(rid, str) and "legge" in rid.lower():
            candidates.append((str(path.relative_to(ROOT)), rid))

    print(f"ERROR: exact source {SOURCE_ID!r} not found.")
    if candidates:
        print("Legge-like source candidates:")
        for rel, rid in candidates:
            print(f"  - {rel}: {rid}")
    sys.exit(2)


def load_locus_values() -> list[str]:
    data = yaml.safe_load(read("vocab/locus.yaml"))

    if not isinstance(data, dict) or not isinstance(data.get("values"), list):
        fail("vocab/locus.yaml does not contain a 'values' list")

    values = data["values"]
    if set(values) != EXPECTED_LOCI:
        fail(
            "PF-003 test requires the pre-decision locus vocabulary. "
            f"Expected {sorted(EXPECTED_LOCI)!r}; got {values!r}"
        )

    if "actor" in values:
        fail("actor locus already exists; PF-003 test would no longer be adversarial")

    return values


def update_pf003() -> None:
    rel = "pilot/PILOT_FAILURE_LOG.md"
    text = read(rel)
    lines = text.splitlines()

    replacement = (
        "| PF-003 | Actor-characteristic concepts have no locus | "
        "The visual-acuity stress test confirms that a source-defined actor "
        "capability cannot be honestly represented by artifact, actor-relative, "
        "experience, outcome, or practice. | locus vocabulary | "
        "Test completed without changing vocab/locus.yaml: critical print size "
        "fits actor-relative, while visual acuity has no valid current locus. "
        "No canonical visual-acuity record or dependent claim was minted. | "
        "Evaluate an actor locus versus another explicit representation of "
        "actor-characteristic constructs before canonicalizing visual acuity. | "
        "confirmed |"
    )

    found = False
    out = []

    for line in lines:
        if line.startswith("| PF-003 |"):
            out.append(replacement)
            found = True
        else:
            out.append(line)

    if not found:
        fail("PF-003 row not found in pilot/PILOT_FAILURE_LOG.md")

    write(rel, "\n".join(out).rstrip() + "\n")


def write_report(source_rel: str) -> None:
    bt = chr(96)

    report = f"""# PF-003 Visual-Acuity Stress Test

Date: 2026-09-26

## Purpose

Test whether an actor-characteristic construct can be represented honestly by
the current {bt}locus{bt} vocabulary without first adding an {bt}actor{bt} value.

The vocabulary was held fixed during the test:

- {bt}artifact{bt}
- {bt}actor-relative{bt}
- {bt}experience{bt}
- {bt}outcome{bt}
- {bt}practice{bt}

## Source used

Canonical source record: {bt}{SOURCE_ID}{bt}

Local source record: {bt}{source_rel}{bt}

Legge & Bigelow (2011), *Does print size matter for reading? A review of
findings from vision science and typography*, Journal of Vision 11(5):8.

Relevant source passage is on article pp. 6–7. The paper distinguishes critical
print size from letter acuity and reading acuity. It defines critical print size
as the smallest character size for which reading can occur at maximum speed,
defines letter acuity by the smallest angular size for identifying unrelated
letters with unconstrained viewing time, and reports that critical print size
is at least twice acuity-letter size for normally sighted readers, with a larger
difference often observed in low vision.

## Candidate classification

### visual acuity

Bearer/change-test result:

- not {bt}artifact{bt}: it is not borne by the designed artifact/environment;
- not {bt}actor-relative{bt}: the construct is an actor capability itself, not a
  property borne by the artifact–actor relation;
- not {bt}experience{bt}: under rev. 4, experience covers perceptual, cognitive,
  or affective state, whereas visual acuity is being represented here as a
  relatively stable visual capability/trait;
- not {bt}outcome{bt}: the construct is not an episode or consequence of use;
- not {bt}practice{bt}: it is not an activity of designing, researching, or
  evaluating.

Result: **no current locus fits without semantic distortion.**

### critical print size

Critical print size is defined relative to reading performance for a reader and
a text stimulus. Changing relevant reader capability or stimulus conditions can
change the threshold. Under the current bearer definition this is a defensible
{bt}actor-relative{bt} construct.

## Claim test

The originally proposed claim
{bt}visual-acuity-influences-critical-print-size{bt} was **not minted**.

Reason: the Legge–Bigelow review clearly distinguishes and quantitatively relates
acuity size and critical print size, but this pilot source alone does not justify
silently converting that relationship into the project's causal-looking
{bt}influences{bt} predicate. Likewise, {bt}decreases{bt} would be ambiguous until
the acuity measure and numeric direction are fixed.

This is an evidence/proposition issue, not an ontology workaround.

## Result

**PF-003 CONFIRMED.**

The test exposes a genuine representation gap for actor-characteristic concepts.
No change was made to {bt}vocab/locus.yaml{bt}, and no knowingly misclassified
canonical record was created.

The next ontology decision is whether to add an {bt}actor{bt} locus or represent
actor-characteristic constructs through another explicit structure while
preserving the bearer semantics of {bt}locus{bt}.
"""

    write("pilot/PF003_VISUAL_ACUITY_TEST.md", report)


def main() -> None:
    audit_untracked()

    print("\n===== PRE-TEST VALIDATION =====")
    rc = run([sys.executable, "scripts/pilot_check.py"])
    if rc.returncode:
        fail("baseline validator failed; PF-003 was not touched")

    source_rel, _ = find_source()
    print(f"VERIFIED SOURCE: {source_rel} -> {SOURCE_ID}")

    loci = load_locus_values()
    print("VERIFIED LOCUS VOCAB:", ", ".join(loci))
    print("VERIFIED: no actor locus exists")

    print("\n===== PF-003 CLASSIFICATION =====")
    print("visual-acuity -> NO CURRENT LOCUS FITS")
    print("critical-print-size -> actor-relative")
    print(
        "visual-acuity-influences-critical-print-size -> NOT MINTED "
        "(source/proposition direction not sufficiently fixed)"
    )

    write_report(source_rel)
    update_pf003()

    print("\n===== POST-TEST VALIDATION =====")
    rc1 = run([sys.executable, "scripts/pilot_check.py"])
    rc2 = run(["git", "diff", "--check"])

    print("\n===== LOCUS IMMUTABILITY CHECK =====")
    loci_after = load_locus_values()
    if loci_after != loci:
        fail("vocab/locus.yaml changed during PF-003 test")
    print("PASS: vocab/locus.yaml unchanged")

    print("\n===== PF-003 ROW =====")
    for line in read("pilot/PILOT_FAILURE_LOG.md").splitlines():
        if line.startswith("| PF-003 |"):
            print(line)

    print("\n===== GIT STATUS =====")
    run(["git", "status", "--short"])

    print("\n===== DIFF STAT =====")
    run(["git", "diff", "--stat"])

    if rc1.returncode or rc2.returncode:
        print("\nRESULT: PF003-VISUAL-ACUITY-01 FAILED validation.")
        sys.exit(1)

    print("\nRESULT: PF003-VISUAL-ACUITY-01 PASSED.")
    print("PF-003 is CONFIRMED, not resolved.")
    print("No actor locus was added.")
    print("No visual-acuity, critical-print-size, or dependent claim record was minted.")
    print("No commit was created.")


if __name__ == "__main__":
    main()
