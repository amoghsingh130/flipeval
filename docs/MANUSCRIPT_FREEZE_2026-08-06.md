# Manuscript freeze, 2026-08-06

**The scientific manuscript is frozen.** Audit compression is closed and
`paper/sections/audit.tex` is not to be compressed further. The line-edit
proposal in `docs/AUDIT_LINE_EDIT_PROPOSAL_2026-08-06.md` is **withdrawn from
consideration**, not pending; it is retained only as a record of what was
considered and declined.

Machine-readable manifest: `docs/MANUSCRIPT_FREEZE_2026-08-06.json`, 34 files,
collective sha256 `f273ae6c4df1c2af40ed6ecfe6ddb82a66408e3d2a0a0f1460a00f8706961002`.

## What the freeze covers

`paper/main.tex`, `paper/abstract.tex`, `paper/audit_denominators.tex`,
`paper/references.bib`, both Figure 1 files, all 20 `paper/sections/*.tex`, and
the 8 `paper/tools/*.py` gates, each with its sha256 and byte count.

## What "frozen" means here, and what it does not

**Closed under this freeze:** any change to a scientific claim, number,
qualification, count, table value, section scope, or the argument's structure.
No further compression of any body section.

**Still open:** typographic and layout repair that changes no rendered text;
regeneration of a generated file from its unchanged source of truth
(`audit_denominators.tex`, `fig1_cancellation.tex`, `READING_COPY.md`);
correcting a defect that a gate reports. Any such change re-runs every gate and
updates the manifest in the same commit.

**A freeze is a discipline, not a lock.** If a real error is found in a frozen
number, it is corrected and the freeze is re-recorded with the reason. What the
freeze forbids is discretionary revision.

## State at freeze

| | |
|---|---|
| branch | `flagship-narrative`, **local, never pushed** |
| main body | pages 1-32 |
| references begin | page 33 |
| total PDF | 100 pages |
| principal evidence concludes | page 28 |
| anonymity switch | `\anonfalse` (arXiv/preprint). `\anontrue` yields the blind TMLR build |

### Gates at freeze, all passing

```
in-image pytest, job 11705552  : 348 passed, 0 skipped, exit 0
PAPER_CHECK                    : OK, 0 dangling refs, 0 unresolved cites
STALE_CLAIM                    : OK
gen_denominator_macros --check : OK on all three layers
gen_audit_tables --check       : OK, 17 rows byte for byte
REGISTRATIONS_VERBATIM         : OK, 7,103 words across 4 documents
ABSTRACT_CHARS                 : 1879 / 1920, margin 41
churn_ratio.py --check         : OK, 25 printed values
check_layout.py                : OK
freeze_prepace --verify        : passed
prose em dashes                : 0
```

## One caveat the freeze cannot close

`main.tex` line 121 sets `\date{Draft \today}`. **The PDF is therefore not
byte-reproducible across days**: today's build says "Draft August 6, 2026" and
tomorrow's will not match it. The *sources* are frozen by hash and are
reproducible; the rendered date is not.

This was left as found rather than changed, because the title block is
manuscript content and this freeze is a record, not an edit. Two options, for
whoever decides:

- for a dated preprint, replace `\today` with the literal freeze date;
- for a submission, drop the word "Draft" as well.

Neither is done here.

## Verifying the freeze

```bash
python3 - <<'EOF'
import hashlib, json, pathlib
m = json.loads(pathlib.Path('docs/MANUSCRIPT_FREEZE_2026-08-06.json').read_text())
bad = [f for f, e in m['files'].items()
       if hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest() != e['sha256']]
print('MANUSCRIPT_FREEZE:', 'OK' if not bad else f'CHANGED: {bad}')
EOF
```
