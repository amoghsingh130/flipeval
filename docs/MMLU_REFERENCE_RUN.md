# Trusted MMLU reference run

This run adjudicates the FP16 validation gate. It uses the preserved model revision,
the same four subjects, the same first 100 test indices per subject, zero-shot, and
the tokenizer chat template. Do not run PACE, the quantized bridge, or the main grid
until its item-level samples have been compared with the archived pilot records.

> **Executed 2026-07-13** via `notebooks/kaggle_mmlu_reference_run.ipynb` on a Kaggle
> T4 (lm_eval 0.4.12, torch 2.10.0+cu128, transformers 5.0.0, Python 3.12.13).
> Zero-shot reference accuracy 0.415 vs pilot 0.430, prediction agreement 72.5%,
> five-shot anchor 0.470 mean. The one deviation from the literal commands below is
> that `pretrained=` pointed at the locally materialized snapshot of the pinned
> revision (the validated recovery for the Kaggle hub-load stall); the snapshot
> directory name was asserted equal to the revision. Preserved archive:
> `kaggle_mmlu_reference_run.tar.gz` at repository root, SHA-256
> `d20d10fc47633707eb1ac356da66c5c1a4fb092799a0dc749463a8dd42fd7e18`. The resulting
> gate decision record is `docs/GATE_DECISION_2026-07-13.md` (gate: PASS with the
> corrected MMLU range 0.415 ± 0.05).

## Environment and zero-shot run

Use the already resolved project version, `lm_eval==0.4.12`. On a T4 Kaggle runtime:

```bash
python -m lm_eval \
  --model hf \
  --model_args pretrained=Qwen/Qwen2.5-1.5B-Instruct,revision=989aa7980e4cf806f80c7fef2b1adb7bc71aa306,dtype=float16 \
  --tasks mmlu_abstract_algebra,mmlu_college_computer_science,mmlu_high_school_statistics,mmlu_machine_learning \
  --num_fewshot 0 \
  --limit 100 \
  --batch_size auto \
  --apply_chat_template \
  --log_samples \
  --output_path results/lm_eval_mmlu_0shot
```

Record the package version (`python -m lm_eval --version`), GPU, full command, model
revision, and output hashes with the result. A run against a mutable model alias is
not an acceptable reference.

Extract the preserved pilot record, then compare all 400 predictions:

```bash
mkdir -p results/kaggle_validation
tar -xzf kaggle_qwen25_1p5b_fp16_chat_validation.tar.gz -C results/kaggle_validation
python scripts/compare_mmlu_reference.py \
  results/kaggle_validation/kaggle_qwen25_1p5b_fp16_chat_validation/fp16.mmlu.jsonl \
  results/lm_eval_mmlu_0shot \
  --output results/mmlu_reference_diff_0shot.csv
```

Interpretation was fixed before seeing the reference result:

- If prediction agreement is at least 95% and reference accuracy is near 0.43, treat
  the implementation as validated and replace the invalid absolute gate with a gate
  derived from this reference result plus a documented tolerance.
- If reference accuracy is materially higher or agreement is below 95%, inspect the
  `pilot_b_disagreement` rows first. Compare leading whitespace, continuation length
  normalization, and the assistant-boundary likelihood span before changing code.
- Do not treat B-label frequency alone as evidence of a defect.

## Five-shot comparability anchor

Run the identical command again with `--num_fewshot 5` and a distinct output path:

```bash
python -m lm_eval \
  --model hf \
  --model_args pretrained=Qwen/Qwen2.5-1.5B-Instruct,revision=989aa7980e4cf806f80c7fef2b1adb7bc71aa306,dtype=float16 \
  --tasks mmlu_abstract_algebra,mmlu_college_computer_science,mmlu_high_school_statistics,mmlu_machine_learning \
  --num_fewshot 5 \
  --limit 100 \
  --batch_size auto \
  --apply_chat_template \
  --log_samples \
  --output_path results/lm_eval_mmlu_5shot
```

The five-shot result is a provenance/comparability receipt, not a replacement for
the registered zero-shot pilot protocol. Write the gate decision record before any
downstream GPU work.
