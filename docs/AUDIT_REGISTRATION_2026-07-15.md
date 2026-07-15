# Published-Claim Audit Registration

Status: **FROZEN 2026-07-15**, by the commit containing this line — before any
per-claim power computation was run. The claim list itself must also be frozen
(§3.4) before verdicts are computed. Deviations require a dated entry under
Dated Amendments stating whether results were inspected before the decision.

Purpose: systematically assess whether published "near-lossless" compression
claims are statistically supported at their reported evaluation sizes. Framing
is constructive — the field lacks reporting standards; flipeval and the
certification tables are the proposed fix — not an indictment of specific
papers. Every verdict is mechanical and recomputable.

## 1. Disclosure of pre-registration data contact

Five candidate claims were collected with exact quotes on 2026-07-15 (GPTQ,
LLM.int8(), SmoothQuant abstracts; the RedHatAI W4A16 Llama-3.1-8B model card;
Meta's quantized Llama 3.2 blog) during a feasibility sweep. No power
computation has been run on any of them. They enter the pool through the same
§3 criteria as later-collected claims.

## 2. Population and sampling frame (fixed)

Claim sources, enumerated exhaustively within each frame:

- **F1 — Method papers:** the published versions of GPTQ, AWQ, SmoothQuant,
  LLM.int8(), SpinQuant, QuIP#, SqueezeLLM, Wanda, and SparseGPT, plus any paper
  citing one of these that appears in the related-work sweep
  (`docs/related_work_checklist.md`) and makes an equivalence-type claim.
- **F2 — Official quantized model cards:** Meta, Qwen, Mistral, and Red Hat
  AI/Neural Magic quantized releases of models in the Llama-2/3.x and Qwen2.5
  families on Hugging Face.
- **F3 — Inference-stack vendor posts:** vLLM, TensorRT-LLM, and llama.cpp
  official blog/docs pages making quantization-quality claims.

Target: **at least 10** claims; all claims meeting §3 inclusion are audited
(no discretionary sub-selection).

## 3. Claim inclusion and extraction (mechanical)

1. **Inclusion:** the source asserts, in prose or a table caption, that a
   compressed model's benchmark quality is equivalent-or-negligibly-different
   from its uncompressed baseline (trigger vocabulary: "near-lossless",
   "negligible", "no (significant) degradation", "matches", "preserves
   accuracy", "X% recovery" with X ≥ 98, or an explicit ≤1 pp delta framed as
   parity). Perplexity-only claims are included only if a benchmark-accuracy
   claim also appears.
2. **Extraction fields (per claim):** exact quote (≤15 words), source and
   version/date, benchmark(s), reported n per benchmark (as stated, else the
   benchmark's standard size, recorded as `imputed`), reported baseline
   accuracy, reported delta, whether per-item outputs are released, whether
   any statistical test or interval is reported.
3. **Double extraction:** each claim's fields are extracted twice on different
   days (solo-author substitute for dual coding) and discrepancies resolved
   before the verdict stage.
4. **Freeze:** the completed claim table is committed as
   `docs/audit_claim_table.csv` before any verdict is computed. Claims found
   after that commit go into a separately reported "post-freeze" stratum.

## 4. Verdict rules (mechanical, computed only after §3.4 freeze)

For each claim × benchmark, at the claim's reported n and baseline accuracy:

- **V1 — Detection power:** minimum detectable accuracy delta at 80% power,
  two-sided α=0.05, under the paired-flip model with the discordance rate
  imputed from the atlas's empirical flip-rate distribution for the nearest
  (method family, bit width, benchmark) cell — sensitivity-checked against the
  independent-binomial bound. Report MDD/claimed-margin ratio.
- **V2 — Equivalence support:** the n required for TOST at margin
  **2 pp** — matching the registered main-grid TOST margin — (and at the
  claim's own margin when it states one). A claim is
  labeled **"underpowered for its own assertion"** iff reported n < required n
  at the applicable margin.
- **V3 — Reproducibility:** binary — could a third party run a paired test
  from released artifacts (per-item outputs public)?

Headline statistic: the fraction of audited claims labeled underpowered under
V2, reported with its count and the full claim table. No claim is described as
"false" or "wrong"; the audited property is the evidential sufficiency of the
reported evaluation, not the truth of the underlying equivalence.

## 5. Robustness reporting

Verdicts are recomputed under (a) the independent-binomial bound instead of the
atlas-imputed discordance rate and (b) a margin sweep over 1 pp and 3 pp; a claim's
verdict is called margin-sensitive if it changes across the sweep, and the
count of margin-sensitive verdicts accompanies the headline number.

## Dated Amendments

None.
