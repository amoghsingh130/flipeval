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

**2026-07-15 — Amendment 1 (§3.3 independence mechanism).** The requirement
that the two extractions occur "on different days" is replaced by an
extractor-independence requirement: the second extraction is performed in a
fresh agent session with **no access to pass-1 outputs** — the extractor is
withheld `docs/audit_claim_table_pass1.csv`, instructed not to read it or
retrieve it from git history, and receives only the frozen protocol and the
source frames. Rationale: temporal separation was a proxy for extractor
independence calibrated to human memory; a fresh agent session carries no
memory of pass 1, so blind same-day extraction provides at least the intended
independence; the source-stability benefit of a second-day fetch is instead
obtained by recording source content hashes in both passes where feasible.
Decision context: made after pass-1 extraction results were known, but before
any verdict, power, MDD, or required-n computation was run; the §4 verdict
rules and the §3.1–3.2 inclusion/extraction rules are unchanged.

**2026-07-31 — Amendment 2 (§4 V2, the applicable margin).**

*Defect.* §4 V2 computes the required $n$ "at margin 2 pp … (and at the claim's
own margin when it states one)". The phrase "when it states one" was never
operationalised in this registration, and §3.2 does not extract a margin: the
frozen claim table `docs/audit_claim_table.csv` has no margin field. The
implementation in `scripts/audit_verdicts.py` supplied one after the freeze, by
taking the largest delta the source reports and treating it as the margin the
source states. Those are different quantities. A reported delta is an outcome of
the evaluation; a margin is a threshold against which an outcome is judged.
Every `margin_basis` value in `results/audit_verdicts_rev2.csv` cites an
observed quantity — for example "max |delta| over the 5 OPT-175B tasks" (R01),
"the larger of the two stated deltas" (R06), "+0.15pp (68.69 vs 68.54)" (R17).
Verdicts labelled "underpowered for its own assertion" therefore rest, for those
claims, on a margin the source did not assert.

*Amendment.* The applicable margin is determined by the following rule, which
replaces the parenthetical in §4 V2. Each audited claim is assigned to exactly
one category:

1. **Formal equivalence claim** — the source states a numeric tolerance that is
   logically prior to the observed result: a threshold that could have been
   written down before the evaluation was run. Qualifying forms include "within
   $X$", "no more than $X$", "at most $X$" used as a requirement, "a tolerance
   of $X$", and equivalent constructions that bound what the source would accept.
2. **Informal near-lossless claim** — the source reports a result and
   characterises it as negligible, but states no threshold prior to it. This
   includes deltas subsequently described as small, recovery percentages
   computed from the result, and phrases such as "at most $X$" used to describe
   the spread of observed differences rather than to set a bound.
3. **Unquantified claim** — the source uses equivalence language without
   sufficient numerical information to evaluate either way. This category does
   not change; it continues to be handled by the §4 indeterminacy rules.

The determination is made against the frozen `exact_quote` for each claim and,
where the quote alone is inconclusive, against the source at the version and
content hash recorded in the frozen claim table. It is recorded per claim, with
the quoted text supporting it, in a new column of the verdicts CSV. **No claim is
re-extracted and no source is re-fetched for extraction purposes**; the frozen
claim table is unchanged. Sources were re-fetched for verification only, under
the eligibility-and-provenance scope recorded below.

Verdicts are then computed as follows:

- The **primary verdict for every claim** is at the registered 2 pp margin,
  which §4 already names first. The headline count is the number of determinate
  claims underpowered at 2 pp.
- A claim in category 1 is **additionally** evaluated at its declared margin,
  reported alongside the primary verdict, and never in place of it.
- Claims in category 2 are reported against the registered 1 pp / 2 pp / 3 pp
  sweep of §5. **No margin derived from a claim's own reported results is
  described as that claim's stated, declared, asserted or own margin**, in the
  paper or in any released artifact.

*Consequential quantities.* Every reported quantity that divides by the
applicable margin is recomputed with it and re-reported: the V1
MDD-to-claimed-margin ratios, the required-$n$-to-reported-$n$ shortfall ratios,
and the §5 margin-sensitivity flag. Values previously reported against a
result-derived margin are withdrawn, not silently updated; both the superseded
and the corrected values remain in the released artifacts.

*Analysis discipline.* The recomputation is run **once**, over the frozen claim
table, and whatever it returns is reported — including if the headline count
falls, rises, or reaches zero. No variant of this rule is constructed after the
recomputed values are seen.

*Eligibility correction (R10).* A full-text review of every source, run
2026-07-31 and recorded in `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md`,
established that R10's recorded `exact_quote` — "average recovery percentage
across all benchmarks is 98.6%" — appears nowhere in its source. The card
contains no prose equivalence claim; `98.6%` is a table cell, and the extraction
composed a sentence from tabular data and recorded it as a quotation. §3.1
requires the assertion to appear "in prose or a table caption", and it appears in
neither. **R10 is therefore excluded from the eligible population by applying the
inclusion rule already registered in §3.1, not by any new criterion.** The
eligible population becomes 16. The frozen claim table is not edited; the
exclusion is recorded in the verdicts CSV with the verification finding beside
it, and the original row remains in the immutable frozen file and in the
published v1.0.0 artifact.

This correction moves the eligible denominator. It changes neither the number of
claims below the planning threshold nor the V3 per-item-outputs result: R10 was
adequately powered at the registered 2 pp margin and recorded `no` on V3, so its
removal cannot reduce the count of flagged claims. **The correction did not
improve any count in the direction favourable to the audit's thesis.**

*Scope.* This amendment changes the applicable margin, and reopens §§3.1–3.2
**only** to correct eligibility and provenance — that is, to apply the existing
inclusion rule to R10 and to record source provenance. No inclusion criterion is
added, widened or narrowed, no claim is re-extracted, and no source is re-fetched
for extraction purposes. Unchanged and not reopened: the frozen claim table
itself; the §4 V1 detection-power formula; the §4 V3 reproducibility verdict; the
indeterminacy rules and the claims currently indeterminate; the discordance
imputation and its tier matching; the atlas; and every registration other than
this one.

*Reporting the surviving power result.* The claim below the planning threshold at
the registered 2 pp margin is reported as a **sensitivity-dependent planning
flag, not a stable binary verdict**, and never without its reversal point. The
required $n$ is a planning quantity computed under an assumed true difference of
zero and a point imputation of discordance; for the single flagged claim the
classification reverses at approximately $d = 0.1189$ against an imputed
$d = 0.13$, and 43.6% of the 792 atlas cells supplying that imputation fall below
the reversal point. Any report of this flag states the imputed value, the
reversal point, and that fraction.

*Decision context.* **Results were inspected before this decision, and so was the
full-text classification.** The audit verdicts were computed on 2026-07-20,
revised to rev-2 on 2026-07-21, reported in the paper, and released in the v1.0.0
artifact; the headline $K = 4$ of 12 has been public since 2026-07-30. The
full-text verification of all 17 sources was run on 2026-07-31, **before this
amendment was signed and at the decision owner's direction**, and its
classification of every claim — including the finding that no source declares a
margin — was known at signature. The rule in this amendment was not constructed
against that classification: it was written and committed on 2026-07-31 at
`19d485c`, before the verification ran, and that committed draft names R14 as its
hard case and resolves it by the same priority test the verification later
applied. The rule is unchanged from that commit. The eligibility correction was
made by applying §3.1 as already registered, and is verdict-neutral in the sense
recorded above. The original immutable version of every superseded value remains
accessible in the frozen claim table and the published v1.0.0 artifact.

*Signed.* Amogh Singh, 2026-07-31. Drafted by Claude Code at `19d485c`, revised at `bb45528` after the full-text source verification, and appended on the verbatim instruction "sign and append". The rule in the *Amendment* clause above is unchanged from `19d485c`.
