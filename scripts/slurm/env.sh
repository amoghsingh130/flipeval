#!/bin/bash
# Shared paths for the pinned Apptainer-based PACE jobs.
set -euo pipefail

export PROJECT_DIR="${PROJECT_DIR:-$HOME/p-<allocation>/flipeval}"
export SCRATCH_DIR="${SCRATCH_DIR:-$HOME/scratch/flipeval}"
export IMAGE="${IMAGE:-$SCRATCH_DIR/flipeval.sif}"
export HF_HOME="${HF_HOME:-$SCRATCH_DIR/hf_cache}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-$HF_HOME/datasets}"
export CALIBRATION_DIR="${CALIBRATION_DIR:-$SCRATCH_DIR/calibration}"
export TOKENIZERS_PARALLELISM=false
# The host scratch root is mounted at /scratch in every job. APPTAINERENV_*
# prevents the host's absolute path from leaking into the container namespace.
export APPTAINERENV_HF_HOME=/scratch/hf_cache
export APPTAINERENV_HF_DATASETS_CACHE=/scratch/hf_cache/datasets
export APPTAINERENV_TOKENIZERS_PARALLELISM=false

mkdir -p "$SCRATCH_DIR"/{hf_cache,calibration,work,logs,checkpoints}
cd "$PROJECT_DIR"

echo "== Job env =="
echo "host:        $(hostname)"
echo "project:     $PROJECT_DIR"
echo "scratch:     $SCRATCH_DIR"
echo "image:       $IMAGE"
echo "hf_home:     $HF_HOME"

if [ ! -f "$IMAGE" ]; then
  echo "MISSING Apptainer image: $IMAGE" >&2
  exit 1
fi
