# Public-Checkpoint Pilot Results

Archive: `pilot_outputs_20260711T000427Z.tar.gz`  
SHA-256: `a72ff2fd8cf3c3d6a469941f0013217954101cd84fddb384c2b078898a72ecb8`

| Task | Method | n | FP16 acc. | Compressed acc. | Net delta | Harmful | Beneficial | State churn | Total churn | McNemar p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GSM8K | GPTQ public | 200 | 0.450 | 0.470 | +0.020 | 0.115 | 0.135 | 0.250 | 0.630 | 0.672 |
| GSM8K | AWQ public | 200 | 0.450 | 0.460 | +0.010 | 0.105 | 0.115 | 0.220 | 0.620 | 0.880 |
| MMLU | GPTQ public | 400 | 0.455 | 0.4125 | -0.0425 | 0.095 | 0.0525 | 0.1475 | 0.220 | 0.036 |
| MMLU | AWQ public | 400 | 0.455 | 0.435 | -0.020 | 0.0925 | 0.0725 | 0.165 | 0.235 | 0.389 |

| Task | Full-sample winner | Bootstrap rank-flip rate | Required n, GPTQ | Required n, AWQ |
|---|---|---:|---:|---:|
| GSM8K | GPTQ public | 0.424 | 4,923 | 17,347 |
| MMLU | AWQ public | 0.144 | 635 | 3,238 |

## Caveats

- Prompts were raw text; Qwen's chat template was not applied. Paired comparisons remain useful, but absolute accuracy is below a standard instruct-model evaluation.
- The Kaggle environment was modified in place and had package conflicts. It is exploratory evidence, not the controlled final environment.
- GPTQ ran with GPTQModel's portable TorchLinear backend after GPTQ v1-to-v2 conversion.
- GPTQ and AWQ were public checkpoints with fixed or undocumented calibration and production details. This pilot cannot test H3 or support controlled causal method comparisons.
- Sample sizes were small: 400 MMLU items and 200 GSM8K items. Confidence intervals are wide and rank-instability estimates apply to these subsets.
