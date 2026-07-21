# Identical-Score Churn — derivation note (2026-07-21)

Descriptive statistic derived from the **completed, committed** atlas. Not a
registered verdict quantity; no registered analysis was tuned to produce it.
Full output: `results/identical_score_churn.csv`.

## Why this note exists

An earlier internal framing of this finding circulated as "6.3% flips at
identical score". **That figure is retired from all public-facing text.** Its
source was the pre-registration feasibility anecdote (the bnb-4bit same-repo
rerun), which is disqualified on two independent grounds:

1. It lies **outside the frozen 59-pair manifest** (`docs/atlas_pair_manifest.json`).
   Same-repo multi-precision runs are an amendment candidate that has not been
   acted on.
2. It is **pre-registration data contact**.

It may appear in the paper only as part of the honestly-disclosed feasibility
narrative, never as an atlas statistic. The numbers below supersede it for every
external use.

## Population

Analysable cells = `excluded_or_skipped` false **and**
`contains_disclosed_probe_cell` false → **1,155 cells**. This is the same
population the certification tables use (`docs/CERTIFICATION_TABLES_2026-07-20.md`),
i.e. 1,254 non-excluded minus the 99 disclosed-probe cells excluded per
`ATLAS_MINING_REGISTRATION_2026-07-15` §6.

Zero-delta = `abs(net_accuracy_delta) < 1e-12` (exact equality; no rounding
tolerance — a rounding-based definition would admit more cells and is not used).

## Results

| statistic | value |
|---|---|
| analysable cells | 1,155 |
| cells posting **exactly identical** accuracy | **113 (9.78 %)** |
| median `accuracy_state_churn` among those | **0.0622 (6.22 %)** |
| mean churn among those | 0.0862 |
| max churn among those | 0.3434 |
| zero-delta cells with **nonzero** churn | 96 of 113 |
| median churn, nonzero-churn cells only | 0.0919 |

Reading: roughly **one in ten** compressed-model evaluations in the public
record posts a score identical to its baseline, and half of those still disagree
with the baseline on more than **6.2 %** of individual items. The aggregate score
is unchanged; the per-item behaviour is not.

## Most extreme zero-delta cell

Top-ranked row of `results/identical_score_churn.csv`:

| field | value |
|---|---|
| pair_index / source | 35 / S1 |
| task | `harness_hendrycksTest_high_school_geography_5` (MMLU) |
| base model | `project-baize/baize-v2-7b` |
| quantized model | `TheBloke/Project-Baize-v2-7B-GPTQ` (GPTQ) |
| n | 198 |
| baseline accuracy | 0.429293 |
| compressed accuracy | 0.429293 (delta = 0.000000) |
| accuracy-state churn | **0.343434** |
| harmful / beneficial flips | 0.171717 / 0.171717 |
| exact McNemar p | 1.0 |

The symmetry is the point: 17.17 % of items broke and 17.17 % healed, so the
net delta is exactly zero and McNemar returns p = 1.0 — the paired test
correctly reports no evidence of a *directional* difference, while a third of
the answers changed. **Honest caveats:** n = 198 is small, and this is an S1
cell (2023-era community GPTQ of a 7B model), which is the noisier of the two
strata. It is an illustration of the mechanism, not a typical magnitude — the
median is 6.22 %, not 34 %.

## Reproduction

Stdlib-only (Phoenix login node has python 3.9, no pandas/numpy). Source:
`results/atlas_cells_summary.csv`, sha256
`98201adef9939c00bef7d89b515cbadf907315eb8a052c7f00437b8910a4712d`.

```python
import csv, statistics as st
falsy = lambda v: v.strip().lower() in ("", "false", "no", "0")
rows = list(csv.DictReader(open("results/atlas_cells_summary.csv")))
an = [r for r in rows if falsy(r["excluded_or_skipped"])
      and falsy(r["contains_disclosed_probe_cell"])]
zero = [r for r in an if abs(float(r["net_accuracy_delta"])) < 1e-12]
churn = [float(r["accuracy_state_churn"]) for r in zero]
print(len(an), len(zero), st.median(churn))   # -> 1155 113 0.0621761658031088
```

## Scope

- **Not fingerprinted.** Neither this note nor `results/` is in
  `INCLUDED_PATHS`/`INCLUDED_TREES` of `scripts/freeze_prepace.py`, so no freeze
  refresh is owed. Doc-and-results-only; no test gate per `AGENTS.md`.
- **Inherits the atlas provisional caveat.** `docs/RESULTS_2026-07-15_ATLAS_AUDIT.md`
  marks atlas numbers provisional for external quoting pending an independent
  spot-check. These statistics carry that caveat until the spot-check is
  recorded as completed.
