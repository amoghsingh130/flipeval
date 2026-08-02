# Rev-3 execution ledger

Coordination state for `docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md`, which is
the authoritative plan. This file maps each checklist section to files, an owner,
prerequisites, and a validation command. It is a status document, not a plan.
When it disagrees with the checklist, the checklist wins.

Baseline: HEAD `377a686`, branched from `546a1f6` (the 2026-08-02 handoff).
Working tree clean, 37 local commits ahead of `origin`, deliberately unpushed.

## Validation commands that actually run here

The Phoenix login node has python 3.9.21 with no pytest, pandas, scipy or torch,
and `apptainer` is not on PATH. These four run on the login node and all pass at
`377a686`:

| Command | Purpose |
|---|---|
| `python3 paper/tools/check_paper.py` | manuscript structural checks, 24 tabulars (227 rows) |
| `python3 paper/tools/verify_registrations.py` | appendix reproduces frozen registrations verbatim |
| `python3 paper/tools/gen_audit_tables.py --check` | regenerates a trusted table and diffs it |
| `python3 scripts/freeze_prepace.py --verify docs/PREPACE_FREEZE.json` | source-state fingerprint |

The test suite is **not** among them. `sbatch scripts/slurm/run_tests.sbatch` is
the only way to run the gate, expectation `207 passed, 0 skipped` at `377a686`.
Anything touching `tests/` is therefore a SLURM round trip, not a local check.

Fingerprint boundary, which decides whether a change needs a freeze refresh:
`INCLUDED_TREES` is `configs`, `flipeval`, `pilot_eval`, `scripts`, `tests`, plus
the named files in `INCLUDED_PATHS`. **`paper/`, `AGENTS.md` and most of `docs/`
are outside it.**

## Section ledger

| § | Subject | Owner | Files | Prerequisites | Validation |
|---|---|---|---|---|---|
| Canonical | rev-3 invariants | A | `results/audit_verdicts_rev3.csv`, new macro file in `paper/` | none | arithmetic-identity tests |
| 1 | Freeze and preserve evidence | **unassigned** | `docs/PREPACE_FREEZE.json`, release manifest | rev-3 numbers final | `freeze_prepace.py --verify` |
| 2 | Complete audit adjudication | A (mechanical) + **Amogh** (human) | `results/audit_verdicts_rev3.csv`, `tests/` | none | R14 invariant test |
| 3 | Lock statistical interpretation | E (tests) + **unassigned** (TOST wording, independent n_req check) | `flipeval/`, `tests/`, `paper/sections/audit.tex` | A integrated | in-image gate |
| 4 | Make toolkit fail closed | E | `flipeval/`, `scripts/`, `tests/` | none | in-image gate |
| 5 | Replace stale manuscript claims | D | `paper/abstract.tex`, `audit.tex`, `appendix_audit_table.tex`, all sections | **A integrated** | `check_paper.py`, linter |
| 6 | Stale-claim and stale-pointer audit | B | `paper/tools/check_paper.py`, `tests/` | none | linter negative controls |
| 7 | Write the amendment transparently | **Amogh only** | `docs/AUDIT_REGISTRATION_2026-07-15.md` amendments | signature | none automatable |
| 8 | Release corrected artifact | C (licensing) + G (Zenodo prep) | `paper/sections/artifacts.tex`, README, release notes | none | manual review |
| 9 | Presentation and human voice | D (partial) + **Amogh** (voice) | all sections | 5 done | human read |
| 10 | J2C-facing validation | F (scout only) | memo first, then **Amogh decides** | none | none yet |
| 11 | arXiv and TMLR packages | H | build scripts, `paper/main.tex` | 5, 9 done | anonymity scanner |
| 12 | Final release gates | **Amogh, TeX machine** | compiled PDF | everything | visual inspection |

## Wave status

| Worker | Task | Branch | State |
|---|---|---|---|
| A | denominator macros, arithmetic invariants | `worker-a-denominator-macros` | running |
| B | stale-claim and stale-pointer linter | `worker-b-stale-claim-linter` | running |
| C | Option A artifact and licensing paperwork | `worker-c-option-a-paperwork` | running |
| F | J2C validation-case scout, read-only | none, memo only | running |
| D | conclusion, limitations, narrative consistency | not started | blocked on A |
| E | golden and boundary tests | not started | wave 2 |
| G | Zenodo v1.1.0 preparation, no upload | not started | wave 3 |
| H | arXiv and TMLR package scaffolding | not started | wave 3 |

## Coordination decisions

**One consolidated gate, not three.** Workers A, B and E all add tests. The
project rule is that whichever session adds tests updates the expected count in
the same commit. Three workers each running the gate, refreshing the freeze and
editing the count would produce three conflicting edits, three SLURM jobs, and
three counts that are each wrong the moment another branch lands. So workers add
tests only; the coordinator runs one in-image gate after integrating all
test-adding work, then does one freeze refresh and one count update. The rule's
intent, that the expectation is never stale, is preserved, because the final
count is only knowable once every test has landed.

**Integration order.** A first, because sections must consume generated macros
rather than hand-typed counts. B second, because the linter must be able to see
the target state without flagging it. C third, because it is independent of both.
D only after A is integrated.

## Open items no worker owns

These are in the checklist but not in the worker plan. They need assignment or an
explicit decision to defer.

1. **§3 TOST wording.** One-sided `alpha = 0.05` corresponds to a 90 percent
   two-sided confidence interval, not 95 percent. This is a substantive
   statistical correction, not a wording preference, and it is unassigned.
2. **§3 independent validation of the required-sample-size calculation**, against
   a second implementation or hand derivation, including nonzero true deltas.
3. **§1 evidence freeze and preservation**, including recording the rev-2 atlas
   path, revision, sha256, schema version and row count 792.
4. **§7 amendment transparency.** Amogh only, since it appends to a frozen
   registration.
5. **Canonical block cross-tab** reconciling the margin taxonomy with the
   "10 of 16 contain no number" statement. Worker A has been asked whether the
   CSV can support it.

## Standing blockers

**History rewrite.** `docs/audit_sources_20260731.tar.gz` enters at `cc357db`;
every commit from there to HEAD carries the blob. `bb45528` is in that range and
is cited in the frozen, signed Amendment 2 at
`docs/AUDIT_REGISTRATION_2026-07-15.md:228`. Removing the blob makes a
signature's provenance chain point at a nonexistent commit. Unblocking requires
Amogh to sign a dated amendment recording the old to new hash mapping. Until
then the branch stays local. `v1.0.0` / `987377a` is an ancestor of `cc357db`, so
the release and its Zenodo archive are outside the rewrite entirely.

**No second human.** Amogh has none and will not get one. Author re-verification
and automated passes are never to be described as independent or inter-rater
verification. Checklist §2 still lists a genuine second human as the target, so
this gap is open, not closed.

**No TeX.** Every §12 gate is blocked on a machine with LaTeX. The rev-3 tables
have never been typeset, and `tmlr.sty` is single-column 6.5 by 9 inches, which
reflows everything.
