#!/bin/bash
#SBATCH --job-name=flipeval-packaging-tests
#SBATCH --output=logs/packaging_tests_%j.out
#SBATCH --error=logs/packaging_tests_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00

# CPU-only test run for the unfingerprinted packaging/ layer. Uses the pinned
# image, like every other gate on this project -- the login node has python
# 3.9.21 and no pytest/numpy/scipy, and standing policy forbids creating a
# second host environment to work around that.
#
# Runs BOTH suites and reports each separately:
#   1. the registered in-image suite, which must stay at its recorded count
#   2. the new packaging suite, which lives outside `testpaths` and so is
#      invisible to (1) by construction -- this run proves that
#
# TWO THINGS THIS SCRIPT GETS RIGHT, both learned from job 11359430 failing:
#
# * `$SCRATCH_DIR:/scratch` MUST be bound. env.sh exports
#   APPTAINERENV_HF_HOME=/scratch/hf_cache, and importing gptqmodel pulls in
#   tokenicer, which mkdirs that path at import time. Without the bind,
#   /scratch is read-only inside the container and two registered tests fail
#   with PermissionError -- a harness defect that reads exactly like a code
#   regression. The mini-grid sbatch binds both; so must this.
#
# * env.sh sets `set -e`, so a failing pytest aborts the whole script and the
#   later suites never run. Exit codes are captured explicitly instead.

# shellcheck source=scripts/slurm/env.sh
source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
mkdir -p logs

export APPTAINERENV_PYTHONPATH=/workspace:/workspace/packaging
BINDS="$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch"

set +e

echo "=== 1. registered suite (gate; expectation lives in CLAUDE.md) ==="
apptainer exec --cleanenv --pwd /workspace --bind "$BINDS" \
  "$IMAGE" python -m pytest -q
REGISTERED=$?
echo "REGISTERED_SUITE_EXIT: $REGISTERED"

echo
echo "=== 2. packaging suite (new, outside the fingerprint) ==="
apptainer exec --cleanenv --pwd /workspace/packaging --bind "$BINDS" \
  "$IMAGE" python -m pytest -q tests
PACKAGING=$?
echo "PACKAGING_SUITE_EXIT: $PACKAGING"

echo
echo "=== 3. CLI smoke test on the fixtures ==="
apptainer exec --cleanenv --pwd /workspace/packaging --bind "$BINDS" \
  "$IMAGE" python -m flipeval_cli compare \
  tests/fixtures/degraded_baseline.jsonl \
  tests/fixtures/degraded_candidate.jsonl \
  --margin 0.02
echo "SMOKE_EXIT: $?"

echo
echo "=== 4. verdict sweep ==="
for stem in equivalent degraded improved underpowered; do
  apptainer exec --cleanenv --pwd /workspace/packaging --bind "$BINDS" \
    "$IMAGE" python -m flipeval_cli compare \
    "tests/fixtures/${stem}_baseline.jsonl" \
    "tests/fixtures/${stem}_candidate.jsonl" \
    --margin 0.02 | grep -E "^VERDICT|^  items|net delta"
  echo "  [${stem}] exit=$?"
done

echo
echo "=== 5. mismatch case (must fail with exit 2) ==="
apptainer exec --cleanenv --pwd /workspace/packaging --bind "$BINDS" \
  "$IMAGE" python -m flipeval_cli compare \
  tests/fixtures/mismatch_baseline.jsonl \
  tests/fixtures/mismatch_candidate.jsonl
echo "MISMATCH_EXIT: $? (expected 2)"

echo
echo "OVERALL: registered=$REGISTERED packaging=$PACKAGING"
