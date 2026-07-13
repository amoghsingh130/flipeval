# WikiText-2 calibration protocol blocker

Status: **human protocol decision required before main-grid execution**  
Detected: 2026-07-13  
Main-grid results inspected: **no**

## Frozen rule that was tested

`PREREGISTRATION.md` requires the WikiText-2 condition to use the same five seeds,
128-sample count, exact 2,048-token length, short-document skipping, and index
retention as C4. The implementation initially interpreted a Hugging Face dataset row
as a document, matching the literal indexed-row API used for C4.

The preflight used:

- `Salesforce/wikitext`, config `wikitext-2-raw-v1`, train split.
- Dataset revision `b08601e04326c79dfdd32d625aee71d232d685c3`.
- `Qwen/Qwen2.5-1.5B-Instruct` revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- The pinned Docker runtime (`torch 2.13.0`, `transformers 5.13.0`,
  `datasets 5.0.0`).
- Seed 0, complete shuffled row-index array, no added special tokens.

Observed result:

```text
CalibrationArtifactError: only 0 of 36718 rows contain at least 2048 tokens;
the frozen protocol requires 128
```

No calibration artifact or model checkpoint was produced.

## Why this is not an implementation bug

WikiText-2 raw represents articles across many short rows rather than exposing each
article as one long row. No row satisfies the registered eligibility threshold, so
changing the random seed cannot make the condition executable.

## Decision options

### A. Reconstruct articles, then apply the frozen rule (recommended)

Define a WikiText document as one article reconstructed deterministically from the
raw heading boundaries. Persist the reconstruction algorithm and article hashes,
shuffle the complete reconstructed-article index array with
`numpy.random.default_rng(seed).shuffle`, skip reconstructed articles shorter than
2,048 tokens, and retain the first 2,048 tokens from 128 eligible articles.

This most closely preserves the preregistered word “document,” while making explicit
that Hugging Face rows are not documents.

### B. Construct fixed contiguous token blocks

Concatenate rows in source order and define non-overlapping 2,048-token blocks before
shuffling block indices. This is easy to reproduce but changes the unit from a
document to a corpus block and is less faithful to the registered language.

### C. Drop or replace the WikiText-2 condition

Remove the calibration-distribution comparison or replace WikiText-2 with a corpus
having naturally long indexed documents. This is the largest design change.

## Required next action

Choose one option and append a dated amendment to `PREREGISTRATION.md` **before** the
first main-grid job. Then implement and test that exact choice. The existing builder
must continue failing closed until the amendment is recorded.
