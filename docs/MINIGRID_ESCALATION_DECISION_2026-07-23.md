# Mini-Grid Escalation Decision Record — 2026-07-23

**Registered first inspection.** Authorized by Amogh 2026-07-23 after
`scripts/verify_minigrid.py` passed over the complete 44-JSONL expected set
(job `11375247`, 409/409 checks, `passed: true`). This is the first reading of
mini-grid quantized accuracy permitted by
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5, and the same-day escalation
decision record that § 5 requires.

**Computation.** `flipeval paired-seeds` (registered hierarchical bootstrap,
2000 replicates, RNG seed 0) run once per cell over the four mini-grid cells,
then the § 3 escalation rule applied mechanically. Job `11376064`; artifacts
`results/minigrid_escalation/`.

---

## The rule, quoted (mini-grid registration § 3, FROZEN 2026-07-15)

> Compute, per the frozen algebra of `PREREGISTRATION.md`, for each of the 4
> cells at 4-bit: winner flips across seeds (ties counted separately, per the
> registered tie rule) and the range/gap criterion
> `max(range_GPTQ, range_AWQ) >= gap`.
>
> **Escalate** to the deferred 7B/8B seed cells iff:
> - winner flips occur in **at least 1 of the 4 cells**, OR
> - the range/gap criterion holds in **at least 2 of the 4 cells**.
>
> If neither condition holds, the 7B/8B cells are not built, and no other result
> (3-bit, other benchmarks, atlas findings) can substitute to trigger escalation.

The winner-flip, gap and range definitions are the frozen algebra of
`PREREGISTRATION.md` § "H3 Decision Rule":

> `d_s = acc_GPTQ,s − acc_AWQ,s`. A winner flip occurs in a cell if there are
> registered seeds `s` and `t` for which `sign(d_s) != sign(d_t)` and both
> differences are nonzero. An exact tie (`d_s = 0`) is neither a flip nor a
> non-flip and is reported separately.
> `gap = |mean_s(acc_GPTQ,s) − mean_s(acc_AWQ,s)|`;
> `range_m = max_s(acc_m,s) − min_s(acc_m,s)`;
> the range/gap criterion holds when `max(range_GPTQ, range_AWQ) >= gap`.

---

## Per-cell registered quantities

Accuracies are the deterministic per-seed full-sample values read from each
cell's own registered `paired-seeds` run (`per_seed[s].accuracies`), so the § 3
test and the reported hierarchical run share one computation.

### qwen25-1p5b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---|---|---|
| 0 | 0.504415 | 0.533542 | −0.029127 |
| 1 | 0.504914 | 0.518943 | −0.014029 |
| 2 | 0.541803 | 0.529341 | **+0.012463** |
| 3 | 0.501282 | 0.528913 | −0.027631 |
| 4 | 0.534254 | 0.537388 | −0.003133 |

ties: none · **winner flip: TRUE** (seed 2 positive, others negative) ·
gap 0.012292 · range_GPTQ 0.040521 · range_AWQ 0.018445 · max_range 0.040521 ·
**range/gap holds: TRUE**
hierarchical: full-sample GPTQ 0.517334 / AWQ 0.529625, delta −0.012292, winner awq ·
joint_rank_flip_rate 0.0445 · joint_exact_tie_rate 0.0005 ·
seed-level SD GPTQ 0.019130 / AWQ 0.006897

### qwen25-1p5b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---|---|---|
| 0 | 0.473000 | 0.584000 | −0.111000 |
| 1 | 0.467000 | 0.565000 | −0.098000 |
| 2 | 0.478000 | 0.558000 | −0.080000 |
| 3 | 0.467000 | 0.555000 | −0.088000 |
| 4 | 0.481000 | 0.588000 | −0.107000 |

ties: none · **winner flip: FALSE** (all negative) ·
gap 0.096800 · range_GPTQ 0.014000 · range_AWQ 0.033000 · max_range 0.033000 ·
**range/gap holds: FALSE**
hierarchical: full-sample GPTQ 0.473200 / AWQ 0.570000, delta −0.096800, winner awq ·
joint_rank_flip_rate 0.0 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.006340 / AWQ 0.015116

### llama32-3b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---|---|---|
| 0 | 0.506694 | 0.515667 | −0.008973 |
| 1 | 0.442886 | 0.533400 | −0.090514 |
| 2 | 0.496867 | 0.520154 | −0.023287 |
| 3 | 0.494873 | 0.509899 | −0.015026 |
| 4 | 0.487253 | 0.504059 | −0.016807 |

ties: none · **winner flip: FALSE** (all negative) ·
gap 0.030922 · range_GPTQ 0.063809 · range_AWQ 0.029341 · max_range 0.063809 ·
**range/gap holds: TRUE**
hierarchical: full-sample GPTQ 0.485714 / AWQ 0.516636, delta −0.030922, winner awq ·
joint_rank_flip_rate 0.0 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.024925 / AWQ 0.011157

### llama32-3b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---|---|---|
| 0 | 0.647000 | 0.626000 | **+0.021000** |
| 1 | 0.645000 | 0.630000 | **+0.015000** |
| 2 | 0.636000 | 0.641000 | −0.005000 |
| 3 | 0.647000 | 0.624000 | **+0.023000** |
| 4 | 0.642000 | 0.607000 | **+0.035000** |

ties: none · **winner flip: TRUE** (seed 2 negative, others positive) ·
gap 0.017800 · range_GPTQ 0.011000 · range_AWQ 0.034000 · max_range 0.034000 ·
**range/gap holds: TRUE**
hierarchical: full-sample GPTQ 0.643400 / AWQ 0.625600, delta +0.017800, winner gptq ·
joint_rank_flip_rate 0.022 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.004615 / AWQ 0.012300

---

## Mechanical application of § 3

| cell | winner flip | range/gap holds |
|---|---|---|
| qwen25-1p5b / mmlu | TRUE | TRUE |
| qwen25-1p5b / gsm8k | FALSE | FALSE |
| llama32-3b / mmlu | FALSE | TRUE |
| llama32-3b / gsm8k | TRUE | TRUE |

- cells with a winner flip: **2 of 4** (threshold: ≥ 1) — **met**
- cells where range/gap holds: **3 of 4** (threshold: ≥ 2) — **met**

Both branches of the disjunction are independently satisfied.

## Decision

**ESCALATE = TRUE.** The § 3 escalation rule fires. The deferred 7B/8B seed cells
(Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct × MMLU, GSM8K) are triggered for
construction and evaluation.

Per § 4 of the mini-grid registration, if escalation fires and all 8 cells
complete, the registered eight-cell H3 Supported/Disconfirmed/Inconclusive rule
is applied exactly as registered. **No H3 verdict is stated here.** This record
applies only the escalation rule; the confirmatory rule is defined over all eight
cells and none of the 7B/8B cells exists yet.

---

## Signature

Escalation rule applied mechanically by the executing session; the numbers above
are read directly from `results/minigrid_escalation/`. Awaiting Amogh's
signature to authorize construction of the 7B/8B cells.

**Signed:** Amogh Singh — escalation affirmed  **Date:** 2026-07-23

Signature recorded by the executing session from Amogh's ruling of 2026-07-23,
which affirmed ESCALATE = TRUE and authorized construction of the 7B/8B cells
under the full standing discipline, subject to an escalation-stage plan and
budget confirmation before any submission.

**Provenance.** Validator `11375247`; paired-seeds + § 3 computation `11376064`;
driver `~/scratch/flipeval/work/escalation_amend.py`; artifacts
`results/minigrid_escalation/{escalation_summary.json, paired_seeds_*.json}`.
Gates behind these cells: re-derived under Amendment 3
(`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`), committed `bd565bd`.
