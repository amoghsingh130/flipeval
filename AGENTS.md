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
- The H3 decision rule is applied only when all eight confirmatory cells
  exist; the mini-grid escalation rule is in the mini-grid registration.
- Do not tune the calibration builder, paired bootstrap, or any registered
  analysis after seeing results.

## Verification gates

- `python3 -m pytest -q` must pass before and after changes
  (baseline: 53 passed, 1 skipped locally; 54 in-container).
- Source-state fingerprint: `python3 scripts/freeze_prepace.py --verify
  docs/PREPACE_FREEZE.json`. After committing source changes, refresh with
  `python3 scripts/freeze_prepace.py` and commit the updated freeze file
  (the tool refuses dirty worktrees — commit first, freeze second).

## PACE (Phoenix) execution facts

- Source lives in `~/ps-compressedlm-0/flipeval`; caches/weights/artifacts in
  `~/scratch/flipeval` (60-day purge — nothing durable goes there).
- No computation on login nodes: submit via `sbatch -A $ACCOUNT -q inferno`
  (or `-q embers` for cheap preemptible CPU work); scripts in `scripts/slurm/`.
- Runbook: `docs/PACE_RUNBOOK.md`; staged plan with go/no-go criteria:
  `docs/PACE_EXECUTION_PLAN_2026-07-15.md`.
- Everything runs inside the pinned Apptainer image; never pip-install over
  the pinned environment — a dependency change is a new environment cell.
