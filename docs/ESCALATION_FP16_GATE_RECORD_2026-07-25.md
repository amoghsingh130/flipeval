# Escalation FP16 Gate Record — all four, committed together (2026-07-25)

Step 5 of the escalation standing order. The four FP16 operational gates for the
escalation grid, derived from the trusted reference runs and committed
**all-or-nothing** into `configs/pace_escalation_h3.yaml` before the validator
runs. Companion to `docs/ESCALATION_FP16_GATE_DERIVATION_2026-07-24.md`, which
fixed the rule; this file records what the rule produced.

## The rule predates every number here

The tolerance rule was committed at **`1b235a8`** (corrected at **`948e780`**:
the byte-identity precondition is MMLU-only, GSM8K uses the stock task as an
independent reference with divergence budgeted by § 3's +0.03). Both commits
land **before any escalation reference job ran** — the earliest reference is
Qwen's `11460030` (2026-07-24), the latest Llama's `11477767` (2026-07-25). The
rule could not have been fitted to a number it had not seen.

Arithmetic, unchanged from the frozen mini-grid rule
(`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` § 3):

```
SE   = sqrt(p(1-p)/n)
half = ceil3(max(0.05, 2*SE + 0.03))
gate = [p - half, p + half]
```

## The four gates

Derivation job **`11478290`**, `DERIVATION_RESULT: ALL4_OK (4/4 cells derived)`.

| model | task | n | p | SE | 2·SE+0.03 | half | **gate** |
|---|---|---:|---:|---:|---:|---:|---|
| qwen25-7b | mmlu | 14,042 | 0.650263 | 0.004024 | 0.038049 | 0.050 | **[0.600263, 0.700263]** |
| qwen25-7b | gsm8k | 1,000 | 0.749000 | 0.013711 | 0.057423 | 0.058 | **[0.691, 0.807]** |
| llama31-8b | mmlu | 14,042 | 0.542444 | 0.004204 | 0.038408 | 0.050 | **[0.492444, 0.592444]** |
| llama31-8b | gsm8k | 1,000 | 0.785000 | 0.012991 | 0.055983 | 0.056 | **[0.729, 0.841]** |

Both MMLU cells and Llama's GSM8K take the 0.05 floor or near it; only Qwen's
GSM8K is driven by its own standard error.

## Outcome, 2026-07-26: all four gates passed, one of them narrowly

The escalation validator (job `11511179`, `passed: true`, 415 checks, 0 errors)
evaluated these gates against the FP16 cells:

| model | task | observed | gate | margin to nearer bound |
|---|---|---:|---|---:|
| qwen25-7b | mmlu | 0.664506 | [0.600263, 0.700263] | 0.035757 |
| qwen25-7b | gsm8k | 0.789000 | [0.691, 0.807] | 0.018000 |
| llama31-8b | mmlu | **0.590514** | [0.492444, **0.592444**] | **0.001930** |
| llama31-8b | gsm8k | 0.789000 | [0.729, 0.841] | 0.052000 |

**Llama-8B MMLU passed by 0.0019, under a ceiling of 0.592444.** Recorded here,
and deliberately not acted on. The gate was derived from a reference run,
committed, and frozen on 2026-07-25 — before any of these cells existed — so a
thin pass is a pass, and thinness is not evidence of anything about the cell.

For context and not for action: at n = 14,042 the binomial standard error on this
baseline is ≈ 0.0042 (the table above records 0.004204). **A 0.0019 margin is well
inside one standard error**, so the observation is statistically indistinguishable
from its own ceiling. That is ordinary sampling behaviour, and it is also an
honest statement of what a gate of this width can and cannot resolve: it
discriminates a broken eval path from an intact one, not a 0.002 shift in
accuracy.

The reason to record it is that it is **evidence the gates were tight enough to
be falsifiable**. A gate nothing could ever fail is decoration; this one came
within a fifth of a percentage point of firing on a cell that was in every other
respect correct. That earns a sentence in the paper's methods discussion.

## § 6 branches — which fired

**Branch 1 for all four cells** (reference completes, accuracy plausible):
apply § 3 arithmetically, record, done.

- **Item counts exact** — 14,042 / 1,000 on every cell (branch 3 not triggered).
- **Plausibility** — MMLU 0.650 and 0.542 inside [0.25, 0.85]; GSM8K 0.749 and
  0.785 inside [0.10, 0.95]. Bounds pre-committed in the derivation doc § 6
  before any escalation reference ran (branch 2 not triggered).
- **GSM8K inline placement** — 1 assistant turn on both models, exemplars
  inline, verified from the samples files.
- **Prompt identity** — zero diffs on both models (branch 4 not triggered):
  Qwen `11459143` 24/24, Llama `11477604` 24/24.

**Regression guard.** Qwen's two ranges were derived and held uncommitted on
2026-07-24. The all-four derivation reproduces them **exactly** —
`[0.600263, 0.700263]` and `[0.691, 0.807]` — confirming the § 3 arithmetic did
not move between the two runs. A drift there would have been a hard stop.

## Llama-8B: no date patch, so no independence reduction

The Llama-8B reference ran with plain `python -m lm_eval` and **no `date_string`
patch**. Its chat template contains no `strftime_now` call and renders the
constant `Today Date: 26 Jul 2024`, verified in-image through the real render
path (probe `11477560`) against a Llama-3.2-3B control that rendered the true
current date in the same environment. See the dated correction in the derivation
doc § 4b.

Consequence worth stating: the 8B reference retains **full invocation
independence** and does not incur the reduction the 3B reference took under
Amendment 3. Its gate exercises scorer, model loading, tokenization *and* an
unpatched invocation — a slightly stronger check than the mini-grid's
counterpart. This is a real difference between the two grids.

## What these gate, and what they do not

These are **FP16 baseline** gates. They check that the eval path was intact —
that the unquantized model scores where an independent harness says it should.
**No quantized accuracy is computed, emitted, or gated anywhere in this
pipeline**, and nothing here is an H3 analysis. The eight-cell H3 rule is
unrun and fires only after the validator passes and Amogh's go.

## Provenance

| | |
|---|---|
| Qwen-7B reference | `11460030` (MMLU 11:59, GSM8K 1:17:52), 2026-07-24 |
| Llama-8B reference | `11477767` (MMLU 6:04, GSM8K 1:29:23), 2026-07-25 |
| Identity probes | `11459143` (Qwen), `11477604` (Llama) — both zero-diff |
| Date probe | `11477560` |
| Derivation | `11478290`, `work/escalation_derive_all4.py` |
| Rule commits | `1b235a8`, corrected `948e780` |
| Model revisions | Qwen `a09a3545…`, Llama `0e9e39f2…` |
