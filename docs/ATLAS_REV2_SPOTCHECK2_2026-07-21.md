# Atlas Rev-2 — Targeted Second Spot-Check (2026-07-21)

**VERDICT: PASS. 14 of 14 cells reconciled, 126 of 126 compared fields, zero
discrepancies.**

Authorized under ruling R6 of 2026-07-21 and executed under ruling item 2 of the
rev-2 close-out. Scope as ruled: the recovered F1 pairs plus a sample of newly
admitted F2 cells, same independent-reimplementation method as pass one.

Artifacts: `~/scratch/flipeval/spotcheck2/` — `select_cells2.py` (selection),
`verify2.py` (verifier), `selection.json`, `recomputed.json`. Run as embers job
`11343673`, in-image. **Scratch is on a 60-day purge; `recomputed.json` and
`selection.json` need a durable home if this check is to remain citable.**

## Selection rule — fixed before any recomputed value existed

Universe: rev-2 cells that are analyzed and non-probe. Strata:

| stratum | definition | pool | taken |
|---|---|---|---|
| **A — recovered-F1** | newly analyzed in rev-2 **and** `run_fallback_used` true | 122 | 5 |
| **B — admitted-F2** | newly analyzed in rev-2 **and** `run_fallback_used` false — admitted purely by the schema fix | 430 | 5 |
| **C — control** | analyzed in **both** revisions | 1,155 | 4 |

Within each stratum, ordered ascending by `md5("{pair_index}|{task}")` and the
first N taken. Deterministic, independent of every metric value.

**Amendment 1, recorded before any cell was recomputed.** The first draft defined
stratum B as "excluded in rev-1 for a missing correctness column, in a pair that
still contributed cells", which left a pool of **1**. The F1 and F2 populations
overlap heavily — most schema-unreadable cells sit in pairs that contributed
nothing at all — so the stratum was restated on the operative distinction
(fallback used vs not). Amended before any comparison was made.

**Stratum C is the point of the check, not filler.** The rev-2 commit claims
`s1_run_combinations` is a *strict generalisation* of rev-1, so a cell that
already succeeded cannot be perturbed. Stratum C tests that claim directly.

## Method

Fresh minimal reimplementation (`verify2.py`), written from
`ATLAS_MINING_REGISTRATION` §§3–5 and `PREREGISTRATION.md` line 49. It does not
import `scripts.atlas_flip_analysis` or `flipeval.core` for any quantity under
test. Raw per-item files re-downloaded from the Hub into a cache directory that
never held the rev-2 run's downloads.

Recomputed independently per cell: join-key dedup (both sides), shared keys,
joinable count, prompt-identity pass rate and the 99 % gate, correctness-column
selection, harmful/beneficial flip counts, net accuracy delta, accuracy-state
churn, baseline and method accuracy, and exact two-sided McNemar. McNemar is
computed in **exact integer arithmetic** via `Fraction` — `2·Σ_{i≤min(b,c)}
C(n,i) / 2ⁿ`, capped at 1 — so no floating-point binomial is trusted.

Where the newer schema is involved, the verifier applies the interpretive choice
recorded in `ATLAS_REV2_CORRECTION_2026-07-21.md` §4 (identity clauses, and
correctness column by presence in the data). That is a **ruled decision this
check applies, not one it re-litigates**; every count, rate and p-value is still
computed independently.

## Results

| stratum | cells | verdict |
|---|---|---|
| A — recovered-F1 | 5 (pairs 1, 41 ×3, 1) | **5/5 reconciled** |
| B — admitted-F2 | 5 (pairs 49 ×2, 29, 26, 31) | **5/5 reconciled** |
| C — control | 4 (pairs 47, 12, 40, 51/S2) | **4/4 reconciled** |
| **total** | **14** | **126/126 fields, 0 discrepancies** |

Two cells in stratum B — pair 49 `logical_fallacies` and pair 29 `hellaswag` —
are precisely the two cells pass one examined and found **"excluded both ways,
reason differs"** (finding F4). They are now analyzed, and their recomputed
values match the committed rev-2 row exactly. That is the F2/F4 fix
demonstrated end to end on the same cells that first exposed it.

**Stratum C reconciled 4/4, including the one S2 cell.** The
strict-generalisation claim holds on the sample: rev-2 did not perturb cells
that already succeeded, and S2 — which neither fix touches — is unchanged.

## One defect found, and it was in the checker

The first run (job `11343636`) returned 13 reconciled and **1 ERROR** on the S2
control cell (pair 51, `gpqa_main`): `JSONDecodeError: Unterminated string`.

This was investigated before any verdict was recorded, because the honest first
hypothesis was a pipeline defect or a corrupt download. It was neither:

- The downloaded file is byte-identical to the pipeline's own cached copy —
  same size, same sha256. Not a download problem.
- The file contains **two U+2028 LINE SEPARATOR characters inside string
  values**. Python's `str.splitlines()` treats U+2028 (and U+2029, `\x0b`,
  `\x0c`, `\x85`) as line breaks; iterating a file object splits on `\n`
  alone. The verifier used `splitlines()` and cut two records mid-string;
  `load_s2_rows` in the pipeline iterates the file object and is **correct**.
- With the loader corrected to `split("\n")`, all 448 records parse and the cell
  reconciles.

**No pipeline defect. The reimplementation was wrong and the pipeline was
right.** Recorded because it is exactly the class of error an independent check
is supposed to distinguish, and because a less careful pass would have filed it
as a rev-2 finding.

## Standing caveats

- **Not verified** (outside the ruled scope): `tost_equivalent`, `tost_p_low/high`,
  `mdd_80_power`, `required_n_for_observed_delta_80_power`, bootstrap CIs,
  `total_answer_churn`, `wrong_to_different_wrong_churn`.
- Pass one's finding **F5** (unpaginated tree listing) is fixed in code and
  covered by unit tests, but the 26 cells that carried the
  "no parquet found for task" reason were not individually re-verified here.
- Sample size is 14 of 1,707 analysable cells. This is a spot-check, not a
  census; it bounds the probability of a systematic defect, it does not exclude
  one.

## Consequence

The rev-2 cell population and its per-cell arithmetic are both now
independently supported: pass one confirmed rev-1's arithmetic (10 cells,
262/262 fields) and identified the population defects; pass two confirms the
corrected population on the cells the correction added, plus an unchanged
control. Per ruling item 5, the paper's `\revtwoTODO` / `\revtwoBanner` figures
are cleared to be updated to rev-2 values, and the blog's DO-NOT-PUBLISH
decision goes to Amogh with this verdict attached.
