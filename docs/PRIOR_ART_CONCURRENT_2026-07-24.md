# Prior-Art Note — Concurrent Work Tracking (2026-07-24)

Purpose: track arXiv-concurrent papers close enough to FlipEval's five legs
(atlas/churn, statistical certification, H3 seeds, harness study, audit) that
they change how we position, cite, or (in the worst case) how we frame the
contribution. Read-only exercise; no registered file touched.

This note **extends and renames** the earlier
`docs/PRIOR_ART_CALIBRATION_DATA_2026-07-24.md`; that note's calibration-paper
content is preserved verbatim as **Section 1** below, and this file is now the
single point of reference for concurrent-work tracking.

**Provenance.** Sections 2–4 were verified against the raw arXiv HTML rendering
fetched directly (not summarizer-relayed) — every methodological quote was
copy-extracted with a location, and the hard-stop trigger terms
(`TOST`, `equivalen*`, `power analys*`, `required…sample`, `mcnemar`, `seed`,
`calibrat`) were grepped exhaustively over the extracted text. Section 1 carries
its own `[search-derived]` / `[to-verify]` caveats as originally written (the
OpenReview source was Cloudflare-walled).

---

## Hard-stop check — result

For the two priority papers (2607.08734, 2604.27405), the four abstract-changing
triggers were searched for directly and **none is present**: no equivalence
testing at a margin, no required-*n* / power computation, no method-ranking
comparison across calibration randomness, no published-claims audit. Evidence is
in each paper's section below. **No change to the abstract is implied.** The
closest paper (2607.08734) reaches a consistent *premise-level* conclusion by a
different route but supplies none of our differentiators.

---

## Section 1 — "Understanding and Selecting Calibration Data for LLM Quantization" (OpenReview `pfw3saHzGU`)

Target: **"Understanding and Selecting Calibration Data for LLM Quantization:
From Sensitivity Analysis to Activation-Based Curation"**, OpenReview forum
`pfw3saHzGU` (<https://openreview.net/forum?id=pfw3saHzGU>).

Purpose: differentiate it from FlipEval, on the specific question of whether it
anticipates **H3** (seed-level *ranking instability* between GPTQ and AWQ under a
preregistered rule with paired statistics). Read-only on the repo.

### 📋 Verbatim-quote verification checklist (for Amogh — one browser pass)

The cluster cannot reach OpenReview (`pfw3saHzGU`) — Cloudflare-walled — so every
quote in this section is `[search-derived]` / `[to-verify]`. Open the forum page
and confirm each item below verbatim; the "supports" column says what the quote is
load-bearing for, so a wording change there changes the positioning, not just a
citation. **Rule: no `[to-verify]` quote may survive into a submitted related-work
section — each must be confirmed verbatim or removed before the preprint.**

| # | claim to confirm (loc) | what it supports |
|---|---|---|
| V1 | Authors, affiliations, venue, decision status, and record date (~2026-06-21/22) — §1.1 | citation completeness + the scoop-priority timeline (their measurement predates our registration) |
| V2 | Seed protocol: *"…seeds that control both sample selection and token order … stability is assessed across three calibration data sampling seeds"* — §1.2 | that they vary the same knob (calibration composition) we do, at 3 seeds vs our 5 — the premise-overlap claim |
| V3 | Aggregate-variance readings: *"…low variance … ±0.3 on LLaMA and ±0.5 on Qwen…"*, perplexity *"<1%"* — §1.3 | that they read seed variance as stable/noise, not as a ranking test |
| V4 | ACDM gains: *"+0.95 and +0.49 percentage points over random sampling on Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct"* — §1.3 | that their head-to-head is data-curation methods, not quantization-method ranking |
| V5 | GPTQ/AWQ sensitivity: *"domain-matched calibration data helps mainly for GPTQ … little consistent benefit for AWQ…"* — §1.3 | the honesty-flag load-bearing point: a sensitivity-profile contrast, not a seed-indexed GPTQ-vs-AWQ ranking |
| V6 | GSM8K noise sentence: *"GSM8K shows the largest per-task variance (±0.8 on LLaMA, ±1.7 on Qwen), consistent with the inherent evaluation noise of exact-match scoring…"* — §1.4 | the convergent harness-sensitivity framing — this is the exact quote we would put in the paper |
| V7 | Absence: that no results table anywhere ranks GPTQ vs AWQ head-to-head across seeds — §1.5 / honesty flag | the H3-independence claim (they do not run H3's test) |

### ⚠️ Source-access caveat — READ FIRST

**I could not open the paper's full text or its OpenReview metadata with the
tools available.** `openreview.net` and both API hosts (`api.openreview.net`,
`api2.openreview.net`) sit behind a Cloudflare browser-verification challenge
that `WebFetch` cannot clear; the PDF endpoint is walled the same way; Semantic
Scholar returned 504/429. Every quotation below is therefore **surfaced from web
search-engine summaries of the paper, corroborated across multiple independent
queries — NOT verified verbatim against the source PDF.** They read as
near-verbatim (especially the GSM8K sentence, which recurred identically across
queries), but for a project with this provenance discipline they must be treated
as **to-verify** until someone opens the OpenReview page directly. Each item is
marked `[search-derived]` or `[to-verify]` accordingly.

**Human action needed** to close this note: open the forum page and confirm
(a) authors + affiliations, (b) venue and decision status, (c) the exact GSM8K
"evaluation noise" sentence, and (d) that no results table anywhere ranks GPTQ
vs AWQ head-to-head across seeds (see the honesty flag at the end of this section).

### 1.1 Identity, authorship, venue, timeline

| field | value | status |
|---|---|---|
| Title | *Understanding and Selecting Calibration Data for LLM Quantization: From Sensitivity Analysis to Activation-Based Curation* | confirmed (forum + search) |
| Authors | **not retrievable** — not surfaced by search; likely anonymized under review or simply not indexed | **UNKNOWN — to-verify** |
| Affiliations | **not retrievable** | **UNKNOWN — to-verify** |
| Venue | reported as an **oral presentation at "ACL-SELVA 2026"** by one search result only | `[to-verify]` — single-source, possibly a hallucinated venue string; confirm on OpenReview |
| Decision / acceptance | not confirmed (the "oral" claim above is the only signal, unverified) | **UNKNOWN — to-verify** |
| Date | OpenReview record dated **2026-06-21/22** (search results split between the two adjacent days) | `[search-derived]` |

**Scoop-priority timeline.** Their record: **~2026-06-21/22**. Our registrations:
`PREREGISTRATION.md` frozen **2026-07-11**; the mini-grid, atlas-mining, and audit
registrations frozen **2026-07-15**. So their calibration-sensitivity paper is
**~3 weeks older** than our earliest frozen registration. This matters for how we
*position*, not for what we claim: their public measurement predates our
registration, which makes it **independent corroboration of our premise** (that
seed/calibration choices move the numbers a compression comparison rests on)
available *before* we committed to testing that premise's consequence. It is not
priority over H3, because — on the evidence below — they do not run H3's test
(see §1.5). Position it as antecedent evidence, not as anticipation.

### 1.2 Their seed protocol `[search-derived]`

- **Three PTQ algorithms**: GPTQ, AWQ, and SmoothQuant+GPTQ.
- **Six models** from the **Qwen2.5 and Llama-3.1** families (named instances
  include **Qwen2.5-7B-Instruct** and **Llama-3.1-8B-Instruct** — the *same two
  models as our escalation 7B/8B cells*).
- **Seeds: three calibration-data sampling seeds.** Search rendering: *"resampling
  with multiple random seeds that control both sample selection and token order …
  calibration seed stability is assessed across three calibration data sampling
  seeds."* So the seed governs **which calibration samples are drawn and in what
  token order** — structurally the same knob our design varies, but at **3 seeds**
  where our registered grid uses **5** (`{0,1,2,3,4}`).
- The sensitivity analysis also **jointly sweeps sample count and sequence
  length** (a different axis from ours; we hold data fixed and vary the seed).

Contrast with ours: we draw 128 samples of exactly 2,048 tokens from C4 by a
fixed seed-determined procedure and give **GPTQ seed s and AWQ seed s the
byte-identical ordered samples** (`PREREGISTRATION.md` §"Experimental Grid").
Their seed varies calibration composition to study each method's *robustness*;
ours pairs it across methods to study *cross-method ranking*.

### 1.3 What they measured `[search-derived]`

- **Within-method accuracy variance under calibration resampling**, reported as
  aggregate ± ranges, not paired per-item differences.
- Search rendering: *"aggregate accuracy exhibits low variance … ±0.3 on LLaMA
  and ±0.5 on Qwen, confirming that gains are stable under calibration
  resampling"* and *"resulting perplexity fluctuates by less than 1% relative to
  the mean, with seed-wise traces largely overlapping."*
- **Method-selection comparison is ACDM vs calibration-*selection* baselines**
  (random sampling, self-calibration, ZipCal) across five benchmarks — gains of
  *"+0.95 and +0.49 percentage points over random sampling on Qwen2.5-7B-Instruct
  and Llama-3.1-8B-Instruct."* This is a comparison of **data-curation methods**,
  not of **quantization methods** against each other.
- Their GPTQ-vs-AWQ statements are about **differing sensitivity to calibration
  data**: *"domain-matched calibration data helps mainly for GPTQ on Qwen2.5
  specialized variants, but provides little consistent benefit for AWQ,
  suggesting that AWQ's sensitivity is governed more by activation-distribution
  mismatch than by surface domain mismatch."* This contrasts the two methods'
  *robustness profiles*; it is **not** a head-to-head accuracy ranking, and not a
  test of whether that ranking flips across seeds.

### 1.4 The GSM8K variance interpretation `[to-verify — quote exactly on OpenReview]`

The sentence the task asked to pin down, as it recurred (identically) across
searches:

> "GSM8K shows the largest per-task variance (±0.8 on LLaMA, ±1.7 on Qwen),
> consistent with the **inherent evaluation noise of exact-match scoring on
> mathematical reasoning**."

Read against our own results this is striking: they attribute the GSM8K
seed-to-seed swing to *evaluation noise of exact-match scoring* — the **same
mechanism** our own campaign isolated when `strict-match` voided 617/1,000 GSM8K
responses and moved FP16 accuracy 0.232→0.566 with no change to the generations
(`docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md` §4.2), and which our harness
sensitivity study measures directly (condition B, R=1.585). They name the cause
and treat it as **noise to be smoothed over**; we treat it as **signal whose
consequence for method rankings must be tested**. This is the cleanest available
statement of the difference in stance, and it strengthens our framing — but the
exact wording must be confirmed against the PDF before we quote it in the paper.

### 1.5 Paired analysis / statistical testing / flip accounting `[search-derived, absence]`

**No evidence of any of it.** Across every search the paper's reported
instruments are **aggregate accuracy ± ranges and perplexity fluctuation** —
descriptive dispersion, not inference. I found **no** mention of: paired per-item
analysis (McNemar, paired bootstrap, per-item difference vectors); statistical
significance testing of a method difference; winner-flip / rank-change accounting
across seeds; a preregistered decision rule over the variance.

This is the load-bearing distinction. Their ± ranges answer *"how stable is a
method's accuracy under resampling?"*; H3 answers *"does the seed reorder which
method wins, and is that instability real under a paired test?"* — the winner-flip
count, the range/gap screen, and the two-level paired bootstrap
(`PREREGISTRATION.md` §"H3 Decision Rule") have no counterpart in what they
report. **Caveat:** absence in search summaries is not proof of absence in the
paper; the human should scan the results tables directly (see the honesty flag).

### 1.6 Overlap with the FlipEval legs

- **H3 / mini-grid (the one that matters):** *premise overlap, not result
  overlap.* Model overlap (Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct = our
  escalation 7B/8B models) is worth noting so a reviewer sees them as adjacent;
  pre-empt by citing them as the antecedent measurement.
- **Harness-sensitivity leg:** *convergent, independent.* Their GSM8K exact-match
  "evaluation noise" attribution is the phenomenon our configuration-sensitivity
  study quantifies (condition B).
- **Audit leg / Atlas leg / Certification legs:** *no overlap.* No audited
  published claims, no public-record atlas, no equivalence margin / TOST /
  required-*n* / anytime-valid stopping.

### 1.7 ⚠️ Honesty flag (calibration paper)

On all retrievable evidence their GPTQ/AWQ comparison is a *sensitivity-profile*
contrast and their head-to-head *method* comparison is ACDM vs
calibration-selection baselines — neither a seed-indexed GPTQ-vs-AWQ accuracy
ranking, and no flip/paired-test machinery found. **What I cannot rule out:**
because the full PDF was inaccessible, I cannot exclude a results table printing
GPTQ and AWQ accuracies side by side per seed. If such a table exists it would
still not be H3 (no rule, no paired test, no flip accounting), but the human
should eyeball the results section before finalizing the related-work positioning.

---

## Section 2 — arXiv:2607.08734, "The Illusion of Equivalency: Statistical Characterization of Quantization Effects in LLMs" (Rababah, Akcora, Leung)

**Status:** v1 only, posted 2026-07-09, cs.AI, CC BY 4.0. HTML fetched and parsed
directly: <https://arxiv.org/html/2607.08734v1>. Authors/affiliations (from the
byline): Baha Rababah (Univ. of Manitoba; Red River College Polytechnic),
Cuneyt Gurcan Akcora (Univ. of Central Florida), Carson K. Leung (Univ. of
Manitoba). No venue beyond the arXiv listing found; treat as an unreviewed
preprint. (Note: the appendix carries a different working title — *"LLMs vs.
Their Quantized Variants: Benchmarking the Illusion of Equivalence"* — suggesting
a retitling between drafts; no substantive content difference found.)

### 2.1 "Correctness agreement" — exact definition and mapping to our churn metric

**Definition 1 (Correctness Agreement), verbatim** (§"Decision behavior and
correctness agreement"):

> "Let z_m and z_m^(c) be binary correctness labels (1 if correct, 0 otherwise)
> assigned to the predictions of the base and quantized models, respectively, on
> input x^(m). The joint correctness between the two models is defined as
> CA(c;θ,D) := (1/M) Σ_{m=1}^{M} 𝟙[z_m=1 ∧ z_m^(c)=1]"

and (§4.3): *"Table 4 reports correctness agreement, the fraction of examples
where both the base and quantized models are correct."*

**Mapping.** Same **per-item join semantics** as our atlas/churn leg (paired
correctness on the identical input across FP16 and quantized), but it captures
only **one cell** of the 2×2 table churn is built from. With `a`=both correct,
`b`=base-correct-quant-wrong, `c`=base-wrong-quant-correct, `d`=both wrong:

- Their CA = `a/n` — the joint-correct cell only.
- It is **not** `1 − churn` (that would be `(a+d)/n`); our churn is `(b+c)/n`.
- But CA is **algebraically recoverable into our churn** given the two
  accuracies: since `Acc_base = a+b` and `Acc_quant = a+c` (fractions of n),
  `churn = (b+c)/n = Acc_base + Acc_quant − 2·CA`. Their Table 4 CA plus the two
  reported accuracies suffices to recompute our churn for every cell they report,
  without their raw per-item labels — a clean citable bridge.

### 2.2 Models, methods, bit-widths, benchmarks, sample sizes

Verbatim (§4): *"We quantize the following four models: Llama-3.2-3B,
Vicuna-7B-v1.5, Mistral-7B-v0.1, and Llama-3.1-8B into legacy quantization
methods (Q8_0, Q5_0, Q4_0) and K-quantization methods (Q6_K, Q5_K, Q4_K, Q3_K,
Q2_K) using llama.cpp."* Benchmarks: *"For perplexity evaluation, we use
WikiText-2 and C4… zero-shot benchmarks including HellaSwag, Winogrande, and ARC
(AI2 Reasoning Challenge)."* Hardware: eight V100-SXM2 32GB.

**Sample sizes per benchmark are not stated anywhere** — no `n=` values are given
in prose, table, or appendix (itself relevant to our audit leg's "reported n"
field: an equivalence-flavored paper that does not state its own eval n).
Quantization family is **llama.cpp GGUF legacy + K-quant only — no GPTQ, AWQ,
SmoothQuant, RTN, or Wanda** — disjoint from FlipEval's registered method grid.

### 2.3 Statistical testing / equivalence / power / per-item release

**Absent, verified by direct search:** zero hits for `TOST`,
`equivalen[ce/cy] testing`, `power analys*`, `required…sample`, `mcnemar`,
`p-value`, `p<`, `confidence interval`. Table 2's "±" values are standard
deviations of a layer-wise structural-statistics distribution, not inferential
intervals over an accuracy estimate. The title's "Statistical Characterization"
refers to their attention-weight moment/divergence analysis (skewness, kurtosis,
KL-type divergences across layers), not to hypothesis testing on accuracy or CA.
Per-item release: not mentioned; the only availability statement is *"Our Python
implementation is included in the submission"* — code, not per-item predictions.

### 2.4 Calibration/seeds, ranking stability, harness sensitivity, claim auditing

- **Calibration/seeds:** absent. `calibrat` appears once, stating the opposite of
  a seed sweep — *"These schemes are simple, deterministic, hardware-agnostic, and
  do not require calibration or retraining."* (§2). `seed` appears **zero times**.
- **Method-ranking stability across seeds:** absent — a single method family
  across bit-widths, one run per config, no resampling axis.
- **Harness/config sensitivity:** absent.
- **Auditing published near-lossless claims:** absent as a formal audit; they
  paraphrase Kurtic et al. (2025) — *"FP8 is effectively lossless, INT8 results in
  minimal accuracy reduction…"* — as motivating background, not as a claim under
  test with recomputed required-*n*.

### 2.5 Timeline vs our freezes / venue

Posted **2026-07-09 — 2 days before** `PREREGISTRATION.md` froze (2026-07-11) and
**6 days before** the mini-grid/atlas/audit registrations (2026-07-15). Their
public posting predates all four of our freezes — the closest-in-time concurrent
paper found. It does **not** anticipate our confirmatory result (no seed sweep, no
paired test, no equivalence machinery), so priority on H3, certification, or the
audit is unaffected; it is the most direct **premise-level** concurrent validation
of the atlas/churn idea and worth citing prominently and generously. v1 only; no
venue signal beyond arXiv (cs.AI).

---

## Section 3 — arXiv:2604.27405, "Beyond the Mean: Within-Model Reliable Change Detection for LLM Evaluation" (Jon-Paul Cacioli)

**Status:** v1, posted 2026-04-30, cs.CL/cs.AI. Independent researcher, Melbourne.
HTML fetched directly: <https://arxiv.org/html/2604.27405v1>. Preregistration
<https://osf.io/3dnsa>; code <https://github.com/synthiumjp/beyond_the_mean>. No
venue beyond arXiv found.

### 3.1 Method, null, within- vs between-model

Verbatim: *"We adapted the Reliable Change Index (RCI; Jacobson and Truax, 1991)
from clinical psychology to item-level LLM version comparison on 2,000 MMLU-Pro
items (K=10 samples at T=0.7)."*; *"SEM = SD(p) × √(1 − r_xx), computed per model.
S_diff = √(SEM_v1² + SEM_v2²), computed per pair."*; *"RCI(i) = (p(i,v2) −
p(i,v1)) / S_diff. Reliable improvement: RCI > 1.96. No reliable change: |RCI| ≤
1.96. Reliable deterioration: RCI < −1.96."* This is a **between-model-version,
within-item** test (per-item probability-of-correctness shift standardized by
test-retest error, thresholded at |z|=1.96) — not a paired-flip/McNemar/TOST
design. Both tested pairs are **model-version** comparisons
(Llama-3-8B-Instruct → Llama-3.1-8B-Instruct; Qwen-2.5-7B-Instruct → Qwen3-8B),
**never quantized-vs-FP16**.

### 3.2 Noise-driven flips vs genuine shifts

*"An item that flips from correct to incorrect on a single greedy trial may be
within the model's noise band. An item that does not flip may nonetheless have
shifted substantially in its underlying response probability."* Operationalized
purely via the |RCI|>1.96 threshold on repeated-sampling (K=10, T=0.7) estimates,
not a paired binomial/McNemar test on greedy pass/fail.

### 3.3 Overlap with McNemar/TOST/required-n — absent

Verified: zero hits for `TOST`, `equivalen*`, `power analys*`, `required…sample`,
`mcnemar`. No equivalence margin defined; |RCI|>1.96 is a reliability-of-change
criterion (detects any reliable change in either direction), **not** an
equivalence criterion at a tolerance band.

### 3.4 Quantization? — none

Confirmed by direct search (zero `quantiz*` hits; nearest is "empirical null
calibration," their own statistical-null procedure). Both pairs are
full-precision version transitions. **Outside our atlas/H3 scope on the object of
study.**

### 3.5 Their "churn rate" — a false-friend term

*"Churn = proportion reliably changed in either direction."*; *"Full-benchmark
churn rates were 21% (minor update) and 28% (generational update)."* Same English
word as our accuracy-state churn, but denominator is "reliably-changed-by-RCI,"
not "flips a correct/incorrect label between two paired evaluations of the same
architecture at two precisions." Cite carefully. Harness-adjacent finding worth
noting: *"Greedy single-shot evaluation missed 42% of reliably changed items and
falsely flagged 25% of unchanged items."* — thematically convergent with our
harness leg (protocol choices change which items look changed), but a different
knob (K-sample/temperature vs. our chat-template date / few-shot rendering /
metric choice). Cite as adjacent corroboration, not axis overlap.

---

## Section 4 — arXiv:2606.19558, "Displacement Is Not Direction: Evaluating Fidelity Metrics for Quantized LLM Deployment" (Nikolić et al.) — brief pass

**Status:** v1, posted 2026-06-17, cs.LG/cs.CL. HTML fetched directly:
<https://arxiv.org/html/2606.19558v1>.

**Silent-zone finding.** *"this relationship collapses to non-significance in the
near-baseline silent zone (ρ=+0.00 on Qwen and ρ=−0.24, p=0.36, on Devstral).
This collapse persists across 14 measurement variants…"*; *"We refer to this
near-baseline region as the silent zone: KLD/PPL still measure distance from the
reference model, but no longer provide useful ranking signal for downstream
quality."* Cohort: **28 GGUF quantizations of Qwen3.6-35B-A3B** (MoE) and **41
quantizations of Devstral-Small-2-24B-Instruct-2512** (dense), vs a BF16
reference across MMLU, coding, tool calling, instruction following, MATH-500.

**Per-item correctness comparison — yes** (most atlas-adjacent of the three). They
extend Dutta et al. (2024)'s **flips** metric: *"We split flips into leapfrogs
(quantized model correct, reference wrong) and drops (reference correct, quantized
model wrong)…"* — per-item paired correctness on **real, community-published GGUF
checkpoints**, with an observational calibration-heterogeneity note (*"the
community published hundreds of GGUF quants… with different calibration recipes…"*
— observed population, not a controlled seed experiment). Inference is bootstrap
CIs on correlation/ranking (*"B=10,000 bootstrap replicates… percentile 95%
confidence intervals"*), **no** TOST/McNemar/required-n/equivalence margin (the
one `equivalen` hit is the prose word "Equivalently").

---

## Combined per-leg overlap verdict table

| Leg | Calibration-data (`pfw3saHzGU`) | 2607.08734 (Illusion of Equivalency) | 2604.27405 (Beyond the Mean) | 2606.19558 (Displacement) |
|---|---|---|---|---|
| **1. atlas/churn** | UNCLAIMED — no public per-item mining | **PARTIALLY CLAIMED** — CA = same per-item join, algebraically convertible to our churn; but their own GPU runs, only the `a/n` cell, not the full table | UNCLAIMED for quantization (no quantized models); adjacent as a per-item-churn method for model *versions* | **PARTIALLY CLAIMED** — leapfrog/drop on real published GGUF checkpoints is closest to atlas's wild-artifact flavor, but still their own evals, not mined public dumps; different target question |
| **2. statistical certification** | UNCLAIMED — descriptive ± only | UNCLAIMED — zero hits for TOST/equivalence/power/McNemar/required-n | UNCLAIMED — RCI is reliability-of-change (|z|>1.96), not equivalence at a margin | UNCLAIMED — bootstrap CIs on correlations only |
| **3. H3 seeds** | Antecedent premise evidence only (accuracy variance across 3 calib seeds, read as noise); no paired test, no rule | UNCLAIMED — legacy GGUF explicitly calibration-free; "seed" appears 0 times | UNCLAIMED — no quantization | UNCLAIMED — "different calibration recipes" = observed-population remark, not a controlled sweep |
| **4. harness study** | Convergent, independent (GSM8K exact-match noise) | UNCLAIMED — no config sweep | **Adjacent/partial** — greedy-vs-K-sample decoding sensitivity, different axis | **Adjacent/partial** — 14 measurement-variant robustness of a *fidelity metric*, different object |
| **5. audit** | UNCLAIMED | UNCLAIMED — paraphrases Kurtic et al. (2025), no quote-and-recompute | UNCLAIMED | UNCLAIMED |

---

## Drafted related-work paragraph (for `paper-writer` to integrate after Amogh's read)

> Concurrent work independently corroborates the premise on which FlipEval
> rests --- that aggregate accuracy conceals per-item behavioral change under
> quantization. Most directly, \citet{TODO-illusion2026}, posted two days before
> our preregistration froze and unknown to us until this prior-art sweep, define
> \emph{correctness agreement} $\mathrm{CA} = \frac{1}{n}\sum_i \mathbb{1}[z_i^{\mathrm{base}}{=}1 \wedge z_i^{\mathrm{quant}}{=}1]$,
> the per-item both-correct rate on the identical paired-input join our
> accuracy-state churn is built from. The two metrics are algebraically
> equivalent given the marginal accuracies: since
> $\mathrm{Acc_{base}} = a{+}b$ and $\mathrm{Acc_{quant}} = a{+}c$, their
> $\mathrm{CA} = a$ and our churn $=(b{+}c) = \mathrm{Acc_{base}} +
> \mathrm{Acc_{quant}} - 2\,\mathrm{CA}$. They study a quantization family
> disjoint from ours --- \texttt{llama.cpp} GGUF ($Q_0$ legacy and $Q_K$
> $k$-quant) rather than GPTQ and AWQ --- and reach a conclusion consistent with
> ours: two independently developed studies, on non-overlapping quantization
> methods, measuring the same per-item phenomenon through algebraically equivalent
> statistics, both find that preserved aggregate accuracy hides substantial
> per-item disagreement. We read this as external corroboration of our premise,
> not competition on it. \citet{TODO-calibdata2026} reach the premise from a
> third direction, resampling the calibration set across three seeds for GPTQ,
> AWQ, and SmoothQuant+GPTQ on six Qwen2.5 and Llama-3.1 models and reading
> GSM8K's largest per-task spread as ``inherent evaluation noise of exact-match
> scoring''; \citet{TODO-beyondmean2026} adapt the clinical Reliable Change Index
> to per-item model-\emph{version} comparisons and likewise recommend reporting a
> churn rate alongside the mean; and \citet{TODO-displacement2026} extend the
> flips metric of \citet{dutta2024} into a leapfrog/drop decomposition over dozens
> of community-published quantized checkpoints, showing that fidelity proxies such
> as KL divergence lose their ranking signal in precisely the near-baseline regime
> our certification tables adjudicate --- motivating direct per-item measurement
> over proxy metrics. What none of this concurrent work provides, and what
> distinguishes our contribution, is the machinery that turns the shared premise
> into a decision: fail-closed statistical certification with equivalence testing
> and required-$n$ at a user-chosen margin, a preregistered test of whether the
> calibration seed \emph{reorders} the GPTQ-vs-AWQ ranking, a controlled study of
> harness and scoring sensitivity, and an audit of published near-lossless claims
> against a reproducible per-item protocol.

Citation keys are placeholders for `paper/refs.bib`: `TODO-illusion2026`
(2607.08734), `TODO-beyondmean2026` (2604.27405), `TODO-displacement2026`
(2606.19558), alongside the existing `TODO-calibdata2026`.

## Drafted blog sentence (acknowledging 2607.08734)

> We're glad to see Rababah, Akcora, and Leung's concurrent "The Illusion of
> Equivalency" (arXiv:2607.08734) reach a conclusion consistent with ours — that
> quantized models diverge from their base model item by item even when aggregate
> accuracy looks preserved. They get there on a quantization family we don't touch
> (llama.cpp GGUF, rather than GPTQ/AWQ) and with a metric, "correctness
> agreement," that turns out to be algebraically the same measurement as our
> per-item churn (churn = base accuracy + quantized accuracy − 2 × correctness
> agreement). Two independently developed studies, disjoint methods, the same
> phenomenon by equivalent math, the same answer: we read that as external
> corroboration of the premise this project then puts to a preregistered
> statistical test — with equivalence testing, a calibration-seed experiment, and
> an audit of published claims that their study, by design, doesn't set out to do.

---

## Dated Amendments

### Independence note re: arXiv:2607.08734 (2026-07-24, Amogh Singh)

Ruled and dictated by Amogh 2026-07-24; drafted into this file by the executing
session. This is a factual record, stated flatly and without an independence
*argument*.

- **(a) First awareness.** The first awareness of arXiv:2607.08734 ("The Illusion
  of Equivalency," Rababah, Akcora, Leung) was **2026-07-24**, through this
  prior-art sweep.

- **(b) Independent development.** The FlipEval registrations were developed and
  frozen without knowledge of that paper. `PREREGISTRATION.md` carries a
  doc-internal freeze date of **2026-07-11** and was first committed as `a8092df`
  on **2026-07-13**; the mini-grid, atlas-mining, and audit registrations, the
  frozen atlas pair manifest, and the audit claim table were committed on
  **2026-07-15** (`b74fd58`, `f06348f`, `715a7ce`).

- **(c) No precedence claim from the repository, stated without hedging.** **No
  committed artifact in this repository predates 2026-07-09**, the paper's arXiv
  posting date. The earliest commit of any kind is `a8092df` (2026-07-13); the
  earliest internal date-reference to project work anywhere in committed files is
  2026-07-10. Independence therefore rests on **independent development and
  non-knowledge, not on precedence**. We do not claim our work predates the paper.

- **(d) No priority claim on the shared premise.** We make **no priority claim**
  over arXiv:2607.08734 on the shared per-item accuracy-state-churn premise (the
  paired per-item correctness join their "correctness agreement" and our churn
  both measure; see Section 2). We cite it as **concurrent, corroborating work**.

**Reviewed and affirmed — Amogh Singh, 2026-07-24.** The facts as written are
accurate to my knowledge.
