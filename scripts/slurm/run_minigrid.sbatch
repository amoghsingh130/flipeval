#!/bin/bash
#SBATCH --job-name=flipeval-minigrid
#SBATCH --output=logs/minigrid_%A_%a.out
#SBATCH --error=logs/minigrid_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=20:00:00
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
# WALLTIME (raised 12h -> 20h, 2026-07-25). The 12 h above was derived from the
# ~7.6 s/item FP16 genspeed figure, at a time when no QUANTIZED GSM8K cell had
# completed anywhere -- an unmeasured limit inherited from a faster
# configuration. Measured on the escalation grid: Qwen-7B AWQ GSM8K runs ~47
# s/item (~12.4 h/cell), Llama-8B AWQ 20-36 s/item, against ~13 s/item for the
# same models under GPTQ. 12 h would have truncated the slowest cells too.
# 20 h is ~61% headroom over the worst measured projection. GSM8K writes its
# JSONL only at the end, so a walltime overrun destroys the whole cell -- never
# trim this to a thin margin, and never override it on the sbatch line.
#
# Index map: idx -> model = idx/22, then rem = idx%22 -> method = rem/2,
# task = rem%2. Model-major so a single model's 22 jobs are a contiguous range
# and can be submitted alone (e.g. --array=0-21 for Qwen).
#
# EVERY GRID-SELECTING INPUT IS REQUIRED -- there are no defaults, deliberately.
#
#   MINIGRID_CONFIG    container path to the grid config
#   MINIGRID_MODELS    space-separated model tags, in index order
#
# This script had defaults for both until 2026-07-25. On that date a resubmit of
# ten escalation cells omitted the declaration, fell through to the mini-grid
# defaults, and opened ten cells of the SEALED, ARCHIVED, PAPER-CITED mini-grid
# in write mode (array 11485972, incident 24). Only the 0444 seal on those JSONLs
# turned it into a PermissionError instead of a truncation.
#
# The asymmetry that allowed it: verify_minigrid.sbatch was hardened to ${VAR:?}
# weeks earlier, so the READER fails closed on a missing grid declaration while
# the WRITER failed open, into write mode, against whatever the default pointed
# at. A runner that can silently target the wrong grid is strictly more dangerous
# than a validator that can, because it writes. NO JOB SCRIPT IS EVER GIVEN A
# DEFAULT GRID -- never reintroduce one here.
#
# There is deliberately no MINIGRID_RESULTS: unlike verify_minigrid.py,
# pilot_eval.run takes no results root and derives run_dir from the config alone
# (`run.output_dir / run.run_name`). Requiring a variable this script cannot act
# on would be a control that looks present and does nothing -- the exact family
# of defect as the inert --exclude and --requeue flags (incidents 11 and 21).
# MINIGRID_CONFIG is the single thing that selects where output lands.

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

: "${MINIGRID_CONFIG:?required (no default: a default targets the wrong grid IN WRITE MODE)}"
: "${MINIGRID_MODELS:?required (space-separated model tags; no default, see above)}"
: "${SLURM_ARRAY_TASK_ID:?required (this script is an array job and has no single-cell mode)}"

CONFIG="$MINIGRID_CONFIG"
# shellcheck disable=SC2206  # word-splitting into the array is intended here
MODELS=(${MINIGRID_MODELS})
METHODS=(fp16 gptq_s0 gptq_s1 gptq_s2 gptq_s3 gptq_s4 awq_s0 awq_s1 awq_s2 awq_s3 awq_s4)
TASKS=(mmlu gsm8k)

# The idx->cell map assumes exactly 2 models x 22 variants. A MINIGRID_MODELS of
# the wrong length would otherwise index past the array and hand pilot_eval.run
# an empty --model-tag rather than failing.
if [ "${#MODELS[@]}" -ne 2 ]; then
  echo "FATAL: MINIGRID_MODELS must name exactly 2 model tags, got ${#MODELS[@]}: ${MODELS[*]}" >&2
  exit 1
fi

IDX=$SLURM_ARRAY_TASK_ID
MODEL=${MODELS[$((IDX / 22))]}
REM=$((IDX % 22))
METHOD=${METHODS[$((REM / 2))]}
TASK=${TASKS[$((REM % 2))]}

if [ -z "$MODEL" ] || [ -z "$METHOD" ] || [ -z "$TASK" ]; then
  echo "FATAL: array index $IDX does not map to a cell (model='$MODEL' method='$METHOD' task='$TASK')" >&2
  exit 1
fi

# Echo the declaration itself, not just its consequences: per the standing rule
# that a scheduler control is in force only when observed, the job's own first
# lines are the record of what it was actually told to run.
echo "minigrid grid: config=$CONFIG models=${MODELS[*]}"
echo "minigrid cell: model=$MODEL method=$METHOD task=$TASK (array index $IDX)"

srun apptainer exec --cleanenv --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m pilot_eval.run \
  --config "$CONFIG" \
  --model-tag "$MODEL" \
  --only-method "$METHOD" \
  --only-task "$TASK"

echo "Done: $MODEL / $METHOD / $TASK"
