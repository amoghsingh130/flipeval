#!/bin/bash
#SBATCH --job-name=flipeval-build
#SBATCH --output=logs/build_%A_%a.out
#SBATCH --error=logs/build_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=06:00:00
#SBATCH --array=0-5

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs outputs/quantized

MODEL_ID="Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION="989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
METHODS=(gptq awq)
M=$((SLURM_ARRAY_TASK_ID / 3))
SEED=$((SLURM_ARRAY_TASK_ID % 3))
METHOD=${METHODS[$M]}
ARTIFACT="/scratch/calibration/qwen25-1p5b-c4-s${SEED}.json"
OUT="/workspace/outputs/quantized/qwen25-1p5b-${METHOD}4-seed${SEED}"

if [ ! -f "$CALIBRATION_DIR/qwen25-1p5b-c4-s${SEED}.json" ]; then
  echo "MISSING paired calibration artifact for seed $SEED; run prepare_calibration.sbatch" >&2
  exit 1
fi

srun apptainer exec --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/build_quantized.py \
  --model-id "$MODEL_ID" \
  --model-revision "$MODEL_REVISION" \
  --method "$METHOD" \
  --seed "$SEED" \
  --bits 4 \
  --dataset c4 \
  --calibration-artifact "$ARTIFACT" \
  --output-dir "$OUT" \
  --trust-remote-code

echo "Done: $OUT"
