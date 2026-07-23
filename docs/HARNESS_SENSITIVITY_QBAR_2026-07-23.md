# Harness Sensitivity Study — Phase 2 Denominator Q̄ (2026-07-23)

Records the Phase 2 denominator of the pre-named headline ratio `R`, computed as
registered once the mini-grid's first inspection was unlocked. This is a results
note, not an amendment; it introduces no statistic the registration did not
already define.

## Authorization and gating

`docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md` § 5.2 (FROZEN 2026-07-22)
defers Q̄ to Phase 2: it "is computed **only** from mini-grid results, after
`scripts/verify_minigrid.py` passes over the complete 44-JSONL expected set and
the first accuracy inspection permitted by
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5 has occurred." That validator
passed as job `11375247` (409/409), and Amogh authorized the first inspection on
2026-07-23. Q̄ is therefore now computable and is computed here, unchanged from
its frozen definition.

## Definition, quoted (§ 5.2)

> the mean, over the **ten** Qwen2.5-1.5B quantized variants
> `{gptq_s0…s4, awq_s0…s4}`, of correctness-state churn against that model's
> `fp16` cell, **restricted to the § 4 item subset** (the 400 bridge MMLU items
> and GSM8K indices 0–199), computed per task.

§ 4 subset: MMLU = 4 bridge subjects (`abstract_algebra`,
`college_computer_science`, `high_school_statistics`, `machine_learning`), first
100 test items each = 400; GSM8K = test indices 0–199 = 200. Correctness-state
churn is the atlas/`flipeval` definition: fraction of items whose
correct/incorrect state changes on the common item set.

## Result — Qwen2.5-1.5B

Subset item counts realized: MMLU 400, GSM8K 200 (both exact).

### MMLU (subset n = 400)

| variant | churn | changed |
|---|---|---|
| gptq_s0 | 0.205000 | 82/400 |
| gptq_s1 | 0.230000 | 92/400 |
| gptq_s2 | 0.185000 | 74/400 |
| gptq_s3 | 0.222500 | 89/400 |
| gptq_s4 | 0.242500 | 97/400 |
| awq_s0 | 0.182500 | 73/400 |
| awq_s1 | 0.155000 | 62/400 |
| awq_s2 | 0.192500 | 77/400 |
| awq_s3 | 0.165000 | 66/400 |
| awq_s4 | 0.210000 | 84/400 |

**Q̄(mmlu) = 0.199000** — mean of the ten. [min 0.155000, max 0.242500,
population SD 0.026768]

### GSM8K (subset n = 200)

| variant | churn | changed |
|---|---|---|
| gptq_s0 | 0.335000 | 67/200 |
| gptq_s1 | 0.250000 | 50/200 |
| gptq_s2 | 0.265000 | 53/200 |
| gptq_s3 | 0.280000 | 56/200 |
| gptq_s4 | 0.255000 | 51/200 |
| awq_s0 | 0.290000 | 58/200 |
| awq_s1 | 0.300000 | 60/200 |
| awq_s2 | 0.295000 | 59/200 |
| awq_s3 | 0.300000 | 60/200 |
| awq_s4 | 0.300000 | 60/200 |

**Q̄(gsm8k) = 0.287000** — mean of the ten. [min 0.250000, max 0.335000,
population SD 0.024104]

## Status of R

`R_cond = C_cond / Q̄` is now computable for Qwen2.5-1.5B: the denominator exists
for both tasks. The numerator `C_cond` comes from the Phase 1 FP16 config-churn
cells (array `11368976`), which are not part of this note. `R` is reported per
condition, per task, with `C_cond` and `Q̄` beside it, per § 5.1 — done at the
study's own analysis time, not here. Neither Q̄ value is 0, so no undefined-ratio
case arises.

Llama-3.2-3B: § 5.2 says "the same construction applies to Llama-3.2-3B once its
cells complete." Its mini-grid cells are complete, so a Llama Q̄ is now also
computable; it is not computed here because the Phase 1 numerator conditions were
run on Qwen only (the Llama sensitivity canary has not run).

## Provenance

Job `11376178`; driver `~/scratch/flipeval/work/qbar.py`; artifact
`results/harness_sensitivity/qbar_qwen25-1p5b.json`. Inputs: the sealed Qwen
mini-grid cells, read after the § 5 first-inspection authorization. Doc-and-
results-only; neither `docs/` nor `results/` is in the source fingerprint.
