# PACE Onboarding Checklist (compressedlm)

Created 2026-07-15. Operational document, not protocol; update freely as facts land.
Companion to `docs/PACE_RUNBOOK.md` (technical stages) and
`docs/PACE_EXECUTION_PLAN_2026-07-15.md` (schedule, budgets, go/no-go rules).

Status of the account: PACESHIP application accepted; independence confirmed to
Jeff Valdez 2026-07-15; account setup in progress under short name `compressedlm`.

## Now, before the account exists

- [ ] Sign up for the live PACE Orientation, Tue Aug 18, 11:00–12:45
      (link in Jeff's 2026-07-15 email, KB0042355). Watch the pre-recorded
      orientation videos on the same KB page beforehand.
- [ ] Confirm GT VPN (GlobalProtect) works from the laptop that will ssh in;
      Phoenix login requires campus network or VPN.
- [ ] Verify the Hugging Face account has accepted the meta-llama license for
      Llama-3.2-3B-Instruct and create a fresh fine-grained read token for cluster
      use. Do not reuse a token that has write scopes.
- [ ] Decide the C4 mirror question in principle (plan Stage 2): if scratch quota
      allows ~400 GB, mirror the pinned C4 shards once; this is the single biggest
      cost lever in the whole campaign.

## Day 1, when the account email arrives

- [ ] Log in: `ssh <gtusername>@login-phoenix-slurm.pace.gatech.edu` (from the
      public getting-started guide; confirm exact hostname in the welcome email).
- [ ] Record in this file: home/project/scratch paths and quotas as they actually
      appear (`pace-quota` or equivalent), the charge account string for
      compressedlm, and the free-tier vs paid QOS names (expected: `embers`
      preemptible free tier, `inferno` charged; confirm).
- [ ] `sinfo` / `pace-check-queue`: record GPU partitions and types actually
      available (plan assumes A100 class; V100 is disqualified for AWQ kernels).
- [ ] Confirm `apptainer` is available on compute nodes (module or default).
- [ ] Confirm compute-node network policy (can jobs reach huggingface.co, or must
      all downloads happen on login/data-mover nodes?). This decides how the C4
      mirror and HF cache get staged.
- [ ] Clone the repo at the frozen commit into `$PROJECT/flipeval` and run
      `python scripts/freeze_prepace.py --verify docs/PREPACE_FREEZE.json`.
- [ ] `huggingface-cli login` with the read token; dry-run `snapshot_download`
      of the four pinned model revisions (the Llama-3.2-3B gated pull is the
      one that can fail).

## Week 1 (maps to plan Stages 1–2)

- [ ] Build `flipeval.sif` on a compute node per the runbook; require 37 passed
      in-image; archive `environment.lock.pace.txt` and the image sha256.
- [ ] If mirroring C4: start the ~305 GB download to `$SCRATCH/flipeval/hf_cache`
      on the appropriate node class and verify the pinned revision resolves
      locally with `HF_HUB_OFFLINE=1`.
- [ ] Submit the instrumented C4 seed-0 preflight (Stage 2), including the
      `--verify-stream-row-count` pass, with the pre-committed abort criteria
      from the execution plan. Record passes, rows scanned, peak RSS, wall time.

## Questions for orientation / first consulting session

1. What GPU types and counts can a PACESHIP (student, free-tier) allocation
   actually request, and what are realistic queue waits on them?
2. embers preemption behavior: signal, grace period, requeue semantics — the
   bridge eval jobs are checkpoint-free single passes, so preemption wastes the
   whole pass.
3. Scratch purge schedule and whether a ~305 GB dataset mirror is acceptable use.
4. Any per-job or per-user network egress limits relevant to a one-time ~305 GB
   Hugging Face download.
5. Whether PACESHIP projects can purchase inferno credits, and the cost model,
   in case October queue contention threatens the timeline.

## Blocked until humans act (from the execution plan)

- Decision Point A: WikiText-2 dated amendment — before any mini-grid job.
- Decision Point B: freeze `docs/MINIGRID_REGISTRATION_*.md` — before any
  mini-grid accuracy inspection.
- Llama-3.2-3B FP16 reference ranges — before any quantized Llama result exists.
