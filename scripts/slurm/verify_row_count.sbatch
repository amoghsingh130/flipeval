#!/bin/bash
#SBATCH --job-name=flipeval-verify-rows
#SBATCH --output=/storage/scratch1/0/asingh3206/flipeval/logs/verify_rows_%j.out
#SBATCH --error=/storage/scratch1/0/asingh3206/flipeval/logs/verify_rows_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00

# Stage 2, part 1 of 2: the registered stream row-count preflight, as its OWN
# job (ruled 2026-07-16/17: never two network scans in one job).
#
# Submit:  sbatch -A paceship-compressedlm -q inferno scripts/slurm/verify_row_count.sbatch
# inferno, not embers: the projected 7.2h pass exceeds the embers 8h MaxWall
# once any margin is allowed.
#
# WHY NOT prepare_calibration.sbatch WITH VERIFY_ROW_COUNT=1:
# build_quantized.py main() runs verify_stream_row_count and then falls THROUGH
# into load_or_create_calibration_artifact (scripts/build_quantized.py:116-137).
# That is verify + create = two full network scans in one job, which the ruling
# forbids. This job calls the module's own registered verification function
# directly, so the check is byte-for-byte the registered one and no fingerprinted
# Python is edited. Artifact creation runs separately afterwards.
#
# The stream factory is wrapped in an instrumenting generator that yields every
# row unchanged, so verify_stream_row_count counts exactly the registered rows
# while the plan's required checkpoints (1M/10M/50M/100M/200M) are logged and
# the pre-committed abort criteria are enforced in-flight.

set -uo pipefail

: "${PROJECT_DIR:?required (no default): the flipeval repository root this job acts on.
  Pass it BEFORE the script path: --export=ALL,PROJECT_DIR=\"$PWD\"  (incidents 21, 29)}"
[ -d "$PROJECT_DIR" ] || { echo "FATAL: PROJECT_DIR=$PROJECT_DIR does not exist" >&2; exit 2; }
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"
for _m in pyproject.toml tests flipeval scripts/slurm/env.sh; do
  [ -e "$PROJECT_DIR/$_m" ] || { echo "FATAL: PROJECT_DIR=$PROJECT_DIR is not a flipeval repository root: missing '$_m'" >&2; exit 2; }
done; unset _m
SCRATCH_DIR="${SCRATCH_DIR:-$HOME/scratch/flipeval}"
IMAGE="${IMAGE:-$SCRATCH_DIR/flipeval.sif}"

export APPTAINERENV_HF_HOME=/scratch/hf_cache
export APPTAINERENV_HF_DATASETS_CACHE=/scratch/hf_cache/datasets
export APPTAINERENV_TOKENIZERS_PARALLELISM=false

mkdir -p "$SCRATCH_DIR"/{hf_cache,logs} "$PROJECT_DIR/results/pace_gate"

echo "=== Stage 2 part 1: registered stream row-count verification ==="
echo "host: $(hostname)  date: $(date -Is)  job: ${SLURM_JOB_ID:-?}  qos: ${SLURM_JOB_QOS:-?}"

if [ ! -f "$IMAGE" ]; then
  echo "FATAL: missing image $IMAGE" >&2
  exit 1
fi

srun apptainer exec --cleanenv --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" "$IMAGE" \
  python - <<'PY'
import resource
import sys
import time

sys.path.insert(0, "/workspace/scripts")
import build_quantized as bq          # noqa: E402  (registered module, imported not edited)
from datasets import load_dataset     # noqa: E402

# Pre-committed abort criteria (plan Stage 2), applied PER PASS including this one.
ABORT_PROJECTED_HOURS = 24.0
ABORT_RSS_GB = 48.0
ABORT_VOLUME_TB = 1.5
CHECKPOINTS = [1_000_000, 10_000_000, 50_000_000, 100_000_000, 200_000_000, 300_000_000]
# Measured 2026-07-17 (job 11225540): 896.1 compressed bytes/row on shard 0.
BYTES_PER_ROW = 896.1

spec = bq.DATASET_SPECS["c4"]
print("dataset:  %s (%s/%s)" % (spec.repo_id, spec.config, spec.split), flush=True)
print("revision: %s" % spec.revision, flush=True)
print("registered row_count: %d" % spec.row_count, flush=True)

state = {"aborted": None}
t0 = time.time()


def rss_gb():
    # ru_maxrss is KB on Linux.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 * 1024.0)


def report(n, tag):
    dt = time.time() - t0
    rate = n / dt if dt > 0 else 0.0
    projected = (spec.row_count / rate / 3600.0) if rate > 0 else float("inf")
    volume_tb = n * BYTES_PER_ROW / 1e12
    print(
        "CHECKPOINT rows=%d tag=%s elapsed=%.1fs rows_per_s=%.0f "
        "projected_full_pass_h=%.2f peak_rss_gb=%.2f est_volume_tb=%.3f"
        % (n, tag, dt, rate, projected, rss_gb(), volume_tb),
        flush=True,
    )
    return projected, rss_gb(), volume_tb


def instrumented_factory():
    """Yield the registered stream unchanged, logging checkpoints and enforcing aborts."""
    inner = bq.make_stream_factory(load_dataset, spec, "/scratch/hf_cache/datasets")()
    for i, row in enumerate(inner, start=1):
        if i in CHECKPOINTS or i % 50_000_000 == 0:
            projected, rss, volume_tb = report(i, "progress")
            # The 24h projection criterion is evaluated at the 50M checkpoint.
            if i >= 50_000_000 and projected > ABORT_PROJECTED_HOURS:
                state["aborted"] = (
                    "projected single pass %.2fh > %.1fh at row %d"
                    % (projected, ABORT_PROJECTED_HOURS, i)
                )
                return
            if rss > ABORT_RSS_GB:
                state["aborted"] = "peak RSS %.2fGB > %.1fGB at row %d" % (rss, ABORT_RSS_GB, i)
                return
            if volume_tb > ABORT_VOLUME_TB:
                state["aborted"] = (
                    "estimated volume %.3fTB > %.1fTB at row %d" % (volume_tb, ABORT_VOLUME_TB, i)
                )
                return
        yield row


try:
    counted = bq.verify_stream_row_count(instrumented_factory, spec)
except bq.CalibrationArtifactError as exc:
    if state["aborted"]:
        print("ABORT_CRITERION_TRIPPED: %s" % state["aborted"], flush=True)
        print("The truncated count below is a consequence of the abort, not a real "
              "row-count mismatch. Do not read it as evidence about row_count.", flush=True)
        print("DETAIL: %s" % exc, flush=True)
        sys.exit(4)
    print("VERIFY_FAILED_CLOSED: %s" % exc, flush=True)
    print("The registered permutation would cover the wrong sampling universe. "
          "This is a hard stop, not a tuning opportunity.", flush=True)
    sys.exit(5)
except Exception as exc:  # noqa: BLE001
    print("VERIFY_ERROR %s: %s" % (type(exc).__name__, exc), flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(3)

report(counted, "final")
print("VERIFIED_ROW_COUNT=%d MATCHES_REGISTERED=%s"
      % (counted, counted == spec.row_count), flush=True)
print("VERIFY_PASS: the pinned stream yields exactly the registered row_count.", flush=True)
PY
RC=$?

echo
echo "verify job rc=$RC"
case "$RC" in
  0) echo "=== STAGE 2 PART 1 PASS ===";
     echo "Next: artifact creation as a SEPARATE job (no VERIFY_ROW_COUNT).";;
  4) echo "=== ABORTED on a pre-committed criterion -- STOP and report ===" >&2;;
  5) echo "=== FAILED CLOSED: row_count mismatch -- STOP, do not tune ===" >&2;;
  *) echo "=== ERROR -- STOP and report ===" >&2;;
esac
date -Is
exit "$RC"
