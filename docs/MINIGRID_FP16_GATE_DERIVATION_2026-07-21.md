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

---

## Dated Amendments

### Amendment 1 (2026-07-21) — GSM8K metric named, exemplar placement corrected

**Written after the first GSM8K reference attempt was inspected, and before any
replacement run was submitted.** The results seen were FP16 baselines from an
independent harness, not mini-grid results; no mini-grid job exists. Ruled by
Amogh 2026-07-21 on the evidence in
`docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md` § 4.

Two defects in the GSM8K half of array `11338637`, both absent from the MMLU
half, which stands unchanged:

**(a) Exemplar placement.** § 2 asserted that omitting `--fewshot_as_multiturn`
yields exemplars inline in the user message. That is **wrong** for lm-eval
0.4.12, which logs `Using default fewshot_as_multiturn=True` and auto-enables
the behaviour whenever a chat template is applied; its own help reads
"Auto-enabled with `--apply_chat_template`. Use 'false' to disable." The first
run therefore placed each exemplar in its own user/assistant turn pair, while
`PREREGISTRATION.md` (line 43) and `pilot_eval` place all three inline in a
single user message.

**Corrected requirement:** the GSM8K reference passes
`--fewshot_as_multiturn false` explicitly. Rendered prompts must be confirmed
inline before the run is used for any derivation.

**(b) GSM8K metric.** § 2 fixed the task, shot count and item range but never
named which of the harness's two GSM8K metrics to read, leaving the choice to
the derivation script, which took `strict-match`.

**Corrected requirement: the GSM8K metric is `exact_match,flexible-extract`.**

The ground is a property of the two implementations, fixed long before any of
this: `pilot_eval.tasks.extract_gsm8k_answer` reads the `####` marker **and
falls back to the last number in the response**. `flexible-extract` is the
harness filter implementing that same convention; `strict-match` requires the
bare regex `#### (-?[0-9.,]+)` and is a stricter rule than the pipeline being
gated has ever applied. A reference metric stricter than the implementation it
gates measures format compliance rather than the quantity of interest.

**Stated plainly rather than glossed:** this choice was made *after* observing
that `strict-match` produced a Qwen gate of [0.175, 0.289] — one the known-good
bridge implementation (0.615 on 200 items) would fail badly — and it is also the
choice that raises the Qwen figure from 0.232 to 0.566. The justification above
does not depend on which number is larger, but the ordering is recorded here so
a reader can weigh it. The § 3 arithmetic is **not** touched, no tolerance is
widened, and the MMLU gates derived under the original text are unaffected.

Any GSM8K figure produced under `strict-match` or under multiturn placement is
void for gate-derivation purposes and is retained only as the diagnostic record
in `docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md`.

### Amendment 3 (2026-07-23, Amogh Singh) — MMLU FP16 gates voided as derived

**Signed by Amogh 2026-07-23 as amended by him.** Written after the Llama-3.2-3B
MMLU FP16 baseline failed its gate; the failure was in view when this was
decided, and that is stated rather than presented as a pre-specified step.

The four FP16 gates were derived from lm-eval reference runs whose MMLU prompts
differ from the registered `pilot_eval` path in two respects: the reference
supplies a subject-specific system message where `pilot_eval` supplies none, and
`pilot_eval` prefixes each item with `"Question: "` where the reference does not.
The gates therefore gated a benchmark the pipeline does not run. **The MMLU gates
for both models are void.** This was found after the Llama-3.2-3B MMLU baseline
failed its gate at 0.527631 against a floor of 0.5309 — the failure was observed
before the correction, and this amendment is made with that result in view.

The GSM8K clause is struck: Qwen GSM8K matches the reference exactly, and Llama
GSM8K differs only in an injected calendar date. GSM8K gates stand.

The reference is rerun for MMLU only, on both models uniformly, against a custom
task definition that reproduces the registered prompt byte-for-byte, with the
Llama date pinned to 22 Jul 2026 — the date the sealed cells carry. Achieving
this requires passing `date_string` explicitly in the reference invocation, as
lm-eval supplies no date itself; this patch is part of the declared independence
reduction. Gates are re-derived mechanically under the unchanged § 3 tolerance
rule. The reference's independence is hereby reduced from
prompt-construction-plus-scorer to scorer-and-model-loading only; this is a real
loss and is recorded as one.

No quantized result has been inspected. The escalation computation has not run.

#### Record of the decision path (added by the executing session, not part of the signed text)

- The pin was originally ruled 2026-07-23 and corrected to 22 Jul 2026 on the
  finding that the sealed cells carry that date; pinning to the amendment date
  would have reintroduced the defect class under repair. Relying on the cluster
  clock happening to read 22 Jul was rejected: it holds until midnight.
- The alternative of accepting the date line as a bounded deviation was
  considered and rejected, on the ground that it would leave the Llama gate
  permanently unreproducible and one line off the cells it gates.
- Pinning `pilot_eval` instead was rejected on sight: a fingerprinted change to
  the registered eval path, invalidating all 44 completed cells.
- Evidence: Phase-1 metadata diff (no accuracy read); prompt-identity probe
  `11369022`, 72 of 72 reconstructions hash-matching the sealed cells;
  date-pin feasibility probe `11369055`, establishing that `date_string` and
  `strftime_now` appear nowhere in `lm_eval` while the Llama template accepts
  `date_string`.
