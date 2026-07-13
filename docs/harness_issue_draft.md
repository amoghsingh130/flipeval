# Draft issue: Add paired `compare` mode for per-sample evaluation logs

Do not post without human review.

## Motivation

Aggregate scores hide whether a model changed behavior on the same items, and a nonsignificant aggregate delta does not establish equivalence. In a 600-item quantization pilot, GSM8K changed correctness state on 22-25% of items and changed 62-63% of extracted answers despite only a +1 to +2 point net accuracy change; the GPTQ-versus-AWQ winner also changed in 42.4% of item bootstraps. A harness-native paired comparison would make these diagnostics available wherever `--log_samples` is already used.

## Proposed CLI

```bash
lm_eval compare \
  --baseline results/fp16 \
  --candidate results/gptq-int4 \
  --tasks mmlu,gsm8k \
  --equivalence-margin 0.02 \
  --bootstrap-iters 2000 \
  --seed 0 \
  --output_path comparisons/gptq-vs-fp16
```

The command would align logged samples by task, document ID, filter, and task hashes; reject incompatible task/prompt/target hashes; and use task-produced per-sample metrics and filtered responses. A multiple-candidate form could additionally compute item-bootstrap ranking stability.

## Proposed Output

```json
{
  "schema_version": "compare-1",
  "baseline": "results/fp16",
  "candidate": "results/gptq-int4",
  "settings": {"margin": 0.02, "bootstrap_iters": 2000, "seed": 0},
  "tasks": {
    "mmlu": {
      "n": 400,
      "baseline_accuracy": 0.455,
      "candidate_accuracy": 0.4125,
      "net_accuracy_delta": -0.0425,
      "harmful_flip_rate": 0.095,
      "beneficial_flip_rate": 0.0525,
      "accuracy_state_churn": 0.1475,
      "wrong_to_different_wrong_churn": 0.0725,
      "total_answer_churn": 0.22,
      "confidence_intervals": {},
      "mcnemar": {"b": 38, "c": 21, "p": 0.036343},
      "tost": {"equivalent": false, "margin": 0.02, "p_low": 0.880144, "p_high": 0.000583},
      "mdd_80_power": 0.053535,
      "required_n_80_power": 635
    }
  }
}
```

## Compatibility

The prototype converter targets the v0.4.x logged-sample schema (checked against v0.4.12): `doc_id`, `doc`, `target`, `resps`, `filtered_resps`, metric names/values, and prompt/target hashes. No evaluator execution changes are required for an initial implementation.
