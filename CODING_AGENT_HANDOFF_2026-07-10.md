# CODING_AGENT_HANDOFF_2026-07-10: Pre-PACE Work Phase

> Historical planning document. For current state and next action, read `KAGGLE_VALIDATION_HANDOFF_2026-07-11.md`, then `STATUS.md` and `KAGGLE.md`. The later FP16 chat-template gate completed with MMLU `0.430`, GSM8K `0.615`, and overall `STOP AND DEBUG`; statements below that the earlier public-checkpoint pilot "passed" do not supersede that gate.

Audience: a coding agent working in the local `compression-eval` repository. No GPU access is assumed except where a task explicitly says "Kaggle validation" (the human runs those cells; you prepare them).

Read first, in order:
1. `handoffv1.md` — research plan, hypotheses (H1/H2/H3), metric definitions, pass criteria.
2. `KAGGLE_CHAT_HANDOFF_2026-07-10.md` — Kaggle setup, auto-gptq failure, public-checkpoint pivot.
3. `KAGGLE_RUN_COMPLETION_HANDOFF_2026-07-10.md` — GPTQ loader recovery, run completion, known limitations.
4. `paper-proposal-v3-dnb.md` — current paper positioning (NeurIPS D&B artifact paper).

## Context you need

The Kaggle pilot is COMPLETE and PASSED. Verified results from `pilot_outputs_20260711T000427Z.tar.gz` (SHA-256 `a72ff2fd8cf3c3d6a469941f0013217954101cd84fddb384c2b078898a72ecb8`):

| task  | method      | n   | fp16 acc | comp acc | net delta | harmful | beneficial | state churn | total churn | McNemar p |
|-------|-------------|-----|----------|----------|-----------|---------|------------|-------------|-------------|-----------|
| gsm8k | gptq_public | 200 | 0.450    | 0.470    | +0.020    | 0.115   | 0.135      | 0.250       | 0.630       | 0.672     |
| gsm8k | awq_public  | 200 | 0.450    | 0.460    | +0.010    | 0.105   | 0.115      | 0.220       | 0.620       | 0.880     |
| mmlu  | gptq_public | 400 | 0.455    | 0.4125   | -0.0425   | 0.095   | 0.0525     | 0.1475      | 0.220       | 0.036     |
| mmlu  | awq_public  | 400 | 0.455    | 0.435    | -0.020    | 0.0925  | 0.0725     | 0.165       | 0.235       | 0.389     |

Rank instability: GSM8K winner gptq_public, bootstrap flip rate 0.424; MMLU winner awq_public, flip rate 0.144. Required-n for observed deltas at 80% power: gsm8k gptq 4,923; gsm8k awq 17,347; mmlu awq 3,238; mmlu gptq 635.

Known defects to fix (both confirmed in the pilot):
- D1: prompts are raw text; Qwen chat template is never applied. FP16 absolute accuracy is ~15 points below published Qwen2.5-1.5B-Instruct numbers (45.5% MMLU vs ~60%).
- D2: `pilot_eval/run.py` overwrites `manifest.json` on each invocation, so `--only-method`/`--only-task` runs destroy the record of earlier methods. The pilot's manifest lists only `awq_public`/`gsm8k` despite six completed evaluations.

PACESHIP compute application is submitted; decision expected ~2 weeks. All tasks below must run without cluster access.

## Task 1: Pilot closeout (do first, small)

1. Port the Kaggle-side GPTQ loader patch into `pilot_eval/modeling.py`: when `method.name == "gptq_public"` (better: when a new optional config field `quantization_backend: gptq_torch` is set), pass `quantization_config=GPTQConfig(bits=4, backend="gptq_torch")` to `from_pretrained`. Make it config-driven, not name-string-driven. The exact working patch is in `KAGGLE_RUN_COMPLETION_HANDOFF_2026-07-10.md` section 4.
2. Add `configs/kaggle_qwen_public_quantized.yaml` to the repo (full YAML is in `KAGGLE_CHAT_HANDOFF_2026-07-10.md`).
3. Create `results/PILOT_RESULTS.md` containing the tables above, the archive SHA-256, and the caveats list from the completion handoff (raw prompts, dirty Kaggle env, TorchLinear backend, public checkpoints, small n).
4. Fix D2: `run.py` must load an existing `manifest.json` if present and merge (union of methods, union of tasks, append a `runs` list with timestamps) instead of replacing. Preserve backward compatibility with manifests lacking the `runs` key.

Acceptance: unit test that invokes the manifest-writing code path twice with different methods and asserts both methods appear in the final manifest.

## Task 2: Chat template support (highest priority code change)

Fix D1. In `pilot_eval/tasks.py` / `modeling.py`:

1. Add a per-task config field `prompt_style: raw | chat` (default `raw` to keep old runs reproducible).
2. In `chat` mode, build messages `[{"role": "user", "content": <prompt>}]` and render with `tokenizer.apply_chat_template(..., add_generation_prompt=True, tokenize=False)`. For GSM8K few-shot, put the few-shot examples inside the user message (simplest defensible choice) OR as alternating user/assistant turns behind a second flag `fewshot_style: inline | turns` — implement `inline` first.
3. MMLU is scored by answer log-likelihood: ensure the choice continuation tokens are appended AFTER the chat template's generation prompt, and that likelihood is computed only over the continuation tokens, exactly as in raw mode. This is the subtle part; add a unit test with a stub tokenizer asserting the scored token span.
4. Record `prompt_style` in each JSONL record's `metadata` and in the manifest.
5. Prepare (do not run) a Kaggle validation cell: FP16-only rerun of the pilot config with `prompt_style: chat`, expected outcome MMLU ≈ 0.55-0.65 and GSM8K ≈ 0.55-0.65. Write it into `notebooks/kaggle_template_validation.ipynb`. The human runs it (~50 min on T4).

Acceptance: pytest passes with a tiny tokenizer fixture; raw-mode outputs are byte-identical to current behavior (regression test using a stored prompt hash from the pilot JSONLs).

## Task 3: Extract `flipeval` standalone package (the paper artifact)

Create a new top-level package (can live in this repo under `flipeval/` initially):

1. Port all statistics out of `pilot_eval/analyze.py`: net delta, harmful/beneficial flip rates, accuracy-state churn, wrong-to-different-wrong churn, total answer churn, bootstrap CIs, McNemar exact test, TOST at a declared margin, MDD at 80% power, required-n, item-bootstrap rank flip rate.
2. Public API: `flipeval.compare(baseline_records, method_records, margin=0.02, bootstrap=1000, seed=...) -> ComparisonResult` and `flipeval.rank_stability(list_of_method_records, ...)`. Records are lists of dicts with at minimum `item_id`, `prediction`, `correct`. Deterministic given `seed`.
3. CLI: `flipeval compare a.jsonl b.jsonl --margin 0.02` producing the same CSVs the pilot produced.
4. TESTS ARE THE POINT OF THIS TASK. Build hand-computed fixtures:
   - synthetic 20-item pair with known b=3, c=5: assert exact flip rates, McNemar b/c, net delta.
   - degenerate cases: zero flips (McNemar undefined/p=1 path), all flips, n=1.
   - TOST: construct a case that is provably equivalent at margin 0.5 and provably not at margin 0.01.
   - bootstrap determinism: same seed → identical CIs.
   - cross-check: run the packaged analyzer against the actual pilot JSONLs (in the extracted archive) and assert it reproduces `pair_summary.csv` and `rank_instability.csv` to 6 decimals. This is the golden regression test; commit the pilot CSVs as fixtures.
5. `pyproject.toml`, Apache-2.0 license, README with a 10-line usage example.

Acceptance: `pip install -e . && pytest` green; golden test reproduces pilot CSVs exactly.

## Task 4: lm-evaluation-harness interop

1. Add a loader `flipeval.io.from_lm_eval_harness(path)` that converts harness `--log_samples` output JSONs into flipeval records. Handle both loglikelihood tasks (MMLU-style: derive predicted choice from argmax of choice loglikelihoods) and generative tasks (GSM8K-style: use the harness's filtered/extracted answer).
2. Test against committed miniature harness output fixtures (construct 3-5 sample files by hand matching the harness schema; document the harness version the schema was taken from).
3. Draft (as a markdown file `docs/harness_issue_draft.md`, do not post) a GitHub issue for EleutherAI/lm-evaluation-harness proposing a `compare` mode: motivation (3 sentences, cite pilot numbers), proposed CLI, proposed output schema. The human will post it.

Acceptance: converter round-trips the fixtures; `flipeval compare` runs end-to-end on harness-format inputs.

### Pre-main-grid statistics extension (queued 2026-07-11)

Before any main-grid results are inspected, extend `flipeval` with the pre-registered two-level paired bootstrap in `PREREGISTRATION.md`. The API must accept GPTQ/AWQ item records grouped by calibration seed; resample the five paired seed labels with replacement, then resample common item IDs with replacement within every selected seed. Report the joint seed-by-item rank-instability estimate, exact-tie replicate rate, seed-level accuracy SD, and item-level SE, while preserving the existing within-seed item-bootstrap metric for pilot comparability. Add deterministic, hand-checkable tests covering paired seed resampling, item alignment, repeated sampled seeds, ties, and fixed RNG seeds. Do not infer or tune the procedure from main-grid outcomes.

Also update `scripts/build_quantized.py` before main-grid checkpoint construction: replace its current bounded streaming reservoir and 512-token default with the registered C4/WikiText-2 algorithm (128 samples of exactly 2,048 tokens, `numpy.random.default_rng(seed)` document-index shuffling, short-document skipping, persisted indices and token hashes, and identical ordered samples for GPTQ/AWQ at a given seed). Add a deterministic calibration-manifest test. The existing builder does not yet implement this protocol and must not be used for a main-grid build until this item is complete.

## Task 5: Pre-registration document

Write `PREREGISTRATION.md` from the plan in `paper-proposal-v3-dnb.md` and `handoffv1.md`:
- H1/H2/H3 stated exactly as in handoffv1 section "Claims".
- Full grid: models (Qwen2.5-1.5B/7B-Instruct, Llama-3.2-1B-or-3B, Llama-3.1-8B-Instruct), methods (RTN, GPTQ, AWQ, SparseGPT-or-Wanda 2:4), bits (4, 3), 5 calibration seeds, 2 calibration datasets (C4, WikiText-2) on one model, benchmarks (MMLU, ARC-Challenge, HellaSwag subset, GSM8K >= 1000 items), chat template ON.
- Primary metrics and exact decision rules for H3 confirm/disconfirm (e.g., "H3 supported if across 5 seeds the GPTQ-vs-AWQ winner flips on >= 1 benchmark for >= 2 of 4 models, or if seed-induced accuracy range exceeds the GPTQ-vs-AWQ mean gap").
- TOST margin fixed at 2 percentage points (from handoffv1).
- Statement that this file will not be edited after the first main-grid job starts, only appended with dated amendments.

## Task 6: Container for PACE

1. Write an Apptainer definition (plus a Dockerfile mirror) pinning: Python 3.11, torch (pick latest stable compatible with gptqmodel's requirement — note the pilot hit gptqmodel wanting torch >= 2.11 while Kaggle had 2.10; pin torch >= 2.11 here), transformers, gptqmodel, autoawq, lm-eval, datasets, and the repo itself. Emit a lockfile (`pip freeze`) into the image and commit a copy.
2. CPU-only smoke path: the container must run `python -m pilot_eval.run --config configs/kaggle_smoke_tiny.yaml` (tiny-gpt2, CPU) and the flipeval test suite. This validates everything except CUDA kernels.
3. Write `docs/PACE_RUNBOOK.md`: SLURM batch script templates (one checkpoint-build job, one eval job, array-job pattern for the seed grid), scratch vs project storage layout, and the bridge-run command sequence for day one of PACE access.

Acceptance: `apptainer build` (or docker build) succeeds; CPU smoke test passes inside the container.

## Task 7: Literature-sweep support (assist only)

Produce `docs/related_work_checklist.md`: a structured checklist of queries and venues (arXiv cs.CL/cs.LG 2025-2026: "flip rate" quantization, "calibration set" sensitivity GPTQ/AWQ, benchmark statistical power LLM, McNemar LLM evaluation) and a table skeleton with columns [paper, what it shows, overlap with H1/H2/H3, our differentiation]. Pre-fill the Dutta et al. "Accuracy is Not All You Need" row from `compression-eval-proposal-v2.md`. The human does the actual reading and judgment calls.

## Order and dependencies

Task 1 → Task 2 (both touch run/modeling). Task 3 is independent and can go in parallel; Task 4 depends on 3. Tasks 5-7 are independent docs. Everything must keep `pilot_eval` working: the pilot JSONLs and CSVs are the regression oracle throughout.

## Out of scope for this phase

Do NOT: build quantized checkpoints, run any GPU evaluation, post the harness issue, edit `PREREGISTRATION.md` after creation (append-only), or restructure the repo layout beyond adding `flipeval/`, `docs/`, `results/`.

## Definition of done

- All acceptance criteria green under `pytest`.
- Golden test reproduces the pilot's `pair_summary.csv` and `rank_instability.csv` exactly from raw JSONLs.
- Raw-prompt mode byte-identical to pilot behavior (prompt-hash regression).
- Container builds and passes CPU smoke.
- A final `STATUS.md` summarizing what was done, what the human must run on Kaggle (template validation notebook), and what waits for PACE.
