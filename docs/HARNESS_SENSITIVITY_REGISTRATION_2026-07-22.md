# Harness-Defaults Sensitivity Study — Registration (EXPLORATORY)

Status: **FROZEN 2026-07-22 by Amogh**, after a verbatim review of the ratio
definition (§ 5.1–5.2), the MMLU C ≡ D resolution (§ 3.3), and the declined
early-inspection amendment (§ 9.1). Both design stops raised at first review
were ruled on 2026-07-22 and are resolved in the text below.

**Results-blind at freeze.** No accuracy from any mini-grid confirmatory cell
has been read by anyone at the time of freezing; the only mini-grid surface
inspected during execution has been job health, file coverage, checksums and
receipt pairing. This registration was written and signed before any result of
this study existed, and before `Q̄`'s source data was inspectable at all — see
§ 5.2, which defers the denominator to the mini-grid's registered first
inspection, and § 9.1, which records the shortcut that was declined.

Changes after this line require a dated amendment under "Dated Amendments",
stating whether results had been inspected first (§ 8).

This document does not amend `PREREGISTRATION.md`,
`docs/MINIGRID_REGISTRATION_2026-07-15.md`, or any other frozen document, and it
introduces no confirmatory claim. It registers an **exploratory** study whose
results are inspectable on completion.

> **Both design stops are resolved.** § 3.3 (MMLU conditions C and D coincide)
> and § 9 (the quantization comparator) were surfaced rather than adapted around,
> and Amogh ruled on both on 2026-07-22. The rulings are recorded in place.

**Standing rule for this study, ruled 2026-07-22:** *conditions are read off the
harness, never invented.* A condition that does not correspond to a
configuration some user actually runs would measure a fiction and defeat the
study's purpose. This rule decided § 3.3 and governs every future amendment.

## 1. Question and motivation

**How much does evaluation-harness configuration move accuracy and per-item
answers on a fixed model, relative to how much quantization moves them under
fixed configuration?**

The motivation is not hypothetical. This campaign produced two live
demonstrations inside eight days, both on the pinned `lm_eval` 0.4.12:

1. **`fewshot_as_multiturn` auto-enabled under a chat template.** No flag was
   set; `lm_eval/config/evaluate_config.py:306-308` turns it on whenever
   `apply_chat_template` is set, moving every few-shot exemplar out of the user
   message into its own conversation turn. Recorded in
   `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` Amendment 1.
2. **`strict-match` vs `flexible-extract` on identical generations.** Both
   filters ship in the stock `gsm8k` task and score the *same* model outputs.
   On Qwen2.5-1.5B, strict-match voided **617 of 1,000** responses, **336 of
   which `pilot_eval`'s extractor scores correct**, because the model writes
   `#### $18` and the strict regex rejects the `$`. Accuracy moved 0.232 →
   0.566. Recorded in `docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md` § 4.2.

If configuration-induced churn on a fixed model is comparable to
quantization-induced churn under fixed configuration, that bears directly on how
compression claims should be read. This study measures it rather than asserting
it.

## 2. Stack, models, and what is deliberately not varied

**Stack: `lm_eval` 0.4.12 inside the frozen cell-3 image
(`8260d04c…`), exclusively.** Every condition varies one of lm-eval's own native
knobs. No `pilot_eval` code is touched, so nothing in the freeze fingerprint
changes and no gate or freeze refresh is owed by the study itself.

**Models: FP16 only.**

- `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`
- `meta-llama/Llama-3.2-3B-Instruct` @ `0cb88a4f764b7a12671c53f0838cd831a0843b95`,
  added by this same protocol **only after its seed-0 canary pair passes**.

**No quantized checkpoints are loaded under this protocol.** lm-eval loads
quantized weights through the `transformers`/HfQuantizer path, which is dead in
cell 3 (GPTQ requires the absent `optimum`; AWQ routes into a missing Marlin
runtime — backend probes `11285100`/`11285139`). Resurrecting it for an
exploratory study is not justified.

## 3. Conditions

One factor at a time from a fixed reference. **Reference config**: chat template
on, 3 inline exemplars (GSM8K) / zero-shot (MMLU), `flexible-extract` scoring.
This is the configuration the mini-grid's own reference runs use, so the study
is anchored to a config the campaign already relies on.

### 3.1 GSM8K conditions

| id | condition | flags relative to reference | new generation pass? |
|---|---|---|---|
| REF | reference | `--apply_chat_template --num_fewshot 3 --fewshot_as_multiturn false` | yes |
| A | exemplars as separate turns | `--fewshot_as_multiturn true` | yes |
| B | strict-match scoring | *none* — see below | **no** |
| C | chat template off, raw text | drop `--apply_chat_template` | yes |
| D | harness stock defaults | no flags at all: chat off, `num_fewshot=5` | yes |

**Condition B costs zero GPU time.** The stock `gsm8k` task defines a
`filter_list` with **both** `strict-match` and `flexible-extract`
(`lm_eval/tasks/gsm8k/gsm8k.yaml`, verified in the image), and both are applied
to the *same* generations in a single run. B is therefore read out of REF's own
results file — a genuine rescore of existing generations, exactly as ruled, with
no approximation.

**Condition A requires the chat template.** `evaluate_config.py:309-312` raises
`"When fewshot_as_multiturn is True, apply_chat_template must be set."` A is
defined on top of the chat-on reference, so this is satisfied; the constraint is
recorded because it forbids a "multiturn without chat template" cell, which is
therefore not part of this design.

**Condition D's stock shot count is 5, not 3** (`num_fewshot: 5` in the shipped
task YAML; the campaign's runs log `Overwriting default num_fewshot of gsm8k
from 5 to 3`). D deliberately bundles every stock default at once and is not
one-factor-at-a-time; it is the "what a careless user gets" cell.

### 3.2 MMLU conditions

MMLU is `output_type: multiple_choice` with `metric_list: [acc]` and **no
`filter_list`** (`tasks/mmlu/default/_default_template_yaml`, verified). So B is
inapplicable, and A is inapplicable because the protocol is zero-shot and there
are no exemplars to place. That leaves C and D, as ruled.

### 3.3 RESOLVED: for MMLU, C and D are the same condition

Verified in the image: MMLU's stock `num_fewshot` resolves to **`None` → 0**
(`TaskManager` reports `mmlu_anatomy: num_fewshot=None`; no MMLU YAML sets it),
and MMLU ships **no `filter_list`**. The reference is already zero-shot and has
no extraction filter to vary. **The only difference between stock MMLU and the
reference config is the chat template** — which is exactly what condition C
varies. So:

- **C** = chat template off, zero-shot, `acc`
- **D** = stock defaults = chat template off, zero-shot, `acc`

These are byte-identical configurations.

**Ruled 2026-07-22 (Amogh): run it once and report it as "C ≡ D",** with the
equivalence and its cause stated in the results note. The alternative —
redefining D for MMLU so that it differs from C — was rejected on the standing
rule above: since stock and reference differ *only* in the chat template, any
redefinition would be inventing a configuration no user runs, and measuring it
would defeat the study's purpose.

MMLU therefore contributes **two** cells per model: REF and C ≡ D.

## 4. Items — and the exclusion that matters most

**Item sets: the bridge subsets, exclusively.**

- MMLU: the 4 bridge subjects (`abstract_algebra`,
  `college_computer_science`, `high_school_statistics`, `machine_learning`),
  first 100 test items each = **400 items**.
- GSM8K: test indices **0–199**.

**EXCLUSION — the mini-grid task definitions are never evaluated under this
protocol.** No run registered here may use full MMLU test (14,042 items, 57
subjects) or GSM8K indices 0–999.

*Reason: mini-grid blindness.* The mini-grid's confirmatory cells are not yet
complete, and `docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5 places the first
accuracy inspection after the validator passes over the complete 44-JSONL set.
An exploratory run over the confirmatory item definitions would be an early look
at that surface under another name. The bridge subsets are operational territory
whose FP16 figures are already published in the signed bridge decision record
(MMLU 0.430, GSM8K 0.615).

This exclusion is mechanical, not advisory: every job under this protocol passes
`--limit 200` (GSM8K) or the 4-subject task list with `--limit 100` (MMLU), and
any run whose logged item count is not 200 or 400 is void for this study.

## 5. Registered quantities

Per condition, versus REF, **paired per item** on the identical item set:

1. **Net accuracy delta** — `acc(condition) − acc(REF)`. Signed.
2. **Correctness-state churn** — fraction of items whose correct/incorrect state
   changes between REF and the condition, in either direction. This is the
   primary quantity; it is the same definition of churn the atlas uses
   (`flipeval/core.py`), so the two are comparable.
3. **Answer churn** — fraction of items whose *extracted answer string* changes,
   where extractable. Defined for GSM8K (all conditions) and for MMLU (the
   predicted letter). Reported alongside churn because an answer can change
   while correctness does not.
4. **Directional split** — of churned items, how many went
   correct→incorrect vs incorrect→correct. Reported so a churn figure is never
   mistaken for a net degradation figure.

### 5.1 The pre-named headline statistic

**R = (config-induced correctness-state churn) / (quantization-induced
correctness-state churn), on the same items, same model.**

Both terms must be fixed exactly, before any run:

- **Numerator** `C_cond`: correctness-state churn between REF and condition
  `cond`, FP16 model, on the item set of § 4.
- **Denominator** `Q̄`: the **mean**, over the comparison set defined in § 5.2,
  of correctness-state churn between the FP16 baseline and one quantized variant
  on that same item set, under the fixed bridge configuration.
- `R_cond = C_cond / Q̄`, reported per condition, per task, per model, with
  `C_cond` and `Q̄` always reported beside it so the ratio can never be read
  without its inputs.
- If `Q̄ = 0` the ratio is undefined and is reported as such, never as infinity
  and never by substituting a floor.

### 5.2 The comparison set, and when the denominator may be computed

**Ruled 2026-07-22 (Amogh): two-phase.** `R` is fully defined now; its
denominator is computed later, from a source that does not exist yet. The reason
is in § 9.

**Phase 1 — now, on freeze.** The numerator `C_cond` and every § 5 quantity are
measured immediately. They are FP16-only on the § 4 item sets and touch no
confirmatory surface, so nothing about them waits.

**Phase 2 — after the mini-grid's registered first inspection.** `Q̄` is computed
**only** from mini-grid results, after `scripts/verify_minigrid.py` passes over
the complete 44-JSONL expected set and the first accuracy inspection permitted by
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5 has occurred. It is defined as:

> the mean, over the **ten** Qwen2.5-1.5B quantized variants
> `{gptq_s0…s4, awq_s0…s4}`, of correctness-state churn against that model's
> `fp16` cell, **restricted to the § 4 item subset** (the 400 bridge MMLU items
> and GSM8K indices 0–199), computed per task.

Restriction to the § 4 subset preserves the same-items, same-model control that
is the entire point of the ratio. Taking the denominator from the mini-grid
rather than the bridge also **upgrades it from 3 seeds to 5**, so the two-phase
path yields a strictly better comparator than the one originally contemplated,
at no cost to blindness.

The same construction applies to Llama-3.2-3B once its cells complete.

Until Phase 2, `R` is reported as **pending**, never estimated, and never
substituted with a comparator from another population.

### 5.3 Secondary external comparator — atlas rev-2

Reported alongside `R`, **clearly labelled as external and not same-items**: the
frozen atlas of published compression pairs, rev-2 (`results/identical_score_churn_rev2.csv`,
current at drafting):

| quantity | rev-2 value |
|---|---|
| analysable cells | **1,707** |
| zero-delta cells | 145 (8.49 %) |
| median `accuracy_state_churn` **among zero-delta cells** | **0.0720** |
| mean, same subpopulation | 0.0887 |
| max | 0.3434 |

Two limitations are stated wherever this is cited, not buried:

1. **It is a different population** — other models, other tasks, other
   compression methods — so it loses the same-items and same-model control. It
   contextualises `R`; it is never `Q̄`.
2. **That median is conditioned on zero-delta cells**, i.e. cells whose net
   accuracy is unchanged. It is not a general quantization-churn median. If an
   all-cell median is wanted it is computed at analysis time from the committed
   rev-2 artifact and labelled as such; this registration deliberately does not
   introduce an uncommitted statistic.

rev-2 supersedes the rev-1 figures (1,155 analysable / 113 zero-delta / median
0.0622) that appear in older documents. Whichever revision is current at freeze
time is the one cited, with its revision named.

## 6. Compute cap and scheduling

**Cap: 10 A100-hours total across the whole study, both models.** If the study
reaches the cap, it stops and reports what it has; the cap is not raised without
a dated amendment.

Estimated: **~2.6 A100-hours** for both models (§ 11), leaving the cap as
genuine headroom rather than a target.

**Priority: strictly behind mini-grid work.** Every job under this protocol is
submitted to `-q embers` (preemptible) unless the queue is empty of Stage 6/7
work, and **no job under this protocol may delay a Stage 6 or Stage 7 job**. If
a mini-grid job is pending, sensitivity jobs wait. Preemption is acceptable
here: these runs are cheap and restartable, and nothing downstream blocks on
them.

## 7. Exclusions, stated positively

- No quantized checkpoint is loaded (§ 2).
- No mini-grid task definition is evaluated (§ 4).
- No `pilot_eval` source is modified; the freeze fingerprint is untouched.
- No result of this study may be used to adjust any registered gate, the mini-grid
  escalation rule, or any confirmatory analysis. It is exploratory and
  descriptive.
- This study does not license reading any confirmatory cell. Ruling 7 of
  2026-07-21 stands unchanged.

## 8. Amendment rules

Exploratory status does not license silent change. Any change to the conditions,
the item sets, the registered quantities, or the definition of `R` is a **dated
amendment appended to this document**, stating whether results had been inspected
before the change. Because the study is exploratory, amendments after inspection
are permitted — but they must say so in terms, and a statistic renamed or
redefined after inspection is reported as such in any write-up.

Conditions found infeasible in 0.4.12 are **dropped and recorded**, never
approximated by hand-built substitutes.

## 9. RESOLVED — the quantization comparator, and an option declined

The first-review design ruling described the comparator as "the already-inspected
bridge deltas". That premise was wrong, and the correction was accepted in full
by Amogh on 2026-07-22. Recorded here because the reasoning matters more than the
outcome.

**The factual point.** The signed bridge decision record
(`docs/BRIDGE_DECISION_RECORD_2026-07-20.md`) states in terms: *"no
quantized-model accuracy has been inspected or characterised, and this record
makes no claim about compression quality."* The only bridge accuracies ever
inspected are the two **FP16** baselines. There were no already-inspected
quantization deltas to cite.

**Why computing them would not have been free.** It would have been the first
inspection of quantized accuracy, on items and checkpoints inside the
confirmatory surface:

- The bridge's 400 MMLU items are **a strict subset** of the mini-grid's full
  MMLU test set — same subjects, same first-100 indices, same `item_id` scheme.
- The bridge's GSM8K indices 0–199 are **a strict subset** of the mini-grid's
  0–999.
- The bridge checkpoints `qwen25-1p5b-{gptq,awq}4-seed{0,1,2}` **are** mini-grid
  variants; `configs/pace_minigrid_h3.yaml` points at those exact paths.

Evaluation is deterministic, so those per-item outcomes reappear inside the
mini-grid's confirmatory cells. Computing GPTQ-vs-AWQ churn on them for 3 of the
5 registered seeds is partial information about precisely the quantities the
escalation rule consumes — what
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5 and ruling 7 of 2026-07-21 exist
to prevent.

**Adopted: the two-phase design of § 5.2.** The study's own measurements run
immediately on freeze; only the denominator waits, and it is then drawn from the
mini-grid's registered first inspection over all 5 seeds.

### 9.1 An option considered and declined, 2026-07-22

One route would have produced the ratio roughly five weeks earlier: a dated
amendment to `docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5, permitting an early
partial inspection of the bridge quantized deltas.

**This was considered and declined by Amogh on 2026-07-22.** The stated ground:
*we do not weaken § 5 blindness to get a number five weeks early.* The blindness
is a registered commitment made before any result existed; spending it for the
convenience of an exploratory study would have been the cheapest possible reason
to break it, and the resulting ratio would have been worth less than the
commitment it cost.

This paragraph is recorded deliberately. A declined shortcut leaves no trace in
the artifacts unless it is written down, and "we could have looked early and
chose not to" is evidence about how the campaign was run that cannot be
reconstructed after the fact.

## 10. Reporting

A dated results note, `docs/HARNESS_SENSITIVITY_RESULTS_<date>.md`, carrying:
every condition's raw accuracy and item count; the four § 5 quantities per
condition; `R` with its numerator and denominator beside it (or a statement that
`Q̄` is pending under § 9 option 1); the run identities (job IDs, image sha,
model revisions, full commands); and every condition dropped as infeasible with
its reason.

If a condition's item count is not exactly 400 (MMLU) or 200 (GSM8K), that
condition is void and is reported as void rather than analysed.

## 11. Feasibility and cost, measured not guessed

Per-item rates are taken from this campaign's own completed reference runs on
the same image and hardware (Qwen full MMLU 14,042 items in 4 m 21 s; Qwen GSM8K
1,000 items in 1 h 08 m; Llama GSM8K 1,000 in 1 h 00 m).

| task | condition | items | est. wall (Qwen) |
|---|---|---|---|
| MMLU | REF | 400 | ~3 min (load-dominated) |
| MMLU | C ≡ D | 400 | ~3 min |
| GSM8K | REF (also yields B) | 200 | ~17 min |
| GSM8K | A | 200 | ~17 min |
| GSM8K | C | 200 | ~17 min |
| GSM8K | D (5-shot) | 200 | ~20 min |

Qwen ≈ **1.3 h**; Llama-3.2-3B ≈ **1.3 h** (its 1,000-item GSM8K run was
marginally faster than Qwen's). **Total ≈ 2.6 A100-hours**, against a 10-hour
cap. Six generation jobs per model; condition B adds none.

## Dated Amendments

None.
