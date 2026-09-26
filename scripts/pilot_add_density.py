#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FILES = {
    "data/sources/woodruff-landay-stonebraker-1998-density.yaml": """id: source:woodruff-landay-stonebraker-1998-density
kind: source
citation: "Woodruff, A., Landay, J. A., & Stonebraker, M. (1998). Constant information density in zoomable interfaces. Proceedings of the Working Conference on Advanced Visual Interfaces (AVI '98), 57–65."
source_type: paper
year: 1998
identifier: "doi:10.1145/948496.948505"
notes: ""
schema_version: "0.1"
""",

    "data/sources/schwartz-chassidim-2014-perceived-density.yaml": """id: source:schwartz-chassidim-2014-perceived-density
kind: source
citation: "Schwartz-Chassidim, H., Meyer, J., Parmet, Y., Rogatka, E., & Amzaleg, O. (2014). Perceived density of road maps. Applied Ergonomics, 45(6), 1579–1587."
source_type: paper
year: 2014
identifier: "doi:10.1016/j.apergo.2014.05.006"
notes: ""
schema_version: "0.1"
""",

    "data/concepts/display-object-density.yaml": """id: concept:display-object-density
kind: concept
label: "Display object density"
aliases:
  - "objective display density"
definition: "The number of displayed objects relative to a defined display unit or area."
definition_sources:
  - source:woodruff-landay-stonebraker-1998-density
locus:
  - artifact
facets:
  - layout
  - information-structure
disciplines:
  - information-design-visualization
  - interface-interaction-design
knowledge_origin:
  - human-factors
  - design-practice
traditions: []
broader: []
part_of: []
related:
  - concept:perceived-density
opposite_of: []
record_status: draft
replaced_by: []
notes: "Pilot operational sense. This is deliberately narrower than the ambiguous everyday term 'density' and should not be read as the only possible objective density metric."
schema_version: "0.1"
""",

    "data/concepts/perceived-density.yaml": """id: concept:perceived-density
kind: concept
label: "Perceived density"
aliases:
  - "subjective visual density"
definition: "A viewer's subjective perception or rating of how dense the information in a visual display appears."
definition_sources:
  - source:schwartz-chassidim-2014-perceived-density
locus:
  - experience
facets:
  - layout
  - information-structure
disciplines:
  - information-design-visualization
  - interface-interaction-design
knowledge_origin:
  - perceptual-science
  - human-factors
traditions: []
broader: []
part_of: []
related:
  - concept:display-object-density
opposite_of: []
record_status: draft
replaced_by: []
notes: "Pilot sense split from objective/display density. The 2014 source operationalizes perceived density through participant ratings of road maps."
schema_version: "0.1"
""",

    "data/claims/display-object-density-influences-perceived-density.yaml": """id: claim:display-object-density-influences-perceived-density
kind: claim
statement: "Properties contributing to objective display density can influence a viewer's perceived density of the display."
modality: explanatory
subject: concept:display-object-density
predicate: influences
object: concept:perceived-density
basis:
  - empirical
evidence_status: unassessed
scope: "Direct empirical support in the cited source concerns electronic road maps, where counts and properties of displayed map elements predicted perceived-density ratings. Generalization beyond comparable visual displays remains unassessed."
sources:
  - source:schwartz-chassidim-2014-perceived-density
record_status: draft
replaced_by: []
notes: "Pilot claim used to test artifact-to-experience sense separation and quantification readiness; no evidence-strength judgment has been made."
schema_version: "0.1"
""",
}

def repo_root() -> Path:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], text=True
            ).strip()
        )
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

def update_pilot_list(root: Path) -> None:
    path = root / "pilot" / "PILOT_RECORDS.md"
    if not path.exists():
        print("WARN: pilot/PILOT_RECORDS.md not found; checkbox not updated.")
        return
    text = path.read_text(encoding="utf-8")
    before = "- [ ] density"
    after = "- [x] density — split into display-object-density / perceived-density"
    if before in text:
        path.write_text(text.replace(before, after), encoding="utf-8")
        print("UPDATED: pilot/PILOT_RECORDS.md")
    elif after in text:
        print("INFO: density pilot checkbox already updated.")
    else:
        print("WARN: density checklist entry not found; no checklist change made.")

def run_check(root: Path) -> int:
    checker = root / "scripts" / "pilot_check.py"
    if not checker.exists():
        print("WARN: scripts/pilot_check.py not found; records written but integrity check was not run.")
        return 0
    print("\n===== PILOT CHECK =====")
    return subprocess.run([sys.executable, str(checker)], cwd=root).returncode

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create the density sense-splitting adversarial pilot records."
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Replace existing density pilot files. Normally leave this off.",
    )
    args = ap.parse_args()

    root = repo_root()
    write_files(root, args.force)
    update_pilot_list(root)

    print("\nRepresentation under test:")
    print("  concept:display-object-density  [locus: artifact]")
    print("                 |")
    print("                 | explanatory empirical claim")
    print("                 v")
    print("  concept:perceived-density       [locus: experience]")
    print("\nPilot question: can the ambiguous term 'density' be split by sense")
    print("without changing IDs, locus rules, or the concept schema?")

    rc = run_check(root)
    if rc:
        print("\nRESULT: density pilot records created, but integrity check FAILED.")
        sys.exit(rc)

    print("\nRESULT: density pilot records created and integrity check PASSED.")
    print("INTERPRETATION: a PASS means the current schema can represent this")
    print("artifact/experience distinction; it does not establish a universal")
    print("definition of density or assess the evidence strength.")

if __name__ == "__main__":
    main()
