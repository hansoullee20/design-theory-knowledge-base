#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(['git','rev-parse','--show-toplevel'], text=True).strip())
EXPECTED_HEAD = '4754c1616e653e11c00ba1ccee23f127deaf2f53'

def fail(msg: str) -> None:
    print(f'ERROR: {msg}')
    sys.exit(2)

def run(cmd, capture=False):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)

def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists(): fail(f'missing required file: {rel}')
    return p.read_text(encoding='utf-8')

def write(rel: str, text: str) -> None:
    p = ROOT / rel
    old = p.read_text(encoding='utf-8') if p.exists() else None
    if old == text:
        print(f'UNCHANGED: {rel}')
        return
    p.write_text(text, encoding='utf-8')
    print(f'UPDATED: {rel}')

def require_clean_checkpoint() -> None:
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        fail(f'expected checkpoint {EXPECTED_HEAD}, got {head}')
    status = subprocess.check_output(['git','status','--short'], cwd=ROOT, text=True)
    if status.strip():
        print(status, end='')
        fail('working tree must be clean before rev. 6 implementation')
    print(f'VERIFIED CHECKPOINT: {head}')

def replace_schema_field() -> None:
    rel = 'schema/concept.schema.yaml'
    text = read(rel)
    if re.search(r'(?m)^\s{2}is_a:', text):
        fail('schema already contains is_a; expected rev. 5 checkpoint')
    new, n = re.subn(r'(?m)^(\s{2})broader:', r'\1is_a:', text, count=1)
    if n != 1:
        fail('schema/concept.schema.yaml: expected exactly one broader field')
    write(rel, new)

def rename_record_fields() -> None:
    changed = 0
    for p in sorted((ROOT/'data'/'concepts').glob('*.yaml')):
        text = p.read_text(encoding='utf-8')
        if re.search(r'(?m)^is_a:', text):
            fail(f'{p.relative_to(ROOT)} already contains is_a')
        new, n = re.subn(r'(?m)^broader:', 'is_a:', text, count=1)
        if n != 1:
            fail(f'{p.relative_to(ROOT)}: expected exactly one top-level broader field')
        p.write_text(new, encoding='utf-8')
        changed += 1
        print(f'UPDATED: {p.relative_to(ROOT)}')
    if changed != 15:
        fail(f'expected 15 concept records, renamed {changed}')

def install_checker() -> None:
    proc = subprocess.run(
        ['git','show','origin/pilot-tools:scripts/pilot_check.py'],
        cwd=ROOT, text=True, capture_output=True
    )
    if proc.returncode:
        print(proc.stderr, end='')
        fail('could not read hardened is_a checker from origin/pilot-tools')
    checker = proc.stdout
    if 'is_a' not in checker or 'broader' in checker:
        fail('pilot-tools checker is not the expected is_a version')
    write('scripts/pilot_check.py', checker)

def patch_foundation() -> None:
    rel = 'docs/PROJECT_FOUNDATION.md'
    text = read(rel)
    text, n = re.subn(
        r'\*\*Status:\*\* Working architecture decision record \(rev\. 5\)\.',
        '**Status:** Working architecture decision record (rev. 6).',
        text, count=1
    )
    if n != 1: fail('foundation rev. 5 status line not found')

    s8 = re.search(r'(?m)^## 8\..*$', text)
    if not s8: fail('foundation §8 heading not found')
    s9 = re.search(r'(?m)^## 9\..*$', text[s8.end():])
    if not s9: fail('foundation §9 heading not found')
    sec_end = s8.end() + s9.start()
    heading = s8.group(0)
    relation = '''
### 8.1 Structural relation semantics

Structural relations are intentionally narrow. They are ontological or navigational assertions, not substitutes for claims.

- `is_a`: on concept A, lists concept B when every instance of A is an instance of B (subsumption). It is transitive, irreflexive, antisymmetric, and acyclic. Endpoints must share the same `locus`.
- `part_of`: on concept A, lists concept B when A is a proper spatial, temporal, or structural constituent of instances of B. It does not mean dimension-of, attribute-of, feature-of, role-of, cause-of, or a step that produces B. It is transitive, irreflexive, and acyclic. Same-locus endpoints are expected; a cross-locus edge requires review.
- `related`: a symmetric, non-transitive navigational relation that asserts no subsumption, mereology, causation, or opposition. It may be used when no stronger structural relation is justified. Redundancy with claim-derived adjacency is tolerated during the v0.1 pilot.
- `opposite_of`: a symmetric relation reserved for genuine conceptual opposites or negations on the same conceptual dimension and `locus`. It is provisional pending FIGURE-GROUND-01.

Directional relations (`is_a`, `part_of`) are stored from subject to target and their inverses are derived. Symmetric relations (`related`, `opposite_of`) may be stored on either or both endpoints; the derived graph deduplicates them.

Validation invariants before Taxonomy v0.1:

1. All structural relations are irreflexive.
2. `is_a` and `part_of` are acyclic.
3. `is_a` endpoints must share the same `locus`; cross-locus `part_of` produces a review warning.
4. The same concept pair cannot simultaneously be linked by both `is_a` and `part_of`.

`is_a` and `part_of` are ontological assertions and should be supported by the same source discipline as definitions. `related` is navigational.
'''
    text = text[:s8.start()] + heading + '\n\n' + relation.strip() + '\n\n' + text[sec_end:]

    rev6 = ('| 6 | 2026-09-26 | Freeze-readiness relation and standards alignment: renamed `broader` to strict `is_a`; defined `is_a`, `part_of`, `related`, and provisional `opposite_of`; added structural-relation invariants and symmetric-storage rules; documented informative standards mappings without importing external ontologies. |')
    if rev6 not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for line in lines:
            out.append(line)
            if line.startswith('| 5 | 2026-09-26 |'):
                out.append(rev6)
                inserted = True
        if not inserted: fail('foundation rev. 5 decision-log row not found')
        text = '\n'.join(out).rstrip() + '\n'

    if re.search(r'(?m)^## 18\.', text):
        fail('foundation already has §18; refusing to overwrite')

    standards = '''
## 18. Informative standards alignment

Established standards are used for generic knowledge plumbing where their semantics fit the project's competency requirements. Project-specific distinctions are introduced only where those standards do not express the required Design Theory reasoning. These mappings are informative until an exporter exists: canonical records do not store RDF vocabulary terms, and no external ontology is imported or maintained as a second source of truth.

| Project construct | Informative alignment |
|---|---|
| `concept` | `skos:Concept` |
| `label` | `skos:prefLabel` |
| `aliases` | `skos:altLabel` |
| `definition` | `skos:definition` |
| `related` | `skos:related` |
| `is_a` | exportable as `skos:broader`; exportable as `rdfs:subClassOf` only when project concepts are modeled as classes |
| `part_of` | project-defined partitive extension |
| `opposite_of` | project extension; retention pending FIGURE-GROUND-01 |
| source metadata | Dublin Core-compatible |
| future source locator | Web Annotation Selector-compatible |
| future provenance | consult W3C PROV patterns |
| future evidence layer | consult ECO, SEPIO, and micropublication patterns |
| future rationale layer | consult QOC, IBIS, and CIMO |
| artifact-reasoning comparison | consult FBS |
| `locus`, `basis`, reasoning chain | project-specific application layer; no required external mapping |

`aliases` is reserved for genuine alternative lexical labels of one concept. User-language observations that can indicate multiple concepts remain a runtime retrieval problem over aliases, definitions, and the claim graph; they are not automatically promoted to aliases.
'''
    text = text.rstrip() + '\n\n' + standards.strip() + '\n'
    write(rel, text)

def patch_plugin_reference() -> None:
    rel = 'docs/PLUGIN_TARGET_ARCHITECTURE.md'
    text = read(rel)
    canonical5 = 'Foundation baseline: `docs/PROJECT_FOUNDATION.md` — foundation rev. 5'
    canonical6 = 'Foundation baseline: `docs/PROJECT_FOUNDATION.md` — foundation rev. 6'
    if canonical5 not in text:
        fail('plugin foundation rev. 5 baseline line not found')
    write(rel, text.replace(canonical5, canonical6, 1))

def verify_no_old_field() -> None:
    bad = []
    for p in [ROOT/'schema'/'concept.schema.yaml', ROOT/'scripts'/'pilot_check.py'] + sorted((ROOT/'data'/'concepts').glob('*.yaml')):
        txt = p.read_text(encoding='utf-8')
        if re.search(r'(?m)^\s*broader:', txt) or '"broader"' in txt:
            bad.append(str(p.relative_to(ROOT)))
    if bad: fail('old broader field remains in: ' + ', '.join(bad))
    print('PASS: no canonical broader field remains')

def main() -> None:
    print('===== CHECKPOINT =====')
    require_clean_checkpoint()

    print('\n===== BASELINE CHECKER =====')
    if run([sys.executable,'scripts/pilot_check.py']).returncode:
        fail('rev. 5 baseline checker failed')

    print('\n===== REV. 6 MUTATION =====')
    replace_schema_field()
    rename_record_fields()
    install_checker()
    patch_foundation()
    patch_plugin_reference()
    verify_no_old_field()

    print('\n===== REV. 6 SELF TEST =====')
    rc1 = run([sys.executable,'scripts/pilot_check.py','--self-test']).returncode
    print('\n===== REV. 6 CORPUS =====')
    rc2 = run([sys.executable,'scripts/pilot_check.py']).returncode
    print('\n===== DIFF CHECK =====')
    rc3 = run(['git','diff','--check']).returncode

    print('\n===== STATUS =====')
    run(['git','status','--short'])
    print('\n===== DIFF STAT =====')
    run(['git','diff','--stat'])

    if rc1 or rc2 or rc3:
        print('\nRESULT: REV6-RELATION-STANDARDS FAILED.')
        sys.exit(1)
    print('\nRESULT: REV6-RELATION-STANDARDS PASSED.')
    print('Corpus remains 32 records — 15 concepts, 6 claims, 11 sources.')
    print('No GRID-STRUCTURE-01 or FIGURE-GROUND-01 records were minted.')
    print('No commit or push was performed.')

if __name__ == '__main__':
    main()