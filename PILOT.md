# Pilot Code

This is a runnable pilot scaffold for the proposal in `handoffv1.md`. It is intentionally per-item first: every model/method/task run writes JSONL records, then the analysis script computes the paper-facing metrics from those records.

## Critique of the Handoff Plan

The core idea is viable, but the pilot only tests the strongest claim if quantization is built locally with multiple calibration seeds. Public GPTQ/AWQ checkpoints can test churn and ranking noise, but usually cannot establish calibration-seed instability because the calibration data is undocumented and fixed.

The second risk is benchmark size. Tiny smoke runs are useful for plumbing only; they should not be interpreted. For the actual go/no-go gate, run enough MMLU/GSM8K items that bootstrap rank flips and churn intervals are not dominated by toy-sample noise.

The third risk is prompt sensitivity. Keep prompts, decoding settings, and answer extraction frozen before the real pilot. If they change after seeing results, the stats story gets weaker.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local quantization, install one or both optional backends:

```bash
pip install auto-gptq
pip install autoawq
```

## Smoke Test

This checks the pipeline with a tiny model and two examples per task.

```bash
python -m pilot_eval.run --config configs/smoke_tiny.yaml
python -m pilot_eval.analyze --run-dir results/smoke_tiny --baseline fp16 --bootstrap 100
```

## Build Quantized Checkpoints

Run these on ICE with a GPU node. Repeat for seeds `0`, `1`, and `2`.

```bash
python scripts/build_quantized.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --method gptq \
  --seed 0 \
  --output-dir outputs/quantized/qwen25-1p5b-gptq4-seed0 \
  --trust-remote-code

python scripts/build_quantized.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --method awq \
  --seed 0 \
  --output-dir outputs/quantized/qwen25-1p5b-awq4-seed0 \
  --trust-remote-code
```

## Run the 1.5B Pilot

```bash
python -m pilot_eval.run --config configs/pilot_qwen_1p5b.yaml
python -m pilot_eval.analyze --run-dir results/qwen25_1p5b_pilot --baseline fp16 --bootstrap 2000
```

The main outputs are:

- `*.jsonl`: per-item logs with predictions, correctness, prompt hashes, method names, and seeds.
- `pair_summary.csv`: net accuracy delta, harmful/beneficial flips, gross churn, total answer churn, bootstrap CIs, McNemar p-values, TOST outputs, and rough minimum detectable differences.
- `rank_instability.csv`: bootstrap item-resampling rank flip rates plus calibration-seed winner changes when seeds are present.

## Pilot Pass Check

Treat the pilot as promising if at least two of these hold:

- Accuracy delta stays around 1-2 points while total answer churn is roughly 8-10% or higher.
- Harmful and beneficial flips visibly cancel in `pair_summary.csv`.
- GPTQ/AWQ ranking flips in roughly 20-30% of bootstrap resamples or across calibration seeds.
- `required_n_for_observed_delta_80_power` suggests a benchmark would need roughly 2x-5x more items to detect the observed degradation.
