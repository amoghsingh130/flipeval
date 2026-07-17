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

Which gate applies depends on where you are and what you touched.

**Laptop-side (the original convention).** `python3 -m pytest -q` must pass
before and after changes: baseline **53 passed, 1 skipped**. The one skip is the
container-only AutoAWQ import test.

**Phoenix-side (authoritative for any cluster-side source change, from
2026-07-16).** The laptop host gate is *unrunnable* on the Phoenix login node —
it has python 3.9.21 and no pytest, torch, pandas, or scipy, and the project
targets 3.11. The equivalent gate is the in-image suite:

```bash
apptainer exec "$IMAGE" python -m pytest -q   # expect: 54 passed, 0 skipped
```

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
