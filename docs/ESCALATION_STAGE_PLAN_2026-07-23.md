# Escalation-Stage Plan — 7B/8B Confirmatory Cells (2026-07-23)

**Status: PLAN FOR REVIEW. No job is submitted under this document until Amogh
confirms the budget.** Requested as the first deliverable of the escalation
ruling (Amogh, 2026-07-23), which affirmed ESCALATE = TRUE
(`docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md`) and authorized construction
of the deferred cells under the full standing discipline.

This plan changes no frozen protocol. It executes the confirmatory cells the
frozen H3 grid already defines and the escalation rule already triggered. The
eight-cell H3 rule is applied once, mechanically, only when all eight cells
exist and Amogh gives the go — no H3 verdict appears anywhere in this document.

---

## 1. Scope — the four new cells

The deferred half of the registered eight-cell confirmatory set
(`PREREGISTRATION.md` § "H3 Decision Rule"):

`{Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct} × {MMLU, GSM8K}`

at 4-bit, GPTQ and AWQ, calibration seeds `{0,1,2,3,4}`, paired C4 calibration
per the registered sampling algorithm. Same benchmarks, prompts, chat-template-on
discipline, and item sets as the completed four cells.

**Models at their pinned revisions** (`configs/main_grid_manifest.yaml`, frozen
2026-07-13):

| tag | model_id | revision |
|---|---|---|
| qwen25-7b | Qwen/Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` |
| llama31-8b | meta-llama/Llama-3.1-8B-Instruct | `0e9e39f249a16976918f6564b8830bc894c89659` |

C4 calibration revision `1588ec45…`; MMLU revision `c30699e8…`; GSM8K revision
`740312ad…` — all as used for the completed cells.

---

## 2. Job inventory

Counts are exact; the structure mirrors the mini-grid one-model-at-a-time,
one-task-per-eval-job layout that is already proven.

| class | count | resource | queue | notes |
|---|---|---|---|---|
| **Canary pairs** | 2 (1 per model, `--array=0,3`) | A100 | inferno | GPTQ+AWQ seed-0 build canary. **Hard stop on failure**, Stage 3 discipline. |
| **Calibration artifacts** | 10 (2 models × 5 seeds) | CPU 8c/64G | embers | C4 stream; GPTQ-`s` and AWQ-`s` share one artifact. **No A100 draw.** |
| **Quantized builds** | 20 (2 models × {GPTQ,AWQ} × 5 seeds) | A100 | inferno | receipts at job time (`write_receipt.sh`). |
| **FP16 reference (gates)** | 2 array jobs → 4 (model×task) | A100 | inferno | `mmlu_pilot` custom task + date-pinned entry, **identity-first** (§ 4). |
| **Prompt-identity probe** | 1 | A100 (tiny) | inferno | precondition; zero diffs before any reference run. |
| **Eval cells** | 44 (2 models × 11 variants × 2 tasks) | A100 | embers `--array`, `--requeue` | one task per job, `--only-method/--only-task`. |
| **Validator** | 1 | CPU 4c/32G | embers | fail-closed over the complete new-cell set. |

Total A100 jobs: 2 + 20 + 5 + 44 = **71**; plus 10 CPU calibration + 1 CPU
validator.

---

## 3. Wall-time and A100-hour estimate

Estimates scale the **measured** mini-grid costs to the larger models. Basis:
completed mini-grid eval = 44 cells, 66.8 A100-h total (median 1.04 h, max
4.11 h); 3B builds GPTQ 6.6 min / AWQ 12.6 min mean; calibration 14–25 h CPU
wall each. Scaling factor for 7B/8B is taken as **≈2.5×** on generation-bound
work (parameter ratio 7B/1.5B ≈ 4.7, 8B/3B ≈ 2.3; batch_size 1 makes it roughly
linear in forward-pass cost, tempered by A100 headroom).

| class | per-job | jobs | A100-h subtotal |
|---|---|---|---|
| Canaries | ~1 h (fails in ~30 s if broken) | 2 | ~2 |
| Builds | GPTQ ~0.3 h, AWQ ~0.6 h | 20 | ~9 |
| FP16 reference | MMLU ~2 h, GSM8K ~6 h | 4 | ~16 |
| Identity probe | ~0.3 h | 1 | ~0.3 |
| Eval — MMLU (choice-scored) | ~2.5 h | 22 | ~55 |
| Eval — GSM8K (generative) | ~7 h | 22 | ~154 |
| **Subtotal** | | | **~236** |
| Rerun/preemption margin (~35 %) | | | ~83 |
| **Total A100-hours** | | | **~320 (range 260–360)** |

**CPU (calibration), separate budget, not A100:** 10 artifacts × ~15–25 h ≈
150–250 CPU-node-hours on embers. Dominated by the C4 scan, largely
model-independent. Serialize or parallelize per scratch/network state.

**The GSM8K generative half is the entire cost story** — ~154 of ~236 A100-h
before margin. Two things bound it: batch_size is pinned at 1 in
`configs/pace_minigrid_h3.yaml`, and 8B generation at bs=1 is slow. This is the
number most worth Amogh's attention, and the canary's generation-speed reading
is what will tighten it before the fan-out commits.

---

## 4. FP16 gates — identity-first, Amendment 3 as the starting point

Amendment 3's correction is this stage's **precondition**, not a lesson learned
after the fact:

1. Extend the `mmlu_pilot` custom task to the two new models — it is
   model-independent (system-message-empty + `"Question: "` stem), so it already
   applies; only the tokenizers differ.
2. Run the **prompt-identity probe** on qwen25-7b and llama31-8b against their
   own FP16 eval cells *before* the reference runs. Zero byte-diffs (prompt-hash
   match) is the gate. Any diff stops and returns to Amogh. Llama-3.1-8B injects
   a date like Llama-3.2-3B, so the date-pinned entry point is used and the pin
   is set to **the date those cells' FP16 baselines are actually produced** —
   captured from the cell, never assumed, never the calendar date at rerun time.
3. **Pre-commit the tolerance rule before the reference jobs run.** The frozen
   § 3 arithmetic (`SE`, `half = max(0.05, 2·SE+0.03)`, clip) is unchanged and
   already committed; this plan re-affirms it applies verbatim to the new cells.
   No new tolerance term, no per-cell adjustment.
4. Derive all four new gates mechanically, **all-or-nothing**, and commit
   together with the in-image gate green (170 passed) and a freeze refresh — the
   config never passes through a half-filled state.

---

## 5. Queue strategy

- **inferno (charged)** for the **critical path**: canaries, builds, FP16
  reference, identity probe. These gate everything and should not wait behind
  the free queue. Bounded, short jobs.
- **embers (free, preemptible)** for the **44 eval cells** and the validator:
  high aggregate hours, individually restartable, `--requeue` set so preemption
  costs only wall time. This is where the ~200 A100-h lives, and it is the right
  place for it.
- `--exclude` is treated as unavailable (inert on this cluster; incident 11);
  placement is verified post-submission with `scontrol` if ever needed.

---

## 6. Sequence and gates

1. **Canary pair per model, hard stop.** No build, calibration fan-out, or eval
   proceeds for a model whose canary fails. Stage 3 discipline unchanged.
2. Calibration fan-out (embers CPU) → 10 artifacts, receipts at job time.
3. Builds (inferno) → 20 checkpoints, receipts at job time, acceptance sweep.
4. FP16 reference identity-first (§ 4) → 4 gates committed all-or-nothing.
5. Eval fan-out (embers, `--array`, `--requeue`) → 44 sealed JSONLs.
6. **Validator fail-closed** over the complete new-cell set. Nonzero exit stops.
7. **Blindness holds:** the four new cells are confirmatory and **sealed** until
   their validator passes **and Amogh gives the go**. Only then is the
   eight-cell H3 rule applied once, mechanically, over all eight cells. No
   session states an H3 verdict before that.

---

## 7. Open feasibility items the canary resolves (not blockers to the plan)

- **8B AWQ host-RAM.** 3B AWQ peaked ~50 GB RSS; 8B may exceed the 64 GB request.
  The canary's build receipt reports peak RSS; if it approaches the ceiling, the
  build jobs move to 128 GB. Flagged, not guessed.
- **GSM8K 8B generation wall.** The canary is a build canary, but a short
  generation-speed reading on the seed-0 FP16 8B (off the confirmatory item set,
  the incident-10 probe pattern) would replace the ~7 h/cell estimate with a
  measurement before 22 GSM8K cells commit. Recommended, cheap, optional.

---

## 8. Budget request

**Requested authorization: ~320 A100-hours (bound at 360), plus ~150–250
CPU-node-hours for calibration on embers.**

For comparison, the mini-grid's own realized eval cost was 66.8 A100-h over 44
cells on models 2–5× smaller; the ~2.5× scaling and the generative GSM8K half
are what carry this to ~320. The execution plan
(`docs/PACE_EXECUTION_PLAN_2026-07-15.md`, totals table) scoped the 7B/8B
campaign as a *separate* Nov–Dec effort outside the mini-grid's ~210 A100-h
budget, so this is additive by design, not an overrun.

**On confirmation of this budget, the ruling authorizes execution without
further per-job approval**, under the gates of § 6. The single points that still
return to Amogh are: any canary failure (hard stop), any identity-probe diff
(§ 4), and the post-validator go before the H3 adjudication.
