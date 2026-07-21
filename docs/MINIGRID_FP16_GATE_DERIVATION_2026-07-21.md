# Mini-Grid FP16 Operational Acceptance Ranges — Derivation Rule

**Written 2026-07-21, BEFORE any reference run for these ranges was submitted and
before any mini-grid accuracy of any kind exists.** This document fixes the
*procedure and the arithmetic*; the resulting numbers are filled into
`configs/pace_minigrid_h3.yaml` mechanically, with no judgement left over once
the reference numbers are read.

This is an **operational** document. It does not amend `PREREGISTRATION.md` or
`docs/MINIGRID_REGISTRATION_2026-07-15.md`. It executes the procedure that
mini-grid registration § 2 already froze:

> Llama-3.2-3B FP16 operational acceptance ranges: to be derived from a trusted
> lm-evaluation-harness reference run on the pinned snapshot (procedure of
> `docs/MMLU_REFERENCE_RUN.md`) and committed into the mini-grid config **before
> any quantized Llama-3.2-3B result exists**. This registration deliberately
> freezes the derivation procedure, not the values.

## 1. Why the scope is four ranges, not one

Registration § 2 names Llama-3.2-3B only, because at drafting time the Qwen
ranges were believed to carry over from the bridge. They do not.

The corrected Qwen bridge gate — MMLU `[0.365, 0.465]`, from
`docs/GATE_DECISION_2026-07-13.md` — was derived on the bridge's **400-item,
4-subject** MMLU subset (`abstract_algebra`, `college_computer_science`,
`high_school_statistics`, `machine_learning`), which that same decision record
describes as "hard-STEM-skewed". The mini-grid runs **full MMLU test: 14,042
items across all 57 subjects** (`configs/main_grid_manifest.yaml`,
`selection: full`). These are different item populations, and an accuracy range
measured on one is not a gate for the other. The same applies to GSM8K: the
`[0.55, 0.65]` range was a *declared* expectation checked against 200 items, and
the mini-grid runs 1,000.

Applying the bridge ranges to mini-grid FP16 results would be a gate that
describes a different benchmark. Ruled by Amogh 2026-07-21, results-blind:
derive **four** ranges — {Qwen2.5-1.5B-Instruct, Llama-3.2-3B-Instruct} ×
{MMLU full test, GSM8K indices 0–999} — from reference runs on the actual
mini-grid task definitions. The bridge ranges remain valid for the bridge and
are not altered.

## 2. Reference run identity (the trusted side)

Per `docs/MMLU_REFERENCE_RUN.md`, the reference is an independent
implementation — `lm-evaluation-harness`, pinned at **0.4.12** in the frozen
cell-3 image — run against the **pinned model snapshot**, never a mutable alias.

| axis | value |
|---|---|
| harness | `lm_eval` 0.4.12 (cell-3 image sha `8260d04c…`) |
| Qwen | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Llama | `meta-llama/Llama-3.2-3B-Instruct` @ `0cb88a4f764b7a12671c53f0838cd831a0843b95` |
| MMLU | lm-eval task group `mmlu`, all 57 subjects, `--num_fewshot 0`, no `--limit` |
| GSM8K | lm-eval task `gsm8k`, `--num_fewshot 3`, `--limit 1000` (first 1,000 test items, dataset order) |
| prompting | `--apply_chat_template` (chat template ON for FP16 baselines, registered) |
| dtype | `float16` |
| logging | `--log_samples`, output hashes recorded |

The reference is deliberately **not** a replica of `pilot_eval`. It uses the
harness's own prompt construction and scorer. That independence is the entire
point — it is what makes the resulting range a check on our implementation
rather than a restatement of it.

**Shot counts, and why.** MMLU is zero-shot on both sides: the registered pilot
protocol is zero-shot (`MMLU_TEMPLATE` carries no exemplars) and the 2026-07-13
reference used `--num_fewshot 0`. GSM8K is **3-shot on both sides**: mini-grid
registration § 2 binds the mini-grid to the bridge configuration's GSM8K
prompt, and that prompt is `pilot_eval.tasks.GSM8K_FEWSHOT` — a fixed **three**
worked examples inline in the user message (`fewshot:` in the run config is a
boolean switch on that block, not a count; ruled by Amogh 2026-07-21, see
§ 6). Matching the reference to 3 exemplars keeps the comparison to a
prompt-format and exemplar-selection difference rather than adding a shot-count
difference on top of it.

**Known and accepted:** lm-eval's GSM8K prompt differs from `pilot_eval`'s
inline 3-example prefix (different exemplars, drawn from the train split, and a
different answer-extraction rule), and lm-eval's MMLU prompt differs from
`MMLU_TEMPLATE`.
The Qwen MMLU precedent measured this divergence directly — 0.430 (pilot) vs
0.415 (reference), 72.5 % item-level agreement — and the gate decision accepted
aggregate equivalence as the criterion. § 3 budgets for exactly this.

## 3. The tolerance rule — fixed now, applied mechanically later

For each (model, task) cell, let `p` be the reference accuracy and `n` the item
count (MMLU 14,042; GSM8K 1,000). Then:

```
SE   = sqrt( p * (1 - p) / n )
half = max( 0.05 , 2*SE + 0.03 )        # rounded UP to 3 decimals
gate = [ p - half , p + half ]          # clipped to [0, 1]
```

Every term is pre-justified:

- **`2*SE`** — sampling noise in the reference measurement itself. This is the
  term the 2026-07-13 Qwen gate used ("tolerance ≈ 2× the binomial standard
  error at n=400").
- **`+ 0.03`** — cross-implementation divergence between the harness and
  `pilot_eval`. Set at **twice the single measured instance** of that divergence
  (|0.430 − 0.415| = 0.015, Qwen MMLU, `docs/GATE_DECISION_2026-07-13.md`). At
  n=400 this term was invisible inside the sampling noise; at n=14,042 sampling
  noise nearly vanishes (2·SE ≈ 0.008) and it would dominate a gate that ignored
  it. A gate that a *correct* implementation is expected to fail is not a gate.
- **`max(…, 0.05)`** — a floor that reproduces the existing Qwen bridge gate
  exactly (0.415 ± 0.05, where 2·SE = 0.0493). It keeps the mini-grid gates no
  tighter than the one already accepted for the bridge.

### What these ranges are, and are not

These are **operational breakage detectors**, applied to FP16 baselines only.
They exist to catch a wrong checkpoint, a dead or substituted kernel, a corrupted
prompt path, or a truncated item set. They are not a scientific claim about model
quality and they are not a hypothesis test.

**Quantized accuracies are never gated.** No range in
`configs/pace_minigrid_h3.yaml` applies to any GPTQ or AWQ variant, and no such
range may be constructed after quantized results are seen. This restates the
runbook rule and the bridge decision record's identical statement.

## 4. Pre-fixed interpretation branches

Fixed before the reference results exist, mirroring
`docs/MMLU_REFERENCE_RUN.md` § interpretation:

1. **Reference completes, accuracy plausible** (MMLU within roughly 0.25–0.75,
   GSM8K within roughly 0.10–0.90 — the ranges outside which a chat-template
   instruct model of this size would indicate a broken run rather than a result):
   apply § 3 arithmetically, write the four ranges into the mini-grid config,
   done. No inspection of anything else.
2. **Reference accuracy outside those plausibility bounds, or the job errors**:
   the *reference* is treated as broken, not the range rule. Diagnose the
   reference run (chat template applied? correct snapshot? correct subject set?
   item count as expected?) before deriving anything. Under no circumstances is
   the tolerance widened to accommodate a surprising reference number — that
   would be tuning a gate to a result.
3. **Item counts do not match 14,042 / 1,000**: hard stop. A count mismatch means
   the reference and the mini-grid are not measuring the same population, which
   invalidates the derivation regardless of the accuracy value.

Under no branch is `§ 3`'s arithmetic changed after a reference number is read.

## 5. Recording

The reference run's identity (job IDs, harness version, GPU, full commands,
snapshot revisions, item counts, output hashes) and the four derived ranges are
recorded in `docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md`, alongside the
arithmetic worked term by term so the derivation is checkable without rerunning
anything. The ranges are committed into `configs/pace_minigrid_h3.yaml` in the
same change, **before any quantized mini-grid result exists**.

## 6. Dependency: the GSM8K shot-count clarification

§ 2's choice of `--num_fewshot 3` rests on a finding about what the bridge
configuration actually ran, recorded separately in
`docs/GSM8K_FEWSHOT_FINDING_2026-07-21.md`. That finding requires a dated
amendment to `docs/MINIGRID_REGISTRATION_2026-07-15.md` written by Amogh. If the
amendment resolves the shot count differently, the GSM8K half of this derivation
must be rerun at the ruled count **before** any mini-grid GSM8K result exists;
the MMLU half is unaffected.
