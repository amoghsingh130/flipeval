# FlipEval

FlipEval measures paired, per-item behavioral change between a baseline model and a compressed or otherwise modified model. It reports net accuracy change alongside harmful and beneficial flips, answer churn, paired significance and equivalence tests, confidence intervals, power estimates, and method-rank stability.

## Install

```bash
python -m pip install -e .
pytest
```

## Usage

```python
import json
from flipeval import compare

def load(path):
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]

baseline = load("fp16.mmlu.jsonl")
method = load("gptq.mmlu.jsonl")
result = compare(baseline, method, margin=0.02, bootstrap=1000, seed=0)
print(result.net_accuracy_delta, result.accuracy_state_churn)
```

The pairwise CLI writes a one-row CSV and prints the full result:

```bash
flipeval compare fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --output comparison.csv
flipeval compare baseline_samples.json method_samples.json --format lm-eval
```

The registered calibration-seed analysis accepts explicit `SEED=PATH` pairs:

```bash
flipeval paired-seeds \
  --first 0=gptq_s0.jsonl --first 1=gptq_s1.jsonl --first 2=gptq_s2.jsonl \
  --first 3=gptq_s3.jsonl --first 4=gptq_s4.jsonl \
  --second 0=awq_s0.jsonl --second 1=awq_s1.jsonl --second 2=awq_s2.jsonl \
  --second 3=awq_s3.jsonl --second 4=awq_s4.jsonl \
  --expected-seeds 5 --bootstrap 2000 --output hierarchical_summary.json
```

This analysis fails closed unless both methods and all seeds contain exactly the
same item IDs. It reports per-seed item-bootstrap intervals, seed-level accuracy SD,
item-level SE, a paired seed-by-item interval, joint rank-flip rate, and exact-tie
rate. A repeated seed draw receives an independent item resample, while both methods
retain the same seed occurrence and item indices.

Each native record must contain `item_id`, `prediction`, and `correct`. Paired records are aligned by `item_id`; duplicate IDs are rejected. The lm-evaluation-harness adapter targets the v0.4.x `--log_samples` schema represented by v0.4.12 and accepts either a full result JSON with a `samples` mapping or a sample JSON/JSONL file.

## Reproducibility

Bootstrap results are deterministic for a given seed. Ties are reported separately
and never counted as flips. `python -m pilot_eval.analyze` remains available as a
compatibility CLI and uses FlipEval internally. The golden test regenerates the
archived pilot summaries from `results/pilot_outputs_20260711T000427Z.tar.gz`.

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

Licensed under Apache-2.0.
