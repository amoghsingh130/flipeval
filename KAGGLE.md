# Kaggle Validation Gate

Updated: 2026-07-13. This is the canonical Kaggle runbook. The longer 2026-07-10 Kaggle handoffs are historical records of the completed public-checkpoint pilot and earlier environment debugging; they do not override this file or `STATUS.md`.

## Validation result

The FP16-only validation completed on 2026-07-11 using Qwen2.5-1.5B-Instruct snapshot `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, 400 MMLU items, and 200 GSM8K items.

| Task | Correct | n | Accuracy | Prompt style | Gate range | Result |
|---|---:|---:|---:|---|---:|---|
| MMLU | 172 | 400 | 0.430 | chat | 0.365–0.465 (corrected 2026-07-13; originally 0.55–0.65) | pass |
| GSM8K | 123 | 200 | 0.615 | chat | 0.55–0.65 | pass |

Overall result: **GATE: PASS**, resolved 2026-07-13 by `docs/GATE_DECISION_2026-07-13.md`. The original 0.55–0.65 MMLU range failed at 0.430 and opened a `STOP AND DEBUG` gate; the trusted-reference run below validated the implementation and corrected the invalid expectation. The corrected MMLU gate is the reference result plus a documented tolerance (`0.415 ± 0.05`).

This run is the gate for all subsequent GPU work:

- **Pass:** MMLU accuracy is in the inclusive corrected range 0.365–0.465, GSM8K accuracy is in the inclusive range 0.55–0.65, and every record reports `prompt_style: chat`.
- **Stop and debug:** either accuracy is outside its range, prompt-style validation fails, or execution does not complete reliably. Preserve all available outputs and investigate the loader, prompts, scorer, and environment before changing any protocol or starting later experiments.

## Reference run result (2026-07-13)

`notebooks/kaggle_mmlu_reference_run.ipynb` executed the `docs/MMLU_REFERENCE_RUN.md` procedure on a Kaggle T4 (lm_eval 0.4.12, torch 2.10.0+cu128, transformers 5.0.0, Python 3.12.13) against the identical snapshot and 400 items:

| Quantity | Value |
|---|---:|
| Reference zero-shot chat accuracy | 0.415 |
| Pilot accuracy (same items) | 0.430 |
| Prediction agreement | 72.5% |
| Five-shot anchor accuracy | 0.470 mean |

The preserved archive is `kaggle_mmlu_reference_run.tar.gz` at repository root, SHA-256 `d20d10fc47633707eb1ac356da66c5c1a4fb092799a0dc749463a8dd42fd7e18`, containing both harness output directories, normalized samples, the 400-row diff CSV, and `reference_summary.json`. The pre-fixed inspection branch (agreement < 95%) was completed: the reference independently reproduces the B-heavy imbalance, disagreements are symmetric and sit on low-margin near-ties, and the whitespace/boundary audit found no scorer defect. Full evidence and the corrected-gate decision are in `docs/GATE_DECISION_2026-07-13.md`.

This execution also validated in practice the previously review-flagged 2026-07-12 session items it exercised: the bundle/dataset extraction layout (including Kaggle's automatic archive extraction), the real lm-evaluation-harness sample format, the sample-normalization step, `scripts/compare_mmlu_reference.py` against real harness output, and both harness commands. The `GSM8K_JSONL` loader fallback was not exercised by this MMLU-only run and remains validated only by local regression tests.

## Prepared inputs

Build the clean private-Dataset upload bundle locally with:

```bash
python scripts/make_kaggle_bundle.py
```

Upload `dist/kaggle_dataset.zip` as a private Kaggle Dataset. Import `notebooks/kaggle_template_validation.ipynb`, attach that Dataset, enable Internet, and select a T4 GPU accelerator. The notebook discovers the attached project, copies it to `/kaggle/working/compression-eval`, installs the declared requirements, generates an FP16-only chat validation configuration, and runs the two tasks.

An optional Kaggle secret named `HF_TOKEN` can be exposed as both `HF_TOKEN` and `HUGGING_FACE_HUB_TOKEN`. Qwen2.5 is public, but authenticated Hugging Face requests can avoid anonymous download throttling.

## Required preservation

Run every cell, including the final preservation cell, even when the measured accuracies miss the expected range. The notebook writes:

```text
/kaggle/working/results/kaggle_qwen25_1p5b_fp16_chat_validation/
  fp16.mmlu.jsonl
  fp16.gsm8k.jsonl
  manifest.json
  validation_config.yaml
  validation_summary.json

/kaggle/working/kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz
```

The final cell prints `GATE: PASS` or `GATE: STOP AND DEBUG`; it does not discard an out-of-range result. Save a Kaggle notebook version with outputs and download the tarball regardless of outcome. In the next session, attach the tarball or paste the two accuracy lines from `validation_summary.json`.

## Completed execution and recovery record

The initial Hub-backed model loads stalled during weight materialization, first at `1/338` and later at `142/338`. The following recovery worked:

1. Set a fresh cache at `/kaggle/working/hf-cache`, disable Xet, and explicitly download the model with `snapshot_download(..., max_workers=1)`.
2. Point the generated baseline `model_id` to the completed local snapshot.
3. Run the evaluator offline with `HF_ENABLE_PARALLEL_LOADING=false` and `CUDA_VISIBLE_DEVICES=0`. This loaded all 338 tensors in about one second and MMLU completed in 71 seconds.
4. Fully offline task loading then failed because GSM8K had not been cached. A separate `load_dataset("openai/gsm8k", ...)` request hung without progress.
5. Download the canonical OpenAI GSM8K `test.jsonl` from `openai/grade-school-math`, temporarily make the Kaggle copy of `pilot_eval/tasks.py` honor `GSM8K_JSONL`, and rerun only `--only-task gsm8k`. This completed successfully without overwriting MMLU. A permanent, schema-validated version was added locally on 2026-07-12 but remains pending the technical review flagged above before Kaggle testing.

The `torch_dtype` deprecation and unauthenticated-Hub messages were warnings. The materialization stalls and missing offline GSM8K cache were the actual execution problems. The local GSM8K workaround preserved the official 1,319-row test order and the evaluator consumed the configured first 200 rows.

## Preserved artifact

The downloaded archive is at repository root:

```text
kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz
SHA-256: f22e4a6bcce2666a58fb6a4338889b969157db5edb20a122ef68243bfa08b739
```

Internal JSONL checksums:

- MMLU: `99f8dd2493bc78d34dcada3029a95237af846da183112ec1e808cde982cde4c0`
- GSM8K: `a41c34c976087ce9d45f8c886f7c2d368d4a4d7995c89405280cd38d888bbf1c`

MMLU subject accuracies were abstract algebra `0.33`, college computer science `0.45`, high-school statistics `0.49`, and machine learning `0.45`. Predictions were strongly imbalanced: `A=31`, `B=158`, `C=123`, `D=88`.

## Reference-run notebook

`notebooks/kaggle_mmlu_reference_run.ipynb` executes the `docs/MMLU_REFERENCE_RUN.md` procedure on Kaggle: it locates the attached Dataset, finds the preserved pilot records (handling Kaggle's automatic extraction of the uploaded tarball) and verifies the MMLU JSONL checksum, installs `lm_eval==0.4.12`, materializes the exact model snapshot with the validated `snapshot_download(..., max_workers=1)` recovery, runs the zero-shot and five-shot commands against the local snapshot path (asserted equal to revision `989aa79...`), normalizes harness sample files (injecting `task_name` from the filename when rows omit it), runs `scripts/compare_mmlu_reference.py` over all 400 items, applies the pre-fixed interpretation rule, and packages everything into `/kaggle/working/kaggle_mmlu_reference_run.tar.gz`. It was executed successfully on 2026-07-13 (results above); the resulting hand-written gate decision record is `docs/GATE_DECISION_2026-07-13.md`.

## Work remaining before the main grid

The Kaggle validation gate is resolved and no further Kaggle rerun is required. The
registered calibration builder and paired two-level bootstrap are now implemented
under local deterministic tests. Their real C4/WikiText and GPU-backend preflights
belong on PACE and are described in `docs/PACE_RUNBOOK.md`.

The six-checkpoint GPTQ/AWQ bridge can proceed after those preflights. The broader
main grid additionally requires RTN/Wanda construction and ARC-Challenge/HellaSwag
execution paths; these newly explicit implementation states and the 137-variant,
548-output expected matrix are frozen in `configs/main_grid_manifest.yaml`.

## Historical Kaggle records

- `KAGGLE_CHAT_HANDOFF_2026-07-10.md`: initial Kaggle setup, failed local quantization, and pivot to public checkpoints.
- `KAGGLE_RUN_COMPLETION_HANDOFF_2026-07-10.md`: completed public-checkpoint pilot, packaging, recovery details, and caveats.
- `KAGGLE_RUN_COMPLETION_HANDOFF_2026-07-10.md` is not the status of the current FP16 chat-template validation; the runs are separate.
