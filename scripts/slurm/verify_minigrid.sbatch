#!/bin/bash
#SBATCH --job-name=flipeval-verify-minigrid
#SBATCH --output=logs/verify_minigrid_%j.out
#SBATCH --error=logs/verify_minigrid_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00

# Fail-closed validation over the COMPLETE 44-JSONL expected set. Run this only
# once every cell exists; it is the Stage 6 -> Stage 7 gate, and a nonzero exit
# means stop. Reading its output is the only inspection of mini-grid results
# permitted before the grid is complete.

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

apptainer exec --cleanenv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/verify_minigrid.py \
  --config /workspace/configs/pace_minigrid_h3.yaml \
  --results-root /workspace/results \
  --project-root /workspace
