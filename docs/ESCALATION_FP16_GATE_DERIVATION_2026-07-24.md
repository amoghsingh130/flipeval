# Escalation FP16 Operational Acceptance Ranges — Derivation Rule

**Written 2026-07-24, BEFORE any escalation reference run is submitted and before
any escalation accuracy of any kind exists.** This document fixes the *procedure,
the arithmetic, and the two-track sequencing*; the resulting four numbers are
filled into the escalation eval config mechanically, with no judgement left over
once the reference numbers are read.

This is an **operational** document. It does not amend `PREREGISTRATION.md`,
`docs/MINIGRID_REGISTRATION_2026-07-15.md`, or the escalation registration. It
executes, for the four new confirmatory cells, the same derivation procedure that
mini-grid registration § 2 froze and that
`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` (as corrected by Amendment 3)
already carried out for the 1.5B/3B cells. **The derivation procedure is frozen;
the values are not.**

The escalation stage is authorized by `docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md`
(ESCALATE=TRUE) and planned in `docs/ESCALATION_STAGE_PLAN_2026-07-23.md` § 4
("FP16 gates — identity-first"). This document is that section's execution record.

## 1. Scope — four ranges

Four FP16 operational acceptance ranges, one per escalation cell:

| model | tag | pinned revision | tasks |
|---|---|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | `qwen25-7b` | `a09a35458c702b33eeacc393d103063234e8bc28` | MMLU full test, GSM8K 0–999 |
| `meta-llama/Llama-3.1-8B-Instruct` | `llama31-8b` | `0e9e39f249a16976918f6564b8830bc894c89659` | MMLU full test, GSM8K 0–999 |

Item populations are identical to the mini-grid: MMLU is the **full test split,
all 57 subjects, 14,042 items**; GSM8K is the **first 1,000 test items in dataset
order**. Revisions are the ones pinned in `configs/main_grid_manifest.yaml`; a
reference against a mutable alias is not an acceptable reference
(`docs/MMLU_REFERENCE_RUN.md`).

These ranges apply to **FP16 baselines only**. No range here applies to any GPTQ
or AWQ variant, and none may be constructed after any quantized escalation result
is seen. This restates the runbook rule, the bridge decision record, and the
mini-grid derivation's identical statement.

## 2. Reference run identity — the trusted side, post-Amendment-3

The reference is an independent implementation — `lm-evaluation-harness` pinned at
**0.4.12** in the frozen cell-3 image (sha `8260d04c…`) — run against the pinned
model snapshot. It adopts the **Amendment-3-corrected** form from the mini-grid,
not the original stock-task form, because the original was found to gate a
benchmark the pipeline does not run.

| axis | value |
|---|---|
| harness | `lm_eval` 0.4.12 (cell-3 image sha `8260d04c…`) |
| MMLU | custom task `mmlu_pilot` (`--include_path .../custom_tasks/mmlu_pilot`), all 57 subjects, `--num_fewshot 0`, no `--limit` |
| GSM8K | stock `gsm8k`, `--num_fewshot 3`, `--limit 1000`, `--fewshot_as_multiturn false` |
| prompting | `--apply_chat_template` (chat template ON for FP16 baselines, registered) |
| dtype | `float16` |
| seed | `--seed 0,1234,1234,1234` (lm-eval 0.4.12 default, stated explicitly) |
| logging | `--log_samples`, output hashes recorded |

**MMLU uses the custom `mmlu_pilot` task, not stock `mmlu`.** Amendment 3
(2026-07-23) established that stock lm-eval MMLU supplies a subject-specific system
message where `pilot_eval` supplies none, and omits `pilot_eval`'s `"Question: "`
stem — so a stock-MMLU reference gates a prompt the pipeline never renders. The
`mmlu_pilot` custom task reproduces the registered `pilot_eval` MMLU prompt
byte-for-byte (system-message-empty + `"Question: "` stem). It is model-independent
— only the tokenizer differs — so it applies to qwen25-7b and llama31-8b
unchanged; this document's precondition (§ 4) is what *proves* that for each model
rather than assuming it.

**GSM8K uses the stock task**, exactly as the mini-grid did: the mini-grid found
GSM8K needed no custom task (Qwen matched the reference exactly; Llama differed
only by an injected calendar date, which a date pin resolves). `--num_fewshot 3`
because mini-grid registration Amendment 2 binds the pipeline to the bridge's
`GSM8K_FEWSHOT` block of **three** inline exemplars; `--fewshot_as_multiturn
false` because lm-eval 0.4.12 auto-enables multiturn under `--apply_chat_template`,
which would split the exemplars into separate turns. GSM8K metric is
`exact_match,flexible-extract` (Amendment 1): `pilot_eval.extract_gsm8k_answer`
reads the `####` marker and falls back to the last number, which is
`flexible-extract`, not `strict-match`.

**Independence, honestly bounded.** As recorded in Amendment 3, the reference's
independence is reduced from prompt-construction-plus-scorer to
scorer-and-model-loading only. That is a real loss and is carried forward here
deliberately: the alternative (a reference matching a prompt the cells never
render) is worse. The § 3 tolerance already budgets for the residual harness/
`pilot_eval` divergence.

## 3. The tolerance rule — fixed now, applied mechanically later

Unchanged from `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` § 3, reproduced
verbatim and applied to the four escalation cells with **no new term and no
per-cell adjustment**. For each (model, task) cell, let `p` be the reference
accuracy and `n` the item count (MMLU 14,042; GSM8K 1,000):

```
SE   = sqrt( p * (1 - p) / n )
half = max( 0.05 , 2*SE + 0.03 )        # rounded UP to 3 decimals
gate = [ p - half , p + half ]          # clipped to [0, 1]
```

Every term is pre-justified in the mini-grid derivation and that justification
carries over unchanged:

- **`2*SE`** — sampling noise in the reference measurement itself.
- **`+ 0.03`** — cross-implementation divergence between the harness and
  `pilot_eval`, set at twice the single measured instance (|0.430 − 0.415| =
  0.015, Qwen MMLU, `docs/GATE_DECISION_2026-07-13.md`). At n=14,042 sampling
  noise nearly vanishes (2·SE ≈ 0.008) and this term would otherwise dominate; a
  gate a *correct* implementation is expected to fail is not a gate.
- **`max(…, 0.05)`** — a floor reproducing the accepted bridge gate width.

These are **operational breakage detectors** applied to FP16 baselines only — they
catch a wrong checkpoint, a dead or substituted kernel, a corrupted prompt path, or
a truncated item set. They are not a scientific claim and not a hypothesis test.
**Quantized accuracies are never gated.**

## 4. Precondition — prompt identity, and why the two tracks differ

Per plan § 4, the reference for each model runs only after a prompt-identity
precondition passes with **zero byte-diffs**. Any diff is a **hard stop and a
return to Amogh**, never a silently-tolerated deviation. What that precondition
*can be checked against*, and therefore *when it can run*, differs between the two
models — and that difference is the reason the tracks are split. It is a property
of the chat templates, not of scheduling convenience.

**The asymmetry.** The `pilot_eval` prompt is a pure function of (item, tokenizer,
chat template). For **Qwen** the chat template injects no calendar date, so that
function is fully determined now: what the future Qwen eval cells will render is
knowable today from the tokenizer alone. For **Llama-3.1-8B** the chat template
injects *today's date* (like Llama-3.2-3B before it), so the rendered prompt
depends on the wall-clock date the eval cell actually runs. That date is
**unknowable before the cell runs**, and the run's queue timing is
nondeterministic. Pinning a *guessed* date now would reproduce the Amendment-3
defect in mirror image: a reference matching prompts the cells never render.

### 4a. Qwen-7B track — runs now (date-free)

The Qwen-7B precondition is a **reconstruction-identity** check that needs no
sealed eval cell, because Qwen is date-free:

> Render the `mmlu_pilot` custom task through the harness on `qwen25-7b`, and
> render the same MMLU items through the registered `pilot_eval` path
> (`render_prompt(tok, item.prompt, "chat")`) on the same pinned tokenizer.
> Hash both and require byte-identical prompt hashes on every checked item
> (≥ 2 subjects, ≥ 10 items each).

The byte-identity precondition covers **MMLU only** — the cell where the reference
uses a custom task built to reproduce the registered prompt exactly. **GSM8K is
deliberately not byte-identical:** its reference is the *stock* lm-eval task, an
independent implementation whose exemplar set and answer-extraction differ from
`pilot_eval.GSM8K_FEWSHOT`, and that divergence is exactly what the § 3 `+0.03`
term budgets for. Requiring byte-identity there would defeat the purpose of an
independent reference. (The mini-grid treated GSM8K the same way: its identity
work only confirmed the `pilot_eval` reconstruction was faithful and, for the
date-injecting model, that the sole *template* divergence was the calendar date.)

This MMLU check is the escalation analogue of the mini-grid's custom-task identity
check (job 11373459), differing only in that it compares the custom task against
the **`pilot_eval` reconstruction** rather than against sealed cells — because for a
date-free model the reconstruction *is* what the cells will contain, exactly, and
no cell need exist to know it. On zero MMLU diffs the Qwen-7B reference runs (MMLU
via `mmlu_pilot`, GSM8K stock); its two ranges are derived mechanically under § 3
and **held uncommitted** (see § 5).

### 4b. Llama-8B track — deferred by design (date-bound)

The Llama-8B reference **runs after the Llama-8B FP16 eval cells exist**, with the
identity probe hash-matching reconstructed prompts against those **sealed cells** —
date line included — and the reference date-pinned to the date those cells carry,
captured from the cell and never assumed. This is exactly the Amendment-3 pattern
(custom `mmlu_pilot` task + `date_string` pinned to the cell date), adopted here
**deliberately as the designed path**, not improvised after a failure.

This deferral is protocol, not a scheduling accident. Its two reasons, recorded
now so they read as designed:

1. **The cell date is unknowable pre-run.** The only date that makes the Llama
   reference reproduce the cells it gates is the date the cells themselves carry,
   and that is fixed only when the cells run.
2. **Queue timing is nondeterministic.** There is no date one could pin in advance
   that is guaranteed to equal the eventual cell date; relying on the cluster
   clock reading a particular day holds only until midnight.

**Why deferring the reference past its eval cells introduces no blindness
problem.** The reference is **FP16-only**. Running it after the FP16 eval cells
exist reads nothing quantized and states no accuracy — the identity probe reads
only `item_id`, `prompt_hash`, and metadata from the sealed cells (never gold,
prediction, scores, or raw output), and the reference measures the FP16 model on an
independent harness. The **one ordering that matters is preserved**: all four gates
are committed **before the validator runs**, so no gate is ever derived or adjusted
with a quantized escalation result in view. The eval cells stay sealed throughout,
as standing.

## 5. All-or-nothing commit, then validator

The four gates are committed **together, all-or-nothing** — the escalation eval
config never passes through a half-filled state. Concretely:

1. Qwen-7B ranges are derived now and **held uncommitted** until the Llama-8B
   ranges exist. Two committed cells and two absent cells would be a half-filled
   gate set; the config must gain all four in one change or none.
2. When the Llama-8B eval cells exist, its reference runs (§ 4b), its two ranges
   are derived under the same § 3 arithmetic, and **all four** land in the
   escalation eval config's `baseline_accuracy_ranges` in a single commit, with the
   in-image gate green and a freeze refresh — mirroring the mini-grid, where the
   validator fails closed until the ranges are present.
3. Only then does the validator run over the complete new-cell set. The
   post-validator go to Amogh, and the eight-cell H3 rule, follow as in plan § 6–7.

The reference runs' identity (job IDs, harness version, GPU, full commands,
snapshot revisions, item counts, output hashes) and the four derived ranges,
worked term by term, are recorded in
`docs/ESCALATION_FP16_GATE_RECORD_2026-07-24.md` alongside this rule.

## 6. Pre-fixed interpretation branches

Fixed before any escalation reference result exists, mirroring the mini-grid
derivation § 4 and `docs/MMLU_REFERENCE_RUN.md`:

1. **Reference completes, accuracy plausible** (MMLU roughly 0.25–0.85, GSM8K
   roughly 0.10–0.95 for a chat-template instruct model of this size — outside
   these a broken run is likelier than a result): apply § 3 arithmetically, record
   the range, done. No inspection of anything else.
2. **Reference accuracy outside those plausibility bounds, or the job errors**:
   the *reference* is treated as broken, not the range rule. Diagnose the reference
   (chat template applied? correct snapshot? correct subject set / item count?
   custom task loaded? for Llama, date pin equal to the cell date?) before deriving
   anything. **Under no circumstances is the tolerance widened to accommodate a
   surprising reference number.**
3. **Item counts do not match 14,042 / 1,000**: hard stop. A count mismatch means
   the reference and the escalation cells are not measuring the same population.
4. **Any prompt-identity diff (§ 4)**: hard stop, return to Amogh. No reference is
   run, and no gate is derived, from a prompt path that does not reproduce the
   registered one byte-for-byte.

Under no branch is § 3's arithmetic changed after a reference number is read.
