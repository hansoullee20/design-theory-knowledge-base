#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FILES = {
    "data/sources/gibson-1979-ecological-approach.yaml": """id: source:gibson-1979-ecological-approach
kind: source
citation: "Gibson, J. J. (1979). The Ecological Approach to Visual Perception. Houghton Mifflin."
source_type: book
year: 1979
identifier: "isbn:9780395270493"
notes: ""
schema_version: "0.1"
""",
    "data/sources/norman-1999-affordance-conventions-design.yaml": """id: source:norman-1999-affordance-conventions-design
kind: source
citation: "Norman, D. A. (1999). Affordance, conventions, and design. interactions, 6(3), 38–43."
source_type: paper
year: 1999
identifier: "doi:10.1145/301153.301168"
notes: ""
schema_version: "0.1"
""",
    "data/sources/norman-2014-design-everyday-things.yaml": """id: source:norman-2014-design-everyday-things
kind: source
citation: "Norman, D. (2014). The Design of Everyday Things: Revised and Expanded Edition. MIT Press."
source_type: book
year: 2014
identifier: "isbn:9780262525671"
notes: ""
schema_version: "0.1"
""",
    "data/concepts/affordance-ecological.yaml": """id: concept:affordance-ecological
kind: concept
label: "Ecological affordance"
aliases:
  - "Gibsonian affordance"
definition: "An action possibility that exists in relation between features of an environment and the action capabilities of an organism."
definition_sources:
  - source:gibson-1979-ecological-approach
locus:
  - artifact
  - experience
facets:
  - interaction
disciplines:
  - interface-interaction-design
knowledge_origin:
  - perceptual-science
traditions:
  - ecological-psychology
broader: []
part_of: []
related:
  - concept:affordance-perceived
opposite_of: []
record_status: draft
replaced_by: []
notes: "INTENTIONAL PILOT STRESS CASE: the current locus vocabulary has no relational actor-environment value. artifact + experience is a temporary, knowingly imperfect representation and should trigger review."
schema_version: "0.1"
""",
    "data/concepts/affordance-perceived.yaml": """id: concept:affordance-perceived
kind: concept
label: "Perceived affordance"
aliases:
  - "perceived action possibility"
definition: "An action possibility that a user perceives to be available in an interface or artifact, whether or not the corresponding action is actually possible."
definition_sources:
  - source:norman-1999-affordance-conventions-design
locus:
  - experience
facets:
  - interaction
disciplines:
  - interface-interaction-design
knowledge_origin:
  - cognitive-psychology
  - design-practice
traditions:
  - ecological-psychology
  - cognitive-engineering-hci
broader: []
part_of: []
related:
  - concept:affordance-ecological
  - concept:signifier
opposite_of: []
record_status: draft
replaced_by: []
notes: "Pilot sense separated from Gibson's ecological affordance following Norman's explicit distinction between real and perceived affordances."
schema_version: "0.1"
""",
    "data/concepts/signifier.yaml": """id: concept:signifier
kind: concept
label: "Signifier"
aliases: []
definition: "A perceivable cue that communicates where or how an action can be performed."
definition_sources:
  - source:norman-2014-design-everyday-things
locus:
  - artifact
facets:
  - interaction
disciplines:
  - interface-interaction-design
knowledge_origin:
  - design-practice
  - cognitive-psychology
traditions:
  - cognitive-engineering-hci
broader: []
part_of: []
related:
  - concept:affordance-perceived
opposite_of: []
record_status: draft
replaced_by: []
notes: ""
schema_version: "0.1"
""",
    "data/claims/signifier-influences-perceived-affordance.yaml": """id: claim:signifier-influences-perceived-affordance
kind: claim
statement: "A perceivable signifier can influence what actions a user perceives to be available."
modality: explanatory
subject: concept:signifier
predicate: influences
object: concept:affordance-perceived
basis:
  - theoretical
  - conventional
evidence_status: unassessed
scope: "Design interaction contexts. This pilot claim represents Norman's design-theory distinction; empirical evidence strength has not yet been assessed."
sources:
  - source:norman-2014-design-everyday-things
record_status: draft
replaced_by: []
notes: ""
schema_version: "0.1"
"""
}

FAILURE_ROW = (
    "| PF-002 | Ecological affordance locus | Gibsonian affordance is relational between environmental features and actor capabilities; "
    "the current locus vocabulary (artifact / experience / outcome / practice) cannot represent that relation cleanly. | "
    "concept schema / locus vocabulary | Temporarily encoded as locus: [artifact, experience], which is knowingly inaccurate. | "
    "Evaluate adding a relational locus or representing affordance through a relation-bearing construct after the pilot; do not resolve yet. | open |"
)

CHECKBOXES = {
    "- [ ] affordance — ecological": "- [x] affordance — ecological",
    "- [ ] affordance — perceived": "- [x] affordance — perceived",
    "- [ ] signifier": "- [x] signifier",
}

def repo_root() -> Path:
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    except Exception:
        print("ERROR: run inside the design-theory-knowledge-base repository.")
        sys.exit(2)

def write_files(root: Path, force: bool) -> None:
    for rel, content in FILES.items():
        path = root / rel
        if path.exists() and not force:
            print(f"ERROR: {rel} already exists. Re-run with --force only if replacement is intentional.")
            sys.exit(2)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"WROTE: {rel}")

def update_failure_log(root: Path) -> None:
    path = root / "pilot" / "PILOT_FAILURE_LOG.md"
    if not path.exists():
        print("WARN: pilot/PILOT_FAILURE_LOG.md not found; PF-002 not logged.")
        return
    text = path.read_text(encoding="utf-8")
    if "| PF-002 |" in text:
        print("INFO: PF-002 already present in failure log.")
        return
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + FAILURE_ROW + "\n", encoding="utf-8")
    print("UPDATED: pilot/PILOT_FAILURE_LOG.md (PF-002)")

def update_pilot_list(root: Path) -> None:
    path = root / "pilot" / "PILOT_RECORDS.md"
    if not path.exists():
        print("WARN: pilot/PILOT_RECORDS.md not found; checklist not updated.")
        return
    text = path.read_text(encoding="utf-8")
    original = text
    for before, after in CHECKBOXES.items():
        text = text.replace(before, after)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("UPDATED: pilot/PILOT_RECORDS.md")
    else:
        print("INFO: affordance pilot checkboxes already updated or wording differs.")

def run_check(root: Path) -> int:
    checker = root / "scripts" / "pilot_check.py"
    if not checker.exists():
        print("WARN: scripts/pilot_check.py not found; records written but integrity check was not run.")
        return 0
    print("\n===== PILOT CHECK =====")
    return subprocess.run([sys.executable, str(checker)], cwd=root).returncode

def main() -> None:
    ap = argparse.ArgumentParser(description="Create the affordance/signifier adversarial pilot records.")
    ap.add_argument("--force", action="store_true", help="Replace existing affordance pilot files. Normally leave this off.")
    args = ap.parse_args()

    root = repo_root()
    write_files(root, args.force)
    update_failure_log(root)
    update_pilot_list(root)

    print("\nRepresentation under test:")
    print("  concept:affordance-ecological  [RELATIONAL; temporarily artifact + experience]")
    print("  concept:affordance-perceived   [locus: experience]")
    print("  concept:signifier              [locus: artifact]")
    print("                 |")
    print("                 | explanatory claim")
    print("                 v")
    print("  concept:affordance-perceived")
    print("\nEXPECTED PILOT SIGNAL: pilot_check.py should emit a warning for")
    print("multiple locus values on ecological affordance. That warning is intentional")
    print("and corresponds to PF-002 in the failure log.")

    rc = run_check(root)
    if rc:
        print("\nRESULT: affordance pilot records created, but integrity check FAILED.")
        sys.exit(rc)

    print("\nRESULT: affordance pilot records created.")
    print("A PASS with one multi-locus WARNING is the expected outcome.")
    print("That confirms a real schema limitation rather than a malformed record.")

if __name__ == "__main__":
    main()
