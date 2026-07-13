# Gate Decision Record: FP16 MMLU Validation Gate

Date: 2026-07-13. This record resolves the `STOP AND DEBUG` gate opened by the
2026-07-11 FP16 chat-template validation (`KAGGLE.md`, `STATUS.md`), following the
trusted-reference procedure registered in `docs/MMLU_REFERENCE_RUN.md`.

## Decision

**GATE: PASS.** The pilot MMLU implementation is validated. The declared MMLU
expectation of 0.55–0.65 was invalid for this protocol and is corrected.

- New MMLU gate for the FP16 zero-shot chat validation on the fixed 400-item,
  four-subject subset: accuracy within **0.415 ± 0.05 = [0.365, 0.465]**
  (tolerance ≈ 2× the binomial standard error at n=400, documented here).
- The completed pilot result of **0.430** passes the corrected gate.
- The GSM8K gate is unchanged (0.55–0.65) and already passed at 0.615.
- No registered protocol was changed: `PREREGISTRATION.md` is untouched, and no
  evaluation code was changed as a result of this decision.

The PACE bridge and main grid remain blocked only by the two pre-existing
implementation items (calibration builder parity and the paired two-level
bootstrap), not by this gate.

## Reference run identity

- Notebook: `notebooks/kaggle_mmlu_reference_run.ipynb`, executed on Kaggle 2026-07-13.
- Archive: `kaggle_mmlu_reference_run.tar.gz` (repository root)
  SHA-256 `d20d10fc47633707eb1ac356da66c5c1a4fb092799a0dc749463a8dd42fd7e18`.
- Model: `Qwen/Qwen2.5-1.5B-Instruct`, snapshot revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` (identical to the pilot run; the
  snapshot directory name was asserted equal to the pinned revision).
- Environment: `lm_eval` 0.4.12, `torch` 2.10.0+cu128, `transformers` 5.0.0,
  `datasets` 5.0.0, `accelerate` 1.13.0, Python 3.12.13, Tesla T4.
- Zero-shot command:
  `python3 -m lm_eval --model hf --model_args pretrained=<local snapshot of 989aa79...>,dtype=float16 --tasks mmlu_abstract_algebra,mmlu_college_computer_science,mmlu_high_school_statistics,mmlu_machine_learning --num_fewshot 0 --limit 100 --batch_size auto --apply_chat_template --log_samples --output_path results/lm_eval_mmlu_0shot`
- Five-shot command: identical with `--num_fewshot 5` and a distinct output path.
- The only deviation from the literal commands in `docs/MMLU_REFERENCE_RUN.md` is
  `pretrained=` pointing at the locally materialized snapshot of the pinned
  revision (the validated recovery for the Kaggle hub-load stall); reference
  identity is unchanged.

## Results

| Quantity | Value |
|---|---:|
| Pilot MMLU accuracy (400 items) | 0.430 |
| Reference zero-shot accuracy (same 400 items) | 0.415 |
| Prediction agreement | 72.5% |
| `pilot_B_reference_non_B` rows | 35 |
| Five-shot reference accuracy (anchor) | 0.470 mean |

Per-subject (pilot / reference zero-shot / reference five-shot):

- abstract_algebra: 0.33 / 0.26 / 0.38
- college_computer_science: 0.45 / 0.50 / 0.49
- high_school_statistics: 0.49 / 0.43 / 0.59
- machine_learning: 0.45 / 0.47 / 0.42

## Which pre-fixed interpretation branch fired

`docs/MMLU_REFERENCE_RUN.md` fixed the interpretation before the reference result
was seen. Agreement (72.5%) is below 95%, so the applicable branch was: inspect
the `pilot_b_disagreement` rows first and compare leading whitespace, continuation
length normalization, and the assistant-boundary likelihood span before changing
code. That inspection is recorded below; the automatic-validation branch
(agreement ≥ 95%) did not fire, so this decision rests on the inspection evidence.

## Inspection evidence

All quantities were computed from `mmlu_reference_diff_0shot.csv` and the logged
harness samples inside the preserved archive, against the archived pilot records
(`kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz`, MMLU JSONL SHA-256
`99f8dd2493bc78d34dcada3029a95237af846da183112ec1e808cde982cde4c0`).

1. **Aggregate equivalence.** 0.430 vs 0.415 is a difference of 0.015 with a
   per-run binomial standard error of ≈0.0247 at n=400. Two independent
   implementations with different prompts land on statistically indistinguishable
   accuracy.
2. **The B-imbalance is a model property, not a scorer defect.** Prediction
   counts: pilot A=31/B=158/C=123/D=88; reference A=71/B=155/C=85/D=89; gold
   A=96/B=84/C=100/D=120. The independent harness reproduces the B-heavy
   behavior under zero-shot chat prompting.
3. **Disagreements are symmetric.** Of 110 disagreeing items, the pilot is
   correct on 36, the reference on 30, and neither on 44. There is no direction
   in which the reference systematically outperforms the pilot.
4. **Disagreements concentrate on near-ties.** Median top-2 log-likelihood margin
   on disagreeing items: 0.406 (pilot) / 0.523 (reference), versus 1.062 / 1.258
   on agreeing items. Item-level divergence is prompt-format sensitivity on
   low-confidence items, not scoring error.
5. **`pilot_b_disagreement` rows.** On the 35 items where the pilot predicted B
   and the reference did not, the reference was correct only 13 times — no
   evidence of a pilot-specific B defect.
6. **Whitespace and boundary check.** The harness scores the bare letters
   `'A'..'D'` immediately after `<|im_start|>assistant\n`, with a subject-specific
   system message; the pilot scores `' A'..' D'` (leading space) after its own
   `MMLU_TEMPLATE` user message with no system message. Both are single-token,
   zero-shot conditional-likelihood scorers over four choices; no length
   normalization is involved on either side. The earlier local audits of the
   pilot's assistant-boundary likelihood slice stand unchallenged.

## Expected-range provenance audit

The 0.55–0.65 MMLU range does not appear in `PREREGISTRATION.md`. It entered the
workflow as an informal expected outcome in `CODING_AGENT_HANDOFF_2026-07-10.md`
(validation-cell preparation step) and was most plausibly derived from published
Qwen2.5-1.5B-Instruct MMLU figures, which are five-shot aggregates over all 57
subjects. It is not comparable to a zero-shot, chat-template, four-subject
(hard-STEM-skewed) 400-item subset: even the five-shot reference anchor on this
subset averages only 0.470. The expectation, not the implementation, was wrong.

## Consequences

- `STATUS.md` and `KAGGLE.md` now record the gate as PASS under the corrected
  range, with this file as the decision record.
- The FP16 validation protocol itself (subjects, indices, prompt style, scorer)
  is unchanged and remains the paired-churn baseline for the PACE bridge.
- Remaining blockers before the main grid are unchanged and independent of this
  gate: bring `scripts/build_quantized.py` into exact agreement with the
  registered 128 × 2,048-token calibration protocol, and implement the registered
  paired two-level seed-by-item bootstrap in `flipeval`
  (`CODING_AGENT_HANDOFF_2026-07-10.md`).
