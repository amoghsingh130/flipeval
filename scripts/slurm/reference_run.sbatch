#!/bin/bash
#SBATCH --job-name=flipeval-reference
#SBATCH --output=logs/reference_%A_%a.out
#SBATCH --error=logs/reference_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=12:00:00
#SBATCH --array=0-3

# Trusted lm-evaluation-harness reference runs, from which the mini-grid FP16
# operational acceptance ranges are derived.
#
# Procedure: docs/MMLU_REFERENCE_RUN.md (registered by mini-grid registration
# section 2, which freezes the derivation procedure and not the values).
# Arithmetic and tolerance: docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md,
# committed BEFORE this script was first submitted so the tolerance cannot be
# tuned to a reference number.
#
# The reference is deliberately an INDEPENDENT implementation -- the harness's
# own prompt construction and scorer, not pilot_eval's. That is what makes the
# range a check on our implementation rather than a restatement of it.
#
# Array index -> (model, task):
#   0  Qwen2.5-1.5B-Instruct  MMLU     2  Llama-3.2-3B-Instruct  MMLU
#   1  Qwen2.5-1.5B-Instruct  GSM8K    3  Llama-3.2-3B-Instruct  GSM8K

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

# Revisions are the pinned ones in configs/main_grid_manifest.yaml. A reference
# run against a mutable model alias is not an acceptable reference
# (docs/MMLU_REFERENCE_RUN.md).
TAGS=(qwen25-1p5b qwen25-1p5b llama32-3b llama32-3b)
MODEL_IDS=(
  Qwen/Qwen2.5-1.5B-Instruct
  Qwen/Qwen2.5-1.5B-Instruct
  meta-llama/Llama-3.2-3B-Instruct
  meta-llama/Llama-3.2-3B-Instruct
)
REVISIONS=(
  989aa7980e4cf806f80c7fef2b1adb7bc71aa306
  989aa7980e4cf806f80c7fef2b1adb7bc71aa306
  0cb88a4f764b7a12671c53f0838cd831a0843b95
  0cb88a4f764b7a12671c53f0838cd831a0843b95
)
TASKS=(mmlu gsm8k mmlu gsm8k)

IDX=$SLURM_ARRAY_TASK_ID
TAG=${TAGS[$IDX]}
MODEL_ID=${MODEL_IDS[$IDX]}
REVISION=${REVISIONS[$IDX]}
TASK=${TASKS[$IDX]}

# MMLU: full test split, all 57 subjects, zero-shot -- the registered pilot
# protocol carries no exemplars, and the 2026-07-13 Qwen reference was
# --num_fewshot 0.
#
# GSM8K: first 1,000 test items, 3-shot. Three, not one: mini-grid registration
# Amendment 2 (2026-07-21) binds the mini-grid to the validated bridge
# configuration's prompt, and pilot_eval.tasks.GSM8K_FEWSHOT is a fixed block of
# three worked examples. Matching the shot count keeps the comparison to a
# prompt-format difference rather than stacking a shot-count difference on top.
#
# --fewshot_as_multiturn false is REQUIRED, not optional. lm-eval 0.4.12
# auto-enables multiturn whenever a chat template is applied ("Using default
# fewshot_as_multiturn=True"), which puts each exemplar in its own
# user/assistant turn pair. The preregistration (line 43) and pilot_eval both
# place all three exemplars inline in a single user message. The first attempt
# (array 11338637, 2026-07-21) omitted this and produced multiturn prompts;
# see docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md, Amendment 1.
case "$TASK" in
  mmlu)  TASK_ARGS=(--tasks mmlu --num_fewshot 0) ;;
  gsm8k) TASK_ARGS=(--tasks gsm8k --num_fewshot 3 --limit 1000
                    --fewshot_as_multiturn false) ;;
  *) echo "unknown task: $TASK" >&2; exit 1 ;;
esac

OUT="/scratch/reference/${TAG}.${TASK}"
mkdir -p "$SCRATCH_DIR/reference"

echo "reference:  $TAG / $TASK"
echo "model:      $MODEL_ID @ $REVISION"
echo "output:     $OUT"

# --apply_chat_template: chat template is ON for every method including FP16
#   baselines (registered). Note that it also auto-enables multiturn few-shot,
#   which is why the GSM8K branch above disables that explicitly.
# --seed: lm_eval 0.4.12's own default, stated explicitly rather than inherited,
#   because GSM8K few-shot exemplars are sampled and the selection must be
#   reproducible.
srun apptainer exec --cleanenv --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m lm_eval \
  --model hf \
  --model_args "pretrained=${MODEL_ID},revision=${REVISION},dtype=float16" \
  "${TASK_ARGS[@]}" \
  --batch_size auto \
  --apply_chat_template \
  --seed 0,1234,1234,1234 \
  --log_samples \
  --output_path "$OUT"

echo "Done: $OUT"
