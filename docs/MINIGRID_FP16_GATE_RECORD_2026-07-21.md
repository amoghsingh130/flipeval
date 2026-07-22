# Mini-Grid FP16 Gate Record — reference runs and derivation

Executes `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`, whose arithmetic
was committed (`3d24761`) before reference array `11338637` was submitted.

**Outcome: all four gates are derived and committed.** The MMLU half was sound
on the first attempt; the GSM8K half was defective, was ruled on, corrected, and
rerun (§ 4, § 6). No mini-grid job has been submitted and no mini-grid accuracy
exists.

| cell | gate |
|---|---|
| Qwen2.5-1.5B / MMLU | **[0.532538, 0.632538]** |
| Qwen2.5-1.5B / GSM8K | **[0.513000, 0.637000]** |
| Llama-3.2-3B / MMLU | **[0.530900, 0.630900]** |
| Llama-3.2-3B / GSM8K | **[0.635000, 0.755000]** |

## 1. Reference run identity

Array `11338637`, cell-3 image `8260d04c…`, `lm_eval` 0.4.12, A100, dtype
float16, `--seed 0,1234,1234,1234` (the harness default, stated explicitly).
All four array tasks COMPLETED `0:0`.

| cell | job | wall | model revision | n (verified) |
|---|---|---|---|---|
| Qwen2.5-1.5B / MMLU | `_0` | 4 m 21 s | `989aa798…` | 14,042 over 57 subtasks |
| Qwen2.5-1.5B / GSM8K | `_1` | 1 h 09 m | `989aa798…` | 1,000 of 1,319 |
| Llama-3.2-3B / MMLU | `_2` | 5 m 33 s | `0cb88a4f…` | 14,042 over 57 subtasks |
| Llama-3.2-3B / GSM8K | `_3` | 1 h 00 m | `0cb88a4f…` | 1,000 of 1,319 |

Item counts match the mini-grid populations exactly, so § 4 branch 3 (count
mismatch = hard stop) did not fire for any cell.

## 2. Derivation as run

Applied by `~/scratch/flipeval/work/derive_fp16_gates.py` inside the pinned
image (job `11341852`). The script only reads results and applies the frozen
formula; it makes no choices, with the one exception recorded in § 4.2.

| cell | n | p | SE | 2·SE+0.03 | half | gate |
|---|---:|---:|---:|---:|---:|---|
| Qwen / MMLU | 14,042 | 0.582538 | 0.004162 | 0.038323 | **0.050** | **[0.532538, 0.632538]** |
| Llama / MMLU | 14,042 | 0.580900 | 0.004164 | 0.038328 | **0.050** | **[0.530900, 0.630900]** |
| Qwen / GSM8K | 1,000 | 0.232000 | 0.013348 | 0.056697 | 0.057 | [0.175000, 0.289000] — **held** |
| Llama / GSM8K | 1,000 | 0.656000 | 0.015022 | 0.060044 | 0.061 | [0.595000, 0.717000] — **held** |

Both MMLU cells land on the 0.05 floor, exactly as the rule's design
anticipated: at n=14,042 the sampling term is only ~0.008, and the gate is
carried by the implementation-divergence budget.

## 3. MMLU — sound, and why

- **Zero-shot**, so the exemplar-placement defect of § 4.1 cannot apply.
- Chat template applied (verified in the rendered prompts).
- Scored by log-likelihood over the four option letters. There is **no
  answer-extraction filter**, so the metric-convention defect of § 4.2 cannot
  apply either.
- Both accuracies (0.5825, 0.5809) sit mid-band of the pre-fixed plausibility
  range 0.25–0.75, so § 4 branch 1 applies and the arithmetic was applied as
  written.

Qwen's 0.5825 is also consistent with the 2026-07-13 four-subject reference
being lower (0.415): that subset is hard-STEM-skewed, which is precisely why the
bridge range was ruled not to transfer.

## 4. GSM8K — two independent defects, held for a ruling

### 4.1 Exemplar placement is not the registered one

`PREREGISTRATION.md` (line 43) places GSM8K few-shot examples **inline within
the user message**, and `pilot_eval` does exactly that — one user turn
containing all three exemplars and the question.

The reference did **not**. From `logs/reference_11338637_1.err`:

```
INFO [config.evaluate_config:307] Using default fewshot_as_multiturn=True.
```

lm-eval 0.4.12 turns `fewshot_as_multiturn` **on by default** once a chat
template is applied. The rendered prompts confirm it: each exemplar is its own
`user` / `assistant` turn pair. `scripts/slurm/reference_run.sbatch` carries a
comment asserting the opposite — that omitting the flag yields inline placement.
**That comment is wrong** and is corrected regardless of how this is ruled.

The shot count itself was correct (`Overwriting default num_fewshot of gsm8k
from 5 to 3`).

### 4.2 The metric convention was never specified, and the script chose

The frozen derivation rule fixes the task, shot count and item range for GSM8K
but **never names which of the harness's two GSM8K metrics to read**. The
derivation script chose `strict-match`. That was an unregistered choice made in
code, and it is recorded here as such rather than presented as rule-following.

`strict-match` requires the regex `#### (-?[0-9.,]+)`. `pilot_eval`'s own
`extract_gsm8k_answer` takes the `####` marker **and falls back to the last
number in the text** — definitionally the `flexible-extract` convention.

Measured on the Qwen samples: of 1,000 strict rows, **617 scored `[invalid]`,
and 336 of those are answers `pilot_eval`'s extractor scores CORRECT.** The
model routinely emits `#### $18` — right answer, dollar sign, no strict match.
That accounts for the whole gap: 0.232 + 0.336 ≈ 0.568 ≈ the harness's own
`flexible-extract` figure of 0.566.

| cell | strict-match | flexible-extract |
|---|---:|---:|
| Qwen / GSM8K | 0.232 | 0.566 |
| Llama / GSM8K | 0.656 | 0.774 |

So the Qwen strict-match figure measures **format compliance, not arithmetic**,
and a gate of [0.175, 0.289] is one the known-good bridge implementation — which
measured 0.615 on 200 items — would fail by a wide margin. The derivation
document's own words apply: "A gate that a *correct* implementation is expected
to fail is not a gate."

### 4.3 Why this is not fixed unilaterally

Switching to `flexible-extract` now would raise the Qwen number from 0.232 to
0.566, and choosing a metric *after* seeing that the first choice produced an
unusable gate is results-contingent tuning — the thing the derivation document
exists to prevent. There is a defensible independent ground for the switch
(match the reference metric to the pilot's long-standing extraction convention,
a criterion about implementations rather than about which number is larger), but
it was not written down in advance, and the fact that it also happens to be the
choice that makes the gate work is stated here plainly rather than glossed.

The exemplar-placement defect is separate and is not cured by any metric choice.

**Held for Amogh. No GSM8K gate is committed, and `configs/pace_minigrid_h3.yaml`
therefore still fails the validator closed on missing ranges.**

> **RESOLVED BY RULING (Amogh, 2026-07-21).** The hold above is discharged. The
> metric choice is ruled: **`exact_match,flexible-extract`**, on the
> pre-existing-extractor ground — `pilot_eval.tasks.extract_gsm8k_answer` has
> always read the `####` marker with a last-number fallback, which is the
> convention `flexible-extract` implements, so a `strict-match` reference would
> gate the pipeline against a stricter rule than the pipeline has ever applied.
> The ruling requires the disclosure that both metric values were observed
> before the choice was made; that disclosure is present and is retained
> verbatim in the paragraph above and in Amendment 1.
>
> Recorded in **`fe69ab4`** ("Amend the FP16 gate rule: name the GSM8K metric,
> correct exemplar placement"), with the `--fewshot_as_multiturn false`
> requirement following in **`2541984`**. Both the metric name and the
> disclosure sentence were verified present in that amendment text on
> 2026-07-21 before this note was written.
>
> **This item is off the blocked list.** What remains is execution, not a
> decision: the replacement reference array `11342098` must complete, and all
> four ranges are then derived and committed together.

## 5. GSM8K, as re-run — the derivation that stands

Array **`11342098`** (`--array=1,3`), same image and pinned revisions, with
`--fewshot_as_multiturn false` and the metric fixed to
`exact_match,flexible-extract` by Amendment 1 **before submission**. Both tasks
COMPLETED `0:0` (1 h 08 m, 59 m).

**Placement verified mechanically, not by eye.** The derivation script counts
assistant-turn markers in the first logged prompt and refuses to derive a GSM8K
gate unless there is exactly one — inline exemplars produce one (the generation
prompt), multiturn produces four at 3-shot. Both cells reported
`placement OK: 1 assistant turn, exemplars inline`.

| cell | n | p | SE | 2·SE+0.03 | half | gate |
|---|---:|---:|---:|---:|---:|---|
| Qwen / GSM8K | 1,000 | 0.575000 | 0.015632 | 0.061265 | 0.062 | **[0.513000, 0.637000]** |
| Llama / GSM8K | 1,000 | 0.695000 | 0.014559 | 0.059119 | 0.060 | **[0.635000, 0.755000]** |

**Independent sanity check, not part of the rule.** The bridge measured
`pilot_eval` FP16 GSM8K at **0.615** on its 200-item subset. That falls inside
the new Qwen gate [0.513, 0.637] — the correct implementation passes, which is
exactly what the voided strict-match gate of [0.175, 0.289] would have failed.
This is a consistency observation on an already-published bridge figure, not an
input to the derivation; the gate was fixed by the frozen arithmetic before this
comparison was made.

Placement mattered less than the metric: Qwen moved 0.566 → 0.575 between
multiturn and inline, against 0.232 → 0.566 between strict and flexible. Both
defects were corrected anyway, because a reference that runs a prompt the
mini-grid never runs is not a reference regardless of how small the difference
turns out to be.

## 6. What is committed

All four ranges, in `configs/pace_minigrid_h3.yaml` under
`minigrid_acceptance.baseline_accuracy_ranges`, together in a single change and
**before any quantized mini-grid result exists**. The config never passed
through a half-filled state:
`tests/test_minigrid_config.py::test_fp16_ranges_are_either_derived_or_explicitly_pending`
requires all four or none, and it held throughout.

The void first-attempt GSM8K outputs are retained as diagnostic evidence at
`~/scratch/flipeval/reference/{qwen25-1p5b,llama32-3b}.gsm8k.void-multiturn-strictmatch-11338637`
and are not readable by the derivation script.
