#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"], text=True).strip())
OUTDIR = Path(sys.argv[1]) if len(sys.argv)>1 else Path("/tmp/design-theory-parallel")
OUTDIR.mkdir(parents=True, exist_ok=True)

head = subprocess.check_output(["git","rev-parse","--short","HEAD"],cwd=ROOT,text=True).strip()

memo = [
"# Skill Creator and Evidence-Layer Research Memo","",
f"Repository HEAD: {head}","",
"## 1. Skill Creator boundary","",
"- The current runtime contract already establishes that the canonical repository is authority and the reasoning skill is a consumer.",
"- Generated doctrine should be rebuilt from the Foundation and controlled vocabularies, not hand-maintained as a second canon.",
"- A Skill Creator should therefore be a derived build pipeline, not a new canonical record kind.",
"- Its inputs should include a canonical Git commit/tag, Foundation text, vocabularies, schemas, and selected canonical records.",
"- Its outputs should be rebuildable artifacts: generated doctrine, retrieval configuration, skill workflow package, test fixtures, and a build manifest binding those outputs to the source commit.",
"- The generated skill must remain read-only against canon; any proposed canonical change should go through proposals/branch review rather than direct mutation.",
"",
"## 2. Minimum Skill Creator controls","",
"- source-commit binding;",
"- deterministic generation where practical;",
"- generated-versus-handwritten file separation;",
"- competency/regression tests for the reasoning workflow;",
"- bounded retrieval rather than whole-corpus loading;",
"- explicit treatment of evidence_status and basis;",
"- no silent schema inference or canon mutation;",
"- build manifest recording source commit, generator version, and generated files.",
"",
"## 3. Evidence-layer research","",
"- ECO is useful primarily as a controlled vocabulary for evidence types and assertion methods; it should not be treated as a ready-made confidence score.",
"- SEPIO is closer to the future Design Theory evidence layer because it models claims, evidence lines, supporting information, methods, tools, and agents.",
"- Micropublications are particularly relevant to contradiction/challenge because the model explicitly supports challenge and disagreement around claims and evidence.",
"- W3C PROV remains appropriate for generic provenance plumbing and derivation, but provenance alone does not encode evidential support or contradiction semantics.",
"",
"## 4. Recommended Design Theory position","",
"- Do not add evidence_profile or contradiction structures merely because external ontologies exist.",
"- First require a concrete competency question that needs multiple evidence items, support/challenge relations, or evidence-quality assessment.",
"- When that trigger occurs, evaluate an additive evidence layer with claim -> evidence-line relationships rather than adding manual strong/moderate/weak labels to claim records.",
"- Keep source provenance, evidence type, support/challenge relation, and confidence/assessment as separate concerns.",
"",
"## 5. Candidate future competency questions","",
"1. Can two evidence items support and challenge the same canonical claim without duplicating that claim?",
"2. Can the system distinguish evidence type from evidence quality?",
"3. Can an evidence assessment change without changing proposition identity?",
"4. Can a runtime explain why a claim is treated as tentative using evidence records rather than a hand-entered strength label?",
"5. Can generated skill doctrine bind to a canonical Git commit and detect drift before use?",
"",
"## 6. External references reviewed","",
"- Evidence & Conclusion Ontology (ECO): https://www.evidenceontology.org/",
"- Scientific Evidence and Provenance Information Ontology (SEPIO): https://monarchinitiative.org/ontologies/sepio",
"- W3C PROV-O Recommendation: https://www.w3.org/TR/prov-o/",
"- Clark et al., Micropublications: a semantic model for claims, evidence, arguments and annotations in biomedical communications, 2014/2015: https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/",
"",
"## 7. Current decision","",
"- Skill Creator: research direction supported; implementation remains downstream of stable canon and generated-doctrine testing.",
"- Evidence/contradiction layer: defer canonical schema changes until a concrete competency question fails under the present claim/source model.",
"- Repository mutation: none."
]

path=OUTDIR/"skill_creator_evidence_research.md"
path.write_text("\n".join(memo)+"\n",encoding="utf-8")
print("OUTCOME: SKILL_EVIDENCE_RESEARCH_COMPLETE")
print("REPORT:",path)
print("REPOSITORY_MUTATION: 0")
