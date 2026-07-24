# Prior-Art Note — "Understanding and Selecting Calibration Data for LLM Quantization" (2026-07-24)

Target: **"Understanding and Selecting Calibration Data for LLM Quantization:
From Sensitivity Analysis to Activation-Based Curation"**, OpenReview forum
`pfw3saHzGU` (<https://openreview.net/forum?id=pfw3saHzGU>).

Purpose: differentiate it from FlipEval, on the specific question of whether it
anticipates **H3** (seed-level *ranking instability* between GPTQ and AWQ under a
preregistered rule with paired statistics). Read-only on the repo.

---

## ⚠️ Source-access caveat — READ FIRST

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
vs AWQ head-to-head across seeds (see the honesty flag at the end).

---

## 1. Identity, authorship, venue, timeline

| field | value | status |
|---|---|---|
| Title | *Understanding and Selecting Calibration Data for LLM Quantization: From Sensitivity Analysis to Activation-Based Curation* | confirmed (forum + search) |
| Authors | **not retrievable** — not surfaced by search; likely anonymized under review or simply not indexed | **UNKNOWN — to-verify** |
| Affiliations | **not retrievable** | **UNKNOWN — to-verify** |
| Venue | reported as an **oral presentation at "ACL-SELVA 2026"** by one search result only | `[to-verify]` — single-source, possibly a hallucinated venue string; confirm on OpenReview |
| Decision / acceptance | not confirmed (the "oral" claim above is the only signal, unverified) | **UNKNOWN — to-verify** |
| Date | OpenReview record dated **2026-06-21/22** (search results split between the two adjacent days) | `[search-derived]` |

### Scoop-priority timeline

- Their record: **~2026-06-21/22**.
- Our registrations: `PREREGISTRATION.md` frozen **2026-07-11**; the mini-grid,
  atlas-mining, and audit registrations frozen **2026-07-15**.

So their calibration-sensitivity paper is **~3 weeks older** than our earliest
frozen registration. This matters for how we *position*, not for what we claim:
their public measurement predates our registration, which makes it **independent
corroboration of our premise** (that seed/calibration choices move the numbers a
compression comparison rests on) available *before* we committed to testing that
premise's consequence. It is not priority over H3, because — on the evidence
below — they do not run H3's test (see §5). Position it as antecedent evidence,
not as anticipation.

---

## 2. Their seed protocol `[search-derived]`

- **Three PTQ algorithms**: GPTQ, AWQ, and SmoothQuant+GPTQ.
- **Six models** from the **Qwen2.5 and Llama-3.1** families (named instances
  include **Qwen2.5-7B-Instruct** and **Llama-3.1-8B-Instruct** — the *same two
  models as our escalation 7B/8B cells*; see §6).
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

## 3. What they measured `[search-derived]`

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

## 4. The GSM8K variance interpretation `[to-verify — quote exactly on OpenReview]`

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

## 5. Paired analysis / statistical testing / flip accounting `[search-derived, absence]`

**No evidence of any of it.** Across every search the paper's reported
instruments are **aggregate accuracy ± ranges and perplexity fluctuation** —
descriptive dispersion, not inference. I found **no** mention of:

- paired per-item analysis (McNemar, paired bootstrap, per-item difference
  vectors);
- statistical significance testing of a method difference;
- winner-flip / rank-change accounting across seeds;
- a preregistered decision rule over the variance.

This is the load-bearing distinction. Their ± ranges answer *"how stable is a
method's accuracy under resampling?"*; H3 answers *"does the seed reorder which
method wins, and is that instability real under a paired test?"* — the winner-flip
count, the range/gap screen, and the two-level paired bootstrap
(`PREREGISTRATION.md` §"H3 Decision Rule") have no counterpart in what they
report. **Caveat:** absence in search summaries is not proof of absence in the
paper; the human should scan the results tables directly (see the honesty flag).

## 6. Overlap with the FlipEval legs

- **H3 / mini-grid (the one that matters):** *premise overlap, not result
  overlap.* They resample calibration seeds and observe accuracy variance; we
  test whether that variance flips the GPTQ-vs-AWQ ranking under a frozen rule
  with paired statistics. Their same-day corroboration of the *premise* is
  useful; it does not touch the *result*. **Model overlap is worth noting:** they
  study Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, our exact escalation 7B/8B
  models — so a reviewer may see them as adjacent, and we should pre-empt that by
  citing them as the antecedent measurement.
- **Harness-sensitivity leg:** *convergent, independent.* Their GSM8K
  "exact-match evaluation noise" attribution is the same phenomenon our §
  configuration-sensitivity study quantifies (condition B). Cite them as external
  corroboration that the scoring/eval surface is a real variance source.
- **Audit leg:** *no overlap.* They audit no published equivalence/near-lossless
  claims; they propose a curation method (ACDM). Our audit of 17 claims and the
  required-*n* framing are orthogonal.
- **Atlas leg:** *no overlap.* No public-record atlas of compression pairs; their
  evaluation is their own six models on five benchmarks.
- **Certification / sequential legs:** *no overlap.* No equivalence margin, no
  TOST, no required-*n* tables, no anytime-valid stopping.

---

## Drafted paragraph for the paper (Related Work — calibration sensitivity)

> Concurrent with our registration, \citet{TODO-calibdata2026} study calibration
> data for post-training quantization across GPTQ, AWQ, and SmoothQuant+GPTQ on
> six Qwen2.5 and Llama-3.1 models, resampling the calibration set across three
> seeds and reporting the resulting accuracy variance. They observe that
> seed-to-seed accuracy is stable in aggregate but that GSM8K carries the largest
> per-task spread, which they attribute to the ``inherent evaluation noise of
> exact-match scoring''. Their measurement is corroborating evidence for our
> premise --- that calibration-seed choice moves the very numbers a compression
> comparison rests on --- but it is not an anticipation of our result: they read
> the variance as noise to be smoothed, and report aggregate $\pm$ ranges, whereas
> we test whether that same variance \emph{reorders} GPTQ and AWQ under a
> preregistered winner-flip-and-range/gap rule adjudicated with paired,
> seed-blocked statistics. Where they ask how robust a method's accuracy is to
> resampling, we ask whether resampling changes which method wins.

Citation key `TODO-calibdata2026` is a placeholder; fill authors/venue into
`paper/refs.bib` once the OpenReview page is read directly.

---

## ⚠️ Honesty flag (as the task required)

The task asked to flag anything *closer to H3 than the summary implies*, and
specifically any place they compare GPTQ vs AWQ across seeds verbatim.

- **What I can say:** on all retrievable evidence their GPTQ/AWQ comparison is a
  *sensitivity-profile* contrast (GPTQ is domain-sensitive on Qwen specialized
  variants; AWQ is activation-driven), and their head-to-head *method*
  comparison is ACDM vs calibration-selection baselines — neither is a
  seed-indexed GPTQ-vs-AWQ accuracy ranking, and I found no flip/paired-test
  machinery.
- **What I cannot rule out:** because the full PDF was inaccessible, I cannot
  exclude a results table that happens to print GPTQ and AWQ accuracies side by
  side per seed. If such a table exists, it would still not be H3 (no rule, no
  paired test, no flip accounting), but the human should eyeball the results
  section to be certain no sentence reads as a ranking-stability claim. **This is
  the one gap that must be closed by opening the source before we finalize the
  related-work positioning.**

## Sources consulted

- OpenReview forum (walled): <https://openreview.net/forum?id=pfw3saHzGU>
- Web search corroboration across five queries (2026-07-24), covering the seed
  protocol, aggregate/GSM8K variance, ACDM gains, and GPTQ/AWQ sensitivity.
  OpenReview and both API hosts unreachable via WebFetch (Cloudflare challenge);
  Semantic Scholar 504/429.
