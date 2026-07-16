#!/bin/bash
#SBATCH --job-name=flipeval-bridge
#SBATCH --output=logs/bridge_%A_%a.out
#SBATCH --error=logs/bridge_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=08:00:00
#SBATCH --array=0-6

source "$(dirname "$0")/env.sh"
mkdir -p logs results/qwen25_1p5b_bridge_chat

METHODS=(fp16 gptq_s0 gptq_s1 gptq_s2 awq_s0 awq_s1 awq_s2)
METHOD=${METHODS[$SLURM_ARRAY_TASK_ID]}
srun apptainer exec --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m pilot_eval.run \
  --config /workspace/configs/pace_bridge_chat.yaml \
  --only-method "$METHOD"
