# Escalation Stage — Generation-Speed Measurement (2026-07-23)

Condition 1 of the budget confirmation: replace the plan's ~154 A100-h GSM8K
estimate with a measurement before any GSM8K eval cell is submitted. FP16
generation on the two new models, GSM8K, off the confirmatory item set (indices
≥ 1000), blindness contract enforced in code (job `11378480`).

## Result

| model | s/item | tok/s | cap-hit | projected full cell (1000 items) |
|---|---|---|---|---|
| **qwen25-7b** | 4.73 | 46.2 | 6/16 | **1.31 A100-h** |
| llama31-8b | — | — | — | **not measured — access-blocked (below)** |

The measured Qwen-7B rate is **~5× faster than the plan's ~7 h/cell guess**. At
1.31 h/cell the GSM8K half is far below the estimate: 11 Qwen cells ≈ 14 A100-h.
Even assuming Llama-8B runs ~15 % slower (~1.5 h/cell → ~17 A100-h for its 11
cells), the **GSM8K eval half projects to ~31 A100-h, not 154** — removing ~123
A100-h from the stage total. Revised stage total lands well under half the plan
estimate and nowhere near the 360 hard bound. The 8 h embers wall is also no
longer a risk at ~1.3 h/cell.

The MMLU (choice-scored, non-generative) cells are not measured here; they are
confirmed at the reference/canary stage. They were never the cost driver.

## Blocker — Llama-3.1-8B is a gated repo the account cannot download

The probe failed on `meta-llama/Llama-3.1-8B-Instruct` with a 403:

> Access to model meta-llama/Llama-3.1-8B-Instruct is restricted and you are not
> in the authorized list.

Confirmed as a **per-model access grant**, not a token fault (`hf_access_check`):
`model_info` resolves for all three, but 3.1-8B *file* download is denied while
**3.2-3B (used throughout the mini-grid) succeeds**. Meta gates the 3.1 and 3.2
families separately; the account holds 3.2-3B but not 3.1-8B.

**Required human action (Amogh):** request/accept access at
`https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct` under the account whose
token is in `$HF_TOKEN`. Until granted, the Llama-8B half of the escalation
(canary, calibration, builds, eval) cannot run. The Qwen-7B half is fully
unblocked.

## Budget impact

Strictly favourable. The dollar guard's conservative projection stands as an
upper bound; the measured total is far lower. `docs/ESCALATION_DOLLAR_GUARD_2026-07-23.md`
is not loosened — a lower measured cost only widens the reserve.

## Provenance

Job `11378480` (inferno, exit 1 — Qwen result captured before the Llama access
failure); driver `~/scratch/flipeval/work/genspeed_8b_fp16.py`;
access check `hf_access_check.sbatch`.
