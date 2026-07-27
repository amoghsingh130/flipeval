# Campaign Incident Log

**Living operational document.** Not a registration, not a frozen file, and
outside the source-state fingerprint (`docs/` is not in `INCLUDED_PATHS` /
`INCLUDED_TREES` of `scripts/freeze_prepace.py`). No test gate or freeze refresh
is owed for edits here. Append new entries; do not rewrite closed ones except to
add a correction block in place.

**Scope.** One entry per operational incident — a defect, a false alarm, a
failed control, or a stop — that cost time, changed a procedure, or would have
corrupted a record if it had gone unnoticed. Scientific rulings live in their
own dated documents and are cited from here, not restated.

**Evidence rule.** Every entry is written from committed artifacts: correction
memos, probe documents, `sbatch` headers, job logs, `sacct`, and commit
messages. Where an incident survives only in a job log and a script header
rather than in a memo, the entry says so and cites those primary records
directly. Nothing here is written from recollection.

**The last line of each entry** — *"Without the gate"* — is a counterfactual,
written to be arguable rather than rhetorical. Where the honest answer is "it
would have been caught later anyway", the entry says that.

---

## Index

| # | Date | Incident | Caught by |
|---|---|---|---|
| 1 | 2026-07-18 | Canary pair: GPTQ `torchvision` import, AWQ host-`gcc` env leak | Stage 3 GPU canary |
| 2 | 2026-07-21 | `fewshot: 1` ran three exemplars, not one | Source inspection during mini-grid prep |
| 3 | 2026-07-21 | `fewshot_as_multiturn` auto-enabled under a chat template | FP16 gate reference run inspection |
| 4 | 2026-07-21 | `strict-match` voided 617 of 1,000 GSM8K rows | The gate the metric produced |
| 5 | 2026-07-21 | Atlas F1/F2 population defects (+F4, F5) | Commissioned independent spot-check |
| 6 | 2026-07-21 | Calibration operational receipts never written | Plan-line audit against `results/` |
| 7 | 2026-07-22 | Receipt writer: `sacct` array-index trap and MaxRSS settling race | Asymmetric array probe, by construction |
| 8 | 2026-07-22 | Llama canary AWQ receipt carried task 0's resources | Pairwise comparison of the two receipts |
| 9 | 2026-07-22 | Six build receipts predate the receipt writer | Acceptance sweep over receipt fields |
| 10 | 2026-07-22 | One sick A100 ran a cell at 66 s/item | Wall-time comparison against siblings |
| 11 | 2026-07-22 | `sbatch --exclude` accepted and silently discarded | Post-submission `scontrol` verification |
| 12 | 2026-07-22 | Stale `pilot_eval` baked into the image's site-packages | Probe launched by file path instead of `-m` |
| 13 | 2026-07-22 | Missing `/scratch` bind read as a code regression | Rerun with the bind restored |
| 14 | 2026-07-21 | In-image test-count expectation stale at 145 vs 161 | Gate run that should have failed and could not |
| 15 | 2026-07-22 | Harness-sensitivity preflight FAIL; config-churn array dead on dependency | The preflight, fail-closed by design — **RESOLVED, probe defect** |
| 16 | 2026-07-22 | Llama-3.2-3B FP16 MMLU baseline below its registered gate | The registered mini-grid validator — **RESOLVED 2026-07-23** |
| 17 | 2026-07-23 | Sensitivity condition REF would have run as a duplicate of A | Rebuild inspection after the preflight reconciliation |
| 18 | 2026-07-23 | Qwen-7B AWQ build hit two distinct memory ceilings (40 GB device, then 64 GB host) | The escalation build canary, twice |

---

## 1. Canary pair failed both tasks in ~30 s each (2026-07-18)

**What surfaced.** Stage 3 canary pair `11233679` (`--array=0,3`) failed both
array tasks in roughly 30 seconds each, before either touched the GPU workload.

**What caught it.** The Stage 3 GPU canary itself — a registered pause point
that runs the real pinned dependencies on real GPU hardware before any seed-1/2
or bridge compute is spent. It fired exactly where it was placed.

**Root cause.** Two independent faults, one per task:

- **GPTQ (task 0):** `gptqmodel` eagerly imports every model definition at
  `import gptqmodel` time, including multimodal ones
  (`gptqmodel.models.auto` → `definitions.afmoe` → `definitions.internvl_chat` →
  `import torchvision`). `torchvision` was not in the pinned image, so the import
  chain died with `ModuleNotFoundError` even though this project quantizes only
  a plain text model. `--nv` was already on the invocation, ruling out the
  GPU-context hypothesis immediately.
- **AWQ (task 3):** imports succeeded, but `model.quantize()`'s Triton JIT kernel
  compile shelled out to `gcc` and failed with `FileNotFoundError` on a host
  spack-managed path (`/usr/local/pace-apps/spack/.../gcc-12.3.0-.../bin/gcc`)
  that does not exist inside the container. An `env`-diff probe confirmed the
  mechanism: with no `--cleanenv` on any `apptainer exec` invocation, `CC`, `CXX`
  and `MODULEPATH` leaked from the submitting shell into the container, and the
  leaked `CC` shadowed the image's own working `/usr/bin/gcc` 12.2.0.

**Resolution.** `--cleanenv` added to all 12 `apptainer exec` invocations across
`scripts/slurm/`, which resolved AWQ; `APPTAINERENV_*` was confirmed to still
pass the sanctioned variables through. GPTQ needed `torchvision==0.28.0` in the
image, which is an environment-cell change, so it was **held for an explicit
human decision rather than auto-applied** and landed as a rebuild. Two hardening
changes rode along: `build_gptq`/`build_awq` now print the full chained
`ImportError` traceback before the fail-closed `SystemExit` (the bare `SystemExit`
had masked the real cause, which only surfaced by bypassing the wrapper in a
probe), and `test_pinned_gptqmodel_exposes_expected_api` was added so the gate
stops certifying a `sys.modules` monkeypatched fake as proof the runtime works.

**IDs.** Canary `11233679`; calibration predecessor `11233678` (15:43:38 wall,
exit 0:0). Record: `docs/PACE_ENVIRONMENT_NOTE.md` § "Stage 3 canary pair".

**Without the gate.** The mocked unit-test suite passed throughout — it proved
the selection and quantization logic was wired correctly against a *fake*
`gptqmodel`, and could not prove the real runtime imports. Without the canary,
the first contact with the real dependency would have been a full build or
bridge run, and both faults would have surfaced after GPU-hours were committed
rather than after 30 seconds and zero.

---

## 2. `fewshot: 1` ran three exemplars, not one (2026-07-21)

**What surfaced.** `pilot_eval/tasks.py` treats `fewshot` as a **boolean switch**,
not a count: `prefix = GSM8K_FEWSHOT if fewshot else ""` (tasks.py:99), where
`GSM8K_FEWSHOT` is a fixed block of three worked examples. `fewshot: 1`,
`fewshot: 3` and `fewshot: 99` are byte-identical in effect. The validated bridge
config sets `fewshot: 1`, so **the bridge ran GSM8K 3-shot.**

**What caught it.** Source inspection during the mini-grid preparation pass. No
accuracy result of any kind was inspected in finding or reporting it.

**Root cause.** A config field whose name implies a count while behaving as a
flag. The run itself was not defective — the prompt was well-formed, identical
across all seven methods, and the validator's prompt-parity checks passed as
designed. The defect was in the *description*, and it propagated into
`docs/MINIGRID_REGISTRATION_2026-07-15.md` § 2, which read "**1 few-shot example**
… **matching the validated bridge configuration**" — two halves naming different
prompts, leaving the frozen registration internally inconsistent and the
mini-grid unconfigurable until resolved.

**Resolution.** Surfaced as a stop rather than adapted around. Amogh ruled
Reading A the same day: the bridge artifact governs, the mini-grid runs the
3-exemplar prompt, and the literal "1" is recorded as a drafting error. Landed as
**Amendment 2** to the frozen registration, dictated by Amogh and appended
verbatim. `configs/pace_minigrid_h3.yaml` keeps `fewshot: 1` so the emitted
prompt stays byte-identical to the validated canary, with an inline comment
stating the true exemplar count; the mini-grid validator now asserts GSM8K prompt
hashes are identical across every variant within a model, so future drift is
caught mechanically rather than by reading. The misleading field name is logged
as debt in `docs/GSM8K_FEWSHOT_FINDING_2026-07-21.md` § 6, deliberately **not**
fixed mid-campaign.

**IDs.** `docs/GSM8K_FEWSHOT_FINDING_2026-07-21.md`; Amendment 2 in
`docs/MINIGRID_REGISTRATION_2026-07-15.md`. No mini-grid GSM8K job was submitted
before the amendment landed.

**Without the gate.** The mini-grid would have run under a registration whose two
halves specified different prompts, and whichever prompt the config happened to
emit would have become the confirmatory record with no dated ruling behind it.
The inconsistency was in frozen text, so it would eventually have been found —
but most likely at analysis time, after 44 cells had been spent.

---

## 3. `fewshot_as_multiturn` auto-enabled under a chat template (2026-07-21)

**What surfaced.** The first GSM8K FP16 reference run placed each few-shot
exemplar in its own user/assistant turn pair, while `PREREGISTRATION.md` line 43
and `pilot_eval` place all three inline in a single user message.

**What caught it.** Inspection of the FP16 gate reference run before it was used
for any derivation — the run's own logged prompts, not its accuracy.

**Root cause.** `lm-eval` 0.4.12 logs `Using default fewshot_as_multiturn=True`
and auto-enables the behaviour whenever a chat template is applied
(`lm_eval/config/evaluate_config.py:306-308`). No flag was set. The derivation
document's § 2 had asserted that *omitting* `--fewshot_as_multiturn` yields inline
exemplars; that assertion was simply wrong for this version, and the harness's own
help text says so ("Auto-enabled with `--apply_chat_template`. Use 'false' to
disable.").

**Resolution.** The GSM8K reference now passes `--fewshot_as_multiturn false`
explicitly, and rendered prompts must be confirmed inline before a run is used for
any derivation. Placement is asserted mechanically rather than by eye: the
derivation script counts assistant turns in the first logged prompt and refuses to
derive a GSM8K gate unless there is exactly one. Recorded as **Amendment 1(a)** to
`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`, written after the first attempt
was inspected and before any replacement run was submitted.

**IDs.** Array `11338637` (first attempt); corrected GSM8K array `11342098`.
Amendment 1, `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`.

**Without the gate.** All four FP16 operational gates would have been derived
against a prompt the mini-grid does not run, and the GSM8K gates would have been
describing a different experiment than the one they gate. This is also the
incident that motivated the harness-defaults sensitivity study — a default that
changes the prompt with no flag set is the study's first live demonstration.

---

## 4. `strict-match` voided 617 of 1,000 GSM8K rows (2026-07-21)

**What surfaced.** The first GSM8K FP16 gate derivation produced a Qwen range of
**[0.175, 0.289]** — a range the known-good bridge implementation (0.615 on 200
items, `pilot_eval`) would fail badly.

**What caught it.** The gate itself, read against an independent implementation
of the same quantity. A gate that a known-good pipeline fails is either a broken
pipeline or a broken gate, and the disagreement forced the question.

**Root cause.** The stock `gsm8k` task ships **two** filters, `strict-match` and
`flexible-extract`, which score the *same* generations. § 2 of the derivation
fixed the task, shot count and item range but never named which metric to read,
so the derivation script took `strict-match`. `strict-match` requires the bare
regex `#### (-?[0-9.,]+)`; `pilot_eval.tasks.extract_gsm8k_answer` reads the
`####` marker **and falls back to the last number in the response**, which is the
convention `flexible-extract` implements. On Qwen2.5-1.5B, strict-match voided
**617 of 1,000** responses, **336 of which `pilot_eval`'s extractor scores
correct** — moving accuracy from **0.232 to 0.566 on byte-identical generations**.

**Resolution.** The GSM8K metric is now named explicitly:
`exact_match,flexible-extract`. The ground is a property of the two
implementations and predates all of this — a reference metric stricter than the
implementation it gates measures format compliance rather than the quantity of
interest. **The ordering was recorded rather than glossed:** the choice was made
after observing that strict-match produced a gate the bridge would fail, and it is
also the choice that raises the figure; Amendment 1(b) states this plainly so a
reader can weigh it. The § 3 arithmetic was not touched, no tolerance was widened,
and the MMLU gates derived under the original text stand unaffected. The derived
Qwen GSM8K gate is `[0.513, 0.637]`, which the bridge's 0.615 falls inside.

Downstream, this incident is what the standalone comparison CLI's `--filter` guard
was built from: a multi-filter file with no `--filter` is a fail-closed error
listing the available names, because there is no defensible default — not index 0,
and not a hardcoded preference for flexible-extract.

**IDs.** Amendment 1, `docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`; gates
committed `dbe5ad9`; CLI guard `d0b4be5`, verified in-image job `11360149`.

**Without the gate.** The mini-grid's GSM8K cells would have been gated against
[0.175, 0.289]. Every FP16 cell would have failed its own operational gate, and
the campaign would have stopped to debug a pipeline that was working correctly —
or, worse, the gate would have been widened to accommodate it.

---

## 5. Atlas F1/F2 population defects (2026-07-21)

**What surfaced.** Four implementation defects in the atlas mining pipeline, two
of them material to the cell population:

- **F1:** the registered § 3.2 earlier-run fallback was never implemented.
  `find_s1_task_file` took the newest run per side and never revisited, so **11 S1
  pairs contributed zero analyzed cells**.
- **F2:** the parser read only top-level `acc_norm`/`acc` and only the `hashes`
  struct. A newer lighteval schema nests metrics under `metrics` and stores raw
  `example`/`full_prompt`, so **583 of the 643** cells filed as "no binary
  correctness column (float-scored tasks)" were binary-scored cells the parser
  could not see.
- **F4:** `join_cell` recorded the symptom "no joinable items" and `run_pair`
  discarded the computed join whenever a later `CellSkip` fired, making exclusions
  unauditable from the archived cell. **This is what hid F2 for six days.**
- **F5:** `list_repo_files` ignored `Link: rel="next"` — latent, no rev-1 cell
  affected.

**What caught it.** The independent spot-check commissioned to clear the
provisional-for-external-quoting caveat: 10 stratified cells recomputed from
freshly re-downloaded raw per-item files by a from-scratch reimplementation of the
registered definitions, not a rerun of the pipeline. It reconciled **262 of 262
fields with zero discrepancies** — the per-cell *arithmetic* was sound — and in
doing so established that what was wrong was *which cells reached the arithmetic*.

**Root cause.** Under-implementation of a frozen protocol, concealed by a logging
defect (F4) that reported symptoms instead of root causes. F1 is the serious one
because its loss is not random: it removes exactly the pairs whose quantized side
was re-run later, a selection rule correlated with the model being popular enough
to re-evaluate, while § 6 promises that all enumerated non-excluded cells are
reported.

**Resolution.** **The registration was not amended; the code was corrected to
comply with it.** The disclosure that results had already been inspected when the
defect was found is stated first, in § 1 of the memo, rather than buried — the
rev-1 atlas had been computed and read, the certification tables built on it, and
the audit verdicts published internally. Rev-2 uses the same frozen 59-pair
manifest, same bootstrap 1000 / seed 0, and writes versioned artifacts that do not
overwrite rev-1; both revisions stay in the record. A **targeted second
spot-check** over recovered-F1, admitted-F2 and unchanged-control strata passed
14/14 cells, 126/126 fields. Population moved 1,155 → **1,707** analysable cells;
identical-score figures 113 (9.78%) / 6.22% → **145 (8.49%) / 7.20%**; K and J did
not move.

A retraction rode along and is worth its own line: the earlier gloss attributing
643 float-scored and 132 empty-join exclusions to upstream reporting practice was
**retracted in the paper, not only in the results note**. It had attributed to
upstream data a limitation that was ours.

**IDs.** Spot-check jobs `11338401`, `11338619`, `11338712`, `11338745`; code fix
`4dc9db0`; rev-2 runs `11339935`, `11341992`, downstream regeneration `11343383`,
committed artifacts job `11343754`; second spot-check `8b3e0de`; paper resync
`272136b`. Memo: `docs/ATLAS_REV2_CORRECTION_2026-07-21.md`. Gate at the time:
157 passed, 0 skipped, job `11339898`, 12 regression tests added.

**Without the gate.** The paper would have shipped an atlas missing roughly a
third of its eligible cells, with the loss concentrated in exactly the pairs
someone cared enough about to re-evaluate — and a sentence blaming the leaderboard
for our own parser. The arithmetic would have been correct throughout, which is
why nothing internal to the pipeline would have complained.

---

## 6. Calibration operational receipts were never written (2026-07-21)

**What surfaced.** `docs/PACE_EXECUTION_PLAN_2026-07-15.md` line 38 requires an
operational receipt per calibration artifact — peak RSS, cached bytes, wall time,
`passes`, `stream_rows_scanned`, copied into `results/`. **No such receipt was
ever written.** All 10 artifacts existed; `results/` had none.

**What caught it.** An audit of plan commitments against the contents of
`results/` — reading the plan line by line and asking what file it names.

**Root cause.** A plan requirement with no code path behind it and no check that
would notice its absence.

**Resolution.** Ruled by Amogh: real gap, reconstruct with disclosure.
Reconstructed from **primary records only** — `sacct` `Elapsed` and `MaxRSS` of
the workload step, and `retrieval.*` fields written into each artifact at build
time — recovering 10/10 on four of five quantities. **Cached bytes is absent from
every primary record and is emitted as `null` with a stated reason rather than
estimated.** Each receipt carries `"reconstructed": true` with its job ID and log
path. The log↔artifact mapping was established by reading each log's
`Calibration artifact:` line, not inferred from timestamps, and the sha256 chain
verifies 10 of 10.

This was scoped correctly as an **operational-bookkeeping gap, not a validity
problem**: the scientifically load-bearing provenance was written into each
artifact at build time and is intact. A related question — whether
`verify_bridge.py`'s "paired calibration receipts" criterion had been checking
something else — was answered *yes*, and answered in the memo: it resolves a
per-checkpoint `calibration_manifest.json`, i.e. exactly the scientific
provenance and none of the operational quantities. The bridge validation is
therefore sound and unaffected.

**Two traps recorded for reuse.** The epilog `mem=` line is **not** peak RSS — it
reports the `.batch` shell wrapper (~9,800K) against real peaks of ~6.9–7.4 GB, an
understatement of ~750× that "would have looked plausible enough to survive
review". And `sacct` and the epilog **disagree on wall time** for some array tasks
(`11303134_4`: 14:37:05 vs 14:53:04); `sacct` is authoritative.

**IDs.** `docs/CALIBRATION_RECEIPTS_RECONSTRUCTION_2026-07-21.md`;
`results/calibration_receipts.{json,csv}`; failed job `11233525_0` excluded, its
replacement `11233678_0` used.

**Without the gate.** Ten artifacts with no operational provenance, and — more
costly — the two traps above would have been rediscovered by whoever eventually
wrote a receipt writer, most likely by writing the epilog number and believing it.

---

## 7. Receipt writer: the array trap and the settling race (2026-07-22)

**What surfaced.** Two defects in `scripts/slurm/write_receipt.sh`, the job-time
receipt writer built so the reconstruction of incident 6 would never be repeated.

- **The array trap.** `sacct -j <id>.0` returns the `.0` step of **every** task in
  the array, not just the caller's — querying `11347807.0` returns both
  `11347807_0.0` and `11347807_5.0` — so `head -1` stamped the first task's
  resource profile onto every task's receipt.
- **The settling race.** The step row appears in `sacct` **before** `MaxRSS` is
  populated, and `Elapsed` is still being finalised at that moment. Polling until
  the row merely existed produced a null peak RSS and a wall time one second short
  (the probe read 00:00:25 for a step that ended at 00:00:26).

**What caught it.** A **deliberately asymmetric array probe** — two tasks
allocating different memory for different durations, built specifically so that
borrowing the wrong task's numbers would be visible. The settling race surfaced on
the probe's *first* attempt (`11349492`), which **failed closed with a null rather
than a wrong number**, which is the behaviour the writer was designed for.

**Root cause.** Both are `sacct` semantics that are invisible in the
single-task case: the array-wide step query, and accounting lag behind step exit.

**Resolution.** The lookup now queries the array-aware label and **row-matches the
returned JobID**, emitting nulls with a stated reason if no matching row comes
back rather than borrowing another task's numbers. The poll now continues until
`MaxRSS` itself is non-empty, with a distinct reason recorded if it never
populates. Proven on probe `11349557`: receipts read 00:00:06 / 210,028K and
00:00:27 / 1,236,044K, matching `sacct` row for row.

**IDs.** Fix `c598ac2` (shell-only: `bash -n` + `shellcheck` clean); writer
introduced `4190a52`, proven before use on probe `11347802`; freeze refreshed
`24fb6a6`. Probes `11349492` (surfaced settling), `11349557` (proved fix).

**Without the gate.** Every array-built receipt in the campaign would have carried
task 0's memory and wall time under another task's name — internally consistent,
individually plausible, and wrong. See incident 8 for the one that had already
happened.

---

## 8. The Llama canary AWQ receipt carried task 0's resources (2026-07-22)

**What surfaced.** The Llama canary's AWQ receipt claimed **7m43s and 20.5 GB** —
GPTQ's figures — instead of its own **14m15s and 47.4 GB**.

**What caught it.** **Comparing the pair, not reading either one.** Both figures
were individually plausible; nothing about the AWQ receipt looked wrong in
isolation. It was the two receipts side by side that showed one had borrowed the
other's numbers.

**Root cause.** The `sacct` array-index trap of incident 7, already in the field.
The GPTQ receipt happened to be correct because it was task 0 — the row `head -1`
picked.

**Resolution.** Corrected from `sacct`, row-matched on JobID. **Each receipt now
carries a correction block naming the defect, the fields changed, the values
before, and the fix commit, rather than being silently rewritten.** Resource
metadata only: the builds, their checkpoints and their calibration provenance are
unaffected, so no rebuild was warranted and none was performed.

**IDs.** Correction `9b3d8e4`; defect fixed in `c598ac2`; build array `11347807`.

**Without the gate.** A build receipt asserting the wrong peak RSS is exactly the
input a future capacity or OOM diagnosis would trust, and there is no later stage
that would have contradicted it. This one had no independent check downstream —
pairwise comparison was the only thing that could have found it.

---

## 9. Six build receipts predate the receipt writer (2026-07-22)

**What surfaced.** The Qwen seed-0/1/2 checkpoints were built 2026-07-18 and
2026-07-19 (jobs `11260334`, `11262390`). The receipt writer's first commit is
`4190a52`, timestamped 2026-07-22T00:33:14-04:00. Six checkpoints therefore had no
job-time receipt and could not have had one.

**What caught it.** The acceptance sweep over receipt fields, which found six
artifacts with no receipt where the rule demanded one.

**Root cause.** A rule introduced mid-campaign cannot bind the past. What it can
demand of the past is honest labeling.

**Resolution.** Ruled option A: reconstruct the six from `sacct` using the fixed
row-matched lookup, each recording its source rows verbatim, the writer's first
commit and timestamp, the job start time, and the reason it is exempt. Nothing
inferred — node recorded as absent rather than guessed, `cached_bytes` null with
its standing reason. **The rebuild option was rejected**: risking bit-nonidentical
rebuilds of the exact checkpoints underneath the signed bridge validation and the
cell-3 freeze, to improve bookkeeping, inverts the project's priorities.

The important half is the gate change. **The acceptance sweep now gates
reconstruction rather than accepting it**: a receipt marked `reconstructed` must
name its source rows and reason, cite the writer's first commit, and carry a job
start time **strictly before that commit**. Any job started after the writer
existed can no longer be satisfied by a reconstruction, so the exemption cannot
quietly widen — and the boundary is checkable against git history rather than
asserted. Sweep re-run in full: 253 checks, 0 failures, all six exemptions granted
on vintage with their start times shown against the boundary.

**IDs.** `d57e974`; builds `11260334`, `11262390`; writer `4190a52`.

**Without the gate.** "Reconstructed" would have become a permanently available
escape hatch that any future missing receipt could claim, and the distinction
between *could not have had one* and *should have had one and didn't* would have
been unrecoverable within a week.

---

## 10. One sick A100 ran a cell at 66 s/item (2026-07-22)

**What surfaced.** Mini-grid cell `11350246_9` (Qwen2.5-1.5B / `gptq_s3` / GSM8K)
ran at ~66 s/item from the first item — 290 of 1,000 items in 5 h 21 m — against
6–8 s/item for its four GPTQ siblings. Projected completion ~16.5 h against a 12 h
wall, with output written only at end of run, so the wall kill would have
destroyed the cell entirely.

**What caught it.** Wall-time comparison against sibling cells during routine job
health monitoring — a permitted inspection surface under the eval-phase lockdown.

**Root cause.** **One physical GPU.** Established by elimination, all off the
confirmatory item set:

- *Load path clean:* the same build's MMLU cell was the **second-fastest** of the
  five GPTQ MMLU cells (0:44:43).
- *Build clean:* receipt and artifact in family with siblings on every field —
  5m47s wall, 10.4 GB peak RSS, same `image_sha256`, own registered calibration
  artifact, 1,161,317,309 B against siblings' 1,161,317,307–317 B.
- *Artifact clean:* an off-register generation probe on **GSM8K test indices
  1000–1011** (the registered cell is 0–999; the probe raises rather than run if
  handed a start index below 1000) measured **22.09 tok/s against the sibling
  control's 22.03, ratio 1.00**, generated length within 7%, stop-at-cap 3/12 vs
  2/12. In situ the cell had averaged ~2.8 tok/s — a 7.8× shortfall in the cell,
  not in the artifact.
- *Node clean:* the node has 2 A100s, and cell `_9` always had exactly one of our
  cells on the other GPU throughout its window (`_5`, `_18`, `_22`, `_28`, `_33`)
  — **all at normal speed**.
- Weak corroboration: `nvidia-smi` into the live allocation returned its CSV
  header and no GPU rows.

**Resolution.** Cancelled per ruling at 05:39:50 elapsed. Resubmitted unchanged as
`11358057_9` — same script, same config, same 12 h wall — and completed normally.
**The probe falsified the hypothesis it was authorized to test** (generate-to-cap),
and that refutation is written into the document explicitly so the suggestive
framing does not outlive it. The bridge's slow `awq_s1` GSM8K half remains **open
as its own unexplained entry** and is deliberately *not* retro-explained by this
finding.

**The accidental A/B.** The intended mitigation failed (incident 11), the cell
relanded on the suspect node, drew its *other* A100, and ran at 6.68 s/it. Same
node, same image, same build, same registered configuration, differing only in
which physical device the job bound to: 66.4 s/item before, 8.9 s/item now. **A
run on a different node would have left node-level causes formally open; this one
closes them.** The diagnosis was confirmed by the failure of the mitigation rather
than by the mitigation.

**IDs.** Cell `11350246_9` (CANCELLED); probe `11357902` (first attempt `11357773`,
see incident 12); resubmission `11358057_9` (COMPLETED). Records `69fa60e`,
corrected `a0e206c`; `docs/MINIGRID_SLOW_CELL_PROBE_2026-07-22.md`.

**Without the gate.** The cell would have hit the 12 h wall and been destroyed
with no partial output, and the natural reading of "the `gptq_s3` build is slow"
would have cast suspicion on a quantization seed — a confirmatory variant — on the
basis of a hardware fault. The probe's blindness contract is what let this be
diagnosed at all without touching the confirmatory item set.

---

## 11. `sbatch --exclude` is accepted and silently discarded (2026-07-22)

**What surfaced.** The authorized mitigation for incident 10 —
`--exclude=atl1-1-02-018-27-0` — was passed, accepted, and had no effect. The
submitted job records a **different** node than the one passed:
`ExcNodeList=atl1-1-01-007-2-0` while `NodeList=atl1-1-02-018-27-0`, the node that
was supposedly excluded.

**What caught it.** Post-submission verification with `scontrol show job` — not the
clean `sbatch` exit, which reported success.

**Root cause.** PACE runs a site `job_submit` Lua plugin (`JobSubmitPlugins = lua`)
that **overwrites** `ExcNodeList` rather than merging into it. Confirmed
independently: three mini-grid cells submitted with **no `--exclude` whatsoever**
(`11350246_35`, `_37`, `_43`) carry the identical value `atl1-1-01-007-2-0`.

**Resolution.** **Treat `--exclude` as unavailable on this cluster.** Any future
placement constraint must be verified after submission via `scontrol show job <id>`
rather than assumed from a clean `sbatch` exit. Commit `a0e206c` corrects the
record left by `69fa60e`, which had asserted an exclusion that was never in force.

**IDs.** `a0e206c` correcting `69fa60e`; evidence jobs `11358057_9`, `11350246_35`,
`_37`, `_43`. Recorded at `docs/MINIGRID_SLOW_CELL_PROBE_2026-07-22.md` § 8.1.

**Without the gate.** This is the project's own named failure class — a control
that reports success while doing nothing, the same shape as the stale test-count
expectation in incident 14. The record would have carried a false statement about
where a resubmitted confirmatory cell ran, and the next session would have burned
another run rediscovering it. As it happened the inert flag produced *better*
evidence than the working flag would have (incident 10), which is luck, not a
defence of the flag.

---

## 12. Stale `pilot_eval` baked into the image's site-packages (2026-07-22)

**What surfaced.** The generation probe's first attempt died in 28 s with
`ValueError: unknown quantization backend: gptqmodel_torch`, raised from
`/usr/local/lib/python3.11/site-packages/pilot_eval/modeling.py` — a **stale
`pilot_eval` baked into the image**, predating the `gptqmodel_torch` backend that
the entire mini-grid uses.

**What caught it.** Launching the probe **by file path** instead of with `-m`.
That puts the script's own directory at `sys.path[0]` and never adds cwd, so the
stale copy won.

**Root cause.** The image carries a copy of the project source in site-packages.
`python -m pilot_eval.run` under `--pwd /workspace` puts cwd at `sys.path[0]`, so
`/workspace/pilot_eval` shadows it — which is why the grid is unaffected, and the
38 clean exits at the time were the proof. Had shadowing not worked, all 44 cells
would have failed on this exact `ValueError` instead.

**Resolution.** The probe now asserts `pilot_eval.__file__` resolves under
`/workspace` and refuses to run otherwise — an **interim guard only**. The image
is to be rebuilt without the stale copy, on the post-campaign list in priority
position, and **deliberately not actioned mid-grid**. Shadowing is explicitly not
accepted as a fix: an image whose fallback import path silently runs old code is a
landmine regardless of whether anything currently steps on it. The same hazard is
cited in `10c2c29` as the reason the packaging CLI's console script is named
`flipeval-compare` rather than claiming `flipeval`, which would let install order
decide which entry point runs.

**IDs.** Failed probe `11357773`; successful probe `11357902`; recorded `69fa60e`,
`docs/MINIGRID_SLOW_CELL_PROBE_2026-07-22.md` § 6.

**Without the gate.** The grid was never at risk — but the *correct module is
selected by implicit `sys.path` ordering, with nothing that complains if it
changes*. A future job launched by file path gets the stale copy; a stale copy that
happens **not** to raise would run different code under a registered method name
and produce results that look fine. This was found by accident, and the entry
exists so the rebuild is not forgotten.

---

## 13. A missing `/scratch` bind read as a code regression (2026-07-22)

**What surfaced.** Packaging-tests job `11359430` reported **2 failed, 168
passed** — `test_pinned_gptqmodel_exposes_expected_api` and
`test_pinned_gptqmodel_builds_qwen2_shell_model_under_pinned_transformers`, both
registered tests, both in the suite whose recorded expectation is 170 passed / 0
skipped. Read cold, that is a source regression in the pinned GPTQ path.

**What caught it.** The rerun with the bind restored: job `11359447`, same source,
**170 passed**. The two runs differ in the `apptainer exec --bind` argument and
nothing else.

**Root cause.** The job bound only `$PROJECT_DIR:/workspace` and omitted
`$SCRATCH_DIR:/scratch`. `env.sh` exports `APPTAINERENV_HF_HOME=/scratch/hf_cache`;
importing `gptqmodel` pulls in `tokenicer`, which **mkdirs that path at import
time**. Without the bind, `/scratch` is read-only inside the container and the
import fails with `PermissionError` — surfacing through `pytest.importorskip` as
two failing tests rather than as a missing mount. The traceback in the log shows
the chain ending in `tokenicer/__init__.py:29: in _configure_hf_cache`.

**Resolution.** No source change; nothing was wrong with the code. The harness was
fixed: `packaging_tests.sbatch` now binds both paths, and its header records this
as one of two things it "gets right, both learned from job 11359430 failing" — the
second being that `env.sh` sets `set -e`, so a failing pytest aborts the script and
later suites never run, which is why exit codes are now captured explicitly. The
mini-grid sbatch already bound both.

**Primary evidence.** This incident has no correction memo; it is recorded in the
`packaging_tests.sbatch` header comment and in the two job logs
(`logs/packaging_tests_11359430.out`, `logs/packaging_tests_11359447.out`). This
entry is written from those, per the evidence rule above.

**IDs.** `11359430` (FAILED, 2 failed / 168 passed), `11359447` (COMPLETED, 170
passed, gate cited in `10c2c29`), later `11360149` (170 registered + 25 packaging,
cited in `d0b4be5`).

**Without the gate.** A false regression against the pinned quantization path, at
a moment when the campaign's standing rule is to stop and surface on unexpected
failure. The likely cost is hours spent bisecting a source tree that was never
broken — and the worse branch is "fixing" the tests to accommodate a
`PermissionError`, which would have disabled the two tests that exist to prove the
real runtime imports (see incident 1).

---

## 14. The in-image test-count expectation sat stale at 145 vs 161 (2026-07-21)

**What surfaced.** The recorded gate expectation in `AGENTS.md`, `CLAUDE.md` and
`scripts/slurm/build_image.sbatch` read **145** while the suite was really at
**161**. A concurrent session had added 16 tests without updating the count.

**What caught it.** A gate run whose reported number did not match the recorded
one — noticed on the run, not by a check, because no check existed.

**Root cause.** More than one agent session commits to this worktree, and the
expected count is a hand-maintained constant. **A stale expectation is a gate that
cannot fail, which is worse than no gate:** a suite of 161 passing tests satisfies
"at least 145" trivially, so 16 tests could have been deleted without the gate
noticing.

**Resolution.** Corrected to 161 in all three places in `dbe5ad9`, and to **170** in
`1966e5d` when that commit added tests. The procedural fix landed in the same
commit as ruling 5: `AGENTS.md` and `CLAUDE.md` now require **whichever session
adds tests to update the expected count in the same commit**, and cite this
incident by its numbers as the reason. `git log` before assuming HEAD is yours is
now written into the guardrails.

**IDs.** `dbe5ad9` (161, job `11343941`); `1966e5d` (170, job `11347835`); rule in
`CLAUDE.md` / `AGENTS.md`.

**Without the gate.** The in-image suite is the authoritative gate for every
cluster-side source change on this project. Held at 145 it would have kept
reporting PASS through any regression that left at least 145 tests passing, for as
long as nobody happened to read the number — and the incident's own discovery was
incidental, which is the argument for the same-commit rule.

---

## 15. Harness-sensitivity preflight FAIL; config-churn array dead on dependency (2026-07-22) — **OPEN**

**What surfaced.** After the harness-defaults sensitivity registration was frozen
and committed (`b9c2604`), the FP16 config-churn jobs were submitted as authorized.
The preflight failed; the dependent array never ran and is now unrunnable:

```
JobId=11361531  JobState=PENDING  Reason=DependencyNeverSatisfied
Dependency=afterok:11361530(failed)
```

**What caught it.** The preflight, which is fail-closed by design and gates the
array behind `afterok`. It did exactly what it was placed to do: **no GPU time was
spent under a protocol whose conditions may not be expressible.**

**Root cause.** Two layers, and only the first is understood.

*First attempt `11361507`* died on `ImportError: cannot import name 'setup_parser'
from 'lm_eval.__main__'` — the probe's own method, not a finding about the harness.

*Second attempt `11361530`* ran to completion and returned `PREFLIGHT_RESULT:
FAIL`. Six of seven probed flags are **absent from `lm_eval --help`**:
`--apply_chat_template`, `--num_fewshot`, `--fewshot_as_multiturn`, `--limit`,
`--log_samples`, `--output_path`; only `--tasks` was found. A follow-up help dump
(`11361596`) found **no argparse-style parser object in `lm_eval.__main__` at all**
(`parser-ish names: []`), and `lm_eval --help` produced no matching lines.

The task-level checks all **PASSED** — gsm8k ships both filters, gsm8k stock
`num_fewshot` is 5, and all four probed MMLU subjects are zero-shot with no
`filter_list`, confirming the § 3.3 "C = D" resolution against the live harness.
So the tasks are as registered; what is not as assumed is the **CLI surface**.

The preflight also raised, as a `[NOTE]` rather than a conclusion, that
`evaluate_config` sets `fewshot_as_multiturn` from `apply_chat_template` and that
condition REF (chat on, multiturn off) **may be inexpressible**. Reading the seven
matched lines, the auto-enable fires only when `fewshot_as_multiturn is None`, and
the hard error fires only for multiturn=True with chat off — so an **explicit**
False under a chat template appears permitted. The open question is therefore *how
to pass it*, given that the flag is not on the CLI surface the probe could see, not
*whether the condition exists*.

**Resolution.** **None yet — surfaced, not worked around.** Per the standing rule,
this is a design-level stop: it touches whether a frozen registration's conditions
can be run as written, which is not an agent's call. `11361531` is left dead in
the queue rather than resubmitted, and no cap was consumed.

**IDs.** Registration `b9c2604`; preflight `11361507` (FAILED, method defect),
`11361530` (FAILED, `PREFLIGHT_RESULT: FAIL`); help dump `11361596` (COMPLETED);
dead array `11361531`. Logs at `logs/sens_preflight_1136153{0,7}.{out,err}`,
`logs/help_dump_11361596.out`. Scripts staged outside the fingerprint at
`~/scratch/flipeval/work/`.

**Without the gate.** The array would have run six FP16 conditions against flags
the harness may silently ignore. `lm-eval` accepting an unknown argument or
falling back to a default is precisely how incident 3 happened — and there, the
wrong prompt was only caught because someone read the rendered output. Six
conditions differing by flags that did nothing would have produced a clean-looking
sensitivity table whose conditions were all the same run.

---

## 16. Llama-3.2-3B FP16 MMLU baseline fell below its registered gate (2026-07-22) — **OPEN**

**What surfaced.** The mini-grid validator, run over the complete 44-JSONL set as
the registered first inspection, failed. 408 of 409 checks passed. The one
failure:

```
llama32-3b: baseline mmlu accuracy 0.527631 is within [0.5309, 0.6309]
```

0.527631 against a floor of 0.5309 — short by 0.0033 (0.33 pp). The other three
FP16 baselines sit inside their gates. `decision_record_written: false`; the
validator declined to write the record, and the escalation computation did not
run.

**What caught it.** The FP16 operational gate, which is the only accuracy the
validator is permitted to compute. It is a gate that exists solely to catch this
class of problem, and it fired on its first use.

**Root cause — the reference gated a different benchmark than the pipeline
runs.** Established by a metadata-only Phase 1 diff (no accuracy read) and then
proven byte-exactly by a prompt-identity probe whose reconstructions hash-match
the sealed cells (72 of 72, job `11369022`). Three differences between the
lm-eval reference run and the registered `pilot_eval` MMLU path:

| dimension | lm-eval reference | `pilot_eval` |
|---|---|---|
| system message | subject-specific *"The following are multiple choice questions (with answers) about {subject}."* | model template default — Qwen's *"You are Qwen…"* persona; Llama's empty system block |
| item stem | bare question text | `"Question: "` prefix (`tasks.py:20`) |
| Llama date block | `Today Date: 21 Jul 2026` | `Today Date: 22 Jul 2026` |

Matching, and therefore not the cause: model revision, dtype, shot count (0-shot
across all 61 subtasks both sides), metric (`acc` only), item count 14,042, and
seeds. `fewshot_as_multiturn=True` appears in the MMLU reference but is inert at
0-shot.

The Llama/Qwen asymmetry follows from the templates: lm-eval supplies a system
message, and Llama's template renders that block *plus* a date preamble while
Qwen's renders the instruction alone — so the reference↔pipeline prompt delta is
strictly larger for Llama. Consistent with the observed 5.3 pp vs 1.2 pp gaps;
not proven by them.

**Second defect, independent of the first.** The Llama template injects the
current calendar date. The sealed cells carry `Today Date: 22 Jul 2026`; the
reference that derived their gates carries `21 Jul 2026`. **The Llama prompts
are not reproducible by rerunning the same command on a different day**, in
either implementation, for either task.

**Resolution — CLOSED 2026-07-23.** Amendment 3 was signed
(`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`, commit `e3d1341`). The MMLU
gates were void as derived, not the pipeline: the reference supplied a
subject-specific system message where `pilot_eval` supplies none and omitted the
`"Question: "` stem prefix. A custom `mmlu_pilot` task reproduced the registered
prompt byte-for-byte — proven before any rerun by prompt-hash identity against
the sealed cells (`11373459`, 24/24 both models) — and the reference was rerun
under a date-pinned entry point (`22 Jul 2026`, the date the sealed cells carry;
`date_string` had to be passed explicitly because lm-eval supplies no date, a
declared independence reduction). Gates re-derived mechanically under the
unchanged § 3 tolerance rule for both models uniformly (`11373818`, `11375093`),
committed with the in-image gate at 170 passed (`bd565bd`, gate job `11375139`).
The validator then passed 409/409 (`11375247`): Llama MMLU FP16 0.527631 now
sits inside the corrected gate [0.453418, 0.553418]. The 7.8 pp Llama MMLU drop
under the corrected prompt (0.580900 → 0.503418) is the size of the reference's
error, and confirms the diagnosis directly.

**IDs.** Validator `11368769` (FAILED, 1:0, 409 checks); prompt-identity probe
`11369022` (72/72 hash-match); gates committed `dbe5ad9`; derivation
`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md`; references `11338637`,
`11342098`.

**Without the gate.** The escalation rule would have been applied over four cells
whose FP16 baselines were never cross-validated, and the 5.3 pp
implementation gap would have sat underneath every H3 quantity in the paper,
invisible — the gate is the only artifact in the campaign that compares the
registered pipeline against an independent implementation at all.

---

## 17. Sensitivity condition REF would have run as a duplicate of condition A (2026-07-23)

**What surfaced.** While rebuilding the config-churn array against the `run`
subcommand, array cell 2 — condition **REF** — read:

```
FLAGS="--apply_chat_template --num_fewshot 3"
```

with no multiturn flag. `lm_eval` auto-enables `fewshot_as_multiturn` under a
chat template, so REF would have rendered multi-turn prompts: byte-identical to
condition **A** in cell 3. The study's headline contrast would have been two runs
of the same configuration, reported as a difference.

**What caught it.** Inspection during the rebuild, prompted by the preflight
reconciliation having just established what the flag surface actually is. Nothing
in the array would have failed; both cells would have completed cleanly.

**Root cause.** The same harness default as incident 3, in the study written *to
measure that default*. The registration names REF as
`--apply_chat_template --num_fewshot 3 --fewshot_as_multiturn false`; the sbatch
omitted the third flag, and an omitted flag is not an unset value here.

**Resolution.** REF now passes `--fewshot_as_multiturn false` explicitly and A
passes `true` explicitly rather than relying on a bare switch. Expressibility was
confirmed against the pinned image rather than assumed —
`--fewshot_as_multiturn [<bool>]`, *"Auto-enabled with --apply_chat_template. Use
'false' to disable."* The array also now invokes `python -m lm_eval run`
explicitly instead of relying on the documented back-compat shim that
auto-inserts `run`.

**IDs.** Rebuilt array `11368976`; preflight reconciliation `11368795`,
`11368817`; dead predecessor `11361531` cancelled.

**Without the gate.** Six cells, two of them the same configuration, producing a
sensitivity table whose headline row measured nothing. The study's own
motivating finding is that this harness turns defaults on silently; it would have
been published having been caught by it.

---

## 18. Qwen-7B AWQ build hit two distinct memory ceilings, one per attempt (2026-07-23)

**What surfaced.** The Qwen-7B AWQ seed-0 build — the escalation stage's build
canary, deliberately run before the five-seed fan-out — failed twice, each time
on a *different* resource:

- **Attempt 1** (`11391539_3`, 2026-07-23): OOM on a **40 GB A100** during the
  AWQ scale search, ~70 s in. **Device** memory.
- **Attempt 2** (`11409297_3`, resubmitted on an **80 GB** A100 with
  `--constraint=A100-80GB`): the device side was now fine — it ran 20× longer
  and reached **23 of 28 layers (82 %)** — but was **host-OOM-killed** at
  `oom_kill` StepId `11409297.0`, `step_state OUT_OF_MEMORY`, peak RSS
  67,046,660 KB ≈ **63.9 GB** against the `--mem=64G` cgroup cap. **Host** RAM.

**What caught it.** The build canary, functioning exactly as placed — a single
seed-0 build run ahead of the fan-out precisely so a fresh model's memory
envelope is discovered at 1× cost, not rediscovered by seeds 1–4 at 5×. It fired
twice and converted **two** separate ceilings into recorded facts.

**Root cause.** Qwen2.5-7B is wider than Llama-3.1-8B where AWQ is expensive:
`intermediate_size` 18944 vs 14336. That width pushes the AWQ activation search
past a 40 GB card (device) *and* pushes the host working set past 64 GB (host) —
two independent limits that happen to bite the same model. The 63.9 GB "peak" is
not a demand measurement: the build died at 82 % of layers with the tail and
final packing still ahead, so true host demand is unknown and was still rising.
The near-identical Llama-8B AWQ figure (67,045,052 KB, **COMPLETED** at 64 GB)
confirms the reading — that model fit under the same cap by a hair, so 63.9 GB is
the ceiling both builds pressed against, not the ceiling either one needed.

**Resolution.** Ruling (Amogh, 2026-07-24): Qwen-7B AWQ cells move to
**`--mem=128G`** (not 96 GB — 96 would gamble that the unmeasured tail needs
under ~32 GB more, and a third failed attempt costs ~20 A100-min plus a queue
round-trip). Scoped to the Qwen-7B AWQ cells only, as a submit-time override
alongside `--constraint=A100-80GB`; the `64G` sbatch default is unchanged for
every other cell, and Llama-8B AWQ's 64 GB half is untouched. Both envelopes are
now on record in `ESCALATION_STAGE_PLAN_2026-07-23.md` §7 and the
`build_quantized.sbatch` header. Failure receipt for attempt 2 committed as the
record. Placement of the 128 GB resubmit verified via `scontrol`
(constraint + memory grant) before it is trusted.

**Without the gate.** Both ceilings would have been discovered inside the
five-seed fan-out instead of ahead of it — the device OOM at ~5× the wasted GPU
time, and the host OOM at 82 % of a ~30-minute build × up to five seeds, each
producing an empty output dir and a confusing OUT_OF_MEMORY with the GPU
apparently idle. The canary is a build canary by design; here it earned its cost
twice over.

---

## 19. The acceptance sweep assumed single-file weights; 7B/8B are sharded (2026-07-25)

**Evidence.** `logs/escalation_acceptance_sweep_11470366.err` (`FileNotFoundError:
.../qwen25-7b-gptq4-seed0/model.safetensors`), `.out` (`ESCALATION_SWEEP_EXIT: 1`
after three PASS lines); `scontrol show job 11470455`
(`Reason=DependencyNeverSatisfied Dependency=afterok:11470366(failed)`); the
checkpoint listing showing `model-00001-of-00002.safetensors`,
`model-00002-of-00002.safetensors`, `model.safetensors.index.json`;
`logs/proof_shard_reload_11476608.out` for the fix.

**What happened.** The escalation acceptance sweep — standing-order step 2, the
gate that releases the 44-cell eval fan-out — died 25 s in, on the first cell it
touched. Its reload check opened a literal `model.safetensors`. Every mini-grid
checkpoint (1.5 B, 3 B) is a single file; every escalation checkpoint (7 B, 8 B)
is 2-way sharded. The script was the mini-grid sweep with `MODELS` swapped, and
it inherited a file-layout assumption that only becomes false at scale.

The sweep had passed three checks (presence, receipt, quant_method/bits) on that
one cell before dying, so **nothing was verified**: the reload, receipt pairing,
provenance and disjointness checks never ran on any of the 20 checkpoints. The
builds themselves were fine — all 16 seed-3/4 builds COMPLETED exit 0, all 20
checkpoints complete on disk.

**This is the third scale-inherited defect in this stage**, and the pattern is
now named: *mini-grid-era code carries assumptions that hold at 1.5 B/3 B and
are false at 7 B/8 B, and they surface only when the larger models run.* The
prior two were resource envelopes — device memory 40 GB → 80 GB, host memory
64 G → 128 G (entry 18). This one is data layout, which is the more dangerous
kind: an envelope breach announces itself as an OOM, while a layout assumption
can read part of a file and return success.

**Resolution.** Ruling (Amogh, 2026-07-25): fix, prove, then resume — with the
proof required to demonstrate *shard completeness*, not merely absence of a
crash. The stated danger was a sweep that reads shard 1, skips shard 2, and
reports PASS on a half-verified checkpoint; that outcome is worse than the
crash, because it is a gate that certifies what it never looked at.

The reload was rewritten (`work/shard_reload.py`, imported by the sweep so the
proof exercises the same code) to be **index-driven and complete by
construction**: iteration comes from `model.safetensors.index.json`'s
`weight_map`; every shard the index names must exist *and* be recorded as
opened; the tensor keys actually read are compared against the index's full key
set; a missing index is an explicit branch on "no index present", never a
`try`/`except` that could swallow a real absence — sharded files on disk with no
index fail loudly rather than falling through to the single-file path.

Proof job `11476608` (CPU-only, 32 s, exit 0) reported per-shard counts for
`qwen25-7b-gptq4-seed0`: shard 1 = 611 tensors / 1,634,576,384 elements, shard 2
= 316 / 329,896,448, **sum 927 = the index's 927-key `weight_map`**. A
shard-1-only read sums to 611 and fails that check, which is what makes the
proof discriminating rather than decorative. It also carried the 3 B single-file
cell as a regression (still PASS, `layout=single-file`) and two negative
controls: an index naming two shards with only one on disk, and sharded files
with the index removed. Both were refused.

A scan of the rest of the chain for the same class of assumption found no
further layout dependency — `pilot_eval` loads through
`from_pretrained`/`from_quantized`, which read the index natively; the validator
opens no weights; the receipt writer measures the checkpoint *directory* with
`du -sb`. It did find one live vacuous-pass hazard of a different kind:
`scripts/slurm/verify_minigrid.sbatch` hardcodes the **mini-grid** config and
results root, so running it unchanged after the escalation eval would validate
the already-complete mini-grid and exit 0 — a PASS carrying no information about
the escalation grid. Recorded here; it must be pointed at the escalation config
before step 6.

**Without the gate.** The sweep is fail-closed by construction and its `afterok`
link held: the 44-cell eval array went to `DependencyNeverSatisfied` rather than
launching over an unverified checkpoint set, and no confirmatory cell was
touched. The crash itself cost nothing. What the gate did *not* catch on its own
is the half-read failure mode — had the checkpoints been sharded in a way that
let `safe_open` succeed on a partial set, this sweep would have returned PASS
and the eval would have been released over checkpoints whose second shard was
never examined. That gap was closed by the fix, not by the gate.

---

## 20. The validator would have validated the wrong grid, and green (2026-07-25)

**Evidence.** `scripts/slurm/verify_minigrid.sbatch` before commit `1b263b4`
(hardcoded `--config /workspace/configs/pace_minigrid_h3.yaml --results-root
/workspace/results`); `configs/pace_escalation_h3.yaml` vs
`configs/pace_minigrid_h3.yaml` (`output_dir: results` in both, disjoint
`run_name`s); gate job `11477117`; `tests/test_verify_minigrid.py`.

**What happened.** Found by the scan ordered after incident 19, before the
validator was due to run. The Stage 6 → Stage 7 gate hardcoded the mini-grid
config and results root. Pointed at the escalation grid it would not have
errored: it would have found the complete, self-consistent, already-validated
mini-grid, checked all 44 of *those* cells, and exited **0**. A green validator
certifying nothing about the grid it claimed to check.

This is a different failure from entry 19, and worse in kind. A wrong config is
not a crash — it is a *valid run of the wrong thing*, and every signal it emits
is genuine. Nothing downstream could distinguish it from the intended run.

**Resolution.** Ruling (Amogh, 2026-07-25): fix at the root, not by repointing
the hardcoded value. Every input is now required with no default —
`MINIGRID_CONFIG`, `MINIGRID_RESULTS`, `MINIGRID_MODELS`, `MINIGRID_CELLS`, each
via `${VAR:?}`, all four verified to abort `rc=1` before the image starts. The
last two are the operator's declaration of *intent*, made independently of the
config and checked against it, because both grids live under the same results
root and the results root therefore cannot disambiguate them. Only two
declarations that must agree can. `verify_minigrid.py` also now asserts each run
dir holds **exactly** the cells the config declares — equality, not containment,
so a missing cell and a foreign cell both fail — and these checks run first,
before any per-file work.

**A control that reported success while doing nothing, caught in the writing.**
The first draft branched on `verify_common.check()`, which returns `None`. So
`if not check(...): continue` was unconditionally true and the cell-equality
check never executed once — the fixture with a deliberately planted foreign
JSONL returned `passed: True`. The new test caught it on the first gate run
(`1 failed, 181 passed`). The call site now evaluates the condition into a
variable and carries a comment saying why `check()`'s return must never be
branched on. Worth recording plainly: the check added to prevent a vacuous pass
was itself vacuous for one gate run, and only a test written to fail caught it.

Six tests, in-image gate **176 → 182** (job `11477117`, 182 passed, 0 skipped,
0 failed).

**Without the gate.** The mini-grid was complete and passing, so the wrong-grid
run would have produced a summary indistinguishable from a real one: 44 files,
all checks green, `passed: true`. It would have been cited as the escalation
grid's validation in the step-6 → step-7 handoff, and the H3 decision would have
rested on a validator that never opened an escalation cell. Nothing later in the
chain re-checks which grid the validator looked at.

---

## 21. `--requeue` is accepted and inert; the eval array ran on the wrong queue (2026-07-25)

**Evidence.** `scontrol show config` → `PreemptType = preempt/qos`,
`PreemptMode = CANCEL`; `sacctmgr show qos embers` → `PreemptMode=cluster`
(inherits CANCEL); `scontrol show job 11476696` → `Requeue=1`; `scontrol show job
11476696_3` → **"not found"**; `sacct -j 11476696` showing tasks 3, 5, 7, 8
`PREEMPTED` at 01:40:21 / 01:29:12 / 01:00:11 / 01:00:06;
`docs/ESCALATION_STAGE_PLAN_2026-07-23.md` § 3 dated note; resubmission
`11477918`.

**What happened.** Two failures compounded, one inherited and one mine.

*The wrong queue.* The stage plan's own table lists the 44 eval cells on
`embers`, and a **dated note in the same document explicitly corrects it**: the
cells run on `inferno`, "because `embers` preemption of a bs=1 pass wastes the
whole pass," and the dollar guard already accounts for inferno eval. The
resubmission after incident 19 carried the prior session's `-q embers`
submission line forward without checking it against that correction. The
predicted failure then happened, for the stated reason.

*The inert control.* The array carried `--requeue`, and `Requeue=1` is set on
the job — but Phoenix preempts with `PreemptMode = CANCEL`, so preempted jobs
are **destroyed, not requeued**. Four cells died and none came back; the
controller no longer knows they existed. `--requeue` was accepted at submission,
reported as set by `scontrol`, and did nothing.

**Cost.** 5.16 A100-h of preempted work discarded (3 Qwen GSM8K cells and one
MMLU cell), plus calendar. Those hours were free — the waste was in wall-clock,
not dollars. **No data-integrity impact:** the six completed cells were verified
at their exact expected counts (14,042 / 1,000) before being write-protected,
and no confirmatory result was corrupted or read.

**A stub hazard the preemption exposed.** `pilot_eval/run.py` opens each output
`"w"` *before* the item loop and writes incrementally, so a killed cell leaves a
**zero-byte or truncated JSONL on disk**, not nothing. Two 0-byte files
(`gptq_s0.gsm8k.jsonl`, `gptq_s1.gsm8k.jsonl`) sat in the results directory
looking exactly like completed cells to any existence-only coverage check. The
registered validator catches them on exact item counts; a weaker check would
not. Worth stating because the intuition — "it writes at the end, so a killed
job leaves nothing" — is the opposite of the truth.

**Resolution.** Pending cells 11–43 cancelled; cells 3, 5, 7, 8 and 11–43
resubmitted on `inferno` as `11477918`. Cell 9 was left running on `embers`
rather than discarding live work, tracked explicitly for preemption. The six
completed cells were `chmod a-w`'d **before** the resubmit, since a hand-typed
array range next to a runner that opens `"w"` unconditionally is one typo away
from destroying finished work — the standing archive/protect convention arriving
a few hours early.

Two details of the recovery are worth recording. The resubmit range given was
`3,5,11-43`; between it being written and being run, cells 7 and 8 were
preempted and cell 10 completed, so the range was corrected to `3,5,7,8,11-43`
and six cells were protected rather than five. Queue state read once and reused
is stale state. And the cancel and the resubmit must not overlap: two arrays
holding the same task id would both open the same JSONL `"w"`, so the cancel is
strictly ordered before the submit.

**The third accepted-but-inert control, and one never logged.** This joins
`--exclude` (11) and a third that was caught, recovered, and recorded only in a
commit message: on 2026-07-24 the build fan-out was first submitted with
`--array/--export/--constraint/--mem/--dependency` placed **after** the script
path, so `sbatch` parsed them as script arguments and the jobs silently fell
back to script defaults — targeting Qwen2.5-1.5B with `--array=0-5`. One task
started against a **frozen mini-grid checkpoint** before all eight were
cancelled within ~8 s; mtimes confirmed every frozen checkpoint untouched. It
belongs here and had no entry until now.

All three share one shape: **the scheduler accepted the flag and the flag did
nothing**, and in every case `sbatch` exited 0.

**Without the gate.** There was no gate — that is the finding. Nothing in the
submission path checks that a requested scheduler behaviour is actually in
force, so the loss was discovered by noticing cells missing from `squeue` rather
than by any control firing. The rule adopted in `AGENTS.md` is that a scheduler
control is not in effect until **independently observed** — `scontrol` after
submission, the QOS/partition configuration, or observed behaviour. Acceptance
at submission proves nothing. That rule would have caught all three of these
before they cost anything.

The queue error carries its own lesson, separate from preemption: **a correction
that lives only in a plan document is easy to carry past.** The `embers` line in
the plan's table is still there, still wrong, contradicted by a note further down
the same file. Constraints that must bind a submission belong in the `sbatch`
script, where the submission line cannot ignore them.

---

## 22. A limit copied from a faster configuration is an unmeasured limit (2026-07-25)

**Evidence.** `sacct -j 11477918 --format=SubmitLine` →
`sbatch ... --array=3,5,7,8,11-43 --time=08:00:00 ...`;
`scripts/slurm/run_minigrid.sbatch` line 10 at the time → `#SBATCH
--time=12:00:00`; `scontrol show job 11477918_13` → `TimeLimit=08:00:00`,
`RunTime=06:25:16`; tqdm progress recovered from `logs/minigrid_11477918_*.err`;
`scontrol update JobId=11477918_13 TimeLimit=16:00:00` → **"Access/permission
denied"**; resubmission `11485972` observed at `TimeLimit=20:00:00`.

**What happened.** Ten of the 44 escalation eval cells were on course to hit
their walltime with **nothing written**. GSM8K cells emit their JSONL only at
the end, so an overrun destroys the entire cell rather than truncating it.

Measured rates, from the logs, against an 8 h wall:

| cell | done | cumulative s/it | projected |
|---|---|---:|---:|
| qwen AWQ GSM8K ×5 | 468–596 / 1000 | 38–48 | 10.5–12.4 h |
| llama AWQ GSM8K ×5 | 162–419 / 1000 | 25–36 | 7.3–10.0 h |
| qwen GPTQ GSM8K (idx 9) | 558 / 1000 | 11.1 | 3.1 h |

**Two causes, not one.** The proximate cause was a hand-composed
`--time=08:00:00` on the submission line, overriding the script. But the
script's own **12 h default would also have truncated the slowest cells** — it
derived from the ~7.6 s/item FP16 genspeed probe, fixed at a time when no
quantized GSM8K cell had completed anywhere. It was never measured against the
configuration it governed. Fixing only the override would have left a limit that
still failed, just less often.

**The limit could not be repaired in place.** `scontrol update TimeLimit` is
denied to unprivileged users for an increase; only reduction is permitted. Once
a job is running under a short wall, the sole remedy is cancel-and-rerun.

**A rate-reading trap.** tqdm's `s/it` is a *smoothed recent* rate, not the
cumulative average, and the two disagreed materially. Task 35 reported 20 s/it
(projecting 6.4 h — apparently safe) while its cumulative `elapsed/done` was
**29.6 s/it**, projecting 8.23 h, past the wall; its instantaneous rate then
drifted to 40.7. The first read of the logs classified it as safe on the
displayed figure. Cumulative rate is the honest projector for a walltime
decision; the displayed one flatters a job that is slowing down.

**Cost.** ~17 A100-h of guaranteed-waste burn avoided by cancelling early;
~35 A100-h of already-spent work discarded across the ten cells. **No
data-integrity impact:** all 33 completed cells were verified at exact counts
(14,042 / 1,000) and write-protected `0444` before the cancels, and the ten
target cells were confirmed 0-byte and writable before resubmission.

**Fixes.** `--time` raised to 20:00:00 **in the script** (~61 % headroom over the
worst measured projection), with the measured per-backend rates recorded in the
comment beside it, and the resubmission carries **no `--time` on the line at
all** — a hand-composed override being the defect under repair, the fix must not
reproduce its shape.

## 23. Qwen AWQ GSM8K runs 3.6× slower than GPTQ on identical hardware (2026-07-25)

**Evidence.** tqdm cumulative rates from `logs/minigrid_11477918_*.err` and
`logs/minigrid_11478252_9.err`, same A100 partition (`gpu-a100`), same
`batch_size: 1`, same `max_new_tokens: 256`, same 1,000 GSM8K items.

| model | backend | s/item | per-cell |
|---|---|---:|---:|
| Qwen2.5-7B | `gptqmodel_torch` | ~11–13 | ~3.1 h |
| Qwen2.5-7B | `awq_gemm` | ~38–48 | ~10.5–12.4 h |
| Llama-3.1-8B | `awq_gemm` | ~25–36 | ~7.3–10.0 h |

Qwen AWQ decode works out to roughly **5 tokens/s on an A100** — far below what
the hardware supports, and slower than the *unoptimised* portable TORCH kernel
it is nominally an optimisation over. The asymmetry does not appear on MMLU:
AWQ and GPTQ MMLU cells both completed in ~1:02–1:12, because MMLU is scored by
log-likelihood and never enters the decode loop. It is generation-specific.

**Not acted on, deliberately.** `quantization_backend: awq_gemm` is registered
in `configs/pace_escalation_h3.yaml`, and 33 cells were already sealed at `0444`
under it. Swapping backends mid-grid would tune a registered parameter *and*
break comparability with frozen cells. Walltime was the only legitimate lever,
and it is the one that was pulled (22).

**Recorded because it is a finding, not only an obstacle.** A widely-deployed
4-bit kernel being ~3.6× slower than the reference implementation at batch 1 is
the kind of artifact this campaign exists to surface. It earns a sentence in the
paper's artifacts discussion. It changes nothing about this run's numbers.

## 24. A seal cannot cover a write path its author did not know existed (2026-07-25)

**Rerun: array `11494460`** (submitted 2026-07-26, ten cells, **outcome
pending**). Submitted only after the fix below, with the grid declared
explicitly and every control observed rather than assumed:
`ArrayTaskId=13,15,17,19,21,35,37,39,41,43`, `TimeLimit=20:00:00`,
`Partition=gpu-a100`, `QOS=inferno`, `MinMemoryNode=64G`. Amend with the
outcome when the cells land.

**Interim, 2026-07-26 13:40** — eight of ten landed, indices 41 and 43 still
running, so this is not yet the outcome. All eight `COMPLETED 0:0`, all exactly
1000 records, each sealed at `0444` as it landed. Elapsed 07:38:54–12:09:44: the
Llama arm 07:38–08:05, the Qwen arm 10:29–12:10.

**The 12 h counterfactual, stated precisely, because the loose version
understates it.** Under the pre-(22) walltime, index 19 (`12:09:44`) would have
been killed — and index 21 finished at `11:55:11`, clearing 12 h by **five
minutes**. Four of the five Qwen cells landed between 10:29 and 12:10. The arm's
distribution therefore *straddles* 12 h rather than sitting under it, and a
five-minute margin on a write-at-close job is not a margin at all: GSM8K writes
its JSONL only at the end, so a cell that crosses the wall loses everything, not
a suffix. The finding that generalizes is not "12 h would have killed one cell"
but **"12 h would have killed one cell and nearly killed another"** — the
inherited default was not slightly short, it was *inside the noise band of the
quantity it was bounding*. That is what makes a limit unsafe irrespective of
whether any particular run clears it, and it is why (22)'s rule asks what
configuration a limit was measured on rather than whether it looks big enough.

**Concurrency, for scheduling future arrays.** The array never ran wider than
**9** of its ten cells, and index 43 started at `10:48:36`, one second after
index 13 ended at `10:48:35` — a slot handoff, not a coincidence. The effect is
a ~19 h span for the rerun against ~12.4 h had it gone ten-wide; the tenth cell
alone contributes ~6 h of tail. Whether this is a QOS `MaxJobs`/`MaxSubmitJobs`
ceiling, an association limit, or simply A100 availability is **unresolved and
queued for the post-campaign hygiene batch** (`sacctmgr show qos inferno`,
`sacctmgr show assoc`) — it decides whether this is a constraint to plan array
width around or one to request a change to. Per the standing rule, the cap is an
*observation* of behaviour here, not a confirmed configured limit.

Note on the queue, since incident 21 turned on it: `gpu-a100` has
`PreemptMode=CANCEL`, and `sacctmgr show qos inferno` gives `Preempt=embers` —
`inferno` is the *preemptor*, not the preemptee. That asymmetry is why the
`embers` array `11476696` lost cells to preemption while `11477918` on `inferno`
did not. `Requeue=1` is reported on this job and remains inert under
`PreemptMode=CANCEL`; it is not load-bearing here.

**Evidence.** `sacct -j 11485972 --format=SubmitLine` →
`sbatch --parsable -A paceship-compressedlm -q inferno
--array=13,15,17,19,21,35,37,39,41,43 --chdir=... scripts/slurm/run_minigrid.sbatch`
(no grid declaration); ten identical tracebacks in
`logs/minigrid_11485972_*.err` at `pilot_eval/run.py:145`,
`PermissionError: [Errno 13] Permission denied:
'results/qwen25_1p5b_minigrid_h3/awq_s0.gsm8k.jsonl'`; log line
`minigrid cell: model=qwen25-1p5b method=awq_s0 task=gsm8k` against
`model=qwen25-7b` for the same index under `11477918`; archive manifest
`results/minigrid_run_20260722.manifest.json` recording
`results/*_minigrid_h3/manifest.json` at **`mode: 0o444`**; those same two files
found at `0644` with mtimes `20:57`/`21:00` matching the last qwen and llama
task starts; both corrupted files preserved at
`docs/forensics/20260725_wrongconfig/`.

### The mechanism, first

`os.replace()` is a **rename**. A rename needs write permission on the
**directory**. It does not consult the mode of the file it replaces. So this,
in `pilot_eval/run.py::_atomic_write`:

```python
temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
...
os.replace(temporary, path)
```

is entirely unaffected by `chmod a-w manifest.json`. The seal was applied. The
seal was correct. The seal was **irrelevant to that write path**. And because
the replacement file is newly created under the default umask, it lands at
`0644` — which is why the manifests were found writable afterwards, and why the
loss of protection is silent and self-erasing: the evidence that a file was
sealed is destroyed by the very write the seal failed to stop.

**File-level sealing therefore cannot stop an atomic-rename writer.** This is
not an incomplete control that missed some files. It is the *wrong control* for
that write path, and it would have failed on 100 % of files it was applied to.

### Two write paths in one program, indistinguishable at the convention level

`pilot_eval/run.py` writes its outputs two different ways:

| what | how | `0444` on the file stops it? |
|---|---|---|
| cell JSONLs | `out_path.open("w")` (line 145) | **yes** — `PermissionError` |
| `manifest.json` | temp file + `os.replace()` (line 89) | **no** — mode not consulted |

Nothing at the level the convention was written at — "`chmod a-w` on every JSONL
and `manifest.json` in the set" — distinguishes these. Both are "the program
writes a file in the run directory." The author enumerated the right files and
still got a control that worked on 44 of them and was inert on 2, with no signal
that the coverage was partial. **Enumerate-and-protect fails the moment the
thing you enumerated is not the thing that grants access.**

The fix is to seal the **container**: `chmod a-w` the run directory itself.
A read-only directory blocks rename-in-place, blocks new file creation, and
needs no knowledge of how any writer is implemented. Verified after sealing:
reads of `manifest.json` and the directory listing still succeed, and creating
any file in it raises `PermissionError`. `verify_minigrid.py` is unaffected —
it only reads run dirs, and writes its summary to the results *root*.

### What was actually written

The corruption was **purely append-only**, and coherent. Every scalar field —
`run_name`, `created_at`, `config`, `methods`, `tasks`, `loaded` — stayed
byte-identical to the archived original, and the existing `runs` prefix was
untouched. What changed was five appended run-start records per file:

```json
{"started_at": "2026-07-26T00:55:25+00:00", "methods": ["awq_s0"], "tasks": ["gsm8k"]}
```

`runs` went 23 → 28 and 22 → 27. The result is a manifest asserting that five
mini-grid AWQ GSM8K cells were re-run on Jul 26 when nothing was written and the
JSONLs are the Jul 22 originals. **It parses, it validates, and it is false** —
invisible to any check that asks whether the file is well-formed rather than
whether it is the same file.

### Proximate cause

The submission omitted `MINIGRID_CONFIG` and `MINIGRID_MODELS`. The exports had
lived in a terminal that was closed mid-campaign; the resubmit was composed in a
fresh shell where they were simply unset. The line also dropped the `--export=ALL`
that the working `11477918` line carried — but that was a symptom of recomposing
the line from memory, **not the cause**: `scontrol show config` shows no
`SBATCH_EXPORT` override, so Slurm's default `--export=ALL` was in force and
would have propagated the variables had they existed.

### Root cause

`scripts/slurm/verify_minigrid.sbatch` was hardened on 2026-07-21 so every grid
variable is required via `${VAR:?}` (incident 20). `run_minigrid.sbatch` was
not. **The hardening was applied to the reader and not to the writer.** So the
validator failed *closed* on a missing grid declaration, while the runner failed
*open* — into write mode, against whatever its default happened to point at.

That asymmetry is backwards from the risk. A validator with a default grid
returns a wrong answer. A runner with a default grid **destroys the other grid**.
The more dangerous of the two was the one left unguarded, for four days, while
the campaign's attention was on the one that had already been caught.

### The inverse of the accepted-but-inert family

Incidents 11, 21 and 22 share a shape: a control that *appeared* present and did
nothing — `--exclude` silently discarded by a `job_submit` plugin, `--requeue`
set and reported but defeated by `PreemptMode=CANCEL`, options after the script
path parsed as arguments.

This is the mirror image, and worth separating from them. The `0444` seal was
**genuinely present, genuinely correct, and genuinely worked** — on the write
path its author had in mind. It covered less than the author believed because
the program contained a second write path that was not in the author's model of
it. The lesson does not generalise to "verify your controls are in effect"; that
would have passed here. It generalises to **verify what your control is
attached to, and whether the access it governs is the access the writer needs.**

### "Nothing was lost" is conditional, and both conditions were luck

All 44 mini-grid JSONLs verified byte-identical to the archive by `sha256`
(44/44, both against the tarball and on disk). That outcome required **two**
independent protections, on two different write paths:

- the `0444` seal, which stopped `open("w")` on the JSONLs — created 2026-07-25
  as general prudence about a gitignored result set, **not** in anticipation of
  a runner defaulting to the wrong grid;
- the git-committed tarball, which is the only reason the manifests were
  recoverable at all — since the seal did not protect them, restoration was the
  *only* remedy available.

Neither was load-bearing by design at the time it was created. Had the archive
been made a day later, or the seal skipped as premature, this is a destroyed
confirmatory grid — archived, hash-verified, analysed, its escalation decision
signed and cited in the paper — with no version history to recover from. The
correct reading of this incident is not that the defences worked. It is that
**the campaign was one unrelated decision away from an unrecoverable loss, and
found out by accident.**

### Fixes

- `run_minigrid.sbatch`: `MINIGRID_CONFIG` and `MINIGRID_MODELS` required via
  `${VAR:?}`, defaults **removed entirely**; `SLURM_ARRAY_TASK_ID` required; the
  model list length-checked against the 2×22 index map and the resolved cell
  checked non-empty; the grid declaration echoed as the job's own first log line.
  Deliberately **no** `MINIGRID_RESULTS` — `pilot_eval.run` takes no results root
  and derives `run_dir` from the config alone, so requiring one would be a
  control that looks present and does nothing, i.e. this incident's own lesson
  applied in reverse. (A real version — `run.py` asserting the config-derived
  `run_dir` against an independently declared path — is queued for the
  post-campaign hygiene batch, as an assertion in code, not an env var.)
- `tests/test_run_minigrid_guards.py`: 12 tests driving the real script with a
  stubbed `srun`, so "did execution reach the container?" is a file-existence
  check. Includes a positive control, so an always-abort guard cannot pass, and
  static guards that the defaults cannot return and that runner and validator
  cannot drift apart again. In-image suite 183 → 195.
- Convention widened: **no job script is ever given a default grid** — reader or
  writer — replacing "validators must be told which grid they are validating".
- Convention corrected: **seal the container, not a file list.** Archive-and-seal
  now `chmod a-w`s the run directory as well as its files, with write restored
  per-file only for cells a pending job must write. Applied to both mini-grid
  directories on 2026-07-25; applies to the escalation directories the moment
  their validator passes.
- Manifests restored from `results/minigrid_run_20260722.tar.gz` and re-sealed,
  hashes confirmed `6e5057d6…` / `695e394d…`.

**Cost.** ~7 minutes of A100 time across ten jobs that died in 30–55 s each. No
data lost. The expensive part was that the ten escalation cells cancelled under
incident 22 went un-rerun for the time it took to find this, and that the finding
required suspecting a mode bit that had already been set correctly.

## 25. "The validator is model-agnostic" was verified for the models and not for the contract (2026-07-26)

**Status: RESOLVED 2026-07-26 under Amogh's ruling of the same day** — see
"Ruling and resolution" at the end of this entry. The account below is the state
at the stop, kept as written.

The escalation eval was complete and its validator had not run. Job `11509869`
**FAILED, ExitCode 1:0, after 1 second**, before a single acceptance check
executed:

```
File "/workspace/scripts/verify_minigrid.py", line 126, in verify_minigrid
    calibration = acceptance["calibration"]
KeyError: 'calibration'
```

`configs/pace_escalation_h3.yaml` declares a `minigrid_acceptance` block with
four keys — `expected_jsonl_files`, `expected_item_counts`,
`task_dataset_revisions`, `baseline_accuracy_ranges`. The mini-grid config
declares a fifth, `calibration` (`configs/pace_minigrid_h3.yaml:215-222`), and
the validator reads it with a **subscript** where it reads the other four with
`.get()`. Four of five acceptance keys are optional; the fifth is mandatory, and
it is the one the escalation config omits.

### The design confirmation that missed it

The reuse decision is on record: the validator is "config-driven +
model-agnostic … SAME validator works over an escalation config — no fork
(pending a scan for any model-specific hardcode)". That scan was run, and it
answered the question it was asked. **Model-agnosticism was the wrong property to
check.** `verify_minigrid.py` is genuinely indifferent to which models a config
declares — it iterates `models` and `run_name` — and it is simultaneously
*strict* about which acceptance keys the config supplies. The escalation config
was then written against the validator's *iteration* surface and not against its
*contract* surface, and nothing compared the two key sets. A diff of
`minigrid_acceptance` between the two configs would have shown this in one line,
at any point in the three days since `15dde30`.

This is the accepted-but-inert family inverted once more. Incident 24's version:
a control that passes for a reason other than the one its user believed. This
one: a control *scan* that passes because it examined the axis along which the
two grids agree, while the axis along which they differ went unexamined.

### Why it surfaced only now, and why that is the good case

The validator could not have been run earlier — it is deliberately not chained
`afterok` on the eval array, because the four FP16 gates must commit between
eval and validation, and until they did the config failed closed by design
(`test_escalation_validator_fails_closed_on_the_pending_state`). So the first
possible invocation was the first actual one. The failure is **fail-closed and
loud**: a `KeyError` at line 126, before any per-file work, exit 1, no summary
written. It could not have produced a green validation over an incomplete
contract, which is the outcome that would have mattered.

### What the missing block would have to say, and why that is still not mine to write

The values are not a judgement call and not unknown. Every escalation checkpoint
carries a build-time `calibration_manifest.json` recording `bits=4`,
`sample_count=128`, `sequence_length=2048`, and
`dataset={repo_id: allenai/c4, config: en, revision: 1588ec454efa…}`, with 128
document indices and 128 token hashes — byte-identical to the mini-grid protocol,
written when each checkpoint was built and therefore predating this failure by
days. The block that would satisfy the validator is a restatement of those
receipts and of `pace_minigrid_h3.yaml:215-222`.

It is nonetheless **not written here**, for the same reason the four FP16 gates
were committed all-or-nothing rather than filled in as they were derived: an
acceptance criterion added to a config *after* the cells it accepts already exist
is a criterion whose author knew what it would be applied to. That the values are
attested elsewhere is an argument Amogh can weigh; it is not an argument an agent
should act on unilaterally, and the standing order lists validator failure as a
hard stop. The cells are archived and sealed, so nothing degrades while this
waits.

### State at the stop

- **All 44 escalation cells exist**, at exactly {14042, 1000} records. Array
  `11494460`, all ten reruns COMPLETED `0:0`.
- **Archived** — `results/escalation_run_20260726.tar.gz` + `.sha256` +
  per-file manifest, commit `63176e9`, ARCHIVE_ROUNDTRIP PASS (48 files,
  159.5 MB → 13.1 MB).
- **Sealed** — both run directories `dr-xr-xr-x`, nothing writable inside, and
  the seal *proven at the mechanism* rather than read off the mode bits, per
  incident 24: `os.replace` into each directory refused with `PermissionError`
  errno 13, `open("w")` on a cell likewise. Probe targeted a non-existent
  filename so it could not clobber a cell; no residue.
- **Cell hash-match `11509865`: PASS, exit 0**, 2m12s. 22/22 Llama-8B cells
  hash-matched against reconstruction (14042 and 1000), cross-variant agreement
  at 1 distinct `prompt_hash` per item on both tasks, date invariant
  `Today Date: 26 Jul 2024` intact. Template/tokenizer drift between build time
  and eval time is ruled out.
- **Validator `11509869`: FAILED**, as above. It ran only because it was chained
  `afterok:11509865`, and the chain worked — the dependency was observed
  `PENDING Reason=Dependency ... (unfulfilled)` before release.

**No accuracy was read from any confirmatory cell at any point.** The hash-match
reads `item_id` and `prompt_hash` only; the validator died before its FP16 gate.

**Without the gate:** nothing silent. The validator fails closed on a missing
mandatory key, so the alternative to catching it here was catching it on whatever
day someone next ran the validator. The real cost is ordering — the escalation
result set is complete, archived, sealed and hash-matched, and cannot be
certified until a five-line acceptance block is ruled on. The lesson is narrower
than incident 24's and worth stating on its own: **when a component is reused
across grids, diff the contract, not the code path.** "It is model-agnostic"
answers a question about the code; "it accepts what this config supplies" is a
question about the pair, and only the second one predicts whether the run works.

### Ruling and resolution (Amogh, 2026-07-26)

Approved, with the direction of authority reversed: **derive the block from the
frozen registration, then verify the mini-grid config against what was derived**
— never copy the mini-grid config forward. The reason is precise. That config's
calibration block had only ever been validated against mini-grid *builds*, which
proves the builds match the config and says nothing about whether the config
matches the registration. Copying it forward would propagate any drift into the
escalation grid and would mean the already-published mini-grid had been accepted
against a criterion that never matched its own registration.

**Three-way comparison — ALL SEVEN KEYS AGREE.** Derived mechanically from
`configs/main_grid_manifest.yaml` (FROZEN 2026-07-13), which is machine-readable
and pins six of the seven directly, plus
`docs/ESCALATION_STAGE_PLAN_2026-07-23.md` § 1 ("at 4-bit, GPTQ and AWQ") for
`bits`, the frozen manifest permitting `[4, 3]` with 3-bit deferred:

| key | frozen source | derived | mini-grid config |
|---|---|---|---|
| `dataset` | manifest `calibration_datasets.c4.repo_id` | `allenai/c4` | matches |
| `dataset_config` | manifest `calibration_datasets.c4.config` | `en` | matches |
| `dataset_revision` | manifest `calibration_datasets.c4.revision` | `1588ec454efa1a09f29cd18ddd04fe05fc8653a2` | matches |
| `sample_count` | manifest `calibration.sample_count` | `128` | matches |
| `sequence_length` | manifest `calibration.sequence_length` | `2048` | matches |
| `bits` | escalation plan § 1 | `4` | matches |
| `paired_seeds` | manifest `calibration.seeds` | `[0, 1, 2, 3, 4]` | matches |

Independently corroborated by `PREREGISTRATION.md` (FROZEN 2026-07-11) line 34:
128 samples of exactly 2,048 tokens from `allenai/c4` configuration `en`, seeds
`{0,1,2,3,4}`, GPTQ seed `s` and AWQ seed `s` receiving identical ordered
samples. **The mini-grid config matches its registration exactly** — worth having
on the record, because it retroactively strengthens the provenance of a result
set that has already been published.

**The signed plan enumerates NO acceptance criteria — a third possibility.** The
ruling anticipated two cases: the plan lists five keys (the config contradicted
its own plan) or four (the omission propagated from the plan). Neither holds.
`docs/ESCALATION_STAGE_PLAN_2026-07-23.md` describes the validator's *role* — a
line in the job inventory (§ 2) and step 6 of the sequence, both saying
"fail-closed over the complete new-cell set" — and never enumerates the
acceptance contract at all. So the omission did not propagate from the plan and
did not contradict it: **the config was authored with no signed enumeration to
check against.** That is a gap in the plan template as much as in the config, and
it is the true fact this entry asserts.

**Disclosure.** Before the ruling, while establishing that the values were not in
doubt, this session **did read** `outputs/quantized/qwen25-7b-awq4-seed0/calibration_manifest.json`
and saw `bits=4`, `sample_count=128`, `sequence_length=2048`, C4 `en`
@`1588ec454efa…`, 128 document indices and 128 token hashes. So the block was
written by an author who already knew what the check would find. It does not
invalidate the transcription — every written value traces to a frozen document,
and the diff is the falsifiable evidence of that — but this project discloses
"I knew what the answer would be" rather than omitting it, per the mini-grid's
own precedent.

**PRE-COMMITTED BEFORE THE BLOCK WAS EVER EVALUATED, in the ruling's words:**

> IF THE CALIBRATION CHECK FAILS, THAT IS A FINDING ABOUT THE BUILDS, NOT A
> DEFECT IN THE CRITERION. The response is to report the deviation, not to
> loosen, scope down, or make optional any part of the block. A criterion
> transcribed from a document frozen fifteen days before the cells existed does
> not get relaxed because cells fail it. If it fires, we stop, and we work out
> what the builds actually did.

**Hardening — a declared required set, not pairwise equality.**
`verify_minigrid.py` now declares `REQUIRED_ACCEPTANCE_KEYS` as an explicit
constant, validates the acceptance block against it **up front**, and raises
`MissingAcceptanceKeys` naming **every** missing key rather than whichever one a
subscript reaches first. All five keys are read through one accessor,
`acceptance_value`; the `.get()`/subscript split that caused this is gone, and
`expected_jsonl_files` lost an `is not None` guard that had made a "required"
count optional in practice.

*One documented departure from the literal instruction.*
`baseline_accuracy_ranges` is **not** in the required tuple. It has a registered
absent-state — a config may omit it while declaring
`baseline_accuracy_ranges_status: pending-…`, which is exactly how the escalation
config legitimately sat between its eval fan-out and its four-gate commit, and is
covered by `test_escalation_validator_fails_closed_on_the_pending_state`. Putting
it in the raising set would have deleted that state. It is instead named as
`GATED_ACCEPTANCE_KEY` and still fails closed as a check. Both classes fail
closed; the asymmetry is now declared with its reason, which is what separates it
from the accidental split this incident was about.

Four new tests (in-image suite **195 → 199**, job `11510834`,
`199 passed, 2 warnings`, `IN_IMAGE_PYTEST_EXIT: 0`): the required set asserted
over **every** config under `configs/` that declares an acceptance block — found
by inspection, so a third grid config is covered the day it is committed, where a
pairwise comparison between two named files would silently stop covering anything
— plus the pairwise contract-diff kept as the secondary check, the incident-25
regression itself, and an assertion that missing keys are reported together. The
pairwise test deliberately uses no `pytest.skip`: an in-image skip is a gate
failure here, so it degrades to a vacuous pass instead of a false alarm.

**A passing check on the wrong property is now the fourth instance this month**
of a control that verified something adjacent to its purpose — after the `0444`
seal (24), the validator's run-dir check (20), and the C1 pre-submission check
for array `11494460` (24). The other three were controls whose *justification*
was wrong; this one is a *scan* that examined the axis along which the two grids
agree while the axis along which they differ went unexamined. Same family, one
step earlier in the process: it is possible to verify the wrong property before
there is any control to justify.

## 26. The archive convention covers directories, and the validator's output path is a default (2026-07-26)

**Status: RESOLVED 2026-07-26.** Two findings, in the order that matters.

### The finding: the archive convention has a hole, and both validation summaries were in it

The standing preservation convention protects a completed confirmatory set by
archiving it and sealing it. Both operations take **run directories**:
`minigrid_run_20260722.tar.gz` holds the two mini-grid run dirs and nothing else,
`escalation_run_20260726.tar.gz` the two escalation ones. **Loose artifacts at
the results root were therefore never archived at all** — not by oversight in a
particular run, but because the convention has no clause that reaches them.

`results/minigrid_validation_summary.json` is one of those artifacts. It is the
fail-closed validation of the mini-grid over its complete 44-cell set, it is
cited by `docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md`, and it existed in
exactly one place on disk, gitignored, with no archive and no history. The same
was true of the escalation summary the moment it was written.

That is the finding. The clobber below is how it surfaced; it is not the reason
the gap mattered. Any `rm`, any scratch purge, any mis-specified `--output` would
have destroyed a record backing a signed decision, and nothing would have noticed.

**Convention extended (CLAUDE.md / AGENTS.md):** a completed validation summary
is part of the confirmatory record and is preserved with it. Both summaries are
now allowlisted into git directly rather than tarballed — 50 KB of JSON does not
need compression, and version history is precisely the protection that was
missing.

### How it surfaced: a default output path named after one grid

Immediately after the escalation validator passed (job `11511179`),
`results/minigrid_validation_summary.json` was found holding the **escalation**
summary: 415 checks over `qwen25-7b` / `llama31-8b`, mtime 21:46. The mini-grid's
own summary — 409 checks over `qwen25-1p5b` / `llama32-3b`, written 2026-07-22
21:35 — had been overwritten.

**Mechanism.** `verify_minigrid.py` defaults `--output` to
`RESULTS_ROOT/minigrid_validation_summary.json`, and `verify_minigrid.sbatch`
never passes `--output`. Both grids share one results root, so **both grids'
validators write the same filename.** The escalation invocation was correct in
every respect the campaign has hardened — `MINIGRID_CONFIG`, `MINIGRID_RESULTS`,
`MINIGRID_MODELS` and `MINIGRID_CELLS` all declared, the grid confirmed from the
job's own first log line — and it still clobbered the other grid's record,
because none of those controls governs where the output lands.

This is incident 24's rule pointed at the one place it was not applied. That rule
was widened to *"every job script that reads **or writes** a grid must be told
which grid, with no fallback"*, and the validator was treated as the reader of
the pair. It reads the grid and **writes a summary**, and its write path kept a
default named after the grid it was originally built for.

**Recovery.** The file was gitignored and untracked, so there was no history to
restore from — but the validator prints the complete summary to stdout before
writing it, so `logs/verify_minigrid_11375247.out` held the mini-grid summary
verbatim. Restored from that log through the same serializer
(`json.dump(..., indent=2)` plus a trailing newline): **50,143 bytes, byte-for-byte
the pre-clobber size** recorded in this session's first listing of `results/`.
The escalation summary was preserved first, under
`results/escalation_validation_summary.json`. Both now exist; neither validation
has to be re-run.

**Restore verified against a signed record, not against its own source.** Size
equality is corroboration and nothing more — it would hold for any file the same
serializer produced. The restored summary was therefore cross-checked against the
four quantities `docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md` cites
independently of the log it was recovered from: job `11375247`, **409 checks**,
`passed: true`, **44 cells**. All four match, and the models in it are
`qwen25-1p5b` / `llama32-3b`. The restore is confirmed against the signed record.

**Cause fixed (authorized 2026-07-26).** `--output` is now **required** in
`verify_minigrid.py` — the default is deleted, not overridden — and
`MINIGRID_OUTPUT` is required in `verify_minigrid.sbatch` via `${VAR:?}`, in the
same shape as the runner's grid variables, echoed in the job's own declaration
line alongside config, results, models and cells. Two tests: the CLI must refuse
to run without `--output`, and a static guard pins both the `${VAR:?}` form and
the absence of the old default string, since a behavioural test cannot catch a
default reintroduced beside a guard. In-image suite **199 → 201**.

**What made this survivable was an accident.** The summary is recoverable only
because the validator happens to `print` it before writing it. Had it written
silently, a completed validation record backing a signed decision would have been
destroyed with no copy anywhere — which is the archive gap above, arriving as a
near miss rather than as a loss.

**Without the gate:** it would have gone unnoticed indefinitely. Nothing checks
that file's mtime or content, no test covers the output path, and both summaries
say `"passed": true` — so the only symptom was a filename whose contents belonged
to the other grid. It was caught because the clobbered file was listed at the
start of this session and again after, not because any control fired.

## Cross-cutting patterns

Recorded because they recur, not as a summary.

**Controls that report success while doing nothing.** Three of these are now
*scheduler* controls specifically: `--exclude` accepted and discarded (11),
`--requeue` set and inert under `PreemptMode=CANCEL` (21), and sbatch options
placed after the script path and parsed as script arguments (21). Every one was
accepted at submission, `sbatch` exited 0, and nothing was in force. Hence the
`AGENTS.md` rule: **a scheduler control is not in effect until independently
observed** — `scontrol`, the QOS/partition config, or behaviour. Outside the
scheduler: the test-count expectation held at 145 (14); the mocked
`gptqmodel` unit test certifying a runtime it never touched (1); `verify_bridge.py`
checking a different file than the plan required (6); the validator's own
run-dir check, skipped for one gate run because it branched on a function
returning `None` (20). Every one passed. The
project's response has been to make controls **verify after the fact** —
`scontrol` after submission, exact test counts rather than floors, a real GPU
canary, and receipt gating by vintage against git history.

**Controls that pass for a reason other than the one their user believed.** A
narrower and nastier relative of the family above: the control is real and its
result is correct, but the stated grounds for trusting it are false — so it goes
on passing until the mechanism nobody examined changes, and the passing record
is not evidence about the mechanism anyone cited. Three instances in the week of
2026-07-19, which is what makes it a pattern rather than a coincidence:

- The `0444` seal (24). It did hold the 44 JSONLs — but against `open("w")`
  only, while the two `manifest.json` files it was equally believed to cover fell
  to `os.replace`, which needs directory write and never touches the target's
  mode. "The set is sealed" was true for a narrower reason than believed.
- The validator's run-dir check (20), green because it branched on a helper
  returning `None`, not because the run dir was right.
- The pre-submission **C1 check** for array `11494460`, which compared the
  proposed `MINIGRID_CONFIG` against `manifest["config"]`, justified as "the
  value the run that produced 33 good cells used." It is not that.
  `merge_manifest` (`pilot_eval/run.py:30-37`) sets `run_name`, `created_at` and
  `config` **only on the branch that creates the file**, so the field records
  whichever escalation job wrote the manifest *first* — plausibly `11476696`
  rather than `11477918`. The check passed correctly, because every legitimate
  escalation job used the same config; it would have passed just as readily had
  the first writer been an illegitimate one, which is precisely the case it was
  put there to catch.

The remedy is the same in all three: name the mechanism the control actually
exercises, and confirm that mechanism is the one that matters. A control whose
justification is wrong is not a control that happens to work — it is an
untested control with a passing record attached.

**Scale-inherited assumptions.** Code written against the 1.5 B/3 B mini-grid
carries assumptions that are true at that scale and false at 7 B/8 B, and they
surface only when the larger models run: device memory 40 GB → 80 GB and host
memory 64 G → 128 G (18), then single-file → 2-way-sharded weights (19), then
walltime 12 h → 20 h (22). Four in one stage. Resource breaches announce
themselves as an OOM; layout and shape
assumptions do not, and can return success over data they never read — so the
rule adopted at (19) is that a fix for one of these must be proven to do the
*whole* job (all shards opened, counts summing to the manifest), never merely to
stop erroring. Anything ported from the mini-grid era is suspect until the
larger models have actually exercised it.

The walltime case (22) sharpens the shape of the family: **a value correct for
the configuration it was written against is silently wrong for the one it is
applied to**, and the giveaway is that it was never *measured* against the new
configuration. The 12 h came from an FP16 genspeed probe and governed quantized
cells that had never been timed; 40 GB was measured on 3 B and applied to 7 B.
Each was a real measurement, reused past its domain. When a limit is inherited,
the question is not "is it big enough?" but "what configuration was it measured
on, and is that the one it now governs?"

**Defects found by comparison, not by reading.** The AWQ receipt's borrowed
resources (8) and the sick GPU (10) were both individually plausible and only
visible against a sibling. Neither had a downstream check that would have caught
them.

**Logging the symptom instead of the cause.** F4 hid F2 for six days (5); the bare
`SystemExit` masked the GPTQ import chain (1); a `PermissionError` surfaced as two
failing tests (13). All three were fixed by recording root cause at the point of
failure.

**Stops that were surfaced rather than adapted around.** The fewshot registration
inconsistency (2), the six pre-writer receipts (9), the two design stops in the
sensitivity registration, the preflight failure (15), and the Llama MMLU gate
(16). In each case the adaptation was available and cheaper, and was not taken.

**Probes that reported on themselves.** Entry 15's preflight declared six flags
absent that the harness accepts, because it probed a subcommand CLI at top level
and matched `--tasks` in example prose. Its replacement carries a positive
control — a flag vector known to have run — on the principle that a probe whose
control fails is reporting on the probe. The prompt-identity probe of entry 16
applies the same rule differently: it recomputes `prompt_hash` and matches it
against the sealed cells, so the prompts it prints are proven to be the ones
scored rather than the ones the code appears to build.
