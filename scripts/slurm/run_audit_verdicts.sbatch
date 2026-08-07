#!/bin/bash
#SBATCH --job-name=flipeval-audit-verdicts
#SBATCH --output=logs/audit_verdicts_%j.out
#SBATCH --error=logs/audit_verdicts_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00

# The registered audit verdict computation (AUDIT_REGISTRATION §4-5, as amended
# 2026-07-31 by Amendment 2).
#
# EVERY INPUT IS REQUIRED -- no defaults. audit_verdicts.py previously defaulted
# --atlas to the REV-1 atlas, superseded 2026-07-21. A run against it completes,
# self-consistently, and exits 0 while imputing from 484 GPTQ 4-bit cells
# instead of rev-2's 792. Nothing in the output announces which revision it
# used, so the operator must declare it.
#
# Amendment 2's *Analysis discipline* clause: the recomputation is run ONCE and
# whatever it returns is reported. AUDIT_OUTPUT must therefore name a path that
# does not exist; the script refuses to overwrite, so a superseded verdict set
# can never be silently replaced by a rerun.
#
#   AUDIT_CLAIM_TABLE   container path to the frozen claim table
#   AUDIT_ATLAS         container path to the CURRENT atlas cell summary
#   AUDIT_OUTPUT        container path for the verdicts CSV (must not exist)
#
# Example:
#   export AUDIT_CLAIM_TABLE=/workspace/docs/audit_claim_table.csv \
#          AUDIT_ATLAS=/workspace/results/atlas_cells_summary_rev2.csv \
#          AUDIT_OUTPUT=/workspace/results/audit_verdicts_rev3.csv
#   sbatch -A "$ACCOUNT" -q inferno -p cpu-small --export=ALL \
#          scripts/slurm/run_audit_verdicts.sbatch

# shellcheck source=scripts/slurm/env.sh
: "${PROJECT_DIR:?required (no default): the flipeval repository root this job acts on.
  Pass it BEFORE the script path: --export=ALL,PROJECT_DIR=\"$PWD\"  (incidents 21, 29)}"
source "$PROJECT_DIR/scripts/slurm/env.sh"
mkdir -p logs

: "${AUDIT_CLAIM_TABLE:?required (no default)}"
: "${AUDIT_ATLAS:?required (no default: a default selects the superseded rev-1 atlas)}"
: "${AUDIT_OUTPUT:?required (no default: a default overwrites a superseded verdict set in place)}"

echo "audit_verdicts: claim_table=$AUDIT_CLAIM_TABLE atlas=$AUDIT_ATLAS output=$AUDIT_OUTPUT"

host_output="${AUDIT_OUTPUT/#\/workspace/$PROJECT_DIR}"
if [ -e "$host_output" ]; then
  echo "REFUSING: $host_output already exists. Amendment 2 allows one run; pick a new path." >&2
  exit 1
fi

apptainer exec --cleanenv --pwd /workspace \
  --bind "$PROJECT_DIR:/workspace,$SCRATCH_DIR:/scratch" \
  "$IMAGE" python -m scripts.audit_verdicts \
  --claim-table "$AUDIT_CLAIM_TABLE" \
  --atlas "$AUDIT_ATLAS" \
  --output "$AUDIT_OUTPUT"
rc=$?

echo "AUDIT_VERDICTS_EXIT: $rc"
exit "$rc"
