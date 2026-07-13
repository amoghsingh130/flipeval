#!/bin/bash
# Shared environment for PACE-ICE GPU jobs. Sourced by the sbatch scripts.
# Edit these once; both build + run jobs use them.

set -euo pipefail

# --- Project location (repo root on ICE) -----------------------------------
export PROJECT_DIR="${PROJECT_DIR:-$HOME/scratch/Critiquing-Ranking-Quantized-LLMs}"

# --- Caches on scratch (home has a small quota; models are large) ----------
export SCRATCH_DIR="${SCRATCH_DIR:-$HOME/scratch}"
export HF_HOME="${HF_HOME:-$SCRATCH_DIR/hf_cache}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-$SCRATCH_DIR/hf_cache/datasets}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$SCRATCH_DIR/pip_cache}"
export TOKENIZERS_PARALLELISM=false
mkdir -p "$HF_HOME" "$HF_DATASETS_CACHE" "$PIP_CACHE_DIR"

# --- Modules + conda env ----------------------------------------------------
# PACE provides anaconda3 as a module. Create the env once (see README), then
# these lines activate it inside the job.
module purge
module load anaconda3
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate crql

cd "$PROJECT_DIR"

echo "== Job env =="
echo "host:        $(hostname)"
echo "project:     $PROJECT_DIR"
echo "hf_home:     $HF_HOME"
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no-gpu')"
