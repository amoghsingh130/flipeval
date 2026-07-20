#!/bin/bash
#SBATCH --job-name=flipeval-image
#SBATCH --output=/storage/scratch1/0/asingh3206/flipeval/logs/image_%j.out
#SBATCH --error=/storage/scratch1/0/asingh3206/flipeval/logs/image_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00

# Stage 1 container gate (docs/PACE_EXECUTION_PLAN_2026-07-15.md).
#
# Builds flipeval.sif from flipeval.def, runs the in-image test suite and the
# CPU smoke, then exports the PACE-resolved lock and image checksum per the
# runbook's "Build and fingerprint the image" section.
#
# Submit:  sbatch -A paceship-compressedlm -q embers scripts/slurm/build_image.sbatch
# CPU only; no GPU. Fits the embers 8h MaxWall with margin.
#
# Deliberately does NOT source env.sh: that helper exits 1 when $IMAGE is
# absent, which is precisely this job's starting state.

set -uo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}"
SCRATCH_DIR="${SCRATCH_DIR:-$HOME/scratch/flipeval}"
IMAGE="${IMAGE:-$SCRATCH_DIR/flipeval.sif}"

# Home is 20GB; the image and its build cache are far larger. Both must live on
# scratch or the build dies on quota.
export APPTAINER_CACHEDIR="$SCRATCH_DIR/work/apptainer_cache"
export APPTAINER_TMPDIR="$SCRATCH_DIR/work/apptainer_tmp"

# The smoke's writes all target /kaggle/working/results; bind it to scratch
# rather than modifying container/cpu_smoke.sh (the image is read-only at run).
KAGGLE_BIND="$SCRATCH_DIR/work/kaggle"

GATE_DIR="$PROJECT_DIR/results/pace_gate"
PYTEST_LOG="$GATE_DIR/in_image_pytest.log"
SMOKE_LOG="$GATE_DIR/cpu_smoke.log"
BUILD_LOG="$GATE_DIR/apptainer_build.log"

mkdir -p "$SCRATCH_DIR"/{hf_cache,calibration,checkpoints,work,logs} \
         "$APPTAINER_CACHEDIR" "$APPTAINER_TMPDIR" "$KAGGLE_BIND" "$GATE_DIR"

echo "=== Stage 1 container gate ==="
echo "host:       $(hostname)"
echo "date:       $(date -Is)"
echo "job:        ${SLURM_JOB_ID:-?}  qos: ${SLURM_JOB_QOS:-?}  partition: ${SLURM_JOB_PARTITION:-?}"
echo "project:    $PROJECT_DIR"
echo "scratch:    $SCRATCH_DIR"
echo "image:      $IMAGE"
echo "cachedir:   $APPTAINER_CACHEDIR"
echo "tmpdir:     $APPTAINER_TMPDIR"

if ! command -v apptainer >/dev/null 2>&1; then
  echo "FATAL: apptainer not found on $(hostname)" >&2
  exit 1
fi
echo "apptainer:  $(apptainer --version)"

cd "$PROJECT_DIR" || exit 1
echo "build context: $(pwd)  (flipeval.def '%files . /workspace' copies this tree)"

echo
echo "=== git provenance of the built source ==="
git rev-parse HEAD 2>&1
git status --porcelain 2>&1 | head -20
echo "(a dirty tree here means the image does not match a commit)"

# ---------------------------------------------------------------------------
# Build. Write to a temp path and move into place only on success: embers is
# preemptible, and a truncated $IMAGE would still satisfy env.sh's -f test and
# silently poison every later job.
# ---------------------------------------------------------------------------
TMP_IMAGE="$SCRATCH_DIR/work/flipeval.sif.building.$$"
rm -f "$TMP_IMAGE"

echo
echo "=== apptainer build (unprivileged; falls back to --fakeroot) ==="
BUILD_MODE="unprivileged"
if apptainer build "$TMP_IMAGE" flipeval.def 2>&1 | tee "$BUILD_LOG"; then
  echo "build succeeded (mode: unprivileged)"
else
  echo "unprivileged build failed; retrying with --fakeroot" >&2
  BUILD_MODE="fakeroot"
  rm -f "$TMP_IMAGE"
  if apptainer build --fakeroot "$TMP_IMAGE" flipeval.def 2>&1 | tee -a "$BUILD_LOG"; then
    echo "build succeeded (mode: --fakeroot)"
  else
    echo "FATAL: both unprivileged and --fakeroot builds failed. See $BUILD_LOG" >&2
    rm -f "$TMP_IMAGE"
    exit 1
  fi
fi

if [ ! -f "$TMP_IMAGE" ]; then
  echo "FATAL: build reported success but produced no image" >&2
  exit 1
fi
mv -f "$TMP_IMAGE" "$IMAGE" || exit 1
echo "image in place: $IMAGE ($(du -h "$IMAGE" | cut -f1), build mode: $BUILD_MODE)"

# ---------------------------------------------------------------------------
# Gate 1: in-image test suite.
# Ruled 2026-07-16: 54 passed, 0 skipped, 0 failed. Any skip fails the gate --
# a skip means a pinned dependency silently failed to import rather than being
# absent by design. (The stale 37 is corrected in the plan's dated erratum.)
# Raised to 55 on 2026-07-18: the torchvision==0.28.0 rebuild makes
# test_pinned_gptqmodel_exposes_expected_api import gptqmodel for real instead
# of skipping, so it now runs and passes.
# Raised to 58 on 2026-07-18 (cell 3): the gptqmodel revision-shim fix adds two
# revision-shim regression tests plus a real CPU shell-model construction gate
# (test_pinned_gptqmodel_builds_qwen2_shell_model_under_pinned_transformers).
# ---------------------------------------------------------------------------
echo
echo "=== Gate 1: in-image pytest (expect 66 passed, 0 skipped, 0 failed) ==="
apptainer exec --cleanenv --bind "$SCRATCH_DIR:/scratch" "$IMAGE" \
  python -m pytest -q 2>&1 | tee "$PYTEST_LOG"
PYTEST_RC=${PIPESTATUS[0]}

SUMMARY=$(grep -E '[0-9]+ (passed|failed|skipped|error)' "$PYTEST_LOG" | tail -1)
n_of() { echo "$SUMMARY" | grep -oE "[0-9]+ $1" | tail -1 | awk '{print $1}'; }
PASSED=$(n_of passed);  PASSED=${PASSED:-0}
SKIPPED=$(n_of skipped); SKIPPED=${SKIPPED:-0}
FAILED=$(n_of failed);  FAILED=${FAILED:-0}
ERRORS=$(n_of error);   ERRORS=${ERRORS:-0}

echo
echo "pytest exit=$PYTEST_RC summary='$SUMMARY'"
echo "parsed: passed=$PASSED skipped=$SKIPPED failed=$FAILED errors=$ERRORS"

GATE_FAIL=0
[ "$PYTEST_RC" -ne 0 ] && { echo "GATE FAIL: pytest exit $PYTEST_RC" >&2; GATE_FAIL=1; }
[ "$PASSED" != "66" ]  && { echo "GATE FAIL: expected 66 passed, got $PASSED" >&2; GATE_FAIL=1; }
[ "$SKIPPED" != "0" ]  && { echo "GATE FAIL: expected 0 skipped, got $SKIPPED (a skip = a pinned dep failed to import)" >&2; GATE_FAIL=1; }
[ "$FAILED" != "0" ]   && { echo "GATE FAIL: $FAILED failed" >&2; GATE_FAIL=1; }
[ "$ERRORS" != "0" ]   && { echo "GATE FAIL: $ERRORS errors" >&2; GATE_FAIL=1; }

# Grep-friendly evidence line. From Stage 1 onward the in-image suite is the
# authoritative gate for cluster-side source changes, so freeze-refresh commits
# cite this line and its log path rather than an unrunnable host result.
echo "IN_IMAGE_PYTEST_SUMMARY: passed=$PASSED skipped=$SKIPPED failed=$FAILED errors=$ERRORS rc=$PYTEST_RC job=${SLURM_JOB_ID:-?} log=$PYTEST_LOG"

if [ "$GATE_FAIL" -ne 0 ]; then
  echo "STOPPING: in-image test gate failed. Not running the smoke; not exporting the lock." >&2
  exit 1
fi
echo "Gate 1 PASS: 66 passed, 0 skipped, 0 failed"

# ---------------------------------------------------------------------------
# Gate 2: CPU smoke. Bound to scratch for /kaggle/working (image is read-only)
# and for the HF cache the tiny-gpt2 pull needs.
# ---------------------------------------------------------------------------
echo
echo "=== Gate 2: CPU smoke (outputs -> $KAGGLE_BIND/results) ==="
apptainer exec --cleanenv \
  --bind "$KAGGLE_BIND:/kaggle/working" \
  --bind "$SCRATCH_DIR:/scratch" \
  "$IMAGE" sh /workspace/container/cpu_smoke.sh 2>&1 | tee "$SMOKE_LOG"
SMOKE_RC=${PIPESTATUS[0]}

if [ "$SMOKE_RC" -ne 0 ]; then
  echo "GATE FAIL: cpu_smoke.sh exited $SMOKE_RC" >&2
  exit 1
fi

echo
echo "--- smoke outputs ---"
find "$KAGGLE_BIND/results" 2>&1 | head -30
for f in pair_summary.csv rank_instability.csv; do
  found=$(find "$KAGGLE_BIND/results" -name "$f" 2>/dev/null | head -1)
  if [ -n "$found" ]; then echo "OK      regenerated $f -> $found"
  else echo "GATE FAIL: smoke did not regenerate $f" >&2; GATE_FAIL=1; fi
done
[ "$GATE_FAIL" -ne 0 ] && { echo "STOPPING: smoke did not produce both analysis summaries." >&2; exit 1; }
echo "Gate 2 PASS: CPU smoke exit 0, both analysis summaries regenerated"

# ---------------------------------------------------------------------------
# Fingerprint: PACE lock kept SEPARATE from the Docker-mirror lock (runbook).
# ---------------------------------------------------------------------------
echo
echo "=== Export PACE lock and image checksum ==="
apptainer exec --cleanenv "$IMAGE" cat /opt/flipeval/environment.lock.txt \
  > "$PROJECT_DIR/container/environment.lock.pace.txt" || exit 1
sha256sum "$IMAGE" > "$PROJECT_DIR/container/flipeval.sif.sha256" || exit 1
echo "wrote container/environment.lock.pace.txt ($(wc -l < "$PROJECT_DIR/container/environment.lock.pace.txt") packages)"
echo "wrote container/flipeval.sif.sha256: $(cat "$PROJECT_DIR/container/flipeval.sif.sha256")"

# ---------------------------------------------------------------------------
# Pin comparison. Divergence on any of the six is a NO-GO per the plan: a
# divergent resolve is a new environment cell under the frozen backend rule.
# Reported, never auto-corrected.
# ---------------------------------------------------------------------------
echo
echo "=== Pin check vs container/environment.lock.resolved.txt (Docker mirror) ==="
PINS="torch transformers GPTQModel autoawq lm_eval datasets"
DIVERGED=0
for pkg in $PINS; do
  want=$(grep -iE "^${pkg}==" "$PROJECT_DIR/container/environment.lock.resolved.txt" | head -1)
  got=$(grep -iE "^${pkg}==" "$PROJECT_DIR/container/environment.lock.pace.txt" | head -1)
  if [ -z "$got" ]; then
    printf '  DIVERGENT %-14s docker=%-24s pace=<ABSENT>\n' "$pkg" "${want:-<absent>}"; DIVERGED=1
  elif [ "$(echo "$want" | tr '[:upper:]' '[:lower:]')" = "$(echo "$got" | tr '[:upper:]' '[:lower:]')" ]; then
    printf '  match     %-14s %s\n' "$pkg" "$got"
  else
    printf '  DIVERGENT %-14s docker=%-24s pace=%s\n' "$pkg" "${want:-<absent>}" "$got"; DIVERGED=1
  fi
done

echo
echo "--- full lock diff (informational; the six pins above are the gate) ---"
diff "$PROJECT_DIR/container/environment.lock.resolved.txt" \
     "$PROJECT_DIR/container/environment.lock.pace.txt" || true

echo
if [ "$DIVERGED" -ne 0 ]; then
  echo "NO-GO: PACE lock diverges from the pinned versions on at least one of the six." >&2
  echo "A divergent resolve is a new environment cell under the frozen backend rule." >&2
  echo "Do not fix forward. Stop and report." >&2
  exit 2
fi

echo "=== STAGE 1 GATE PASS ==="
echo "image:      $IMAGE"
echo "build mode: $BUILD_MODE"
echo "sha256:     $(cut -d' ' -f1 < "$PROJECT_DIR/container/flipeval.sif.sha256")"
echo "tests:      66 passed, 0 skipped, 0 failed"
echo "smoke:      exit 0, both analysis summaries regenerated"
echo "smoke out:  $KAGGLE_BIND/results"
echo "pins:       all six match the Docker-mirror lock"
echo "logs:       $GATE_DIR"
date -Is
