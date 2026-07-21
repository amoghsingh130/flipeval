# Calibration Operational Receipts — Reconstruction Note (2026-07-21)

Records a deviation against `docs/PACE_EXECUTION_PLAN_2026-07-15.md` line 38 and
its resolution. Ruled by Amogh 2026-07-21: **real gap, reconstruct with
disclosure.** Artifacts: `results/calibration_receipts.json` (full) and
`results/calibration_receipts.csv` (index).

## 1. The gap

Plan line 38 requires, for each calibration artifact, "an operational receipt
with peak RSS, cached bytes, wall time, `passes`, `stream_rows_scanned`; a copy
of the receipt (not the token IDs) into `$PROJECT/flipeval/results/`."

**No such receipt was ever written.** All 10 artifacts exist
(`~/scratch/flipeval/calibration/{qwen25-1p5b,llama32-3b}-c4-s{0..4}.json`), and
`results/` contained no calibration receipt until this note.

This is an **operational-bookkeeping gap, not a validity problem.** The
scientifically load-bearing provenance — `artifact_sha256`,
`selected_document_indices`, `selected_token_hashes`, `retrieval`, `dataset`,
`tokenizer`, `seed` — was written into each artifact at build time and is
intact. Nothing about the campaign's claims rests on the missing operational
figures.

## 2. Count correction

The authoritative count is **10** calibration artifacts (2 models × 5 seeds), per
plan line 8. An earlier advisory framing of "13, with 7 remaining" was an error
on our side; it does not correspond to any file or plan text in this repository.
No file changes were needed to resolve it. Recorded here so the discrepancy is
not rediscovered later as a supposed inconsistency.

## 3. Reconstruction method

Reconstructed from **primary records only**, never estimated:

| quantity | source | status |
|---|---|---|
| wall time | `sacct` `Elapsed` | **recovered, 10/10** |
| peak RSS | `sacct` `MaxRSS` of the **workload step** (`.0`) | **recovered, 10/10** |
| `passes` | artifact `retrieval.passes` (written at build time) | **recovered, 10/10** |
| `stream_rows_scanned` | artifact `retrieval.stream_rows_scanned` | **recovered, 10/10** |
| cached bytes | — | **ABSENT** |

**Cached bytes is absent from every primary record** — not in the job log, not in
`sacct`, not in the artifact. It is emitted as `null` with a stated reason rather
than estimated, per the ruling.

Each receipt carries `"reconstructed": true` with the SLURM job ID, the log path,
and a note that it was not written at build time. The log↔artifact mapping was
established by reading each log's `Calibration artifact:` line, not inferred from
timestamps. The failed job `11233525_0` (1 s, no artifact) is excluded; its
successful replacement is `11233678_0`.

**Cross-check: the sha256 chain verifies 10 of 10.** Each artifact's internal
`artifact_sha256` equals the digest its build job logged at the time. The
artifacts are the ones the logs describe.

### Two traps worth recording

**The epilog `mem=` line is not peak RSS.** Every job log's
`Rsrc Used: ... mem=~9,800K` reports the `.batch` step — the shell wrapper —
not the workload. Actual peaks are ~6.9–7.4 GB on the `.0` step. A receipt built
from the epilog line would have understated peak memory by a factor of ~750 and
looked plausible enough to survive review.

**`sacct` and the log epilog disagree on wall time for some array tasks.** For
`11303134_4` the epilog reads `walltime=14:37:05` while `sacct` reads
`14:53:04`. The receipts use `sacct`, the accounting database, as authoritative.

## 4. What `verify_bridge.py` actually validated

The ruling asked whether the bridge's "paired calibration receipts" criterion ran
against something else. **It did.**

`scripts/verify_bridge.py:155` resolves
`receipt_path = checkpoint / "calibration_manifest.json"` — a **per-checkpoint
manifest inside each quantized checkpoint directory**, not the plan-line-38
operational receipt in `results/`. It checks seed, sample count, sequence
length, dataset repo/config/revision, index and token-hash counts, model and
tokenizer identity, and `artifact_sha256` — i.e. exactly the scientific
provenance, and none of the operational quantities (peak RSS, wall time, cached
bytes, passes, rows scanned).

So the bridge validation was sound and is unaffected by this gap: it never
depended on the missing receipts, and the criterion it did enforce is the one
that matters for pairing correctness.

**The live checkpoint copies are gone, but the manifests themselves survive in
the archive.** `~/scratch/flipeval/checkpoints/` is empty — the bridge
checkpoints were scratch-transient by design and were cleaned up after
`results/bridge_run_20260720.tar.gz` was archived.

**Copies are preserved in the committed bridge tarball**, at:

```
results/bridge_run_20260720.tar.gz
  └─ bridge_bundle_20260720/calibration_receipts/
       qwen25-1p5b-{gptq4,awq4}-seed{0,1,2}.calibration_manifest.json   (6 files)
```

Six manifests, matching the bridge's three paired seeds × two methods. So the
provenance `verify_bridge.py` checked is durably retained, alongside the signed
`docs/BRIDGE_DECISION_RECORD_2026-07-20.md` and the archived run artifacts.
Nothing is lost.

Anyone re-running `verify_bridge.py` today against a bare scratch tree will
still fail on missing receipts, because the validator resolves them from live
checkpoint directories rather than from the archive. **That failure is an
artifact of cleanup, not a regression**, and the manifests can be restored from
the tarball above. Rebuilt checkpoints regenerate their own manifests at build
time, so the condition also clears itself on any re-run. Recorded so it is not
rediscovered later as a scare.

## 5. Scope

- Reconstruction only. **No calibration artifact was rebuilt, modified, or
  re-derived**, and no registered quantity is touched.
- Neither `results/` nor `docs/` is in the freeze fingerprint
  (`INCLUDED_PATHS` / `INCLUDED_TREES` of `scripts/freeze_prepace.py`), so no
  freeze refresh and no test gate is owed for this note or its artifacts.
- `results/calibration_receipts.{json,csv}` were added to the `.gitignore`
  allowlist rather than force-added, so their tracking is visible in the ignore
  rules.
- The reconstruction script is retained in the session scratchpad rather than
  committed to `scripts/`, which is a fingerprinted tree; the method is fully
  described above and the inputs (`sacct`, `logs/`, the artifacts) are durable.
  `logs/` lives on project storage, not the 60-day-purge scratch.
