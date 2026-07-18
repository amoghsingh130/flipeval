#!/bin/bash
#SBATCH --job-name=flipeval-c4-mirror
#SBATCH --output=/storage/scratch1/0/asingh3206/flipeval/logs/mirror_c4_%j.out
#SBATCH --error=/storage/scratch1/0/asingh3206/flipeval/logs/mirror_c4_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=07:30:00

# Stage 1.5: mirror the pinned C4 `en` shards into the scratch HF hub cache and
# prove HF_HUB_OFFLINE=1 streaming resolution of the pinned revision.
#
# Submit:  sbatch -A paceship-compressedlm -q embers scripts/slurm/mirror_c4.sbatch
#          PROBE_ONLY=1 sbatch ... (stop after the mechanism probe)
#
# Wall is 7h30m to stay inside the embers 8h MaxWall. Downloads resume, so a
# preemption is recoverable. Per the 2026-07-16 ruling, fall back to inferno
# only if sustained throughput collapses below ~15 MB/s.
#
# ORDERING (deliberate): the ruling says "mirror, then prove offline streaming".
# This script proves the *mechanism* on two shards FIRST and exits before the
# ~305GB download if it fails. Rationale: build_quantized.py's stream factory
# calls load_dataset(..., streaming=True), which reads through HfFileSystem over
# HTTP, while snapshot_download fills the hub cache -- a different layer. If
# HF_HUB_OFFLINE=1 cannot resolve from the mirror, the mirror is inert for this
# code path and the download would be wasted. Same proof, cheaper ordering.

set -uo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}"
SCRATCH_DIR="${SCRATCH_DIR:-$HOME/scratch/flipeval}"
IMAGE="${IMAGE:-$SCRATCH_DIR/flipeval.sif}"
PROBE_ONLY="${PROBE_ONLY:-0}"
# REQUIRE_OFFLINE=1 (default): a failed offline-resolution probe stops the job
# before the large download. Set 0 to mirror anyway -- correct once the probe
# outcome is already known and the mirror is wanted for the shard-reading
# fallback verification path rather than for streaming.
REQUIRE_OFFLINE="${REQUIRE_OFFLINE:-1}"

# Pinned C4 revision. Authoritative source: scripts/build_quantized.py
# DATASET_SPECS["c4"] and configs/main_grid_manifest.yaml. Never abbreviate.
C4_REV="1588ec454efa1a09f29cd18ddd04fe05fc8653a2"

export APPTAINERENV_HF_HOME=/scratch/hf_cache
export APPTAINERENV_HF_DATASETS_CACHE=/scratch/hf_cache/datasets
export APPTAINERENV_TOKENIZERS_PARALLELISM=false

mkdir -p "$SCRATCH_DIR"/{hf_cache,logs,work}

echo "=== Stage 1.5: C4 mirror + offline streaming proof ==="
echo "host:      $(hostname)"
echo "date:      $(date -Is)"
echo "job:       ${SLURM_JOB_ID:-?}  qos: ${SLURM_JOB_QOS:-?}"
echo "image:     $IMAGE"
echo "c4 rev:    $C4_REV"
echo "probe only: $PROBE_ONLY"

if [ ! -f "$IMAGE" ]; then
  echo "FATAL: missing image $IMAGE -- run scripts/slurm/build_image.sbatch first" >&2
  exit 1
fi

df -h "$SCRATCH_DIR" | tail -1

# ---------------------------------------------------------------------------
# Phase A: partial mirror (two shards + repo metadata).
# ---------------------------------------------------------------------------
echo
echo "=== Phase A: partial mirror (2 train shards + metadata) ==="
A_START=$(date +%s)
apptainer exec --cleanenv --bind "$SCRATCH_DIR:/scratch" "$IMAGE" python - <<PY
import sys
from huggingface_hub import snapshot_download
try:
    p = snapshot_download(
        repo_id="allenai/c4",
        repo_type="dataset",
        revision="$C4_REV",
        allow_patterns=[
            "README.md",
            "en/c4-train.00000-of-01024.json.gz",
            "en/c4-train.00001-of-01024.json.gz",
        ],
        max_workers=8,
    )
    print("PARTIAL_MIRROR_OK", p)
except Exception as exc:
    print("PARTIAL_MIRROR_FAIL", type(exc).__name__, exc)
    import traceback; traceback.print_exc()
    sys.exit(3)
PY
A_RC=$?
A_END=$(date +%s)
echo "phase A: rc=$A_RC elapsed=$((A_END - A_START))s"
[ "$A_RC" -ne 0 ] && { echo "FATAL: partial mirror failed; not proceeding." >&2; exit 1; }

# ---------------------------------------------------------------------------
# Phase B: the actual question -- does HF_HUB_OFFLINE=1 streaming resolve from
# the mirror? Streaming is lazy and opens shard 0 first, so two shards prove the
# resolution path even though the split has 1024.
# ---------------------------------------------------------------------------
echo
echo "=== Phase B: HF_HUB_OFFLINE=1 streaming resolution probe ==="
APPTAINERENV_HF_HUB_OFFLINE=1 apptainer exec --cleanenv --bind "$SCRATCH_DIR:/scratch" "$IMAGE" python - <<PY
import os, sys, traceback
print("HF_HUB_OFFLINE =", os.environ.get("HF_HUB_OFFLINE"))
from datasets import load_dataset
try:
    ds = load_dataset(
        "allenai/c4", "en",
        split="train",
        revision="$C4_REV",
        streaming=True,
        cache_dir="/scratch/hf_cache/datasets",
    )
    it = iter(ds)
    rows = [next(it) for _ in range(3)]
    print("OFFLINE_STREAM_OK rows=%d keys=%s first_text_len=%d"
          % (len(rows), sorted(rows[0].keys()), len(rows[0]["text"])))
except Exception as exc:
    print("OFFLINE_STREAM_FAIL", type(exc).__name__, exc)
    traceback.print_exc()
    sys.exit(3)
PY
B_RC=$?
echo "phase B: rc=$B_RC"

if [ "$B_RC" -ne 0 ] && [ "$REQUIRE_OFFLINE" = "1" ]; then
  echo
  echo "=== STAGE 1.5 RESULT: offline streaming does NOT resolve from the mirror ===" >&2
  echo "The mirror is inert for build_quantized.py's streaming code path." >&2
  echo "Per the 2026-07-16 ruling: without the mirror, Stage 2 verification" >&2
  echo "splits into its own job and execution STOPS for reassessment --" >&2
  echo "two network scans in one job is not permitted." >&2
  echo "Not downloading ~305GB. Stopping for human review." >&2
  exit 3
fi

if [ "$B_RC" -ne 0 ]; then
  # Measured 2026-07-16 (job 11223841): load_dataset must reach the Hub to
  # RESOLVE allenai/c4 before streaming opens a byte, and HF_HUB_OFFLINE=1
  # makes that resolution raise rather than fall back to the cached snapshot.
  # Ruled 2026-07-17: mirror anyway. It is ~31min at the measured link rate and
  # it enables the fallback parallel line-count verification path, which reads
  # the shards directly and needs no Hub resolution.
  echo "Phase B FAILED but REQUIRE_OFFLINE=0 -- continuing to mirror as ruled."
  echo "The mirror serves the shard-reading fallback path, not the streaming path."
else
  echo "Phase B PASS: the mirror serves the streaming path offline."
fi

if [ "$PROBE_ONLY" = "1" ]; then
  echo "PROBE_ONLY=1 -- stopping before the full mirror as requested."
  exit 0
fi

# ---------------------------------------------------------------------------
# Phase C: full mirror. Resumable; validation shards included as cheap
# insurance against config resolution wanting the full file list.
# ---------------------------------------------------------------------------
echo
echo "=== Phase C: full mirror of the pinned C4 en split ==="
BEFORE_KB=$(du -sk "$SCRATCH_DIR/hf_cache" 2>/dev/null | cut -f1)
C_START=$(date +%s)
apptainer exec --cleanenv --bind "$SCRATCH_DIR:/scratch" "$IMAGE" python - <<PY
import sys
from huggingface_hub import snapshot_download
try:
    p = snapshot_download(
        repo_id="allenai/c4",
        repo_type="dataset",
        revision="$C4_REV",
        allow_patterns=[
            "README.md",
            "en/c4-train.*.json.gz",
            "en/c4-validation.*.json.gz",
        ],
        max_workers=8,
    )
    print("FULL_MIRROR_OK", p)
except Exception as exc:
    print("FULL_MIRROR_FAIL", type(exc).__name__, exc)
    import traceback; traceback.print_exc()
    sys.exit(3)
PY
C_RC=$?
C_END=$(date +%s)
AFTER_KB=$(du -sk "$SCRATCH_DIR/hf_cache" 2>/dev/null | cut -f1)

ELAPSED=$((C_END - C_START))
DELTA_KB=$((AFTER_KB - BEFORE_KB))
echo
echo "phase C: rc=$C_RC elapsed=${ELAPSED}s downloaded_delta=$((DELTA_KB / 1024))MB total_cache=$((AFTER_KB / 1024))MB"
if [ "$ELAPSED" -gt 0 ]; then
  echo "MIRROR_THROUGHPUT_MB_S: $((DELTA_KB / 1024 / ELAPSED))"
  echo "(ruling: fall back to inferno only if sustained throughput < ~15 MB/s)"
fi
[ "$C_RC" -ne 0 ] && { echo "FATAL: full mirror failed (resumable -- resubmit to continue)." >&2; exit 1; }

SHARDS=$(find "$SCRATCH_DIR/hf_cache" -name "c4-train.*.json.gz" 2>/dev/null | wc -l)
echo "train shards present: $SHARDS (expect 1024)"

# ---------------------------------------------------------------------------
# Phase D: re-prove offline streaming against the COMPLETE mirror. Phase B used
# two shards; this is the proof Stage 2 actually depends on.
# ---------------------------------------------------------------------------
echo
echo "=== Phase D: offline streaming proof against the complete mirror ==="
if [ "$B_RC" -ne 0 ]; then
  echo "SKIP: Phase B already established that offline resolution fails."
  echo "A complete mirror does not change that -- the failure is in Hub"
  echo "resolution, not in file availability. Stage 2 transport stays networked."
  echo
  echo "=== STAGE 1.5 COMPLETE (mirror only; offline streaming unavailable) ==="
  echo "mirror:  $SCRATCH_DIR/hf_cache ($((AFTER_KB / 1024 / 1024))GB, $SHARDS train shards)"
  echo "use:     shard-reading fallback verification path; NOT the streaming path."
  date -Is
  exit 0
fi
APPTAINERENV_HF_HUB_OFFLINE=1 apptainer exec --cleanenv --bind "$SCRATCH_DIR:/scratch" "$IMAGE" python - <<PY
import sys, time, traceback
from datasets import load_dataset
try:
    ds = load_dataset(
        "allenai/c4", "en",
        split="train",
        revision="$C4_REV",
        streaming=True,
        cache_dir="/scratch/hf_cache/datasets",
    )
    t0 = time.time()
    n = 0
    for _ in ds:
        n += 1
        if n >= 200000:
            break
    dt = time.time() - t0
    print("OFFLINE_STREAM_FULL_OK rows=%d elapsed=%.1fs rows_per_s=%.0f" % (n, dt, n / dt))
    # Extrapolation to one full pass over the registered 364,868,892 rows. This
    # is the number that decides Stage 2 tractability -- the scan is gunzip +
    # JSON parse bound, not network bound.
    print("PROJECTED_FULL_PASS_HOURS: %.2f" % (364868892 / (n / dt) / 3600.0))
except Exception as exc:
    print("OFFLINE_STREAM_FULL_FAIL", type(exc).__name__, exc)
    traceback.print_exc()
    sys.exit(3)
PY
D_RC=$?
echo "phase D: rc=$D_RC"
[ "$D_RC" -ne 0 ] && { echo "FATAL: offline streaming failed against the complete mirror." >&2; exit 1; }

echo
echo "=== STAGE 1.5 COMPLETE ==="
echo "mirror:     $SCRATCH_DIR/hf_cache ($((AFTER_KB / 1024 / 1024))GB, $SHARDS train shards)"
echo "offline:    HF_HUB_OFFLINE=1 streaming resolves the pinned revision"
echo "Stage 2 may run against the mirror with verify+create in one 48h inferno job."
date -Is
