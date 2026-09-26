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

BT = chr(96)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(2)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    old = path.read_text(encoding="utf-8")
    if old == text:
        print(f"UNCHANGED: {rel}")
        return
    path.write_text(text, encoding="utf-8")
    print(f"UPDATED: {rel}")


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def replace_top_level_field(rel: str, key: str, rendered_value: str) -> None:
    text = read(rel)
    lines = text.splitlines(keepends=True)
    start = None
    end = None

    for i, line in enumerate(lines):
        if re.match(rf"^{re.escape(key)}:", line):
            start = i
            break

    if start is None:
        fail(f"{rel}: top-level field {key!r} not found")

    end = len(lines)
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_]+:", line):
            end = i
            break

    newline = "\n" if lines[start].endswith("\n") else ""
    replacement = f"{key}: {rendered_value}{newline}"
    new_lines = lines[:start] + [replacement] + lines[end:]
    write(rel, "".join(new_lines))


def require_contains(rel: str, needle: str) -> None:
    if needle not in read(rel):
        fail(f"{rel}: expected text not found: {needle}")


# ------------------------------------------------------------------
# B1 — stale PF-002 commentary
# ------------------------------------------------------------------

replace_top_level_field(
    "data/concepts/legibility-typeface.yaml",
    "notes",
    yaml_quote(
        "This sense concerns reader-relative typeface legibility. "
        "Artifact-side properties such as x-height, aperture, stroke form, "
        "and spacing are separate concepts rather than definitions of legibility."
    ),
)

replace_top_level_field(
    "data/concepts/readability-linguistic.yaml",
    "notes",
    yaml_quote(
        "This sense concerns reader-relative linguistic readability. "
        "Artifact-side textual properties used by readability formulas remain "
        "separate concepts or measurable variables."
    ),
)

replace_top_level_field(
    "data/concepts/affordance-ecological.yaml",
    "notes",
    yaml_quote(
        "Ecological affordance is distinct from perceived affordance; "
        "perception is not constitutive of the ecological affordance."
    ),
)

text = read("pilot/PILOT_RECORDS.md")
cleaned = []
for line in text.splitlines():
    if "legibility" in line.lower() or "readability" in line.lower():
        line = re.sub(
            r"\s*\([^)]*(?:forced|knowingly)[^)]*\)",
            "",
            line,
            flags=re.I,
        )
        line = re.sub(
            r"\s+—[^\n]*(?:forced|knowingly)[^\n]*",
            "",
            line,
            flags=re.I,
        )
    cleaned.append(line)
write("pilot/PILOT_RECORDS.md", "\n".join(cleaned).rstrip() + "\n")


# ------------------------------------------------------------------
# B2 — artifact definitions: intended purpose, not achieved effect
# ------------------------------------------------------------------

replace_top_level_field(
    "data/concepts/signifier.yaml",
    "definition",
    yaml_quote(
        "A perceptible cue in an artifact that indicates where or how an action can be performed."
    ),
)

replace_top_level_field(
    "data/concepts/signifier.yaml",
    "notes",
    yaml_quote(
        "Paraphrases Norman's functional account while keeping achieved effects "
        "on an actor in claim records."
    ),
)

replace_top_level_field(
    "data/concepts/hierarchy-specified.yaml",
    "definition",
    yaml_quote(
        "An ordering of relative importance encoded in a visual artifact through "
        "differences such as size, position, color, contrast, or other visual treatment."
    ),
)

replace_top_level_field(
    "data/concepts/affordance-ecological.yaml",
    "disciplines",
    "[]",
)


# ------------------------------------------------------------------
# B3 — Foundation rev. 4
# ------------------------------------------------------------------

rel = "docs/PROJECT_FOUNDATION.md"
text = read(rel)

text = text.replace(
    "**Status:** Working architecture decision record (rev. 3). Decisions may be superseded; see §17.",
    "**Status:** Working architecture decision record (rev. 4). Decisions may be superseded; see §17.",
    1,
)

rider = (
    "Classify the thing, not its function: an artifact-locus definition may "
    "state the artifact element's intended purpose, but it must not define "
    "the concept by an achieved effect on an actor; achieved effects are claims."
)

if rider not in text:
    marker = (
        "Actor characteristics themselves are not assigned a locus by this amendment; "
        "that open issue is tracked separately in the pilot."
    )
    if marker not in text:
        fail("PROJECT_FOUNDATION.md: PF-002 locus paragraph anchor not found")
    text = text.replace(marker, marker + "\n\n" + rider, 1)

skill_step = (
    "8a. Generate the reasoning-skill doctrine from §5/§8/§9 and "
    + BT + "vocab/" + BT
    + " (a view; non-canonical; carries the canon commit/tag)."
)

if skill_step not in text:
    match = re.search(
        r"(?m)^(8\.\s+Record structural relations;[^\n]*)$",
        text,
    )
    if not match:
        fail("PROJECT_FOUNDATION.md: §12 step 8 not found")
    text = text[:match.end()] + "\n" + skill_step + text[match.end():]

claim_rule = (
    "- A claim's ID names its proposition. A material change to the proposition "
    "— including a predicate change such as "
    + BT + "increases" + BT + " → " + BT + "influences" + BT
    + " — creates a new claim; the old claim becomes "
    + BT + "record_status: deprecated" + BT + " with "
    + BT + "replaced_by" + BT
    + " pointing to the successor. Editing "
    + BT + "statement" + BT + " wording, "
    + BT + "scope" + BT + ", or "
    + BT + "sources" + BT
    + " without changing the proposition keeps the ID."
)

if claim_rule not in text:
    marker = "- IDs are immutable and never reused. Changing a label never changes the ID."
    if marker not in text:
        fail("PROJECT_FOUNDATION.md: §15 immutable-ID anchor not found")
    text = text.replace(marker, marker + "\n" + claim_rule, 1)

rev4 = (
    "| 4 | 2026-09-26 | Freeze-readiness corrections: locus change-test rider "
    "distinguishes artifact purpose from achieved actor effects; claim IDs now "
    "name propositions and material predicate changes create successor claims; "
    "generated reasoning-skill doctrine is explicitly a non-canonical, "
    "versioned view of foundation and vocabularies. |"
)

if rev4 not in text:
    lines = text.splitlines()
    output = []
    inserted = False
    for line in lines:
        output.append(line)
        if line.startswith("| 3 | 2026-09-26 |"):
            output.append(rev4)
            inserted = True
    if not inserted:
        fail("PROJECT_FOUNDATION.md: §17 rev. 3 row not found")
    text = "\n".join(output).rstrip() + "\n"

write(rel, text)


# ------------------------------------------------------------------
# B4 — JSON Schema title cleanup
# ------------------------------------------------------------------

for rel in (
    "schema/concept.schema.yaml",
    "schema/claim.schema.yaml",
    "schema/source.schema.yaml",
):
    text = read(rel)
    text = re.sub(r"(?m)^\$title:", "title:", text)
    write(rel, text)


# ------------------------------------------------------------------
# B6 — Runtime contract
# ------------------------------------------------------------------

rel = "docs/PLUGIN_TARGET_ARCHITECTURE.md"
text = read(rel)

text = text.replace("validate_record(yaml)", "validate_record(record)")

head, sep, tail = text.partition("\n\n")
head = re.sub(r"\brev\.\s*[23]\b", "rev. 4", head, count=1, flags=re.I)
text = head + (sep + tail if sep else "")

runtime_addendum = """## Canon version and proposal invariants

- `proposals/` is non-canonical. It is excluded from canonical traversal and retrieval, must pass `validate_record(record)` before review, and is never auto-merged into canonical data.
- Retrieval exposes each record's `schema_version`.
- Generated reasoning-skill doctrine records the Git commit or taxonomy tag from which it was generated, so doctrine and retrieved canonical data cannot silently drift across versions.
"""

if "## Canon version and proposal invariants" not in text:
    text = text.rstrip() + "\n\n" + runtime_addendum

write(rel, text)


# ------------------------------------------------------------------
# B7 — Competency questions
# ------------------------------------------------------------------

rel = "docs/COMPETENCY_QUESTIONS.md"
text = read(rel)


def replace_question(text: str, number: int, replacement: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{number}\.\s+.*?(?=^\d+\.\s+|^##\s+|\Z)"
    )
    match = pattern.search(text)
    if not match:
        fail(f"COMPETENCY_QUESTIONS.md: CQ{number} not found")
    return text[:match.start()] + replacement.rstrip() + "\n" + text[match.end():]


text = replace_question(
    text,
    28,
    "28. Can it represent the F-pattern as a claim whose "
    + BT + "scope" + BT
    + " states its contextual limits? "
    "(Contested status is an evidence-phase property.)",
)

text = replace_question(
    text,
    32,
    "32. Can a reasoning session retrieve only the records relevant to its "
    "current reasoning step within a bounded retrieval budget, without loading "
    "the knowledge base wholesale? (Post-freeze runtime verification; no runtime "
    "exists in v0.1.)",
)

cq33 = (
    "33. Can candidate artifact-level causes of an experience- or outcome-locus "
    "concept be retrieved by inverse claim lookup (claims whose object is that "
    "concept), without any diagnosis field on the concept?"
)

if not re.search(r"(?m)^33\.\s+", text):
    match = re.search(r"(?ms)^32\.\s+.*?(?=^\d+\.\s+|^##\s+|\Z)", text)
    if not match:
        fail("COMPETENCY_QUESTIONS.md: rewritten CQ32 not found")
    insertion = match.end()
    text = text[:insertion] + "\n" + cq33 + "\n" + text[insertion:]

write(rel, text)


# ------------------------------------------------------------------
# B8 — Pilot governance rules
# ------------------------------------------------------------------

rel = "pilot/PILOT_FAILURE_LOG.md"
text = read(rel)

governance = """Pilot governance during Taxonomy v0.1:
- `disciplines` is not populated merely because the field exists; leave it empty unless the pilot specifically tests disciplinary classification.
- Canonical `notes` contains record content only. Pilot rationale, temporary workarounds, and migration commentary belong in this failure log.
- A mechanically created `perceived-X` concept requires a source that independently defines or operationalizes the perceived construct; do not create perceived twins by naming convention alone.
"""

if "Pilot governance during Taxonomy v0.1:" not in text:
    marker = "Do not silently work around a schema problem."
    if marker not in text:
        fail("PILOT_FAILURE_LOG.md: governance insertion anchor not found")
    text = text.replace(marker, marker + "\n\n" + governance.rstrip(), 1)

write(rel, text)


# ------------------------------------------------------------------
# Pre-cleanup acceptance gates
# ------------------------------------------------------------------

print("\n===== SELF TEST =====")
self_test = subprocess.run(
    [sys.executable, "scripts/pilot_check.py", "--self-test"],
    cwd=ROOT,
)

print("\n===== REAL CORPUS =====")
corpus = subprocess.run(
    [sys.executable, "scripts/pilot_check.py"],
    cwd=ROOT,
)

print("\n===== DIFF CHECK =====")
diff_check = subprocess.run(
    ["git", "diff", "--check"],
    cwd=ROOT,
)

if self_test.returncode or corpus.returncode or diff_check.returncode:
    print("\nRESULT: BLOCKING-CORRECTIONS-01 FAILED validation.")
    print("Obsolete helper scripts were NOT deleted.")
    sys.exit(1)


# ------------------------------------------------------------------
# B5 — remove obsolete one-shot helpers only after successful validation
# ------------------------------------------------------------------

patterns = (
    "pilot_add_*.py",
    "pilot_resolve_*.py",
    "pilot_finalize_*.py",
    "diagnose_*.py",
)

removed = []
scripts = ROOT / "scripts"

for pattern in patterns:
    for path in scripts.glob(pattern):
        if path.name == "pilot_check.py":
            continue
        path.unlink()
        removed.append(path.name)

self_path = scripts / "apply_blocking_corrections_01.py"
if self_path.exists():
    self_path.unlink()
    removed.append(self_path.name)

print("\n===== SCRIPT CLEANUP =====")
for name in sorted(set(removed)):
    print(f"REMOVED: scripts/{name}")

remaining = sorted(
    p.name for p in scripts.iterdir()
    if p.is_file()
)
print("REMAINING:", ", ".join(remaining) if remaining else "(none)")

if remaining != ["pilot_check.py"]:
    print("ERROR: scripts/ contains unexpected files after cleanup")
    sys.exit(1)


# ------------------------------------------------------------------
# Final gates / reporting
# ------------------------------------------------------------------

print("\n===== FINAL CORPUS CHECK =====")
final_check = subprocess.run(
    [sys.executable, "scripts/pilot_check.py"],
    cwd=ROOT,
)

print("\n===== FINAL DIFF CHECK =====")
final_diff = subprocess.run(
    ["git", "diff", "--check"],
    cwd=ROOT,
)

print("\n===== STALE PF-002 LANGUAGE =====")
grep = subprocess.run(
    ["grep", "-rilE", "forced|knowingly", "data/"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
if grep.returncode == 0 and grep.stdout.strip():
    print(grep.stdout, end="")
    print("ERROR: stale forced/knowingly wording remains in data/")
    sys.exit(1)
print("PASS: no stale forced/knowingly wording in data/")

print("\n===== GIT STATUS =====")
subprocess.run(["git", "status", "--short"], cwd=ROOT)

print("\n===== DIFF STAT =====")
subprocess.run(["git", "diff", "--stat"], cwd=ROOT)

if final_check.returncode or final_diff.returncode:
    print("\nRESULT: BLOCKING-CORRECTIONS-01 FAILED final gates.")
    sys.exit(1)

print("\nRESULT: BLOCKING-CORRECTIONS-01 PASSED.")
print("No commit was created. PF-003 records were not created.")
