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
    if re.search(r"^\s*-\s+actor-relative\s*$", original, re.M):
        print(f"UNCHANGED: {path} already contains actor-relative")
        return

    # Insert only in the enum/list containing the locus quartet.
    pattern = re.compile(
        r"(?P<indent>\s*)- artifact\n"
        r"(?P=indent)- experience\n"
        r"(?P=indent)- outcome\n"
        r"(?P=indent)- practice"
    )
    m = pattern.search(original)
    if not m:
        print(f"ERROR: could not find the locus enum quartet in {path}")
        sys.exit(2)

    i = m.group("indent")
    replacement = (
        f"{i}- artifact\n"
        f"{i}- actor-relative\n"
        f"{i}- experience\n"
        f"{i}- outcome\n"
        f"{i}- practice"
    )
    text = original[:m.start()] + replacement + original[m.end():]
    write_if_changed(path, original, text)

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

    text = text.replace(
        "**Status:** Working architecture decision record (rev. 2). Decisions may be superseded; see §17.",
        "**Status:** Working architecture decision record (rev. 3). Decisions may be superseded; see §17.",
    )

    old = """- `locus` (**required**): where the thing exists.
  - `artifact`: specifiable by the designer (spacing, contrast ratio, grid)
  - `experience`: a perceptual, cognitive, or affective construct (grouping, salience, perceived hierarchy)
  - `outcome`: a measurable consequence of use (reading speed, error rate, task completion)
  - `practice`: an activity of designing or evaluating

  `outcome` is strictly a locus value. It names a construct, not a measured result; measured results are `observation` records (§10). A record with more than one locus value must be reviewed for splitting into senses (e.g. specified hierarchy vs. perceived hierarchy).
"""
    new = """- `locus` (**required**): the bearer of the property. Decide it by asking what must change for the property itself to change.
  - `artifact`: borne by the designed artifact or environment itself (spacing, contrast ratio, grid)
  - `actor-relative`: borne by the relation between a designed artifact/environment and an actor's capabilities; it can change when either the artifact/environment or the relevant capability changes, but not merely because the actor's perception or belief changes (ecological affordance, typeface legibility, linguistic readability)
  - `experience`: borne by a person's perceptual, cognitive, or affective state (grouping, salience, perceived hierarchy, perceived affordance)
  - `outcome`: borne by an episode or consequence of use and available for observation or measurement (reading speed, error rate, task completion)
  - `practice`: borne by an activity of designing, researching, or evaluating

  `outcome` is strictly a locus value. It names a construct, not a measured result; measured results are `observation` records (§10). A record with more than one locus value must be reviewed for splitting into senses rather than using multiple loci to encode a relation. Actor characteristics themselves are not assigned a locus by this amendment; that open issue is tracked separately in the pilot.
"""
    if old not in text:
        print("ERROR: expected §5.3 locus block not found in docs/PROJECT_FOUNDATION.md")
        sys.exit(2)
    text = text.replace(old, new, 1)

    text = text.replace(
        "Quality attributes (accessibility, usability, legibility) are **concepts**, not domains.",
        "Quality attributes (accessibility, usability, legibility) are **concepts**, not domains; when the property is borne by the artifact/environment relative to an actor's capabilities, its locus is `actor-relative`.",
        1,
    )

    text = text.replace(
        "A **measurable variable** is an `outcome`- or `experience`-locus concept **`operationalized_by`** a `method`.",
        "A **measurable variable** is an `outcome`-, `experience`-, or `actor-relative`-locus concept **`operationalized_by`** a `method`.",
        1,
    )

    rev3 = "| 3 | 2026-09-26 | PF-002 resolved after independent affordance and legibility/readability stress tests: `locus` redefined as property bearer; additive `actor-relative` locus introduced for artifact/environment–actor capability relations; actor characteristics remain an open pilot issue. |"
    if rev3 not in text:
        marker = "| 2 | 2026-09-26 | Record kinds + orthogonal fields (locus, facets, disciplines, knowledge_origin, traditions); concepts separated from claims; no structural ENABLES/AFFECTS; later layers additive; lifecycle `evidence_status` with reserved `evidence_profile`, no hand-entered strength rating; mechanism as explanatory claim; `outcome` locus only, `observation` for measured data; `operationalized_by` reserved; quantification readiness as reserved commitment; ID and file rules; pilot before freeze. |"
        if marker not in text:
            print("ERROR: rev. 2 decision-log row not found")
            sys.exit(2)
        text = text.replace(marker, marker + "\n" + rev3, 1)

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
