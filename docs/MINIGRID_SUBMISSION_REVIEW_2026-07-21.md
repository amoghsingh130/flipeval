# Mini-Grid Submission Review Pack

**Prepared 2026-07-21 for Amogh's review. Nothing here authorises fan-out.**
Stage 5 of `docs/PACE_EXECUTION_PLAN_2026-07-15.md` is complete when this pack
is accepted; Stage 6 submission remains gated on an explicit go.

No mini-grid job has been submitted. No mini-grid accuracy of any kind exists.
The only accuracy figures anywhere in this pack are FP16 baselines from
independent trusted reference runs, which are the registered gate inputs.

---

## 1. What was asked for, and where it landed

| # | Deliverable | Status | Artifact |
|---|---|---|---|
| 1 | Mini-grid config, 22 variants | done | `configs/pace_minigrid_h3.yaml` |
| 2 | Mini-grid validator | done | `scripts/verify_minigrid.py` (+ `verify_common.py`) |
| 3 | FP16 reference ranges (4, not 1 — see § 2b) | done | `reference_run.sbatch`, jobs `11338637` + `11342098` |
| 4 | Wall-time item: TRITON or splitting | done, resolved | `docs/PACE_ENVIRONMENT_NOTE.md` § RESOLVED 2026-07-21 |

Supporting, not asked for but required by what was found:

| Artifact | Why it exists |
|---|---|
| `docs/MINIGRID_REGISTRATION_2026-07-15.md` § Amendment 2 | § 3 below — the registration contradicted itself |
| `docs/GSM8K_FEWSHOT_FINDING_2026-07-21.md` | the supporting finding for that amendment |
| `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` | § 4 — the bridge gates do not transfer |
| `scripts/slurm/run_minigrid.sbatch`, `verify_minigrid.sbatch` | the config is unrunnable without them |
| `build_quantized.sbatch` parameterisation | it hard-coded Qwen and 3 seeds |

---

## 2. Three things I found before writing anything, and how they were ruled

Each changed a deliverable, so each was surfaced rather than absorbed.

**(a) `fewshot: 1` never meant one example.** `pilot_eval/tasks.py:99` treats
`fewshot` as a **boolean switch** on `GSM8K_FEWSHOT`, a fixed block of **three**
worked examples. The validated bridge therefore ran GSM8K 3-shot, while
mini-grid registration § 2 says "1 few-shot example ... matching the validated
bridge configuration" — two clauses naming two different prompts, inside a
frozen document. **Ruled (Amendment 2, dictated by Amogh, appended verbatim):**
the bridge artifact binds, "1" was a drafting error, `fewshot` keeps its boolean
semantics. The mini-grid's GSM8K block is byte-identical to the bridge's, and a
test asserts the emitted prompt still carries three exemplars.

**(b) The Qwen bridge FP16 gates do not describe the mini-grid.** MMLU
`[0.365, 0.465]` was derived on the bridge's 400-item, 4-subject subset that
`docs/GATE_DECISION_2026-07-13.md` itself calls hard-STEM-skewed; the mini-grid
runs full MMLU, 14,042 items over 57 subjects. GSM8K `[0.55, 0.65]` was a
declared expectation checked on 200 items, not 1,000. The execution plan's
Stage 6 line ("bridge-corrected range for Qwen; Stage 5 reference range for
Llama") assumed a transfer that does not hold. **Ruled:** derive four ranges,
both models × both tasks, from reference runs on the actual mini-grid task
definitions.

**(c) Dataset revisions were declared but never enforced.** `tasks.py` called
`load_dataset` with no `revision=`, so MMLU and GSM8K resolved to whatever
`main` pointed at. Writing pinned revisions into the config would have been a
claim the pipeline did not honour. **Ruled:** thread it through — mini-grid
cells are confirmatory cells, so data identity binds here in a way it did not
for the operational bridge.

---

## 3. The config — `configs/pace_minigrid_h3.yaml`

2 models × {fp16, gptq s0–4, awq s0–4} = **22 variants** × 2 tasks = **44
JSONLs**, at the identities pinned in `configs/main_grid_manifest.yaml`.

- **MMLU** — full test split, all **57 subjects listed explicitly** rather than
  wildcarded, so the item population is auditable from the config alone. Their
  test splits sum to exactly **14,042**, verified in-image against pinned
  revision `c30699e8…` (job `11338439`). `limit` is `null`, because the loader
  applies `limit` *per subject*.
- **GSM8K** — `limit: 1000` (indices 0–999, dataset order) at pinned revision
  `740312ad…`; `fewshot: 1` retained so the prompt is byte-identical to the
  bridge, with the boolean semantics called out inline so the field is never
  misread as a count again.
- **Chat prompts** on both tasks, for every method including FP16 baselines.
- **Every quantized variant names its backend explicitly** — `gptqmodel_torch`
  or `awq_gemm`. Framework kernel auto-selection is the campaign's known hazard
  class, and the validator cross-checks the *recorded* backend and kernel
  against the declaration.

New schema: a `models:` list, one entry per cell pair, with **tasks shared at
the top level**. That is deliberate — the registered parity requirement is that
every variant of a model sees the identical item set, and one shared task list
makes divergence unrepresentable rather than merely detected afterwards. Model
selection via `--model-tag` is **required and never defaulted**: silently
picking the first model would evaluate the wrong weights into a correctly-named
run directory.

---

## 4. The validator — `scripts/verify_minigrid.py`

Enforces, over the complete expected set and nothing less: 44 JSONLs; exact
counts (MMLU 14,042, GSM8K 1,000); item/gold/prompt-hash parity across all 11
variants within each model; chat prompt metadata; the pinned dataset revisions;
FP16 gates per model per task; receipt pairing for **5 seeds × 2 models ×
{GPTQ, AWQ}**; and recorded backend/kernel matching the config.

Two checks have no bridge counterpart:

- **Cross-model artifact disjointness.** Calibration eligibility is
  tokenizer-dependent, so two models can never legitimately share a C4 artifact.
  A shared one means a build read the wrong model's file — and the per-model
  checks cannot see it, because each model's receipts stay internally
  consistent.
- **Missing FP16 ranges are a hard failure**, not a skipped check. A grid
  validated without its FP16 gates has no baseline evidence that the eval path
  was intact.

It computes **no quantized accuracy**. `verify_bridge.py`'s primitives moved to
`verify_common.py` so the two validators cannot drift; bridge behaviour is
unchanged and its existing tests still pin it.

---

## 5. FP16 reference ranges — derived and committed

**The tolerance rule was committed (`3d24761`) before any reference run was
submitted**, so no gate could be tuned to a reference number:

```
SE   = sqrt( p*(1-p)/n )
half = max( 0.05 , 2*SE + 0.03 )        # rounded UP to 3 decimals
gate = [ p - half , p + half ]          # clipped to [0, 1]
```

| cell | n (verified) | p | half | **gate** |
|---|---:|---:|---:|---|
| Qwen2.5-1.5B / MMLU | 14,042 | 0.582538 | 0.050 | **[0.532538, 0.632538]** |
| Qwen2.5-1.5B / GSM8K | 1,000 | 0.575000 | 0.062 | **[0.513000, 0.637000]** |
| Llama-3.2-3B / MMLU | 14,042 | 0.580900 | 0.050 | **[0.530900, 0.630900]** |
| Llama-3.2-3B / GSM8K | 1,000 | 0.695000 | 0.060 | **[0.635000, 0.755000]** |

**Confirmed for the record (ruling 1, 2026-07-21): the four half-widths
0.050 / 0.062 / 0.050 / 0.060 are the mechanical output of the rule quoted
above, with no per-cell adjustment of any kind.** Each is
`max(0.05, 2*SE + 0.03)` evaluated at that cell's own `p` and `n` and rounded up
to three decimals — nothing else entered:

| cell | 2·SE + 0.03 | vs the 0.05 floor | half |
|---|---:|---|---:|
| Qwen / MMLU | 0.038323 | floor wins | 0.050 |
| Qwen / GSM8K | 0.061265 | formula wins | 0.062 |
| Llama / MMLU | 0.038328 | floor wins | 0.050 |
| Llama / GSM8K | 0.059119 | formula wins | 0.060 |

Both MMLU cells land on the 0.05 floor exactly as designed: at n=14,042 the
sampling term is ~0.008, so the gate is carried by the implementation-divergence
budget rather than by sampling noise. Both GSM8K cells clear the floor on the
formula, at n=1,000 where sampling noise is real. The arithmetic is applied by
`~/scratch/flipeval/work/derive_fp16_gates.py`, which reads results and
evaluates the formula; no cell was touched by hand.

**The GSM8K half took two attempts, and the first was wrong.** Full account in
`docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md` § 4. Briefly: lm-eval 0.4.12
auto-enables `fewshot_as_multiturn` under a chat template, so exemplars landed
in separate turns instead of inline as the preregistration requires; and the
frozen rule never named which GSM8K metric to read, so the derivation script
took `strict-match`, which voided 617 of 1,000 Qwen rows — 336 of them answers
`pilot_eval` scores correct, because the model writes `#### $18`. Amendment 1
named `flexible-extract` (on the ground that `extract_gsm8k_answer` has always
been marker-else-last-number) and required `--fewshot_as_multiturn false`; **it
was committed before the rerun was submitted**, and it records openly that the
metric choice followed seeing the first result. The rerun (`11342098`) verified
inline placement mechanically — the derivation script now refuses to derive a
GSM8K gate unless the prompt has exactly one assistant turn.

**Independent sanity check:** the bridge's `pilot_eval` FP16 GSM8K figure of
0.615 falls inside the new Qwen gate [0.513, 0.637]. The correct implementation
passes — which the voided [0.175, 0.289] would have failed badly. This is an
observation on an already-published figure, not an input to the derivation.

## 6. The wall-time item — resolved, and the premise was wrong

Full detail in `docs/PACE_ENVIRONMENT_NOTE.md` § "RESOLVED 2026-07-21". Probe
`11338533` on the existing `qwen25-1p5b-gptq4-seed0` checkpoint, through the
real `pilot_eval` loader, renderer and scorer:

| task | `TorchLinear` | `TritonV2Linear` | speedup |
|---|---|---|---|
| MMLU (scoring) | **0.199 s/item** → 0.78 h / 14,042 | 0.193 s/item | 1.027× |
| GSM8K (generation) | **7.641 s/item** → 2.12 h / 1,000 | 7.519 s/item | 1.016× |

**The 2.86 s/item that raised the item was compile warmup.** First-item cost was
**10.29 s** against a 0.199 s steady state, and a 2-item smoke cannot separate
the two. The measured rates reproduce the bridge's actual 22–30 min wall times,
which is why they are trusted over the smoke. **TRITON parity is exact:**
agreement 1.000 over 60 MMLU items, **max |Δlogprob| = 0.0**, byte-identical
GSM8K generations.

**Recommendation, which is to change almost nothing:**

1. **Keep `TorchLinear`.** 1.6–2.7 % does not justify moving a registered
   nuisance variable. The parity evidence now exists if TRITON is ever needed.
2. **Adopt per-task job splitting** — free, since `--only-task` already existed.
   The motivation is tail risk, not throughput: the bridge's `awq_s1` GSM8K half
   ran 2 h 07 m against 22–30 m for its peers (~38 s/item against 7.6 measured
   here). Splitting stops a slow generation half endangering a cheap scoring
   half and bounds what preemption destroys.
3. **Keep the 12 h walls.** Now generous rather than tight, with room for the 5×
   generation outlier.

Revised evaluation-stage estimate: ~66 GPU-hours against the ~110 h budgeted.

**Stated, not buried:** GSM8K generation cost is right-skewed, the probe's
steady mean (7.64 s) exceeded its all-item mean (6.87 s), and 20 items is a thin
sample of that tail. That is precisely why the recommendation is generous walls
plus splitting rather than tightening walls to the measurement.

---

## 7. Verification evidence

| gate | result | evidence |
|---|---|---|
| in-image suite | **161 passed, 0 skipped, 0 failed** | job `11343941` |
| shell scripts | `bash -n` + `shellcheck` clean | all five sbatch files |
| source fingerprint | `passed: true` after each commit | `docs/PREPACE_FREEZE.json` |
| calibration artifacts | **10/10 PASS, 0 failures** | job `11339076` |
| dataset pins resolve | MMLU 14,042 / 57 subjects; GSM8K 1,319 rows | job `11338439` |
| FP16 reference derivation | 4/4 derived, placement asserted inline | job `11343903` |
| lm-eval CLI surface | all flags present, 0.4.12 | jobs `11338567`, `11338615` |

Calibration artifact detail (job-health only): all ten carry 128 distinct
document indices × 2,048 tokens, the pinned tokenizer fingerprints, C4 revision
`1588ec45…`, and `passes=2`; seeds are disjoint within each model and no
artifact sha is shared between models.

Commits, each followed by a freeze refresh: `3d24761` (Amendment 2 + derivation
rule), `123c83c` (reference-run job), `8e9797f` (config, validator, fan-out
scripts, wall-time resolution), `fe69ab4` (gate-rule Amendment 1), `2541984`
(placement fix), `dbe5ad9` (the four derived gates). `2699972` committed the
untracked `paper/` tree at your instruction, after confirming the retired 6.3 %
anecdote appears only inside its labelled disclosure paragraph.

The in-image count moved 109 → 145 on this work, then to **161** when the
concurrent atlas rev-2 session added 16 tests without updating the recorded
expectation; `AGENTS.md`, `CLAUDE.md` and `build_image.sbatch` are corrected to
161 here.

---

## 8. What is still owed before fan-out

1. **This pack's acceptance**, and your explicit go for Stage 6.
2. **The 12 remaining quantized builds** — Qwen seeds 3–4 and Llama seeds 0–4,
   × 2 methods, minus the 6 Qwen checkpoints that already exist. Per the plan,
   the **Llama seed-0 GPTQ/AWQ canary pair must pass first**, exactly as Stage 3
   did for Qwen, before the other 8 Llama builds.
3. **`STATUS.md`'s unresolved main-grid implementation items**, which the signed
   bridge record also lists as outstanding.

The WikiText-2 amendment (Decision Point A) is closed, and Decision Point B is
closed by the frozen registration plus Amendment 2.
