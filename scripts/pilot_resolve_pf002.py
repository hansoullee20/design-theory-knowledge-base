#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

def root() -> Path:
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
    except Exception:
        print("ERROR: run inside the design-theory-knowledge-base repository.")
        sys.exit(2)

def require(path: Path) -> str:
    if not path.exists():
        print(f"ERROR: required file missing: {path}")
        sys.exit(2)
    return path.read_text(encoding="utf-8")

def write_if_changed(path: Path, old: str, new: str) -> bool:
    if old == new:
        print(f"UNCHANGED: {path}")
        return False
    path.write_text(new, encoding="utf-8")
    print(f"UPDATED: {path}")
    return True

def add_actor_relative_to_vocab(path: Path) -> None:
    text = require(path)
    if re.search(r"^\s*-\s+actor-relative\s*$", text, re.M):
        print(f"UNCHANGED: {path} already contains actor-relative")
        return

    m = re.search(r"^(?P<i>\s*)-\s+artifact\s*$", text, re.M)
    if not m:
        print(f"ERROR: could not find artifact value in {path}")
        sys.exit(2)

    insert_at = m.end()
    line = f"\n{m.group('i')}- actor-relative"
    text = text[:insert_at] + line + text[insert_at:]
    write_if_changed(path, require(path), text)

def add_actor_relative_to_schema(path: Path) -> None:
    original = require(path)
    lines = original.splitlines(keepends=True)

    # Locate the unique schema property named 'locus' regardless of indentation.
    candidates = []
    for i, line in enumerate(lines):
        m = re.match(r"^(?P<i>\s*)locus:\s*$", line.rstrip("\n"))
        if m:
            candidates.append((i, len(m.group("i"))))

    if len(candidates) != 1:
        print(f"ERROR: expected exactly one locus property in {path}, found {len(candidates)}")
        for i, _ in candidates:
            print(f"  line {i+1}: {lines[i].rstrip()}")
        sys.exit(2)

    locus_start, locus_indent = candidates[0]
    locus_end = len(lines)

    # The locus block ends at the next nonblank key at the same or shallower indent.
    key_re = re.compile(r"^(?P<i>\s*)(?P<key>[A-Za-z0-9_$-]+):")
    for i in range(locus_start + 1, len(lines)):
        raw = lines[i].rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = key_re.match(raw)
        if m and len(m.group("i")) <= locus_indent:
            locus_end = i
            break

    block = "".join(lines[locus_start:locus_end])

    if re.search(r'^\s*-\s*["\']?actor-relative["\']?\s*$', block, re.M):
        print(f"UNCHANGED: {path} locus enum already contains actor-relative")
        return

    # Block-style enum item. Preserve quoted/unquoted style of artifact.
    for j in range(locus_start, locus_end):
        raw = lines[j].rstrip("\n")
        m = re.match(r'^(?P<i>\s*)-\s+(?P<q>["\']?)artifact(?P=q)\s*$', raw)
        if m:
            indent = m.group("i")
            quote = m.group("q")
            newline = "\n" if lines[j].endswith("\n") else ""
            rendered = f"{quote}actor-relative{quote}" if quote else "actor-relative"
            lines.insert(j + 1, f"{indent}- {rendered}{newline}")
            text = "".join(lines)
            write_if_changed(path, original, text)
            return

    # Flow-style enum fallback.
    flow = re.search(r"enum:\s*\[(?P<body>[^\]]+)\]", block)
    if flow:
        raw_values = [v.strip() for v in flow.group("body").split(",")]
        normalized = [v.strip("\"'") for v in raw_values]
        if "artifact" in normalized:
            idx = normalized.index("artifact") + 1
            artifact_rendered = raw_values[idx - 1]
            quote = artifact_rendered[0] if artifact_rendered[:1] in {"\"", "'"} else ""
            rendered = f"{quote}actor-relative{quote}" if quote else "actor-relative"
            raw_values.insert(idx, rendered)
            new_enum = "enum: [" + ", ".join(raw_values) + "]"
            new_block = block[:flow.start()] + new_enum + block[flow.end():]
            text = "".join(lines[:locus_start]) + new_block + "".join(lines[locus_end:])
            write_if_changed(path, original, text)
            return

    print(f"ERROR: found locus property but could not identify its artifact enum value in {path}")
    print("---- locus block ----")
    print(block.rstrip())
    print("---------------------")
    sys.exit(2)

def replace_locus(path: Path, new_value: str) -> None:
    original = require(path)
    pattern = re.compile(r"^locus:\n(?:  - [^\n]+\n)+", re.M)
    m = pattern.search(original)
    if not m:
        print(f"ERROR: could not find locus block in {path}")
        sys.exit(2)
    replacement = f"locus:\n  - {new_value}\n"
    text = original[:m.start()] + replacement + original[m.end():]
    write_if_changed(path, original, text)

def fix_affordance(path: Path) -> None:
    original = require(path)
    text = original

    text = re.sub(
        r'^definition: ".*"\n',
        'definition: "What the environment offers an animal for action relative to that animal\'s capabilities, existing whether or not it is perceived."\n',
        text,
        count=1,
        flags=re.M,
    )

    # Replace the temporary stress-case note if it is still present.
    text = re.sub(
        r'^notes: "INTENTIONAL PILOT STRESS CASE:.*"\n',
        'notes: "Re-filed as actor-relative after PF-002 was confirmed across ecological psychology, typography/vision science, and readability research. Perception is not treated as constitutive of the ecological affordance."\n',
        text,
        count=1,
        flags=re.M,
    )

    write_if_changed(path, original, text)

def update_foundation(path: Path) -> None:
    original = require(path)
    text = original

    # Rev marker: tolerate an already-updated file.
    text = text.replace(
        "**Status:** Working architecture decision record (rev. 2). Decisions may be superseded; see §17.",
        "**Status:** Working architecture decision record (rev. 3). Decisions may be superseded; see §17.",
        1,
    )

    # Replace only the locus subsection inside §5.3, without depending on exact wording.
    sec_start = text.find("### 5.3 Classification fields")
    sec_end = text.find("### 5.4 ", sec_start)
    if sec_start < 0 or sec_end < 0:
        print("ERROR: could not identify §5.3 boundaries in docs/PROJECT_FOUNDATION.md")
        sys.exit(2)

    sec = text[sec_start:sec_end]

    locus_start = sec.find("- \`locus\`")
    if locus_start < 0:
        print("ERROR: could not find locus bullet inside §5.3")
        sys.exit(2)

    # The next classification-field bullet marks the end of the locus block.
    next_candidates = [
        sec.find("- \`facets\`", locus_start + 1),
        sec.find("- \`disciplines\`", locus_start + 1),
        sec.find("- \`knowledge_origin\`", locus_start + 1),
        sec.find("- \`traditions\`", locus_start + 1),
    ]
    next_candidates = [x for x in next_candidates if x >= 0]
    if not next_candidates:
        print("ERROR: could not determine end of locus block in §5.3")
        sys.exit(2)
    locus_end = min(next_candidates)

    locus_block = """- \`locus\` (**required**): the bearer of the property. Decide it by asking what must change for the property itself to change.
  - \`artifact\`: borne by the designed artifact or environment itself (spacing, contrast ratio, grid)
  - \`actor-relative\`: borne by the relation between a designed artifact/environment and an actor's capabilities; it can change when either the artifact/environment or the relevant capability changes, but not merely because the actor's perception or belief changes (ecological affordance, typeface legibility, linguistic readability)
  - \`experience\`: borne by a person's perceptual, cognitive, or affective state (grouping, salience, perceived hierarchy, perceived affordance)
  - \`outcome\`: borne by an episode or consequence of use and available for observation or measurement (reading speed, error rate, task completion)
  - \`practice\`: borne by an activity of designing, researching, or evaluating

  \`outcome\` is strictly a locus value. It names a construct, not a measured result; measured results are \`observation\` records (§10). A record with more than one locus value must be reviewed for splitting into senses rather than using multiple loci to encode a relation. Actor characteristics themselves are not assigned a locus by this amendment; that open issue is tracked separately in the pilot.
"""

    new_sec = sec[:locus_start] + locus_block + sec[locus_end:]
    text = text[:sec_start] + new_sec + text[sec_end:]

    # Quality-attribute sentence: amend only if not already actor-relative-aware.
    qa_old = "Quality attributes (accessibility, usability, legibility) are **concepts**, not domains."
    qa_new = "Quality attributes (accessibility, usability, legibility) are **concepts**, not domains; when the property is borne by the artifact/environment relative to an actor's capabilities, its locus is \`actor-relative\`."
    if qa_new not in text and qa_old in text:
        text = text.replace(qa_old, qa_new, 1)

    # Quantification hook: tolerate wording already changed.
    q_old = "A **measurable variable** is an \`outcome\`- or \`experience\`-locus concept **\`operationalized_by\`** a \`method\`."
    q_new = "A **measurable variable** is an \`outcome\`-, \`experience\`-, or \`actor-relative\`-locus concept **\`operationalized_by\`** a \`method\`."
    if q_new not in text and q_old in text:
        text = text.replace(q_old, q_new, 1)

    # Decision log: append rev. 3 after rev. 2 if absent.
    rev3 = "| 3 | 2026-09-26 | PF-002 resolved after independent affordance and legibility/readability stress tests: \`locus\` redefined as property bearer; additive \`actor-relative\` locus introduced for artifact/environment–actor capability relations; actor characteristics remain an open pilot issue. |"
    if rev3 not in text:
        lines = text.splitlines()
        inserted = False
        out = []
        for line in lines:
            out.append(line)
            if line.startswith("| 2 | 2026-09-26 |") and not inserted:
                out.append(rev3)
                inserted = True
        if not inserted:
            print("ERROR: could not find rev. 2 row in §17 decision log")
            sys.exit(2)
        text = "\n".join(out)
        if original.endswith("\n"):
            text += "\n"

    write_if_changed(path, original, text)

def resolve_pf002(path: Path) -> None:
    original = require(path)
    lines = original.splitlines()
    replacement = (
        "| PF-002 | Actor-relative locus | The original locus vocabulary could not represent properties borne by an artifact/environment relative to actor capabilities; confirmed independently by ecological affordance, typeface legibility, and linguistic readability. | concept schema / locus vocabulary | Added `actor-relative`; re-filed the three confirmed records; redefined locus as the bearer of the property using the change test. | Preserve the additive locus through the remaining pilot; actor characteristics remain tracked separately as PF-003. | resolved |"
    )
    found = False
    out = []
    for line in lines:
        if line.startswith("| PF-002 |"):
            out.append(replacement)
            found = True
        else:
            out.append(line)
    if not found:
        print(f"ERROR: PF-002 row not found in {path}")
        sys.exit(2)
    text = "\n".join(out).rstrip() + "\n"
    write_if_changed(path, original, text)

def correct_checker_description(path: Path) -> None:
    if not path.exists():
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

    add_actor_relative_to_vocab(r / "vocab/locus.yaml")
    add_actor_relative_to_schema(r / "schema/concept.schema.yaml")

    for rel in [
        "data/concepts/affordance-ecological.yaml",
        "data/concepts/legibility-typeface.yaml",
        "data/concepts/readability-linguistic.yaml",
    ]:
        replace_locus(r / rel, "actor-relative")

    fix_affordance(r / "data/concepts/affordance-ecological.yaml")
    update_foundation(r / "docs/PROJECT_FOUNDATION.md")
    resolve_pf002(r / "pilot/PILOT_FAILURE_LOG.md")
    correct_checker_description(r / "scripts/pilot_check.py")

    rc1 = run([sys.executable, "scripts/pilot_check.py"], r)
    rc2 = run(["git", "diff", "--check"], r)

    print("\n===== GIT STATUS =====")
    subprocess.run(["git", "status", "--short"], cwd=r)

    print("\n===== DIFF STAT =====")
    subprocess.run(["git", "diff", "--stat"], cwd=r)

    if rc1 or rc2:
        print("\nRESULT: PF-002 migration applied, but validation FAILED.")
        sys.exit(1)

    print("\nRESULT: PF-002 migration applied and validation PASSED.")
    print("No commit was created. PF-003 remains open.")

if __name__ == "__main__":
    main()
