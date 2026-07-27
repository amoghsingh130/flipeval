# H3 Eight-Cell Confirmatory Decision Record — 2026-07-26

**STATUS: SIGNED — 2026-07-26, by Amogh Singh.** See § Sign-off. Drafted by the
executing session the same day the analysis ran, as the registration requires,
and signed unmodified: no number, threshold, verdict or tie count in this record
changed between drafting and signature.

**The registered primary confirmatory analysis, run once.** Authorized by Amogh
2026-07-26 after the escalation validator passed (job `11511179`,
`passed: true`, 415/415 checks, 0 errors, 44/44 cells), and after the two
preconditions that ruling attached: an output-path audit and a known-answer
regression against the signed 2026-07-23 record. Both are reported below, before
the result.

**Verdict: H3 is SUPPORTED.**

---

## The rule, quoted (`PREREGISTRATION.md` § "H3 Decision Rule", FROZEN 2026-07-11)

> The primary confirmatory analysis is restricted to 4-bit GPTQ and AWQ over the
> fixed set `S = {Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Llama-3.2-3B-Instruct,
> Llama-3.1-8B-Instruct} × {MMLU, GSM8K}`, which contains eight model-by-benchmark
> cells.
>
> `d_s = acc_GPTQ,s − acc_AWQ,s`. A winner flip occurs in a cell if there are
> registered seeds `s` and `t` for which `sign(d_s) != sign(d_t)` and both
> differences are nonzero. An exact accuracy tie (`d_s = 0`) is counted as
> neither a flip nor a non-flip and is reported separately. Thus a tie cannot
> create or erase a flip between two non-tied seeds.
>
> `gap = |mean_s(acc_GPTQ,s) − mean_s(acc_AWQ,s)|`;
> `range_m = max_s(acc_m,s) − min_s(acc_m,s)`;
> the range/gap criterion holds exactly when `max(range_GPTQ, range_AWQ) >= gap`.
>
> **Supported:** H3 is supported if winner flips occur in at least 3 of the 8
> confirmatory cells, or the range/gap criterion holds in at least 4 of the 8.
>
> **Disconfirmed:** H3 is disconfirmed if winner flips occur in at most 1 of the 8
> and `max(range_GPTQ, range_AWQ) < 0.5 × gap` in at least 6 of the 8.
>
> **Inconclusive:** Every outcome satisfying neither rule is reported as
> inconclusive, without post-hoc promotion.

**Computation.** `flipeval paired-seeds` (registered hierarchical bootstrap, 2000
replicates, RNG seed 0) once per cell over all eight cells, then the rule applied
mechanically. Job `11511724`, driver `~/scratch/flipeval/work/h3_eight_cell.py`.
Per-cell accuracies are the deterministic full-sample values from each cell's own
registered run (`per_seed[s].accuracies`), so the decision test and the reported
hierarchical run share one computation. The per-cell `cell()` function is carried
over **unchanged** from `work/escalation_amend.py`, the driver behind the signed
2026-07-23 escalation decision — which is what makes the regression below a test
of this analysis rather than a restatement of it.

**Run once.** No variation, no unregistered sensitivity check, no second
denominator convention, no re-reading. This document reports the single run.

---

## Precondition 1 — output-path audit (incident 26)

Incident 26 established that a defaulted output path in this codebase can
silently overwrite a completed artifact, and
`results/minigrid_escalation/escalation_summary.json` — which backs the signed,
frozen, paper-cited 2026-07-23 decision — sits in the same tree.

`--out-dir` is **required, with no default**, and the script refuses to overwrite
any existing target or to write inside a sealed run directory. Audit printed by
the job itself before computing anything:

```
  --out-dir: /workspace/results/h3_eight_cell
    writes: h3_eight_cell_summary.json                (exists=False)
    writes: paired_seeds_{qwen25-1p5b,llama32-3b,qwen25-7b,llama31-8b}_{mmlu,gsm8k}.json
                                                       (all exists=False)
  protected artifacts checked against:
    results/minigrid_escalation/escalation_summary.json    (exists=True)
    results/minigrid_validation_summary.json               (exists=True)
    results/escalation_validation_summary.json             (exists=True)

PATH_AUDIT: PASS (no collision with any protected or sealed artifact)
```

**Worth recording: this was closer than it looks.** Four of the nine target
basenames — `paired_seeds_qwen25-1p5b_{mmlu,gsm8k}.json` and
`paired_seeds_llama32-3b_{mmlu,gsm8k}.json` — are **byte-identical to the names of
signed artifacts** already sitting in `results/minigrid_escalation/`. Only the
choice of output directory separates them. Had this analysis defaulted its output
to the directory its predecessor used, it would have overwritten four signed
artifacts in the ordinary course of doing its job. The non-overwrite guard is
what makes that safe rather than lucky.

## Precondition 2 — known-answer regression against the signed record

The four mini-grid cells have registered quantities already computed, signed and
published in `docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md`. They are inputs to
the eight-cell rule regardless, so re-deriving them is a free regression test on a
signed known answer. **The four escalation cells are not read until the four
mini-grid cells reproduce**; a mismatch aborts before they are touched, because it
would mean the analysis code changed behaviour since 2026-07-23 and would put the
published escalation screen and its verdict in question.

| cell | winner flip | gap | range_GPTQ | range_AWQ | max_range | reproduced |
|---|---|---:|---:|---:|---:|---|
| qwen25-1p5b / mmlu | TRUE | 0.012292 | 0.040521 | 0.018445 | 0.040521 | exact |
| qwen25-1p5b / gsm8k | FALSE | 0.096800 | 0.014000 | 0.033000 | 0.033000 | exact |
| llama32-3b / mmlu | FALSE | 0.030922 | 0.063809 | 0.029341 | 0.063809 | exact |
| llama32-3b / gsm8k | TRUE | 0.017800 | 0.011000 | 0.034000 | 0.034000 | exact |

`KNOWN_ANSWER: PASS (4/4 cells reproduce the signed values exactly)` — winner
flips, range/gap verdicts, tie sets, and all four quantities per cell to the six
decimals at which they were published.

---

## Per-cell registered quantities, all eight cells

### qwen25-1p5b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.504415 | 0.533542 | -0.029127 |
| 1 | 0.504914 | 0.518943 | -0.014029 |
| 2 | 0.541803 | 0.529341 | +0.012463 |
| 3 | 0.501282 | 0.528913 | -0.027631 |
| 4 | 0.534254 | 0.537388 | -0.003133 |

ties: none · **winner flip: TRUE** · gap 0.012292 · range_GPTQ 0.040521 · range_AWQ 0.018445 · max_range 0.040521 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.517334 / AWQ 0.529625, delta -0.012292, winner awq · joint_rank_flip_rate 0.0445 · joint_exact_tie_rate 0.0005 ·
seed-level SD GPTQ 0.019130 / AWQ 0.006897

### qwen25-1p5b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.473000 | 0.584000 | -0.111000 |
| 1 | 0.467000 | 0.565000 | -0.098000 |
| 2 | 0.478000 | 0.558000 | -0.080000 |
| 3 | 0.467000 | 0.555000 | -0.088000 |
| 4 | 0.481000 | 0.588000 | -0.107000 |

ties: none · **winner flip: FALSE** · gap 0.096800 · range_GPTQ 0.014000 · range_AWQ 0.033000 · max_range 0.033000 ·
**range/gap holds: FALSE** · max_range < 0.5·gap: TRUE
hierarchical: full-sample GPTQ 0.473200 / AWQ 0.570000, delta -0.096800, winner awq · joint_rank_flip_rate 0.0 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.006340 / AWQ 0.015116

### llama32-3b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.506694 | 0.515667 | -0.008973 |
| 1 | 0.442886 | 0.533400 | -0.090514 |
| 2 | 0.496867 | 0.520154 | -0.023287 |
| 3 | 0.494873 | 0.509899 | -0.015026 |
| 4 | 0.487253 | 0.504059 | -0.016807 |

ties: none · **winner flip: FALSE** · gap 0.030922 · range_GPTQ 0.063809 · range_AWQ 0.029341 · max_range 0.063809 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.485714 / AWQ 0.516636, delta -0.030922, winner awq · joint_rank_flip_rate 0.0 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.024925 / AWQ 0.011157

### llama32-3b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.647000 | 0.626000 | +0.021000 |
| 1 | 0.645000 | 0.630000 | +0.015000 |
| 2 | 0.636000 | 0.641000 | -0.005000 |
| 3 | 0.647000 | 0.624000 | +0.023000 |
| 4 | 0.642000 | 0.607000 | +0.035000 |

ties: none · **winner flip: TRUE** · gap 0.017800 · range_GPTQ 0.011000 · range_AWQ 0.034000 · max_range 0.034000 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.643400 / AWQ 0.625600, delta +0.017800, winner gptq · joint_rank_flip_rate 0.022 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.004615 / AWQ 0.012300

### qwen25-7b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.663296 | 0.656602 | +0.006694 |
| 1 | 0.668495 | 0.659094 | +0.009400 |
| 2 | 0.667213 | 0.665575 | +0.001638 |
| 3 | 0.654679 | 0.653183 | +0.001496 |
| 4 | 0.670346 | 0.658240 | +0.012107 |

ties: none · **winner flip: FALSE** · gap 0.006267 · range_GPTQ 0.015667 · range_AWQ 0.012391 · max_range 0.015667 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.664806 / AWQ 0.658539, delta +0.006267, winner gptq · joint_rank_flip_rate 0.0025 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.006224 / AWQ 0.004537

### qwen25-7b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.769000 | 0.747000 | +0.022000 |
| 1 | 0.728000 | 0.712000 | +0.016000 |
| 2 | 0.721000 | 0.744000 | -0.023000 |
| 3 | 0.743000 | 0.741000 | +0.002000 |
| 4 | 0.753000 | 0.741000 | +0.012000 |

ties: none · **winner flip: TRUE** · gap 0.005800 · range_GPTQ 0.048000 · range_AWQ 0.035000 · max_range 0.048000 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.742800 / AWQ 0.737000, delta +0.005800, winner gptq · joint_rank_flip_rate 0.2575 · joint_exact_tie_rate 0.01 ·
seed-level SD GPTQ 0.019267 / AWQ 0.014195

### llama31-8b / mmlu

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.566444 | 0.582681 | -0.016237 |
| 1 | 0.559749 | 0.586526 | -0.026777 |
| 2 | 0.541233 | 0.588449 | -0.047215 |
| 3 | 0.581256 | 0.562954 | +0.018302 |
| 4 | 0.572497 | 0.586384 | -0.013887 |

ties: none · **winner flip: TRUE** · gap 0.017163 · range_GPTQ 0.040023 · range_AWQ 0.025495 · max_range 0.040023 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.564236 / AWQ 0.581399, delta -0.017163, winner awq · joint_rank_flip_rate 0.0405 · joint_exact_tie_rate 0.0 ·
seed-level SD GPTQ 0.015100 / AWQ 0.010520

### llama31-8b / gsm8k

| seed | acc_GPTQ | acc_AWQ | d_s |
|---|---:|---:|---:|
| 0 | 0.758000 | 0.735000 | +0.023000 |
| 1 | 0.739000 | 0.754000 | -0.015000 |
| 2 | 0.750000 | 0.754000 | -0.004000 |
| 3 | 0.725000 | 0.761000 | -0.036000 |
| 4 | 0.727000 | 0.761000 | -0.034000 |

ties: none · **winner flip: TRUE** · gap 0.013200 · range_GPTQ 0.033000 · range_AWQ 0.026000 · max_range 0.033000 ·
**range/gap holds: TRUE** · max_range < 0.5·gap: FALSE
hierarchical: full-sample GPTQ 0.739800 / AWQ 0.753000, delta -0.013200, winner awq · joint_rank_flip_rate 0.126 · joint_exact_tie_rate 0.003 ·
seed-level SD GPTQ 0.014307 / AWQ 0.010654

---

## Mechanical application of the rule

| cell | winner flip | range/gap holds | max_range < 0.5·gap |
|---|---|---|---|
| qwen25-1p5b / mmlu | **TRUE** | **TRUE** | FALSE |
| qwen25-1p5b / gsm8k | FALSE | FALSE | **TRUE** |
| llama32-3b / mmlu | FALSE | **TRUE** | FALSE |
| llama32-3b / gsm8k | **TRUE** | **TRUE** | FALSE |
| qwen25-7b / mmlu | FALSE | **TRUE** | FALSE |
| qwen25-7b / gsm8k | **TRUE** | **TRUE** | FALSE |
| llama31-8b / mmlu | **TRUE** | **TRUE** | FALSE |
| llama31-8b / gsm8k | **TRUE** | **TRUE** | FALSE |

- cells with a winner flip: **5 of 8** (SUPPORTED threshold: ≥ 3) — **met**
- cells where range/gap holds: **7 of 8** (SUPPORTED threshold: ≥ 4) — **met**
- cells with `max_range < 0.5 × gap`: **1 of 8** (DISCONFIRMED threshold: ≥ 6) — not met

**Supported limb** (flips ≥ 3 **OR** range/gap ≥ 4): **TRUE** — satisfied twice
over, by each disjunct independently.
**Disconfirmed limb** (flips ≤ 1 **AND** strict ≥ 6): **FALSE** — both conjuncts
fail.

The two limbs cannot both hold, and do not; the outcome is classified cleanly by
the frozen text with no interpretation required.

## **H3 VERDICT: SUPPORTED**

## Ties, reported separately under the registered denominator convention

- cells containing at least one exact tie (`d_s = 0`): **0 of 8**
- total tied (model, task, seed) triples: **0 of 40**

No exact tie occurs anywhere in the confirmatory set, so the registered tie rule —
a tie is neither a flip nor a non-flip, and can neither create nor erase a flip
between two non-tied seeds — has no effect on any cell's classification. The
denominator for both criteria remains all 8 cells. Had ties occurred, they would
be excluded from the flip determination within their cell while the cell itself
still counted toward the 8.

## What this verdict does and does not say

It says that over the eight registered confirmatory cells, the choice between
GPTQ and AWQ at 4 bits is not stable against calibration-seed randomness alone:
the winner reverses across seeds in 5 of 8 cells, and in 7 of 8 the spread induced
by seed choice is at least as large as the mean gap between the two methods.

It does not license any statement about 3-bit behaviour, ARC-Challenge,
HellaSwag, calibration-dataset effects, or any cell outside `S`. The registration
is explicit that those are reported separately and cannot substitute for this
rule. Nor does the FP16 baseline gate say anything about quantized accuracy; it
gates the baseline only.

## Provenance

| | |
|---|---|
| Analysis job | `11511724` (COMPLETED, `H3_EIGHT_CELL_EXIT: 0`, 24 s), `logs/h3_eight_cell_11511724.out` |
| Driver | `~/scratch/flipeval/work/h3_eight_cell.py`, `h3_eight_cell.sbatch` |
| Artifacts | `results/h3_eight_cell/{h3_eight_cell_summary.json, paired_seeds_*.json}` (9 files) |
| Escalation validator | `11511179` — `passed: true`, 415 checks, 0 errors, 44/44 cells |
| Mini-grid validator | `11375247` — `passed: true`, 409 checks, 44/44 cells |
| Cell hash-match | `11509865` — PASS, 22/22 Llama-8B cells, no template/tokenizer drift |
| Escalation cells | array `11494460` and predecessors; archived `results/escalation_run_20260726.tar.gz`, both run dirs sealed |
| Mini-grid cells | archived `results/minigrid_run_20260722.tar.gz`, both run dirs sealed |
| Known answer | `docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md` (signed) |
| Bootstrap | 2000 replicates, RNG seed 0, seeds {0,1,2,3,4}, `expected_seed_count=5` |

---

## Sign-off

**SIGNED.** Amogh Singh, 2026-07-26 — verbatim instruction: *"sign H3"*, given
after this record was written and committed at `264095f`, in response to the
reported verdict, the two precondition results, and the per-cell table above.

**What the signature attaches to.** The record as committed at `264095f`, whose
content is unchanged by this signature — only this block and the status header
were added. The verdict, the eight per-cell quantities, the two threshold counts,
the tie counts and both precondition results are byte-identical to what was
reported before the signature was given.

**Results-inspection basis.** This is the registered primary confirmatory
analysis; reading these quantized accuracies is its authorized purpose and the
point at which the campaign's inspection lockdown ends for the confirmatory set.
Before it, the only accuracy any session read from an escalation cell was the
FP16 baseline gate. The analysis ran once, and is not to be run again — no
variation, no unregistered sensitivity check, no second denominator convention,
no re-reading with different rounding.

**What the signature authorizes.** Downstream use of the verdict: selecting the
abstract's H3 variant, filling `\minigridTODO`, and writing the eight-cell result
into the paper. Each of those remains a separate piece of work, to be done
against this record and reviewed on its own terms.

**What it does not authorize.** Any statement beyond the eight cells of `S` at
4 bits. The registration is explicit that 3-bit results, ARC-Challenge,
HellaSwag and calibration-dataset effects are reported separately and cannot
substitute for this rule; the signature does not extend to them.
