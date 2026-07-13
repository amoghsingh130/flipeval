# Kaggle Execution Handoff: Compressed-LLM Pilot (Historical)

Last updated: 2026-07-10. This handoff is for starting a new chat from the current Kaggle execution state.

> Superseded for current actions by `KAGGLE.md` and `STATUS.md`. This file is retained as a historical record of the initial Kaggle setup and public-checkpoint pivot.

For full research context, read `handoffv1.md` first. That file explains the paper idea, novelty collision with Dutta et al. "Accuracy is Not All You Need", the statistical plan, the pilot pass/fail criteria, venue strategy, and the broader compute plan. This file is narrower: it records exactly what happened while trying to run the pilot on Kaggle, what code exists, what worked, what failed, and what to do next.

---

## Current User State

The user is currently in a Kaggle notebook and is running:

```bash
python -m pilot_eval.run --config configs/kaggle_qwen_public_quantized.yaml
```

They are waiting for results.

This is the current pivot path: evaluate **public Qwen2.5 1.5B FP16/GPTQ/AWQ checkpoints** on Kaggle instead of locally building GPTQ/AWQ checkpoints with calibration seeds, because `auto-gptq` failed to install on Kaggle.

---

## Repo/Project Files That Matter

Primary context files:

- `handoffv1.md` — main project handoff; read this for the research plan.
- `compression-eval-proposal-v2.md` — current collision-aware proposal.
- `PILOT.md` — local/ICE-style pilot instructions.
- `KAGGLE.md` — Kaggle setup/runbook.
- `KAGGLE_CHAT_HANDOFF_2026-07-10.md` — this file.

Pilot code:

- `pilot_eval/run.py` — runs model/task evaluation and writes JSONL per-item logs.
- `pilot_eval/analyze.py` — consumes JSONL logs and writes summary CSVs.
- `pilot_eval/tasks.py` — loads MMLU and GSM8K and extracts answers.
- `pilot_eval/modeling.py` — loads Hugging Face causal LMs, scores MMLU by answer log likelihood, runs deterministic GSM8K generation.
- `pilot_eval/config.py` — YAML config parsing.

Kaggle support:

- `configs/kaggle_smoke_tiny.yaml` — smoke-test config.
- `configs/kaggle_qwen_1p5b.yaml` — intended local-checkpoint GPTQ/AWQ config for Kaggle paths.
- `scripts/kaggle_bootstrap.py` — copies dataset code into `/kaggle/working/compression-eval` and installs requirements.
- `scripts/kaggle_pack_outputs.py` — packages results from `/kaggle/working`.
- `scripts/make_kaggle_bundle.py` — creates a clean Kaggle Dataset bundle locally.
- `notebooks/kaggle_pilot.ipynb` — notebook template.
- `dist/kaggle_dataset.zip` — generated Kaggle upload artifact.

Local quantization support:

- `scripts/build_quantized.py` — intended helper for building GPTQ/AWQ checkpoints from Qwen2.5-1.5B with known calibration seeds.

Important: `configs/kaggle_qwen_public_quantized.yaml` was created inside the Kaggle notebook with `%%writefile`; it may not yet exist in the local repo unless explicitly copied back. Its content is shown below.

---

## Kaggle Upload/Access Situation

The user uploaded the Kaggle dataset such that folder structure was preserved under:

```text
/kaggle/input/datasets/amoghsingh130/compression-eval-pilot-code/
```

The requirements file path seen in Kaggle was:

```text
/kaggle/input/datasets/amoghsingh130/compression-eval-pilot-code/requirements.txt
```

The correct project root on Kaggle is:

```text
/kaggle/input/datasets/amoghsingh130/compression-eval-pilot-code
```

The bootstrap should be invoked with explicit `--source`, because the first auto-detect path picked the wrong root:

```python
PROJECT_INPUT_ROOT = "/kaggle/input/datasets/amoghsingh130/compression-eval-pilot-code"
BOOTSTRAP = f"{PROJECT_INPUT_ROOT}/scripts/kaggle_bootstrap.py"

!python {BOOTSTRAP} --source {PROJECT_INPUT_ROOT} --install
%cd /kaggle/working/compression-eval
```

Then verify:

```python
!pwd
!ls
!ls pilot_eval
!ls configs
!ls scripts
!test -f requirements.txt && echo "requirements.txt found"
```

---

## Bugs Encountered And Fixes

### 1. Bootstrap source-root detection bug

Original error:

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory:
'/kaggle/working/compression-eval/requirements.txt'
```

Cause:

`scripts/kaggle_bootstrap.py` auto-detected `pilot_eval/` as the project root instead of the folder above it. It copied only part of the project into `/kaggle/working/compression-eval`, so `requirements.txt` was missing.

Immediate Kaggle workaround:

```python
PROJECT_INPUT_ROOT = "/kaggle/input/datasets/amoghsingh130/compression-eval-pilot-code"
BOOTSTRAP = f"{PROJECT_INPUT_ROOT}/scripts/kaggle_bootstrap.py"

!python {BOOTSTRAP} --source {PROJECT_INPUT_ROOT} --install
%cd /kaggle/working/compression-eval
```

Local repo fix already made:

```python
candidates.extend(path.parent.parent for path in root.glob("**/pilot_eval/run.py"))
```

in `scripts/kaggle_bootstrap.py`.

### 2. Smoke test warnings

During smoke test with `sshleifer/tiny-gpt2`, Kaggle printed warnings like:

```text
The tied weights mapping and config for this model specifies to tie transformer.wte.weight to lm_head.weight...
GPT2LMHeadModel LOAD REPORT...
UNEXPECTED transformer.h.{0, 1}.attn.masked_bias
UNEXPECTED transformer.h.{0, 1}.attn.bias
```

These are harmless for the tiny GPT-2 smoke test.

### 3. Smoke test passed

Smoke command:

```bash
python -m pilot_eval.run --config configs/kaggle_smoke_tiny.yaml
python -m pilot_eval.analyze \
  --run-dir /kaggle/working/results/kaggle_smoke_tiny \
  --baseline fp16 \
  --bootstrap 100
```

Output confirmed:

- `fp16/mmlu` ran on 2 examples.
- `fp16/gsm8k` ran on 2 examples.
- `compressed_placeholder/mmlu` ran on 2 examples.
- `compressed_placeholder/gsm8k` ran on 2 examples.
- Analyzer wrote:

```text
/kaggle/working/results/kaggle_smoke_tiny/pair_summary.csv
```

The toy accuracies were all `0.0`, which is not a problem. The smoke test only proved that package import, dataset download, model loading, JSONL logging, and analysis work.

### 4. Quantization backend install failed

Command that failed:

```bash
python scripts/kaggle_bootstrap.py --install --with-quantization
```

That command internally ran:

```bash
pip install -q auto-gptq autoawq
```

`auto-gptq` failed. Relevant output:

```text
Collecting auto-gptq
Using cached auto_gptq-0.7.1.tar.gz
Preparing metadata (setup.py) ... done
Discarding ... auto_gptq-0.7.1.tar.gz ... has inconsistent version:
expected '0.7.1', but metadata has '0.7.1+cu1281'

Using cached auto_gptq-0.7.0.tar.gz
Preparing metadata (setup.py) ... done
Discarding ... auto_gptq-0.7.0.tar.gz ... has inconsistent version:
expected '0.7.0', but metadata has '0.7.0+cu1281'

Using cached auto_gptq-0.6.0.tar.gz
error: subprocess-exited-with-error
python setup.py egg_info did not run successfully.
metadata-generation-failed
```

Interpretation:

Kaggle's current Python/CUDA image does not cleanly install `auto-gptq` from PyPI. This is a package/environment issue, not a user mistake. It likely relates to current Kaggle Python/CUDA plus stale `auto-gptq` packaging metadata.

Decision:

Do not keep fighting local GPTQ/AWQ checkpoint building on Kaggle right now. Move calibration-seed checkpoint building to ICE/PACE or another controlled Python 3.10/3.11 environment later. Use Kaggle first for a public-checkpoint evaluation pilot.

---

## Current Pivot: Public Quantized Qwen Checkpoints

Because local `auto-gptq` failed on Kaggle, the current working plan is:

1. Use Kaggle to run evaluation on:
   - FP16 baseline: `Qwen/Qwen2.5-1.5B-Instruct`
   - public GPTQ checkpoint: `Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4`
   - public AWQ checkpoint: `Qwen/Qwen2.5-1.5B-Instruct-AWQ`
2. Analyze churn, net accuracy delta, harmful/beneficial flips, and item-bootstrap ranking instability.
3. Do **not** claim calibration-seed instability from this public-checkpoint run. Public checkpoints have fixed/unknown calibration.

The config currently running in Kaggle was created with:

```python
%%writefile configs/kaggle_qwen_public_quantized.yaml
run_name: kaggle_qwen25_1p5b_public_quantized
output_dir: /kaggle/working/results
device_map: auto
batch_size: 1

baseline:
  name: fp16
  model_id: Qwen/Qwen2.5-1.5B-Instruct
  dtype: float16
  trust_remote_code: true

methods:
  - name: gptq_public
    model_id: Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4
    dtype: float16
    trust_remote_code: true

  - name: awq_public
    model_id: Qwen/Qwen2.5-1.5B-Instruct-AWQ
    dtype: float16
    trust_remote_code: true

tasks:
  - name: mmlu
    split: test
    subjects:
      - abstract_algebra
      - college_computer_science
      - high_school_statistics
      - machine_learning
    limit: 100

  - name: gsm8k
    split: test
    limit: 200
    fewshot: 1
    max_new_tokens: 256
```

Current running command:

```bash
python -m pilot_eval.run --config configs/kaggle_qwen_public_quantized.yaml
```

After it finishes, run:

```bash
python -m pilot_eval.analyze \
  --run-dir /kaggle/working/results/kaggle_qwen25_1p5b_public_quantized \
  --baseline fp16 \
  --bootstrap 1000
```

Then inspect:

```bash
ls /kaggle/working/results/kaggle_qwen25_1p5b_public_quantized
cat /kaggle/working/results/kaggle_qwen25_1p5b_public_quantized/pair_summary.csv
cat /kaggle/working/results/kaggle_qwen25_1p5b_public_quantized/rank_instability.csv
```

If the run succeeds, package outputs:

```bash
python scripts/kaggle_pack_outputs.py
```

---

## How To Interpret The Public-Checkpoint Run

This run can support:

- Testing whether the evaluation pipeline handles real Qwen checkpoints.
- Measuring net accuracy deltas between FP16, public GPTQ, and public AWQ.
- Measuring harmful flips, beneficial flips, gross accuracy-state churn, wrong-to-different-wrong churn, and total answer churn.
- Measuring item-bootstrap ranking instability between public GPTQ and public AWQ.

This run cannot support:

- H3 calibration-seed instability, because there is only one fixed public checkpoint per method and the calibration data/seed is not controlled.

If the public run shows churn despite small net accuracy deltas, that is a promising H1/H2 pilot signal. If it shows no churn and no rank instability, do not kill the paper immediately; the public checkpoints may be too polished or incomparable. The real test still needs controlled local quantization seeds.

---

## If The Current Public-Checkpoint Run Fails

Likely failure modes:

### A. Public GPTQ/AWQ checkpoint requires missing quantization loaders

If loading `Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4` or `Qwen/Qwen2.5-1.5B-Instruct-AWQ` fails because `auto-gptq`, `autoawq`, or a CUDA extension is missing, do not spend too long patching Kaggle.

Fallback: use Kaggle for FP16 vs built-in Hugging Face/bitsandbytes quantized loading instead. This is less aligned with GPTQ/AWQ, but useful for checking churn and pipeline behavior.

Need next-agent action: add a config/modeling path for bitsandbytes 4-bit loading, or manually modify `pilot_eval/modeling.py` to accept quantization config fields.

### B. Out of memory

For Qwen2.5-1.5B on T4 x2, OOM is not expected, but possible if multiple models remain loaded or the environment fragments memory.

Try:

```bash
python -m pilot_eval.run \
  --config configs/kaggle_qwen_public_quantized.yaml \
  --only-method fp16
```

Then separately:

```bash
python -m pilot_eval.run \
  --config configs/kaggle_qwen_public_quantized.yaml \
  --only-method gptq_public
```

Then:

```bash
python -m pilot_eval.run \
  --config configs/kaggle_qwen_public_quantized.yaml \
  --only-method awq_public
```

The runner writes method/task JSONLs into the same run directory, so analysis can be run after all three finish.

### C. Dataset/model download issue

Make sure Kaggle Internet is enabled in notebook settings. If Qwen model access fails, check if the model is gated or if Hugging Face token is needed. Qwen2.5 1.5B normally should not require a token, but a Kaggle secret `HF_TOKEN` can be added if needed.

---

## Time/Compute Estimate Discussed

On Kaggle GPU T4 x2:

- Smoke test: roughly 5-15 minutes, mostly downloads/install.
- Minimal real pair with local quantization, if quantization worked: estimated 1.5-4 hours.
- Full Qwen2.5-1.5B pilot with six locally quantized checkpoints: estimated 4-10 hours.

But local quantization did not work due to `auto-gptq` install failure, so current public-checkpoint run should be faster than full local quantization. Expected rough range for public FP16/GPTQ/AWQ evaluation on the configured 100 MMLU-per-subject subset plus 200 GSM8K:

- Model/download overhead: can be significant on first run.
- Evaluation: likely 1-3 hours, depending on generation speed and checkpoint loader behavior.

T4 x2 does not necessarily give 2x speedup. Current code loads/evaluates one model/method at a time. The second GPU mainly helps with memory/sharding; it is not explicit data parallel evaluation.

---

## Recommended Next Steps For New Chat

1. Ask the user whether the currently running public-checkpoint command finished or failed.
2. If it finished, ask for or inspect:
   - `pair_summary.csv`
   - `rank_instability.csv`
   - any stderr/stdout warnings
3. If it failed, classify failure as:
   - missing quantization loader,
   - OOM,
   - download/token problem,
   - code bug.
4. If it succeeded, interpret H1/H2 signals only:
   - net delta near zero plus nontrivial churn is interesting,
   - harmful and beneficial flips canceling is interesting,
   - bootstrap ranking flips between public GPTQ/AWQ are interesting,
   - but do not claim H3 calibration-seed instability.
5. Decide the next execution path:
   - If public checkpoint run works and gives signal: save/package results, then later run controlled quantization seeds on ICE/PACE.
   - If public checkpoint run fails because public quantized loaders need old packages: add a bitsandbytes 4-bit fallback for Kaggle.
   - If Kaggle remains too brittle: move all quantization work to ICE/PACE and use Kaggle only for smoke/evaluation when possible.
6. Update `handoffv1.md` and this file with the public-checkpoint results once available.

---

## One-Sentence Summary

The Kaggle smoke test passed, local GPTQ/AWQ checkpoint building failed because `auto-gptq` cannot install cleanly in Kaggle's current environment, and the user is currently running a public Qwen2.5-1.5B FP16/GPTQ/AWQ evaluation as a useful H1/H2 pilot that does not test calibration-seed instability.
