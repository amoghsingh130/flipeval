#!/bin/bash
#SBATCH --job-name=flipeval-calibration
#SBATCH --output=logs/calibration_%A_%a.out
#SBATCH --error=logs/calibration_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --array=0-2%1

# shellcheck source=scripts/slurm/env.sh
: "${PROJECT_DIR:?required (no default): the flipeval repository root this job acts on.
  Pass it BEFORE the script path: --export=ALL,PROJECT_DIR=\"$PWD\"  (incidents 21, 29)}"
source "$PROJECT_DIR/scripts/slurm/env.sh"
mkdir -p logs

SEED=$SLURM_ARRAY_TASK_ID

# Model/artifact identity is parameterized so one script serves every
# calibration cell. The defaults reproduce the registered Qwen2.5-1.5B
# invocation byte-for-byte, so existing runbook commands are unchanged; other
# models are selected by exporting these at submit time, e.g.
#   sbatch --array=0-4 --export=ALL,CALIB_MODEL_ID=meta-llama/Llama-3.2-3B-Instruct,...
# Values must match the pinned tag in configs/main_grid_manifest.yaml.
# REGISTERED VALUES (copy these; they are no longer inherited silently):
#   CALIB_MODEL_ID=Qwen/Qwen2.5-1.5B-Instruct
#   CALIB_MODEL_REVISION=989aa7980e4cf806f80c7fef2b1adb7bc71aa306
#   CALIB_ARTIFACT_PREFIX=qwen25-1p5b-c4-s
: "${CALIB_MODEL_ID:?required (no default: selects WHICH model the calibration set is built for)}"
: "${CALIB_MODEL_REVISION:?required (no default: a default pins a revision the operator did not choose)}"
: "${CALIB_ARTIFACT_PREFIX:?required (no default: names the OUTPUT calibration artifacts)}"

echo "calib model:  $CALIB_MODEL_ID @ $CALIB_MODEL_REVISION"
echo "calib artifact: /scratch/calibration/${CALIB_ARTIFACT_PREFIX}${SEED}.json"

srun apptainer exec --cleanenv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python /workspace/scripts/build_quantized.py \
  --model-id "$CALIB_MODEL_ID" \
  --model-revision "$CALIB_MODEL_REVISION" \
  --seed "$SEED" \
  --dataset c4 \
  --dataset-cache-dir /scratch/hf_cache/datasets \
  --calibration-artifact "/scratch/calibration/${CALIB_ARTIFACT_PREFIX}${SEED}.json" \
  --prepare-calibration-only \
  --trust-remote-code \
  ${VERIFY_ROW_COUNT:+--verify-stream-row-count}
