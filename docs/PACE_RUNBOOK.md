# PACE Runbook

## Preconditions

Do not run GPU jobs until all of the following are true:

1. The project-local Git repository is on the intended frozen commit.
2. `python -m pytest -q` passes in the image.
3. `docs/PREPACE_FREEZE.json` matches the checked-out files.
4. The real C4 calibration-artifact preflight passes. The WikiText-2 protocol
   blocker described below requires a dated human-approved resolution before
   WikiText-dependent main-grid work, but does not block this C4-only bridge.
5. The bridge is treated only as an operational canary, not an H3 analysis.

## Storage layout

Keep source, manifests, summaries, and final logs in project storage. Keep model
weights, the Hugging Face cache, calibration artifacts, and intermediate checkpoints
in scratch.

```text
$PROJECT/flipeval/                    # source and durable results
$PROJECT/flipeval/results/            # JSONLs, summaries, receipts, decision records
$SCRATCH/flipeval/hf_cache/           # model and dataset cache
$SCRATCH/flipeval/calibration/        # shared immutable per-seed artifacts
$SCRATCH/flipeval/checkpoints/        # large checkpoint staging
$SCRATCH/flipeval/flipeval.sif        # Apptainer image
```

The pinned C4 `en` train split contains 364,868,892 rows. The implementation allocates
and shuffles its complete index array (about 2.9 GB as `int64`), then retrieves the
required global rows through the pinned sequential Hugging Face stream and restores
them to permutation order before applying the length rule. This is exactly equivalent
to indexing the complete shuffled array; it is not reservoir sampling and does not
change the registered selection rule. It avoids materializing the >1 TB decoded
Arrow dataset, but a random prefix normally forces a scan through most of the
hundreds-of-GB compressed split. Confirm RAM, cache quota, network policy, and wall
time before submitting. Record `retrieval.passes` and
`retrieval.stream_rows_scanned` from the resulting artifact.

## Build and fingerprint the image

```bash
export PROJECT=$HOME/p-<allocation>/flipeval
export SCRATCH_ROOT=$HOME/scratch/flipeval
export IMAGE=$SCRATCH_ROOT/flipeval.sif
mkdir -p "$PROJECT" "$SCRATCH_ROOT"/{hf_cache,calibration,checkpoints,work,logs}

cd "$PROJECT"
apptainer build "$IMAGE" flipeval.def
apptainer exec "$IMAGE" python -m pytest -q
apptainer exec "$IMAGE" sh /workspace/container/cpu_smoke.sh
apptainer exec "$IMAGE" cat /opt/flipeval/environment.lock.txt \
  > container/environment.lock.pace.txt
sha256sum "$IMAGE" > container/flipeval.sif.sha256
```

The existing `container/environment.lock.resolved.txt` came from the Docker mirror.
Retain the PACE-generated lock separately rather than overwriting it.

## Calibration artifact preflight

The artifact builder pins:

- Qwen2.5-1.5B-Instruct revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- C4 revision `1588ec454efa1a09f29cd18ddd04fe05fc8653a2`.
- WikiText revision `b08601e04326c79dfdd32d625aee71d232d685c3`.

Before any bridge checkpoint build, create seed 0 once and validate the resulting
JSON. It must contain 128 distinct document indices and 128 samples of exactly 2,048
token IDs, and its checksum must validate when loaded again. Because this is the
first real C4 execution, also preserve peak RSS, cached bytes, wall time, stream-pass
count, and scanned-row count in the operational receipt.

```bash
apptainer exec --pwd /workspace \
  --bind "$PROJECT:/workspace,$SCRATCH_ROOT:/scratch" "$IMAGE" \
  python /workspace/scripts/build_quantized.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --model-revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 \
  --seed 0 --dataset c4 \
  --dataset-cache-dir /scratch/hf_cache/datasets \
  --calibration-artifact /scratch/calibration/qwen25-1p5b-c4-s0.json \
  --prepare-calibration-only --trust-remote-code
```

The WikiText-2 preflight was executed locally on 2026-07-13 inside the pinned Docker
runtime with the exact Qwen revision. It found **0 of 36,718 train rows** at least
2,048 tokens and stopped as designed. The row-level interpretation of the registered
condition is therefore impossible. Resolve `docs/WIKITEXT2_PROTOCOL_BLOCKER.md` with
a dated amendment before WikiText-dependent main-grid execution. This does not
authorize changing or delaying the separately registered C4-only bridge. Do not
concatenate rows, reconstruct articles, change datasets, or relax the length rule
without recording that choice.

## Staged bridge canary

Use the maintained helpers in `scripts/slurm/`:

1. Generate only the C4 seed-0 artifact with `prepare_calibration.sbatch --array=0`.
2. Build only array indices 0 and 3 first: GPTQ seed 0 and AWQ seed 0.
3. Confirm both checkpoints save, reload through the evaluation runner, and contain
   receipts with the identical artifact checksum, indices, and token hashes.
4. Generate the seed-1 and seed-2 artifacts serially, then build their four
   checkpoints.
5. Run the seven evaluation methods one per array job with `run_bridge.sbatch`.
6. Run `verify_bridge.sbatch` only after all evaluation jobs succeed.

Example staged submission (do not submit the second block until the two canaries
have been reviewed):

```bash
# PROJECT_DIR is REQUIRED (incident 29) and must precede the script path
# (incident 21). Everything below assumes:
#   export SB="sbatch -A $ACCOUNT -q inferno --export=ALL,PROJECT_DIR=$PWD"
CALIB0=$($SB --parsable --array=0 scripts/slurm/prepare_calibration.sbatch)
CANARY=$($SB --parsable --array=0,3 --dependency=afterok:$CALIB0 \
  scripts/slurm/build_quantized.sbatch)

# Pause here and review CALIB0 and CANARY artifacts/logs.
CALIB12=$($SB --parsable --array=1-2%1 scripts/slurm/prepare_calibration.sbatch)
BUILD12=$($SB --parsable --array=1-2,4-5 --dependency=afterok:$CALIB12 \
  scripts/slurm/build_quantized.sbatch)
BRIDGE=$($SB --parsable --dependency=afterok:$BUILD12 scripts/slurm/run_bridge.sbatch)
sbatch --dependency=afterok:$BRIDGE scripts/slurm/verify_bridge.sbatch
```

`scripts/verify_bridge.py` enforces the frozen operational criteria in
`configs/pace_bridge_chat.yaml`: fourteen expected JSONLs, exact counts, merged
manifest coverage, chat prompts, matching item/gold/prompt sets, FP16 accuracy gates,
and paired calibration receipts. It writes a checksum-bearing summary and leaves the
human decision record unwritten.

Archive the config, calibration receipts, JSONLs, manifest, validator summary,
environment lock, image checksum, and SLURM logs together. Then write a short human
bridge decision record.

> **Checkpoint manifests are scratch-transient by design — this is not a
> regression.** `verify_bridge.py` resolves its "paired calibration receipts"
> from `<checkpoint>/calibration_manifest.json` in the **live** checkpoint
> directories under `$SCRATCH/flipeval/checkpoints/`. Those directories are
> cleaned up once the run is archived, so **re-running `verify_bridge.py`
> against a bare scratch tree will fail on missing receipts even though nothing
> is wrong.** Two things clear it: copies of the manifests are preserved in the
> archived bundle (`results/bridge_run_20260720.tar.gz`, under
> `bridge_bundle_20260720/calibration_receipts/`) and can be restored, and
> **any rebuilt checkpoint regenerates its own manifest at build time**. So a
> mini-grid re-run needs no special handling here. Do not diagnose this as a
> provenance loss. See `docs/CALIBRATION_RECEIPTS_RECONSTRUCTION_2026-07-21.md`
> § 4.

## Main-grid readiness

Generate the frozen expected matrix with:

```bash
python scripts/expected_grid.py
```

`configs/main_grid_manifest.yaml` expands to 137 model variants and 548 expected
task JSONLs. Do not start this grid merely because the GPTQ/AWQ bridge passes. The
current audit still requires RTN and Wanda builders plus native ARC-Challenge and
HellaSwag execution/conversion paths. Their status is machine-readable in the main
grid manifest and summarized in `STATUS.md`.

When every main-grid implementation status is resolved, freeze a new release
manifest and execute the grid without inspecting partial accuracy results. Inspect
only job health, artifact checksums, and expected-file coverage until all registered
cells are complete.

## Registered hierarchical analysis

For each model/benchmark/bit cell, use all five GPTQ/AWQ seed files:

```bash
flipeval paired-seeds \
  --first 0=gptq_s0.jsonl --first 1=gptq_s1.jsonl --first 2=gptq_s2.jsonl \
  --first 3=gptq_s3.jsonl --first 4=gptq_s4.jsonl \
  --second 0=awq_s0.jsonl --second 1=awq_s1.jsonl --second 2=awq_s2.jsonl \
  --second 3=awq_s3.jsonl --second 4=awq_s4.jsonl \
  --expected-seeds 5 --bootstrap 2000 --seed 0 \
  --output hierarchical_summary.json
```

The command fails on seed or item-set mismatches and reports per-seed item
uncertainty, method seed-level SD, item-level SE, the paired two-level delta interval,
joint rank-flip rate, and exact-tie rate. Apply the preregistered H3 decision rule
only after every one of the eight confirmatory 4-bit model-by-benchmark cells exists.
