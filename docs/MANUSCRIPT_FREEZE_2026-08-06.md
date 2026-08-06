# Manuscript freeze, 2026-08-06

**The scientific manuscript is frozen.** Audit compression is closed and
`paper/sections/audit.tex` is not to be compressed further. The line-edit
proposal in `docs/AUDIT_LINE_EDIT_PROPOSAL_2026-08-06.md` is **withdrawn from
consideration**, not pending; it is retained only as a record of what was
considered and declined.

Machine-readable manifest: `docs/MANUSCRIPT_FREEZE_2026-08-06.json`, 34 files,
collective sha256 `42a3d76e65b6f36216a9ba3008453d778fe4f8fd9e7952f4def9d052b2e746ce`
(re-frozen after the date repair; the first freeze was `f273ae6c…961002`).

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

## The date caveat, CLOSED 2026-08-06

The first freeze recorded that `main.tex` set `\date{Draft \today}`, so the PDF
was not byte-reproducible across days. **That is now repaired.** The line reads
`\date{August 2026}`, a fixed string that renders identically in both identity
modes and needs no `\ifanon` routing.

arXiv advises against `\today` precisely because it may rebuild a submission
later, silently changing the displayed date on a paper whose sources are frozen.
**The rendered PDF is now reproducible across days**, which is what a freeze
should mean.

This was release hygiene, not a reopening of scientific content: exactly one
file changed, `paper/main.tex`, and the manifest above is the re-freeze.

If the arXiv build should say ``Preprint'' while the blind build does not, route
the date through `\ifanon` as the identifiers are routed. It is deliberately not
routed now, because one neutral string cannot desynchronise between modes.

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
