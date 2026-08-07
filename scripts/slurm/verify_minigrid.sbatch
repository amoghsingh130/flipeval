#!/bin/bash
#SBATCH --job-name=flipeval-verify-minigrid
#SBATCH --output=logs/verify_minigrid_%j.out
#SBATCH --error=logs/verify_minigrid_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00

# Fail-closed validation over the COMPLETE expected set. Run this only once
# every cell exists; it is the Stage 6 -> Stage 7 gate, and a nonzero exit means
# stop. Reading its output is the only inspection of grid results permitted
# before the grid is complete.
#
# EVERY INPUT IS REQUIRED -- there are no defaults, deliberately. This script
# previously hardcoded the mini-grid config and results root. Run unchanged
# after the escalation eval it would have validated the already-complete
# mini-grid and exited 0: a green validator certifying nothing about the grid it
# claimed to check. A default here is not a convenience, it is a wrong answer
# waiting to be believed, so an unset variable aborts before the image starts.
#
#   MINIGRID_CONFIG    container path to the grid config
#   MINIGRID_RESULTS   container path to the results root
#   MINIGRID_MODELS    space-separated model tags this run must cover
#   MINIGRID_CELLS     number of JSONL cells the grid must expand to
#   MINIGRID_OUTPUT    container path for the validation summary
#
# MINIGRID_OUTPUT is required for the same reason as the rest, and was added
# after it bit (incident 26, 2026-07-26). --output used to default to
# RESULTS_ROOT/minigrid_validation_summary.json: a filename naming ONE grid, in a
# results root BOTH grids share. The escalation run therefore overwrote the
# mini-grid's completed validation summary while declaring config, results root,
# model tags and cell count correctly -- none of which governs where output goes.
# The validator was hardened as this pair's reader; it also WRITES.
#
# MINIGRID_MODELS and MINIGRID_CELLS are the operator's declaration of which
# grid this is, made independently of the config. verify_minigrid.py checks both
# against the config, so a config/intent mismatch errors instead of quietly
# validating the wrong grid.
#
# Example (escalation):
#   export MINIGRID_CONFIG=/workspace/configs/pace_escalation_h3.yaml \
#          MINIGRID_RESULTS=/workspace/results \
#          MINIGRID_MODELS="qwen25-7b llama31-8b" \
#          MINIGRID_CELLS=44 \
#          MINIGRID_OUTPUT=/workspace/results/escalation_validation_summary.json
#   sbatch -A "$ACCOUNT" -q inferno --export=ALL scripts/slurm/verify_minigrid.sbatch

# shellcheck source=scripts/slurm/env.sh
: "${PROJECT_DIR:?required (no default): the flipeval repository root this job acts on.
  Pass it BEFORE the script path: --export=ALL,PROJECT_DIR=\"$PWD\"  (incidents 21, 29)}"
source "$PROJECT_DIR/scripts/slurm/env.sh"
mkdir -p logs

: "${MINIGRID_CONFIG:?required (no default: a default validates the wrong grid)}"
: "${MINIGRID_RESULTS:?required (no default: a default validates the wrong grid)}"
: "${MINIGRID_MODELS:?required (space-separated model tags, checked against the config)}"
: "${MINIGRID_CELLS:?required (expected cell count, checked against the config)}"
: "${MINIGRID_OUTPUT:?required (no default: a default output path names one grid and overwrites the summary of the other -- incident 26)}"

echo "verify: config=$MINIGRID_CONFIG results=$MINIGRID_RESULTS models=$MINIGRID_MODELS cells=$MINIGRID_CELLS output=$MINIGRID_OUTPUT"

# shellcheck disable=SC2086  # word-splitting MINIGRID_MODELS into argv is intended
apptainer exec --cleanenv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/verify_minigrid.py \
  --config "$MINIGRID_CONFIG" \
  --results-root "$MINIGRID_RESULTS" \
  --project-root /workspace \
  --expect-model-tags $MINIGRID_MODELS \
  --expect-cells "$MINIGRID_CELLS" \
  --output "$MINIGRID_OUTPUT"
