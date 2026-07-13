#!/bin/bash
#SBATCH --job-name=crql-build
#SBATCH --output=logs/build_%A_%a.out
#SBATCH --error=logs/build_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --array=0-5
# 6 tasks = {gptq,awq} x {seed 0,1,2}. One GPU each; they run independently.
# Add your instructional account if required, e.g.:  #SBATCH -A gts-<PI>-ice

source "$(dirname "$0")/env.sh"
mkdir -p logs

MODEL_ID="Qwen/Qwen2.5-1.5B-Instruct"
METHODS=(gptq awq)
SEEDS=(0 1 2)

# Map array index -> (method, seed): index = method_idx*3 + seed_idx
M=$(( SLURM_ARRAY_TASK_ID / 3 ))
S=$(( SLURM_ARRAY_TASK_ID % 3 ))
METHOD=${METHODS[$M]}
SEED=${SEEDS[$S]}

OUT="outputs/quantized/qwen25-1p5b-${METHOD}4-seed${SEED}"
echo "Building $METHOD seed=$SEED -> $OUT"

srun python scripts/build_quantized.py \
  --model-id "$MODEL_ID" \
  --method "$METHOD" \
  --seed "$SEED" \
  --output-dir "$OUT" \
  --trust-remote-code

echo "Done: $OUT"
