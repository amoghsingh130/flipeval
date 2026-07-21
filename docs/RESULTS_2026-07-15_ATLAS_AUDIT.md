# Results Note: Public-Data Atlas and Audit Extraction (2026-07-15)

Status: descriptive results from the two registered zero-GPU workstreams.
Numbers below are cell-level descriptives.

> **SPOT-CHECK COMPLETED 2026-07-21 — CAVEAT NARROWED, NOT LIFTED.**
> The independent spot-check commissioned for this document has been run:
> 10 cells stratified across {S1, S2} × {zero-delta, high-churn,
> McNemar-significant, excluded}, recomputed from freshly re-downloaded raw
> per-item files by a from-scratch reimplementation of the registered
> definitions (not a rerun of `scripts/atlas_flip_analysis.py`).
> **Result: 262 of 262 compared fields reconciled, zero discrepancies, and no
> upstream data drift.** The per-cell join, gates, flip counts, churn, net
> delta and exact McNemar p of rev-1 are independently confirmed sound.
>
> **What remains provisional is the cell population, not the arithmetic.** The
> same spot-check found that rev-1 omitted the registered §3.2 earlier-run
> fallback (11 S1 pairs contributed zero cells) and could not read a newer
> details schema (583 cells misfiled as float-scored). Every
> denominator-dependent number in this document — cell counts, S1/S2
> descriptives, and everything downstream of them — is therefore
> **superseded pending atlas rev-2**. See
> `docs/ATLAS_REV2_CORRECTION_2026-07-21.md`.
>
> Do not quote the aggregates below externally until rev-2 lands and passes its
> targeted second spot-check.

## 1. Atlas flip analysis (ATLAS_MINING_REGISTRATION_2026-07-15)

Pipeline: `scripts/atlas_flip_analysis.py` (bootstrap 1000, seed 0) over the
frozen 59-pair manifest (`docs/atlas_pair_manifest.json`). Full per-cell JSONs:
`results/atlas_run_20260715.tar.gz` (sha256 in sibling file); summaries:
`results/atlas_cells_summary.csv`, `results/atlas_exclusions.csv`.

- 2,055 enumerated pair-task cells; **1,254 analyzed** (S1 = 906, S2 = 348);
  801 excluded/skipped.

  > **CORRECTION (2026-07-21).** This bullet previously read "dominated by 643
  > cells with no binary correctness column (float-scored tasks) and 132 with
  > empty join intersections — the leaderboard evaluated different item sets
  > across runs, itself a reporting-standards observation." **Both halves of
  > that gloss are retracted.** The independent spot-check established that
  > **583 of the 643** are binary-scored cells whose metrics the rev-1 parser
  > could not reach (a newer lighteval schema nests them under `metrics`), and
  > that empty join intersections were frequently produced by the same parser
  > failing to read the join key at all, not by the leaderboard evaluating
  > different item sets. The retracted sentence attributed to upstream data a
  > limitation that was ours. Only `harness_truthfulqa_mc_0` among the sampled
  > cells is genuinely non-binary. See
  > `docs/ATLAS_REV2_CORRECTION_2026-07-21.md`; corrected counts come from
  > rev-2 and are not restated here.

- With the two §1-disclosed probe **pairs** excluded — 99 cells, not two: the
  manifest flag is pair-level, so every task of pair_index 2 and 50 carries it
  (ratified in `docs/AUDIT_VERDICTS_2026-07-20.md` §"Interpretive choices" #6):

| | S1 (v1 archive, TheBloke-era GPTQ etc.) | S2 (Neural Magic W4A16/INT8/FP8, 8B–405B) |
|---|---|---|
| Cells | 846 | 309 |
| Median accuracy-state churn | 0.133 | 0.048 |
| Median absolute net accuracy delta | 0.023 | 0.009 |
| TOST-equivalent at 2 pp (cells) | 47 (5.6%) | 53 (17.2%) |
| Exact McNemar p < 0.05 (cells) | 148 (17.5%) | 19 (6.1%) |

- Reading: churn runs roughly 5–6× the net delta at every scale from 3B to
  405B; the large majority of cells are neither certifiable as equivalent at
  2 pp nor detectably degraded at their actual sample sizes (the
  "underpowered gray zone" motivating the certification tables). The S1→S2
  churn drop is consistent with genuine method improvement while the
  evidential gap persists.
- Population caveats (registered): S1 is community quantizations of
  2023-era models conditioned on leaderboard coverage; S2 is one vendor's
  releases. This is the public record of compression evaluation, not a
  census of quantization.

## 2. Audit claim table (AUDIT_REGISTRATION_2026-07-15, as amended)

- Dual extraction complete: pass 1 (13 claims), blind pass 2 per Amendment 1
  (17 claims + 6 logged exclusions, source sha256 recorded). Reconciliation
  memo: `docs/AUDIT_RECONCILIATION_2026-07-15.md`.
- **Frozen table: `docs/audit_claim_table.csv`, 17 claims** (commit 715a7ce):
  **F1 = 7, F2 = 7, F3 = 3** by the table's own `frame` column.
  *(Corrected 2026-07-21: this line previously read "7 method papers, 8 official
  model cards/blog, 2 vendor docs", which does not match the frozen table —
  R11, the Meta blog, is F2, and R12/R13/R14 are F3. The frozen table governs.)*
- Pre-verdict observations recorded with the table: two source-internal
  contradictions (SqueezeLLM abstract "lossless to 3-bit" vs its own −3.1 pp
  MMLU table; Red Hat W4A16 prose "93.0% recovery" vs its own table's 105.4%
  on Arena-Hard); three claims whose numeric evidence exists only as chart
  images; one equivalence claim shipped with an n=250 eval and no on-page
  baseline; only 1 of 17 claims has per-item outputs released.
- Honest non-claimers worth citing as positive examples: QuIP#, SpinQuant
  (papers), Qwen quantized model cards, llama.cpp docs.
- **Verdict computation (V1–V3) is now protocol-legal and has not been run.**

## 3. Provenance

Registrations: commits b74fd58 (frozen registrations), d6e02dd (Amendment 1).
Data freezes: f06348f (pair manifest), 715a7ce (claim table).
Pipeline: e3-series commits through 715dbaa (S1 timestamp fix); local suite
53 passed, 1 skipped at the time of the run.
