# FlipEval PACE Execution Plan — First Login through H3 Mini-Grid Completion

**Prepared 2026-07-15 (experiment-planner agent, read-only). Governs: Phoenix cluster, project "compressedlm", onboarding ~Aug 18 2026.**
**Governing documents (frozen, never altered by this plan):** `PREREGISTRATION.md`, `configs/pace_bridge_chat.yaml`, `configs/main_grid_manifest.yaml`, `docs/PACE_RUNBOOK.md`, `docs/PREPACE_FREEZE.json`.

**Scope note.** The mini-grid = {Qwen2.5-1.5B-Instruct rev `989aa79…`, Llama-3.2-3B-Instruct rev `0cb88a4…`} × {GPTQ, AWQ} × 4-bit × seeds {0,1,2,3,4} = 20 checkpoints, + 2 FP16 baselines, evaluated on MMLU (full test, per manifest) and GSM8K (test indices 0–999, per manifest). This covers 4 of the 8 registered confirmatory H3 cells; the frozen H3 decision rule cannot be adjudicated from it alone. See "Registration actions" at the end — two documents must be committed **before** any mini-grid accuracy is inspected.

**A key cost fact the plan is built around:** calibration artifacts are per model × seed (eligibility at ≥2,048 tokens depends on the tokenizer), so the mini-grid needs **10 C4 artifacts** (2 models × 5 seeds), and `create_calibration_artifact_from_stream` (scripts/build_quantized.py:249–330) retrieves shuffled indices in windows of 4,096 via fresh sequential stream passes. The first window's max index is ~the full 364,868,892-row range, so **each pass scans essentially the whole compressed C4 `en` train split (~305 GB)**, and if <128 eligible docs land in a window, another full pass follows. Mitigating this (one local mirror, many local passes) is the single biggest operational lever below.

---

## Stage 0 — Access, quotas, and frozen-source transfer (no GPU)

- **Objective.** Working Phoenix login; storage layout per runbook; repo at the frozen commit; HF access verified (Llama-3.2-3B is a gated repo — confirm the HF token on the cluster can pull rev `0cb88a4f…` and the pinned C4/MMLU/GSM8K revisions).
- **Inputs.** Git repo at commit `6d7cdc4` (or current frozen HEAD of `codex/pre-pace-implementation` merged as intended), `docs/PREPACE_FREEZE.json`, HF token.
  <br>*Note, 2026-07-28: the branch `codex/pre-pace-implementation` was renamed to `main` and deleted. The name above is left as written because it is accurate for this document's date; read it as `main`. The same name appears in `docs/PREPACE_FREEZE.json`, which is a generated record of the state at freeze time and is deliberately not regenerated — see the rename note in `docs/RELEASE_CHECKLIST_v1.0.0.md`.*
- **SLURM request.** None (login node only). Record actual quota numbers: project quota, scratch quota (need ≥400 GB scratch if the C4 mirror option is taken; ≥100 GB otherwise), scratch purge policy, and the exact GPU partition/QOS names and charge account for "compressedlm" (confirm at Aug 18 orientation: expected `-q embers` free/preemptible vs `-q inferno` charged, `--gres=gpu:A100:1` style requests).
- **Artifacts.** `$PROJECT/flipeval` populated; a dated `docs/PACE_ENVIRONMENT_NOTE.md`-style operational note (new file, allowed — operational, not protocol) recording quotas, partition names, account string, and network policy on compute nodes.
- **Fail-closed validation.** `python scripts/freeze_prepace.py` (or the check it feeds) confirms checked-out files match `docs/PREPACE_FREEZE.json`; `git status` clean; HF `snapshot_download` dry-check of all four pinned model revisions and the Llama gate succeeds.
- **Go/no-go (commit before results).** GO iff freeze check passes byte-exact AND Llama-3.2-3B gated access confirmed AND scratch quota ≥100 GB. NO-GO on any freeze mismatch: stop, do not "fix forward" on the cluster; re-sync from the local frozen commit.

## Stage 1 — Apptainer build + in-container test gate (CPU)

- **Objective.** Build `flipeval.sif` from `flipeval.def`; prove the PACE container reproduces the local gate.
- **Inputs.** `flipeval.def`, `container/requirements.lock`.
- **SLURM request.** 1 CPU node job (or interactive): 8 CPUs, 32 GB, 4 h, no GPU, QOS embers. Build on a compute node, not login.
- **Artifacts.** `$SCRATCH/flipeval/flipeval.sif`; `container/flipeval.sif.sha256`; `container/environment.lock.pace.txt` kept **separate** from the Docker-mirror lock (runbook requirement); pytest and `cpu_smoke.sh` logs archived to `$PROJECT/flipeval/results/pace_gate/`.
- **Fail-closed validation.** In-image `python -m pytest -q` must report **54 passed, 0 skipped, 0 failed** (see Erratum 2026-07-16; the count below was corrected from the stale 37), including the AutoAWQ calibration-ID preservation test; any in-image skip is a gate failure; `container/cpu_smoke.sh` completes and regenerates both analysis summaries; diff `environment.lock.pace.txt` vs `environment.lock.resolved.txt` and record every divergence.
- **Go/no-go.** GO iff 54/54 pass with zero skips and CPU smoke exits 0. If the PACE lock diverges from the pinned versions of torch 2.13.0 / transformers 5.13.0 / GPTQModel 7.1.0 / AutoAWQ 0.2.9 / lm-eval 0.4.12 / datasets 5.0.0: NO-GO — a divergent resolve is a new environment cell under the preregistration's backend rule; rebuild with hard pins rather than proceed.

## Stage 2 — C4 seed-0 artifact preflight (Qwen2.5-1.5B), the measured one

- **Objective.** First real execution of the registered C4 selection: produce `qwen25-1p5b-c4-s0.json` and the operational receipt with `retrieval.passes` and `retrieval.stream_rows_scanned`, under instrumented RAM/IO/wall-time checkpoints.
- **Inputs.** `scripts/slurm/prepare_calibration.sbatch --array=0`, image from Stage 1.
- **Recommended pre-step (operational, no protocol change — verify code path first).** Download the pinned C4 `en` train shards (revision `1588ec45…`, ~305 GB compressed) once into `$SCRATCH/flipeval/hf_cache`, then let the streaming loader read locally. This converts N network scans into N local scans and is the difference between a tractable and an intractable Stage 5 (10 artifacts). It requires confirming `load_dataset(..., streaming=True)` with the pinned revision resolves from the local cache/`HF_HUB_OFFLINE=1`; if it does not, treat network streaming as the baseline and budget accordingly. Only do this if scratch quota ≥400 GB.
- **SLURM request.** CPU-only: 8 CPUs, **64 GB** (2.9 GB int64 index array + tokenizer + stream buffers; observed headroom target ≤48 GB RSS), **48 h wall** (script default), scratch bound at `/scratch`, QOS embers acceptable but note preemption restarts the pass from zero — prefer inferno if credits allow.
- **Measured checkpoints (log at stream rows 1M, 10M, 50M, 100M, 200M, and per pass):** elapsed wall time, rows/s, peak RSS, cumulative network bytes (or local read bytes), pass count.
- **Abort criterion (commit before submission).** Abort and reassess if any of: (a) projected single-pass time > 24 h at the 50M-row checkpoint (linear extrapolation), (b) peak RSS > 48 GB, (c) pass count reaches 4 without completing 128 samples, (d) cumulative scratch/network volume exceeds 1.5 TB. Abort = kill job, write the measurements into the operational note, and fix the retrieval-window strategy as an **operational** change (window size is not part of the registered selection rule — the selection is defined by the shuffled index array — but any code change here must be re-tested through the Stage 1 gate and recorded).
- **Artifacts.** `/scratch/calibration/qwen25-1p5b-c4-s0.json`; operational receipt with peak RSS, cached bytes, wall time, `passes`, `stream_rows_scanned`; a copy of the receipt (not the token IDs) into `$PROJECT/flipeval/results/`.
- **Fail-closed validation.** Re-load the artifact through the builder's own validator: exactly 128 distinct document indices, 128 × exactly 2,048 token IDs, tokenizer fingerprint matches the pinned Qwen revision, content checksum revalidates on second load.
- **Go/no-go.** GO iff validation passes and measured cost implies the full 10-artifact Stage 5 fits within (passes×pass-time×10) ≤ 10 days of serial CPU time or can be parallelized within quota. Then, and only then, build seeds 1–2 serially (`--array=1-2%1`) for the bridge.

## Stage 3 — Paired GPTQ/AWQ seed-0 GPU kernel canaries

- **Objective.** First real GPU quantization: GPTQ seed 0 and AWQ seed 0 from the identical artifact; prove save → reload → paired receipts. This is the mandatory AutoAWQ canary flagged in STATUS.md (pinned AutoAWQ is deprecated upstream; kernel behavior on the real GPU is unproven).
- **Inputs.** `scripts/slurm/build_quantized.sbatch --array=0,3 --dependency=afterok:<calib0>`.
- **SLURM request.** 1× GPU per job. **Pin the GPU type now and never change it through the end of the mini-grid** (a GPU/kernel change is a new environment cell). Recommend **A100** (`--gres=gpu:A100:1` or Phoenix equivalent): V100 (CC 7.0) does not support the modern AWQ/Marlin 4-bit kernel paths and is disqualified; RTX6000 (CC 7.5) is marginal. 8 CPUs, 64 GB, 6 h wall each (1.5B quantization is well under this).
- **Artifacts.** `outputs/quantized/qwen25-1p5b-gptq4-seed0/` and `…awq4-seed0/` with checkpoint-local pairing receipts.
- **Fail-closed validation (runbook step 3).** Both checkpoints save; both reload through the evaluation runner (`pilot_eval.run` load path); receipts in both carry the **identical** artifact checksum, document indices, and token hashes; AWQ's deprecation warning is logged but the emitted calibration IDs match the artifact (mirrors the in-image test, now on GPU).
- **Go/no-go.** GO iff both reload without kernel errors/NaN weights and receipt triplets are byte-identical across methods. NO-GO on any AWQ kernel failure: after two failed fix attempts stop and write up symptom/assumptions/discriminating evidence before touching the pinned runtime — any dependency change is a new environment cell and restarts Stage 1.

## Stage 4 — Bridge run (one method per job) + bridge validator

- **Objective.** Execute the frozen operational canary: 7 evaluation methods (fp16, gptq_s0–2, awq_s0–2) on MMLU 4×100 + GSM8K 200, chat prompts, then the fail-closed validator. **Operational only — not H3.**
- **Inputs.** Seeds 1–2 artifacts (Stage 2 tail), builds `--array=1-2,4-5`, then `run_bridge.sbatch` (`--array=0-6`), then `verify_bridge.sbatch`, per the staged dependency chain in `scripts/slurm/README.md`.
- **SLURM request.** Builds: 4 jobs × A100 × 6 h. Bridge evals: 7 jobs × A100, keep script's 64 GB/8 CPU, 8 h wall each (600 items at bs=1 on a 1.5B model is ~1–2 h; 8 h is safe). Validator: CPU, 16 GB, 1 h.
- **Artifacts.** 14 JSONLs + merged manifest under `results/qwen25_1p5b_bridge_chat/`; `bridge_validation_summary.json`; archived bundle (config, receipts, JSONLs, manifest, validator summary, env lock, image checksum, SLURM logs); then a short **human bridge decision record** (required by the runbook, deliberately left unwritten by the validator).
- **Fail-closed validation.** `scripts/verify_bridge.py` enforces the frozen criteria: 14 JSONLs, exact counts (400/200), manifest coverage, chat prompts, identical item/gold/prompt sets, FP16 gates MMLU ∈ [0.365, 0.465] and GSM8K ∈ [0.55, 0.65], paired calibration receipts. Nonzero exit = stop.
- **Go/no-go (commit before submission).** GO to mini-grid work iff validator exits 0 AND no job required manual result edits AND the human decision record is written and committed. Any FP16 gate failure = NO-GO + debug under the 2-attempt reassessment rule; quantized accuracies are **not** gates and must not be turned into ad-hoc gates after being seen.

## HUMAN DECISION POINT A — WikiText-2 amendment (deadline: before the first mini-grid job is submitted; target 2026-09-18)

`docs/WIKITEXT2_PROTOCOL_BLOCKER.md`: 0/36,718 rows reach 2,048 Qwen tokens; the frozen row-level reading is impossible. The C4-only bridge and the C4-only mini-grid do not *execute* WikiText, but the blocker doc requires the dated amendment **before the first main-grid job**, and mini-grid checkpoints *are* main-grid cells — so resolve it before mini-grid fan-out, not after. Decision owner: Amogh, alone, results-blind (only the preflight failure has been seen, which is recorded). Recommended: Option A (deterministic article reconstruction), recorded as a dated amendment in `PREREGISTRATION.md` § Dated Amendments, with the builder continuing to fail closed until the amended rule is implemented and tested. This amendment does not need the WikiText condition *implemented* before the mini-grid — only decided and recorded.

## HUMAN DECISION POINT B — Mini-grid registration + escalation rule (same deadline, before any mini-grid accuracy inspection)

The 2026-07-15 strategy (mini-grid now; 7B/8B only on instability; Wanda/3-bit/RTN-timing deferred) is a scope change relative to the frozen 8-cell H3 protocol, and "escalate if the mini-grid shows ranking instability" is itself an inspection of confirmatory-cell results. Before fan-out, commit a new doc (e.g., `docs/MINIGRID_REGISTRATION_2026-09.md`) + a dated amendment pointer that fixes, verbatim and in advance: (1) the mini-grid cell set (4 of 8 confirmatory cells); (2) the **escalation trigger** as a mechanical rule — suggested: escalate to the 7B/8B seed cells iff (winner flips in ≥1 of the 4 small-model cells) OR (range/gap criterion holds in ≥2 of 4); (3) the statement that the frozen H3 supported/disconfirmed rule is adjudicated **only** if all 8 cells are eventually run, and otherwise the paper reports the 4 cells descriptively with H3 formally inconclusive; (4) GSM8K few-shot count for the mini-grid (the preregistration fixes "inline in user message" but not the count — pin it, presumably matching the bridge's `fewshot: 1`); (5) the Llama-3.2-3B FP16 operational acceptance ranges (see Stage 5). None of this edits the frozen H3 protocol; it constrains the experimenter.

## Stage 5 — Mini-grid preparation: configs, Llama reference ranges, remaining artifacts

- **Objective.** Everything needed for fan-out, frozen before any fan-out accuracy exists.
- **Work items.**
  1. New `configs/pace_minigrid_h3.yaml` (two models, 22 variants, MMLU full test at pinned revision `c30699e8…`, GSM8K indices 0–999 at `740312ad…`, chat prompts, per-method entries) plus parameterized sbatch scripts (current scripts hard-code Qwen-1.5B — build_quantized.sbatch:16, prepare_calibration.sbatch:19). Local tests + Stage 1-style in-image test rerun; commit; refresh the source freeze.
  2. **Llama-3.2-3B FP16 operational gate ranges**, derived the same way the corrected MMLU bridge gate was (trusted lm-eval reference on the pinned snapshot, e.g. Kaggle T4 as in `docs/MMLU_REFERENCE_RUN.md`), committed into the mini-grid config **before** any quantized Llama result exists.
  3. Remaining C4 artifacts: Qwen seeds 3–4; Llama seeds 0–4 (its tokenizer changes eligibility, full builder run). 7 CPU jobs using Stage 2's measured budget; serialize (`%1`) if network-streaming, parallelize if the local C4 mirror worked.
  4. Llama paired canaries: GPTQ seed 0 + AWQ seed 0, exactly as Stage 3, same GPU type, before the other 8 Llama builds.
- **SLURM.** Artifacts: 7 × CPU (8 CPU, 64 GB, wall = 1.5× measured Stage 2 time). Llama canaries: 2 × A100, 6 h.
- **Fail-closed validation.** Per-artifact revalidation (128 × 2,048, checksum, tokenizer fingerprint — Llama artifacts must carry the Llama fingerprint); Llama canary receipt-pairing check identical to Stage 3.
- **Go/no-go.** GO iff all 10 artifacts validate, both Llama canaries pass, Decision Points A and B are committed with dates, and the freeze file matches the new config commit. Any single artifact failure blocks only its seed pair — but all 5 seeds are required before *analysis*, so the grid does not proceed to Stage 7 with <5 seeds per model.

## Stage 6 — Mini-grid fan-out

- **Objective.** Build 18 remaining checkpoints (20 minus 2 Qwen seed-0 already built — note Qwen seeds 1–2 GPTQ/AWQ also exist from the bridge and are reused, so 12 new: Qwen s3–4 × 2 methods + Llama s1–4 × 2 methods), then run 22 variants × 2 tasks.
- **SLURM.**
  - Builds: 12 × (A100, 8 CPU, 64 GB, 6 h; Llama-3B comfortably fits).
  - Evals: one **method per job** (as in the bridge; per-method-per-task if a `--only-task` flag is added — preferable for preemption tolerance, but that is a code change requiring the Stage 5 gate). 22 jobs: Qwen variants 12 h wall, Llama variants 16 h wall, A100 × 1, 64 GB, 8 CPU. The advisory-locked manifest merge already makes parallel jobs safe.
  - QOS: inferno for evals if credits permit (embers preemption of a 10-h MMLU pass wastes the whole pass at bs=1 unless per-task splitting lands).
- **Artifacts.** 44 task JSONLs (22 variants × 2 tasks), merged manifests per model run-dir, all receipts, SLURM logs.
- **Fail-closed validation (job health only — no accuracy inspection).** Per the runbook's grid discipline: inspect only exit codes, artifact checksums, expected-file coverage, and receipt pairing until **all** cells are complete. Extend `verify_bridge.py` into a mini-grid validator (Stage 5 code item) enforcing: 44 expected JSONLs, exact item counts (MMLU 14,042; GSM8K 1,000), identical item/gold/prompt sets within each model, chat prompt metadata, FP16 gates (bridge-corrected range for Qwen; Stage 5 reference range for Llama), and identical GPTQ/AWQ receipts for all 5 seeds × 2 models.
- **Go/no-go.** GO to Stage 7 iff the mini-grid validator exits 0 over the complete expected set. Failed jobs are rerun with the same registered seed and calibration indices (frozen exclusion rule); a job that fails twice triggers the written reassessment protocol.

## Stage 7 — Registered hierarchical analysis + escalation adjudication

- **Objective.** First accuracy inspection. Run `flipeval paired-seeds` per the runbook command (5 GPTQ + 5 AWQ files, `--expected-seeds 5 --bootstrap 2000 --seed 0`) for each of the 4 cells; compute winner flips, ties, range/gap per the frozen algebra; apply the **pre-committed escalation rule from Decision Point B** mechanically.
- **SLURM.** CPU only: 4 jobs × (4 CPU, 16 GB, 2 h).
- **Artifacts.** 4 `hierarchical_summary.json` files; a dated escalation decision record stating which rule branch fired, written the same day results are first opened.
- **Fail-closed validation.** The command itself fails closed on seed/item-set mismatch. Additionally: recompute one cell's summary twice and require byte-identical output (deterministic bootstrap check).
- **Go/no-go.** Mechanical: escalation trigger fires → schedule 7B/8B seed-cell campaign (Nov–Dec window, new plan document); does not fire → mini-grid results stand, H3 reported per Decision Point B's pre-committed framing.

---

## Totals

**GPU-hours (A100-equivalent).**

| Item | Est. |
|---|---|
| Stage 3 canaries (2 builds) | 3 h |
| Stage 4 builds (4) + bridge evals (7 × ~1.5 h) + margin | 20 h |
| Stage 5 Llama canaries (2) | 4 h |
| Stage 6 builds (12 × ~1–1.5 h) | 16 h |
| Stage 6 evals: 11 Qwen-variant jobs × ~4 h + 11 Llama × ~6 h | 110 h |
| Rerun/preemption margin (~35%) | 55 h |
| **Total** | **~210 A100-hours; budget 300 to be safe** |

CPU-hours (calibration): dominated by C4 scans — with a local mirror, ~10 × (1–3 passes × 3–8 h) ≈ 100–250 CPU-node-hours; without it, potentially 2–4× that plus ~0.3–1.2 TB of network transfer per artifact. This is why the Stage 2 mirror decision matters more than any GPU number.

**Storage.** Project: ≤10 GB (44 JSONLs ≈ 2–5 GB + bridge + logs + receipts). Scratch: models ~12 GB; 20 4-bit checkpoints ~35 GB; artifacts <1 GB; Apptainer image ~15 GB; optional C4 mirror ~305 GB → **~70 GB without mirror, ~400 GB with** (recommended if quota allows).

**Calendar (Aug → Oct 2026).**

| Week of | Milestone |
|---|---|
| Aug 17 | Orientation Aug 18; Stage 0 complete |
| Aug 24 | Stage 1 image + 37-test gate; C4 mirror decision + download started |
| Aug 31 | Stage 2 seed-0 preflight measured; seeds 1–2 built |
| Sep 7 | Stage 3 canaries reviewed |
| Sep 14 | Stage 4 bridge + validator + human bridge record; **Decision Points A & B committed by Sep 18** |
| Sep 21 | Stage 5: mini-grid config frozen, Llama reference ranges, artifacts (Qwen 3–4, Llama 0–4) |
| Sep 28 | Llama canaries; Stage 6 builds |
| Oct 5–12 | Stage 6 eval fan-out (queue-contention buffer built in) |
| Oct 19 | Mini-grid validator green; Stage 7 analysis + escalation record |
| Oct 26 | Buffer / start of escalation campaign or writing. Leaves Nov–Dec for optional 7B/8B, Jan for analysis/atlas/audit integration, Feb 2027 full draft, ~Mar COLM |

**Top 5 risks.**
1. **C4 retrieval cost explodes** (multi-pass ~305 GB scans × 10 artifacts, 48 h walls, network policy). Mitigate: local shard mirror, instrumented checkpoints, the pre-committed abort criterion, window-size fix as tested operational change.
2. **Pinned AutoAWQ (deprecated) fails on real A100 kernels/driver.** Mitigate: seed-0 canary gate before any fan-out; 2-attempt reassessment rule; any dependency change = new environment cell + Stage 1 rerun, decided before results exist.
3. **Governance breach: escalation rule or WikiText amendment not committed before first accuracy look.** Mitigate: Decision Points A & B are hard submission blockers in Stage 5's go/no-go; validator-only inspection discipline in Stage 6.
4. **Queue contention/preemption in October** (embers preemption wastes whole bs=1 MMLU passes). Mitigate: one-method-per-job granularity, inferno credits for the 22 eval jobs, fan-out started by Oct 5, optional `--only-task` split landed at Stage 5.
5. **Llama-3.2-3B specifics untested** (gated access, chat template, no validated FP16 gate range). Mitigate: Stage 0 access check; Stage 5 trusted lm-eval reference run fixing ranges before any quantized Llama result; Llama canaries before its 8-build fan-out.

**Items requiring a dated amendment or new registration doc (all before the corresponding execution/inspection):**
1. WikiText-2 document definition — dated amendment to `PREREGISTRATION.md` (Decision Point A).
2. Mini-grid scope + mechanical escalation rule + statement that frozen H3 adjudication requires all 8 cells — new registration doc + dated amendment pointer (Decision Point B).
3. GSM8K few-shot count for confirmatory cells (unpinned in the preregistration) — fixed inside item 2.
4. Llama-3.2-3B FP16 operational acceptance ranges — committed, dated, pre-inspection (operational gate, mirroring the 2026-07-13 bridge-gate correction pattern).
5. Contingent: any pinned-package or GPU-type change after Stage 3 — recorded as a new environment cell per the frozen backend rule, never a silent replacement.

Key file references: `STATUS.md`, `PREREGISTRATION.md`, `docs/PACE_RUNBOOK.md`, `docs/WIKITEXT2_PROTOCOL_BLOCKER.md`, `configs/pace_bridge_chat.yaml`, `configs/main_grid_manifest.yaml`, `scripts/build_quantized.py` (window logic lines 249–330), `scripts/slurm/*.sbatch`, `scripts/verify_bridge.py`. The hard-coded Qwen model in `prepare_calibration.sbatch`/`build_quantized.sbatch` and the absence of a mini-grid config/validator are the only new code artifacts this plan requires; both are gated behind Stage 5's freeze-and-test step.

---

## Dated Errata

This is an operational planning document, not a frozen protocol. Errata correct
facts that were stale or wrong when written; they never relax a registered rule.

### Erratum 2026-07-16 — Stage 1 in-image test count: 37 → 54

Stage 1 originally required **37 passed** in-image. That number was correct only
for the 2026-07-13 Docker-mirror image, when the host suite stood at 36 passed +
1 skipped. The atlas pipeline has since added 10 tests, taking the host suite to
**53 passed, 1 skipped**; the single host skip is the container-only AutoAWQ
import test, which *executes* inside the image. The in-image expectation is
therefore **54 passed, 0 skipped, 0 failed**.

Ruled by Amogh on 2026-07-16: the Stage 1 gate is 54 passed / 0 skipped /
0 failed, and **any in-image skip is a gate failure** (a skip means a pinned
dependency silently failed to import rather than being absent by design).
Stage 1's fail-closed validation and go/no-go bullets above are corrected in
place. `docs/PACE_ONBOARDING_CHECKLIST.md` carried the same stale 37 and is
corrected to match. `AGENTS.md` already recorded 54 in-container and needed no
change. No registered protocol is affected; the host-side gate (53 passed,
1 skipped) is unchanged.

Decided before any Stage 1 job was submitted and before any quantized accuracy
result existed.

### Erratum 2026-07-17 — the C4 cost premise is falsified: decode-bound, not network-bound

This plan is built around a cost claim stated in its opening ("A key cost fact
the plan is built around"), in Stage 2's recommended pre-step, in the CPU-hours
total, and in Risk 1: that each C4 pass scans ~305 GB over the network, that
this dominates the campaign, and that a local shard mirror is "the single
biggest operational lever" and "the difference between a tractable and an
intractable Stage 5."

**Measured 2026-07-16/17 on Phoenix compute nodes, the premise does not hold.**

| Measurement | Result | Job |
|---|---|---|
| Compute-node link, LFS byte range | 161.8 MB/s (HTTP 206, `cas-bridge.xethub.hf.co`) | 11222157 |
| Network streaming, registered path | **14,021 rows/s → 7.23 h/pass** | 11225540 |
| Local raw `zcat \| wc -l` (gunzip ceiling) | 48,862 rows/s → 2.07 h/pass | 11225540 |
| Local JSON builder on a mirrored shard | 17,673 rows/s → 5.73 h/pass | 11225540 |

A local read beats the network by only **1.26×**, and both sit far below the
raw gunzip ceiling. **The bottleneck is JSON decode on one core, not
transport.** A full pass is ~7.2 h, not the multi-day scan the plan feared, so
10 artifacts at ~7–15 h each is trivially tractable and the C4 cost is not the
campaign's dominant risk.

Consequences, ruled 2026-07-17:

1. **The mirror is demoted** from operational lever to *diagnostic asset*. It
   cannot serve the registered streaming path at all: `load_dataset` must reach
   the Hub to *resolve* the dataset before streaming opens a byte, and
   `HF_HUB_OFFLINE=1` makes that resolution raise rather than fall back to the
   cached snapshot (job 11223841, `OfflineModeIsEnabled`). Retained until Stage 2
   fully completes, because per-shard line counts over the mirror are the only
   cheap tool that could localize a `row_count` discrepancy; afterwards the
   60-day purge may take it. Do not build plans around it.
2. **The local-files loader rewrite is struck permanently.** Its ceiling is
   1.26× (7.2 h → 5.7 h) in exchange for editing fingerprinted Python on the
   registered selection path plus a transport-equivalence argument. The
   condition it was contingent on (network-bound *and* passes > ~30 h) is false
   on both clauses.
3. **Stage 2's CPU-hours estimate is superseded.** "~100–250 CPU-node-hours with
   a mirror, 2–4× that without, plus 0.3–1.2 TB of network transfer per
   artifact" reflected the falsified premise. The real figure is ~7–15 h per
   artifact over the network, ~1 CPU core bound on decode.

Nothing registered changes: artifact creation keeps the pinned
`load_dataset(..., streaming=True)` transport and the registered selection rule.
Decided before any calibration artifact existed and before any accuracy result.
