# Mini-Grid Registration: Scope, Escalation Rule, and Reporting

Status: **FROZEN 2026-07-15**, by the commit containing this line, before any
mini-grid job exists and before any mini-grid accuracy result was inspected.
Deviations require a dated entry under Dated Amendments stating whether results
were inspected before the decision.

This document does not amend `PREREGISTRATION.md` (frozen 2026-07-11). It
constrains the experimenter for a staged subset of the registered grid. The
registered H3 protocol, metrics, and decision rule are unchanged.

## 1. Scope

The mini-grid executes exactly 4 of the 8 registered confirmatory H3 cells:

`{Qwen2.5-1.5B-Instruct, Llama-3.2-3B-Instruct} × {MMLU, GSM8K}`

at 4-bit, GPTQ and AWQ, calibration seeds {0,1,2,3,4}, paired C4 calibration
sets per the registered sampling algorithm. Pinned model, dataset, and benchmark
revisions are those in `configs/main_grid_manifest.yaml`. The 7B/8B cells
(Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct × MMLU, GSM8K) are deferred and
executed only if the escalation rule in §3 fires.

## 2. Benchmark execution parameters not fixed by the preregistration

- GSM8K few-shot count for all mini-grid (and any later confirmatory) cells:
  **1 few-shot example, inline in the user message — matching the validated
  bridge configuration `configs/pace_bridge_chat.yaml`**.
- GSM8K items: test indices 0–999 in dataset order. MMLU: full test split.
- Chat template ON for every method including FP16 baselines (registered).
- Llama-3.2-3B FP16 operational acceptance ranges: to be derived from a trusted
  lm-evaluation-harness reference run on the pinned snapshot (procedure of
  `docs/MMLU_REFERENCE_RUN.md`) and committed into the mini-grid config
  **before any quantized Llama-3.2-3B result exists**. This registration
  deliberately freezes the derivation procedure, not the values; the values are
  recorded in the mini-grid config commit and are operational gates only.

## 3. Escalation rule (mechanical, pre-committed)

Compute, per the frozen algebra of `PREREGISTRATION.md`, for each of the 4
cells at 4-bit: winner flips across seeds (ties counted separately, per the
registered tie rule) and the range/gap criterion
`max(range_GPTQ, range_AWQ) >= gap`.

**Escalate** to the deferred 7B/8B seed cells iff:

- winner flips occur in **at least 1 of the 4 cells**, OR
- the range/gap criterion holds in **at least 2 of the 4 cells**.

If neither condition holds, the 7B/8B cells are not built, and no other result
(3-bit, other benchmarks, atlas findings) can substitute to trigger escalation.

## 4. Relation to the frozen H3 decision rule

The registered Supported/Disconfirmed/Inconclusive rule is defined over all 8
confirmatory cells. Therefore:

1. If escalation fires and all 8 cells complete, the frozen rule is applied
   exactly as registered.
2. If escalation does not fire (or the 7B/8B cells are otherwise not run), the
   paper reports the 4 completed cells **descriptively**, and H3 is reported as
   **formally inconclusive under the registered rule** — never as supported or
   disconfirmed on 4 cells. No reduced-cell variant of the rule will be
   constructed after results are seen.
3. The registered secondary analyses (3-bit dose-response, ARC-Challenge,
   HellaSwag, WikiText-2 calibration-distribution contrast) remain deferred
   with the rest of the main grid and are not part of the mini-grid.

## 5. Analysis and inspection discipline

- During fan-out, only job health, checksums, expected-file coverage, and
  receipt pairing are inspected (runbook grid discipline). First accuracy
  inspection happens only after the mini-grid validator passes over the
  complete 44-JSONL expected set.
- The registered hierarchical analysis (`flipeval paired-seeds`, 2000
  replicates, bootstrap seed 0) is run once per cell; the escalation rule in
  §3 is then applied mechanically and a dated escalation decision record is
  written the same day.
- The paired-bootstrap rank-flip denominator convention (tie replicates
  included in the denominator, ties also reported separately) is the one
  implemented and documented in `flipeval/core.py` as of commit `a8ba9f0`;
  it is hereby fixed in words and will not be re-chosen after inspection.

## Dated Amendments

None.
