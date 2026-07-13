# PACE Runbook

## Storage Layout

Keep source, small configs, manifests, summary CSVs, and final logs in project storage. Keep model weights, Hugging Face caches, calibration caches, temporary build files, and intermediate checkpoints in scratch.

```text
$PROJECT/flipeval/                 # cloned repository and durable results
$PROJECT/flipeval/results/         # manifests, JSONLs, CSVs copied back from scratch
$SCRATCH/flipeval/hf_cache/        # model and dataset cache
$SCRATCH/flipeval/checkpoints/     # quantized checkpoints
$SCRATCH/flipeval/work/            # temporary job output
$SCRATCH/flipeval/flipeval.sif     # Apptainer image
```

Set these once:

```bash
export PROJECT=$HOME/p-<allocation>/flipeval
export SCRATCH_ROOT=$HOME/scratch/flipeval
export IMAGE=$SCRATCH_ROOT/flipeval.sif
mkdir -p "$PROJECT" "$SCRATCH_ROOT"/{hf_cache,checkpoints,work,logs}
```

## Build the Image

Build on a PACE node with outbound package access, then record the resolved environment beside the image:

```bash
cd "$PROJECT"
apptainer build "$IMAGE" flipeval.def
apptainer exec "$IMAGE" python -m pytest -q
apptainer exec "$IMAGE" cat /opt/flipeval/environment.lock.txt > container/environment.lock.resolved.txt
```

The CPU smoke additionally downloads `tiny-gpt2` and two-item task subsets:

```bash
apptainer exec --bind "$PROJECT:/workspace,$SCRATCH_ROOT:/scratch" \
  "$IMAGE" sh /workspace/container/cpu_smoke.sh
```

## Checkpoint-Build Job

Save as `build.sbatch`. Adjust account, partition, GPU type, and wall time to the awarded allocation.

```bash
#!/bin/bash
#SBATCH --job-name=flipeval-build
#SBATCH --account=<allocation>
#SBATCH --partition=<gpu-partition>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=%x-%j.out
set -euo pipefail
export HF_HOME=$SCRATCH_ROOT/hf_cache
mkdir -p "$OUT_DIR"
srun apptainer exec --nv --bind "$PROJECT:/workspace,$SCRATCH_ROOT:/scratch" "$IMAGE" \
  python /workspace/scripts/build_quantized.py \
  --model-id "$MODEL_ID" --method "$METHOD" --bits "$BITS" --seed "$SEED" \
  --output-dir "$OUT_DIR" --trust-remote-code
```

Submit one checkpoint explicitly:

```bash
sbatch --export=ALL,PROJECT="$PROJECT",SCRATCH_ROOT="$SCRATCH_ROOT",IMAGE="$IMAGE",MODEL_ID=Qwen/Qwen2.5-1.5B-Instruct,METHOD=gptq,BITS=4,SEED=0,OUT_DIR="$SCRATCH_ROOT/checkpoints/qwen25-1p5b-gptq4-s0" build.sbatch
```

## Evaluation Job

```bash
#!/bin/bash
#SBATCH --job-name=flipeval-eval
#SBATCH --account=<allocation>
#SBATCH --partition=<gpu-partition>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=%x-%j.out
set -euo pipefail
export HF_HOME=$SCRATCH_ROOT/hf_cache
cd "$PROJECT"
ARGS=()
if [[ -n "${ONLY_METHOD:-}" ]]; then ARGS+=(--only-method "$ONLY_METHOD"); fi
srun apptainer exec --nv --bind "$PROJECT:/workspace,$SCRATCH_ROOT:/scratch" "$IMAGE" \
  python -m pilot_eval.run --config "$CONFIG" "${ARGS[@]}"
apptainer exec --bind "$PROJECT:/workspace" "$IMAGE" \
  python -m pilot_eval.analyze --run-dir "$RUN_DIR" --baseline fp16 --bootstrap 2000
```

## Seed-Grid Array

```bash
#!/bin/bash
#SBATCH --job-name=flipeval-grid
#SBATCH --account=<allocation>
#SBATCH --partition=<gpu-partition>
#SBATCH --array=0-19
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
set -euo pipefail
METHODS=(gptq awq)
BITS=(4 3)
SEED=$((SLURM_ARRAY_TASK_ID % 5))
CELL=$((SLURM_ARRAY_TASK_ID / 5))
METHOD=${METHODS[$((CELL / 2))]}
BIT=${BITS[$((CELL % 2))]}
OUT_DIR="$SCRATCH_ROOT/checkpoints/${MODEL_TAG}-${METHOD}${BIT}-s${SEED}"
export METHOD BITS=$BIT SEED OUT_DIR
srun apptainer exec --nv --bind "$PROJECT:/workspace,$SCRATCH_ROOT:/scratch" "$IMAGE" \
  python /workspace/scripts/build_quantized.py --model-id "$MODEL_ID" --method "$METHOD" \
  --bits "$BITS" --seed "$SEED" --output-dir "$OUT_DIR" --trust-remote-code
```

## Day-One Bridge Sequence

1. Build the image and run `pytest` plus `container/cpu_smoke.sh`.
2. Copy `container/environment.lock.resolved.txt` into project storage before any GPU run.
3. Submit the six Qwen2.5-1.5B 4-bit checkpoint builds for GPTQ/AWQ seeds 0-2.
4. Symlink completed checkpoints into the paths expected by `configs/pace_bridge_chat.yaml`.
5. Submit the FP16 method first, then each compressed method separately. Manifest merging preserves every invocation.
6. Analyze only after all expected JSONLs exist; archive configs, manifest, JSONLs, CSVs, SLURM logs, and environment lock together.

```bash
cd "$PROJECT"
sbatch --export=ALL,CONFIG=configs/pace_bridge_chat.yaml,RUN_DIR=results/qwen25_1p5b_bridge_chat,ONLY_METHOD=fp16 eval.sbatch
for method in gptq_s0 gptq_s1 gptq_s2 awq_s0 awq_s1 awq_s2; do
  sbatch --export=ALL,CONFIG=configs/pace_bridge_chat.yaml,RUN_DIR=results/qwen25_1p5b_bridge_chat,ONLY_METHOD="$method" eval.sbatch
done
```

Do not launch the full preregistered grid until the bridge confirms chat-template accuracy and preserves the pilot's paired-signal interpretation.
