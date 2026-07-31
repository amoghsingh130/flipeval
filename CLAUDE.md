# Agent Guardrails (Claude Code, Codex, and any other coding agent)

This is a preregistered research project. Some files are FROZEN and constrain
what any agent may do. Read this before editing anything.

## Frozen files — never edit their registered content

- `PREREGISTRATION.md` (frozen 2026-07-11)
- `docs/MINIGRID_REGISTRATION_2026-07-15.md`
- `docs/ATLAS_MINING_REGISTRATION_2026-07-15.md`
- `docs/AUDIT_REGISTRATION_2026-07-15.md`
- `docs/atlas_pair_manifest.json`, `docs/audit_claim_table.csv` (frozen data)

Changes to frozen protocols happen ONLY as dated entries appended under each
file's "Dated Amendments" section, written by the human (Amogh), stating
whether results were inspected before the decision. If a task seems to
require editing frozen content, stop and surface it instead.

## Result-inspection discipline

- Never interpret partial main-grid or mini-grid accuracy results. During
  grid execution, inspect only job health, checksums, expected-file
  coverage, and receipt pairing.
- **LIVE from 2026-07-22, mini-grid eval phase.** Once eval cells begin
  completing, NO session reads accuracy from any confirmatory cell — not to
  sanity-check, not in passing, not "just the baseline". The permitted surface
  is job health, file coverage, checksums and receipt pairing, and the only
  tool that may aggregate is `scripts/verify_minigrid.py`, whose sole accuracy
  output is the registered FP16 gate. The escalation rule fires on the
  registered computation over complete cells, never on anyone's peek.
- The H3 decision rule is applied only when all eight confirmatory cells
  exist; the mini-grid escalation rule is in the mini-grid registration.
- Do not tune the calibration builder, paired bootstrap, or any registered
  analysis after seeing results.

## Preserving a completed confirmatory result set

**Standing convention, effective 2026-07-25 (Amogh).** The moment a
confirmatory result set is complete, and **before any downstream job runs
against a different config**, do both of these, in this order:

1. **Archive it** — tarball + `.sha256` + a per-file manifest, committed to git
   past the `results/*` ignore (the atlas precedent, e.g.
   `results/minigrid_run_20260722.tar.gz`). Verify the round-trip before
   committing: `sha256sum -c`, then extract and re-hash every file against the
   manifest.
2. **Write-protect it** — `chmod a-w` on the run **directory** and on every file
   in it. This is permanent, not a temporary measure. **Seal the container, not
   a file list** (revised 2026-07-25 after incident 24 — see below).

**Why.** `results/*` is gitignored, so a completed set has no version history to
recover from — a stray `rm`, a scratch purge, or a mis-specified rerun destroys
it outright, and these cells cannot be regenerated without rerunning the
campaign. The write-protection specifically closes a live hazard found
2026-07-25: `pilot_eval/run.py` opens each output `"w"` unconditionally, and
every grid writes under the same `results/` root, so a single unset
`MINIGRID_CONFIG` would have truncated the sealed mini-grid at file-open,
before any log line could warn. `0444` turns that into a `PermissionError`.
That is exactly what happened on 2026-07-25 (array 11485972): the seal held on
all 44 JSONLs and nothing was lost.

**Why the directory, and not just the files.** The same incident showed the
file-list form of this rule is *mechanically* insufficient, not merely
incomplete. `pilot_eval/run.py::_atomic_write` updates `manifest.json` by
writing a temp file and calling `os.replace()`. A rename needs write permission
on the **directory**, never on the target file — so `0444` on `manifest.json` is
inert against that write path, and the replacement lands at the umask default of
`0644`. Both sealed mini-grid manifests were `0o444` in the archive and were
still overwritten, then found writable afterwards. Sealing individual files
protects only against `open("w")`; sealing the directory is what actually closes
rename-in-place. Never conclude a set is protected from its file modes alone.

**Cells a pending job must still write stay writable, individually.** Restore
write on exactly those paths (and, while any cell is pending, on the directory),
and re-seal the moment each one lands. A blanket `chmod a-w` over a directory
holding 0-byte stubs makes the rerun fail at `open()` in precisely the way
11485972 did.

Applied to the mini-grid on 2026-07-25, and to the escalation cells on
2026-07-26 (`results/escalation_run_20260726.tar.gz`, both run dirs sealed).

**The set is not only the run directories — extended 2026-07-26 (incident 26).**
The tarballs above cover run *directories*, so loose artifacts at the results
root were never archived at all: `minigrid_validation_summary.json` had no copy
anywhere, and an unrelated job overwrote it. A completed validation summary is
part of the confirmatory record and gets preserved with it. Small text artifacts
are allowlisted into git directly rather than tarballed — version history is the
protection that was missing, and 50 KB of JSON does not need compression.

**Seal what you inferred, verify what you restored.** Size equality is
corroboration, not content verification: a restored artifact is confirmed by
cross-checking values that a *signed* record cites independently (for the
mini-grid summary: job `11375247`, 409 checks, `passed: true`, 44 cells, per
`docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md`), never against the log it was
recovered from alone.

## No job script is ever given a default grid

**Widened 2026-07-25 (incident 24), from "validators must be told which grid
they are validating".** Every job script that reads *or writes* a grid must be
told which grid, with no fallback. An unset grid variable aborts the job before
the image starts.

`scripts/slurm/verify_minigrid.sbatch` takes `MINIGRID_CONFIG`,
`MINIGRID_RESULTS`, `MINIGRID_MODELS` and `MINIGRID_CELLS` — **all required, no
defaults**. `MINIGRID_MODELS`/`MINIGRID_CELLS` are the operator's declaration of
intent, checked against the config by `verify_minigrid.py`, and each run dir
must hold exactly the cells the config declares.

`scripts/slurm/run_minigrid.sbatch` takes `MINIGRID_CONFIG` and
`MINIGRID_MODELS` — **also required, also no defaults**, plus a length check on
the model list and a non-empty check on the resolved cell. It deliberately takes
no `MINIGRID_RESULTS`: `pilot_eval.run` has no results-root argument and derives
`run_dir` from the config alone, so requiring one would be a control that looks
present and does nothing.

The failure this prevents is not a crash. A validator pointed at the wrong
config validates a complete, self-consistent grid and exits **0**, certifying
nothing about the grid it was meant to check. Both grids live under the same
results root, so only an independent declaration of intent can catch it.

**The runner is the more dangerous of the two, because it writes.** The
validator was hardened on 2026-07-21; the runner kept its defaults until
2026-07-25, so the reader failed closed while the writer failed open — into
write mode, against whatever the default pointed at. Array 11485972 then omitted
the declaration and opened ten cells of the sealed, archived, paper-cited
mini-grid for truncation. Only the `0444` seal stopped it. Never reintroduce a
default in either script, and treat any new grid-touching script as covered by
this rule from its first commit.

## Scheduler controls are not in effect until independently observed

**Standing rule, effective 2026-07-25.** A scheduler flag is in force only when
you have *observed* it — via `scontrol show job/node/partition` after
submission, the QOS or partition configuration (`sacctmgr show qos`,
`scontrol show config`), or the job's actual behaviour. **Acceptance at
submission proves nothing**: `sbatch` exiting 0 means the command parsed, not
that the request took effect.

Three controls have now been found accepted-but-inert in this campaign, all with
a clean `sbatch` exit:

- `--exclude` — accepted and silently discarded by Phoenix's `job_submit` Lua
  plugin, which overwrites `ExcNodeList` (incident 11).
- `--requeue` — set, and `scontrol` reports `Requeue=1`, but Phoenix preempts
  with `PreemptMode=CANCEL`, so preempted jobs are destroyed, never requeued
  (incident 21). Four eval cells vanished.
- **Options placed after the script path** — parsed as *script arguments*, so
  `--array/--export/--constraint/--mem/--dependency` were all ignored and the
  job ran with script defaults (incident 21). **Every `sbatch` option must
  precede the script path.**

Check the specific thing you asked for: `NodeList` for placement, `Requeue` plus
the cluster's `PreemptMode` for retry, `Dependency` for chaining, `Features` and
`MinMemoryNode` for resources, and the job's own first log line for anything
passed by environment.

**Corollary: a constraint that must bind a submission belongs in the `sbatch`
script, not only in a plan document.** The 44 eval cells ran on `embers` because
a dated correction naming `inferno` lived in a plan file while the table above it
still said `embers`; the submission line carried the stale value forward and
preemption then destroyed the work exactly as the correction predicted. Prose
corrections do not bind submissions. Script defaults and required variables do.

## Verification gates

Which gate applies depends on where you are and what you touched.

**Laptop-side (the original convention).** `python3 -m pytest -q` must pass
before and after changes: baseline **53 passed, 1 skipped**. The one skip is the
container-only AutoAWQ import test.

**Phoenix-side (authoritative for any cluster-side source change, from
2026-07-16).** The laptop host gate is *unrunnable* on the Phoenix login node —
it has python 3.9.21 and no pytest, torch, pandas, or scipy, and the project
targets 3.11. The equivalent gate is the in-image suite:

```bash
apptainer exec "$IMAGE" python -m pytest -q   # expect: 207 passed, 0 skipped
```

Run it with `scripts/slurm/run_tests.sbatch`, which executes the suite in the
already-built image. Do **not** rebuild the image to run the gate: a rebuild
re-resolves the pinned environment, so it tests a different environment cell
than the change will run in.

**Whichever session adds tests updates this expected count in the same commit.**
More than one agent session commits to this worktree. A stale expectation is a
gate that cannot fail, which is worse than no gate: on 2026-07-21 the count sat
at 145 while the suite was really at 161, because a concurrent session added 16
tests without touching it. Run `git log` before assuming HEAD is yours.

Run it **before** the commit that triggers a freeze refresh, and cite the
`IN_IMAGE_PYTEST_SUMMARY:` line and its log path from
`scripts/slurm/build_image.sbatch` as the evidence. **Any in-image skip is a
gate failure** — a skip means a pinned dependency silently failed to import
rather than being absent by design. Never pip-install a host environment on the
cluster to recreate the laptop gate: that is a second, unregistered environment
whose versions will not match the pinned image.

**By change type.** Shell-only changes require `bash -n` plus `shellcheck`
(available at `/usr/bin/shellcheck`); doc-only changes require no test gate.
Both still follow commit → freeze → commit **if they land in a fingerprinted
tree** (`configs`, `flipeval`, `pilot_eval`, `scripts`, `tests`, plus the
`INCLUDED_PATHS` list in `scripts/freeze_prepace.py`). `AGENTS.md` and most of
`docs/` are outside the fingerprint and need no freeze refresh.

**Source-state fingerprint.** `python3 scripts/freeze_prepace.py --verify
docs/PREPACE_FREEZE.json`. After committing source changes, refresh with
`python3 scripts/freeze_prepace.py` and commit the updated freeze file (the tool
refuses dirty worktrees — commit first, freeze second).

*One-time bootstrap, not precedent:* `scripts/slurm/build_image.sbatch` was
committed under a waiver on 2026-07-16, because the image it builds is itself
the prerequisite for the gate. Recorded in `docs/PACE_ENVIRONMENT_NOTE.md`.

## PACE (Phoenix) execution facts

- Source lives in `~/ps-compressedlm-0/flipeval`; caches/weights/artifacts in
  `~/scratch/flipeval` (60-day purge — nothing durable goes there).
- No computation on login nodes: submit via `sbatch -A $ACCOUNT -q inferno`
  (or `-q embers` for cheap preemptible CPU work); scripts in `scripts/slurm/`.
- Runbook: `docs/PACE_RUNBOOK.md`; staged plan with go/no-go criteria:
  `docs/PACE_EXECUTION_PLAN_2026-07-15.md`.
- Everything runs inside the pinned Apptainer image; never pip-install over
  the pinned environment — a dependency change is a new environment cell.
