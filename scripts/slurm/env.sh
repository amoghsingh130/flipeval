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
# Gated repos (meta-llama/*) need an auth token inside the container. --cleanenv
# strips host vars and ~/.cache/huggingface is not among the binds, so the token
# is read from the host and forwarded explicitly. Conditional: jobs on ungated
# repos are unaffected if no token file exists. The token is never written to
# the repo or echoed -- only its presence is reported.
HF_TOKEN_FILE="${HF_TOKEN_PATH:-$HOME/.cache/huggingface/token}"
HF_TOKEN_STATUS=absent
if [ -r "$HF_TOKEN_FILE" ]; then
  APPTAINERENV_HF_TOKEN="$(tr -d '[:space:]' < "$HF_TOKEN_FILE")"
  export APPTAINERENV_HF_TOKEN
  HF_TOKEN_STATUS=present
fi

mkdir -p "$SCRATCH_DIR"/{hf_cache,calibration,work,logs,checkpoints}
cd "$PROJECT_DIR"

echo "== Job env =="
echo "host:        $(hostname)"
echo "project:     $PROJECT_DIR"
echo "scratch:     $SCRATCH_DIR"
echo "image:       $IMAGE"
echo "hf_home:     $HF_HOME"
echo "hf_token:    ${HF_TOKEN_STATUS}"

if [ ! -f "$IMAGE" ]; then
  echo "MISSING Apptainer image: $IMAGE" >&2
  exit 1
fi
