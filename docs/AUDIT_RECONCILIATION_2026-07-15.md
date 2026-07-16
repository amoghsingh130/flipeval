# Audit Claim Table Reconciliation (Pass 1 × Pass 2)

Date: 2026-07-15. Inputs: `docs/audit_claim_table_pass1.csv` (13 claims,
general-purpose agent, some fields summarizer-derived) and
`docs/audit_claim_table_pass2.csv` (17 claims + 6 logged exclusions, blind
fresh-session extraction per Amendment 1, source sha256 recorded).
Output: `docs/audit_claim_table.csv` (17 claims, R01–R17), **frozen by the
commit containing this file**, before any verdict/power computation (§3.4).

## Inclusion adjudications

- **Agreed by both passes (12 sources):** GPTQ, LLM.int8(), SmoothQuant, AWQ,
  SqueezeLLM, Wanda, SparseGPT, Red Hat Llama-3.1-8B W4A16, Red Hat
  Llama-3.1-8B FP8, Red Hat Qwen2.5-7B W4A16, Meta quantized-Llama blog,
  TensorRT-LLM quantization blog (pass 1 read the rendered page, pass 2 the
  GitHub source of the same document; treated as one source).
- **QuIP# — EXCLUDED (disagreement resolved against inclusion).** Pass 2
  included it on "perform similarly … very close to FP16 performance."
  Neither phrase is in the §3.1 trigger vocabulary; the sentence describes
  4-bit PTQ methods generally rather than asserting parity for QuIP#
  specifically; and pass 1's independent read found no qualifying language.
  Strict rule text controls. Recorded so the paper can cite QuIP# (with
  SpinQuant and the Qwen/llama.cpp docs) as honest non-claiming sources.
- **Enumeration gaps included after single-pass raw verification (5):**
  R13 (vLLM LLM-Compressor FP8 docs page; pass-1 only), R14 (vLLM Apr-2026
  FP8 KV-cache blog; pass-2 only), R15–R17 (Red Hat W8A8-8B, W4A16-70B,
  W8A16-Llama-3 cards; pass-2 only). Each carries a
  `single-pass extraction` flag in `verdict_stage_flags`.

## Field-merge policy

Primary quote = the sentence with literal §3.1 trigger vocabulary (AWQ,
SparseGPT switched to pass-2 anchors on this basis; SmoothQuant and
SqueezeLLM kept the abstract-level claim with the alternative preserved in
notes). Numeric fields: raw-verified extraction preferred, union of detail
kept, disagreements resolved by re-reading the cited table (none survived —
every numeric disagreement was scope, not value). Per-source purity enforced
on R11 (Meta blog): pass 1 had imported numbers from the companion HF model
card, which itself contains no qualifying prose; blog-only fields are now
chart-image-only, with the card's numbers retained in notes as context.

## Verdict-stage flags (pre-registered observations, not verdicts)

- R05 SqueezeLLM and R08 Red Hat W4A16: source-internal contradictions
  (abstract "lossless to 3-bit" vs own −3.1 pp table; prose 93.0% vs table
  105.4% Arena-Hard recovery).
- R02, R11, R14: headline comparison exists only as chart images.
- R13: equivalence claim with an n=250 evaluation and no on-page baseline.
- R04: claim's metric is CIDEr (generation quality), not accuracy.

## Fidelity notes

Pass-1 rows C01, C02, C05, C10 were partly summarizer-derived; where their
values entered merged rows they matched pass-2's raw-verified reads except as
noted in row-level `reconciliation_notes`. Pass 2 recorded sha256 of fetched
sources; future re-fetches should compare against these before re-quoting.
