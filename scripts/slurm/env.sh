#!/bin/bash
# Shared paths for the pinned Apptainer-based PACE jobs.
set -euo pipefail

export PROJECT_DIR="${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}"
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
# HF Hub download/metadata read timeouts (huggingface_hub 1.24.0 defaults: 10s
# each) raised to 60s so intermittent Hub 503s / slow shard reads while streaming
# C4 on compute nodes do not trip 'read operation timed out'. Only these two
# timeouts are env-settable in the pinned stack; the datasets 5.0.0 streaming
# retry counts (20x outer, with 503-specific and rate-limit backoff) are
# hardcoded and already generous, so no code change is made. --cleanenv strips
# bare host vars, so these must use the APPTAINERENV_ prefix to reach the image.
export APPTAINERENV_HF_HUB_DOWNLOAD_TIMEOUT=60
export APPTAINERENV_HF_HUB_ETAG_TIMEOUT=60

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
