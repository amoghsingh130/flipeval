# PACE Phoenix Environment Note

Created 2026-07-16. **Operational document, not protocol** — update freely as
facts land. Records measured cluster facts behind the staged plan in
`docs/PACE_EXECUTION_PLAN_2026-07-15.md`. Nothing here relaxes a registered rule.

All facts below were measured on 2026-07-16 from the Phoenix login node or from
two throwaway `embers` probe jobs (`11222009`, `11222157`).

## Charge account

| Field | Value |
|---|---|
| Charge account (`$ACCOUNT`) | **`paceship-compressedlm`** |
| Balance | 1000.00 |
| Reserved | 0.00 |
| Available | 1000.00 |

Submit everything as `sbatch -A paceship-compressedlm -q <embers|inferno> …`.

## Storage paths and quotas (`pace-quota`, 2026-07-16)

| Filesystem | Path | Used | Limit |
|---|---|---|---|
| Home | `/storage/home/hcoda1/0/asingh3206` | 1.6 GB | **20.0 GB** |
| Scratch | `/storage/scratch1/0/asingh3206` | 0.0 GB | 15,360 GB |
| Project | `/storage/project/ps-compressedlm-0` | 0.0 GB | 1,024 GB |

Symlinks in play: `~/scratch -> /storage/scratch1/0/asingh3206` and
`~/ps-compressedlm-0 -> /storage/project/ps-compressedlm-0/asingh3206`. The
defaults in `scripts/slurm/env.sh` resolve correctly through both.

Scratch is **not backed up** and purges files older than 60 days. The C4 mirror
and HF cache live there and must be assumed re-stageable after any long gap.

All five required scratch subdirectories exist under `~/scratch/flipeval`:
`hf_cache`, `calibration`, `checkpoints`, `work`, `logs`.

**Correction to the onboarding checklist:** it records home as 10 GB; the actual
limit is **20 GB**. Still far too small for the ~15 GB Apptainer image or its
build cache — `APPTAINER_CACHEDIR` and `APPTAINER_TMPDIR` must point at scratch
for any build, or the build dies on quota.

## Partitions, QOS, and GPU types

GPU partitions and their GRES (from `sinfo`):

| Partition | GRES | Time limit |
|---|---|---|
| `gpu-a100` | `gpu:a100:2`, `gpu:a100:8` | 3-00:00:00 |
| `gpu-h100` | `gpu:h100:8` | — |
| `gpu-h200` | `gpu:h200:8` | — |
| `gpu-l40s` | `gpu:l40s:8` | — |
| `gpu-rtx6000` | `gpu:rtx_6000:4` | — |
| `gpu-rtxpro-blackwell` | `gpu:rtx_pro_6000_blackwell:8` | — |
| `gpu-v100` | `gpu:v100:2` | 3-00:00:00 |

**A100 is available**, satisfying the plan's GPU pin. V100 (CC 7.0) remains
disqualified for the AWQ/Marlin 4-bit kernel paths; rtx6000 (CC 7.5) marginal.
A representative A100 node (`atl1-1-01-006-3-0`) has 64 CPUs and 515 GB RAM, so
the 8-CPU / 64 GB job shapes fit comfortably.

QOS available to this account (`sacctmgr show assoc`): **`embers`, `inferno`**.

| QOS | MaxWall | Note |
|---|---|---|
| `embers` | **08:00:00** | free/preemptible |
| `inferno` | none configured | charged against the $1,000 |

**The 8-hour `embers` MaxWall is structural, not a preference.**
`scripts/slurm/prepare_calibration.sbatch` requests 48 h and therefore *cannot*
run under `embers` — calibration jobs must use `inferno`. This is why the plan's
"embers acceptable but prefer inferno" for Stage 2 is really "inferno required."

**GRES casing is a non-issue.** `sbatch --test-only` accepts both
`--gres=gpu:A100:1` (as `build_quantized.sbatch:16` writes it) and
`--gres=gpu:a100:1`, despite `sinfo` reporting the type lowercase. No source
change needed.

**Queue estimate (2026-07-16):** `--test-only` against `gpu-a100` under `inferno`
projected a start roughly two days out. An estimate, not a reservation — the
Stage 3 canaries may not be same-day.

## Apptainer

`apptainer 1.4.4-1.el9` at `/usr/bin/apptainer` on compute nodes. **Absent on the
login node, and there is no module for it** (`module spider apptainer` fails;
PACE's own containerized apps invoke `apptainer exec` directly against shipped
`.sif` images). This is consistent with the no-computation-on-head-nodes policy
and confirms the image build must be a batch job, as the plan already requires.

## Network policy (compute nodes)

Egress from compute nodes is **open**; no proxy variables are set.

| Target | Result |
|---|---|
| `huggingface.co/api/...` | 200 |
| C4 pinned-revision API endpoint | 200 |
| `github.com` | 200 |
| Real LFS shard byte range | **206, 161.8 MB/s** |

The actual LFS byte path resolves to **`cas-bridge.xethub.hf.co`** (Hugging
Face's Xet backend). A 50 MB range request returned a valid gzip stream
(magic `1f 8b`) in 0.32 s.

**`cdn-lfs.huggingface.co` does not resolve** — that hostname is stale and its
DNS failure is *not* evidence of a firewall. Do not use it as a reachability
probe.

**Consequence for the C4 mirror (plan Stage 2's "single biggest lever"):** at the
measured rate, ~305 GB is ≈31 minutes; even at a pessimistic sustained 20 MB/s
it is ≈4.2 h — inside the `embers` 8 h wall. The mirror is therefore run as an
`embers` job, falling back to `inferno` only if sustained throughput collapses
below ~15 MB/s on the first attempt (ruled 2026-07-16).

## Pre-Stage-5 blockers

### Gated Llama-3.2-3B access — **CLEARED 2026-07-16**

Pinned revision: `0cb88a4f764b7a12671c53f0838cd831a0843b95`
(`configs/main_grid_manifest.yaml:14`).

**Failing evidence, first test on 2026-07-16 (before the fix):** the
authenticated refs endpoint returned
`Access to model meta-llama/Llama-3.2-3B-Instruct is restricted and you are not
in the authorized list.`, and `resolve/<pinned-rev>/config.json` returned **403**
with the cluster token while the identical Qwen call returned 200. Two candidate
causes were identified and both were addressed in the browser: (1) the license
was not accepted/approved, and (2) the fine-grained token carried only
`repo.content.read` scoped to the user entity, without the global *"Read access
to contents of all public gated repos you can access"* permission.

**Clearing evidence, retested 2026-07-16 after the fix:** refs endpoint answers
normally and reports `main` at `0cb88a4f…3b95` (identical to the pin);
`resolve/<pinned-rev>/config.json` returns **200** (878 B, valid
`LlamaForCausalLM` config); a gated weight-shard range request
(`model-00001-of-00002.safetensors`) returns **206**. The gated *byte* path, not
just metadata, is confirmed.

Retest command (re-run after any token rotation or scratch purge):

```bash
TOK=$(cat ~/.cache/huggingface/token)
REV=0cb88a4f764b7a12671c53f0838cd831a0843b95
curl -sSL -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOK" \
  "https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/resolve/$REV/config.json"
# 200 = cleared; 403 = blocked; anything else, investigate before Stage 5.
```

**Standing rule (ruled 2026-07-16):** Stage 5 and the mini-grid config freeze
must not begin while this blocker is OPEN. It is now CLEARED, so it no longer
gates Stage 5 — but a token rotation or a lapse in license acceptance reopens
it, and the retest above is the only accepted evidence.

**Repo metadata is a false negative detector.** `GET /api/models/meta-llama/...`
returns 200 *unauthenticated* even while file access is 403. Only an
authenticated file fetch (or `snapshot_download`) tests the gate. The onboarding
checklist's `snapshot_download` dry-run would have caught this; a metadata check
would not.

## Corrections to the 2026-07-16 briefing

Recorded so the operational history stays honest:

1. **"Gated Llama-3.2-3B access is verified" was wrong when stated.** It had
   never been tested end-to-end; the first real test returned 403 with an
   explicit authorized-list rejection. Access has since been granted and
   verified (above). — *Amogh, 2026-07-16*
2. **Stopping Stage 0 on that failed gate was correct behavior**, not excessive
   caution: the plan's Stage 0 go/no-go names gated Llama access explicitly, and
   proceeding on the theory that "Llama is only needed at Stage 5" would have
   walked past a written gate. — *Amogh, 2026-07-16*
3. **The Stage 1 in-image test count of 37 was stale**; the gate is 54 passed /
   0 skipped / 0 failed, and any in-image skip is a gate failure. See the dated
   erratum in `docs/PACE_EXECUTION_PLAN_2026-07-15.md`.
4. **One error was the agent's own:** an initial 404 against the Llama revision
   endpoint came from a mistyped revision (the plan abbreviates `0cb88a4f…`, and
   the guessed tail was wrong). The pinned revision exists and resolves; the
   real finding was the 403, not the 404. Always take the revision from
   `configs/main_grid_manifest.yaml`, never from an abbreviation.

## Verification gates on Phoenix — the host gate is unrunnable here (2026-07-16)

**Measured:** the Phoenix login node has `python3` **3.9.21** at `/usr/bin/python3`
and **no pytest, torch, pandas, or scipy**; no project venv exists; and no
`python`/`anaconda3` module supplies them (they resolve to the same 3.9.21 with
numpy 1.23.5 and yaml 5.4.1 only). The project targets Python 3.11. AGENTS.md's
`53 passed, 1 skipped` baseline was established in the laptop dev environment,
which has never existed on this cluster.

Recreating it here was considered and **rejected**: `tests/test_pilot_eval.py`
imports torch, so a host environment means multi-GB wheels at *unpinned*
versions (`requirements.txt` says `torch>=2.3`; the image pins 2.13.0). That is
a second, unregistered environment whose results would not match the image's —
the opposite of what the gate is for.

**Ruled 2026-07-16:**

1. **This change waived.** `scripts/slurm/build_image.sbatch` is shell-only, a
   new file, imported by nothing. Required checks for changes touching no Python
   are `bash -n` **plus `shellcheck`** (present at `/usr/bin/shellcheck`,
   v0.10.0). Both were run and are clean.
2. **Standing rule from Stage 1 onward.** For any cluster-side source change the
   authoritative gate is the in-image suite —
   `apptainer exec $IMAGE python -m pytest -q`, expecting **54 passed,
   0 skipped** — run *before* the commit that triggers a freeze refresh.
   `scripts/slurm/build_image.sbatch` emits an `IN_IMAGE_PYTEST_SUMMARY:` line
   carrying counts, exit code, job ID, and log path, so freeze-refresh commits
   can cite grep-able evidence. AGENTS.md's Verification gates section is
   updated to match: the 53+1 host gate stays as the laptop-side convention, the
   in-image gate is its Phoenix-side equivalent.
3. **Circularity, acknowledged for the record.** Stage 1's own sbatch is
   necessarily committed under the waiver, because the image it builds is the
   gate's prerequisite. **A one-time bootstrap, not precedent.**

## Ruled decisions carried into execution (2026-07-16)

- Stage 1 gate: 54 passed, 0 skipped, 0 failed in-image; any skip fails the gate.
- Stage 1 build sets `APPTAINER_CACHEDIR`/`APPTAINER_TMPDIR` to scratch, and runs
  the CPU smoke with `--bind "$SCRATCH_DIR/work/kaggle:/kaggle/working"` rather
  than modifying `container/cpu_smoke.sh`.
- Stage 1.5 (new): mirror the pinned C4 `en` shards to the scratch HF cache, then
  prove `HF_HUB_OFFLINE=1` streaming resolution of the pinned revision on a small
  probe before Stage 2. Stage 2 runs against the mirror.
- Stage 2 abort criteria (24 h projection at the 50M-row checkpoint, 48 GB RSS,
  1.5 TB volume cap) apply **per pass, including the `VERIFY_ROW_COUNT` pass**.
  With the mirror, verify+create in one 48 h job is accepted. Without the mirror,
  verification splits into its own job and execution stops for reassessment —
  two network scans in one job is not permitted.
- GPU-type pin stays A100. It remains changeable **only until the first
  quantization job runs, never after**. If `--test-only` shows H100 starting
  materially sooner, the comparison is reported before anything is submitted.
