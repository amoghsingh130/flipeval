#!/bin/bash
# Shared paths for the pinned Apptainer-based PACE jobs.
set -euo pipefail

# ---------------------------------------------------------------------------
# PROJECT_DIR IS REQUIRED AND HAS NO DEFAULT (2026-08-07, incident 29).
#
# This file used to read `PROJECT_DIR="${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}"`,
# so every job sourcing it silently acted on THAT checkout when the variable was
# unset. On 2026-08-07 the in-image test gate certified the wrong tree and exited
# 0 because of it. The default is removed here, at the shared source, rather than
# shadowed in one caller.
#
# There is deliberately NO repository auto-discovery to replace it -- no
# `git rev-parse --show-toplevel`, no `$(dirname "$0")/../..`. Discovery is the
# same defect wearing a different hat: it silently picks a tree instead of
# failing when nobody said which one.
# ---------------------------------------------------------------------------
env_die() { echo "env.sh: FATAL: $*" >&2; exit 2; }

[ -n "${PROJECT_DIR:-}" ] || env_die "PROJECT_DIR is not set. It is REQUIRED and has no default.
  Pass it explicitly, BEFORE the script path (options after the path are parsed
  as script arguments -- incident 21):
    sbatch -A \"\$ACCOUNT\" -q inferno --export=ALL,PROJECT_DIR=\"\$PWD\" scripts/slurm/<job>.sbatch"
[ -d "$PROJECT_DIR" ] || env_die "PROJECT_DIR=$PROJECT_DIR does not exist or is not a directory"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)" || env_die "cannot resolve PROJECT_DIR"
for _marker in pyproject.toml tests flipeval scripts/slurm/env.sh; do
  [ -e "$PROJECT_DIR/$_marker" ] \
    || env_die "PROJECT_DIR=$PROJECT_DIR is not a flipeval repository root: missing '$_marker'"
done
unset _marker
export PROJECT_DIR

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

# ---------------------------------------------------------------------------
# IMAGE selects the ENVIRONMENT CELL, so it is a source selector under the
# no-defaults rule. It keeps a default PATH on purpose: requiring the operator
# to type a path proves only that a file exists there, not that it is the
# pinned image. What actually closes the hazard is verifying the digest, so
# that is what is done -- unconditionally, with no opt-out flag, because an
# opt-out is a default by another name.
#
# Fails closed in both directions: a missing digest record is a failure, not a
# skip. A rebuild re-resolves the pinned environment and so is a different
# cell; if that is intended, rebuild via build_image.sbatch (which does not
# source this file) and update container/flipeval.sif.sha256 deliberately.
# ---------------------------------------------------------------------------
IMAGE_SHA_FILE="$PROJECT_DIR/container/flipeval.sif.sha256"
[ -r "$IMAGE_SHA_FILE" ] \
  || env_die "no recorded image digest at $IMAGE_SHA_FILE -- refusing to run against an unverified environment cell"
IMAGE_SHA_EXPECTED="$(awk '{print $1}' "$IMAGE_SHA_FILE" | head -1)"
[ -n "$IMAGE_SHA_EXPECTED" ] || env_die "recorded image digest is empty at $IMAGE_SHA_FILE"
IMAGE_SHA_ACTUAL="$(sha256sum "$IMAGE" | awk '{print $1}')"
if [ "$IMAGE_SHA_ACTUAL" != "$IMAGE_SHA_EXPECTED" ]; then
  env_die "image digest mismatch -- this is NOT the pinned environment cell
  image:    $IMAGE
  expected: $IMAGE_SHA_EXPECTED
  actual:   $IMAGE_SHA_ACTUAL"
fi
echo "image_sha:   ${IMAGE_SHA_ACTUAL:0:8}… verified against container/flipeval.sif.sha256"
