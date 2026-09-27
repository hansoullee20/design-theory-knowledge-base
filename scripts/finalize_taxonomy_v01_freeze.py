#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip())

EXPECTED_COUNTS = (54, 28, 9, 17)


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        fail(f"missing required file: {rel}")
    return p.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    p.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        fail(f"{label}: expected exactly 1 match, found {n}")
    return text.replace(old, new, 1)


def counts():
    concepts = list((ROOT / "data/concepts").glob("*.yaml"))
    claims = list((ROOT / "data/claims").glob("*.yaml"))
    sources = list((ROOT / "data/sources").glob("*.yaml"))
    return (
        len(concepts) + len(claims) + len(sources),
        len(concepts),
        len(claims),
        len(sources),
    )


def run(*args: str) -> str:
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode:
        fail(f"command failed ({p.returncode}): {' '.join(args)}")
    return p.stdout


def assert_live_terms_clean() -> None:
    roots = [
        ROOT / "data",
        ROOT / "schema",
        ROOT / "scripts",
        ROOT / "vocab",
    ]
    bad = []

    broader_re = re.compile(r"^\s*broader\s*:", re.MULTILINE)
    removed_key_re = re.compile(
        r"^\s*(?:AFFECTS|ENABLES)\s*:",
        re.MULTILINE,
    )

    for base in roots:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".yaml", ".yml", ".py", ".md", ".txt"}:
                continue

            text = path.read_text(encoding="utf-8")

            if "opposite_of" in text:
                bad.append(f"{path.relative_to(ROOT)}: opposite_of")
            if broader_re.search(text):
                bad.append(f"{path.relative_to(ROOT)}: broader key")
            if removed_key_re.search(text):
                bad.append(f"{path.relative_to(ROOT)}: removed structural key")

    if bad:
        fail("stale live structural term(s): " + "; ".join(bad))


print("===== TAXONOMY v0.1 FREEZE FINALIZATION =====")
print("===== PRECONDITIONS =====")

branch = subprocess.check_output(
    ["git", "branch", "--show-current"],
    cwd=ROOT,
    text=True,
).strip()
if branch != "main":
    fail(f"expected main, got {branch!r}")

foundation = read("docs/PROJECT_FOUNDATION.md")
if "(rev. 11)" not in foundation:
    fail("expected Foundation rev. 11")

if counts() != EXPECTED_COUNTS:
    fail(
        f"expected corpus {EXPECTED_COUNTS}, got {counts()}"
    )

failure_log = read("pilot/PILOT_FAILURE_LOG.md")
open_pf_lines = [
    line for line in failure_log.splitlines()
    if re.search(r"\bPF-\d+\b", line)
    and re.search(r"\bopen\b", line, flags=re.I)
]
if len(open_pf_lines) != 1 or "PF-001" not in open_pf_lines[0]:
    fail(
        "expected PF-001 to be the sole open pilot failure; found: "
        + repr(open_pf_lines)
    )

pilot_records = read("pilot/PILOT_RECORDS.md")
for required in (
    "## GRID-STRUCTURE-01",
    "## FIGURE-GROUND-01",
    "## CARD-SORTING-01",
    "## WCAG-01-RETEST",
    "## PF-007-RESOLUTION-01 / LEFT-ALIGNMENT-01-RETEST",
    "## WHITESPACE-DENSITY-01",
    "## DEPRECATION-01",
):
    if required not in pilot_records:
        fail(f"missing required pilot record: {required}")

if "## TAXONOMY-v0.1-FREEZE-AUDIT" in pilot_records:
    fail("freeze audit already finalized")

assert_live_terms_clean()

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
pass_count = sum(
    1 for line in out.splitlines()
    if line.startswith("PASS:")
)
if pass_count != 28:
    fail(f"expected 28 passing self-tests, got {pass_count}")
if "SELF-TEST RESULT: PASS" not in out:
    fail("self-test suite did not pass")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("canonical checker is not clean")

run("git", "diff", "--check")

print("PRECONDITIONS: PASS")

print("\n===== RECONCILE HISTORICAL DEPRECATION TODO =====")

rel = "pilot/PILOT_RECORDS.md"
text = read(rel)

old = (
    "- [ ] DEPRECATION-01 must decide whether references to deprecated records "
    "warn, fail, or resolve through `replaced_by`; no rule is activated "
    "before that pilot."
).replace("`", chr(96))

new = (
    "- [x] DEPRECATION-01 later resolved the lifecycle rule: active references "
    "to deprecated concepts remain valid with a review warning; replacement "
    "integrity is enforced. See `## DEPRECATION-01` below."
).replace("`", chr(96))

text = replace_once(
    text,
    old,
    new,
    "historical DEPRECATION-01 TODO",
)

freeze_block = '''
## TAXONOMY-v0.1-FREEZE-AUDIT

- [x] Foundation pre-freeze architecture: rev. 11.
- [x] Corpus: 54 records — 28 concepts, 9 claims, 17 sources.
- [x] Permanent self-test suite: 28 PASS.
- [x] Canonical checker: PASS with 0 warnings.
- [x] `git diff --check`: clean.
- [x] No removed structural term remains live under `data/`, `schema/`, `scripts/`, or `vocab/`.
- [x] Required pilot stress-test set is accounted for through the recorded pilot sequence.
- [x] PF-006 and PF-007 are resolved.
- [x] DEPRECATION-01 is resolved and executable lifecycle invariants are active.
- [x] PF-001 is the sole intentionally open pilot finding and is explicitly deferred to the immediate post-freeze provenance/locator phase; it does not change taxonomy semantics.
- [x] No canonical deprecated record exists at the freeze checkpoint.
- [x] No non-empty `replaced_by` exists at the freeze checkpoint.
- [x] Freeze verdict: `PASS`.
- [x] Taxonomy v0.1 is ready for a dedicated checkpoint commit/tag before PF-001 work begins.
'''.replace("`", chr(96))

text = text.rstrip() + "\n\n" + freeze_block.strip() + "\n"
write(rel, text)

print("\n===== FOUNDATION FREEZE MARKER =====")

rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)

text = replace_once(
    text,
    "**Status:** Working architecture decision record (rev. 11). Decisions may be superseded; see §17.",
    (
        "**Status:** Taxonomy v0.1 frozen architecture checkpoint (rev. 12). "
        "Further taxonomy/schema changes require a new post-freeze revision; see §17."
    ),
    "foundation freeze status",
)

row11_pattern = re.compile(
    r"^\| 11 \| 2026-09-27 \| DEPRECATION-01 lifecycle hardening:.*\|$",
    re.MULTILINE,
)
matches = row11_pattern.findall(text)
if len(matches) != 1:
    fail(
        "foundation decision row 11: expected exactly 1 match, "
        f"found {len(matches)}"
    )

row11 = matches[0]
row12 = (
    row11
    + "\n| 12 | 2026-09-27 | TAXONOMY-v0.1-FREEZE-AUDIT: all freeze gates passed "
      "at 54 records (28 concepts, 9 claims, 17 sources), 28 permanent self-tests, "
      "checker PASS with 0 warnings, and clean diff hygiene; required pilot cases "
      "were accounted for; PF-001 remains the sole intentionally deferred post-freeze "
      "provenance/locator item; Taxonomy v0.1 declared frozen before any PF-001 mutation. |"
)

text = text.replace(row11, row12, 1)
write(rel, text)

print("\n===== FINAL VALIDATION =====")

if counts() != EXPECTED_COUNTS:
    fail(
        f"record counts changed during finalization: {counts()}"
    )

assert_live_terms_clean()

out = run(sys.executable, "scripts/pilot_check.py", "--self-test")
pass_count = sum(
    1 for line in out.splitlines()
    if line.startswith("PASS:")
)
if pass_count != 28 or "SELF-TEST RESULT: PASS" not in out:
    fail("post-finalization self-test mismatch")

out = run(sys.executable, "scripts/pilot_check.py")
if "RESULT: PASS (0 warning(s))" not in out:
    fail("post-finalization checker is not clean")

run("git", "diff", "--check")

foundation = read("docs/PROJECT_FOUNDATION.md")
if "Taxonomy v0.1 frozen architecture checkpoint (rev. 12)" not in foundation:
    fail("freeze status marker missing")
if "| 12 | 2026-09-27 | TAXONOMY-v0.1-FREEZE-AUDIT:" not in foundation:
    fail("freeze decision row missing")

pilot_records = read("pilot/PILOT_RECORDS.md")
if "## TAXONOMY-v0.1-FREEZE-AUDIT" not in pilot_records:
    fail("freeze audit record missing")
if old in pilot_records:
    fail("stale DEPRECATION-01 TODO still present")

print("\n===== STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== RESULT =====")
print("OUTCOME: READY_FOR_FREEZE_COMMIT")
print("FREEZE VERDICT: PASS")
print("Foundation: rev. 12")
print("Taxonomy: v0.1 FROZEN")
print("COUNTS: 54 records — 28 concepts, 9 claims, 17 sources")
print("SELF-TESTS: 28 PASS")
print("CHECKER: PASS (0 warnings)")
print("PF-001: OPEN, intentionally deferred post-freeze")
print("Historical DEPRECATION-01 TODO: reconciled")
print("No taxonomy/schema semantics changed by freeze finalization.")
print("No commit, tag, or push performed.")
