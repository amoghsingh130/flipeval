# Kaggle FP16 Chat Validation Handoff

Updated: 2026-07-11

## Bottom line

The Kaggle run completed and its archive is now in the repository root. The execution workarounds succeeded, but the declared accuracy gate failed:

| Task | Result |
|---|---:|
| MMLU | `172/400 = 0.430` |
| GSM8K | `123/200 = 0.615` |

All 600 records report `prompt_style: chat`. GSM8K is inside the declared `0.55–0.65` range; MMLU is not. Current decision: **STOP AND DEBUG**. Do not start the PACE bridge, quantized bridge evaluation, or main grid.

## Artifact identity

- File: `kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz`
- Archive SHA-256: `f22e4a6bcce2666a58fb6a4338889b969157db5edb20a122ef68243bfa08b739`
- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- Snapshot revision: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`
- MMLU JSONL SHA-256: `99f8dd2493bc78d34dcada3029a95237af846da183112ec1e808cde982cde4c0`
- GSM8K JSONL SHA-256: `a41c34c976087ce9d45f8c886f7c2d368d4a4d7995c89405280cd38d888bbf1c`

The archive contains both JSONLs, `manifest.json`, `validation_config.yaml`, and `validation_summary.json`. It was independently extracted locally; record counts and accuracies were recomputed and match the summary.

Two provenance caveats are intentional: the manifest contains several failed/retried invocations and both the original Hub ID and final local-snapshot path, while the completed JSONLs identify the local snapshot path. The summary restores the canonical Hub ID and exact revision. The temporary `GSM8K_JSONL` edit existed only in `/kaggle/working/compression-eval`; it has not been ported into the local repository.

## What worked

- Kaggle exposed two T4 GPUs and sufficient `/kaggle/working` storage.
- Explicit `snapshot_download` with a fresh cache and `max_workers=1` completed successfully.
- Loading the resolved local snapshot with offline Hub mode, parallel loading disabled, and only GPU 0 visible completed all 338 tensors in about one second.
- MMLU ran to `400/400` in 71 seconds.
- The official OpenAI GSM8K test JSONL contained 1,319 valid `question`/`answer` rows.
- A temporary Kaggle-only `GSM8K_JSONL` loader fallback plus `--only-task gsm8k` completed GSM8K without overwriting MMLU.
- The watchdog streamed both stdout and stderr and would terminate after five minutes without output.

## What did not work

- Repeated direct Hub-backed `from_pretrained` calls stalled indefinitely during tensor materialization (`1/338`, then `142/338`). The model download itself was not corrupt.
- Setting full offline mode before all datasets were cached caused the expected GSM8K `OfflineModeIsEnabled` failure after MMLU completed.
- A separate anonymous `load_dataset("openai/gsm8k", "main", split="test")` subprocess produced no progress for more than ten minutes.
- The first temporary `tasks.py` edit had inconsistent indentation and failed at import; replacing the complete `load_gsm8k` function and running `py_compile` fixed it.
- Applying the chat template did not recover MMLU absolute accuracy: the earlier raw pilot baseline was `0.455`, while this chat run was `0.430`. GSM8K improved from the earlier raw pilot's `0.450` to `0.615`.

## Evidence useful for MMLU debugging

Per-subject accuracy:

- abstract algebra: `0.33`
- college computer science: `0.45`
- high-school statistics: `0.49`
- machine learning: `0.45`

Prediction counts across 400 items:

- A: 31
- B: 158
- C: 123
- D: 88

The answer imbalance is a diagnostic clue. Existing local audits already showed that the chat template boundary and continuation likelihood slice are internally consistent, so do not assume the bug is the already-audited off-by-one without new contrary evidence.

## First task for the next chat

Diagnose the MMLU expectation/scorer mismatch without changing the registered protocol or running more quantization experiments:

1. Recompute archive summaries and inspect a small stratified set of MMLU records, especially items predicted B where the gold is A or D.
2. Establish a trusted reference using the exact model revision and identical 400 subject/index pairs, preferably lm-evaluation-harness with its prompt and few-shot settings recorded.
3. Compare zero-shot versus published few-shot provenance. The current config uses `fewshot: 0` for MMLU, so the declared `0.55–0.65` expectation may not be directly comparable.
4. Compare reference choice scoring: continuation text, leading whitespace, length normalization, chat assistant boundary, and whether the reference uses direct letter generation or conditional likelihood.
5. Decide from evidence whether to fix implementation, correct an invalid validation expectation, or both. Record the decision before any PACE/main-grid run.

The canonical overview is `STATUS.md`; the detailed Kaggle record is `KAGGLE.md`.
