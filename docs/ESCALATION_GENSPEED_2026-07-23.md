# Escalation Stage — Generation-Speed Measurement (2026-07-23)

Condition 1 of the budget confirmation: replace the plan's ~154 A100-h GSM8K
estimate with a measurement before any GSM8K eval cell is submitted. FP16
generation on the two new models, GSM8K, off the confirmatory item set (indices
≥ 1000), blindness contract enforced in code (job `11378480`).

## Result

| model | s/item | tok/s | cap-hit | projected full cell (1000 items) |
|---|---|---|---|---|
| **qwen25-7b** | 4.73 | 46.2 | 6/16 | **1.31 A100-h** |
| **llama31-8b** | 5.52 | 30.8 | 2/16 | **1.53 A100-h** |

Both models now measured (Llama-8B added 2026-07-23 after access was granted,
job `11381675`). **Qwen-7B 1.31 A100-h/cell, Llama-8B 1.53 A100-h/cell.** The
GSM8K eval half is therefore **11 × 1.31 + 11 × 1.53 = ~31 A100-h, not 154** —
removing ~123 A100-h from the stage total. Revised stage total lands well under
half the plan estimate and nowhere near the 360 hard bound. Neither model's
per-cell wall (1.31 / 1.53 h) approaches the 8 h embers wall. Condition 1's
stop-and-report (eval half beyond 360) is not triggered with wide margin.

The MMLU (choice-scored, non-generative) cells are not measured here; they are
confirmed at the reference/canary stage. They were never the cost driver.

## Blocker — RESOLVED 2026-07-23

### (original) Llama-3.1-8B gated-repo download denial

The probe failed on `meta-llama/Llama-3.1-8B-Instruct` with a 403:

> Access to model meta-llama/Llama-3.1-8B-Instruct is restricted and you are not
> in the authorized list.

Confirmed as a **per-model access grant**, not a token fault (`hf_access_check`):
`model_info` resolves for all three, but 3.1-8B *file* download is denied while
**3.2-3B (used throughout the mini-grid) succeeds**. Meta gates the 3.1 and 3.2
families separately; the account holds 3.2-3B but not 3.1-8B.

**Resolution (2026-07-23).** Diagnosed as a fine-grained token that lacked
3.1-8B in its scope while downloading gated 3.2-3B fine (the token permission
worked; the repo was not in its allowlist). Amogh confirmed the model page
showed *granted* and edited the token's scope; the same token value then
downloaded 3.1-8B at the pinned revision (re-probe `11381642`, ACCESS_RESULT:
GRANTED). Full timeline: `docs/ESCALATION_LLAMA_ACCESS_2026-07-23.md`. The Llama
generation-speed measurement above was taken immediately after.

## Budget impact

Strictly favourable. The dollar guard's conservative projection stands as an
upper bound; the measured total is far lower. `docs/ESCALATION_DOLLAR_GUARD_2026-07-23.md`
is not loosened — a lower measured cost only widens the reserve.

## Provenance

Job `11378480` (inferno, exit 1 — Qwen result captured before the Llama access
failure); driver `~/scratch/flipeval/work/genspeed_8b_fp16.py`;
access check `hf_access_check.sbatch`.
