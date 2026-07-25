#!/bin/bash
#SBATCH --job-name=flipeval-minigrid
#SBATCH --output=logs/minigrid_%A_%a.out
#SBATCH --error=logs/minigrid_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=12:00:00
#SBATCH --array=0-43

# H3 mini-grid evaluation fan-out: 44 jobs, one (model, method, task) each.
#
# ONE TASK PER JOB, not one method per job as in the bridge. Measured on the
# cell-3 A100 (probe 11338533, steady state with warmup separated): MMLU scoring
# is ~0.20 s/item -> ~0.8 h for 14,042 items, while GSM8K generation is ~7.6
# s/item -> ~2.1 h for 1,000. The two halves have very different cost and very
# different tail risk -- the bridge's awq_s1 GSM8K half ran 2 h 07 m against
# 22-30 m for its peers -- so splitting them keeps a slow generation half from
# putting a cheap scoring half at risk, and costs nothing: pilot_eval.run
# already accepts --only-task. It also bounds what preemption can destroy.
#
# Index map: idx -> model = idx/22, then rem = idx%22 -> method = rem/2,
# task = rem%2. Model-major so a single model's 22 jobs are a contiguous range
# and can be submitted alone (e.g. --array=0-21 for Qwen).

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

CONFIG="${MINIGRID_CONFIG:-/workspace/configs/pace_minigrid_h3.yaml}"
# Model tags are parameterized alongside the config so this one script also serves
# the escalation grid (MINIGRID_CONFIG=.../pace_escalation_h3.yaml with
# MINIGRID_MODELS="qwen25-7b llama31-8b"). The default reproduces the mini-grid
# invocation byte-for-byte; the idx->cell mapping is unchanged because both grids
# are 2 models x 22 variants = 44.
# shellcheck disable=SC2206  # word-splitting into the array is intended here
MODELS=(${MINIGRID_MODELS:-qwen25-1p5b llama32-3b})
METHODS=(fp16 gptq_s0 gptq_s1 gptq_s2 gptq_s3 gptq_s4 awq_s0 awq_s1 awq_s2 awq_s3 awq_s4)
TASKS=(mmlu gsm8k)

IDX=$SLURM_ARRAY_TASK_ID
MODEL=${MODELS[$((IDX / 22))]}
REM=$((IDX % 22))
METHOD=${METHODS[$((REM / 2))]}
TASK=${TASKS[$((REM % 2))]}

echo "minigrid cell: model=$MODEL method=$METHOD task=$TASK (array index $IDX)"

srun apptainer exec --cleanenv --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m pilot_eval.run \
  --config "$CONFIG" \
  --model-tag "$MODEL" \
  --only-method "$METHOD" \
  --only-task "$TASK"

echo "Done: $MODEL / $METHOD / $TASK"
