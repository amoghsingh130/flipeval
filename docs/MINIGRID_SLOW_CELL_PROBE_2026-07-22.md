# Mini-Grid Slow-Cell Probe — qwen25-1p5b / gptq_s3 / gsm8k (cell `11350246_9`)

Executes rulings 1–2 of 2026-07-22 and the resubmission ruling of the same date
(Amogh, advisory session). Records an inspection performed **strictly off the
confirmatory item set**.

**Outcome: the probe matched neither pre-authorized branch, and the cause is
hardware.** Generation speed for the suspect build is normal (branch (b) not
triggered) *and* generation does not run to the token cap any more than its
control does (branch (a)'s second condition not met). The evidence isolates the
fault to one physical GPU. The cell has been resubmitted unchanged and is
running at normal speed on the suspect node's *other* A100, which confirms the
diagnosis directly (§ 8). The authorized `--exclude` was silently discarded by a
site plugin and is inert on this cluster (§ 8.1).

**No accuracy was read, from this cell or any other.** The probe records
timings, token counts, and stop reasons only; generated text, gold answers, and
correctness are never touched.

## 1. What was observed in situ

Cell `11350246_9` (Qwen2.5-1.5B, `gptq_s3`, GSM8K) ran at ~66 s/item from the
first item — 290 of 1,000 items in 5 h 21 m — against 6–8 s/item for its four
GPTQ siblings. Projected completion ~16.5 h against a 12 h wall, with output
written only at end of run, so the wall kill would have destroyed the cell.

Cancelled per ruling 1 at 05:39:50 elapsed, `CANCELLED`, no partial output (as
expected by construction).

## 2. Free on-disk evidence — both cheap causes eliminated

**Load path is clean.** The s3 MMLU cell is choice-scored, no generation:

| Qwen MMLU cell | wall |
|---|---|
| `gptq_s0` | 1:02:19 |
| `gptq_s1` | 0:46:31 |
| `gptq_s2` | 0:46:10 |
| **`gptq_s3`** | **0:44:43** |
| `gptq_s4` | 1:02:22 |

s3 is the second-fastest GPTQ MMLU cell. The slowness is generation-specific.

**Build is clean.** `build-qwen25-1p5b-gptq4-seed3.json`: 5 m 47 s wall
(siblings 4:19–5:47), 10.4 GB peak RSS (siblings 7.3–10.8 GB), exit 0, same
`image_sha256` `8260d04c…` as all five, own calibration artifact
`qwen25-1p5b-c4-s3.json` as registered. On disk the artifact is 1,161,317,309 B
against siblings' 1,161,317,307–317 B with an identical file set.

## 3. The probe

Job `11357902`, cell-3 image, A100, same harness entry points
(`load_model_and_tokenizer`, `render_prompt`, `model.generate` kwargs) as
`pilot_eval` uses, so tokens/sec is comparable to the cell that stalled.

Blindness contract, enforced in code rather than asserted:

- Items are GSM8K test indices **1000–1011**. The registered cell is
  `limit: 1000`, i.e. indices 0–999. The probe raises rather than run if handed
  a start index below 1000.
- Generated text is never printed, stored, or returned; `answer` is never read;
  correctness is never computed.
- Recorded quantities: prompt tokens, new tokens, wall seconds, tokens/sec,
  stop reason.

Script `~/scratch/flipeval/work/gen_speed_probe.py`, sha256
`e257ef675791bbefd7fdd0f3c89f019af5d3650e5583ddf66a85acd8df81e999`. Deliberately
staged outside the fingerprinted tree per ruling 4 (no source changes mid-grid);
it should be committed after the campaign if this diagnostic is to be reusable.

## 4. Probe result

12 items per build, warm-up excluded, `gptq_s2` as sibling control.

| build | tok/s | mean new tokens | mean s/item | stop=cap | kernel |
|---|---|---|---|---|---|
| `gptq_s3` (suspect) | **22.09** | 187.0 | 8.46 | 3/12 | `TorchLinear` |
| `gptq_s2` (control) | **22.03** | 174.6 | 7.92 | 2/12 | `TorchLinear` |

Control/suspect tokens-per-sec ratio **1.00**. Same kernel on both.

Neither branch fits:

- **Not (b).** Tokens/sec is not degraded — it is identical to the control to
  three significant figures.
- **Not (a).** Generation does not run to the cap. 3 of 12 items hit it against
  2 of 12 for the control; mean generated length differs by 7%, not the ~8×
  that the 58 s/it figure would require.

At the probe's measured 8.46 s/item, the full 1,000-item cell projects to
**~2.4 h** — in family with its siblings' 1:42–2:20, and nothing like 16.5 h.
**The build is exonerated. The slowness did not reproduce.**

## 5. Where that leaves the cause

In situ the cell averaged 66.4 s/item ≈ **2.8 tok/s**. On demand the same build
does 22.09 tok/s. That is a ~7.8× shortfall in the cell, not in the artifact.

Node contention is ruled out by the co-tenancy record. `atl1-1-02-018-27-0` has
**2** A100s, and cell `_9` (04:18:01–09:57:51) always had exactly one of our
cells on the other GPU — all of which ran at normal speed:

| task | window | wall | note |
|---|---|---|---|
| `_5` | 03:37:14–05:19:55 | 1:42:41 | GSM8K, normal |
| `_18` | 05:20:05–05:58:46 | 0:38:41 | MMLU, normal |
| `_22` | 05:59:16–06:22:44 | 0:23:28 | normal |
| `_28` | 06:22:58–07:08:10 | 0:45:12 | normal |
| `_33` | 07:08:25–09:08:16 | 1:59:51 | GSM8K, normal |

Same node, same wall-clock window, second A100, normal throughput. This
isolates the anomaly to **the individual GPU cell `_9` was bound to**, not to
the node, the co-tenant, the image, or the build.

Weak corroboration: an `nvidia-smi` query issued into the running allocation
(step `11350246_9.1`, 09:49:31) returned its CSV header and **no GPU rows**.
Not conclusive on its own, but consistent with a device in a bad state.

## 5a. Closure of the earlier generate-to-cap framing

The ruling that authorized this probe raised, as its hypothesis (a), that the
cell might be generating to the `max_new_tokens` cap on every item — the model
never emitting a stop sequence — and noted this would rhyme with the shape of
the bridge's slow `awq_s1` GSM8K half. That framing was reasonable on the
arithmetic available at the time (58 s/it ≈ 8× the siblings, and 256 ≈ 8× a
typical short GSM8K answer).

**The probe falsified it.** Tokens-per-sec ratio 1.00; mean generated length
within 7% of the control; stop-at-cap 3/12 against the control's 2/12. There is
no generate-to-cap behaviour to explain, in this cell or this build.

This is recorded explicitly so the suggestive framing does not outlive its
refutation. **The anomaly was hardware, full stop.** It carries no information
about H3, about the `gptq_s3` artifact, or about quantization seed behaviour,
and it must not be cited as though it did.

The bridge's `awq_s1` slow half remains **open as its own unexplained entry**.
It is not retro-explained by this finding: it ran on different hardware at a
different time and was never probed. Nothing here should be read back onto it.

## 6. Defect found while probing — stale `pilot_eval` in the image

The probe's first attempt (`11357773`) died in 28 s:

```
ValueError: unknown quantization backend: gptqmodel_torch
  /usr/local/lib/python3.11/site-packages/pilot_eval/modeling.py
```

The image carries a **stale `pilot_eval` baked into site-packages**, predating
the `gptqmodel_torch` backend that the entire mini-grid uses.

**The grid is not affected.** `python -m pilot_eval.run` under `--pwd /workspace`
puts cwd at `sys.path[0]`, so `/workspace/pilot_eval` shadows the stale copy —
and had it not, all 44 cells would have failed on this exact `ValueError`
instead of 38 completing with exit `0:0`. The probe failed because launching a
script *by file path* puts the script's own directory at `sys.path[0]` and never
adds cwd.

The hazard is that the correct module is selected by implicit `sys.path`
ordering, with nothing that complains if it changes. A future job launched by
file path gets the stale copy; a stale copy that happens not to raise would run
different code under a registered method name. The probe now asserts
`pilot_eval.__file__` resolves under `/workspace` and refuses to run otherwise.

**Post-campaign list, priority position** (ruled 2026-07-22): the image is to be
rebuilt without the stale copy. Shadowing is not a fix — an image whose fallback
import path silently runs old code is a landmine regardless of whether anything
currently steps on it. The probe's `__file__` assertion is the interim guard
only. **Not actioned mid-grid** (ruling 4).

## 7. Rest of the array

38 of 44 cells `COMPLETED` `0:0`; the 5 still running are all Llama GSM8K at
10–17 s/item, projecting 3.5–4.5 h against the 12 h wall. Every completed file
is at its exact expected count (14,042 MMLU / 1,000 GSM8K). No tracebacks, OOMs,
or preemptions anywhere in the array.

## 8. Resubmission and cell provenance

Resubmitted as job **`11358057_9`**, array index 9 of the unmodified
`scripts/slurm/run_minigrid.sbatch`, which resolves by the frozen index map to
`model=qwen25-1p5b method=gptq_s3 task=gsm8k`.

**Configuration is the registered one, unchanged.** Same script, same
`configs/pace_minigrid_h3.yaml`, same 12 h wall — the 2.4 h projection of § 4
needs no extension.

**The intended operational deviation, `--exclude=atl1-1-02-018-27-0`, was
authorized and passed — and did not take effect.** Its evidence base, all from
§ 5, was:

- The in-situ 7.8× shortfall (2.8 tok/s) vanishes on demand (22.09 tok/s, ratio
  1.00 against the sibling control).
- Cells on the *twin* A100 of the same node, in the same wall-clock window, ran
  at normal speed throughout (`_5`, `_18`, `_22`, `_28`, `_33`).
- `nvidia-smi` into the live allocation returned its CSV header and no GPU rows.

Node selection is operational scheduling, not registered content, so it changes
nothing the preregistration governs.

### 8.1 `--exclude` is inert on this cluster

`sbatch` accepted the flag, returned a job id, and discarded it. The submitted
job records a *different* node than the one passed:

```
ExcNodeList=atl1-1-01-007-2-0        # not the node passed
NodeList=atl1-1-02-018-27-0          # the node that was excluded
```

Cause: PACE runs a site `job_submit` Lua plugin (`JobSubmitPlugins = lua`) that
**overwrites** `ExcNodeList` rather than merging into it. The three mini-grid
cells still running, submitted with no `--exclude` whatsoever, carry the
identical value `atl1-1-01-007-2-0` (`11350246_35`, `_37`, `_43`).

**Treat `--exclude` as unavailable here.** It is a control that reports success
while doing nothing, which is the failure class this project already guards
against in its test-count gate. Any future placement constraint must be
**verified after submission** (`scontrol show job <id>` for `NodeList`) rather
than assumed from a clean `sbatch` exit. This paragraph exists so the next
session does not re-derive it from a wasted run.

### 8.2 What happened instead, and why it is the better evidence

The cell relanded on `atl1-1-02-018-27-0` — the suspect node — and **ran at
normal speed**: 29 items in 4 m 17 s, 6.68 s/it, projecting ~2 h against the
siblings' 1:42–2:20 and § 4's 2.4 h estimate.

The node has 2 A100s and this run drew the other one. That is a cleaner result
than the exclusion would have produced: the same node, the same image, the same
build, the same registered configuration, differing only in which physical
device the job bound to — 66.4 s/item before, 8.9 s/item now. A run on a
different node would have left node-level causes formally open. This one does
not.

**The fault was one physical GPU.** § 5's diagnosis is confirmed, and confirmed
by accident rather than by the mitigation.

Completion at an in-family wall time is a job-health observation, not an
accuracy one.
