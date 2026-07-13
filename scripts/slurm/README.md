# PACE bridge SLURM helpers

These files implement the operational sequence in `docs/PACE_RUNBOOK.md` with the
pinned Apptainer image. Edit `PROJECT_DIR` in `env.sh` or export it when submitting.

The C4 artifact step is intentionally separate from checkpoint construction. It
creates one immutable artifact per seed, then GPTQ and AWQ consume the same file.

```bash
# First verify RAM/cache quota and the C4 sequential-stream plan in the runbook.
CALIB0=$(sbatch --parsable --array=0 scripts/slurm/prepare_calibration.sbatch)
CANARY=$(sbatch --parsable --array=0,3 --dependency=afterok:$CALIB0 \
  scripts/slurm/build_quantized.sbatch)

# Pause and review the seed-0 artifact, GPTQ/AWQ receipts, reloads, and logs.
CALIB12=$(sbatch --parsable --array=1-2%1 scripts/slurm/prepare_calibration.sbatch)
BUILD12=$(sbatch --parsable --array=1-2,4-5 --dependency=afterok:$CALIB12 \
  scripts/slurm/build_quantized.sbatch)
BRIDGE=$(sbatch --parsable --dependency=afterok:$BUILD12 scripts/slurm/run_bridge.sbatch)
sbatch --dependency=afterok:$BRIDGE scripts/slurm/verify_bridge.sbatch
```

The bridge validator requires all fourteen JSONLs, merged manifest coverage,
chat-prompt metadata, identical item/gold/prompt sets, baseline accuracy inside the
predeclared ranges, and identical GPTQ/AWQ calibration receipts for seeds 0–2. It
writes `bridge_validation_summary.json` and exits nonzero on any mismatch.

The three-seed bridge is an operational canary only. It must not be interpreted as
the registered five-seed H3 analysis.
