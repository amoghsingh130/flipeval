# Bridge Decision Record — Qwen2.5-1.5B chat bridge

**STATUS: SIGNED — ACCEPTED, 2026-07-20, by Amogh Singh.** See § Sign-off for
the verbatim ruling. Drafted by agent 2026-07-20; the runbook (§ bridge)
requires this record to be written by a human after the validator passes, and
the validator deliberately leaves it unwritten
(`decision_record_written: false`).

## Decision requested

Accept the Qwen2.5-1.5B GPTQ/AWQ chat bridge as operationally valid, closing
Stage 4 — or reject/hold.

## What ran

| item | value |
|---|---|
| bridge array | `11285959_1..6` (6 quantized method-jobs), all COMPLETED exit `0:0` |
| validator | `11285960`, COMPLETED exit `0:0`, 2 s |
| fp16 baseline | carried forward from `11262391_0` (COMPLETED, 11:31); its JSONLs were untouched by the resubmit and the validator re-checked them |
| config | `configs/pace_bridge_chat.yaml` |
| image | cell 3, sha256 `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` |
| run dir | `results/qwen25_1p5b_bridge_chat/` (14 JSONLs + manifest + summary) |

## Validator result — PASS

`bridge_validation_summary.json`: `"passed": true`, `"errors": []`, 114 checks,
all `true`. Full text is in the bundle; the summary shape is:

- **Manifest** — method coverage, task coverage, invocation history: pass.
- **Per-file structure (14 files)** — exact record counts (MMLU 400, GSM8K 200),
  unique item IDs, record labels matching filename, chat prompts in use: pass
  for all 14.
- **Item/gold/prompt identity vs baseline** — all 7 methods × 2 tasks: pass.
- **Pinned model revision declared on baseline**: pass.
- **Calibration receipts** — all 6 checkpoints match the frozen protocol and the
  bridge config's provenance: pass.
- **Seed pairing** — seeds 0/1/2 each have both GPTQ and AWQ receipts, and the
  GPTQ/AWQ calibration artifacts are byte-identical within each seed: pass.

### FP16 gates vs registered ranges

| task | measured baseline | registered range | verdict |
|---|---|---|---|
| MMLU | **0.430000** | [0.365, 0.465] | inside |
| GSM8K | **0.615000** | [0.55, 0.65] | inside |

Both sit comfortably interior, not at an edge. These are the only accuracy
numbers in this record; per the runbook and CLAUDE.md, no quantized-model
accuracy has been inspected or characterised, and this record makes no claim
about compression quality. `"interpretation": "Operational bridge validation
only; not an H3 analysis."`

## How the earlier failure was resolved

The 2026-07-19 bridge attempt (`11262391_1-6`) failed all six quantized tasks at
model load: GPTQ wanted `optimum` (absent from the frozen cell-3 lock), AWQ hit
missing Marlin kernels. That was option **B/C** of the recorded fork — a code and
config change inside the frozen cell, not a new environment cell. Landed as:

- `a8219e3` — EXLLAMA_V2 recorded as SIGILL on cell-3 hardware; kernel disqualified.
- `f70de59` — quantized eval routed through native loaders with explicit kernel
  selection, bypassing the `transformers` HfQuantizer path.
- `98b013e` — load info recorded via `record_load_info` rather than `merge_manifest`.
- `e76e23a`, `fefd37e` — freeze refreshes.

The frozen cell 3 was **not** broken: no dependency changed, so the canary-frozen
environment still governs and no re-canary was owed. Kernels actually used are
recorded per job: `gptqmodel_torch` / `TorchLinear` for GPTQ, `awq_gemm` /
`WQLinear_GEMM` for AWQ (kernel is a registered nuisance variable and appears in
every run manifest).

## Observations for the record (job health only)

1. **Wall-time outlier, `11285959_5` (awq_s1): 2 h 07 m vs 22–30 m for the other
   five.** Confined to the GSM8K half (its MMLU JSONL landed at 23:34 with the
   pack; GSM8K at 01:30). Same node class, same backend/kernel as awq_s0, same
   64 GB/8 CPU request, exit `0:0`, no errors in `.err`. All mechanical checks on
   its outputs pass, including 200 records and item/gold/prompt identity. Flagged
   as unexplained-but-clean; **not** diagnosed further, because a plausible
   explanation would require looking at generation content, which is out of
   bounds pre-sign-off. Worth resolving before mini-grid fan-out, where it would
   multiply across cells.
2. **GPTQ `TorchLinear` throughput** remains the open mini-grid planning item
   logged in `cb8ebf3`. The bridge is small enough that it did not bind here.
3. **Calibration artifacts live only in scratch** (60-day purge). They are now
   captured in the archive bundle below, which is the durable copy.

## Archive bundle

`results/bridge_run_20260720.tar.gz`
sha256 `26497dc3d81b0eaeccf34945a7baea75a7d22bbe4431edd1ecadaa5c3a657eac`
(4.7 MB, 43 files, each hashed in the bundle's own `MANIFEST_SHA256.json`)

| bundle path | contents |
|---|---|
| `config/` | `pace_bridge_chat.yaml` |
| `calibration_artifacts/` | `qwen25-1p5b-c4-s{0,1,2}.json` (rescued from scratch) |
| `calibration_receipts/` | 6 × `calibration_manifest.json`, one per checkpoint |
| `jsonls/` | all 14 bridge JSONLs |
| `validator/` | `manifest.json`, `bridge_validation_summary.json` |
| `environment/` | `environment.lock.pace.txt`, `requirements.lock`, `flipeval.sif.sha256` |
| `slurm_logs/` | bridge `_1..6` `.out`/`.err`, verify `.out`/`.err` |

## Recommendation

**Accept.** Every registered operational criterion passed, both FP16 gates are
interior, seed pairing is byte-exact, and the one anomaly is a wall-time outlier
with clean outputs. The awq_s1 timing question is worth a look before mini-grid
fan-out but does not undermine bridge validity.

Accepting this record closes Stage 4. It does **not** authorise the mini-grid or
the main grid: `STATUS.md` still lists unresolved main-grid implementation items,
and the WikiText-2 protocol blocker (`docs/WIKITEXT2_PROTOCOL_BLOCKER.md`) still
requires a dated amendment in `PREREGISTRATION.md` before the first main-grid
job — and mini-grid checkpoints are main-grid cells, so it lands before mini-grid
fan-out, not after.

## Sign-off

**ACCEPTED.** Signed by **Amogh Singh**, 2026-07-20, verbatim:

> Bridge decision record SIGNED by Amogh Singh: the validator passed all
> registered operational criteria, FP16 gates sit within the corrected ranges,
> and the paired calibration receipts verify across all three seeds and both
> methods. The bridge is accepted as the operational canary for the mini-grid.

**Results-inspection basis.** The stated grounds are validator output only —
registered operational criteria, the two FP16 baseline gates, and receipt
pairing. No quantized-model accuracy was inspected by the agent in preparing
this record, and none appears in it. This line records the basis as stated; it
is not an attestation made on Amogh's behalf.

**Scope of the acceptance.** This closes Stage 4 and establishes the bridge as
the operational canary for the mini-grid. It does not by itself authorise
mini-grid fan-out, which remains gated on the prerequisites listed above and
enumerated in `docs/PACE_EXECUTION_PLAN_2026-07-15.md` § Stage 5 — chiefly the
WikiText-2 dated amendment to `PREREGISTRATION.md` (whose Dated Amendments
section reads "None." as of this commit) and the Llama-3.2-3B FP16 operational
acceptance ranges required by `docs/MINIGRID_REGISTRATION_2026-07-15.md` § 2
before any quantized Llama-3.2-3B result exists.

---
*Drafted by Claude Code 2026-07-20; signed by Amogh Singh the same day.*
