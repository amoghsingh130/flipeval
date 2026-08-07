#!/bin/bash
#SBATCH --job-name=flipeval-tests
#SBATCH --output=logs/run_tests_%j.out
#SBATCH --error=logs/run_tests_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00

# The in-image pytest gate, run against the ALREADY-BUILT image.
#
# CLAUDE.md makes the in-image suite authoritative for any cluster-side source
# change, but until now the only script that ran it was build_image.sbatch. That
# made the gate cost an image rebuild, which is both slow and wrong: rebuilding
# to test a Python change re-resolves the pinned environment and so tests a
# different environment cell than the one the change will actually run in.
# This script runs the suite in the pinned image exactly as it stands.
#
# The suite is read-only with respect to results/: it reads the frozen claim
# table and the atlas summary and asserts over computed rows in memory. It does
# not write any grid output, so the sealed confirmatory directories are not at
# risk from it.
#
# EXPECTED: the count recorded in CLAUDE.md ("Verification gates"). ANY SKIP IS
# A GATE FAILURE -- a skip means a pinned dependency silently failed to import
# rather than being absent by design. Whichever session adds tests updates that
# count in the same commit; a stale expectation is a gate that cannot fail.
#
#   PROJECT_DIR   REQUIRED. The repository root to test. NO DEFAULT.
#   PYTEST_ARGS   optional extra pytest arguments (default: none)
#
# Example:
#   sbatch -A "$ACCOUNT" -q inferno -p cpu-small \
#          --export=ALL,PROJECT_DIR="$PWD" \
#          scripts/slurm/run_tests.sbatch
#
# ---------------------------------------------------------------------------
# PROJECT_DIR IS REQUIRED AND HAS NO DEFAULT (added 2026-08-07, incident 29).
#
# This script used to read:
#     source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"
# so an unset PROJECT_DIR silently tested a DIFFERENT CHECKOUT and exited 0. On
# 2026-08-07 that certified the wrong tree during the v1.1.0 integration: it
# reported 298 passed against an expectation of 348 and returned success. The
# failure is not a crash -- it is a green gate that describes a tree nobody
# asked about, which is the same shape as incident 24.
#
# The validation below runs BEFORE env.sh is sourced. When this guard was added
# env.sh still carried the same default, so checking afterwards would have read
# a value env.sh had just invented. That default was removed from env.sh on
# 2026-08-07, so the two now agree; this check is kept as the nearer of the two,
# because it gives the operator a message naming this script.
# ---------------------------------------------------------------------------
die() { echo "run_tests: FATAL: $*" >&2; exit 2; }

[ -n "${PROJECT_DIR:-}" ] || die "PROJECT_DIR is not set. It is REQUIRED and has no default.
  Pass it explicitly, BEFORE the script path (options after the path are parsed
  as script arguments -- incident 21):
    sbatch -A \"\$ACCOUNT\" -q inferno -p cpu-small \\
           --export=ALL,PROJECT_DIR=\"\$PWD\" scripts/slurm/run_tests.sbatch"

[ -d "$PROJECT_DIR" ] || die "PROJECT_DIR=$PROJECT_DIR does not exist or is not a directory"

# Resolve, so the log records the real tree and two spellings of one path cannot
# read as two different trees.
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)" || die "cannot resolve PROJECT_DIR"
export PROJECT_DIR

# It must be a repository ROOT, not a subdirectory and not an unrelated tree.
# Checked by the project's own marker files rather than by .git, so this works
# in a linked worktree (where .git is a file) and in an exported snapshot.
for marker in pyproject.toml tests flipeval scripts/slurm/env.sh; do
  [ -e "$PROJECT_DIR/$marker" ] || die "PROJECT_DIR=$PROJECT_DIR is not a flipeval repository root: missing '$marker'"
done
[ -n "$(find "$PROJECT_DIR/tests" -maxdepth 1 -name 'test_*.py' -print -quit)" ] \
  || die "PROJECT_DIR=$PROJECT_DIR has no tests/test_*.py -- refusing to report a vacuous pass"

# shellcheck source=scripts/slurm/env.sh
source "$PROJECT_DIR/scripts/slurm/env.sh"
mkdir -p logs

echo "run_tests: PROJECT_DIR validated explicit -> $PROJECT_DIR"
echo "run_tests: tests/ holds $(find "$PROJECT_DIR/tests" -maxdepth 1 -name 'test_*.py' | wc -l) test files"

echo "run_tests: image=$IMAGE project=$PROJECT_DIR args=${PYTEST_ARGS:-<none>}"

# shellcheck disable=SC2086  # splitting PYTEST_ARGS into argv is intended
apptainer exec --cleanenv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m pytest -q /workspace/tests ${PYTEST_ARGS:-}
rc=$?

echo "IN_IMAGE_PYTEST_EXIT: $rc"
exit "$rc"
