# FlipEval — Paper Reading Copy

**Generated 2026-07-27T20:03:43Z from `paper/main.tex` at commit `2560919`.**

No PDF: the Phoenix login node has no `pdflatex`, `xelatex`, `lualatex`, `latexmk`, `tectonic` or `pandoc`, and the pinned Apptainer image is an ML runtime with no TeX distribution. Per the fallback, the sections are concatenated **verbatim, in `main.tex` input order** (nested `\input` expanded in place), with no content edits. LaTeX markup is left as-is deliberately: substituting rendered text would be an edit.

A reader's index is at the end.


---

## FILE: `paper/abstract.tex`

```latex
% Atlas figures below are REV-2 (2026-07-21), resolved after the targeted
% second spot-check passed 14/14 cells, 126/126 fields. Keep in sync with
% sections/{atlas,certification,audit,minigrid}.tex.
%
% H3 VARIANT SELECTION CLOSED 2026-07-27. All eight registered confirmatory
% cells exist and the frozen support rule fired, so variant (A) was selected and
% the dead (B)/(C) blocks and their selection instructions were deleted. The
% verdict sentence below is variant (A) with one word changed -- see the note at
% that paragraph.
%
% SUMMARY-RESTATEMENT INVARIANT (paper/OUTLINE.md rule 4): this file contains no
% primary figures. Every number here appears in the section it summarises at
% coarser or equal precision. Walked figure-by-figure on 2026-07-27; the walk is
% recorded in the commit that introduced this revision.

\begin{abstract}
A difference of a fraction of a point in benchmark accuracy is the standard
evidence that a compressed language model is equivalent to its original. We show
this quantity is least informative precisely when two models are most alike: a
net delta is what survives cancellation between opposing per-item changes, and
cancellation is most complete in exactly the regime every equivalence claim
occupies.

% SOURCE: \S\ref{sec:atlas:netgross} (5.3x, ratio of medians on the 1,707-cell
% rev-2 population); \S\ref{sec:minigrid:churnratio} Result 1 (median 12.7x);
% \S\ref{sec:atlas:identical} (145 cells, 8.49% -> 8.5%; churn median 0.0720
% -> 7.2%).
Across an atlas of 1{,}707 paired model-by-task cells mined from public
per-item evaluation dumps (3B to 405B parameters), per-item churn runs
$5.3\times$ the net accuracy delta; between two compression methods at one bit
width, the median is $12.7\times$. At the limit, 145 cells (8.5\%) post an
\emph{exactly identical} accuracy to their baseline while disagreeing on a median
of 7.2\% of items.

% SOURCE: \S\ref{sec:audit:results} and Table~\ref{tab:audit-underpowered}
% (4 of 12, 2.0x-12.9x); \S\ref{sec:audit:indeterminate} (5 of 17);
% \S\ref{sec:audit} (0 of 17 release per-item outputs).
In a preregistered audit of 17 equivalence claims from method papers, model
cards and vendor documentation, \textbf{4 of the 12 whose reporting
permits a verdict are underpowered for their own assertion}, by factors of
$2.0\times$ to $12.9\times$; a further \textbf{5 of the 17} cannot be evaluated
at all. \textbf{None of the 17 sources releases the per-item outputs a third
party would need to run the paired comparison itself.} No claim is asserted
false; we audit evidential sufficiency, not truth.

% SOURCE: \S\ref{sec:certification}, Table~\ref{tab:certification}
% (mmlu median 2,164; gpqa median 749) and \S\ref{sec:cert:churn-not-difficulty}.
% LENGTH CUT 2026-07-27: the 4.2x pooled paired-advantage figure was dropped
% here to reach the target length, per the drafting instruction's stated cut
% order. It remains in \S\ref{sec:intro} and Table~\ref{tab:certification}.
We supply the missing apparatus: equivalence testing at a declared margin, and
\emph{certification tables} giving the items an evaluation needs, computed from
disagreement actually observed under compression rather than from
independent-binomial variance. The requirement follows churn, not difficulty:
MMLU needs about 2{,}164 items at a 2\,pp margin where the harder GPQA needs
749.

% SOURCE: \S\ref{sec:minigrid:verdict}; docs/H3_EIGHT_CELL_DECISION_2026-07-26.md
% (SIGNED). This is drafted variant (A) with ONE word changed: it read "not
% reproducible", which over-claims against the bootstrap result of
% \S\ref{sec:minigrid:supporting} (three cells show individual seeds disagreeing
% while the five-seed mean survives resampling). "Unreliable" is what the
% evidence carries. The registered artifact is the decision rule and the
% verdict, not this prose; the change and its cause are recorded in
% docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md.
A preregistered controlled experiment pairs GPTQ and AWQ on byte-identical
calibration samples across five seeds. Under the frozen eight-cell
decision rule, H3 is supported: the calibration seed alone reorders the two
methods in \textbf{5 of 8} confirmatory cells, so a single-calibration
comparison is unreliable.

Every protocol was frozen before the analysis it governs, and every number here
is recomputable from released artifacts.
\end{abstract}
```

---

## FILE: `paper/sections/introduction.tex`

```latex
% Atlas figures below are REV-2 (2026-07-21), resolved after the targeted
% second spot-check passed 14/14 cells, 126/126 fields. Keep in sync with
% sections/{atlas,certification,audit,minigrid}.tex.
% =====================================================================
% Section: Introduction.
% Numbers here must mirror sections/audit.tex, certification.tex, atlas.tex and
% minigrid.tex exactly; if one changes, change both. SOURCE comments repeated
% for safety. This file is DERIVATIVE -- it contains no primary figures
% (paper/OUTLINE.md rule 4, the summary-restatement invariant).
% =====================================================================

\section{Introduction}
\label{sec:intro}

A compressed language model is usually released with a sentence of the form
``negligible degradation'' or ``$99.x\%$ recovery'', supported by a difference of
a fraction of a point in aggregate accuracy on a fixed benchmark. That sentence
is an equivalence claim. Equivalence claims have a statistical form---a declared
margin, a test, and a sample size sufficient to reject the composite null that
the difference exceeds the margin---and the sentence almost never has it.

The problem is worse than a missing test, because the evidence being offered is
weakest exactly where it is being offered. A net accuracy delta is the residue
left after per-item changes in opposite directions cancel. The more alike two
models are, the more completely those changes cancel, and the smaller the
residue becomes relative to the behavioural change underneath it. So the
quantity the field uses to establish that two models are the same is least
informative precisely in the regime where that claim is made. Everything in this
paper follows from taking that observation seriously and measuring it.

\paragraph{The audit.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Headline; results/audit_verdicts.csv.
Of 17 equivalence claims enumerated from method papers, official quantized model
cards, and inference-stack vendor documentation, 5 cannot be evaluated at all
from what they report, and \textbf{4 of the remaining 12 are underpowered for
their own assertion}: the smallest difference their evaluation could resolve
exceeds the difference they pronounce negligible, by $2.0\times$ to
$12.9\times$. \textbf{None of the 17 releases the per-item outputs} that a third
party would need to run the paired comparison the claim asserts. No claim is
described as false; the audited property is the evidential sufficiency of the
reported evaluation. \TODO{one-sentence example of a claim + its shortfall,
chosen for legibility, once the section is final}

\paragraph{The fix.}
Equivalence is a certification problem. We compute certification tables---how
many items an evaluation needs in order to certify a compressed model within
$\pm m$ points of its baseline---from the per-item disagreement rates actually
observed under compression rather than from independent-binomial variance.
% SOURCE: results/certification_tables_rev2.csv column paired_advantage_at_median
% (GSM8K 2.25--2.26, MuSR 14.66--14.68); docs/CERTIFICATION_TABLES_2026-07-20.md
% §"Why the naive column". REV-2: GSM8K end was 1.7x under rev-1; corrected
% 2026-07-26 to agree with Table~\ref{tab:certification} and §5.
The correction is large: $2.3\times$ to $14.7\times$ fewer items by family,
$4.2\times$ pooled. And the requirement is set by churn rather than difficulty,
which defeats the natural intuition: MMLU needs about 2{,}164 items at 2\,pp
where the harder GPQA needs 749.

\paragraph{The evidence.}
% SOURCE: \S\ref{sec:atlas:netgross} (5.3x on the rev-2 1,707-cell population);
% docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §Results;
% results/identical_score_churn_rev2.csv (analysable_cells 1707,
% zero_delta_cells 145, zero_delta_share 0.084944, churn_median 0.072000).
% REV-2: "a median of 6.2%" was rev-1's churn_median 0.062176 and was corrected
% to 7.2% on 2026-07-26, in step with the abstract and
% \S\ref{sec:atlas:identical}. All three state the same quantity.
% REV-1 SURVIVOR, CORRECTED 2026-07-27: "five to six times" was rev-1's ratio;
% the rev-2 value is 5.3x in both strata. Fourth such survivor found.
Both rest on an atlas of 1{,}707 paired model-by-task cells mined from public
per-item evaluation dumps spanning 3B to 405B parameters, in which churn runs
$5.3\times$ the net delta, and 145 cells (8.5\%) post an exactly identical
accuracy to their baseline while still disagreeing with it on individual items,
at a median of 7.2\% of items. The ratio is remarkably stable across a
generational change in method: the two strata differ by nearly a factor of three
in how much behaviour they disturb, and understate that disturbance by the same
multiple---better methods have made the difference smaller without making the
evidence for equivalence any more sufficient (\S\ref{sec:atlas:netgross}).

\paragraph{The controlled experiment.}
% SOURCE: \S\ref{sec:minigrid:verdict};
% docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED, 05c86f2);
% \S\ref{sec:minigrid:churnratio} Result 1 (median 12.7x).
The same logic predicts something sharper, and a preregistered experiment tests
it. If cancellation grows with similarity, then the least informative comparison
of all is not compressed against original but \emph{compressed against
compressed}---two methods at the same bit width, which are far closer to each
other than either is to its baseline. Pairing GPTQ and AWQ on byte-identical
calibration samples across five calibration seeds, over eight registered
model-by-benchmark cells, we find churn running a median of $12.7\times$ the net
delta, more than double the atlas ratio; and under the frozen eight-cell decision
rule \textbf{H3 is supported}---the calibration seed alone reorders the two
methods in \textbf{5 of 8} cells. Which of two compression methods wins can be
decided by a random draw of calibration data, at a gap the field would report as
equivalence.

\paragraph{The instrument is not fixed either.}
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §§1, 7;
% docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md §4.2 (0.232 -> 0.566 on unchanged
% generations); \S\ref{sec:sensitivity} for the registered ratio R.
All of the above assumes the evaluation itself holds still. A small preregistered
exploratory study says it does not: on a single fixed FP16 model, changing the
answer-extraction filter moved reported GSM8K accuracy from $0.232$ to $0.566$
with \emph{not one token of model output changed}. That is a scoring decision,
not a modelling one, and it is larger than every compression effect in this
paper. It is one model and licenses no confirmatory reading
(\S\ref{sec:sensitivity}), but a reader can check it in an afternoon on the
pinned harness version, and it bounds how much any unstated configuration choice
can be worth.

\paragraph{What is new, and what is not.}
Per-item flips as a diagnostic for compressed models are due to
\citet{dutta2024flips}, and calibration-\emph{data} effects on quantization
quality are due to \citet{williamsaletras2024}; we claim neither. Our
contributions are (i) the preregistered audit of published equivalence claims
and its verdict artifact; (ii) empirical certification tables and the
paired-design correction they quantify; (iii) the atlas of the public record,
and the measured cancellation ratio in both the observational and controlled
regimes; and (iv) a preregistered seed-paired experiment showing that the
calibration seed alone reorders two compression methods in 5 of 8 registered
cells. Relative to the closest existing work \citep{llmaccuracystats2026}, which
performs one-sided McNemar \emph{detection}, our delta is the shift from
detection to certification: a declared margin, TOST, and required-$n$ tables.

\paragraph{Preregistration.}
All protocols were frozen before the analyses they govern
(\S\ref{sec:prereg}), deviations are dated amendments rather than edits, and
the analyst decisions that moved the headline are reported together with the
direction they moved it---including the two corrections that removed the
paper's largest numbers.

\TODO{paper-map paragraph and artifact URLs/DOI once minted}
```

---

## FILE: `paper/sections/related_work.tex`

```latex
% =====================================================================
% Section: Related work and positioning.
% Rule for this section: cite honestly and preemptively. Every prior claim we
% do NOT own is attributed in the same paragraph where our version appears.
%
% BIBLIOGRAPHY STATUS (2026-07-27): the placeholder file paper/refs.bib is
% retired. Every key cited here resolves to a verified entry in
% paper/references.bib, each carrying a comment naming the primary source it
% was read from and the date it was read. The sweep's search record --
% databases, dates, queries, screened counts -- is in
% docs/related_work_checklist.md §"Sweep Record".
% =====================================================================

\section{Related work and positioning}
\label{sec:related}

\subsection{Per-item behaviour under compression}

\citet{dutta2024flips} show that compressed models can match baseline aggregate
accuracy while flipping many individual answers, and propose flips and KL
divergence as complementary metrics. \textbf{The flips metric is theirs, and we
do not claim it.} What we add is (i) the same decomposition measured across the
public record at scale rather than in a controlled study
(\S\ref{sec:atlas}), (ii) the use of the observed flip-rate distribution as the
\emph{variance model} for equivalence certification
(\S\ref{sec:certification}), and (iii) the audit that follows from it
(\S\ref{sec:audit}).

Concurrent work reaches the same premise independently.
\citet{rababah2026illusion}, posted two days before our preregistration froze
and unknown to us until the prior-art sweep of 2026-07-24, define
\emph{correctness agreement}---the per-item rate at which base and quantized
models are both correct on the same input. That statistic is the joint-correct
cell of the same $2\times2$ table our accuracy-state churn is built from, and
the two are interconvertible given the marginal accuracies: with $a$ both
correct, $b$ base-only correct and $c$ quantized-only correct,
$\mathrm{churn} = (b+c)/n = \mathrm{Acc}_{\mathrm{base}} +
\mathrm{Acc}_{\mathrm{quant}} - 2\,\mathrm{CA}$. They study a quantization
family disjoint from ours---\texttt{llama.cpp} GGUF legacy and $k$-quant rather
than GPTQ and AWQ---and reach a conclusion consistent with ours. We read this as
external corroboration of the premise, not competition on it, and we make no
priority claim over it: no committed artifact in this repository predates its
posting.
% SOURCE for the independence and no-precedence statements:
% docs/PRIOR_ART_CONCURRENT_2026-07-24.md, "Dated Amendments" (a)-(d),
% reviewed and affirmed by the author 2026-07-24.
What they do not supply, and what the rest of this paper is, is the machinery
that turns the shared premise into a decision: equivalence testing at a declared
margin, required-$n$, a preregistered test of whether the calibration seed
reorders two methods, and an audit of published claims. Their paper reports no
equivalence test, no power or sample-size computation, and no per-item release;
it also reports a layer-level analysis---query and key projections more
sensitive than value and output---that we do not attempt.

Two further concurrent studies measure per-item change on adjacent objects.
% SOURCE: docs/PRIOR_ART_CONCURRENT_2026-07-24.md §§3-4, both verified against
% the raw arXiv HTML rendering.
\citet{cacioli2026beyondmean} adapts the clinical Reliable Change Index to
per-item comparisons between model \emph{versions} rather than precisions, and
likewise recommends reporting a churn rate beside the mean;
\citet{nikolic2026displacement} extend the flips metric into a leapfrog/drop
decomposition over dozens of community-published quantized checkpoints, and find
that KL-divergence proxies lose their ranking signal in precisely the
near-baseline region our certification tables adjudicate.

\subsection{Calibration sensitivity in post-training quantization}

\citet{williamsaletras2024} establish that the calibration \emph{data} affects
quantized model quality, finding substantial variation in downstream task
performance across calibration sets. \textbf{Calibration-data effects are
theirs.} Our registered question is orthogonal and finer-grained: holding the
calibration corpus fixed, does the calibration \emph{sample seed} change the
\emph{ranking} of two methods? The design pairs GPTQ seed $s$ and AWQ seed $s$ on
byte-identical calibration samples, so a seed-level ranking difference is
attributable to method-by-calibration interaction rather than to the two methods
seeing different data (\S\ref{sec:minigrid}).

The sweep found no prior work that varies a calibration \emph{seed} with the
corpus held fixed and asks whether the resulting instability reorders two
methods. The nearest antecedents vary the calibration set itself, and they
disagree with each other about how much that matters---which is the subject of
\S\ref{sec:related:reconcile}.

\subsection{The literature disagrees with itself, and our design says why}
\label{sec:related:reconcile}

\textbf{The two most direct antecedents of this paper reach opposite
conclusions about the same knob.} \citet{williamsaletras2024} find
\emph{substantial} variation in downstream task performance across calibration
sets, explicitly contrasting their result with prior work that suggested greater
robustness. \citet{paglieri2024outliers} find the effect \emph{diminishing}:
where the older OPT models degrade badly and vary with the calibration set,
Llama-2 7B, Llama-3 8B, Command-R 35B and Mistral 7B are robust, with Mistral 7B
close to immune, and they argue the field should stop building its quantization
literature around outlier preservation. Both are careful studies of calibration
sensitivity, published within a year of each other, pointing in opposite
directions.

The second of these is also the strongest available objection to this paper,
and it is the one a reader is most likely to arrive already holding: if modern
models are insensitive to the calibration set, why would the calibration seed
reorder anything?

Our answer is that both results hold at once, and that the disagreement between
them is a symptom of measuring the wrong thing for the question the field
actually asks. Three differences do the work, and our own numbers show why.

\paragraph{The intervention is different, and ours is strictly finer.} Both
antecedents vary the calibration \emph{data}. \citet{paglieri2024outliers} do it
across sets differing in quality, content and language---a
RedPajama sample, calibration drawn from uniformly random ASCII punctuation and
whitespace, task-specific sets from ARC-Challenge and PiQA, and multilingual
sets from FLORES+. We hold the corpus fixed and vary only the sample seed, an
intervention they do not make. A finding that swapping the corpus for random
punctuation barely moves accuracy does not entail that redrawing the sample
leaves the \emph{ordering} of two methods intact; the two questions are not
nested in the direction the objection needs.

\paragraph{The unit of analysis is different.} \citet{paglieri2024outliers}
study one method at a time, reporting GPTQ W4A16, AWQ W4A16, SmoothQuant W8A8
and a naive W8A8 baseline in separate result sections, and they report no
head-to-head ranking between methods and no ranking flips. Our unit of analysis
is the \emph{gap between} two methods at the same bit width---a quantity neither
antecedent's design measures.

\paragraph{Individual robustness plus a small method gap implies ranking
instability.} This is the reconciliation proper, and it is not a rhetorical
move: it is what \S\ref{sec:minigrid} measures. Each method is individually
stable in absolute accuracy, much as they report---and the seed-induced range is
at least as large as the mean GPTQ--AWQ gap in 7 of our 8 confirmatory cells.
% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED), "Mechanical
% application of the rule": range/gap holds in 7 of 8. Wording follows that
% record's own "at least as large as"; do not tighten it to "smaller than".
Those two facts together \emph{are} ranking instability. We are not
contradicting their robustness finding; we are showing it has a consequence they
did not test for. A field that reads ``calibration choice barely moves accuracy''
as licence to compare two methods from one calibration run each has drawn the
wrong inference from a correct result.

\paragraph{The magnitude question, answered honestly.} Robustness claims are
claims about size, so the reconciliation has to be quantitative. The figures
that follow come from a \emph{post-hoc} resolution analysis, prompted by this
very paper and labelled as such wherever it appears (\S\ref{sec:minigrid}); it
is descriptive and modifies no verdict. On MMLU our seed-induced ranges run 5.5
to 17.5 paired standard errors---a spread no robustness claim reaches, and one
the benchmark resolves comfortably at $n = 14{,}042$.
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, step 5 table,
% max_range/SE column, MMLU rows: 11.07, 17.45, 5.53, 11.19.
On GSM8K at $n = 1{,}000$ the same ranges run roughly two standard errors, and
we say so rather than averaging the two tasks together: that arm of the
experiment does not resolve the effect it was built to measure
(\S\ref{sec:minigrid:resolution}, \S\ref{sec:limitations}).
% SOURCE: same table, GSM8K rows: 1.92, 2.35, 3.61, 2.45.

\paragraph{What the disagreement was about.} Read this way, the two antecedents
are not really in conflict. \citet{williamsaletras2024} and
\citet{paglieri2024outliers} both measure how much a \emph{single} method's
absolute accuracy moves when the calibration data changes, and they disagree
about the size of that movement on the model generations each studied. Neither
measures what a practitioner comparing two methods actually depends on---that the
\emph{ordering} survives---and a quantity nobody measured is one the field has no
basis to assume stable. Our design does not settle their disagreement. It shows
that settling it would not have answered the question either way.

\subsection{Losslessness, defined and achieved versus audited}

\citet{helcig2026slq} occupy the phrase this paper is about. They formalise
three notions of losslessness for quantized LLMs---task-lossless (zero-shot
accuracy preserved within sampling variance), the stricter
distribution-lossless (next-token distributions practically indistinguishable),
and a $\gamma^2$ variance law relating symmetric to asymmetric
quantization---propose the Expected Acceptance Rate as an interpretable fidelity
metric, and ship SLQ, a method that reaches those targets at low bit widths.

Their question and ours are different, and the difference is the whole of
\S\ref{sec:certification}. \emph{They define losslessness and build a method to
achieve it.} \emph{We audit whether existing published claims of losslessness
have the evidence to support them, and compute how many items it would take to
certify one.} Their paper contains no equivalence test at a declared margin, no
power or required-$n$ computation, no McNemar test, and no audit of others'
claims; ours contains no quantization method. The two are complements: a
practitioner who adopts EAR as a fidelity target still needs to know how large
an evaluation must be before the accuracy half of a losslessness claim means
anything, and that number is what our certification tables supply.

\subsection{Statistics for language-model evaluation}

The closest existing work is \citet{llmaccuracystats2026}, which brings
one-sided McNemar \emph{detection} to LLM accuracy comparisons and ships it in
the evaluation harness the field already uses. We agree with its diagnosis and
differ in the question asked. Detection asks whether there is evidence of a
difference; a non-significant result is not equivalence, and at the sample sizes
in \S\ref{sec:audit} it is frequently just an absence of resolution. Our deltas
are: (i) TOST certification at a \emph{declared} margin;
(ii) required-$n$ certification tables computed from empirical churn rather than
% SOURCE: results/certification_tables_rev2.csv column paired_advantage_at_median
% (GSM8K 2.25--2.26, MuSR 14.66--14.68). REV-2: the low end was 1.7 under rev-1;
% corrected 2026-07-26 with the abstract, introduction and §5.
from independent-binomial variance, with the $2.3$--$14.7\times$ correction that
implies; and (iii) the audit of published claims, which is the
empirical case that the distinction matters in practice. An anytime-valid
sequential extension---confidence sequences that let a practitioner stop as soon
as the model is certified---is registered and in progress; it reports no results
here and is not claimed as a contribution of this paper.

\subsection{Reporting-standards audits}

The constructive-audit genre is well established: \citet{dodge2019showyourwork}
on reporting the compute and search behind reported numbers, and
\citet{marie2021mtaudit} on the statistical practice of machine-translation
evaluation. We follow both in framing and in tone: the finding is about what the
field reports, not about whether individual authors are right, and the paper's
deliverable is a standard plus the tooling to meet it. The genre has also begun
to adopt preregistration directly, which is the precedent for
\S\ref{sec:prereg}: \citet{gringras2026frontierlag} run a preregistered
bibliometric audit of which models the evaluation literature actually tests, and
\citet{thomas2026prereg} propose preregistering an analysis against a model not
yet released, so that the configuration cannot be tuned against the outcome.

\subsection{Compression methods audited}

The audited claims span the two dominant post-training families. Weight-only
quantization is represented by GPTQ \citep{gptq2022}, AWQ \citep{awq2023} and
SqueezeLLM \citep{squeezellm2023}; weight-and-activation quantization by
LLM.int8() \citep{llmint82022} and SmoothQuant \citep{smoothquant2022};
one-shot pruning by SparseGPT \citep{sparsegpt2023} and Wanda
\citep{wanda2023}. We audit the equivalence \emph{language} these papers use
and the evidence offered for it, not the methods themselves, and the audit's
verdicts are about reporting practice rather than about whether a method works.
Two of the most aggressive methods in the set are also the most restrained in
what they assert: SpinQuant \citep{spinquant2024} and QuIP\#
\citep{quipsharp2024} report their accuracy deltas without equivalence
language, and are cited here as positive examples alongside the Qwen quantized
model cards and the \texttt{llama.cpp} documentation.
% SOURCE for the honest-non-claimer list:
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §2, "Honest non-claimers" bullet.
```

---

## FILE: `paper/sections/preregistration.tex`

```latex
% =====================================================================
% Section: Preregistration, freezes, and analyst degrees of freedom
% -- COMPLETE DRAFT
%
% TRIMMED 2026-07-26. The disclosed-contact subsection, the seven interpretive
% choices in full, and the full spot-check narrative moved VERBATIM to
% sections/appendix_prereg_detail.tex. Nothing was deleted in the move. What
% stays here is the freeze timeline, a pointer-summary of the contact, the
% compressed choice-1 statement, inspection discipline, the full H3 rule, and a
% three-point spot-check summary.
%
% PRIMARY SOURCES:
%   PREREGISTRATION.md                        (frozen 2026-07-11)
%   docs/AUDIT_REGISTRATION_2026-07-15.md     (frozen; Amendment 1 appended)
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md (frozen)
%   docs/MINIGRID_REGISTRATION_2026-07-15.md  (frozen)
%   docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices", §Provenance
%   docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3 (freeze commits)
%
% DISCLOSURE BOUNDARY -- ENFORCE ON EVERY EDIT.
% The retired "6.3% flips at identical score" anecdote (bnb-4bit same-repo
% rerun) NO LONGER APPEARS IN THIS FILE. It moved to
% sections/appendix_prereg_detail.tex on 2026-07-26 and that file is now the
% ONLY place it may appear in any FlipEval text. Do not reintroduce it here,
% in the abstract, in §\ref{sec:atlas}, or anywhere in the blog post. The
% boundary comment travels with the anecdote; the authoritative statement of it
% is at the top of appendix_prereg_detail.tex.
% =====================================================================

\section{Preregistration, freezes, and analyst degrees of freedom}
\label{sec:prereg}

An audit paper is only as good as its own protocol discipline. This section
documents that discipline, including where it cost us the result we would have
preferred; readers who want results first may skip to \S\ref{sec:audit}. Full
text of the disclosures, the interpretive rulings and the spot-check is in
Appendix~\ref{app:prereg-detail}.

\subsection{What was frozen, and when}
\label{sec:prereg:timeline}

% SOURCE: PREREGISTRATION.md header lines 3-7;
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3 (commits b74fd58, d6e02dd, f06348f,
% 715a7ce); docs/AUDIT_VERDICTS_2026-07-20.md §Provenance (claim-table sha256).
\begin{table}[t]
\centering
\small
\caption{Freeze timeline. Each artifact was committed before the analysis it
governs could be run, and each frozen file carries a \emph{Dated Amendments}
section: deviations are appended, never edited in, and each records whether
results had been inspected before the decision.}
\label{tab:freeze-timeline}
\begin{tabular}{llll}
\toprule
Date & Artifact & Commit & What it fixed in advance \\
\midrule
2026-07-11 & \texttt{PREREGISTRATION.md} & --- & Grid, metrics, TOST margin (2\,pp), H3 decision rule \\
2026-07-15 & Three registrations & \texttt{b74fd58} & Audit, atlas-mining, and mini-grid protocols \\
2026-07-15 & Audit Amendment 1 & \texttt{d6e02dd} & Blind-extraction independence mechanism \\
2026-07-15 & Pair manifest & \texttt{f06348f} & The 59 atlas pairs, before any flip statistic \\
2026-07-15 & Claim table & \texttt{715a7ce} & The 17 audited claims, before any verdict \\
2026-07-20 & WikiText-2 amendment & --- & ``Document'' definition, Decision Point A \\
\bottomrule
\end{tabular}
\end{table}

The frozen claim table's content hash is recorded with the verdicts
(sha256 \texttt{842b9756...5af7b15}), as is the atlas summary's
(\texttt{98201ade...10a4712d}) and the container image's, so a reader can
confirm the inputs to any reported number were the frozen ones. Three properties
of this arrangement do work in the paper. The mechanical parts of the
audit---inclusion trigger vocabulary, extraction fields, verdict formulas,
robustness sweep---were fixed before any claim's power was computed, so the
audit cannot have selected its claims or its statistics to produce a headline;
the atlas pair list was frozen before any flip statistic, so the atlas cannot
have selected pairs to produce churn; and the H3 decision rule was fixed, in
algebra, before the first compressed checkpoint existed, so the paper reports
whatever that rule returns.

\subsection{Disclosed pre-registration data contact}
\label{sec:prereg:contact}

% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md §1;
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §1;
% docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §"Why this note exists".
% Full text, including the retired anecdote, at app:prereg:contact. Do not
% restate the anecdote here -- see the disclosure boundary at the top of this
% file.
Preregistration is a claim about ordering, so the places where our order was
imperfect are disclosed by the registrations themselves rather than discovered
by a reader. Three exist, all recorded in the frozen documents: five audit
claims collected as exact quotes before the audit registration was written, with
no power computation run on any of them; two atlas feasibility probes whose
results were known before the mining registration was drafted, flagged and
excluded from every headline aggregate at the level of the whole pair (99 cells,
not two tasks); and one pre-registration motivating observation, retired from
every quantitative use both because it is pre-registration contact and because
it lies outside the frozen 59-pair manifest, its registered replacement being
the identical-score statistic of \S\ref{sec:atlas:identical}.
Appendix~\ref{app:prereg:contact} gives all three in full.

\subsection{The interpretive choices that moved the headline}
\label{sec:prereg:choices}

Frozen protocols do not eliminate analyst judgement; they make it visible and
datable. Seven passages of the audit registration were ambiguous enough to
require a ruling before verdicts could be computed. All seven were ruled on
2026-07-20, each is implemented in code, each is reversible by re-running with
the alternative, and all seven are stated in full in
Appendix~\ref{app:prereg:choices}. One carries a methodological point that
belongs in the main text.

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #1,
% including the "Methods-narrative note" paragraph; K values cross-checked
% against results/audit_verdicts.csv columns verdict and
% verdict_at_registered_2pp.
The frozen §4 names the 2\,pp registered margin first, adds ``(and at the
claim's own margin when it states one)'', and labels the verdict
``underpowered for its own assertion'' \emph{at the applicable margin}. Two
readings survive that text: a uniform 2\,pp yardstick gives $K = 1$ of 12, while
each claim's own stated margin gives $K = 5$, and $K = 4$ after the ruling that
moved R04 out of the determinate set. \textbf{The first pass of this analysis
returned $K = 1$.} Re-reading the frozen label produced $K = 5$---a source
asserting parity within 0.15\,pp has made a 0.15\,pp claim, and judging it
against a 2\,pp yardstick audits a claim nobody made---and the third ruling then
yielded the reported $K = 4$.

The order in which those numbers arrived is the point. \emph{The correction ran
against the direction the analyst's first instinct had gone.} The first pass had
already produced a defensible, publishable, conservative number; the frozen text
required a larger one and governed. That is the evidence available, from inside
a solo-authored project, that the rule text drove the analysis rather than the
desired result---and had it run the other way, the same discipline would have
required reporting the smaller number. Both readings ship in the released CSV
(\S\ref{sec:audit:results}).

\subsection{Result-inspection discipline}
\label{sec:prereg:discipline}

% SOURCE: CLAUDE.md/AGENTS.md project guardrails; PREREGISTRATION.md
% §"Outcomes and Analysis"; docs/MINIGRID_REGISTRATION_2026-07-15.md §5.
During grid execution only job health, checksums, expected-file coverage and
receipt pairing are inspected; the first accuracy inspection happens only after
the mini-grid validator passes over the complete expected file set. The
registered analysis is run once per cell, the escalation rule applied
mechanically, and a dated escalation decision record written the same day. The
paired-bootstrap rank-flip denominator convention (tie replicates included,
ties also reported separately) was fixed in words in the registration, naming
the implementing commit, so it cannot be re-chosen after inspection. No
registered analysis---calibration builder, paired bootstrap, or verdict
rule---is tuned after results are seen.

\subsection{The H3 reporting rule, stated before the results exist}
\label{sec:prereg:h3rule}

% SOURCE: PREREGISTRATION.md §"H3 Decision Rule";
% docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 3, 4.
% THIS FILE STATES NO H3 OUTCOME. That is deliberate and survives the signed
% verdict of 2026-07-26: §3's job is the protocol, §7's is the result. Updated
% 2026-07-27 only to stop asserting the four-cell contingency as live -- all
% eight cells completed, so that branch never fired.
The registered decision rule is defined over eight confirmatory
model-by-benchmark cells:
$\{$Qwen2.5-1.5B, Qwen2.5-7B, Llama-3.2-3B, Llama-3.1-8B$\}
\times \{$MMLU, GSM8K$\}$ at 4 bits, comparing GPTQ seed $s$ against AWQ
seed $s$ on byte-identical calibration samples. H3 is \emph{supported} if winner
flips occur in at least 3 of the 8 cells, or the range/gap criterion holds in at
least 4 of the 8. It is \emph{disconfirmed} if winner flips occur in at most 1
of the 8 and $\max(\mathrm{range}_{\mathrm{GPTQ}}, \mathrm{range}_{\mathrm{AWQ}})
< 0.5 \times \mathrm{gap}$ in at least 6 of the 8. Everything else is
\emph{inconclusive}, reported without post-hoc promotion.

The mini-grid executed \textbf{4 of those 8 cells}
($\{$Qwen2.5-1.5B, Llama-3.2-3B$\} \times \{$MMLU, GSM8K$\}$), with the 7B/8B
cells deferred behind a pre-committed, mechanical escalation rule. The mini-grid
registration stated the consequence of each branch in advance: if all eight
cells complete, the frozen rule is applied exactly as registered; if they do
not, the paper reports the four completed cells descriptively and H3 is
undecided under the registered rule---never supported or disconfirmed on four
cells---and no reduced-cell variant of the rule is constructed after results are
seen.

The escalation screen fired on 2026-07-23, the 7B/8B cells were built, and
\textbf{all eight cells completed}, so the second branch never applied and the
frozen rule was applied once over the full set. Both decisions are dated, signed
records
(\texttt{docs/MINIGRID\_ESCALATION\_DECISION\_2026-07-23.md},
\texttt{docs/H3\_EIGHT\_CELL\_DECISION\_2026-07-26.md}), and the screen's own
authorship discipline is worth stating: it decides which cells to build and
states no H3 outcome, so the confirmatory rule was never applied to a cell set
selected after its result was known. The screen's per-cell outcomes are in
\S\ref{sec:minigrid:escalation} and the verdict in
\S\ref{sec:minigrid:verdict}; this section states neither.

\subsection{The spot-check found a selection bias in our own pipeline}
\label{sec:prereg-spotcheck}
% SOURCE: docs/ATLAS_REV2_CORRECTION_2026-07-21.md; the spot-check report of
% 2026-07-21 (10 cells, 262/262 fields); ruling R7. Full narrative, the two
% defects, and the rev-1 -> rev-2 delta at app:prereg-spotcheck and
% app:prereg:rev2delta.

The protocol required an independent spot-check before any atlas number could be
quoted externally. It re-derived ten stratified cells from a fresh
reimplementation of the registered definitions rather than a rerun of our own
code, and all 262 compared fields reconciled exactly. The arithmetic was right;
the \emph{population} was not. Two defects---an omitted reverse-chronological
fallback clause of our own registration, and a parser that missed a newer nested
metrics schema---had silently dropped cells, the first non-randomly, removing
exactly those pairs whose quantized side had been re-evaluated later. Three
points follow, and none is that we were unlucky.

\textbf{An aggregate can be exactly right and still be built on the wrong
population.} Every cell we checked was computed correctly. Validating by
recomputing our own numbers---the natural, and useless, self-check---would have
confirmed all of them and shipped the selection bias intact. What caught it was
reconstructing the measurement from the protocol text rather than the code.

\textbf{Preregistration did the work it is supposed to do.} The frozen text
determined the direction of the repair: we executed a rule already binding and
under-implemented, rather than choosing one that flattered a result. The
correction was nevertheless made \emph{after} results had been inspected, and we
disclose that rather than presenting it as a pre-specified step.

\textbf{Both revisions are public.} We publish rev-1 and rev-2 and report the
delta (Appendix~\ref{app:prereg:rev2delta}) rather than replacing the record
with its corrected version; the repair enlarged the analysable population by
44\% and left the audit's headline verdicts unmoved. A field whose
near-lossless claims cannot be rechecked because per-item outputs are never
released---the finding of Section~\ref{sec:audit}---is a field whose corrections
are invisible. Ours is not, and that is the point of the artifact rather than an
apology for it.
% CORRECTION TO THE RECORD (2026-07-22). Commit 272136b ("Update the paper's
% banner-marked figures to atlas rev-2") states: "Every \revtwoBanner and
% \revtwoTODO marker is resolved; none remain outside main.tex's macro
% definitions." That claim was false of the tree it described -- the rev-1 vs
% rev-2 delta marker survived it. The commit's substantive work (the figure
% resync across atlas.tex, certification.tex, audit.tex, abstract.tex,
% introduction.tex and appendix_audit_table.tex) was done; only the
% completeness claim in its message was wrong, and a second miss in the same
% commit is recorded at appendix_audit_table.tex (944 -> 962).
% The marker itself was CLOSED on 2026-07-26 by writing the delta narrative at
% app:prereg:rev2delta from docs/ATLAS_REV2_CORRECTION_2026-07-21.md §8.
```

---

## FILE: `paper/sections/audit.tex`

```latex
% =====================================================================
% Section: Audit of published near-lossless claims  -- COMPLETE DRAFT
%
% PRIMARY SOURCES for every number in this section:
%   docs/AUDIT_VERDICTS_2026-07-20.md   (authoritative, computed 2026-07-20)
%   results/audit_verdicts.csv          (per-claim, machine-readable)
%   docs/audit_claim_table.csv          (frozen inputs, sha256 in the doc)
%   docs/AUDIT_REGISTRATION_2026-07-15.md (frozen protocol, §§3-5)
%
% SUPERSESSION NOTICE -- do not "fix" this section against the older doc.
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md line 54 states "only 1 of 17 claims
% has per-item outputs released". That line is SUPERSEDED by the 2026-07-20
% verdicts document, which records 0 yes / 3 partial / 14 no. This paper uses
% 0 of 17. The three "partial" sources are the ones the older line was
% gesturing at.
%
% DISCREPANCY -- CLOSED 2026-07-26. THE FROZEN TABLE GOVERNS.
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md line 48 describes the frozen table as
% "7 method papers, 8 official model cards/blog, 2 vendor docs" (7/8/2). The
% frozen table itself gives F1=7, F2=7, F3=3, re-verified 2026-07-26 by counting
% the `frame` column of docs/audit_claim_table.csv (7/7/3, 17 rows total).
% docs/audit_claim_table.csv is a FROZEN artifact and is authoritative over the
% older narrative doc, so the prose below (7/7/3) is correct as written and no
% paper-side change is required. The stale line survives in the older results
% doc; it is outside this paper's tree and is not edited here. No action is
% outstanding for the paper.
% =====================================================================

\section{An audit of published near-lossless claims}

% RESOLVED to rev-2 (2026-07-21). K and J did NOT move under the rev-2
% discordance imputation: K = 4 of 12, J = 5, uniform-2pp secondary 1 of 12,
% identical to rev-1. No new verdict computation was triggered.
% SOURCE: results/audit_verdicts_rev2.csv; delta in
% docs/ATLAS_REV2_CORRECTION_2026-07-21.md section 8.
\label{sec:audit}

\subsection{What was audited, and what was not}

The audit protocol was registered and frozen on 2026-07-15, before any per-claim
power computation was run, and the claim list itself was frozen separately before
any verdict was computed.\footnote{%
% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md (status line, §3.4);
% docs/AUDIT_VERDICTS_2026-07-20.md §Provenance (claim-table freeze commit
% 715a7ce, sha256 842b9756...5af7b15).
Registration frozen at commit \texttt{b74fd58}; claim table frozen at commit
\texttt{715a7ce} with its sha256 recorded in the verdicts document.}
Sources were enumerated exhaustively within three fixed frames: method papers
(F1), official quantized model cards (F2), and inference-stack vendor
blogs and documentation (F3). A source enters the pool if it asserts, in prose
or a table caption, that a compressed model's benchmark quality is
equivalent-or-negligibly-different from its uncompressed baseline, using a fixed
trigger vocabulary (``near-lossless'', ``negligible'', ``no (significant)
degradation'', ``matches'', ``preserves accuracy'', ``$X\%$ recovery'' with
$X \geq 98$, or an explicit $\leq 1$\,pp delta framed as parity). Every claim
meeting the criterion is audited; there is no discretionary sub-selection.
% SOURCE: docs/audit_claim_table.csv column `frame`: F1=7, F2=7, F3=3.
The frozen table contains 17 claims: 7 method papers, 7 official model cards or
official blogs, and 3 inference-stack vendor documents. Each claim's fields were
extracted twice by mutually blind extraction passes, with source content hashes
recorded, and discrepancies reconciled before the verdict stage
(\S\ref{sec:prereg}).

We state the limit of the exercise before its results.
% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md §4 closing paragraph.
\textbf{No audited claim is described as false, and none of our findings implies
that any audited model is in fact degraded.} The audited property is the
\emph{evidential sufficiency of the reported evaluation}: whether the evaluation
offered in support of an equivalence claim was large enough to have detected the
difference the claim pronounces negligible. A claim can be perfectly correct and
still be unsupported by the evaluation offered for it, and several of the claims
below are very probably correct. What the field lacks is not honesty but a
reporting standard; this section measures the gap that standard would close, and
Section~\ref{sec:certification} supplies the instrument.

\subsection{The reproducibility zero}
\label{sec:audit:v3}

The most actionable finding requires no statistics at all.

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"V3 -- reproducibility";
% results/audit_verdicts.csv column v3_per_item_outputs (0 "yes", 3 "partial",
% 14 "no"). Supersedes RESULTS_2026-07-15_ATLAS_AUDIT.md line 54.
\begin{quote}
\textbf{0 of the 17 audited sources release the per-item outputs that a third
party would need to rerun the paired comparison the claim asserts.}
The tally is 0 \emph{yes}, 3 \emph{partial}, 14 \emph{no}.
\end{quote}

The three partial cases---%
% SOURCE: results/audit_verdicts.csv rows R08, R15, R16 (v3_per_item_outputs =
% "partial", with the per-row `notes` column giving the suite mismatch).
R08, R15 and R16, all Red~Hat AI model cards---are the closest the record comes
to reproducibility, and they illustrate why the count is nonetheless zero: they
release per-item outputs for Arena-Hard, OpenLLM~v2 and HumanEval, but
\emph{not} for the OpenLLM~v1 tasks that the audited equivalence claim is
actually about. The released artifacts and the asserted claim do not intersect.
These three sources are ahead of the field in disclosure practice, and the
correction they need is small: publish the per-item outputs for the suite the
claim quotes.

This finding is more actionable than any power calculation because the two
failures have different repair costs. Underpowering is fixable by evaluating
more items, and Section~\ref{sec:certification} says how many. Irreproducibility
is not fixable downstream at all: with no per-item outputs, nobody outside the
releasing organisation can run the paired test at \emph{any} sample size, cannot
compute churn, and cannot check the arithmetic. Per-item outputs for a
benchmark of a few thousand items are a file of a few megabytes. The gap between
that cost and its consequence is the single clearest reporting-standards
recommendation this paper makes.

\subsection{Verdict rules}
\label{sec:audit:rules}

For each claim, at its reported (or registered-rule-imputed) sample size $n$,
the frozen protocol computes three quantities.
% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md §4; method restated in
% docs/AUDIT_VERDICTS_2026-07-20.md §Method.

\paragraph{V1 --- detection power.} The minimum detectable difference (MDD) at
80\% power and two-sided $\alpha = 0.05$, under the paired-flip model. The
per-item accuracy difference is $d_i \in \{-1, 0, +1\}$; under the null of no
true difference, $\mathrm{Var}(d) = p_d$, the discordance rate, so
$\mathrm{sd} = \sqrt{p_d}$. We report the MDD and the ratio of the MDD to the
margin the claim asserts is negligible.

\paragraph{V2 --- equivalence support.} The number of items required for TOST at
the applicable margin,
\begin{equation}
n_{\mathrm{req}} \;=\; \left\lceil \left(\frac{(z_{1-\alpha} + z_{1-\beta})\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil ,
\label{eq:tost-n}
\end{equation}
with $z_{1-\alpha}$ \emph{one-sided} ($1.6449$), because TOST rejects two
one-sided nulls at level $\alpha$ each. A claim is labelled
\emph{underpowered for its own assertion} iff its reported $n$ is below
$n_{\mathrm{req}}$ at the applicable margin. The choice of one-sided $z$ is not
cosmetic; see \S\ref{sec:prereg:choices}, interpretive choice~5.

\paragraph{V3 --- reproducibility.} Binary, read from the frozen
\texttt{per\_item\_outputs\_released} column and cross-checked against the
extraction reconciliation memo.

\paragraph{Discordance imputation.} $p_d$ is not reported by any source, so it
is imputed from the atlas (\S\ref{sec:atlas}) by matching the nearest
(method family, bit width, benchmark) cell, most-specific tier first, taking the
\emph{median} over the first non-empty tier because per-cell discordance is
right-skewed.
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Method, imputation-tier table.
One claim matched at tier~1 (family + bits + benchmark), 11 at tier~2
(family + bits), 2 at tier~3 (bits + benchmark), 1 at tier~4 (bits), and 2 fell
through to the global tier. A tier whose target field is \texttt{None} cannot
match, so a pruning claim with no bit width descends automatically rather than
being forced into a wrong cell. Both disclosed feasibility-probe pairs (99
atlas cells) are excluded from the imputation pool, per the atlas registration.

\paragraph{Robustness.} Every quantity is recomputed under the
independent-binomial bound $\mathrm{sd} = \sqrt{2p(1-p)}$ and swept over 1\,pp
and 3\,pp margins; a verdict that changes across the sweep is reported as
\emph{margin-sensitive}.

\subsection{Results}
\label{sec:audit:results}

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Headline; results/audit_verdicts.csv
% columns verdict, indeterminate, indeterminate_kind.
Of the 17 claims, 5 are \textbf{indeterminate}---their reporting does not
support a verdict---leaving 12 determinate claims. Of those 12,
\textbf{$K = 4$ are underpowered for their own assertion}.

\begin{table}[t]
\centering
\caption{Determinate claims underpowered for their own assertion, at the margin
the claim itself asserts is negligible. Shortfall is
$n_{\mathrm{req}} / n_{\mathrm{reported}}$.}
\label{tab:audit-underpowered}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Per-claim results", first table;
% results/audit_verdicts.csv columns claimed_margin_pp, n,
% v2_required_n_applicable, verdict.
\begin{tabular}{llrrrr}
\toprule
Claim & Source & Stated margin & Reported $n$ & Required $n$ & Shortfall \\
\midrule
R17 & Red~Hat Llama-3-8B W8A16   & 0.15\,pp & 28{,}659 & 369{,}856 & $12.9\times$ \\
R07 & SparseGPT                  & 0.23\,pp & 12{,}410 & 139{,}134 & $11.2\times$ \\
R06 & Wanda                      & 0.30\,pp & 18{,}904 &  81{,}780 & $ 4.3\times$ \\
R15 & Red~Hat Llama-3.1-8B W8A8  & 0.20\,pp & 42{,}701 &  86{,}556 & $ 2.0\times$ \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:audit-underpowered} is best read as a statement about resolution
rather than about error. R17 asserts parity within 0.15\,pp on an evaluation of
28{,}659 items; certifying parity at that margin, given the discordance rate
that comparable compressed models actually exhibit, would take roughly 370{,}000
items. Nothing in that sentence says the model is degraded. It says the
evaluation was not built to the resolution the sentence about it requires.

The same conclusion appears in the detection direction.

\begin{table}[t]
\centering
\caption{Detection resolution (V1): how much coarser each evaluation is than the
difference it pronounces negligible. The independent-binomial column is the same
quantity computed without the paired-design benefit.}
\label{tab:audit-mdd}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Per-claim results", second table;
% results/audit_verdicts.csv columns v1_mdd_pp_paired, claimed_margin_pp,
% v1_mdd_over_margin_paired, v1_mdd_over_margin_independent.
% R04 and R14 are italicised because they are INDETERMINATE: numbers computable,
% retained for transparency, carrying no verdict and excluded from K.
\begin{tabular}{lrrrr}
\toprule
Claim & MDD (paired) & Claimed margin & Ratio & Ratio (indep.\ binomial) \\
\midrule
R17 & 0.61\,pp & 0.15\,pp & $4.05\times$ & $7.25\times$ \\
R07 & 0.87\,pp & 0.23\,pp & $3.77\times$ & $7.07\times$ \\
R06 & 0.70\,pp & 0.30\,pp & $2.34\times$ & $4.52\times$ \\
R15 & 0.32\,pp & 0.20\,pp & $1.60\times$ & $4.20\times$ \\
\midrule
\textit{(R04)} & \textit{2.09\,pp} & \textit{0.30\,pp} & \textit{$6.97\times$} & \textit{$12.57\times$} \\
\textit{(R14)} & \textit{2.27\,pp} & \textit{0.70\,pp} & \textit{$3.25\times$} & \textit{---\ (no baseline)} \\
\bottomrule
\end{tabular}
\end{table}

Two features of Table~\ref{tab:audit-mdd} matter for how the audit should be
read. First, the independent-binomial column is uniformly \emph{worse}, by
roughly a factor of two: pairing is the generous modelling assumption, and these
evaluations are underpowered even under it. Second, R04 and R14 are italicised
because they carry no verdict; their numbers are computable and are retained in
the released CSV for transparency, but they are excluded from $K$
(\S\ref{sec:audit:indeterminate}).

\paragraph{Two robustness notes.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Headline (secondary reading) and
% §"Margin-sensitive (1 of 12 determinate)"; results/audit_verdicts.csv columns
% verdict_at_registered_2pp and margin_sensitive.
% CARE -- THE TWO "1 of 12" FIGURES BELOW ARE DIFFERENT FACTS. First: one
% determinate claim is underpowered under the uniform 2 pp yardstick. Second:
% one determinate claim's verdict is unstable across the 1 pp -> 3 pp sweep.
% They happen to concern the same claim (R01) and MUST NEVER be merged into a
% single sentence or read as one finding. This paragraph merges the two former
% paragraphs (2026-07-26) but deliberately keeps the two facts in separate
% sentences with the coincidence stated explicitly.
First, judging every claim against the uniform registered 2\,pp margin rather
than the margin it states for itself gives \textbf{1 of 12 underpowered}; both
readings are reported and both ship in the released CSV (\texttt{verdict},
\texttt{verdict\_at\_registered\_2pp}). The factor-of-four difference between
them is interpretive, not statistical, and the reasoning that selects the
primary reading is at \S\ref{sec:prereg:choices}: the frozen label is
``underpowered for its \emph{own} assertion'', and judging a 0.15\,pp parity
claim against a 2\,pp yardstick audits a claim nobody made. Second, and
separately, exactly \textbf{1 of the 12 determinate claims is margin-sensitive}:
R01, whose verdict flips between underpowered and adequately powered across the
1\,pp\,$\to$\,3\,pp sweep, making that verdict an artefact of margin choice
rather than a robust finding; it is reported as such rather than counted as
evidence in either direction. Margin sensitivity qualifies a headline verdict,
so it is counted over the claims that have one---R04 and R14 also flip across
the sweep and retain the \texttt{margin\_sensitive} column in the released CSV,
but neither carries a verdict to qualify. These are two distinct
properties---a verdict under an alternative yardstick, and instability of a
verdict across the sweep---that coincide on one claim.

\subsection{Indeterminate claims: a finding, not a gap}
\label{sec:audit:indeterminate}

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Indeterminate;
% results/audit_verdicts.csv columns indeterminate, indeterminate_kind,
% indeterminate_reason.
$J = 5$ of the 17 claims are indeterminate, in two kinds.

\textbf{Insufficient reporting (4).} A registered input is genuinely absent.
R02 (LLM.int8()) and R11 (Meta's quantized-Llama blog) state no sample size, no
baseline, and no numeric delta---their headline equivalence evidence exists only
as a chart image. R13 (vLLM FP8 documentation) states $n = 250$ but shows no
on-page baseline run at all. R14 (vLLM FP8 KV-cache blog) states a margin of
0.7\,pp and permits $n$ to be imputed, but reports no baseline; its comparison
lives in a figure.

\textbf{Metric-incompatible (1).} R04 (AWQ) reports enough, but about a quantity
the registered model cannot score; see below.

Every indeterminate claim retains whatever components its available inputs
support, listed in the CSV column \texttt{determinate\_components} and reported
as supplementary transparency only---never verdict-bearing. R13 retains V2 (the
paired standard deviation depends on discordance, not on baseline accuracy);
R14 retains V1 (paired) and V2; R04 retains V1 and V2 computed on a substituted
benchmark.

This category is itself a result. Two of the four insufficiently-reported claims
are among the most-cited results in the field, and their headline equivalence
evidence is a chart image with no extractable numbers. That a mechanical,
pre-registered audit cannot evaluate them is precisely the reporting-standards
problem this paper exists to address: the claim may well be true, but it has been
placed beyond the reach of checking.

\subsection{R04: an exclusion we argue against our own interest}
\label{sec:audit:r04}

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #3 and
% §Indeterminate bullet for R04; results/audit_verdicts.csv row R04 columns
% indeterminate_reason, notes, v2_required_n_paired_own_margin (50519 at
% n = 1319 -> 38.3x).
R04 is recorded because excluding it removed what would have been the largest
number in Table~\ref{tab:audit-underpowered}. The AWQ paper's qualifying
sentence---the one that meets the frozen §3 inclusion trigger---asserts
negligible loss on \textbf{COCO CIDEr}, a generation metric that assigns a
graded score to a caption and has no per-item correct/incorrect state; V1 and V2
are flip-model quantities defined on $d_i \in \{-1,0,+1\}$ and do not apply to
it, and there is no discordance rate to impute because there is no per-item
accuracy state to be discordant about. The first pass nonetheless scored R04 on
GSM8K, the source's own accuracy benchmark ($-0.30$\,pp at $n = 1{,}319$), and
reported it as the table's largest shortfall at $38.3\times$. On review this was
overruled---computing a TOST requirement on GSM8K audits a sentence the source
wrote about a different benchmark, in different and non-trigger language---taking
the headline from $K = 5$, $J = 4$ to $K = 4$, $J = 5$ and removing the audit's
biggest number. The GSM8K computation is retained in the released CSV as a
labelled transparency column so a reader can see exactly what was set aside and
why. \textbf{It is not claimed anywhere in this paper as an audit result.} An
audit's currency is unimpeachability, and it is not spent on its own largest
number.

\subsection{What this section does and does not establish}

Establishes, at the reported sample sizes and under the frozen protocol:
(i) no audited source releases per-item outputs for the tasks its equivalence
claim covers; (ii) four determinate claims assert margins finer than their
evaluations could resolve, by $2.0$--$12.9\times$; (iii) five claims cannot be
audited at all from what they report; (iv) both conclusions hold, and worsen,
under the independent-binomial robustness bound.

Does not establish: that any audited model is degraded; that any audited claim
is false; that the claims' authors reached a wrong conclusion. It also does not
establish anything about sources outside the three frozen frames, and it
operates at claim-level rather than claim\,$\times$\,benchmark granularity,
because that is the granularity of the frozen claim table
(\S\ref{sec:prereg:choices}, interpretive choice~4).
```

---

## FILE: `paper/sections/certification.tex`

```latex
% =====================================================================
% Section: Certification tables  -- COMPLETE DRAFT
%
% PRIMARY SOURCES for every number in this section:
%   docs/CERTIFICATION_TABLES_2026-07-20.md  (authoritative narrative)
%   results/certification_tables_rev2.csv    (machine-readable, 3 margins/family)
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §5 (registered metric set)
%
% DISCREPANCY -- CLOSED 2026-07-26 as a wording mismatch, not a data mismatch.
% docs/CERTIFICATION_TABLES_2026-07-20.md line 4 describes the artifact as
% "12 benchmark families x 3 margins". Re-verified against
% results/certification_tables_rev2.csv on 2026-07-26: it holds ELEVEN named
% families (arc_challenge, bbh, gpqa, gsm8k, hellaswag, ifeval, math, mmlu,
% mmlu_pro, musr, winogrande) plus an "ALL (pooled)" row = 12 table ROWS at each
% of 3 margins (33 rows total). So the doc's "12 families" is loose wording for
% 12 rows; there is no missing or extra family and no number is affected.
% The paper is already correct and stays as written: Table~\ref{tab:certification}
% reproduces 11 families + pooled, and the prose says "eleven families".
% Nothing is outstanding for the paper; the doc's line-4 wording is the only
% artefact and it lies outside this tree.
% =====================================================================

\section{Certification tables: how many items an equivalence claim needs}

% RESOLVED to rev-2 (2026-07-21) after the targeted second spot-check passed.
% SOURCE: results/certification_tables_rev2.csv, margin_pp = 2.0 rows.
\label{sec:certification}

\subsection{Detection is not certification}

The statistical question behind ``near-lossless'' is not the one usually
answered. A McNemar test---including the one-sided variant developed by the
closest existing work on LLM accuracy statistics
\citep{llmaccuracystats2026}---asks whether there is evidence that the
compressed model differs from its baseline. Failing to find such evidence is not
evidence of equivalence; with a small enough evaluation, nothing is detectable.
Our registration commits to this in advance: ``we will not interpret failure to
reject a difference as equivalence''.
% SOURCE: PREREGISTRATION.md §"Outcomes and Analysis".

Certification asks the other question: \emph{is the difference provably smaller
than a margin I declare in advance?} The standard instrument is TOST---two
one-sided tests at level $\alpha$ each, rejecting the composite null
$|\Delta| \geq m$ in favour of equivalence within $\pm m$. TOST converts an
equivalence claim into something with a sample-size requirement, and this
section computes that requirement empirically.

\subsection{Method}
\label{sec:cert:method}

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §Method.
For a discordance rate $p_d$ and margin $m$, at 95\% confidence and 80\% power,
\begin{align}
\mathrm{sd}_{\mathrm{paired}}      &= \sqrt{p_d}, &
\mathrm{sd}_{\mathrm{independent}} &= \sqrt{2p(1-p)}, \label{eq:sds}\\[2pt]
n_{\mathrm{req}} &= \left\lceil \left(\frac{(z_{1-\alpha} + z_{1-\beta})\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil
 = \left\lceil \left(\frac{(1.6449 + 0.8416)\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil. \label{eq:nreq}
\end{align}
The paired standard deviation follows from the flip model: the per-item accuracy
difference is $d_i \in \{-1,0,+1\}$, and under the null of no true difference
$\mathrm{Var}(d) = p_d$, the rate at which the two models disagree on
correctness. The independent form uses $p$, the family's median baseline
accuracy, because independent-binomial variance depends on accuracy rather than
on churn. $z_{1-\alpha}$ is \textbf{one-sided}, since TOST rejects two one-sided
nulls at level $\alpha$ each (\S\ref{sec:prereg:choices}, interpretive
choice~5).

The discordance rates are not modelled; they are read off the atlas
(\S\ref{sec:atlas}). For each benchmark family we take the 25th percentile,
median, and 75th percentile of the per-cell accuracy-state churn observed across
that family's atlas cells, giving optimistic, typical, and pessimistic
compression behaviour. Quartiles are \texttt{numpy}'s linear-interpolation
\texttt{np.quantile}.

\subsection{The table}
\label{sec:cert:table}

\begin{table}[t]
\centering
\small
\caption{Items required to certify equivalence within $\pm 2$\,pp at 95\%
confidence and 80\% power, by benchmark family, at the 25th/50th/75th
percentiles of the discordance rates the atlas observes for that family. The
naive column is the same requirement computed by treating the two runs as
independent samples. Eleven benchmark families plus the pooled row.}
\label{tab:certification}
% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §"The table at the registered
% 2 pp margin"; every cell cross-checked against results/certification_tables.csv
% rows with margin_pp = 2.0 (columns n_atlas_cells, discordance_p25/median/p75,
% required_n_p25/median/p75, required_n_independent_binomial,
% paired_advantage_at_median).
\begin{tabular}{lrccrr}
\toprule
Benchmark & Atlas cells & Discordance p25/med/p75 & Required $n$ p25/\textbf{med}/p75 & Naive & Advantage \\
\midrule
musr          &  24 & 0.015 / 0.034 / 0.044 & 232 / \textbf{519} / 681 & 7{,}617 & $14.7\times$ \\
gpqa          &  24 & 0.035 / 0.048 / 0.067 & 545 / \textbf{749} / 1{,}035 & 7{,}233 & $9.7\times$ \\
bbh           & 192 & 0.024 / 0.044 / 0.060 & 371 / \textbf{681} / 928 & 6{,}492 & $9.5\times$ \\
mmlu\_pro     &   5 & 0.048 / 0.053 / 0.059 & 739 / \textbf{827} / 913      & 7{,}695 & $9.3\times$ \\
hellaswag     &  23 & 0.031 / 0.045 / 0.099 & 477 / \textbf{695} / 1{,}538 & 4{,}905 & $7.1\times$ \\
arc\_challenge&  17 & 0.072 / 0.079 / 0.099 & 1{,}112 / \textbf{1{,}218} / 1{,}536 & 7{,}363 & $6.0\times$ \\
ifeval        &   8 & 0.048 / 0.052 / 0.072 & 736 / \textbf{800} / 1{,}108 & 4{,}211 & $5.3\times$ \\
mmlu          & 1311 & 0.093 / 0.140 / 0.259 & 1{,}432 / \textbf{2{,}164} / 4{,}005 & 7{,}727 & $3.6\times$ \\
winogrande    &  23 & 0.067 / 0.092 / 0.221 & 1{,}031 / \textbf{1{,}416} / 3{,}422 & 5{,}600 & $4.0\times$ \\
math          &  56 & 0.107 / 0.141 / 0.169 & 1{,}661 / \textbf{2{,}186} / 2{,}610 & 5{,}222 & $2.4\times$ \\
gsm8k         &  24 & 0.040 / 0.077 / 0.198 & 619 / \textbf{1{,}184} / 3{,}068 & 2{,}671 & $2.3\times$ \\
\midrule
\textbf{ALL (pooled)} & \textbf{1{,}707} & 0.064 / 0.120 / 0.225 & 994 / \textbf{1{,}855} / 3{,}478 & 7{,}722 & $\mathbf{4.2\times}$ \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{How to read a row.} Pick the benchmark family and the equivalence
margin you intend to certify. The three required-$n$ columns are the item counts
you need under optimistic, typical, and pessimistic compression behaviour for
that family. Then compare with the naive column, which is the count you would
compute if you ignored pairing.

% SOURCE: results/certification_tables_rev2.csv, mmlu at margin_pp 1.0/2.0/3.0
% (required_n_median = 8656 / 2164 / 962; required_n_independent_binomial at
% 2 pp = 7727). The rev-1 8,491-vs-8,492 discrepancy against the rev-1 narrative
% doc is moot: both are superseded by rev-2, and the CSV remains authoritative.
\paragraph{Worked example.} \emph{MMLU, 2\,pp margin, typical discordance
$\Rightarrow$ evaluate at least 2{,}164 items.} Ignoring pairing would have
demanded 7{,}727---$3.6\times$ the compute for the same conclusion. Tightening
the margin to 1\,pp raises the requirement to 8{,}656 items; relaxing it to
3\,pp lowers it to 962. The margin is the practitioner's declaration, and its
cost is quadratic; a claim of parity within 1\,pp is four times as expensive to
certify as parity within 2\,pp.

\subsection{Why the naive column belongs in the table}

The independent-binomial column is not a straw man. It is what you get by
treating the baseline and compressed evaluations as two unrelated samples and
comparing proportions, which is the default in most reporting. It is wrong in a
specific, quantifiable way: the two runs are \emph{the same items through two
nearly identical models}, so they agree on the large majority of items, and
their difference has far less variance than independence implies.

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §"Why the naive column is in
% the table"; results/certification_tables_rev2.csv column
% paired_advantage_at_median (GSM8K 2.25--2.26, MuSR 14.66--14.68, pooled 4.16).
% Pointer corrected 2026-07-26: the values here are rev-2, but this comment
% named the rev-1 CSV, whose GSM8K entry is 1.7.
The advantage column is exactly that gap. It ranges from $\mathbf{2.3\times}$
(GSM8K) to $\mathbf{14.7\times}$ (MuSR) and sits at $\mathbf{4.2\times}$ pooled
over 1{,}707 cells: a practitioner using the paired design reaches the same
equivalence conclusion on roughly a quarter of the evaluation budget. The
variation across families is informative in itself---low-churn families (MuSR,
BBH, GPQA) reward pairing most, while high-churn generative families (MATH,
MMLU) both need more items \emph{and} gain less from pairing.

\subsection{The requirement is driven by churn, not by difficulty}
\label{sec:cert:churn-not-difficulty}

The ordering in Table~\ref{tab:certification} is not the intuitive one, and this
is the section's main conceptual point.

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md, closing paragraph of
% §"Why the naive column is in the table"; results/certification_tables.csv,
% mmlu vs gpqa at margin_pp = 2.0. Baseline accuracies in the next paragraph are
% results/certification_tables.csv column median_baseline_accuracy: gpqa 0.3734,
% mmlu 0.39. Discordances are column discordance_median: mmlu 0.13733,
% gpqa 0.048397.
MMLU needs about \textbf{2{,}164} items at a 2\,pp margin. GPQA needs
\textbf{749}. GPQA is by any ordinary account the harder benchmark---its median
baseline accuracy in the atlas is 0.373 against MMLU's 0.390, on a task designed
to resist exactly the models that saturate MMLU. Difficulty is not what sets the
requirement. What sets it is how much the compressed model's per-item
correctness \emph{churns} relative to the baseline: MMLU's typical discordance
is 0.137 against GPQA's 0.048, so MMLU's paired variance is nearly three times
larger and its required sample size scales with it.

The practical consequence is that a practitioner cannot reason about evaluation
size from intuitions about task hardness, headroom, or score level. Two
benchmarks with similar accuracies and similar apparent difficulty can differ by
a factor of three in the evidence they require, and the only way to know which
is which is to measure churn. That is what the atlas is for, and it is why the
certification tables are empirical rather than analytic.

\subsection{Scope and caveats}
\label{sec:cert:caveats}

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §"Scope and caveats", all five
% bullets, plus results/certification_tables_rev2.csv column n_atlas_cells.
% PROSE-IFIED 2026-07-26 from a five-item list. All five caveats survive as
% content, in order: (1) <4-cell families omitted, (2) the two thin rows,
% (3) family aggregation mixes two variation sources, (4) the 99 probe cells,
% (5) certification n != detection n.
These caveats travel with the table, and any reuse of it should carry them.
Families with fewer than four analysable cells are omitted, because a quartile
over three points is not an empirical distribution; this drops nothing from the
registered set, and all surviving families appear in
Table~\ref{tab:certification}. Of those that survive, two rest on thin evidence
and are indicative only---\texttt{mmlu\_pro} (5 cells) and \texttt{ifeval}
(8)---while rev-2 moved \texttt{arc\_challenge} to 17 cells, \texttt{gsm8k} to
24, \texttt{hellaswag} to 23 and \texttt{winogrande} to 23, taking those out of
the thin category, and \texttt{mmlu} (1{,}311), \texttt{bbh} (192) and
\texttt{math} (56) are well supported; a reader should treat the thin rows as a
starting hypothesis to be replaced by their own measured churn, not as a
reference constant. Family aggregation mixes two sources of variation, since the
atlas collapses MMLU's 57 per-subject cells and BBH/MATH/MuSR/GPQA's per-subtask
cells into families, so a family's spread combines subject-level with
model-level variation---which widens the p25--p75 band relative to what a single
practitioner evaluating a single model would see, and therefore makes the
quartile columns \emph{conservative} rather than optimistic. Both disclosed
feasibility-probe pairs (99 cells) are excluded per the atlas registration §6, as
tiny hand-built sanity pairs---$n$ as low as 10, discordance up to 0.9---that
would distort every quartile. Finally, these are certification sample sizes, not
detection sample sizes: they certify equivalence within $\pm m$, the $n$ required
to \emph{detect} a difference at the same margin is larger, and reporting one as
the other is the error this section exists to prevent.

\subsection{What this section does and does not support}

Supports: an empirically grounded, family-specific answer to ``how many items do
I need to certify parity within $\pm m$?''; a quantified $2.3$--$14.7\times$
($4.2\times$ pooled) reduction in required evaluation from using the paired
design correctly; and the demonstration that the requirement tracks churn rather
than difficulty.

Does not support: extrapolation to benchmark families absent from the atlas;
extrapolation to compression methods absent from the atlas population
(\S\ref{sec:atlas:caveats}); any claim that a model meeting these counts is
equivalent---meeting the count makes the test \emph{informative}, and the test
still has to be run and to pass.
```

---

## FILE: `paper/sections/atlas.tex`

```latex
% =====================================================================
% Section: The public-record flip atlas  -- COMPLETE DRAFT
%
% PRIMARY SOURCES for every number in this section:
%   docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1 (cell counts, S1/S2 contrast)
%   results/atlas_cells_summary_rev2.csv      (per-cell, machine-readable)
%   results/atlas_exclusions_rev2.csv         (exclusion reasons)
%   docs/ATLAS_REV2_CORRECTION_2026-07-21.md  (rev-1 -> rev-2 delta, section 8)
%   results/identical_score_churn_rev2.csv    (identical-score, machine-readable)
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md (frozen protocol)
%
% ALL FIGURES ARE ATLAS REV-2 (2026-07-21). Rev-1 is superseded; both revisions
% remain in the record and the delta is reported in the preregistration section.
%
% TWO POPULATIONS -- DO NOT MIX. Every number below states which one it uses.
%   1,807 = analysed cells (S1 1,459 + S2 348), i.e. enumerated minus
%           excluded/skipped. Used ONLY for pipeline-coverage accounting.
%   1,707 = analysis population = 1,807 minus the 99 disclosed-probe cells
%           (S1 1,398 + S2 309). Used for EVERY statistic, and it is the same
%           population as the certification tables and the identical-score note.
%
% VERIFICATION: rev-1's per-cell arithmetic was independently reconciled on 10
% stratified cells (262/262 fields); rev-2's corrected population on a further
% 14 cells (126/126 fields), across recovered-fallback, newly-admitted and
% unchanged-control strata. docs/ATLAS_REV2_SPOTCHECK2_2026-07-21.md.
% =====================================================================

\section{An atlas of the public record of compression evaluation}

% RESOLVED to rev-2 (2026-07-21) after the targeted second spot-check passed
% 14/14 cells, 126/126 fields. Every figure below is rev-2.
% SOURCE: results/atlas_cells_summary_rev2.csv, results/identical_score_churn_rev2.csv;
% delta table in docs/ATLAS_REV2_CORRECTION_2026-07-21.md section 8.
\label{sec:atlas}

\subsection{Construction}
\label{sec:atlas:construction}

The atlas mines paired per-item records from public evaluation dumps at zero GPU
cost. Its protocol was registered and frozen on 2026-07-15, before any flip
statistic was computed beyond two feasibility probes that the registration
discloses by name; the pair list itself was frozen as a machine-readable
manifest, with dataset URLs, run timestamps, and task lists, before any flip
statistic was computed.
% SOURCE: docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §§1, 3.4; manifest freeze
% commit f06348f per docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3.
The registration exists to prevent source- or pair-selection after seeing
results, and it labels these analyses descriptive: they estimate flip and churn
magnitudes in the wild and feed the certification tables, they test no registered
hypothesis, and they cannot substitute for any H3 cell.

Two sources are in scope.
\textbf{S1} is the Open LLM Leaderboard v1 archive---community quantizations
(GPTQ, AWQ, GGUF, 8-bit and 4-bit bitsandbytes) of 2023-era base models, paired
with their base model's details dataset whenever one exists.
\textbf{S2} is the Neural Magic / Red~Hat per-item dumps for quantized
Llama-3.1, covering W4A16, W8A8-INT8 and W8A8-FP8 at 8B, 70B and 405B.
Item pairing is mechanical: items join on the source's own item key, duplicated
keys are dropped entirely on both sides, and an item enters the paired analysis
only if its full-prompt hash is identical across the pair. A pair-task cell is
excluded if fewer than 99\% of joinable items pass that identity check. Differing
harness commits do not exclude a cell---prompt-hash identity is the operative
control---but are recorded per cell and disclosed.

\subsection{Coverage, and what the exclusions reveal}
\label{sec:atlas:coverage}

% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1, first bullet;
% results/atlas_exclusions.csv.
% POPULATION: this subsection (and only this subsection) uses the 1,807 figure.
% SOURCE: results/atlas_cells_summary_rev2.csv, reason column.
The enumeration yields \textbf{2{,}055} pair-task cells, of which
\textbf{1{,}807 are analysed} (S1 = 1{,}459, S2 = 348) and \textbf{248} are
excluded or skipped. The exclusions break down as \textbf{179} cells (72.2\%)
for which no results file exists for that task in any recorded run,
\textbf{36} (14.5\%) whose join intersection is empty, and \textbf{33}
(13.3\%) whose task carries no binary correctness metric in the data at all
(genuinely float-scored tasks, which the flip model does not describe).

Empty join intersections are a reporting-standards observation in their own
right. An empty intersection means the two sides of the pair were evaluated on
\emph{different item sets}: the leaderboard's baseline run and its quantized run
do not share the items whose scores are being compared. The resulting difference
in reported accuracy is not a paired quantity at all, and no per-item analysis
of it is possible. This is invisible to anyone reading only the aggregate
leaderboard numbers.

We state this carefully because an earlier revision of this work overstated it.
Rev-1 of the atlas reported 643 exclusions as float-scored and 132 as empty
joins, and attributed both to upstream reporting practice. An independent
spot-check established that most of those cells were in fact readable and that
our own parser could not see them; the rev-2 figures above are what survives
once that defect is fixed. The episode is documented in
\S\ref{sec:prereg-spotcheck}, and the retraction is recorded rather than
quietly absorbed.

\subsection{The analysis population}
\label{sec:atlas:population}

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §Provenance ("analysable cells
% 1,155 (1,254 non-excluded - 99 probe)"); docs/IDENTICAL_SCORE_CHURN_2026-07-21.md
% §Population; docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §§1, 6.
Every statistic in the remainder of this section, in the certification tables of
\S\ref{sec:certification}, and in the discordance imputation of
\S\ref{sec:audit:rules} uses a single population: the \textbf{1{,}707} cells that
are neither excluded nor part of a disclosed feasibility probe
(S1 = 1{,}398, S2 = 309). The 99 probe cells span the two pairs whose results were
known before the registration was written; the registration requires them to
appear in the atlas but not in any headline aggregate, and they are tiny
hand-built sanity pairs ($n$ as low as 10, discordance up to 0.9) that would
distort any quartile. The 1{,}807 figure of \S\ref{sec:atlas:coverage} is
pipeline accounting and is never used as an analysis denominator.

\subsection{Net delta understates behavioural change by a factor of 5.3}
\label{sec:atlas:netgross}

% SOURCE: Table~\ref{tab:atlas-strata} (results/atlas_cells_summary_rev2.csv,
% the 1,707-cell analysis population), as the ratio of the two medians:
%   S1 0.138 / 0.026 = 5.3077 ; S2 0.048 / 0.009 = 5.3333.
% REV-1 SURVIVOR, CORRECTED 2026-07-27. This read "roughly five to six times"
% and cited docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1's "Reading" bullet. That
% bullet sits under the REV-1 strata table (S1 = 846 cells), which the same
% document states is superseded by rev-2; the "six" end was rev-1's S1 ratio of
% 0.133/0.023 = 5.78. At rev-2 both strata land at 5.3. This is the FOURTH
% rev-1 figure to survive into drafted prose, after the 1.7x GSM8K paired
% advantage, the 643 float-scored cells, and the "four thin families" -- all the
% same cause, prose written against rev-1 tables that rev-2 replaced.
Across the atlas, per-item accuracy-state churn runs \textbf{5.3 times the net
accuracy delta}, and that ratio holds at every scale represented, from 3B to
405B parameters. The net delta a model card reports is the residue left after
harmful and beneficial flips cancel; the churn is the quantity that describes how
much of the model's behaviour actually changed. They are different quantities and
both should be reported. The consequence for inference is direct: churn is the
variance term in Equations~\eqref{eq:sds}--\eqref{eq:nreq}, so a compressed model
whose net delta looks reassuringly small can still be sitting on the noisiest
possible evidence base for the claim that it is unchanged.

% SOURCE: Table~\ref{tab:atlas-strata}. Median churn 0.138 -> 0.048 is a factor
% of 2.875; median |net delta| 0.026 -> 0.009 is a factor of 2.889; the two move
% together, which is why the ratio is preserved to two significant figures.
\paragraph{The ratio is preserved across a generational change in method.}
The two strata differ by nearly a factor of three in how much behaviour they
disturb---median churn falls from $0.138$ in S1 to $0.048$ in S2---and by almost
exactly the same factor in the net delta they report, $0.026$ to $0.009$. The
understatement ratio therefore barely moves: \textbf{5.31 in S1 and 5.33 in S2}.
Two generations of compression method, one of them three times gentler than the
other, hide the disturbance they do cause by the same multiple. This is the
sharpest available form of the argument the rest of this section makes: better
methods have made the difference smaller \emph{without making the evidence for
equivalence any more sufficient}, because the quantity that determines how much
evidence is required scales down in lockstep with the quantity being claimed
small.

\subsection{The gray zone, and how it differs between the two strata}
\label{sec:atlas:grayzone}

\begin{table}[t]
\centering
\caption{The two atlas strata, on the 1{,}707-cell analysis population.
Percentages are within-stratum shares of cells.}
\label{tab:atlas-strata}
% SOURCE: results/atlas_cells_summary_rev2.csv, grouped by source.
% Population: 1,707 (S1 1,398 + S2 309) -- NOT the 1,807 figure.
\begin{tabular}{lrr}
\toprule
 & S1 (v1 archive; TheBloke-era GPTQ etc.) & S2 (Neural Magic W4A16/INT8/FP8, 8B--405B) \\
\midrule
Cells                                & 1{,}398        & 309 \\
Median accuracy-state churn          & 0.138          & 0.048 \\
Median $|$net accuracy delta$|$      & 0.026          & 0.009 \\
TOST-equivalent at 2\,pp             & 68 (4.9\%)     & 53 (17.2\%) \\
Exact McNemar $p < 0.05$             & 371 (26.5\%)   & 19 (6.1\%) \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:atlas-strata} contains the empirical core of the paper's
motivation. In S1, 4.9\% of cells can be certified equivalent at the registered
2\,pp margin and 26.5\% show a detectable difference, which leaves
\textbf{967 cells (69.2\%)} of the public record in a \textbf{gray zone}:
neither certifiable as equivalent at the margin the field implicitly uses, nor
detectably degraded, at the sample sizes actually evaluated. In S2 the shares
move---17.2\% certifiable, 6.1\% detectably different---and
\textbf{240 cells (77.7\%)} remain in the same gray zone.%
% ARITHMETIC NOTE -- RESOLVED 2026-07-26 by per-cell cross-tabulation of the
% tost_equivalent and mcnemar_p flags in results/atlas_cells_summary_rev2.csv,
% over analysable cells (excluded_or_skipped false, contains_disclosed_probe_cell
% false; S1 n=1,398, S2 n=309).
%   S1: TOST 68, McNemar 371, BOTH 8, neither 967 = 69.17%
%   S2: TOST 53, McNemar  19, BOTH 3, neither 240 = 77.67%
% The categories are indeed not disjoint, as this note anticipated -- 8 S1 and
% 3 S2 cells are simultaneously TOST-equivalent at 2 pp and McNemar-significant.
% NOTE THE DIRECTION OF THE CORRECTION: the prose previously said "at least
% three-quarters" for BOTH strata. That was an OVERSTATEMENT for S1, whose exact
% gray zone is 69.2%, below three-quarters. S2 at 77.7% was understated. The
% exact figures replace the bound in both places.


The S1$\to$S2 contrast is a genuine improvement in compression method and
evaluation practice, and should be read as one. Median churn falls from 0.138 to
0.048 and median absolute net delta from 0.026 to 0.009; a modern vendor
quantization of an 8B--405B instruction-tuned model perturbs per-item behaviour
roughly a third as much as a 2023 community quantization of a 7B base model, and
its evaluations are correspondingly more often certifiable. What does \emph{not}
improve is the evidential situation: the modal cell in both strata is one where
the evaluation cannot answer the question the release note answers. Better
methods have made the difference smaller without making the evidence for
``no difference'' sufficient, because certifying a smaller margin requires
\emph{more} items, not fewer (\S\ref{sec:cert:table}).

\subsection{Identical scores, different answers}
\label{sec:atlas:identical}

% SOURCE: docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §Results;
% results/identical_score_churn_rev2.csv (statistic block, rows 2-9):
% analysable_cells 1707, zero_delta_cells 145, zero_delta_share 0.084944,
% churn_median 0.072000, churn_mean 0.088725, churn_max 0.343434,
% zero_delta_nonzero_churn_cells 128, churn_median_nonzero_only 0.092215.
% Population: the same 1,707 cells. Zero-delta is defined as
% abs(net_accuracy_delta) < 1e-12, i.e. exact equality with no rounding
% tolerance; a rounding-based definition would admit more cells and is not used.
% REV-2 CORRECTION 2026-07-26. This comment previously cited the REV-1 file
% results/identical_score_churn.csv and the 1,155-cell population while the
% prose beneath it had already been updated to rev-2 -- the provenance comment
% contradicted the text it governed. Two rev-1 restatements survived here and
% were corrected in the same pass: the nonzero-churn subset median (0.0919 is
% rev-1's churn_median_nonzero_only 0.091868; rev-2 is 0.092215 -> 0.0922), and
% "more than 6% of individual items", which restated rev-1's churn_median
% 0.062176 where rev-2 gives 0.072000 -> "more than 7%".
% "ROUGHLY ONE IN TEN" RECONSIDERED AND TIGHTENED, not merely inherited: it was
% near-exact for rev-1's 9.78% share and is a stretch for rev-2's 8.49%
% (= 1 in 11.8), rounding away from the true value in the direction that
% overstates the finding. Replaced with "about one in twelve" here and in
% \S"What this section does and does not support". Do not restore "one in ten".
The clearest single demonstration that aggregate accuracy is not a summary of
behaviour is the subset of cells where the aggregate does not move at all.

Of the 1{,}707 analysable cells, \textbf{145 (8.49\%) post an exactly identical
accuracy} to their baseline---not similar, identical, to machine precision.
Among those 145 cells, the median accuracy-state churn is \textbf{0.0720}, the
mean is 0.0887, and the maximum is 0.3434; \textbf{128 of the 145} have nonzero
churn, with a median of 0.0922 among that subset. About one in twelve compressed
model evaluations in the public record reports a score identical to its
baseline, and half of those still disagree with the baseline on more than 7\% of
individual items.

\begin{table}[t]
\centering
\caption{The most extreme zero-delta cell in the atlas: identical accuracy,
symmetric flips, $p = 1.0$.}
\label{tab:identical-extreme}
% SOURCE: results/identical_score_churn_rev2.csv, rank 1 row; reproduced in
% docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §"Most extreme zero-delta cell".
% The rank-1 row is byte-identical between rev-1 and rev-2 (pair_index 35,
% high_school_geography_5, churn 0.343434); the citation was repointed to rev-2
% on 2026-07-26 for consistency, not because the values moved.
\begin{tabular}{ll}
\toprule
Field & Value \\
\midrule
pair\_index / source & 35 / S1 \\
Task                 & \texttt{harness\_hendrycksTest\_high\_school\_geography\_5} (MMLU) \\
Base model           & \texttt{project-baize/baize-v2-7b} \\
Quantized model      & \texttt{TheBloke/Project-Baize-v2-7B-GPTQ} (GPTQ) \\
$n$                  & 198 \\
Baseline accuracy    & 0.429293 \\
Compressed accuracy  & 0.429293 \quad (net delta $= 0.000000$) \\
Accuracy-state churn & \textbf{0.343434} \\
Harmful / beneficial flips & 0.171717 / 0.171717 \\
Exact McNemar $p$    & 1.0 \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:identical-extreme} makes the mechanism concrete. Exactly 17.17\%
of items broke and exactly 17.17\% healed. Because the two rates are equal, the
net delta is exactly zero and the exact McNemar test returns $p = 1.0$---and it
is \emph{right} to: there is no evidence of a directional difference between the
two models. Meanwhile a third of the answers changed. A model card reporting
this cell would truthfully write ``no change in accuracy''; a user who had
memorised the baseline's outputs would find one item in three behaving
differently.

% COMPRESSED 2026-07-26. All four caveats retained: small n, symmetric flips
% easier at small n, S1 provenance, and illustration-not-magnitude.
\textbf{Caveats, in the same breath as the example.} At $n = 198$ symmetric flip
counts are easier to hit by chance, and this is an S1 cell---a 2023-era
community GPTQ of a 7B base model, the noisier stratum. It illustrates the
mechanism, not a typical magnitude: the finding worth carrying away is the 145
cells and their 7.20\% median churn, not this one cell's 34\%.

\subsection{Population caveats}
\label{sec:atlas:caveats}

% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1, final bullet ("Population
% caveats (registered)"), reproduced here in substance;
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.
% COMPRESSED 2026-07-26. The census-vs-record distinction and the S1 license
% limitation are both retained verbatim in substance, as instructed.
These caveats are registered, and they are load-bearing. S1 is community
quantizations of 2023-era models conditioned on leaderboard coverage---a pair
exists only if someone chose to submit both the base model and its quantization
to the Open LLM Leaderboard, and that choice was not random with respect to
anything---while S2 is one vendor's releases, evaluated by that vendor.
\textbf{This is the public record of compression evaluation, not a census of
quantization.} It is the right population for what this paper asks (what the
circulating evidence looks like, and how much would suffice) and the wrong one
for how quantization behaves on average, which would need a designed sample
rather than the record left by the field's own reporting choices; the controlled
experiment of \S\ref{sec:minigrid} exists precisely because the atlas cannot
answer causal questions. Two further limits: \textbf{S1's archive carries no
declared license}, recorded as a limitation in the datasheet
(\S\ref{sec:artifacts}), and per-cell statistics inherit the item counts of
whoever ran the original evaluation, which is why many cells are small---an
inheritance that is itself part of the finding.

\subsection{What this section does and does not support}

Supports: that per-item churn under compression is five to six times the net
delta across the public record at every scale from 3B to 405B; that the majority
of publicly recorded compression evaluations fall in a gray zone where neither
equivalence nor degradation is established at their own sample sizes; that
about one cell in twelve posts an identical score while still disagreeing on
items; and that S2's methods are measurably gentler than S1's while the
evidential gap persists.

Does not support: any statement about quantization methods in general, about
models or methods absent from the two sources, or about causal attribution of
churn to any design choice. Nothing here is evidence for or against H3.
```

---

## FILE: `paper/sections/minigrid.tex`

```latex
% =====================================================================
% Section: Controlled seed-paired experiment (H3).
%
% FILLED 2026-07-27. All eight registered confirmatory cells now exist, the
% registered rule has been applied once, and the record is SIGNED:
%   docs/H3_EIGHT_CELL_DECISION_2026-07-26.md  (SIGNED 2026-07-26, 05c86f2)
%   docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md  (supporting, ddb6158)
% Every number in this section is READ from those two documents. Nothing here
% is recomputed, and the only arithmetic performed on them is the churn-ratio
% division in Result 1, which is stated as such.
%
% HARD RULES FOR THIS FILE, unchanged in substance:
%  - The verdict is what the frozen eight-cell rule returned, full stop.
%    Describing where the evidence concentrates is legitimate. Reframing it,
%    discounting it, or constructing any reduced-cell variant is not, and does
%    not become legitimate later.
%  - Nothing in the supporting analyses modifies the verdict. The text says so.
%  - The registration forbids collapsing seed-level SD into item-level SE; they
%    are reported as separate variance components and must stay separate.
%  - The resolution analysis is POST-HOC and is labelled as such at every
%    appearance, with its provenance carried from the results document.
% =====================================================================

\section{Does the calibration seed reorder compression methods?}
\label{sec:minigrid}

\subsection{Design}

% SOURCE: PREREGISTRATION.md §"Experimental Grid" and §"H3 Decision Rule";
% docs/MINIGRID_REGISTRATION_2026-07-15.md §§1-2.
The registered confirmatory design compares 4-bit GPTQ against 4-bit AWQ at
five calibration seeds $\{0,1,2,3,4\}$ over eight model-by-benchmark cells:
$\{$Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Llama-3.2-3B-Instruct,
Llama-3.1-8B-Instruct$\}\times\{$MMLU, GSM8K$\}$, with MMLU as the registered
likelihood-based benchmark and GSM8K as the registered generative one.

The pairing is the design's load-bearing element. For seed $s$, the calibration
set is 128 samples of exactly 2{,}048 tokens drawn from C4 by a fixed,
seed-determined procedure (shuffle the full train-split document index array with
\texttt{numpy.random.default\_rng(s)}, visit documents in that order, skip
documents shorter than 2{,}048 tokens, retain the first 2{,}048 tokens of each
eligible document until 128 are collected), and \textbf{GPTQ seed $s$ and AWQ
seed $s$ receive the identical ordered calibration samples}. A ranking
difference at seed $s$ is therefore attributable to method-by-calibration
interaction rather than to the two methods having seen different data. Selected
document indices and token hashes are persisted. The chat template is on for
every method including the FP16 baselines; GSM8K uses one inline few-shot
example and test indices 0--999; MMLU uses the full test split.

\subsection{Registered quantities}

% SOURCE: PREREGISTRATION.md §"H3 Decision Rule" and §"Hierarchical aggregation
% across calibration seeds".
Per cell, with $d_s = \mathrm{acc}_{\mathrm{GPTQ},s} - \mathrm{acc}_{\mathrm{AWQ},s}$:
a \emph{winner flip} occurs when two registered seeds give $d_s$ and $d_t$ of
opposite sign with both nonzero (exact ties are counted as neither flip nor
non-flip, and reported separately, so a tie can neither create nor erase a flip);
$\mathrm{gap} = |\mathrm{mean}_s(\mathrm{acc}_{\mathrm{GPTQ},s}) -
\mathrm{mean}_s(\mathrm{acc}_{\mathrm{AWQ},s})|$;
$\mathrm{range}_m = \max_s(\mathrm{acc}_{m,s}) - \min_s(\mathrm{acc}_{m,s})$;
and the range/gap criterion holds when
$\max(\mathrm{range}_{\mathrm{GPTQ}}, \mathrm{range}_{\mathrm{AWQ}}) \geq
\mathrm{gap}$. Seed-level SD and item-level SE are reported as separate variance
components rather than collapsed, and the H3-relevant rank-instability estimate
comes from the two-level paired bootstrap that resamples seed labels and, within
each selected seed, items---with GPTQ and AWQ retaining the same sampled seed
labels and item indices.

\subsection{How the eight cells came to exist}
\label{sec:minigrid:scope}

% SOURCE: docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 3, 4;
% docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md (SIGNED);
% docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED).
The eight cells were built in two stages, and the second stage was authorized by
the first under a rule frozen before either ran. The mini-grid executed
\textbf{4 of the 8} cells, $\{$Qwen2.5-1.5B-Instruct,
Llama-3.2-3B-Instruct$\}\times\{$MMLU, GSM8K$\}$; the 7B/8B cells sat behind a
mechanical, pre-committed escalation screen described in
\S\ref{sec:minigrid:escalation}. That screen fired, the deferred cells were
built and evaluated, and the frozen Supported/Disconfirmed/Inconclusive rule was
then applied once over all eight.

Two properties of that sequence matter for how the verdict should be read. The
escalation screen decides only \emph{which cells to build} and states no H3
outcome, so the confirmatory rule was never applied to a cell set chosen after
its own result was known. And the confirmatory rule is defined over all eight
cells and was applied only when all eight existed, exactly as registered---no
reduced-cell variant was constructed at any point, before or after results were
seen.

\input{sections/minigrid_escalation}

\subsection{The eight-cell verdict}
\label{sec:minigrid:verdict}

% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED 2026-07-26 by Amogh
% Singh, commit 05c86f2), "Mechanical application of the rule" and "H3 VERDICT".
% Counts: winner flip 5/8 (threshold >=3), range/gap 7/8 (threshold >=4),
% max_range < 0.5*gap in 1/8 (disconfirm threshold >=6). Ties: 0 of 8 cells,
% 0 of 40 triples.
Applied once, mechanically, to all eight cells:
\textbf{H3 is supported.} The winner reverses across seeds in \textbf{5 of the 8}
cells against a threshold of 3, and the range/gap criterion holds in
\textbf{7 of the 8} against a threshold of 4. The supported limb of the frozen
rule is a disjunction, and \emph{both disjuncts are satisfied independently}:
either one alone would have returned the same verdict.

The disconfirming limb is a conjunction, and both of its conjuncts fail. It
requires winner flips in at most 1 of 8---there are 5---and
$\max\mathrm{range} < 0.5\,\mathrm{gap}$ in at least 6 of 8, which holds in 1.
The two limbs cannot both hold and do not, so the frozen text classifies the
outcome with no interpretation required.

No exact accuracy tie occurs anywhere in the confirmatory set: \textbf{0 of 8}
cells contain one, over \textbf{0 of 40} (model, task, seed) triples. The
registered tie convention---a tie is neither a flip nor a non-flip, and can
neither create nor erase a flip between two non-tied seeds---therefore has no
effect on any cell's classification, and the denominator for both criteria
remains all eight cells.

What the verdict says is bounded by what was registered. Over the eight cells,
the choice between GPTQ and AWQ at 4 bits is not stable against
calibration-seed randomness alone. It licenses no statement about 3-bit
behaviour, ARC-Challenge, HellaSwag, calibration-\emph{dataset} effects, or any
cell outside the registered set; the FP16 baseline gate governs the baseline
only and says nothing about quantized accuracy.

\subsection{Per-cell registered quantities}
\label{sec:minigrid:percell}

% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md, "Per-cell registered
% quantities" (all eight cells) and "Mechanical application of the rule".
% Values are read from that record at the six decimals it publishes.
% The four mini-grid rows also reproduce the signed 2026-07-23 escalation record
% exactly (KNOWN_ANSWER: PASS, 4/4 cells) -- see sec:minigrid:escalation.
Table~\ref{tab:h3-eightcell} gives the two rule inputs per cell, and
Table~\ref{tab:h3-ds} gives the per-seed differences $d_s$ behind the
winner-flip column, so every flip determination in the table above is checkable
by inspection of sign.

\begin{table}[t]
\centering
\small
\caption{The eight registered confirmatory cells. $\mathrm{gap}$ is the absolute
difference of the two five-seed mean accuracies; $\mathrm{range}_m$ is the
seed-wise spread of method $m$; the range/gap criterion holds when
$\max(\mathrm{range}_{\mathrm{GPTQ}},\mathrm{range}_{\mathrm{AWQ}}) \geq
\mathrm{gap}$. Values reproduce the signed decision record.}
\label{tab:h3-eightcell}
\begin{tabular}{llrrrll}
\toprule
Model & Task & $\mathrm{gap}$ & $\mathrm{range}_{\mathrm{GPTQ}}$ & $\mathrm{range}_{\mathrm{AWQ}}$ & Flip & Range/gap \\
\midrule
Qwen2.5-1.5B & MMLU  & 0.012292 & 0.040521 & 0.018445 & \textbf{TRUE}  & \textbf{TRUE} \\
Qwen2.5-1.5B & GSM8K & 0.096800 & 0.014000 & 0.033000 & FALSE          & FALSE \\
Llama-3.2-3B & MMLU  & 0.030922 & 0.063809 & 0.029341 & FALSE          & \textbf{TRUE} \\
Llama-3.2-3B & GSM8K & 0.017800 & 0.011000 & 0.034000 & \textbf{TRUE}  & \textbf{TRUE} \\
Qwen2.5-7B   & MMLU  & 0.006267 & 0.015667 & 0.012391 & FALSE          & \textbf{TRUE} \\
Qwen2.5-7B   & GSM8K & 0.005800 & 0.048000 & 0.035000 & \textbf{TRUE}  & \textbf{TRUE} \\
Llama-3.1-8B & MMLU  & 0.017163 & 0.040023 & 0.025495 & \textbf{TRUE}  & \textbf{TRUE} \\
Llama-3.1-8B & GSM8K & 0.013200 & 0.033000 & 0.026000 & \textbf{TRUE}  & \textbf{TRUE} \\
\midrule
\multicolumn{7}{l}{Winner flip in \textbf{5 of 8} (threshold $\geq 3$: met)\quad$\cdot$\quad Range/gap in \textbf{7 of 8} (threshold $\geq 4$: met)} \\
\multicolumn{7}{l}{$\max\mathrm{range} < 0.5\,\mathrm{gap}$ in \textbf{1 of 8} (disconfirm threshold $\geq 6$: not met)\quad$\cdot$\quad exact ties: \textbf{0 of 40}} \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[t]
\centering
\small
\caption{Per-seed differences $d_s = \mathrm{acc}_{\mathrm{GPTQ},s} -
\mathrm{acc}_{\mathrm{AWQ},s}$ on byte-identical calibration samples. A winner
flip is two seeds of opposite, nonzero sign; the five cells with a flip are
those whose row is not sign-constant. No entry is zero, which is the 0-of-40 tie
count stated above.}
\label{tab:h3-ds}
\begin{tabular}{llrrrrr}
\toprule
Model & Task & $d_0$ & $d_1$ & $d_2$ & $d_3$ & $d_4$ \\
\midrule
Qwen2.5-1.5B & MMLU  & $-0.029127$ & $-0.014029$ & $+0.012463$ & $-0.027631$ & $-0.003133$ \\
Qwen2.5-1.5B & GSM8K & $-0.111000$ & $-0.098000$ & $-0.080000$ & $-0.088000$ & $-0.107000$ \\
Llama-3.2-3B & MMLU  & $-0.008973$ & $-0.090514$ & $-0.023287$ & $-0.015026$ & $-0.016807$ \\
Llama-3.2-3B & GSM8K & $+0.021000$ & $+0.015000$ & $-0.005000$ & $+0.023000$ & $+0.035000$ \\
Qwen2.5-7B   & MMLU  & $+0.006694$ & $+0.009400$ & $+0.001638$ & $+0.001496$ & $+0.012107$ \\
Qwen2.5-7B   & GSM8K & $+0.022000$ & $+0.016000$ & $-0.023000$ & $+0.002000$ & $+0.012000$ \\
Llama-3.1-8B & MMLU  & $-0.016237$ & $-0.026777$ & $-0.047215$ & $+0.018302$ & $-0.013887$ \\
Llama-3.1-8B & GSM8K & $+0.023000$ & $-0.015000$ & $-0.004000$ & $-0.036000$ & $-0.034000$ \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Supporting analyses}
\label{sec:minigrid:supporting}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, header paragraph.
The three registered analyses below were run once per cell at the registered
parameters---2{,}000 bootstrap replicates, RNG seed 0---as part of the same job
that produced the verdict. \textbf{None of them modifies the verdict, and none
can.} The verdict is what the frozen rule returned over winner flips and
range/gap; a weak bootstrap rate or a poorly resolved cell is a limitation to
report, not a second application of the rule.

\paragraph{Variance components, kept separate.}
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slot 2 table.
% The registration forbids collapsing these into one number; they are reported
% side by side and never pooled.
Table~\ref{tab:h3-variance} reports seed-level SD and item-level SE as the
registration requires: side by side, never collapsed into a single dispersion
figure. The two answer different questions---how much a method's accuracy moves
when the calibration seed changes, against how precisely a single seed's
accuracy is estimated from the items---and the comparison between them is the
point. On MMLU the calibration seed moves the number more than the sample of
items does, in every cell: taking per cell the larger of the two seed-level SDs
against its own item-level SE, the ratio runs $1.6$ to $5.9\times$
(Qwen2.5-7B $0.006224$ against $0.003983$; Llama-3.2-3B $0.024925$ against
$0.004214$). On GSM8K the two components are of the same order throughout, and
in \emph{five of the eight} method-by-cell entries the item-level SE is the
larger of the two---the sample of items is moving the number as much as the
calibration seed is.
% Ratios are arithmetic on this table: MMLU per-cell larger-SD/its-SE =
% 4.54, 5.91, 1.56, 3.61 -> range 1.6-5.9. GSM8K SE > SD in 5 of 8 entries
% (qwen1.5b GPTQ+AWQ, llama3b GPTQ+AWQ, llama8b AWQ).

\begin{table}[t]
\centering
\small
\caption{Variance components per cell, reported separately as registered. SD is
across the five calibration seeds; SE is the item-level standard error within a
cell. MMLU cells run at $n = 14{,}042$ and GSM8K at $n = 1{,}000$, which is what
drives the SE columns.}
\label{tab:h3-variance}
\begin{tabular}{llrrrr}
\toprule
& & \multicolumn{2}{c}{Seed-level SD} & \multicolumn{2}{c}{Item-level SE} \\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}
Model & Task & GPTQ & AWQ & GPTQ & AWQ \\
\midrule
Qwen2.5-1.5B & MMLU  & 0.019130 & 0.006897 & 0.004215 & 0.004212 \\
Qwen2.5-1.5B & GSM8K & 0.006340 & 0.015116 & 0.015796 & 0.015658 \\
Llama-3.2-3B & MMLU  & 0.024925 & 0.011157 & 0.004214 & 0.004216 \\
Llama-3.2-3B & GSM8K & 0.004615 & 0.012300 & 0.015154 & 0.015308 \\
Qwen2.5-7B   & MMLU  & 0.006224 & 0.004537 & 0.003983 & 0.004002 \\
Qwen2.5-7B   & GSM8K & 0.019267 & 0.014195 & 0.013815 & 0.013922 \\
Llama-3.1-8B & MMLU  & 0.015100 & 0.010520 & 0.004183 & 0.004163 \\
Llama-3.1-8B & GSM8K & 0.014307 & 0.010654 & 0.013874 & 0.013640 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{The two-level paired bootstrap, and what a winner flip is not.}
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slot 3 table and
% §"Reconciling winner flips with bootstrap rank-flip rates" (5/8 flips,
% 6/8 bootstrap < 0.05, 3/8 both; the two unstable-on-both cells 0.2575, 0.1260).
The two columns of Table~\ref{tab:h3-bootstrap} measure different things, and a
reader who assumes otherwise will read them as self-contradictory. A winner flip
asks whether two \emph{individual seeds} disagree on sign---H3's registered
question, and a description of what happens when a practitioner runs one
calibration and takes the winner. The bootstrap rank-flip rate asks whether the
\emph{five-seed mean} ranking survives resampling seed labels and items
together, with GPTQ and AWQ holding the same sampled labels and indices.

The combination is the sharpest form of the finding. Winner flips occur in 5 of
8 cells; the bootstrap rate is below $0.05$ in 6 of 8; and \textbf{3 cells have
both}---Qwen2.5-1.5B/MMLU ($0.0445$), Llama-3.2-3B/GSM8K ($0.0220$) and
Llama-3.1-8B/MMLU ($0.0405$). In each, some pair of individual seeds disagrees
about which method wins while the five-seed average ranking survives resampling
in more than 95\% of replicates. The practical reading is actionable and is the
one we intend a practitioner to take away: \emph{a single calibration run can
hand you the wrong winner}, and averaging over the registered five seeds is
substantially more stable than any one of them.

\textbf{The limitation on that reading, stated plainly.} With five seeds the
bootstrap resamples seed labels from a sample of five, so it has limited
resolution on the seed-level distribution. What the low rates bound is the
stability of \emph{this} observed mean under resampling; they do not establish
that five seeds suffice in general, and no result here should be read as
licensing five as a sufficient number. Two GSM8K cells are unstable on both
measures---Qwen2.5-7B/GSM8K at $0.2575$ (515 of 2{,}000 replicates) and
Llama-3.1-8B/GSM8K at $0.1260$ (252 of 2{,}000)---where even the five-seed mean
ranking does not survive resampling, and no amount of seed averaging at
$n = 1{,}000$ rescues the comparison.

\begin{table}[t]
\centering
\small
\caption{Two-level paired bootstrap, 2{,}000 replicates at RNG seed 0, both
registered. Tie replicates are reported separately and are included in the
rank-flip denominator, per the registered convention. The final column repeats
the registered winner-flip outcome for comparison; the two are different
questions, not a consistency check.}
\label{tab:h3-bootstrap}
\begin{tabular}{llrlrll}
\toprule
Model & Task & Rank-flip rate & Replicates & Tie rate & Ties & Winner flip \\
\midrule
Qwen2.5-1.5B & MMLU  & 0.0445 & 89 / 2000  & 0.0005 & 1 / 2000  & \textbf{TRUE} \\
Qwen2.5-1.5B & GSM8K & 0.0000 & 0 / 2000   & 0.0000 & 0 / 2000  & FALSE \\
Llama-3.2-3B & MMLU  & 0.0000 & 0 / 2000   & 0.0000 & 0 / 2000  & FALSE \\
Llama-3.2-3B & GSM8K & 0.0220 & 44 / 2000  & 0.0000 & 0 / 2000  & \textbf{TRUE} \\
Qwen2.5-7B   & MMLU  & 0.0025 & 5 / 2000   & 0.0000 & 0 / 2000  & FALSE \\
Qwen2.5-7B   & GSM8K & 0.2575 & 515 / 2000 & 0.0100 & 20 / 2000 & \textbf{TRUE} \\
Llama-3.1-8B & MMLU  & 0.0405 & 81 / 2000  & 0.0000 & 0 / 2000  & \textbf{TRUE} \\
Llama-3.1-8B & GSM8K & 0.1260 & 252 / 2000 & 0.0030 & 6 / 2000  & \textbf{TRUE} \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Flip statistics, read against the atlas.}
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slot 4 table.
% base = GPTQ, method = AWQ, so net delta = acc_AWQ - acc_GPTQ (= -d_s in the
% decision record's sign convention). Churn quantities are direction-symmetric.
% Metrics from flipeval.core.compute_pair_metrics -- the same function behind
% the atlas population of \S\ref{sec:atlas}.
Table~\ref{tab:h3-flips} applies the atlas metrics of \S\ref{sec:atlas} to the
controlled cells, computed by the same function over the same definitions, so
the two populations can be read against each other. Here the contrast is
\emph{method against method at one bit width}, where the atlas contrast is
quantized against FP16.

\begin{table}[t]
\centering
\small
\caption{Flip statistics for the eight confirmatory cells, GPTQ against AWQ,
means over the five paired seeds. Net delta is
$\mathrm{acc}_{\mathrm{AWQ}} - \mathrm{acc}_{\mathrm{GPTQ}}$; harmful and
beneficial are the two directions of correctness change; accuracy-state churn is
their sum; total answer churn adds items that change answer without changing
correctness state.}
\label{tab:h3-flips}
\begin{tabular}{llrrrrrr}
\toprule
Model & Task & Net $\Delta$ & Harmful & Benef. & Churn & Wrong$\to$wrong & Answer churn \\
\midrule
Qwen2.5-1.5B & MMLU  & $+0.012292$ & 0.087965 & 0.100256 & 0.188221 & 0.091924 & 0.280145 \\
Qwen2.5-1.5B & GSM8K & $+0.096800$ & 0.098600 & 0.195400 & 0.294000 & 0.273800 & 0.567800 \\
Llama-3.2-3B & MMLU  & $+0.030922$ & 0.078465 & 0.109386 & 0.187851 & 0.098049 & 0.285899 \\
Llama-3.2-3B & GSM8K & $-0.017800$ & 0.113200 & 0.095400 & 0.208600 & 0.155800 & 0.364400 \\
Qwen2.5-7B   & MMLU  & $-0.006267$ & 0.059393 & 0.053126 & 0.112520 & 0.045250 & 0.157770 \\
Qwen2.5-7B   & GSM8K & $-0.005800$ & 0.091200 & 0.085400 & 0.176600 & 0.110000 & 0.286600 \\
Llama-3.1-8B & MMLU  & $+0.017163$ & 0.081270 & 0.098433 & 0.179704 & 0.090956 & 0.270659 \\
Llama-3.1-8B & GSM8K & $+0.013200$ & 0.083800 & 0.097000 & 0.180800 & 0.096400 & 0.277200 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Cancellation is more complete between two methods than against FP16}
\label{sec:minigrid:churnratio}

% SOURCE: atlas regime from \S\ref{sec:atlas:netgross}
% (docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1). Controlled regime is arithmetic
% on Table~\ref{tab:h3-flips}: churn / |net delta| per cell = 15.31, 3.04, 6.07,
% 11.72, 17.95, 30.45, 10.47, 13.70; min 3.04, max 30.45, median 12.71.
% The extreme cell is Qwen2.5-7B/GSM8K, read directly from the slot 4 row.
% TWO POINTS, NOT A CURVE. Do not restate this as a monotone relationship.
\begin{result}\label{res:churnratio}
The ratio of per-item churn to aggregate net delta is larger in the
controlled method-against-method contrast than in the observational
quantized-against-FP16 contrast. Across the atlas, churn runs
\textbf{$5.3\times$} net delta (\S\ref{sec:atlas:netgross}). Across the eight
controlled cells, comparing GPTQ with AWQ at the same bit width, it runs
\textbf{$3.0\times$ to $30.5\times$}, with a median of \textbf{$12.7\times$}.
\end{result}

The extreme cell makes the size of the discrepancy concrete. On
Qwen2.5-7B/GSM8K the two methods differ by \textbf{0.58\,pp} in aggregate
accuracy---a gap any reader would call equivalence---while \textbf{17.7\%} of
items change correctness state between them and \textbf{28.7\%} of answers
change outright.

The mechanism is cancellation, and it follows from what the two contrasts are.
Two quantization methods at the same bit width are far closer to each other in
aggregate than either is to its FP16 baseline. Harmful and beneficial flips are
correspondingly better balanced, cancellation in the aggregate is more complete,
and the surviving net delta therefore hides a proportionally larger amount of
per-item movement.

\textbf{We observe two regimes; we do not establish a curve.} These are two
measured points---one observational contrast at 1{,}707 cells, one controlled
contrast at 8---and nothing here licenses reading the ratio as a monotone
function of aggregate closeness. What the two points support is the direction of
the effect and the fact that the regime in which equivalence claims are actually
made is the less favourable of the two.
% Atlas 5.3 from \S\ref{sec:atlas:netgross} (rev-2 ratio of medians); controlled
% 3.04 / 12.71 / 30.45 are arithmetic on Table~\ref{tab:h3-flips}.

\subsection{Resolution: which arm of the experiment carries the result}
\label{sec:minigrid:resolution}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, "Step 5 -- resolution
% analysis (POST-HOC)" table and §Disclosure. The disclosure below is carried
% from that document, not paraphrased.
\paragraph{Disclosure.} \textbf{This quantity was not registered.} It was
requested on 2026-07-26, \emph{after} the eight-cell verdict had been computed
and signed, in response to prior art identified the same day---%
\citet{paglieri2024outliers}, which reports calibration effects diminishing in
modern LLMs (\S\ref{sec:related:reconcile}). It is descriptive, it tests no
hypothesis, and it does not modify the verdict. It is recorded with its
provenance rather than folded silently into the registered results.

Using the machinery of \S\ref{sec:certification} itself---paired
$\mathrm{sd} = \sqrt{p_d}$ and paired $\mathrm{SE} = \sqrt{p_d/n}$, with $p_d$
the per-cell GPTQ-against-AWQ accuracy-state churn of
Table~\ref{tab:h3-flips}---the two tasks separate sharply.

\begin{table}[t]
\centering
\small
\caption{Post-hoc resolution analysis. Ranges of the two ratios across the four
cells of each task. $p_d$ is computed per cell from
Table~\ref{tab:h3-flips} and is \emph{not} the harness study's $\bar{Q}$, which
is a quantized-against-FP16 contrast on a different pair.}
\label{tab:h3-resolution}
\begin{tabular}{lrr}
\toprule
Task & $\max\mathrm{range}$ in paired SE & $\mathrm{gap}$ in paired SE \\
\midrule
MMLU ($n = 14{,}042$) & 5.53 -- 17.45 & 2.21 -- 8.45 \\
GSM8K ($n = 1{,}000$) & 1.92 -- 3.61  & 0.44 -- 5.65 \\
\bottomrule
\end{tabular}
\end{table}

\textbf{MMLU carries the result.} All four MMLU cells satisfy the range/gap
criterion, their seed-induced ranges run $5.5$ to $17.5$ paired standard errors,
and their seed-level SD exceeds item-level SE by $1.6$ to $5.9\times$
(Table~\ref{tab:h3-variance}). The instability is far larger than the
measurement noise, and the benchmark resolves it comfortably.

\textbf{GSM8K is under-resolved at $n = 1{,}000$.} There the ranges run roughly
two to three-and-a-half SE, seed-level SD is of the same order as item-level SE,
and in three of the four GSM8K cells the \emph{mean gap itself} sits at or below
$1.25$ SE ($0.44$, $0.98$, $1.23$)---the quantity the range/gap criterion
compares against is, in those cells, not resolved by the benchmark at the $n$
used. Any per-cell reading of GSM8K should say so, and
\S\ref{sec:limitations} does.

This does not weaken the verdict. The range/gap criterion holds in 7 of 8 cells
and winner flips occur in 5 of 8, both computed from the registered per-seed
accuracies by the frozen rule, and neither is a significance test. What it means
is that the GSM8K cells carry materially less resolving power than the MMLU
cells---a statement about where the evidence concentrates, not a reweighting of
the rule.

\subsection{The apparatus caught its own experiment}
\label{sec:minigrid:selfaudit}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, §"The paper's own
% table predicted this"; results/certification_tables_rev2.csv, GSM8K rows at
% margin_pp = 2.0 (p25 0.039992 -> 619; median 0.076573 -> 1,184;
% p75 0.198446 -> 3,068). Observed p_d: 0.1766, 0.1808, 0.2086, 0.2940.
The certification table of \S\ref{sec:certification} requires, for GSM8K at a
2\,pp margin, about \textbf{1{,}184} items at median discordance and
\textbf{3{,}068} at the p75 discordance. The confirmatory GSM8K cells ran at
$n = 1{,}000$---already below the median requirement---and the discordance
actually observed in them is $p_d = 0.1766$, $0.1808$, $0.2086$ and $0.2940$,
at or above the table's p75, where the requirement is roughly three times the
$n$ used.

So the under-resolution was not a surprise: \textbf{this paper's own apparatus
predicted its own experiment's shortfall, and predicted it conservatively.} We
state that explicitly rather than let it be found. A tool that catches its
author is worth more than one that never had to, and an audit standard whose
first casualty is the audit's own controlled experiment is easier to trust than
one that always exonerates.

One caveat bounds the comparison. The certification table's discordance
percentiles describe a quantized-against-FP16 contrast, while $p_d$ here is
GPTQ-against-AWQ. The required-$n$ column is a function of discordance whatever
the pair, so reading the observed $p_d$ against the table's brackets is
legitimate; the percentile labels are not strictly like-for-like and are used
only to locate the magnitude.

\subsection{Deferred registered analyses}

% SOURCE: docs/MINIGRID_REGISTRATION_2026-07-15.md §4.3; PREREGISTRATION.md
% §"Experimental Grid" and the 2026-07-20 Decision Point A amendment.
The registered secondary analyses remain deferred with the rest of the main
grid: the 3-bit dose-response check, ARC-Challenge, HellaSwag, and the
WikiText-2 calibration-distribution contrast on Qwen2.5-1.5B-Instruct. The
last of these is governed by a dated amendment that defines a WikiText-2
``document'' as a reconstructed article, after a preflight found that
0 of 36{,}718 raw rows reach the registered 2{,}048-token length while 425 of
629 reconstructed articles do; the amendment records that no accuracy result had
been inspected when it was taken. None of these analyses can substitute for a
confirmatory cell.
```

---

## FILE: `paper/sections/minigrid_escalation.tex`

```latex
% =====================================================================
% Subsection: the mechanical escalation screen  (belongs to §8, sec:minigrid)
%
% PRIMARY SOURCES for every number here:
%   docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md  (SIGNED decision record)
%   results/minigrid_escalation/escalation_summary.json (machine-readable)
%
% HARD RULE (inherited from minigrid.tex): no sentence states an H3 outcome.
% The escalation rule is a SCREENING rule, not the confirmatory H3 rule. Only
% screening quantities from the signed record are reported (winner-flip and
% range/gap outcomes, gap, max range, the two counts). Per-seed cell accuracies
% are NOT reproduced here. The eight-cell verdict is a \TODO slot.
% =====================================================================

\subsection{The mechanical escalation screen}
\label{sec:minigrid:escalation}

% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md (design recap);
% docs/MINIGRID_REGISTRATION_2026-07-15.md §§1-2.
The four executed cells---$\{$Qwen2.5-1.5B-Instruct, Llama-3.2-3B-Instruct$\}
\times\{$MMLU, GSM8K$\}$, 4-bit GPTQ against 4-bit AWQ at seeds
$\{0,1,2,3,4\}$, with GPTQ and AWQ receiving byte-identical calibration samples
at each seed (\S\ref{sec:minigrid})---feed a pre-committed screen that decides
only one thing: whether the deferred 7B/8B cells are built. The screen is
mechanical and was frozen with the mini-grid registration before any of these
accuracies existed.

\paragraph{The rule, quoted verbatim (mini-grid registration \S3, frozen
2026-07-15).}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md, "The rule, quoted"
% block, reproducing docs/MINIGRID_REGISTRATION_2026-07-15.md §3 verbatim.
\begin{quote}
Compute, per the frozen algebra of \texttt{PREREGISTRATION.md}, for each of the
4 cells at 4-bit: winner flips across seeds (ties counted separately, per the
registered tie rule) and the range/gap criterion
$\max(\mathrm{range}_{\mathrm{GPTQ}}, \mathrm{range}_{\mathrm{AWQ}}) \geq
\mathrm{gap}$.

\emph{Escalate} to the deferred 7B/8B seed cells iff: winner flips occur in
\textbf{at least 1 of the 4 cells}, \textbf{or} the range/gap criterion holds in
\textbf{at least 2 of the 4 cells}.

If neither condition holds, the 7B/8B cells are not built, and no other result
(3-bit, other benchmarks, atlas findings) can substitute to trigger escalation.
\end{quote}

The winner-flip, $\mathrm{gap}$ and $\mathrm{range}_m$ definitions are the frozen
algebra recapped in \S\ref{sec:minigrid}: a winner flip needs two registered
seeds with opposite-signed, both-nonzero $d_s$, and exact ties are reported
separately and never count as flips.
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md (frozen algebra quote);
% PREREGISTRATION.md §"H3 Decision Rule".

\paragraph{Per-cell screen.}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md, "Per-cell registered
% quantities" and "Mechanical application of §3"; cross-checked against
% results/minigrid_escalation/escalation_summary.json fields winner_flip, gap,
% max_range, range_gap_holds per cell. NO per-seed accuracy is reproduced here.
Table~\ref{tab:minigrid-escalation} states each cell's outcome exactly as the
signed decision record does. $\mathrm{gap}$ is the absolute mean method
difference and $\max\mathrm{range}$ is
$\max(\mathrm{range}_{\mathrm{GPTQ}},\mathrm{range}_{\mathrm{AWQ}})$; the
range/gap criterion holds when the latter is at least the former. No cell
contained an exact tie.

\begin{table}[t]
\centering
\small
\caption{The mechanical escalation screen over the four completed mini-grid
cells. Outcomes are reproduced verbatim from the signed decision record; the
per-seed accuracies that produce them are not restated here. ``Winner flip''
and ``range/gap holds'' are the two \S3 predicates; the counts beneath drive the
decision.}
\label{tab:minigrid-escalation}
\begin{tabular}{llrrl}
\toprule
Cell & Winner flip & $\mathrm{gap}$ & $\max\mathrm{range}$ & Range/gap holds \\
\midrule
Qwen2.5-1.5B / MMLU  & \textbf{TRUE}  & 0.012292 & 0.040521 & \textbf{TRUE} \\
Qwen2.5-1.5B / GSM8K & FALSE          & 0.096800 & 0.033000 & FALSE \\
Llama-3.2-3B / MMLU  & FALSE          & 0.030922 & 0.063809 & \textbf{TRUE} \\
Llama-3.2-3B / GSM8K & \textbf{TRUE}  & 0.017800 & 0.034000 & \textbf{TRUE} \\
\midrule
\multicolumn{5}{l}{Winner flip in \textbf{2 of 4} cells (threshold $\geq 1$: met)\quad$\cdot$\quad Range/gap holds in \textbf{3 of 4} cells (threshold $\geq 2$: met)} \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Outcome.}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md, "Mechanical
% application of §3" (2/4, 3/4) and "Decision" (ESCALATE = TRUE);
% results/minigrid_escalation/escalation_summary.json (n_cells_winner_flip 2,
% n_cells_range_gap 3, escalate true). Signature: signed Amogh Singh 2026-07-23.
A winner flip occurs in \textbf{2 of 4} cells (Qwen2.5-1.5B/MMLU and
Llama-3.2-3B/GSM8K), clearing the ``$\geq 1$'' branch, and the range/gap
criterion holds in \textbf{3 of 4} cells, clearing the ``$\geq 2$'' branch. Both
branches of the disjunction are independently satisfied, so the screen fires:
\textbf{escalation is triggered}, and the record was signed on 2026-07-23,
authorizing construction and evaluation of the deferred 7B/8B seed cells
(Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct $\times$ MMLU, GSM8K).

\paragraph{The screen ran on sealed cells.}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md header (validator
% 11375247, 409/409, passed:true; first inspection authorized 2026-07-23) and
% "Provenance" (gates re-derived under Amendment 3,
% docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md, committed bd565bd).
The four cells stayed sealed---no accuracy read by anyone---until the registered
validator passed over the complete 44-JSONL expected set (job \texttt{11375247},
409/409 checks), which is the first mini-grid accuracy inspection the
registration permits and the same-day escalation record it requires. The FP16
gate failure that preceded the run, and its correction, were resolved \emph{before}
any inspection: the gates behind these cells were re-derived under Amendment~3
(\texttt{docs/MINIGRID\_FP16\_GATE\_DERIVATION\_2026-07-21.md}, committed
\texttt{bd565bd}), so the screen fired on a grid whose reference gates were
already settled rather than tuned to its result.

\paragraph{This screen is not the H3 verdict.}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md, "Decision" paragraph
% ("No H3 verdict is stated here ... the confirmatory rule is defined over all
% eight cells"); docs/MINIGRID_REGISTRATION_2026-07-15.md §4.
Escalation is a screening decision about \emph{which cells to build}, not a
conclusion about H3. The confirmatory verdict is the frozen
Supported/Disconfirmed/Inconclusive rule applied once, mechanically, over all
eight cells---this grid plus the 7B/8B cells---and it is defined only when all
eight exist. None of the 7B/8B cells existed when the screen fired, so no verdict
follows from it. That the screen fired says the registered rule judged these four
cells to warrant the confirmatory eight; it said nothing, in either direction,
about what the eight-cell rule would return. The verdict it authorized the
construction of is reported in \S\ref{sec:minigrid:verdict}, and the four cells
above enter it unchanged: re-deriving them inside the eight-cell analysis
reproduced every quantity in Table~\ref{tab:minigrid-escalation} exactly, to the
six decimals published here, which is a regression test of the analysis code
against a signed known answer rather than a restatement of it.
% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md, "Precondition 2 -- known-
% answer regression": KNOWN_ANSWER: PASS (4/4 cells reproduce the signed values
% exactly), covering winner flips, range/gap verdicts, tie sets and all four
% quantities per cell.
```

---

## FILE: `paper/sections/harness_sensitivity.tex`

```latex
% =====================================================================
% Section: Harness-defaults sensitivity study  -- COMPLETE DRAFT
%
% TRIMMED 2026-07-26. The "two live defects" motivation, the design /
% pre-named-ratio subsection (with the two-phase Qbar deferral and the declined
% early-inspection amendment), the full condition-B narrative and the MMLU
% C==D collapse argument moved VERBATIM to
% sections/appendix_harness_detail.tex. Nothing was deleted in the move.
% BOTH RESULT TABLES STAY HERE -- they are the deliverable.
%
% PRIMARY SOURCES for every number in this section:
%   docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md  (FROZEN protocol)
%   docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md       (results narrative)
%   docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md          (the denominator Qbar)
%   results/harness_sensitivity/sensitivity_results_qwen25-1p5b.json (machine-readable)
%
% DISCIPLINE FOR THIS FILE:
%  - Exploratory study; it states NO H3 outcome and licenses no confirmatory read.
%  - The only confirmatory-derived quantity quoted is the committed denominator
%    Qbar (mean over the ten Qwen quantized variants). No per-variant / per-cell
%    confirmatory accuracy or churn is quoted -- see the Qbar artifact only.
%  - R is never printed without C_cond and Qbar beside it (registration §5.1).
% =====================================================================

\section{How much does the harness move the score? A configuration-sensitivity study}
\label{sec:sensitivity}

The certification apparatus of \S\ref{sec:certification} treats the compressed
model as the source of per-item churn and the evaluation as a fixed instrument.
This section asks the complementary question and finds the instrument is not
fixed: \emph{how much does evaluation-harness configuration move accuracy and
per-item answers on a single, unchanged model, relative to how much quantization
moves them under a fixed configuration?}
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §1 (question
% statement), header + §§1, 7 (exploratory status; results-blind at freeze; the
% two live defects, one moving GSM8K accuracy 0.232 -> 0.566 on unchanged
% generations). Both defects and the full design: app:harness-detail.
It is a small, preregistered, \emph{exploratory} study---one model, the bridge
item subsets---frozen before any of its own results existed. The motivation is
not hypothetical: this campaign produced two live configuration defects inside
eight days on the pinned \texttt{lm\_eval}~0.4.12, one of which moved reported
GSM8K accuracy $0.232 \to 0.566$ with not one token of model output changed
(Appendix~\ref{app:harness-detail}).

% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.1 (R definition,
% "C_cond and Qbar always reported beside it", undefined-if-zero rule);
% docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md (Qbar(mmlu)=0.199000,
% Qbar(gsm8k)=0.287000); results/harness_sensitivity/qbar_qwen25-1p5b.json.
The headline statistic, fixed before any run, is
$R_{\mathrm{cond}} = C_{\mathrm{cond}}/\bar{Q}$: the numerator is
correctness-state churn between the reference configuration and a condition on
the fixed FP16 model---the atlas churn definition (\S\ref{sec:atlas})---and the
denominator is the mean correctness-state churn of the ten Qwen2.5-1.5B
quantized variants against that model's FP16 cell on the same items, per task,
giving $\bar{Q}(\text{MMLU}) = \mathbf{0.199}$ and
$\bar{Q}(\text{GSM8K}) = \mathbf{0.287}$. So $R$ asks directly how a
configuration change compares with swapping in a quantized model. The
registration forbids printing the ratio without both inputs, and both appear in
every row below.

% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, GSM8K table
% (n=200, REF acc 0.5750, Qbar 0.287); every cell cross-checked against
% results/harness_sensitivity/sensitivity_results_qwen25-1p5b.json
% per_task.gsm8k.conditions (acc_cond, net_acc_delta, C_cond,
% correctness_changed, answer_churn, dir_correct_to_incorrect,
% dir_incorrect_to_correct, R_cond).
\begin{table}[t]
\centering
\small
\caption{GSM8K configuration sensitivity on FP16 Qwen2.5-1.5B, $n=200$,
reference accuracy $0.575$, against the quantization denominator
$\bar{Q}=0.287$. $C_{\mathrm{cond}}$ is correctness-state churn versus the
reference; $R=C_{\mathrm{cond}}/\bar{Q}$ is reported only with both inputs in
view. The $\text{c}{\to}\text{i}/\text{i}{\to}\text{c}$ column splits churned
items by direction so churn is never read as net degradation.}
\label{tab:sensitivity-gsm8k}
\begin{tabular}{llrrrrr}
\toprule
Cond & Configuration vs.\ reference & Acc & Net $\Delta$ & $C_{\mathrm{cond}}$ & c$\to$i / i$\to$c & $R=C_{\mathrm{cond}}/\bar{Q}$ \\
\midrule
A & exemplars as separate turns   & 0.515 & $-0.060$ & \textbf{0.240} & 30 / 18 & \textbf{0.836} $=0.240/0.287$ \\
B & \texttt{strict-match} rescore & 0.120 & $-0.455$ & \textbf{0.455} & 91 / 0  & \textbf{1.585} $=0.455/0.287$ \\
C & chat template off, 3-shot     & 0.475 & $-0.100$ & \textbf{0.320} & 42 / 22 & \textbf{1.115} $=0.320/0.287$ \\
D & stock defaults (chat off, 5-shot) & 0.495 & $-0.080$ & \textbf{0.300} & 38 / 22 & \textbf{1.045} $=0.300/0.287$ \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:sensitivity-gsm8k} reads directly against the denominator. Three
of the four GSM8K conditions---C, D, and B---have $R \geq 1$: turning the chat
template off (C, $R=1.115$), accepting every stock default at once (D,
$R=1.045$), and switching the extraction filter (B, $R=1.585$) each move a fixed
model's per-item correctness by \emph{as much as or more than} swapping GPTQ for
one of ten quantized variants moves it. Only condition~A, the multiturn
exemplar placement, stays below the quantization scale ($R=0.836$). The net
accuracy deltas ($-0.06$ to $-0.455$) understate the movement in every case,
because they net directional churn that the
$\text{c}{\to}\text{i}/\text{i}{\to}\text{c}$ column keeps separate.
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, GSM8K table (R values
% 0.836/1.585/1.115/1.045; net deltas -0.060/-0.455/-0.100/-0.080).
Condition~B is sharpest because it holds the generations fixed---the stock task
applies both filters to the same outputs, so B is a rescore of \emph{identical}
generations at zero GPU cost, and its $91/0$ split means \texttt{strict-match}
accepts a strict subset of what \texttt{flexible-extract} accepts here
(Appendix~\ref{app:sensitivity:condB}).

% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, MMLU table (n=400,
% REF acc 0.4150, Qbar 0.199; C==D acc 0.4600, net +0.0450, C_cond 0.2100
% (84/400), dir 33/51, R 1.055); results JSON per_task.mmlu.conditions.C_equiv_D.
% C and D are byte-identical for MMLU (registration §3.3); the argument is at
% app:sensitivity:mmlu-collapse.
\begin{table}[t]
\centering
\small
\caption{MMLU configuration sensitivity on FP16 Qwen2.5-1.5B, $n=400$,
reference accuracy $0.415$, against $\bar{Q}=0.199$. Conditions~C and~D are
byte-identical for MMLU and are reported once as $C\equiv D$ (registration
\S3.3).}
\label{tab:sensitivity-mmlu}
\begin{tabular}{llrrrrr}
\toprule
Cond & Configuration vs.\ reference & Acc & Net $\Delta$ & $C_{\mathrm{cond}}$ & c$\to$i / i$\to$c & $R=C_{\mathrm{cond}}/\bar{Q}$ \\
\midrule
$C\equiv D$ & chat template off, zero-shot & 0.460 & $\mathbf{+0.045}$ & \textbf{0.210} & 33 / 51 & \textbf{1.055} $=0.210/0.199$ \\
\bottomrule
\end{tabular}
\end{table}

The MMLU cell makes a point the net delta hides. Turning the chat template off
\emph{raises} reported accuracy by $+4.5$\,pp ($0.415 \to 0.460$), with a
directional split of $33/51$---more items recovered than lost.
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, MMLU row (net +0.0450,
% dir 33/51).
So the harness default is not uniformly worse than the reference: on MMLU it is
better, on GSM8K worse, and either way \emph{different}. The churn behind the
$+4.5$\,pp is $C_{C\equiv D}=0.210$ ($84$ of $400$ items), giving $R=1.055$---again
on the quantization scale. The movement is real, signed differently on the two
tasks, and of a kind compression papers do not report: the setting that almost
never appears in a model card is precisely the one silently moving the number a
``near-lossless'' claim rests on.

\paragraph{The same move, in another domain.} Holding the system fixed and
varying the instrument is not specific to compression.
\citet{bronder2026instrument} do it for language-model \emph{honesty}
evaluation: with the player model held fixed, four instrument
choices---outcome grammar, criterion disclosure, budget rendering and register
presence---substantially changed what the evaluation would have reported, under
decision rules recorded before results were read. That study and this one share
a design and a conclusion on different objects, which is the reason to expect
the effect wherever an evaluation is treated as a fixed instrument.

\paragraph{Scope.}
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md (all R values, range
% 0.836--1.585); docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §2 (Llama
% added only after its canary pair passes), §7 (exploratory; licenses no
% confirmatory read; no gate/rule adjusted).
On a fixed FP16 model and matched items, harness configuration moves per-item
correctness by an amount comparable to quantization---$R \in [0.836,\,1.585]$
across the five conditions, the scoring-filter choice ($R=1.585$) exceeding the
quantization denominator outright---so a compression comparison run under an
unstated or mismatched configuration can be dominated by the configuration.
These caveats travel with the numbers. This is \textbf{one model}
(Qwen2.5-1.5B-Instruct); the Llama-3.2-3B arm is admitted only after its seed-0
canary passes, which has not run, so no Llama $R$ is reported. The items are the
\textbf{bridge subsets} ($n=400$ MMLU, $n=200$ GSM8K), chosen so the study
touches no confirmatory item definition. And the study is
\textbf{exploratory}: it adjusts no gate, no escalation rule, and no
confirmatory analysis, and states no H3 outcome. It contextualises how a
compression score should be read; it decides nothing about the compression
methods themselves.
```

---

## FILE: `paper/sections/discriminant.tex`

```latex
% =====================================================================
% Section: Discriminant validity -- SKELETON with pilot numbers wired.
% COMPRESSED IN PLACE 2026-07-26 to a single paragraph plus the TODO. No
% relocation. Everything the brief required survives: both pilot results, both
% p-values, the churn figures, the required-n figures, the point that the
% smaller evaluation is the one that detected nothing, and the pilot's caveats
% folded into the same paragraph.
%
% SOURCE for every number: results/PILOT_RESULTS.md (archive
% pilot_outputs_20260711T000427Z.tar.gz, sha256 a72ff2fd...898a72ecb8), first
% table (rows MMLU/GPTQ public, GSM8K/GPTQ public, GSM8K/AWQ public) and second
% table (required-n columns). The pilot is exploratory evidence from an unpinned
% Kaggle environment without chat templates, and it cannot test H3.
% =====================================================================

\section{Discriminant validity: the framework does not call everything noise}
\label{sec:discriminant}

A certification-first framework invites one objection: a method demanding
thousands of items before declaring anything will declare nothing. The same
analysis applied to two comparisons answers it. In the project's
public-checkpoint pilot, MMLU with a public GPTQ checkpoint at $n = 400$ showed
a net delta of $-4.25$\,pp, flip rates of $0.095$ harmful and $0.0525$
beneficial, and exact McNemar $p = 0.036$: a detectable degradation. On GSM8K at
$n = 200$, net deltas were $+2.0$\,pp (GPTQ, $p = 0.672$) and $+1.0$\,pp (AWQ,
$p = 0.880$), with accuracy-state churn of $0.250$ and $0.220$ and total answer
churn of $0.630$ and $0.620$---noise-indistinguishable differences sitting on
very large behavioural change, and detecting them at 80\% power would have
needed 4{,}923 and 17{,}347 items against the 200 evaluated. The framework thus
separates real damage from cancellation noise with one analysis and no post-hoc
thresholds, and not in the convenient direction: \emph{the smaller evaluation is
the one that detected nothing}, which is what an underpowered evaluation should
do. The GSM8K rows are also a compact instance of the net-versus-gross gap
\S\ref{sec:atlas} measures at scale. The pilot's own caveats bound all of it:
raw-text prompts with no chat template, so absolute accuracies sit far below a
standard instruct evaluation; an unpinned Kaggle image modified in place; two
public checkpoints with fixed or undocumented calibration, so it cannot test H3;
and wide intervals at $n = 400$ and $200$. It is exploratory evidence for
discriminant behaviour and nothing else.

\TODO{replace or supplement with controlled cells from \S\ref{sec:minigrid}
once they exist, keeping the pilot as the historical record of the same
demonstration under worse conditions}
```

---

## FILE: `paper/sections/artifacts.tex`

```latex
% =====================================================================
% Section: Artifacts -- SKELETON.
% TRIMMED 2026-07-26. The datasheet, metadata/identifiers and maintenance
% subsections moved VERBATIM to sections/appendix_artifacts_detail.tex.
% Nothing was deleted in the move.
% No URL, DOI, or version number may be written here until it exists.
% =====================================================================

\section{Artifacts}
\label{sec:artifacts}

Five artifacts are released. The \textbf{flip atlas} gives per-cell paired
statistics for every enumerated pair-task cell, with the exclusion table and the
frozen pair manifest (\textbf{CC-BY-4.0}). \textbf{\texttt{flipeval}} is the
analysis package---flip rates, the churn family, exact McNemar, TOST at a
declared margin, bootstrap intervals, item-bootstrap rank-flip rates, minimum
detectable difference, required-$n$, and the certification-table generator
(\textbf{Apache-2.0}). The \textbf{audit artifacts} are the frozen claim table
with source content hashes and the per-claim verdict CSV, with every robustness
and transparency column. The \textbf{certification tables} ship twelve rows per
margin at 1, 2 and 3\,pp. The \textbf{reproduction package} carries the
registrations and their dated amendments, configs, the container image sha256,
SLURM scripts, per-run manifests, and the source-state freeze fingerprints.
Appendix~\ref{app:artifacts-detail} holds the datasheet, metadata and
maintenance statements.
\TODO{HuggingFace dataset URL; Zenodo DOI; package URL; released version;
lm-evaluation-harness integration status}
```

---

## FILE: `paper/sections/limitations.tex`

```latex
% =====================================================================
% Section: Limitations -- SKELETON, but every bullet below is already supported
% by a committed source and should survive to the final version.
% =====================================================================

\section{Limitations}
\label{sec:limitations}

\paragraph{The atlas is a record, not a sample.}
% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1 population caveats;
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.
S1 is community quantizations of 2023-era models, conditioned on leaderboard
coverage; S2 is one vendor's releases, evaluated by that vendor. Statistics
computed over the atlas describe the evidence the field circulates, not the
behaviour of quantization in general.

\paragraph{Discordance is imputed for audited claims.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Method, imputation-tier table.
No audited source reports a per-item disagreement rate, so the audit imputes one
from the nearest atlas tier, using the median of the first non-empty tier. Two
claims fall through to the global tier and one matches at the most specific tier;
the match tier is released per claim, and the independent-binomial robustness
column bounds the effect of the imputation in the conservative direction.

\paragraph{Family aggregation in the certification tables.}
% SOURCE: results/certification_tables_rev2.csv column n_atlas_cells
% (mmlu_pro 5, ifeval 8; all other families >= 17); docs/CERTIFICATION_TABLES_
% 2026-07-20.md §"Scope and caveats". REV-2: this read "four families" under
% rev-1; corrected 2026-07-26 to agree with \S\ref{sec:cert:caveats}.
Per-subject and per-subtask cells are collapsed into families, so a family's
quartile band mixes subject-level with model-level variation. This makes the
p25--p75 columns conservative; two families rest on fewer than 12 cells and are
indicative only.

\paragraph{Claim-level granularity in the audit.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #4.
Verdicts are computed per claim, at the pooled $n$ the frozen table records,
rather than per claim\,$\times$\,benchmark, because operating at a finer
granularity would require inventing rows the freeze does not contain.

\paragraph{Audit scope.}
The three frames fix the population; sources outside them are not audited, and
claims discovered after the table freeze would form a separately reported
post-freeze stratum. The audit measures evidential sufficiency only, and says
nothing about whether an audited model is in fact equivalent.

\paragraph{Experimental scope.}
% SOURCE: docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 4;
% docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED) §"What this verdict does
% and does not say".
% RESOLVED 2026-07-27: escalation fired, the 7B/8B cells completed, and all
% eight confirmatory cells exist. The \minigridTODO this paragraph carried is
% closed by stating the executed scope rather than the deferred one.
The controlled experiment covers all 8 registered confirmatory cells---1.5B to
8B parameters, two benchmarks, 4 bits, two methods, five seeds---and nothing
beyond them. The verdict licenses no statement about 3-bit behaviour,
ARC-Challenge, HellaSwag, calibration-\emph{dataset} effects, or any model or
benchmark outside the registered set. The atlas reaches 405B but is
observational; the controlled grid is causal but small, and eight cells is a
small number of cells however cleanly they were obtained.

\paragraph{Five seeds is few, and the bootstrap inherits that.}
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, §"Reconciling winner
% flips with bootstrap rank-flip rates" (3 of 8 cells: winner flip TRUE with
% bootstrap rate < 0.05) and the registered parameters (2000 replicates, seed 0).
The two-level bootstrap of \S\ref{sec:minigrid:supporting} resamples seed labels
from a sample of five, so it has limited resolution on the seed-level
distribution it is drawing from. Where its rank-flip rate is low, what that
bounds is the stability of the \emph{observed} five-seed mean under resampling.
It is not evidence that five seeds are sufficient in general, and the three
cells that combine a winner flip with a rank-flip rate below $0.05$ should be
read as ``one calibration run can mislead, and five were more stable here''---not
as a recommendation of five. A design aimed at the seed-level distribution
itself would need more seeds than the registration committed to.

\paragraph{The GSM8K arm is under-resolved.}
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, step 5 table (POST-HOC)
% and §"The paper's own table predicted this";
% results/certification_tables_rev2.csv GSM8K rows at margin_pp = 2.0.
The four GSM8K confirmatory cells ran at $n = 1{,}000$, where a post-hoc
resolution analysis puts the seed-induced range at roughly two to three-and-a-half
paired standard errors and the mean gap itself at or below $1.25$\,SE in three of
the four cells (\S\ref{sec:minigrid:resolution}). Seed-level SD and item-level SE
are of the same order there, where on MMLU the seed term dominates. This paper's
own certification table asked for about $1{,}184$ GSM8K items at median
discordance and $3{,}068$ at p75, and the discordance observed in these cells sits
at or above p75---so the shortfall was predicted by \S\ref{sec:certification}
before it was measured (\S\ref{sec:minigrid:selfaudit}). The verdict is unaffected,
being a count over the frozen rule rather than a significance test, but the MMLU
cells carry the evidence and any per-cell reading of GSM8K should say so.

\paragraph{Benchmarks and languages.}
% SOURCE: results/atlas_cells_summary_rev2.csv reason column, via
% \S\ref{sec:atlas:construction} (33 cells, 13.3% of 248 exclusions, carry no
% binary correctness metric). REV-2: this cited 643, the rev-1 float-scored
% count that the spot-check retracted (\S\ref{sec:prereg-spotcheck}); corrected
% 2026-07-26 so the paper no longer retracts a number in one section and cites
% it in another.
All benchmarks are English and predominantly multiple-choice or short-answer,
with per-item correctness defined by the original harness. Float-scored
generation tasks are outside the flip model entirely---33 atlas cells were
excluded for exactly this reason---so nothing here applies to quality claims
about open-ended generation, including the CIDEr-style metric that made one
audited claim unscoreable (\S\ref{sec:audit:r04}).

\paragraph{Status of the atlas numbers.}
% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md lines 5-7 (the original
% provisional marking); docs/ATLAS_REV2_CORRECTION_2026-07-21.md §Verification
% (first spot-check 2026-07-21, 10 cells, 262/262 fields, 0 discrepancies,
% embers jobs 11338401/11338619/11338712/11338745) and §"targeted second
% spot-check" (14/14 cells, 126/126 fields).
% \TODO CLOSED 2026-07-26 by restating as completed, per its own instruction:
% both spot-checks have now passed and are documented, so the precondition the
% marker named is met. The independent-check requirement did real work -- it is
% what produced the rev-1 -> rev-2 correction -- so the paragraph is restated
% rather than removed.
The atlas pipeline had two bugs found and fixed during its run, and its numbers
were held provisional pending an independent spot-check. That check has since
been completed twice: a first pass over ten stratified cells reconciled all 262
compared fields and surfaced the population defect that produced rev-2
(\S\ref{sec:prereg-spotcheck}), and a targeted second pass over the recovered
cells reconciled 14 of 14 cells and 126 of 126 fields. The figures reported here
are rev-2 and are no longer provisional. The correction itself, and the delta
between the two revisions, are reported rather than absorbed
(Appendix~\ref{app:prereg:rev2delta}).
```

---

## FILE: `paper/sections/conclusion.tex`

```latex
% =====================================================================
% Section: Conclusion -- SKELETON. The proposed reporting standard is the part
% a reader should be able to copy into a model card, so keep it short, concrete,
% and free of hedging.
% =====================================================================

\section{Conclusion: a reporting standard for compression claims}
\label{sec:conclusion}

The claim ``near-lossless'' is cheap to write and expensive to support. This
paper measured the gap---\textbf{4 of 12 determinate claims underpowered for
their own assertion, 5 of 17 unevaluable from what is reported, 0 of 17
reproducible from released artifacts}---and supplied the apparatus that closes
it: equivalence certification at a declared margin, and sample-size tables
computed from observed churn rather than assumed variance.

% Sequential certification was a full section in earlier drafts. It is a
% registered-but-unrun component and a results-free section reads as padding, so
% it is reduced to this sentence (2026-07-26). Restore the section only when the
% dated registration document exists under docs/ AND the component has run.
The same apparatus is being extended to anytime-valid sequential certification,
in which a confidence sequence lets an evaluation be monitored continuously and
stopped as soon as the model is certified; that component is registered but has
not yet been run, and no results for it are reported here.

We propose five lines that a model card or method paper can adopt directly.

\begin{enumerate}
  \item \textbf{Declare a margin.} ``Equivalent'' without $\pm m$ is not a
  testable statement. State the margin before evaluating.
  \item \textbf{Run the paired test.} Report TOST at your margin, not just a
  non-significant difference test. Failing to detect a difference is not
  equivalence.
  \item \textbf{Report churn next to net delta.} They are different quantities;
  in the public record churn runs $5.3\times$ the net delta, and roughly one
  evaluation cell in ten posts an identical score while still disagreeing on
  items.
  % REV-1 SURVIVOR, CORRECTED 2026-07-27: read "five to six times", which was
  % the rev-1 ratio. Rev-2 gives 5.31 (S1) and 5.33 (S2). See
  % \S\ref{sec:atlas:netgross}.
  \item \textbf{Cite the sample size you met.} Table~\ref{tab:certification}
  gives the count your benchmark family requires at your margin; say which
  column you are in and what you actually ran.
  \item \textbf{Release per-item outputs.} A few megabytes converts an assertion
  into something a third party can check. No source we audited did this for the
  tasks its own claim covers.
\end{enumerate}

% CLOSED 2026-07-27. The \TODO's precondition -- all eight registered cells
% exist -- was met on 2026-07-26, and the verdict is signed
% (docs/H3_EIGHT_CELL_DECISION_2026-07-26.md), so the closing paragraph is
% written and may state the outcome. It states nothing the signed record does
% not contain.
% SOURCE: \S\ref{sec:minigrid:verdict} (5 of 8); \S\ref{sec:minigrid:churnratio}
% Result 1 (5.3x observational, 12.7x controlled).
The controlled experiment says where this standard actually bites, and it is not
where the five lines above suggest. Every one of them is written as though the
comparison at issue were a compressed model against its original. H3 compares
two \emph{compressed} models---GPTQ against AWQ at the same bit width, the
choice a practitioner makes after deciding to compress at all---and finds the
evidence problem strictly worse there: churn at $12.7\times$ the net delta
against the atlas's $5.3\times$, and the winner reversing on nothing but the
calibration seed in 5 of 8 registered cells. The reason is the same mechanism in
its sharpest form. Two compressed models are more alike than either is to the
original, so cancellation is more complete and the aggregate hides more.

That generalises the standard past its own framing. Nothing in the five lines is
about quantization. They are about comparing two models similar enough that
somebody thought the comparison worth making---compressed against original,
method against method, checkpoint against checkpoint, version against version.
Aggregate accuracy is least informative exactly where it is most used, and the
remedy is not a better summary statistic but the per-item evidence and the
declared margin that make a similarity claim checkable at all.
```

---

## FILE: `paper/sections/appendix_audit_table.tex`

```latex
% =====================================================================
% Appendix: the full audit table -- SKELETON.
% The appendix table is generated from results/audit_verdicts.csv; do not
% hand-transcribe it. Column semantics below are copied from that file's header
% and from docs/AUDIT_VERDICTS_2026-07-20.md.
% =====================================================================

\section{Full audit table}
\label{app:audit-table}

\TODO{typeset the full 17-row table directly from
\texttt{results/audit\_verdicts.csv} (one row per claim, landscape, small
font). Do not retype values.}

The released CSV carries, per claim: identity and frame; method family, bit
width and benchmark; the reported or imputed $n$ with its \texttt{n\_basis};
the claimed margin with its \texttt{margin\_basis}; the imputed discordance with
its match tier and the number of atlas cells behind it; indeterminacy status,
kind, and reason; the components that remain computable for indeterminate
claims; the V3 reproducibility value; V1 as paired and independent-binomial MDD
with both margin ratios; V2 required-$n$ at 1, 2 and 3\,pp under both variance
models, plus at the claim's own margin; the applicable margin and its basis;
the margin-sensitivity flag; and both verdicts
(\texttt{verdict} and \texttt{verdict\_at\_registered\_2pp}).

\paragraph{Reading the transparency columns.} Rows marked indeterminate carry
numbers in some V1/V2 columns. Those numbers are \emph{not} verdicts and are not
counted in $K$; they are retained so that a reader can see exactly what the
analysis could and could not evaluate. R04's GSM8K computation is the largest
such quantity and is discussed in \S\ref{sec:audit:r04}.

\section{Certification tables at 1\,pp and 3\,pp}
\label{app:certification-margins}

\TODO{typeset the 1\,pp and 3\,pp margins from
\texttt{results/certification\_tables\_rev2.csv}; the 2\,pp margin is
Table~\ref{tab:certification} in the main text. Note the quadratic margin
scaling: MMLU's median requirement is 8{,}656 items at 1\,pp, 2{,}164 at 2\,pp,
and 962 at 3\,pp.}
% SOURCE: results/certification_tables_rev2.csv, rows mmlu at margin_pp
% 1.0/2.0/3.0, column required_n_median.
%
% CORRECTION (2026-07-22). This block previously read "944 at 3 pp" and pointed
% at the rev-1 CSV, while its 1 pp and 2 pp values (8,656 and 2,164) were
% already rev-2. The triple was mixed: two of three values had been updated and
% the third had not. Commit 272136b lists the intended change as "944 -> 962",
% so the value was identified at the time and missed in this one place.
% Corrected to 962 (results/certification_tables_rev2.csv, mmlu, margin_pp 3.0,
% required_n_median), and the SOURCE pointer moved to the rev-2 file to match.
% The stale value sat inside this TODO rather than in typeset body text, so it
% was never a rendered claim -- but it is the instruction this appendix would
% have been typeset from.

\section{Preregistration documents}
\label{app:registrations}

\TODO{reproduce, verbatim, \texttt{PREREGISTRATION.md} and the three
2026-07-15 registrations with their dated amendments, or link them at the
archived commit. Reviewers should be able to read the frozen rule text that
\S\ref{sec:prereg} describes.}
```

---

## FILE: `paper/sections/appendix_prereg_detail.tex`

```latex
% =====================================================================
% Appendix: Preregistration detail
% -- Relocated from sections/preregistration.tex on 2026-07-26 as part of the
%    structural trim. NOTHING WAS DELETED IN THE MOVE: the disclosed-contact
%    subsection, all seven interpretive choices, and the full spot-check
%    narrative appear here verbatim, with their % SOURCE comments.
%
% PRIMARY SOURCES:
%   docs/AUDIT_REGISTRATION_2026-07-15.md     (frozen; Amendment 1 appended)
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md (frozen)
%   docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices", §Provenance
%   docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §"Why this note exists"
%   docs/ATLAS_REV2_CORRECTION_2026-07-21.md  (spot-check, rev-1 -> rev-2 delta)
%
% DISCLOSURE BOUNDARY -- ENFORCE ON EVERY EDIT.
% The retired "6.3% flips at identical score" anecdote (bnb-4bit same-repo
% rerun) may appear in THIS FILE ONLY, labelled as (i) pre-registration data
% contact and (ii) outside the frozen 59-pair manifest. It must appear nowhere
% else in the paper -- including sections/preregistration.tex, which held it
% until 2026-07-26 -- and nowhere at all in the blog post. It is a motivating
% anecdote inside the honest-disclosure narrative, never an atlas statistic.
% THE BOUNDARY TRAVELS WITH THE ANECDOTE: if this paragraph is ever moved again,
% move this comment with it and update the pointer in preregistration.tex.
% =====================================================================

\section{Preregistration detail}
\label{app:prereg-detail}

This appendix holds the full text of three items summarised in
\S\ref{sec:prereg}: the disclosed pre-registration data contact, the seven
interpretive choices, and the spot-check narrative.

\subsection{Disclosed pre-registration data contact}
\label{app:prereg:contact}

Preregistration is a claim about ordering, so the places where our order was
imperfect are disclosed by the registrations themselves rather than discovered
by a reader.

% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md §1.
\textbf{Audit.} Five candidate claims were collected with exact quotes on
2026-07-15 during a feasibility sweep, before the registration was written
(GPTQ, LLM.int8(), and SmoothQuant abstracts; the Red~Hat AI W4A16 Llama-3.1-8B
model card; Meta's quantized-Llama blog). No power computation had been run on
any of them. They enter the pool through the same §3 criteria as
later-collected claims, and they are not treated as a separate stratum, because
the contact was with the \emph{quotes}, not with any verdict quantity.

% SOURCE: docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §1; the 99 probe cells
% are excluded per §6 and per docs/AUDIT_VERDICTS_2026-07-20.md ruling #6.
\textbf{Atlas.} Two feasibility probes were run on 2026-07-15 before the
registration was drafted, and their results were known: TheBloke/Llama-2-7B-GPTQ
against meta-llama/Llama-2-7b-hf on ARC-Challenge (74 flips of 1{,}170, net
$-1.03$\,pp), and a Neural~Magic Llama-3.1-8B baseline against its W4A16
quantization on \texttt{bbh\_boolean\_expressions} (17 flips of 250, net
$+1.2$\,pp). Those pairs are flagged in the atlas and excluded from every
headline aggregate; the exclusion covers all 99 cells belonging to the two probe
\emph{pairs}, not merely the two probe tasks (\S\ref{app:prereg:choices},
interpretive choice~6).

% SOURCE: docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §"Why this note exists".
% DISCLOSURE BOUNDARY: this paragraph is the ONLY place the 6.3% anecdote may
% appear in any FlipEval public-facing text. Never in the blog, never in the
% abstract, never in §\ref{sec:atlas}, never in §\ref{sec:prereg}.
\textbf{A retired anecdote.} The project's original motivating observation was a
feasibility rerun of a bnb-4bit checkpoint against its own repository's
full-precision weights, in which roughly 6.3\% of items flipped correctness while
the aggregate score was unchanged. That observation is what made the project
seem worth doing, and it is reported here for that reason. It is
\textbf{retired from every quantitative use}, on two independent grounds: it is
pre-registration data contact, and it lies outside the frozen 59-pair manifest,
since same-repository multi-precision runs are an amendment candidate that was
never acted upon. The registered replacement is the identical-score statistic of
\S\ref{sec:atlas:identical}, computed on the frozen atlas population: 145 of
1{,}707 cells (8.49\%) at a median churn of 7.20\%. Where an anecdote and a
registered statistic point the same way, the paper cites the statistic.
% REV-1 SURVIVOR FLAGGED 2026-07-26, RESOLVED 2026-07-26 on the author's ruling.
% All four figures in the preceding sentence were rev-1
% (results/identical_score_churn.csv: analysable_cells 1155, zero_delta_cells
% 113, zero_delta_share 0.097835, churn_median 0.062176) and are now rev-2
% (results/identical_score_churn_rev2.csv: 1707, 145, 0.084944, 0.072000).
% This passage cites the registered replacement statistic as CURRENT, not as
% history, so it must track rev-2 -- unlike \S\ref{sec:atlas:coverage}'s citation
% of the retracted 643, which is deliberate historical narration and stays.
% The abstract's and introduction's companion figure "a median of 6.2%" was the
% same rev-1 churn median and moved to 7.2% in the same commit; all three now
% state churn_median 0.072000 at their respective precisions.

\subsection{The interpretive choices that moved the headline}
\label{app:prereg:choices}

Frozen protocols do not eliminate analyst judgement; they make it visible and
datable. Seven passages of the audit registration were ambiguous enough to
require a ruling before verdicts could be computed. All seven were ruled on
2026-07-20, each is implemented in code, and each is reversible by re-running
with the alternative. Four matter for how the results should be read.

\paragraph{Choice 1: which margin is ``the applicable margin''---and the
$K = 1 \to 5 \to 4$ correction.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #1,
% including the "Methods-narrative note" paragraph; K values cross-checked
% against results/audit_verdicts.csv columns verdict and
% verdict_at_registered_2pp.
The frozen §4 names the 2\,pp registered margin first, adds ``(and at the
claim's own margin when it states one)'', and then labels the verdict
``underpowered for its own assertion'' \emph{at the applicable margin}. Two
readings survive that text. Judged against a uniform 2\,pp yardstick,
$K = 1$ of 12. Judged against each claim's own stated margin, with 2\,pp as the
fallback for claims that state none, $K = 5$---and $K = 4$ after choice~3 below.

The order in which those numbers arrived is the point, so we report it exactly.
\textbf{The first pass of this analysis returned $K = 1$}, by applying the 2\,pp
margin uniformly. Re-reading the frozen label---``underpowered for its
\emph{own} assertion''---produced \textbf{$K = 5$}: a source that asserts parity
within 0.15\,pp has made a 0.15\,pp claim, and judging it against a 2\,pp
yardstick audits a claim nobody made. Ruling on choice~3 then moved one claim
out of the determinate set, yielding the reported \textbf{$K = 4$}.

We draw a specific methodological conclusion from this sequence, and it is not
that the frozen text was perfect. It is that the correction ran \emph{against}
the direction the analyst's first instinct had gone. The first pass had already
produced a defensible, publishable, conservative number; the frozen text
required a larger one, and the frozen text governed. That is the evidence
available, from inside a solo-authored project, that the rule text drove the
analysis rather than the desired result. Had the correction run the other
way---first pass large, frozen text small---the same discipline would have
required reporting the small number, and this paragraph would say so. Both
readings are reported in the paper (\S\ref{sec:audit:results}) and shipped in
the released CSV, so a reader who prefers the uniform yardstick can have it.

\paragraph{Choice 2: what counts as the claim's own margin.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #2;
% results/audit_verdicts.csv columns claimed_margin_pp, margin_basis, and the
% R01 note in column `notes`.
Most claims cover several benchmarks with different deltas. We define the
claimed margin as \textbf{the largest $|\Delta|$ the source asserts is
negligible}. This is the reading most favourable to the source: it grants the
claim the widest margin its own sentence can bear, and therefore the smallest
required sample size. The harsher alternative---matching the delta to the
benchmark whose $n$ was actually used---would, for R01 alone (whose $n$ is
PIQA's 1{,}838 while its largest delta is ARC-Easy's), raise the MDD-to-margin
ratio by roughly $34\times$. We did not take it.

The principle generalises to the whole audit. Every ambiguity was resolved in
the source's favour: pairing rather than independent binomial variance for the
variance model (the paired assumption is the generous one, and
Table~\ref{tab:audit-mdd} shows the independent bound is uniformly worse); the
largest asserted delta as the margin; a claim's own margin rather than a uniform
one; and imputation by \emph{median} discordance from the most specific matching
atlas tier rather than by any upper quantile. \textbf{An audit that resolves
every ambiguity in the audited source's favour and still finds shortfalls of
$2$--$13\times$ is the armoured version of the finding.}

\paragraph{Choice 3: R04 is indeterminate rather than scored on a substituted
benchmark.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #3 and the
% R04 bullet in §Indeterminate; results/audit_verdicts.csv row R04.
Discussed in full at \S\ref{sec:audit:r04}. It is recorded here as a ruling
because it is the second correction that cost the paper a number: it removed
what the first pass had reported as the audit's largest shortfall ($38.3\times$)
and moved the headline from $K = 5, J = 4$ to $K = 4, J = 5$. The GSM8K
computation is retained in the released CSV as a labelled transparency column so
that the set-aside quantity is inspectable rather than deleted.

\paragraph{Choice 5: TOST uses the one-sided $z$.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #5;
% docs/CERTIFICATION_TABLES_2026-07-20.md §Method.
The project's own helper, \texttt{flipeval.required\_n\_for\_effect}, uses the
two-sided $z_{1-\alpha/2}$. That is correct for \emph{detection} and wrong for
TOST, which rejects two one-sided nulls at level $\alpha$ each. Reusing the
helper unchanged would have inflated every required $n$ in this paper by about
27\%---in the conservative direction, under the name ``TOST'', and with no
symptom visible in any output. It would have made every audit shortfall and
every certification count larger than the correct value. The TOST formula is
therefore implemented locally with the one-sided $z_{1-\alpha} = 1.6449$,
documented, and cross-checked against the project implementation on the
quantities the two share; the paired standard deviation is pinned against
\texttt{flipeval.core.minimum\_detectable\_difference} on synthetic delta vectors
in the test suite, so the audit cannot silently fork from the tested library.

\paragraph{The remaining three rulings, in brief.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #4, #6, #7.
Choice~4: verdicts are computed at claim level rather than
claim\,$\times$\,benchmark, because the frozen table stores one pooled $n$ per
claim and operating at a finer granularity would mean inventing rows the freeze
does not contain; every summed task is listed in the released
\texttt{n\_basis} column. Choice~6: ``the two probe-tagged cells'' is read as
two probe \emph{pairs}, comprising 99 cells, all excluded. Choice~7: degenerate
rows are handled per input rather than discarded whole, so an indeterminate
claim keeps the components its available inputs support, reported as
supplementary and never verdict-bearing.

\subsection{The spot-check found a selection bias in our own pipeline}
\label{app:prereg-spotcheck}
% SOURCE: docs/ATLAS_REV2_CORRECTION_2026-07-21.md; the spot-check report of
% 2026-07-21 (10 cells, 262/262 fields); ruling R7.

The protocol required an independent spot-check of the atlas pipeline before any
atlas number could be quoted externally. We report what it found, because the
finding is the paper's thesis applied to the paper.

The check re-downloaded the raw per-item files for ten cells, stratified across
both sources and across zero-delta, high-churn, McNemar-significant and excluded
strata, and recomputed the joins, pairing gates, flip counts, churn, net deltas
and exact McNemar $p$ values from a \emph{fresh reimplementation of the
registered definitions}---deliberately not a rerun of our own pipeline, since
rerunning the same code confirms determinism rather than correctness. All
262 compared fields reconciled exactly, including dyadic $p$ values reproduced
without \texttt{scipy}, and no upstream data drift was detected.

The arithmetic was right. The \emph{population} was not. Two defects surfaced.
First, our implementation omitted a clause of our own registration: when the
prompt-hash gate fails, the protocol requires trying earlier run combinations in
reverse-chronological order, and the code simply took the newest run and gave
up. Eleven pairs contributed zero cells as a result. Crucially, the loss was
\textbf{not random}: it removed exactly those pairs whose quantized side had
been re-evaluated later, a property correlated with a model being popular enough
to re-run. Second, a newer details schema nested its metrics one level deeper
than our parser looked, so 583 cells were recorded as having no binary
correctness metric when in fact they had one, and a sentence in our own results
note attributed that gap to the upstream leaderboard's reporting standards. We
retracted the sentence.

We draw three points from this, and none of them is that we were unlucky.

\textbf{An aggregate can be exactly right and still be built on the wrong
population.} Every cell we checked was computed correctly. Had we validated by
recomputing our own numbers---the natural, and useless, form of self-check---we
would have confirmed all of them and shipped the selection bias intact. What
caught it was reconstructing the measurement from the protocol text rather than
from the code.

\textbf{Preregistration did the work it is supposed to do.} The registration
text was frozen before any statistic existed, and it fully determined the
direction of the repair: we did not choose a rule that flattered a result, we
executed a rule that was already binding and had been under-implemented. That
is why the fix is a correction rather than a post-hoc adjustment, and it is why
we can say so without asking to be trusted. The correction was nevertheless made
\emph{after} results had been inspected, and we disclose that plainly rather
than presenting the repair as a pre-specified step.

\textbf{Both revisions are public.} We publish rev-1 and rev-2 and report the
delta between them, rather than replacing the record with its corrected version.
A field in which near-lossless claims cannot be rechecked because per-item
outputs are never released---the finding of Section~\ref{sec:audit}---is a field
whose corrections are invisible. Ours is not, and the difference is the point of
the artifact rather than an apology for it.

\subsection{The rev-1 to rev-2 delta}
\label{app:prereg:rev2delta}
% SOURCE: docs/ATLAS_REV2_CORRECTION_2026-07-21.md §8 "Rev-1 -> rev-2 delta
% record", all four sub-tables (Population; Headline descriptives per stratum;
% Audit verdicts; Certification tables). Rev-2 ran as embers job 11341992
% (exit 0, 59/59 pairs), downstream regeneration as job 11343383 (exit 0).
% \revtwoTODO CLOSED 2026-07-26: this subsection is the narrative the marker
% asked for. Its own note recorded that every input already existed in §8 and
% that it was not blocked on any pending result.

The repair recovered cells rather than removing them, and the recovery was
confined to S1. The enumerated population is unchanged at 2{,}055 pair-task
cells; analysed cells rise from 1{,}254 to \textbf{1{,}807}, and the
probe-excluded analysable population from 1{,}155 to \textbf{1{,}707}. All of
that movement is S1 (846 $\to$ 1{,}398); S2 is unchanged at 309 cells, which is
the expected control, since no S2 cell's eligibility was affected by either
defect. The reverse-chronological run fallback was exercised for 1{,}007 cells
across 19 pairs, recorded per cell with the accepted run timestamps.

The descriptives moved in the direction a recovered population predicts rather
than in the direction that would flatter the paper. S1 median churn rises
slightly (0.1327 $\to$ 0.1375) and S1 median $|$net delta$|$ rises
(0.0226 $\to$ 0.0263), while the share of S1 cells certifiable at 2\,pp
\emph{falls} from 5.6\% to 4.9\% and the share showing a detectable difference
rises sharply from 17.5\% to 26.5\%---the recovered pairs are larger-$n$ cells,
which resolve more differences. Every S2 field is identical across revisions.

\textbf{The headline verdicts did not move.} $K = 4$ of 12 determinate claims
underpowered for their own assertion and $J = 5$ indeterminate, identical to
rev-1 under the rev-2 discordance imputation, with the uniform-2\,pp secondary
reading unchanged at 1 of 12. No new verdict computation was triggered. In the
certification tables no family entered or left, and \texttt{bbh}, \texttt{gpqa},
\texttt{ifeval}, \texttt{math}, \texttt{mmlu\_pro} and \texttt{musr} are
unchanged in both cell count and required $n$; the families that moved are
\texttt{mmlu} (798 $\to$ 1{,}311 cells, required $n$ 2{,}123 $\to$ 2{,}164),
\texttt{gsm8k} (11 $\to$ 24, 750 $\to$ 1{,}184), \texttt{winogrande}
(15 $\to$ 23, 1{,}879 $\to$ 1{,}416), \texttt{arc\_challenge} (8 $\to$ 17,
1{,}211 $\to$ 1{,}218), \texttt{hellaswag} (14 $\to$ 23, 688 $\to$ 695) and the
pooled row (1{,}155 $\to$ 1{,}707, 1{,}739 $\to$ 1{,}855).

That the audit's headline survived a 44\% enlargement of the atlas population is
worth stating plainly, and it is also worth stating that we did not know it
would when the repair was authorised.
```

---

## FILE: `paper/sections/appendix_harness_detail.tex`

```latex
% =====================================================================
% Appendix: Harness-sensitivity detail
% -- Relocated from sections/harness_sensitivity.tex on 2026-07-26 as part of
%    the structural trim. NOTHING WAS DELETED IN THE MOVE: the "two live
%    defects" motivation and the design / pre-named-ratio subsection (including
%    the two-phase Qbar deferral and the declined early-inspection amendment)
%    appear here verbatim, with their % SOURCE comments.
%
% PRIMARY SOURCES for every number in this appendix:
%   docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md  (FROZEN protocol)
%   docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md       (results narrative)
%   docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md          (the denominator Qbar)
%   results/harness_sensitivity/sensitivity_results_qwen25-1p5b.json
%
% DISCIPLINE FOR THIS FILE (unchanged by the move):
%  - Exploratory study; it states NO H3 outcome and licenses no confirmatory read.
%  - The only confirmatory-derived quantity quoted is the committed denominator
%    Qbar (mean over the ten Qwen quantized variants). No per-variant / per-cell
%    confirmatory accuracy or churn is quoted -- see the Qbar artifact only.
%  - R is never printed without C_cond and Qbar beside it (registration §5.1).
% =====================================================================

\section{Harness-sensitivity detail}
\label{app:harness-detail}

This appendix holds the motivation and the design of the configuration-sensitivity
study of \S\ref{sec:sensitivity}, whose two result tables remain in the main text.

\subsection{Two live defects, not a hypothetical}
\label{app:sensitivity:motivation}

The motivation is on the record: this campaign produced two configuration
effects inside eight days, both on the pinned \texttt{lm\_eval}~0.4.12.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §1.

First, \texttt{fewshot\_as\_multiturn} was auto-enabled under a chat template
with no flag set: the harness turns it on whenever \texttt{apply\_chat\_template}
is set (\texttt{lm\_eval/config/evaluate\_config.py:306--308}), moving every
few-shot exemplar out of the user message into its own conversation turn.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §1 item 1;
% docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md Amendment 1.
Second, and starker, the stock \texttt{gsm8k} task ships two extraction filters,
\texttt{strict-match} and \texttt{flexible-extract}, and scores the \emph{same}
generations under both. On Qwen2.5-1.5B, \texttt{strict-match} voided
\textbf{617 of 1{,}000} responses, \textbf{336} of which \texttt{pilot\_eval}'s
extractor scores correct, because the model writes \texttt{\#\#\#\# \$18} and the
strict regex rejects the \texttt{\$}. Reported accuracy moved
\textbf{$0.232 \to 0.566$} with not one token of the model's output changed.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §1 item 2;
% docs/MINIGRID_FP16_GATE_RECORD_2026-07-21.md §4.2 (617/1000, 336 correct,
% #### $18, 0.232 -> 0.566).
If a scoring switch on unchanged generations can move aggregate accuracy by a
third of the scale, the size of that effect \emph{relative to} quantization is an
empirical quantity worth measuring rather than asserting.

\subsection{Design and the pre-named ratio}
\label{app:sensitivity:design}

% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §§3-4.
The study varies one native \texttt{lm\_eval} knob at a time from a fixed
reference---chat template on, three inline GSM8K exemplars (zero-shot for MMLU),
\texttt{flexible-extract} scoring---which is the configuration the mini-grid's
own reference runs use. All runs are FP16-only, on the bridge item subsets
exclusively: the four bridge MMLU subjects at 100 items each ($n=400$) and GSM8K
test indices 0--199 ($n=200$). No quantized checkpoint is loaded under this
protocol, and the full mini-grid item definitions are never evaluated, so no
confirmatory surface is touched.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §2 (FP16 only),
% §4 (bridge subsets n=400/200; exclusion of the mini-grid item definitions).

The headline statistic is fixed before any run:
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.1.
\begin{equation}
R_{\mathrm{cond}} \;=\; \frac{C_{\mathrm{cond}}}{\bar{Q}},
\label{eq:sensitivity-R}
\end{equation}
where the numerator $C_{\mathrm{cond}}$ is the correctness-state churn between
the reference and a condition---the fraction of items whose correct/incorrect
state changes, the same churn definition the atlas uses
(\S\ref{sec:atlas})---on the FP16 model over the item set above, and the
denominator $\bar{Q}$ is the mean, over the ten Qwen2.5-1.5B quantized variants
$\{\mathrm{gptq}_{s0\ldots s4},\ \mathrm{awq}_{s0\ldots s4}\}$, of
correctness-state churn against that model's FP16 cell on the \emph{same} item
subset, per task. Both terms are reported beside every $R$; the registration
forbids printing the ratio without its inputs, and if $\bar{Q}=0$ the ratio is
undefined rather than infinite.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.1 (numerator,
% denominator, "C_cond and Qbar always reported beside it", undefined-if-zero rule).

The two denominators are
$\bar{Q}(\text{MMLU})=\mathbf{0.199}$ and
$\bar{Q}(\text{GSM8K})=\mathbf{0.287}$; neither is zero, so no undefined case
arises.
% SOURCE: docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md (Qbar(mmlu)=0.199000,
% Qbar(gsm8k)=0.287000); results/harness_sensitivity/qbar_qwen25-1p5b.json.
Their provenance is deliberate. Under the registration's two-phase design the
numerators run immediately on freeze, but $\bar{Q}$ is computed \emph{only} from
mini-grid results after the registered validator passed over the complete
44-JSONL set (409/409 checks) and the first accuracy inspection that
\texttt{MINIGRID\_REGISTRATION} \S5 permits had been authorized---so the
denominator is not an early look at the confirmatory grid under another name.
% SOURCE: docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md (validator 11375247,
% 409/409, first inspection authorized 2026-07-23);
% docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.2 (two-phase deferral).
A shortcut that would have produced the ratio roughly five weeks earlier---a
dated amendment permitting an early partial inspection of the bridge quantized
deltas---was considered and declined, on the ground that the registered
blindness is not weakened to obtain a number sooner.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §9.1
% (option considered and declined by Amogh 2026-07-22).

\subsection{Condition B in full: the scoring rule alone exceeds the quantization effect}
\label{app:sensitivity:condB}

Condition~B is the sharpest result and deserves isolating, because it holds the
generations fixed. It costs zero GPU time: the stock \texttt{gsm8k} task applies
both \texttt{strict-match} and \texttt{flexible-extract} to the same outputs in a
single run, so B is read out of the reference run's own samples file---a genuine
rescore of \emph{identical} generations, not a second pass.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §3.1 (B is a filter
% rescore of REF, zero GPU); docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md
% (B derived from REF samples).
Its correctness churn is therefore the pure effect of the extraction filter:
$C_B = 0.455$ ($91$ of $200$ items), with a directional split of
$\textbf{91}/\textbf{0}$---every changed item went correct$\to$incorrect, so the
$0.455$ accuracy drop equals the churn exactly and \texttt{strict-match} accepts
a strict subset of what \texttt{flexible-extract} accepts here. The resulting
$R_B = 0.455/0.287 = \textbf{1.585}$: on these items, choosing one of two
built-in scoring filters that ship with the same task moves the fixed model's
per-item correctness \emph{more than half again as much} as quantization does.
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, GSM8K row B (C_cond
% 0.4550, 91/200, dir 91/0, R 1.585); results JSON per_task.gsm8k.conditions.B_strict_match.
No compression method in the comparison set produces a swing of that kind from a
choice a practitioner never records.

\subsection{Why MMLU collapses to a single off-reference cell}
\label{app:sensitivity:mmlu-collapse}

% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §3.3 (C == D for
% MMLU); docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, MMLU table.
MMLU is zero-shot with no extraction filter, so conditions~A and~B do not apply;
its stock \texttt{num\_fewshot} resolves to $0$ and it ships no
\texttt{filter\_list}, so stock defaults and the reference differ in
\emph{nothing but the chat template}. Conditions~C (chat off) and~D (stock
defaults) are then byte-identical configurations, and inventing a distinct~D
would mean measuring a configuration no user runs. The registration ruled it be
run once and reported as ``$C \equiv D$''.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §3.3 (num_fewshot
% resolves to 0, no filter_list, C and D byte-identical, ruled "run once, report
% as C == D").
```

---

## FILE: `paper/sections/appendix_artifacts_detail.tex`

```latex
% =====================================================================
% Appendix: Artifact detail (datasheet, metadata, maintenance)
% -- Relocated from sections/artifacts.tex on 2026-07-26 as part of the
%    structural trim. NOTHING WAS DELETED IN THE MOVE: the datasheet,
%    metadata/identifiers and maintenance TODOs appear here verbatim, with
%    their % SOURCE comments.
%
% D&B hygiene. Required in full if NeurIPS Datasets & Benchmarks is the target
% venue; for COLM/ACL the main text keeps one paragraph (sections/artifacts.tex)
% and the detail lives here.
% No URL, DOI, or version number may be written here until it exists.
% =====================================================================

\section{Artifact detail}
\label{app:artifacts-detail}

\subsection{Datasheet}
\label{app:artifacts:datasheet}

\TODO{full datasheet in the \citet{gebru2021datasheets} format. Items already
known and required to appear: S1's Open LLM Leaderboard v1 archive carries
\emph{no declared license}, recorded as a limitation; S2 is Apache-2.0; the
atlas contains no human-subject data and no personally identifying information;
the population is the public record of compression evaluation and not a census
of quantization (\S\ref{sec:atlas:caveats}).}
% SOURCE for the S1 license limitation:
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.

\subsection{Metadata and identifiers}
\label{app:artifacts:metadata}

\TODO{Croissant metadata record; Zenodo DOI; versioning scheme; citation block}

\subsection{Maintenance}
\label{app:artifacts:maintenance}

\TODO{12-month maintenance statement: issue tracker, response commitment,
versioned releases, and the policy for adding atlas pairs (a dated amendment to
the atlas registration, not a silent extension).}
```

---

## Reader's index

Sections in reading order (numbered as the compiled paper numbers them; front matter and appendix marked).

| # | Section | File |
|---|---|---|

| — | Abstract | `paper/abstract.tex` |

| 1 | Introduction | `paper/sections/introduction.tex` |

| 2 | Related work and positioning | `paper/sections/related_work.tex` |

| 3 | Preregistration, freezes, and analyst degrees of freedom | `paper/sections/preregistration.tex` |

| 4 | An audit of published near-lossless claims | `paper/sections/audit.tex` |

| 5 | Certification tables: how many items an equivalence claim needs | `paper/sections/certification.tex` |

| 6 | An atlas of the public record of compression evaluation | `paper/sections/atlas.tex` |

| 7 | Does the calibration seed reorder compression methods? | `paper/sections/minigrid.tex` |

| ↳ | (subsection) The mechanical escalation screen | `paper/sections/minigrid_escalation.tex` |

| 8 | How much does the harness move the score? A configuration-sensitivity study | `paper/sections/harness_sensitivity.tex` |

| 9 | Discriminant validity: the framework does not call everything noise | `paper/sections/discriminant.tex` |

| 10 | Artifacts | `paper/sections/artifacts.tex` |

| 11 | Limitations | `paper/sections/limitations.tex` |

| 12 | Conclusion: a reporting standard for compression claims | `paper/sections/conclusion.tex` |

| App. | Full audit table | `paper/sections/appendix_audit_table.tex` |

| App. | Preregistration detail | `paper/sections/appendix_prereg_detail.tex` |

| App. | Harness-sensitivity detail | `paper/sections/appendix_harness_detail.tex` |

| App. | Artifact detail | `paper/sections/appendix_artifacts_detail.tex` |

