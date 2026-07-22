#!/bin/bash
#SBATCH --job-name=flipeval-build
#SBATCH --output=logs/build_%A_%a.out
#SBATCH --error=logs/build_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=06:00:00
#SBATCH --array=0-5

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs outputs/quantized

# Model/artifact identity is parameterized so one script serves every build
# cell. The defaults reproduce the registered Qwen2.5-1.5B 3-seed invocation
# byte-for-byte -- including the array index map -- so existing runbook commands
# are unchanged. The mini-grid overrides these at submit time, e.g.
#   sbatch --array=0-9 --export=ALL,BUILD_SEEDS_PER_METHOD=5,\
#     BUILD_MODEL_ID=meta-llama/Llama-3.2-3B-Instruct,BUILD_TAG=llama32-3b,...
# Values must match the pinned tag in configs/main_grid_manifest.yaml.
BUILD_MODEL_ID="${BUILD_MODEL_ID:-Qwen/Qwen2.5-1.5B-Instruct}"
BUILD_MODEL_REVISION="${BUILD_MODEL_REVISION:-989aa7980e4cf806f80c7fef2b1adb7bc71aa306}"
BUILD_TAG="${BUILD_TAG:-qwen25-1p5b}"
# Seeds per method sets the array index map: index = method*SEEDS + seed. It
# defaults to 3, the bridge's layout, so a bare resubmission of an existing
# array element still builds exactly what it built before.
BUILD_SEEDS_PER_METHOD="${BUILD_SEEDS_PER_METHOD:-3}"

MODEL_ID="$BUILD_MODEL_ID"
MODEL_REVISION="$BUILD_MODEL_REVISION"
METHODS=(gptq awq)
M=$((SLURM_ARRAY_TASK_ID / BUILD_SEEDS_PER_METHOD))
SEED=$((SLURM_ARRAY_TASK_ID % BUILD_SEEDS_PER_METHOD))
METHOD=${METHODS[$M]}
ARTIFACT_NAME="${BUILD_TAG}-c4-s${SEED}.json"
ARTIFACT="/scratch/calibration/${ARTIFACT_NAME}"
OUT="/workspace/outputs/quantized/${BUILD_TAG}-${METHOD}4-seed${SEED}"

echo "build model:    $MODEL_ID @ $MODEL_REVISION"
echo "build method:   $METHOD seed $SEED -> $OUT"

if [ ! -f "$CALIBRATION_DIR/$ARTIFACT_NAME" ]; then
  echo "MISSING paired calibration artifact for seed $SEED ($ARTIFACT_NAME); run prepare_calibration.sbatch" >&2
  exit 1
fi

# env.sh sets `set -e`, which would abort this script the instant the build
# failed -- before the receipt was written. A failed build's resource profile is
# precisely what a diagnosis needs, so errexit is lifted around the build only.
set +e
srun apptainer exec --cleanenv --nv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/build_quantized.py \
  --model-id "$MODEL_ID" \
  --model-revision "$MODEL_REVISION" \
  --method "$METHOD" \
  --seed "$SEED" \
  --bits 4 \
  --dataset c4 \
  --calibration-artifact "$ARTIFACT" \
  --output-dir "$OUT" \
  --trust-remote-code
BUILD_RC=$?
set -e

# Operational receipt, written HERE rather than reconstructed later
# (ruled 2026-07-21; see docs/CALIBRATION_RECEIPTS_RECONSTRUCTION_2026-07-21.md
# for what reconstruction cost). It goes to results/, which is durable project
# storage, not the 60-day-purge scratch. Written on failure too: a failed build's
# resource profile is exactly what a diagnosis needs.
CKPT_HOST="$PROJECT_DIR/outputs/quantized/${BUILD_TAG}-${METHOD}4-seed${SEED}"
ARTIFACT_SHA="absent"
if [ -r "$CALIBRATION_DIR/$ARTIFACT_NAME" ]; then
  ARTIFACT_SHA="$(sha256sum "$CALIBRATION_DIR/$ARTIFACT_NAME" | awk '{print $1}')"
fi
CKPT_BYTES="0"
if [ -d "$CKPT_HOST" ]; then
  CKPT_BYTES="$(du -sb "$CKPT_HOST" 2>/dev/null | awk '{print $1}' || echo 0)"
fi
bash "$PROJECT_DIR/scripts/slurm/write_receipt.sh" \
  build "$PROJECT_DIR/results/receipts/build-${BUILD_TAG}-${METHOD}4-seed${SEED}.json" \
  "model_id=$MODEL_ID" \
  "model_revision=$MODEL_REVISION" \
  "method=$METHOD" \
  "seed=$SEED" \
  "bits=4" \
  "calibration_artifact=$ARTIFACT_NAME" \
  "calibration_artifact_sha256=$ARTIFACT_SHA" \
  "output_dir=$CKPT_HOST" \
  "output_bytes=$CKPT_BYTES" \
  "build_exit_code=$BUILD_RC" || echo "WARNING: receipt write failed" >&2

echo "Done: $OUT (build rc=$BUILD_RC)"
exit "$BUILD_RC"
