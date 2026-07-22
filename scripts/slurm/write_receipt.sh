#!/bin/bash
# Write an operational receipt for the running job, at job time.
#
# Satisfies docs/PACE_EXECUTION_PLAN_2026-07-15.md line 38 without the
# reconstruct-from-logs exercise of 2026-07-21
# (docs/CALIBRATION_RECEIPTS_RECONSTRUCTION_2026-07-21.md). Ruled 2026-07-21:
# receipts are written at job time, not reconstructed.
#
#   write_receipt.sh <kind> <output.json> [key=value ...]
#
# Two traps, both learned the hard way during that reconstruction and both
# handled here:
#
#   1. THE EPILOG `mem=` LINE IS NOT PEAK RSS. It reports the `.batch` step --
#      the shell wrapper -- typically ~9,800K, against real workload peaks of
#      ~7 GB. A receipt built from it understates peak memory by ~750x. Peak RSS
#      is therefore read from `sacct MaxRSS` of the WORKLOAD step (`.0`).
#   2. `sacct` AND THE EPILOG DISAGREE ON WALL TIME for some array tasks
#      (11303134_4: epilog 14:37:05 vs sacct 14:53:04). `sacct`, the accounting
#      database, is authoritative.
#
# Absent values are emitted as null with a stated reason. Nothing is estimated.
set -uo pipefail

KIND="${1:?usage: write_receipt.sh <kind> <output.json> [key=value ...]}"
OUTPUT="${2:?usage: write_receipt.sh <kind> <output.json> [key=value ...]}"
shift 2

JOB="${SLURM_JOB_ID:-}"
if [ -n "${SLURM_ARRAY_JOB_ID:-}" ] && [ -n "${SLURM_ARRAY_TASK_ID:-}" ]; then
  JOB_LABEL="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
else
  JOB_LABEL="$JOB"
fi

# sacct accounting can lag a few seconds behind step completion; poll briefly
# rather than record a null we would then have to reconstruct.
STEP_LINE=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
  STEP_LINE="$(sacct -n -P -j "${JOB}.0" --format=MaxRSS,Elapsed,State 2>/dev/null | head -1)"
  [ -n "$STEP_LINE" ] && [ "${STEP_LINE%%|*}" != "" ] && break
  sleep 3
done

RAW_RSS="$(printf '%s' "$STEP_LINE" | cut -d'|' -f1)"
STEP_ELAPSED="$(printf '%s' "$STEP_LINE" | cut -d'|' -f2)"
STEP_STATE="$(printf '%s' "$STEP_LINE" | cut -d'|' -f3)"
JOB_ELAPSED="$(sacct -n -P -j "$JOB" --format=Elapsed 2>/dev/null | head -1)"

# sacct reports MaxRSS with a unit suffix (K/M/G) and occasionally as a float.
# Normalise to whole kilobytes; emit null if the field is empty or unparseable
# rather than guessing a number.
PEAK_RSS_KB="null"
PEAK_RSS_REASON=""
if [ -n "$RAW_RSS" ]; then
  PEAK_RSS_KB="$(awk -v v="$RAW_RSS" 'BEGIN{
    u=substr(v,length(v),1); n=v;
    if (u ~ /[KMGT]/) n=substr(v,1,length(v)-1);
    if (n+0 == 0 && n !~ /^0/) { print "null"; exit }
    if (u=="M") n=n*1024; else if (u=="G") n=n*1024*1024; else if (u=="T") n=n*1024*1024*1024;
    printf "%d", n
  }')"
fi
if [ -z "$PEAK_RSS_KB" ] || [ "$PEAK_RSS_KB" = "null" ]; then
  PEAK_RSS_KB="null"
  PEAK_RSS_REASON="sacct MaxRSS for step ${JOB}.0 was empty or unparseable at receipt-write time"
fi

IMAGE_SHA="null"
if [ -r "${PROJECT_DIR:-.}/container/flipeval.sif.sha256" ]; then
  IMAGE_SHA="\"$(awk '{print $1}' "${PROJECT_DIR:-.}/container/flipeval.sif.sha256" | head -1)\""
fi

EXTRA=""
for pair in "$@"; do
  key="${pair%%=*}"
  value="${pair#*=}"
  EXTRA="${EXTRA}  \"${key}\": \"${value}\",
"
done

mkdir -p "$(dirname "$OUTPUT")"
cat > "$OUTPUT" <<JSON
{
  "schema_version": 1,
  "kind": "${KIND}",
  "reconstructed": false,
  "written_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "written_by": "scripts/slurm/write_receipt.sh at job time",
  "slurm_job_id": "${JOB_LABEL}",
  "slurm_job_id_raw": "${JOB}",
  "node": "$(hostname)",
  "partition": "${SLURM_JOB_PARTITION:-unknown}",
  "qos": "${SLURM_JOB_QOS:-unknown}",
  "gres": "${SLURM_JOB_GRES:-none}",
  "image_sha256": ${IMAGE_SHA},
  "step_state": "${STEP_STATE:-unknown}",
  "wall_time": "${STEP_ELAPSED:-unknown}",
  "wall_time_source": "sacct Elapsed of workload step ${JOB}.0 (final; authoritative accounting record, not the epilog line)",
  "job_elapsed_at_write": "${JOB_ELAPSED:-unknown}",
  "job_elapsed_note": "Job-level elapsed sampled while the job is still running, so it excludes teardown. The workload figure above is the final one.",
  "peak_rss_kb": ${PEAK_RSS_KB},
  "peak_rss_source": "sacct MaxRSS of workload step ${JOB}.0 (NOT the epilog mem= line, which reports the .batch shell wrapper)",
$( [ -n "$PEAK_RSS_REASON" ] && printf '  "peak_rss_absent_reason": "%s",\n' "$PEAK_RSS_REASON" )
${EXTRA}  "cached_bytes": null,
  "cached_bytes_absent_reason": "Not exposed by sacct or the workload. Recorded as absent rather than estimated."
}
JSON

echo "RECEIPT: wrote $OUTPUT (wall ${STEP_ELAPSED:-?}, peak_rss_kb ${PEAK_RSS_KB})"
