# Results Note: Public-Data Atlas and Audit Extraction (2026-07-15)

Status: descriptive results from the two registered zero-GPU workstreams.
Numbers below are cell-level descriptives; no registered verdict or headline
aggregate has been computed yet. Pending an independent spot-check of the
same-day pipeline (two bugs were found and fixed during the run), treat as
provisional for external quoting.

## 1. Atlas flip analysis (ATLAS_MINING_REGISTRATION_2026-07-15)

Pipeline: `scripts/atlas_flip_analysis.py` (bootstrap 1000, seed 0) over the
frozen 59-pair manifest (`docs/atlas_pair_manifest.json`). Full per-cell JSONs:
`results/atlas_run_20260715.tar.gz` (sha256 in sibling file); summaries:
`results/atlas_cells_summary.csv`, `results/atlas_exclusions.csv`.

- 2,055 enumerated pair-task cells; **1,254 analyzed** (S1 = 906, S2 = 348);
  801 excluded/skipped, dominated by 643 cells with no binary correctness
  column (float-scored tasks) and 132 with empty join intersections —
  the leaderboard evaluated different item sets across runs, itself a
  reporting-standards observation.
- With the two §1-disclosed probe cells excluded:

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
  7 method papers, 8 official model cards/blog, 2 vendor docs.
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
