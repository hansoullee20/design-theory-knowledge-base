#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FILES = {
    "data/sources/saw-gatzke-2024-visual-hierarchy.yaml": """id: source:saw-gatzke-2024-visual-hierarchy
kind: source
citation: "Saw, J. J., & Gatzke, L. P. (2024). Designing visual hierarchies for the communication of health data. Journal of the American Medical Informatics Association, 31(11), 2722–2729."
source_type: paper
year: 2024
identifier: "doi:10.1093/jamia/ocae175"
notes: ""
schema_version: "0.1"
""",

    "data/concepts/hierarchy-specified.yaml": """id: concept:hierarchy-specified
kind: concept
label: "Specified visual hierarchy"
aliases:
  - "intended visual hierarchy"
definition: "An ordering of relative importance intentionally encoded in a visual artifact through differences such as size, position, color, contrast, or other visual treatment."
definition_sources:
  - source:saw-gatzke-2024-visual-hierarchy
locus:
  - artifact
facets:
  - layout
disciplines:
  - information-design-visualization
knowledge_origin:
  - design-practice
traditions: []
broader: []
part_of: []
related:
  - concept:hierarchy-perceived
opposite_of: []
record_status: draft
replaced_by: []
notes: "Pilot operational sense used to distinguish the hierarchy encoded by a designer from the hierarchy perceived by a viewer."
schema_version: "0.1"
""",

    "data/concepts/hierarchy-perceived.yaml": """id: concept:hierarchy-perceived
kind: concept
label: "Perceived visual hierarchy"
aliases:
  - "perceived hierarchy"
definition: "The ordering of relative importance that a viewer perceives among elements in a visual artifact."
definition_sources:
  - source:saw-gatzke-2024-visual-hierarchy
locus:
  - experience
facets:
  - layout
disciplines:
  - information-design-visualization
knowledge_origin:
  - perceptual-science
  - design-practice
traditions: []
broader: []
part_of: []
related:
  - concept:hierarchy-specified
opposite_of: []
record_status: draft
replaced_by: []
notes: "Pilot operational sense used to distinguish experienced hierarchy from the hierarchy encoded in the artifact."
schema_version: "0.1"
""",

    "data/claims/specified-hierarchy-influences-perceived-hierarchy.yaml": """id: claim:specified-hierarchy-influences-perceived-hierarchy
kind: claim
statement: "The visual hierarchy encoded in an artifact can influence the relative importance perceived by its viewer."
modality: explanatory
subject: concept:hierarchy-specified
predicate: influences
object: concept:hierarchy-perceived
basis:
  - theoretical
  - conventional
evidence_status: unassessed
scope: "Visual information presentation. The effect depends on the cues used, viewer, task, content, and context."
sources:
  - source:saw-gatzke-2024-visual-hierarchy
record_status: draft
replaced_by: []
notes: "Pilot claim. Evidence has not yet been assessed; the source is being used to test representation, not to establish a final evidence rating."
schema_version: "0.1"
""",
}

CHECKBOXES = {
    "- [ ] hierarchy — specified": "- [x] hierarchy — specified",
    "- [ ] hierarchy — perceived": "- [x] hierarchy — perceived",
}

def repo_root() -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        return Path(out)
    except Exception:
        print("ERROR: run inside the design-theory-knowledge-base repository.")
        sys.exit(2)

def write_files(root: Path, force: bool) -> None:
    for rel, content in FILES.items():
        path = root / rel
        if path.exists() and not force:
            print(f"ERROR: {rel} already exists. Re-run with --force only if you intend to replace it.")
            sys.exit(2)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"WROTE: {rel}")

def update_pilot_list(root: Path) -> None:
    path = root / "pilot" / "PILOT_RECORDS.md"
    if not path.exists():
        print("WARN: pilot/PILOT_RECORDS.md not found; checkbox state not updated.")
        return
    text = path.read_text(encoding="utf-8")
    original = text
    for before, after in CHECKBOXES.items():
        text = text.replace(before, after)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("UPDATED: pilot/PILOT_RECORDS.md")
    else:
        print("INFO: hierarchy pilot checkboxes were already checked or wording differs.")

def run_check(root: Path) -> int:
    checker = root / "scripts" / "pilot_check.py"
    if not checker.exists():
        print("WARN: scripts/pilot_check.py not found; records written but integrity check was not run.")
        return 0
    print("\n===== PILOT CHECK =====")
    return subprocess.run([sys.executable, str(checker)], cwd=root).returncode

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create the hierarchy-specified / hierarchy-perceived adversarial pilot records."
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Replace existing hierarchy pilot files. Normally leave this off.",
    )
    args = ap.parse_args()

    root = repo_root()
    write_files(root, args.force)
    update_pilot_list(root)

    print("\nRepresentation under test:")
    print("  concept:hierarchy-specified  [locus: artifact]")
    print("                 |")
    print("                 | explanatory claim")
    print("                 v")
    print("  concept:hierarchy-perceived  [locus: experience]")
    print("\nNo evidence-strength judgment is being made in this pilot.")

    rc = run_check(root)
    if rc:
        print("\nRESULT: hierarchy pilot records created, but integrity check FAILED.")
        sys.exit(rc)

    print("\nRESULT: hierarchy pilot records created and integrity check PASSED.")

if __name__ == "__main__":
    main()
