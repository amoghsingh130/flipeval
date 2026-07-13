# FlipEval

FlipEval measures paired, per-item behavioral change between a baseline model and a compressed or otherwise modified model. It reports net accuracy change alongside harmful and beneficial flips, answer churn, paired significance and equivalence tests, confidence intervals, power estimates, and method-rank stability.

## Install

```bash
python -m pip install -e .
pytest
```

## Usage

```python
import json
from flipeval import compare

def load(path):
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]

baseline = load("fp16.mmlu.jsonl")
method = load("gptq.mmlu.jsonl")
result = compare(baseline, method, margin=0.02, bootstrap=1000, seed=0)
print(result.net_accuracy_delta, result.accuracy_state_churn)
```

The CLI writes a one-row CSV and prints the full result:

```bash
flipeval compare fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --output comparison.csv
flipeval compare baseline_samples.json method_samples.json --format lm-eval
```

Each native record must contain `item_id`, `prediction`, and `correct`. Paired records are aligned by `item_id`; duplicate IDs are rejected. The lm-evaluation-harness adapter targets the v0.4.x `--log_samples` schema represented by v0.4.12 and accepts either a full result JSON with a `samples` mapping or a sample JSON/JSONL file.

## Reproducibility

Bootstrap results are deterministic for a given seed. `python -m pilot_eval.analyze` remains available as a compatibility CLI and uses FlipEval internally. The golden test regenerates the archived pilot summaries from `results/pilot_outputs_20260711T000427Z.tar.gz`.

Licensed under Apache-2.0.
