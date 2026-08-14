# FlipEval

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21708922-blue.svg)](https://doi.org/10.5281/zenodo.21708922)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)

**Paired, per-item statistics for deciding whether a compressed model is
equivalent to its baseline.**

FlipEval is a small, dependency-light Python library and CLI. Give it two sets
of per-item evaluation records, a baseline and a compressed or otherwise
modified model, and it reports what a net accuracy delta hides: how many
individual answers changed, in which direction, whether the difference is
statistically detectable, whether the two models are statistically
*equivalent* at a margin you declare, and how many items you would have needed
to decide.

## Why per-item, and not a net delta

Compressed models are routinely released with a sentence like "negligible
degradation" or "99.x% recovery", supported by a fraction of a point of
aggregate benchmark accuracy. That is an equivalence claim, and a net accuracy
delta is weak evidence for it.

A net delta is the residue left after per-item changes in opposite directions
cancel. The more alike two models are, the more completely those changes
cancel. So the quantity used to argue two models are the same is least
informative exactly where that argument is made. Across an atlas of 1,707
paired model-by-task cells mined from public per-item evaluation dumps, the
ratio of median accuracy-state churn to median absolute accuracy change is
5.40; between two compression methods at the same bit width the median of the
per-cell ratios is 12.7x, against 3.85x on that same aggregation in the atlas.

FlipEval measures the churn directly and supplies the decision apparatus that
goes with it: a declared margin, a paired equivalence test, and required
sample sizes computed from disagreement actually observed under compression
rather than from independent-binomial variance.

## Install

```bash
python -m pip install -e .
```

Requires Python 3.9 or newer (developed and tested on 3.11). Runtime
dependencies are `numpy>=1.26` and `scipy>=1.12`.

To run the test suite:

```bash
python -m pip install -e ".[test]"
pytest
```

## Quickstart

### As a library

```python
from flipeval import compare
from flipeval.io import read_jsonl

baseline = read_jsonl("fp16.mmlu.jsonl")
method = read_jsonl("gptq.mmlu.jsonl")

result = compare(baseline, method, margin=0.02, bootstrap=1000, seed=0)

print(f"net delta        {result.net_accuracy_delta:+.4f}")
print(f"churn            {result.accuracy_state_churn:.4f}")
print(f"harmful flips    {result.harmful_flip_rate:.4f}")
print(f"beneficial flips {result.beneficial_flip_rate:.4f}")
print(f"McNemar p        {result.mcnemar_p:.4g}")
print(f"equivalent at 2pp? {result.tost_equivalent}")
```

A typical result shows the point of the tool: a net delta near zero sitting on
top of a churn rate several times larger, with `tost_equivalent` returning
`False` because the sample was never large enough to certify equivalence in the
first place.

### As a CLI

```bash
# The paper's five-line reporting standard for one model pair.
flipeval report fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --benchmark mmlu

# How many items a declared margin costs, before you run anything.
flipeval required-n --benchmark mmlu --margin 2.0
flipeval required-n --list

# Pairwise comparison. Writes a one-row CSV and prints the full result.
flipeval compare fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --output comparison.csv

# Read lm-evaluation-harness --log_samples output directly. `report` and
# `compare` both take either a --log_samples file or the output directory.
flipeval compare baseline_samples.json method_samples.json --format lm-eval
```

`--margin` is a **proportion** for `report` and `compare` (`0.02` is two
accuracy points), because they compare it against accuracies, and **percentage
points** for `required-n` (`2.0`), because the published certification table is
in points. Both sides range-check the argument and say which unit they wanted.

`examples/` is a runnable end-to-end walkthrough of this workflow against
`lm-evaluation-harness` output, with a deterministic fixture, so it runs with no
GPU, no model download and no harness install. Start at `examples/README.md`.

## Does it work as a library?

Yes. The library is the primary interface and the CLI is a thin wrapper over
it. Everything below is importable, stable, and covered by the test suite.

### Top-level API (`from flipeval import ...`)

| Name | Kind | Purpose |
|---|---|---|
| `compare` | function | Pairwise baseline-vs-method comparison. Returns `ComparisonResult`. |
| `five_line_report` | function | The paper's five-line reporting standard for one pair. Returns `FiveLineReport`. |
| `required_n_for_benchmark` | function | Required *n* by benchmark family and margin, read from the published certification table. Returns `RequiredN`. |
| `required_n_from_discordance` | function | The same arithmetic for a family the table does not cover, from a measured discordance rate. Returns `int`. |
| `rank_stability` | function | Bootstrap rank-flip rate across two or more methods. Returns `RankStabilityResult`. |
| `paired_seed_bootstrap` | function | Two-level (seed, item) bootstrap for two methods across matched calibration seeds. Returns `HierarchicalBootstrapResult`. |
| `required_n_for_effect` | function | Items needed to resolve a given effect, from observed paired deltas. Returns `int` or `None`. |
| `minimum_detectable_difference` | function | Smallest effect resolvable at the given n, alpha and power. Returns `float`. |
| `ComparisonResult` | dataclass | Frozen result record, see fields below. |
| `FiveLineReport` | dataclass | The computed block (`to_text()`, `to_dict()`) and every number behind it. |
| `RequiredN` | dataclass | One certification-table row: the family, the margin, the p25/median/p75 churn rates and their required counts. |
| `RankStabilityResult` | dataclass | `methods`, `n_common_items`, `full_sample_winner`, `rank_flip_rate`, `deltas`. |
| `PerSeedBootstrapResult` | dataclass | Per-seed slice of the hierarchical result. |
| `HierarchicalBootstrapResult` | dataclass | Joint intervals, seed-level SD, item-level SE, per-seed breakdown. |

All result types are `@dataclass(frozen=True)`, so they are hashable, safe to
pass around, and convert cleanly with `dataclasses.asdict()` for serialization.

### `ComparisonResult` fields

```
n                              paired item count
baseline_accuracy              accuracy of the baseline records
method_accuracy                accuracy of the method records
net_accuracy_delta             method_accuracy - baseline_accuracy
harmful_flip_rate              correct -> incorrect, as a rate
beneficial_flip_rate           incorrect -> correct, as a rate
accuracy_state_churn           harmful + beneficial, the quantity the net delta hides
wrong_to_different_wrong_churn answer changed, both wrong
total_answer_churn             any change of predicted answer
confidence_intervals           dict of metric -> (low, high), bootstrap percentile
mcnemar_b_harmful              discordant pair count, harmful direction
mcnemar_c_beneficial           discordant pair count, beneficial direction
mcnemar_p                      exact McNemar p-value
tost_equivalent                True if equivalent at the declared margin
tost_p_low, tost_p_high        the two one-sided test p-values
```

### Planning helpers

These take an array of per-item paired deltas and answer the "how many items do
I need" question. Both are exported at the top level:

```python
import numpy as np
from flipeval import minimum_detectable_difference, required_n_for_effect

deltas = np.array([...])  # per-item (method_correct - baseline_correct), in {-1, 0, 1}

minimum_detectable_difference(deltas, alpha=0.05, power=0.80)        # -> float
required_n_for_effect(deltas, effect=0.02, alpha=0.05, power=0.80)   # -> int | None
```

Because the variance is estimated from the observed paired deltas rather than
assumed binomial, `required_n_for_effect` returns substantially different
numbers from a standard unpaired power calculator. That difference is the
point.

A lower-level `tost_equivalence(deltas, margin=0.02, alpha=0.05)` is available
as `flipeval.core.tost_equivalence`. It is not exported at the top level because
`compare()` already surfaces the same test through `ComparisonResult`, and
unlike `compare()` it takes deltas rather than records.

### I/O helpers (`from flipeval.io import ...`)

```python
from flipeval.io import read_jsonl, from_lm_eval_harness

records = read_jsonl("gptq.mmlu.jsonl")
records = from_lm_eval_harness("samples.json")
```

These stay in `flipeval.io` rather than at the top level, so
`from flipeval import read_jsonl` will fail. Import them from the submodule as
shown.

## Input format

Each native record is a mapping that must contain:

| Field | Type | Meaning |
|---|---|---|
| `item_id` | str | Stable identifier used to pair records |
| `prediction` | str | The model's predicted answer |
| `correct` | bool | Whether the prediction was scored correct |

```json
{"item_id": "mmlu:0", "prediction": "B", "correct": true}
{"item_id": "mmlu:1", "prediction": "D", "correct": false}
```

Paired records are aligned by `item_id`. **Duplicate IDs are rejected** and
comparison fails closed rather than silently dropping or reordering items.

The `lm-evaluation-harness` adapter targets the v0.4.x `--log_samples` schema
(represented by v0.4.12) and accepts a full result JSON with a `samples`
mapping, a sample JSON/JSONL file, or the `--output_path` directory the harness
wrote, which is searched recursively for `samples_<task>_<timestamp>.jsonl` and
concatenated. Loglikelihood tasks (MMLU-style) and generative tasks (GSM8K-style)
are both handled; for generative tasks the prediction is the harness's own
filtered answer, so scoring stays the harness's decision rather than ours.

## Calibration-seed analysis

The registered seed-paired analysis takes explicit `SEED=PATH` pairs, so the
pairing is declared rather than inferred from filename order:

```bash
flipeval paired-seeds \
  --first  0=gptq_s0.jsonl --first  1=gptq_s1.jsonl --first  2=gptq_s2.jsonl \
  --first  3=gptq_s3.jsonl --first  4=gptq_s4.jsonl \
  --second 0=awq_s0.jsonl  --second 1=awq_s1.jsonl  --second 2=awq_s2.jsonl \
  --second 3=awq_s3.jsonl  --second 4=awq_s4.jsonl \
  --expected-seeds 5 --bootstrap 2000 --output hierarchical_summary.json
```

Or from Python:

```python
from flipeval import paired_seed_bootstrap

result = paired_seed_bootstrap(
    first_records_by_seed={s: read_jsonl(f"gptq_s{s}.jsonl") for s in range(5)},
    second_records_by_seed={s: read_jsonl(f"awq_s{s}.jsonl") for s in range(5)},
    method_names=("gptq", "awq"),
    bootstrap=2000,
    expected_seed_count=5,
)
print(result.joint_rank_flip_rate, result.seed_level_accuracy_sd)
```

This analysis **fails closed** unless both methods and all seeds contain exactly
the same item IDs. It reports per-seed item-bootstrap intervals, seed-level
accuracy SD, item-level SE, a paired seed-by-item interval, joint rank-flip
rate, and exact-tie rate. A repeated seed draw receives an independent item
resample, while both methods retain the same seed occurrence and item indices.

## Reproducibility

Bootstrap results are deterministic for a given seed. Ties are reported
separately and never counted as flips. `python -m pilot_eval.analyze` remains
available as a compatibility CLI and uses FlipEval internally. The golden test
regenerates the archived pilot summaries from
`results/pilot_outputs_20260711T000427Z.tar.gz`.

This repository backs a preregistered study. Protocols were frozen before the
analyses they govern, and deviations are recorded as dated amendments rather
than edits. See `PREREGISTRATION.md` and `docs/` for the frozen protocols, and
`CLAUDE.md` for the working conventions that keep them intact.

## Paper and artifacts

FlipEval is the toolkit behind *Certifying Compressed Language Models: An Audit
and a Statistical Toolkit*.

- **Archived artifacts:** [10.5281/zenodo.21708922](https://doi.org/10.5281/zenodo.21708922) (concept DOI, always resolves to the latest version)
- **Per-item outputs and atlas:** [huggingface.co/datasets/AmoghSingh123/flipeval-artifacts](https://huggingface.co/datasets/AmoghSingh123/flipeval-artifacts)

Everything the paper reports, from the per-item outputs behind every controlled
result to the atlas, the audit table, the analysis package and the reproduction
package, is archived at the DOI above.

### Citation

```bibtex
@software{singh_flipeval,
  author  = {Singh, Amogh},
  title   = {FlipEval: Paired Behavioral-Change Statistics for
             Compressed-Model Evaluation},
  year    = {2026},
  doi     = {10.5281/zenodo.21708922},
  url     = {https://github.com/amoghsingh130/flipeval},
  license = {Apache-2.0}
}
```

## Audited source corpus

The literature audit reads 17 sources in full. **Their full-text captures are not
redistributed and are not part of any release.** A redistribution review on
2026-08-02 examined the terms attached to each source and found four of them, the
Meta AI blog post, the NVIDIA TensorRT-LLM documentation page, and two vLLM pages,
carrying no grant that would permit a third party to republish their text; the
seven method papers sit under arXiv's default licence, which authorises arXiv to
distribute them rather than authorising us to. Publishing the corpus was never an
option that was open to us. This section records what was checked and what it
found, and is not a general statement about what any licence permits.

What is published instead is enough to rebuild the corpus and confirm it is the
same one the audit read:

- the source URL per claim, in `docs/audit_claim_table.csv` (frozen);
- the pinned version identifier, byte count, SHA-256 and provenance status per
  source, in `docs/audit_sources_manifest.tsv`;
- `scripts/fetch_audit_sources.py`, which re-fetches each source from its own
  publisher by the retrieval method recorded for it and compares digests;
- quoted text, as short excerpts with their locations, in the paper.

```bash
python3 scripts/fetch_audit_sources.py \
  --manifest docs/audit_sources_manifest.tsv \
  --claims   docs/audit_claim_table.csv \
  --out      /path/to/rebuilt_sources
```

All three path arguments are required and the script has no defaults, for the
same reason `--atlas` and `--output` have none: a defaulted run exits 0 and
certifies the wrong corpus. Add `--offline` to verify a directory you already
have without fetching anything. Retrieval is per-source and not interchangeable:
for the arXiv papers only the ar5iv full-text HTML reproduces the recorded
digest, and the PDF, the extracted text and the `/abs` page each hash
differently.

### What the digests do and do not establish

Fifteen of the seventeen reproduced their recorded digests exactly when
re-fetched on 2026-07-31. Two do not, and the manifest's `status` column records
which is which per row rather than reporting a single pass rate.

- **R11 is `MISMATCH`, and that is a property of the source.** The page is served
  with per-response content: two fetches seconds apart returned different bytes.
  Its recorded digest was never a valid fingerprint of the page, so it can neither
  confirm nor refute a content change. The script reports `EXPECTED-DRIFT` for it
  on a live run and does not fail.
- **R13 is `NO-BASELINE`.** A digest **is** recorded for the archived capture, so
  a re-fetch can be checked against that capture. What is missing is any digest
  recorded *before* the capture was made, so the capture itself was never
  corroborated against an independent earlier record.

Provenance for these two is documentary, not cryptographic, and neither is
described anywhere as hash-verified.

## License

Licensed under [Apache-2.0](LICENSE).
