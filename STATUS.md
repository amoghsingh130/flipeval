# Pre-PACE Implementation Status

Updated: 2026-07-13

## 2026-07-12 session changes: review completed by execution

The following work was prepared during the 2026-07-12 coding session and was originally flagged for technical review before Kaggle/GPU use:

- A permanent `GSM8K_JSONL` loader fallback with JSONL schema validation and regression tests.
- `scripts/compare_mmlu_reference.py` for exact item-set/gold validation, aggregate comparison, prediction agreement, full CSV diffs, and pilot-B/reference-non-B diagnostics.
- `docs/MMLU_REFERENCE_RUN.md` with pinned zero-shot and five-shot lm-evaluation-harness commands for the exact Qwen snapshot and four 100-item subjects.
- Comparator tests, Kaggle documentation updates, and a rebuilt `dist/kaggle_dataset.zip`.

On 2026-07-13 the reference-run workflow (harness commands, Kaggle extraction layout, sample-format normalization, and the item-level comparator against real lm-eval 0.4.12 output) was executed end-to-end on a Kaggle T4 through `notebooks/kaggle_mmlu_reference_run.ipynb` and completed successfully on all 400 items; the environment-sensitive details are therefore validated in practice. The gate outcome is recorded in `docs/GATE_DECISION_2026-07-13.md` and summarized below. The `GSM8K_JSONL` fallback was not exercised by this MMLU-only run and remains validated only by its local regression tests.

## Complete

- Config-driven GPTQ Torch backend loading via `quantization_backend: gptq_torch`.
- Durable manifest merging across partial method/task invocations, including legacy-manifest upgrades and per-invocation timestamps.
- Raw/chat task prompt modes. Chat mode uses the tokenizer chat template with an assistant generation prompt; MMLU continuations are appended afterward and only continuation tokens are scored. Prompt style is logged per record and task manifest.
- Public-checkpoint Kaggle config, pilot result note, archive checksum/caveats, and standalone golden CSV fixtures.
- FP16-only Kaggle chat-template validation notebook with an explicit pass/stop gate and unconditional packaging of JSONLs, manifest, generated config, machine-readable summary, and tar archive.
- Offline GSM8K loading through `GSM8K_JSONL`, with schema validation and tests; this session change is pending the technical review flagged above before Kaggle use.
- Standalone Apache-2.0 `flipeval` package, API, CLI, deterministic bootstrap statistics, rank stability, lm-evaluation-harness v0.4.x conversion, README, and packaging metadata.
- Harness `compare` issue draft and miniature multiple-choice/generative fixtures.
- Frozen pre-registration with all scientific TBDs resolved before main-grid execution, plus the related-work sweep checklist.
- GPTQModel-based local checkpoint builder; AutoAWQ path retained for AWQ.
- Python 3.11 Docker and Apptainer definitions, direct pins, resolved 119-package environment freeze, CPU smoke script, chat bridge config, and PACE/SLURM runbook.

## Verification

- `python3 -m pip install -e .`: passed.
- Independent `python3 -m pytest -q` rerun on 2026-07-11: 17 passed in 3.06 seconds; after strengthening the golden schema assertion: 17 passed in 2.02 seconds.
- Independently extracted the pilot archive into a fresh temporary directory and reran `python3 -m pilot_eval.analyze --bootstrap 1000 --seed 0` outside the pytest wrapper.
- Regenerated `pair_summary.csv` and `rank_instability.csv` now match the committed pilot fixtures in exact column order and categorical values, with maximum numeric absolute difference `0`.
- The manual rerun initially exposed that the golden pytest used `check_like=True`, masking a `pair_summary.csv` column-order difference. The analyzer column order was fixed and the test now requires the exact schema.
- Pilot archive SHA-256 reconfirmed: `a72ff2fd8cf3c3d6a469941f0013217954101cd84fddb384c2b078898a72ecb8`.
- Raw GSM8K pilot prompt hash regression: `2b93ef0019f94fd7`.
- MMLU chat scoring was manually audited: the rendered template is tokenized as the prompt, the choice is tokenized separately and concatenated afterward, and the shifted likelihood slice starts at `prompt_len - 1`, so it includes exactly the continuation labels and no template labels.
- Real Qwen2.5 tokenizer boundary check passed: the assistant generation prompt ended with `<|im_start|>assistant\n`, `" A"` encoded as token `[362]`, and separate prompt/continuation concatenation exactly matched full-string tokenization.
- Docker image `flipeval:local` built successfully on arm64 with Python 3.11, Torch 2.13.0, GPTQModel 7.1.0, AutoAWQ 0.2.9, Transformers 5.13.0, and lm-eval 0.4.12.
- In-image test suite: 17 passed.
- In-image CPU smoke: tiny-gpt2 completed two MMLU and two GSM8K items for baseline and placeholder methods, then wrote both analysis CSVs.
- Apptainer was not installed locally; the equivalent Docker mirror was built as allowed by the acceptance criterion.
- The updated Kaggle validation notebook is valid nbformat JSON, all code cells compile, its upload bundle contains the required notebook/config/runtime files, and the relevant local regression selection passed (`7 passed`).
- The completed FP16 chat-template validation archive is present at repository root as `kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz` (SHA-256 `f22e4a6bcce2666a58fb6a4338889b969157db5edb20a122ef68243bfa08b739`). It extracts cleanly and contains 400 MMLU plus 200 GSM8K JSONL records, a merged manifest, the generated config, and the machine-readable summary.
- Recalculation from the JSONLs matches the summary exactly: MMLU `172/400 = 0.430`; GSM8K `123/200 = 0.615`; every record reports `prompt_style: chat`. The gate therefore completed with `STOP AND DEBUG`, not an execution failure.

## Required Before Main Grid

The 2026-07-11 update to `PREREGISTRATION.md` resolved the scientific choices below before any main-grid execution:

1. Llama-3.2-3B-Instruct is the fourth model.
2. Wanda at 2:4 sparsity is the pruning method; SparseGPT is out of scope.
3. HellaSwag uses validation indices 0 through 1,999.
4. Calibration uses seeds `{0, 1, 2, 3, 4}`, 128 samples of 2,048 tokens, the registered deterministic sampling algorithm, and paired GPTQ/AWQ samples.
5. Four-bit is confirmatory; 3-bit is a reported secondary/exploratory dose-response analysis.
6. Seed pairing, tie handling, mean gap, and method seed ranges are defined algebraically.
7. H3 is evaluated over the fixed eight-cell set of four models by MMLU/GSM8K.
8. Support, disconfirmation, and the pre-declared inconclusive region have fixed count thresholds.
9. Seeds enter a paired two-level seed-by-item bootstrap with variance components reported separately.

Implementation blockers remain before the main grid: `scripts/build_quantized.py` must be brought into exact agreement with the registered calibration builder, and `flipeval` must implement the registered paired two-level bootstrap. Both are queued in `CODING_AGENT_HANDOFF_2026-07-10.md`; neither may be implemented or tuned after inspecting main-grid results.

## Kaggle Validation Gate: Resolved PASS (2026-07-13)

The FP16 chat-template validation completed 2026-07-11 on snapshot `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`: GSM8K `0.615` (pass), MMLU `0.430` against the declared 0.55–0.65 range, which opened a `STOP AND DEBUG` gate.

On 2026-07-13 the trusted-reference procedure from `docs/MMLU_REFERENCE_RUN.md` was executed on a Kaggle T4 via `notebooks/kaggle_mmlu_reference_run.ipynb` (archive `kaggle_mmlu_reference_run.tar.gz` at repository root, SHA-256 `d20d10fc47633707eb1ac356da66c5c1a4fb092799a0dc749463a8dd42fd7e18`). lm-evaluation-harness 0.4.12 on the identical snapshot and 400 items scored `0.415` zero-shot chat (prediction agreement 72.5%), with the five-shot anchor at `0.470` mean. The pre-fixed inspection branch was completed: the reference independently reproduces the B-heavy prediction imbalance, disagreements are symmetric and concentrate on low-margin near-tie items, and the whitespace/assistant-boundary audit found no pilot scorer defect. The 0.55–0.65 expectation was traced to an informal note in `CODING_AGENT_HANDOFF_2026-07-10.md`, not the preregistration, and is not comparable to this zero-shot four-subject subset.

Decision (full record: `docs/GATE_DECISION_2026-07-13.md`): the pilot implementation is validated; the MMLU gate is corrected to `0.415 ± 0.05 = [0.365, 0.465]`, which the completed `0.430` result passes. **The gate state is PASS.** No registered protocol and no evaluation code were changed.

## Waiting for PACE

The validation gate has passed. Only after the two implementation blockers above are resolved, follow `docs/PACE_RUNBOOK.md` on day one:

1. Build `flipeval.def` and copy its emitted resolved lock into project storage.
2. Run the CPU smoke on PACE.
3. Build the six Qwen2.5-1.5B GPTQ/AWQ 4-bit seed-0-to-2 bridge checkpoints.
4. Run `configs/pace_bridge_chat.yaml` one method per job and confirm merged manifest coverage.
5. Confirm chat-template absolute accuracy and paired churn signals before starting the preregistered full grid.

GPU quantization kernels, controlled calibration seeds, the PACE bridge, and the full H1/H2/H3 grid remain intentionally unrun in this pre-access phase.
