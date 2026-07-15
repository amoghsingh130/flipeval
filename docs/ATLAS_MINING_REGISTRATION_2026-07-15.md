# Public Per-Item Atlas Mining Registration

Status: **FROZEN 2026-07-15**, by the commit containing this line — before any
flip statistic from these sources was computed beyond the two feasibility
probes disclosed in §1. Deviations require a dated entry under Dated
Amendments stating whether results were inspected before the decision.

Purpose: extend the Compression Flip Atlas with paired per-item records mined
from public evaluation dumps, at zero GPU cost. These analyses are
**descriptive/exploratory**: they estimate flip and churn magnitudes in the
wild and feed the certification tables. They test no registered hypothesis and
cannot substitute for any H3 cell. This protocol is registered to prevent
source- or pair-selection after seeing results.

## 1. Disclosure of pre-registration data contact

Two feasibility probes were run on 2026-07-15 before this draft was written,
and their results are known: (a) TheBloke/Llama-2-7B-GPTQ vs
meta-llama/Llama-2-7b-hf on ARC-Challenge (74/1,170 flips, net −1.03 pp), and
(b) neuralmagic Llama-3.1-8B baseline vs W4A16 on bbh_boolean_expressions
(17/250 flips, net +1.2 pp). These two cells are flagged `probe=true` in the
atlas and excluded from any aggregate statistic quoted in the paper's abstract
or headline claims.

## 2. Sources (fixed; no additions after freeze without a dated amendment)

- **S1 — Open LLM Leaderboard v1 archive** (`open-llm-leaderboard-old` details
  datasets; public, ungated; no declared license — recorded as a limitation in
  the datasheet).
- **S2 — Neural Magic/Red Hat per-item dumps**: `neuralmagic/
  quantized-llama-3.1-leaderboard-v2-evals` (Apache-2.0) and, if their
  per-item schema validates, the companion arena-hard and humaneval datasets.

## 3. Pair enumeration rule (run BEFORE any flip computation)

1. Enumerate all S1 details datasets whose model name matches, case-insensitive,
   any of: `GPTQ`, `AWQ`, `GGUF`, `8bit`, `4bit`, `bnb`. For each, identify the
   base model from the quantizer's model card; include the pair iff a details
   dataset exists for that exact base model.
2. Within a pair, use the latest run timestamp per task for each side unless
   prompt-hash agreement (rule §4.2) fails, in which case try earlier run
   combinations in reverse-chronological order and record the choice.
3. S2 pairs are the nine baseline×{W4A16, W8A8-INT8, W8A8-FP8} combinations at
   8B/70B/405B, all tasks present in the dump.
4. The frozen pair list (a machine-readable manifest with dataset URLs, run
   timestamps, and task lists) is committed as
   `docs/atlas_pair_manifest.json` **before** flip statistics are computed.
   Pairs discovered later require a dated amendment here.

## 4. Item pairing validity rules (mechanical)

1. Join key: S1 `hashes.example`; S2 `doc_id` with byte-identical `doc`
   (or `doc_hash` where present). Duplicated join keys within a file are
   dropped entirely (both occurrences) and counted.
2. An item enters the paired analysis iff its full-prompt hash (S1
   `hashes.full_prompt`; S2 `prompt_hash`) is identical across the pair.
   A pair-task cell is **excluded** iff fewer than **99%** of joinable items
   pass this identity check; exclusions are reported with their rates.
3. Per cell, record both sides' harness identity (lighteval/lm-eval git SHA,
   model args, dtype) verbatim from the results JSON. Differing harness SHAs do
   not exclude a cell (prompt-hash identity is the operative control) but are
   recorded and disclosed per cell.

## 5. Metrics (identical to the controlled-atlas suite)

Per cell: net accuracy delta, harmful/beneficial flip rates, accuracy-state
churn, total answer churn where raw predictions exist, exact two-sided McNemar,
TOST at the registered 2 pp margin, minimum detectable difference at 80% power,
and required-n. Primary correctness column: `acc_norm` where present, else
`acc` (S1); the task's primary metric as logged (S2); the choice is recorded
per cell. No cell-level results drive inclusion/exclusion decisions.

## 6. Reporting

All enumerated, non-excluded cells are reported in the atlas regardless of
outcome. Aggregates over cells are accompanied by the cell count and the
exclusion table. The `probe=true` cells of §1 appear in the atlas but not in
headline aggregates.

## Dated Amendments

None.
