# Kaggle Public-Checkpoint Pilot Completion Handoff (Historical)

Last updated: 2026-07-10 America/New_York (the packaged artifact is timestamped 2026-07-11 UTC).

> Superseded for current actions by `KAGGLE.md` and `STATUS.md`. This file describes the earlier public FP16/GPTQ/AWQ pilot, not the current FP16 chat-template validation gate.

This is a continuation handoff. Read these earlier documents first:

- [`handoffv1.md`](handoffv1.md) for the research question, novelty constraints, hypotheses, statistical plan, pass/fail criteria, and broader compute strategy.
- [`KAGGLE_CHAT_HANDOFF_2026-07-10.md`](KAGGLE_CHAT_HANDOFF_2026-07-10.md) for Kaggle setup, the failed local-quantization attempt, the pivot to public checkpoints, and the original public-checkpoint configuration.

This document records what happened after the public-checkpoint evaluation began, how the GPTQ loader was recovered, what completed, what remains unverified, and the exact next actions.

---

## Current State

The user reports that the FP16, public GPTQ, and public AWQ evaluation/analysis scripts finished and that Kaggle produced:

```text
/kaggle/working/pilot_outputs_20260711T000427Z.tar.gz
```

The archive exists only in the live Kaggle environment until it is downloaded or preserved in a saved Kaggle version. Its contents and checksum have not yet been brought into this local repository.

The actual values in `pair_summary.csv` and `rank_instability.csv` have not yet been shared. Do not claim that the pilot passed or failed until those files are inspected.

Expected run directory:

```text
/kaggle/working/results/kaggle_qwen25_1p5b_public_quantized
```

Expected evaluation files and line counts:

```text
fp16.mmlu.jsonl          400
fp16.gsm8k.jsonl         200
gptq_public.mmlu.jsonl   400
gptq_public.gsm8k.jsonl  200
awq_public.mmlu.jsonl    400
awq_public.gsm8k.jsonl   200
```

Expected analysis files:

```text
pair_summary.csv
rank_instability.csv
```

---

## Configuration Evaluated

The Kaggle-only config was `configs/kaggle_qwen_public_quantized.yaml`:

- FP16: `Qwen/Qwen2.5-1.5B-Instruct`
- GPTQ: `Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4`
- AWQ: `Qwen/Qwen2.5-1.5B-Instruct-AWQ`
- MMLU: four subjects, up to 100 test items per subject, 400 items total
- GSM8K: 200 test items, one few-shot prefix, `max_new_tokens: 256`
- Evaluation is sequential with effective batch size one; the two Kaggle GPUs are not used for explicit data parallelism.

The full YAML is preserved in the previous Kaggle handoff.

---

## Confirmed FP16 Timings

The initial combined run successfully completed FP16 before failing while loading GPTQ:

```text
fp16/mmlu:  400/400 in 01:33 (4.28 items/s)
fp16/gsm8k: 200/200 in 45:25 (13.63 s/item)
```

The FP16 JSONL files were already closed and persisted before the GPTQ load failure. Later commands used `--only-method`, so FP16 did not need to be rerun or overwritten.

The Transformers warning about ignored `temperature`, `top_p`, and `top_k` flags was harmless because project generation explicitly uses `do_sample=False`.

---

## GPTQ Failure and Recovery Timeline

### 1. Missing Optimum

The first GPTQ load failed with:

```text
ImportError: Loading a GPTQ quantized model requires optimum (`pip install optimum`)
```

`optimum` was installed in the Kaggle notebook.

### 2. Missing/Incompatible GPTQ Backend

The next attempt raised:

```text
NameError: name 'QuantizeConfig' is not defined
```

This showed that Optimum alone was not a usable GPTQ execution backend in the current package combination. `gptqmodel` was then installed with:

```bash
pip install -q gptqmodel --no-build-isolation
```

Pip reported numerous conflicts with preinstalled Kaggle/Colab packages, including `protobuf`, `numpy`, `pandas`, and Jupyter-related constraints. Those warnings did not prevent GPTQModel from installing, but they mean the resulting environment is not a clean or controlled dependency environment.

### 3. Marlin CUDA Compilation Failure

GPTQModel initially attempted to compile its Marlin CUDA extension and emitted a very long series of errors from `marlin_template.h`, including undefined `dequant` and `dequant_fp8_scales` identifiers and incompatible operand types.

This was a CUDA extension/toolchain compatibility failure, not corrupt model weights or corrupt evaluation results. Continuing to install additional CUDA packages was explicitly avoided.

### 4. Force the Portable Torch Backend

The Kaggle copy of `pilot_eval/modeling.py` was patched so `gptq_public` passes an explicit Transformers `GPTQConfig`:

```python
load_kwargs = {}
if method.name == "gptq_public":
    from transformers import GPTQConfig

    load_kwargs["quantization_config"] = GPTQConfig(
        bits=4,
        backend="gptq_torch",
    )

model = AutoModelForCausalLM.from_pretrained(
    method.model_id,
    revision=method.revision,
    trust_remote_code=method.trust_remote_code,
    torch_dtype=torch_dtype,
    device_map=run.device_map,
    **load_kwargs,
)
```

An initial notebook text-replacement added `**load_kwargs` without successfully inserting the definition, causing:

```text
NameError: name 'load_kwargs' is not defined
```

A follow-up patch inserted the definition shown above. This edit was made only in `/kaggle/working/compression-eval`; the local repository's `pilot_eval/modeling.py` remains unchanged.

### 5. Interrupted Import Was Not a Pathlib Failure

One retry ended in a traceback containing internal `PosixPath._str` and `_drv` `AttributeError` messages. The actual final exception was:

```text
^C
KeyboardInterrupt
```

The process had been manually interrupted while `importlib.metadata.packages_distributions()` scanned the now-expanded Python environment. The `pathlib` messages were internal lazy-cache lookups exposed by the interruption, not independent filesystem errors.

### 6. Successful TorchLinear Load

The successful environment reported:

```text
GPT-QModel   : 7.1.0
Transformers : 5.13.0
Torch        : 2.10.0+cu128
Triton       : 3.6.0
Kernel       : TorchLinear
```

It also reported that GPTQ v1 was converted internally to GPTQ v2 and that TorchLinear compilation was triggered. The short compatibility test then completed:

```text
gptq_public/mmlu: 400/400 in 02:41 (2.48 items/s)
```

The user subsequently reported GPTQ GSM8K reaching `200/200`.

---

## Warnings That Were Nonfatal

The successful GPTQ run included several noisy but nonfatal messages:

- Unauthenticated Hugging Face Hub requests: affects rate limits/download reliability, not scores.
- `torch_dtype` deprecation: project uses an older keyword; behavior still worked.
- GPTQModel C++ extensions skipped because it requested Torch >= 2.11 while Kaggle had 2.10: the forced TorchLinear fallback still loaded and evaluated.
- Quantization-config merge warning: the checkpoint's saved quantization settings were retained while the explicitly passed backend setting overrode the loading backend.
- Python GIL warning: relevant to quantization/packing throughput, not the correctness of this single-model evaluation.
- `fatal: not a git repository`: GPTQModel attempted to query Git metadata in the Kaggle staged directory; evaluation continued.
- Hugging Face `HEAD` requests returning 404 for optional dataset scripts or `custom_generate/generate.py`: capability probes; cached/configured resources loaded afterward.
- Blank `text/plain`/`text/html` log objects: notebook rendering noise from GPTQModel's logger.

---

## AWQ and Packaging Status

After GPTQ reached `200/200`, the instructed sequence was:

```bash
python -m pilot_eval.run \
  --config configs/kaggle_qwen_public_quantized.yaml \
  --only-method awq_public \
  --only-task mmlu

python -m pilot_eval.run \
  --config configs/kaggle_qwen_public_quantized.yaml \
  --only-method awq_public \
  --only-task gsm8k

python -m pilot_eval.analyze \
  --run-dir /kaggle/working/results/kaggle_qwen25_1p5b_public_quantized \
  --baseline fp16 \
  --bootstrap 1000

python scripts/kaggle_pack_outputs.py
```

The user then reported the packaged archive path, implying this sequence completed. However, the AWQ console output, exact line counts, analysis table, and archive listing were not pasted. Treat completion as user-reported until verified from the archive.

---

## Immediate Verification and Preservation

Run this as one Kaggle notebook cell. `%%bash` is important because it keeps the shell variables in one process. Quotes are used even though these paths currently contain no spaces.

```bash
%%bash
RUN="/kaggle/working/results/kaggle_qwen25_1p5b_public_quantized"
ARCHIVE="/kaggle/working/pilot_outputs_20260711T000427Z.tar.gz"

wc -l "$RUN"/*.jsonl
cat "$RUN/pair_summary.csv"
cat "$RUN/rank_instability.csv"
tar -tzf "$ARCHIVE"
sha256sum "$ARCHIVE"
```

Then:

1. Download `pilot_outputs_20260711T000427Z.tar.gz` from Kaggle's Files/Output panel.
2. Save a Kaggle notebook version so the output remains recoverable.
3. Bring the archive into the next chat/workspace for inspection.
4. Record the SHA-256 checksum in the experiment log.

Do not start another evaluation before inspecting these results.

---

## How To Interpret the Pending CSVs

`pair_summary.csv` contains, per task and compressed method:

- baseline and compressed accuracy
- net accuracy delta
- harmful and beneficial flip rates
- accuracy-state churn
- wrong-to-different-wrong churn
- total answer churn
- bootstrap confidence intervals
- McNemar test results
- TOST equivalence results at the configured two-point margin
- minimum detectable difference and estimated sample requirement

`rank_instability.csv` measures how often the public GPTQ-versus-AWQ winner changes across item-bootstrap resamples.

The pilot's predeclared promising signals, from the earlier handoff/proposal, include at least two of:

- net accuracy within roughly 1-2 points while gross churn is roughly 8-10% or higher
- harmful and beneficial flips substantially cancel
- GPTQ/AWQ rank flips in roughly 20-30% or more of bootstrap resamples
- estimated required sample size is roughly 2-5 times the evaluated subset

Do not mechanically declare a pass from thresholds alone. Inspect confidence intervals, absolute task accuracy, paired item counts, and whether effects agree across MMLU and GSM8K.

---

## Methodological Limitations To Preserve

1. This public-checkpoint run can test H1/H2-style churn and ranking noise, but it cannot test H3 calibration-seed instability. Calibration data and seeds for the public checkpoints are fixed or undocumented.
2. GPTQ was executed through GPTQModel's portable `TorchLinear` backend after runtime conversion from GPTQ v1 to its internal GPTQ v2 representation. Record this in any result table or experiment manifest.
3. The Kaggle Python environment was materially changed by installing current Optimum/GPTQModel packages and showed dependency conflicts. This is acceptable for exploratory evidence, not a controlled final experiment.
4. The project currently feeds Qwen raw text prompts rather than applying Qwen's chat template. Paired comparisons remain meaningful because methods receive the same prompts, but absolute MMLU/GSM8K accuracy may not represent standard Qwen-Instruct performance. Very low absolute accuracy should trigger a prompt-format audit before scaling.
5. MMLU has 400 items and GSM8K has 200 in this pilot. Confidence intervals will be wide, score resolution is 0.25 and 0.5 percentage points respectively, and rank-instability estimates describe these subsets rather than full benchmarks.
6. Public GPTQ and AWQ checkpoints may differ in undocumented production details beyond the method label. Final causal claims require locally built checkpoints with controlled base weights, calibration samples, seeds, software, and kernels.

---

## Next Decision After Archive Inspection

If the public run shows small net deltas with substantial paired churn or unstable GPTQ/AWQ ordering:

- preserve the result as motivating pilot evidence
- move controlled checkpoint construction to ICE/PACE or another pinned Python/CUDA environment
- run multiple calibration seeds and datasets to test H3
- fix/apply the intended prompt template before final benchmark runs
- use measured per-model timings to replace placeholder PACESHIP compute estimates

If the public run shows no churn or rank instability:

- do not immediately reject the paper concept
- audit prompts, extraction, paired IDs, and absolute task accuracy
- recognize that polished public checkpoints are not a controlled method comparison
- make the controlled multi-seed experiment the deciding test

If the public run shows very large degradation:

- treat loader/backend/prompt incompatibility as the leading explanation
- inspect per-item outputs and environment details before interpreting it as quantization damage

The next concrete action is to inspect the downloaded archive and report the actual CSV values. No further Kaggle compute is required until that interpretation is complete.
