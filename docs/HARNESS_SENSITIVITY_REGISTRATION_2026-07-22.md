# Harness-Defaults Sensitivity Study — Registration (EXPLORATORY)

Status: **DRAFT, 2026-07-22, unfrozen.** Drafted by agent; frozen by Amogh on
review. **No job runs under this protocol until the registration is committed.**

This document does not amend `PREREGISTRATION.md`,
`docs/MINIGRID_REGISTRATION_2026-07-15.md`, or any other frozen document, and it
introduces no confirmatory claim. It registers an **exploratory** study whose
results are inspectable on completion.

> **Two blocking items require Amogh's decision before this is frozen.** § 9
> records a design conflict with frozen text that I am not able to resolve
> silently, and § 3.3 records a condition that collapses into another. Both are
> flagged rather than adapted around.

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

### 3.3 BLOCKING: for MMLU, C and D are the same condition

Verified in the image: MMLU's stock `num_fewshot` resolves to **`None` → 0**
(`TaskManager` reports `mmlu_anatomy: num_fewshot=None`; no MMLU YAML sets it).
The reference is already zero-shot, and MMLU has no filters. Therefore:

- **C** = chat template off, zero-shot, `acc`
- **D** = stock defaults = chat template off, zero-shot, `acc`

These are byte-identical configurations. **Options, for Amogh:**

1. **Run once, report as both** (recommended) — one MMLU non-reference cell,
   labelled "C ≡ D", with this equivalence stated in the results. Honest and
   cheapest.
2. **Drop D for MMLU**, keeping C only.
3. **Redefine D for MMLU** to include something stock that the reference
   overrides — but there is nothing else: the reference and stock differ *only*
   in the chat template. Any redefinition would be inventing a condition, not
   reading one off the harness.

I recommend option 1 and have costed the plan that way. Nothing is run either
way until this is settled.

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

### 5.2 The comparison set — see § 9 before reading this as settled

The intended comparison set is the six bridge quantized variants
`{gptq_s0, gptq_s1, gptq_s2, awq_s0, awq_s1, awq_s2}` for Qwen2.5-1.5B, each
against `fp16`, on the 400 MMLU / 200 GSM8K bridge items, from
`results/qwen25_1p5b_bridge_chat/*.jsonl` (archived in
`results/bridge_run_20260720.tar.gz`, sha256 `26497dc3…`).

**§ 9 explains why this set cannot be used at the time the study runs, and what
I propose instead.**

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

## 9. BLOCKING DESIGN CONFLICT — the quantization comparator

The design ruling describes the comparator as "the already-inspected bridge
deltas". **The bridge quantized deltas have not been inspected, and computing
them now would conflict with frozen text.** Stating this rather than proceeding.

**The factual point.** The signed bridge decision record
(`docs/BRIDGE_DECISION_RECORD_2026-07-20.md`) says, in terms: *"no
quantized-model accuracy has been inspected or characterised, and this record
makes no claim about compression quality."* The only bridge accuracies ever
inspected are the two **FP16** baselines. So there is no already-inspected
quantization delta to cite.

**Why computing it now is not a free action.** It would be the first inspection
of quantized accuracy, on items and checkpoints that are inside the confirmatory
surface:

- The bridge's 400 MMLU items are **a strict subset** of the mini-grid's full
  MMLU test set — same subjects, same first-100 indices, same `item_id` scheme.
- The bridge's GSM8K indices 0–199 are **a strict subset** of the mini-grid's
  0–999.
- The bridge checkpoints `qwen25-1p5b-{gptq,awq}4-seed{0,1,2}` **are** mini-grid
  variants; `configs/pace_minigrid_h3.yaml` points at those exact paths.

Evaluation is deterministic, so those per-item outcomes will reappear inside the
mini-grid's confirmatory cells. Computing GPTQ-vs-AWQ churn on them for 3 of the
5 registered seeds is partial information about the very quantities the
escalation rule consumes. That is what
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5 ("first accuracy inspection
happens only after the mini-grid validator passes over the complete 44-JSONL
expected set") and ruling 7 of 2026-07-21 exist to prevent.

**Options.**

1. **Two-phase (recommended).** Freeze this registration in full now, including
   `R`. Run the config-churn half **immediately** — it is FP16-only and touches
   no confirmatory surface, so it is unaffected. Compute `Q̄` and therefore `R`
   **after** the mini-grid validator passes and the registered first inspection
   occurs. The denominator then comes from the mini-grid itself, restricted to
   the § 4 item subset, giving all **5** seeds instead of 3 — a strictly better
   comparator, at zero cost to blindness. The study's own measurements are not
   delayed at all; only the ratio waits.
2. **Use the bridge deltas now.** Requires a dated amendment to the frozen
   mini-grid registration § 5 permitting an early partial inspection, written by
   you, stating that it happened before grid completion. My recommendation is
   against: it spends registered blindness on an exploratory convenience.
3. **Use the atlas as the comparator instead.** `results/identical_score_churn.csv`
   and the atlas population (1,155 published compression cells, median churn
   0.0622) are already inspected and public, so there is no blindness cost. But
   it is a different set of models and items, so the "same items, same model"
   control — the scientific point of the ratio — is lost. Usable as a *secondary*
   comparator for external context, not as `Q̄`.

**Proposal: option 1 as the registered path, with option 3 reported alongside as
a secondary, clearly-labelled external comparator.** Nothing is run until you
rule.

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
