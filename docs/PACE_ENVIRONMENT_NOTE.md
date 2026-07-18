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

## Stage 1 container gate — PASS 2026-07-16 (job 11223607)

Built on compute node `atl1-1-02-006-21-2` under `embers`/`cpu-small` in
**12 min 23 s**, peak RSS 22.7 GB, from a clean tree at commit `29d1fd6`.

| Item | Result |
|---|---|
| Image | `~/scratch/flipeval/flipeval.sif`, 5.8 GB |
| Image SHA-256 | `09ed767f29e1c0ebb97451b070bc91759301a2d9b63c706511f8b1dcd013418d` |
| Build mode | unprivileged (no `--fakeroot` needed) |
| In-image tests | **54 passed, 0 skipped, 0 failed** (16.72 s) |
| CPU smoke | exit 0; both analysis summaries regenerated |
| Six gated pins | all match the Docker-mirror lock |

The 54-passed result confirms the erratum: the stale 37 would have failed the
gate. Two warnings are expected and benign — AutoAWQ's upstream deprecation
notice (the reason the runtime stays frozen and the GPU canary is mandatory) and
a `torch.jit.script` deprecation.

**Build mechanics that worked.** No `/etc/subuid` mapping exists for this user,
but apptainer 1.4.4 handled it automatically: `User not listed in /etc/subuid,
trying root-mapped namespace` → `%post` ran under fakeroot. Unprivileged builds
work; `--fakeroot` was never needed. Lustre emits benign
`ignoring ENOTSUP on setxattr` warnings throughout. `APPTAINER_CACHEDIR`/
`APPTAINER_TMPDIR` on scratch were necessary and sufficient.

### Lock divergence from the Docker mirror — recorded, not a gate failure

The plan requires recording **every** divergence. The six gated packages match;
five transitive dependencies resolved newer on PACE (`pip` picked up releases
published since the 2026-07-10 mirror build, because `container/requirements.lock`
pins direct dependencies only):

| Package | Docker mirror | PACE |
|---|---|---|
| anyio | 4.14.1 | 4.14.2 |
| filelock | 3.29.7 | 3.30.2 |
| hf-xet | 1.5.1 | 1.5.2 |
| narwhals | 2.23.0 | 2.24.0 |
| typer | 0.26.8 | 0.27.0 |

**Not a NO-GO under the ruled criterion**, which names torch / transformers /
GPTQModel / AutoAWQ / lm-eval / datasets — all six match. None of the five
plausibly touches quantization kernels or numerics: async I/O, file locking, the
Xet download backend, a dataframe-compat shim, and a CLI framework. (`hf-xet` is
the backend serving `cas-bridge.xethub.hf.co`, so it is on the C4 mirror byte
path but not on any numerical path.)

**Open question for Amogh, not blocking Stages 1.5–3:** these five are unpinned
and will drift again on any future rebuild, so an image rebuilt after a scratch
purge would not be byte-identical to the one the canaries ran on. If that
matters for the paper's reproducibility claim, hard-pin them in
`container/requirements.lock` — but note that rebuilding the image is itself a
new environment cell, so the pinning decision should be made *before* Stage 3
runs the first quantization job, or deferred until after the mini-grid
completes. `container/environment.lock.pace.txt` records the exact resolve and
is retained separately from the Docker-mirror lock per the runbook.

## Stage 1.5 — C4 transport measured; the mirror is a diagnostic asset (2026-07-17)

### Offline streaming does not resolve from the mirror (job 11223841)

`snapshot_download` cached two probe shards in 29 s, then:

```
OFFLINE_STREAM_FAIL ConnectionError Couldn't reach 'allenai/c4' on the Hub (OfflineModeIsEnabled)
```

**Mechanism.** Three caches, none connected: `snapshot_download` fills the *hub*
cache; `load_dataset(..., streaming=True)` resolves through the Hub API and then
reads via `HfFileSystem` over HTTP; `build_quantized.py` passes `cache_dir=` for
the *datasets* cache. The failure is in **resolution**, not file availability —
`load_dataset` must reach the Hub before streaming opens a byte, so a complete
mirror cannot fix it. The download layer is fine.

The probe was deliberately ordered to test the mechanism on two shards *before*
the ~305 GB download: cost of the negative answer was **644 MB and 36 s**.

### Rates (job 11225540) — decode-bound, not network-bound

| Path | Rows/s | Projected full pass |
|---|---|---|
| Network streaming (registered) | **14,021** | **7.23 h** |
| Local raw `zcat \| wc -l` (gunzip ceiling) | 48,862 | 2.07 h |
| Local JSON builder (mirrored shard) | 17,673 | 5.73 h |

Bytes/row: **2,155** text (uncompressed), **896.1** compressed. Shard 0 is
305 MB compressed (319,308,785 bytes).

Local beats network by only **1.26×**; both are far below the gunzip ceiling.
**JSON decode on one core is the constraint; the 161.8 MB/s link never was.**
See the 2026-07-17 erratum in `docs/PACE_EXECUTION_PLAN_2026-07-15.md`.

### Struck permanently: the local-files loader rewrite

Rewriting `make_stream_factory` to read mirrored shards
(`load_dataset("json", data_files=[...])`) is **struck and no longer tracked**,
by ruling 2026-07-17. Ceiling 1.26× (7.2 h → 5.7 h) against editing fingerprinted
Python on the registered selection path plus a transport-equivalence argument.
Its precondition — network-bound *and* passes > ~30 h — is false on both
clauses. The measurement is the record; do not revisit without new measurements
that overturn it.

### Mirror status: retain until Stage 2 completes, then let it purge

Demoted to diagnostic asset. Its one remaining use: if the verify pass returns
anything other than 364,868,892, per-shard line counts over the mirror localize
the discrepancy (which shards, how many rows) cheaply on embers — impossible
without it. After the artifact passes validate, the 60-day purge may take it.

### Shard-0 observation

Shard 0 holds exactly **356,317 rows**; ×1024 = **364,868,608**, i.e. **284
short** of the registered 364,868,892. Equal shard sizes were never an
assumption anyone made, so this is expected variance rather than a defect. The
verify pass settles `row_count` definitively.

### Pre-committed response to a verification mismatch (ruled 2026-07-17, before the job returned)

Recorded **before** the verify job returned, so the response cannot be shaped by
its result:

- **Exit 5 (count ≠ registered `row_count`) is a HARD STOP and a human
  decision.** The registered permutation universe is built on that constant. No
  constant edits, no "off by 284 is close enough," no resubmission. Bring Amogh:
  the verified count, per-shard line counts from the mirror, and which shards
  deviate from 356,317. The likely resolution is a dated correction recording
  the true count *before any artifact exists* — but that call is made with
  numbers in hand.
- **Exit 4 (a pre-committed abort criterion tripped) stops for reassessment**
  with measurements. Its truncated count is an artifact of the abort and is not
  evidence about `row_count`.

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

## Stage 2 first attempt — latent env.sh sourcing bug, caught by the fail-closed check (2026-07-17)

**Finding.** `prepare_calibration.sbatch`, `build_quantized.sbatch`,
`run_bridge.sbatch`, and `verify_bridge.sbatch` all sourced their environment
with `source "$(dirname "$0")/env.sh"`. Under standard `sbatch`, the batch
script is spooled to a job-specific path on the compute node
(`/var/lib/slurm/slurmd/job<id>/slurm_script`) before it runs, so `$0` never
points back to `scripts/slurm/` — `dirname "$0"` is worthless inside a
`#SBATCH` script. This is a general SLURM property, not a Phoenix-specific
quirk.

**Why the two working Stage 1/1.5 scripts dodged it.** `mirror_c4.sbatch` and
`verify_row_count.sbatch` never source `env.sh` at all — both hardcode
absolute paths directly. Only the untested Stage 2/3/4 scripts used the
dirname trick, and Stage 2 (job `11233525`) was its first real invocation.

**Cost of the failure: 1 second, zero data.** `env.sh` never ran, so
`PROJECT_DIR`/`IMAGE` were unset, apptainer had nothing to bind at
`/workspace`, and the job died with `FATAL: container creation failed: mount
source /workspace doesn't exist`, exit 255, before touching the network or the
mirror. The image-existence fail-closed check in `env.sh` did exactly its job
— no partial artifact, no corrupted calibration state, nothing to clean up.

**Fix (commits `a5dabd1`, `d0ffaa8`, `91f3b13`).** Replaced the sourcing line
in all four scripts with
`source "${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}/scripts/slurm/env.sh"`,
matching `env.sh`'s own default and keeping `env.sh` as the single environment
contract (no duplication). Repo-wide grep confirmed these were the only four
instances of the pattern. Added a `# shellcheck source=` directive per file so
`shellcheck -x` follows and checks `env.sh` itself rather than emitting
SC1091; all four now pass `bash -n` and `shellcheck -x` clean (rc=0), matching
the three untouched sbatch scripts. `logs/` (relative `--output=logs/...`
SBATCH paths land job logs in the project tree) was added to `.gitignore` —
untracked logs were blocking the freeze tool's dirty-worktree check.

**Fix proven before resubmitting the real job.** A throwaway `embers` probe
(outside `scripts/`, not committed) sourced `env.sh` the new way and printed
`PROJECT_DIR`, `IMAGE`, and the image-existence check: all green
(`IMAGE_EXISTS_CHECK=PASS`), 1 s walltime.

**Resubmitted 2026-07-17.** Seed-0 calibration job `11233678` (`--array=0`,
inferno) running; Stage 3 canary pair `11233679` (`--array=0,3`, inferno)
queued `afterok:11233678_*`, per the standing pre-authorization in
`docs/PACE_RUNBOOK.md:113-114`.

## Stage 3 canary pair — two real runtime failures, caught on schedule (2026-07-18)

**Calibration completed clean.** Job `11233678` finished after 15:43:38 wall
time (`retrieval.passes=2`, `retrieval.stream_rows_scanned=729,664,541` = two
full 364,868,892-row sequential C4 scans; the frozen protocol's window=4096
vs. target=128 margin usually needs one pass but did not this time), peak RSS
7,236,216K, 128 samples, artifact `qwen25-1p5b-c4-s0.json`
(`sha256:f0a1ed0a...c38af49`), exit 0:0.

**Canary pair `11233679` failed both array tasks in ~30s each**, before
touching the GPU workload. This is exactly what the canary pause point is
for. Diagnosed CPU-side only (no GPU queue needed) via a short `embers` probe
job, per the standing rule against interpreting anything from the failure
beyond job health:

- **GPTQ (array task 0):** `gptqmodel`'s real import chain
  (`gptqmodel.models.auto` → `definitions.afmoe` → `definitions.internvl_chat`
  → `import torchvision`) fails with `ModuleNotFoundError: No module named
  'torchvision'`. The package eagerly imports every model definition
  including multimodal ones at `import gptqmodel` time, even though this
  project only quantizes a plain text model. `--nv` was already present on
  the sbatch invocation, ruling that hypothesis out immediately. This is a
  missing pinned dependency, not an env-leak or GPU-context issue.
- **AWQ (array task 3):** imports fine, but `model.quantize()`'s Triton JIT
  kernel compile shells out to `gcc` and fails with `FileNotFoundError` on
  `/usr/local/pace-apps/spack/.../gcc-12.3.0-.../bin/gcc` — a host
  spack-managed path that doesn't exist inside the container. Confirmed via
  an `env`-diff probe: without `--cleanenv`, `CC`, `CXX`, and `MODULEPATH`
  leak from the submitting shell straight into the container (`apptainer
  exec` has no `--cleanenv` in any `scripts/slurm/*.sbatch` invocation before
  this fix). The image's own compiler (`gcc 12.2.0` at `/usr/bin/gcc`) is
  fine and never gets used because the leaked `CC` shadows it. Confirmed
  `--cleanenv` still lets `APPTAINERENV_HF_HOME` /
  `APPTAINERENV_HF_DATASETS_CACHE` / `APPTAINERENV_TOKENIZERS_PARALLELISM`
  through — the sanctioned channel is unaffected.

**Fix applied (shell-only, `bash -n` + `shellcheck -x` clean on all seven
touched `.sbatch` files):** added `--cleanenv` to all 12 `apptainer exec`
invocations across `scripts/slurm/`, relying on `APPTAINERENV_*` for
everything the container legitimately needs. This resolves AWQ. It does not
resolve GPTQ — that needs `torchvision` added to the pinned image, which is
an environment-cell change requiring an image rebuild, and is being held for
an explicit decision rather than auto-applied (the same reasoning the plan
already uses for the compiler-missing branch: legal now because no quantized
artifact exists yet, but a rebuild the human signs off on, not one an agent
triggers on its own).

**Hardening landed in the same commit:**
1. `build_gptq`/`build_awq` in `scripts/build_quantized.py` now print the
   full chained `ImportError` traceback (`traceback.print_exception(exc)`)
   before raising the `SystemExit` fail-closed message, so the next real
   failure isn't masked the way this one initially was (the bare
   `SystemExit` swallowed the traceback; the real cause only surfaced by
   bypassing the wrapper in a diagnostic probe).
2. Added `test_pinned_gptqmodel_exposes_expected_api` to
   `tests/test_build_quantized.py`, mirroring the existing
   `test_pinned_autoawq_preserves_pre_tokenized_calibration_ids` pattern
   (`pytest.importorskip("gptqmodel")`, then a real import asserting
   `GPTQConfig`/`GPTQModel` exist) — so the in-image gate stops certifying a
   `sys.modules` monkeypatched fake as proof the runtime works.

**Gate consequence, current transitional state.** Because `gptqmodel` is
genuinely broken in the pinned image right now, the new test *skips*
(doesn't fail) under `pytest.importorskip`. Measured in-image result today:
**54 passed, 1 skipped, 0 failed** (bind-mounted live source tree, matching
how every production job actually runs pytest against the pinned
runtime) — not the `54 passed, 0 skipped` baseline in `AGENTS.md`. That
document intentionally is **not** updated to a final number yet: the skip
correctly documents the real, open GPTQ gap rather than masking it, and the
target (`55 passed, 0 skipped`, or similar) only gets recorded once
`torchvision` lands in a rebuilt image. Anyone re-running
`build_image.sbatch`'s Gate 1 against the current source tree without first
fixing `torchvision` will now correctly hard-fail on the skip — that's
intended, not a regression.

**The lesson.** The unit-test gate (mocked `sys.modules["gptqmodel"]`) only
ever proved the surrounding selection/quantization logic was wired up
correctly against a *fake* module — it could not and did not prove the real
runtime imports on GPU hardware. Only the canary — a real GPU job running
the real pinned dependency — could prove that, and it did exactly what it
was registered to do: fail fast (~30s, zero GPU-hours burned on either task)
before any seed-1/2 or bridge compute was spent on a broken runtime. That
division of labor (fast mocked unit tests for logic, an expensive real-run
canary for runtime truth) is by design, not an accident to fix, and is worth
a sentence in the paper's ops appendix.

## Environment-cell rebuild — torchvision==0.28.0 added to close the GPTQ gap (2026-07-18)

The GPTQ canary gap (missing `torchvision`, above) needed an image rebuild.
Approved as a single environment-cell change because **zero quantized artifacts
exist yet** — the same reasoning the plan uses for the compiler branch. This is
the **last free rebuild**: the pin freezes permanently once the canary produces
its first GPU output.

### Pre-check before touching the def (embers job 11258458, --cleanenv, current image)

Two questions settled before editing, so the rebuild would be one cell, not two:

1. **Compiler already in-image.** Under `--cleanenv`, `/usr/bin/gcc` and
   `/usr/bin/cc` are both `gcc (Debian) 12.2.0` (`step0_rc=0`). `build-essential`
   was always in the def; the AWQ Triton JIT path compiles with the in-image
   compiler now that the leaked host `CC` is gone. **No toolchain addition
   needed — the rebuild is torchvision-only.**
2. **torchvision pairing is exact and does not move torch.** A constrained
   dry-run resolve (`pip install --dry-run --report torchvision torch==2.13.0`)
   reports `Would install torchvision-0.28.0` with `requires_dist: torch (==2.13.0)`
   and torch "already satisfied" at 2.13.0 — i.e. torchvision's own metadata
   pins torch exactly, and pulling it drifts torch by **zero** patch versions.
   Installed from plain PyPI, the same index/method as torch. Pinned in
   `container/requirements.lock` as a hard `==`, never a floating resolve.

### Two build failures, both fail-closed with zero collateral, before the pass

The pinned image is unforgiving by design, and it caught two mistakes on the way:

- **Job 11258508 — `%post` torch-pin assertion (my bug, not a drift).** The
  assertion compared `torch.__version__ == '2.13.0'`, but the runtime string is
  `2.13.0+cu130` (the CUDA-13 local-version tag the pinned wheel has always
  carried; `pip freeze` normalizes it away in the lock, so the lock reads
  `torch==2.13.0`). PEP 440 `torch==2.13.0` matches `2.13.0+cu130`, so torch
  never moved. Fixed to guard the **base** release
  (`torch.__version__.split('+')[0] == '2.13.0'`), which is the correct reading
  of "moved even a patch version."
- **Job 11258600 — `%test` pytest (a latent collision torchvision exposed).**
  `import gptqmodel` → `tokenicer` → `_configure_hf_cache()` does
  `HF_HOME.mkdir(parents=True)` **at import time**. The `%environment`
  `HF_HOME=/scratch/hf_cache` is correct at runtime (jobs bind `/scratch` and set
  it via `APPTAINERENV_HF_HOME`), but during `apptainer build` the `%test` phase
  has no `/scratch` bind and a read-only root → `OSError [Errno 30] Read-only
  file system: '/scratch'`. This was latent while `torchvision` was absent:
  `import gptqmodel` failed early with `ModuleNotFoundError`, so
  `pytest.importorskip` **skipped** the test before `tokenicer` was ever reached.
  Fixed by redirecting `HF_HOME`/`HF_DATASETS_CACHE` to a writable build-local
  `/tmp` path **in the `%test` block only** — runtime is untouched (it overrides
  `HF_HOME` through `APPTAINERENV_*`), and Gate 1 remains the authoritative run
  because it execs pytest with `/scratch` bound. The `%post` pytest already
  passed with gptqmodel importing for real (it uses a writable default cache),
  so the 55-pass was demonstrated before Gate 1 even ran.

Both fixes are runtime-neutral and were folded into the single environment-cell
commit `ffc366c`. The failed-build job logs (`image_11258508.out`,
`image_11258600.out`) permanently record the iteration.

### Gate result — PASS (embers job 11258719, 2026-07-18, 9 min 25 s, exit 0:0)

| Item | Result |
|---|---|
| Gate 1 in-image pytest | **55 passed, 0 skipped, 0 failed** (`rc=0`) |
| Evidence line | `IN_IMAGE_PYTEST_SUMMARY: passed=55 skipped=0 failed=0 errors=0 rc=0 job=11258719 log=…/results/pace_gate/in_image_pytest.log` |
| Gate 2 CPU smoke | exit 0; both analysis summaries regenerated |
| Six gated pins | all match the Docker-mirror lock |
| Build mode | unprivileged |

`AGENTS.md`/`CLAUDE.md` in-image gate and `scripts/slurm/build_image.sbatch`
Gate 1 are updated 54 → **55** to match: `test_pinned_gptqmodel_exposes_expected_api`
now imports gptqmodel for real instead of skipping.

### Both fingerprints — old cell superseded, new cell live

| Cell | Image sha256 | PACE lock | Status |
|---|---|---|---|
| Old (built 2026-07-16) | `09ed767f29e1c0ebb97451b070bc91759301a2d9b63c706511f8b1dcd013418d` | `container/environment.lock.pace.superseded-2026-07-16.txt` | **Built, never produced a quantized artifact, superseded** |
| New (built 2026-07-18) | `9d2bb608c7b54bf71a5d688723d06c38bf36b8849758fcb9e95c1fda7ca9550e` | `container/environment.lock.pace.txt` | **Live** — the pin the canary runs on |

Both lock files are retained in the tree. New-cell resolve diverges from the
old-cell resolve on exactly three lines: `+torchvision==0.28.0` (intended),
`filelock 3.30.2 → 3.31.0`, and `huggingface_hub 1.23.0 → 1.24.0`. The two
transitive drifts are the same unpinned-dependency behavior recorded in the
Stage 1 "Lock divergence" section (requirements.lock pins direct deps only);
neither touches quantization kernels or numerics (a file lock and the HF hub
client), and **all six gated pins match** — not a NO-GO under the ruled
criterion.

**Rationale for the record.** This environment-cell change is clean because no
quantized artifact exists yet; the pin freezes permanently at the first
successful GPU output. This is the last free rebuild — any dependency change
after the canary emits its first checkpoint is a new, un-superseded cell.

> **Freeze-point clarification (ruled by Amogh, 2026-07-18).** The clause above
> — "the pin freezes at the first successful GPU output" — is **superseded**.
> The environment pin freezes at the **first PASSED canary pair**, not at the
> first artifact on disk. A single artifact from a split canary (one method
> succeeds, the other fails) does *not* freeze the cell, because paired-receipt
> verification never ran and the two methods did not come from one proven
> environment. See the cell-3 section below.

## Environment-cell rebuild — gptqmodel/Transformers 5.x `revision=` fix, cell 3 (2026-07-18)

**Why a third cell.** The cell-2 canary pair (`11258797`) split: AWQ seed0
COMPLETED and wrote a 1.1 G artifact, but GPTQ seed0 FAILED at model load with
`TypeError: Qwen2ForCausalLM.__init__() got an unexpected keyword argument
'revision'` (`gptqmodel/utils/hf.py build_shell_model` →
`transformers .../auto_factory.from_config`). The torchvision rebuild (cell 2)
fixed the earlier import gap, letting GPTQ get far enough to hit this next wall:
gptqmodel 7.1.0 forwards `revision=` into `from_config`, which Transformers
5.13.0 rejects.

**Governance applied (per the freeze-point clarification above).** A split
canary does not freeze the cell. The cell-2 AWQ artifact is therefore
**quarantined, not kept**:
`outputs/quantized/qwen25-1p5b-awq4-seed0` →
`qwen25-1p5b-awq4-seed0.cell2-superseded`, never to be read by anything
downstream. Both canaries rerun under the fixed cell 3 so both receipts come
from one environment. **Cell 3 is the genuinely last rebuild: after a passed
canary pair the environment is frozen for the campaign, hard.**

### Diagnosis — no released gptqmodel fixes it (all CPU-side, no GPU)

The failing call path (`build_shell_model` → `AutoModelForCausalLM.from_config`)
is CPU-reachable, so the whole diagnosis ran on `embers` CPU with no GPU queue.

- **Root cause.** gptqmodel 7.1.0's `utils/hf.py:build_shell_model` forwards its
  model-init kwargs straight into `AutoModelForCausalLM.from_config`. It strips
  `device_map`/`_fast_init` at that seam but **not** `revision`. Under
  transformers 5.x, `from_config` passes unknown kwargs into the concrete model
  `__init__`, and `Qwen2ForCausalLM.__init__` rejects `revision`. Older
  transformers tolerated the stray kwarg; 5.13.0 does not.
- **`revision` is inert at that seam.** In `loader.py:from_pretrained`, the
  pinned revision is consumed by `get_model_local_path` (weight/config fetch)
  **before** `build_shell_model` is called; by the time the shell model is
  built, weights are already local and `revision` only governs hub fetches, not
  architecture (which comes from the config object). Stripping `revision` only
  at the `from_config` boundary therefore cannot change which revision is
  fetched.
- **No release fixes it.** The only gptqmodel release after 7.1.0 is **7.2.0**
  (verified against the GitHub tags API — there is no 7.1.1). Its
  `gptqmodel/utils/hf.py` is **byte-identical** to 7.1.0's `build_shell_model`,
  so 7.2.0 does not fix the bug. And the 7.1.0→7.2.0 delta (12 commits) is
  dominated by new model-architecture definitions and touches the
  quantization/model-construction surface (`models/auto.py`, `models/base.py`,
  `models/loader.py`, `models/writer.py`, `utils/structure.py`,
  `looper/stage_layer.py`) — **not** compat-only. Under the decision rule, a
  version bump is off the table on both counts (doesn't fix it; not
  compat-only).
- **Reproduced + confirmed on the pinned image** (embers CPU job `11259695`,
  cell-2 image): raw path raises
  `TypeError: Qwen2ForCausalLM.__init__() got an unexpected keyword argument
  'revision'`; the from_config-boundary shim (pop `revision`) constructs the
  Qwen2 shell model cleanly (`PROBE_SHIM: SUCCESS type= Qwen2ForCausalLM`).

### Chosen fix — a narrow, from_config-boundary compat shim in our code

Per the decision rule's second branch (only path that fixes it involves
un-pinnable upstream change), the fix lives in **our** code, not the runtime:
`scripts/build_quantized.py:_strip_revision_from_shell_model` wraps
`gptqmodel.utils.hf.build_shell_model` to drop **only** `revision` before
delegating (it extends gptqmodel's own existing `device_map`/`_fast_init` strip
by exactly one key). `build_gptq` installs it — idempotently — right before
`GPTQModel.load`; because `loader.from_pretrained` imports `build_shell_model`
from the module at call time, patching the module attribute takes effect. The
`GPTQModel.load(..., revision=...)` call is unchanged, so the pinned revision is
still used for the weight fetch.

**This is a pinned-runtime workaround, not an upstream fix.** It is documented
here and guarded by three tests (`tests/test_build_quantized.py`): two
regression tests proving the shim strips only `revision` and is a no-op
otherwise (run everywhere), and a real CPU-side construction gate
(`test_pinned_gptqmodel_builds_qwen2_shell_model_under_pinned_transformers`)
that asserts the raw path still raises in exactly this shape and the shim
recovers a clean `Qwen2ForCausalLM` construction — closing the gap the canary
exposed (the import test passed while construction failed). In-image gate count
rises **55 → 58**.

### Gate result — PASS (embers job 11259853, 2026-07-18, 10 min 19 s, exit 0:0)

| Item | Result |
|---|---|
| Gate 1 in-image pytest | **58 passed, 0 skipped, 0 failed** (`rc=0`) |
| Evidence line | `IN_IMAGE_PYTEST_SUMMARY: passed=58 skipped=0 failed=0 errors=0 rc=0 job=11259853 log=…/results/pace_gate/in_image_pytest.log` |
| Gate 2 CPU smoke | exit 0; both analysis summaries regenerated |
| Six gated pins | all match the Docker-mirror lock |
| Build mode | unprivileged |

The revision shim is bind-mounted source (`scripts/build_quantized.py`), so it is
not baked into the pinned pip environment — the **PACE lock is byte-identical to
cell 2** (same `requirements.lock`, same `flipeval.def`; the build rewrote
`container/environment.lock.pace.txt` with no diff). The image sha differs only
because the source tree baked by `%files` changed (the shim + tests).

### Three cells — cell 2 superseded, cell 3 live and frozen

| Cell | Image sha256 | PACE lock | Status |
|---|---|---|---|
| Cell 1 (2026-07-16) | `09ed767f…013418d` | `environment.lock.pace.superseded-2026-07-16.txt` | Built, no artifact, superseded |
| Cell 2 (2026-07-18) | `9d2bb608…7ca9550e` | `environment.lock.pace.txt` (identical to cell 3) | **Superseded** — produced only the quarantined split-canary AWQ artifact, which does not freeze the cell |
| Cell 3 (2026-07-18) | `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` | `environment.lock.pace.txt` | **Live** — the revision-shim cell the paired canary reruns on |

Cell 2's PACE resolve equals cell 3's (no dependency change), so no separate
superseded lock file is needed — the retained `environment.lock.pace.txt` is the
resolve for both. The tracked image checksum `container/flipeval.sif.sha256` now
records the cell-3 sha. **Cell 3 is the genuinely last rebuild: it freezes at the
first PASSED canary pair (per the clarification above).**
