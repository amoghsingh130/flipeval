#!/bin/bash
#SBATCH --job-name=flipeval-calibration
#SBATCH --output=logs/calibration_%A_%a.out
#SBATCH --error=logs/calibration_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --array=0-2%1

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

SEED=$SLURM_ARRAY_TASK_ID
srun apptainer exec --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/build_quantized.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --model-revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 \
  --seed "$SEED" \
  --dataset c4 \
  --dataset-cache-dir /scratch/hf_cache/datasets \
  --calibration-artifact "/scratch/calibration/qwen25-1p5b-c4-s${SEED}.json" \
  --prepare-calibration-only \
  --trust-remote-code \
  ${VERIFY_ROW_COUNT:+--verify-stream-row-count}
