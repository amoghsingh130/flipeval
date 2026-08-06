# FlipEval — Paper Reading Copy

**Generated 2026-08-06T05:20:44Z from `paper/main.tex` at commit `48e77b1`.**

No PDF: the Phoenix login node has no `pdflatex`, `xelatex`, `lualatex`, `latexmk`, `tectonic` or `pandoc`, and the pinned Apptainer image is an ML runtime with no TeX distribution. Per the fallback, the sections are concatenated **verbatim, in `main.tex` input order** (nested `\input` expanded in place), with no content edits. LaTeX markup is left as-is deliberately: substituting rendered text would be an edit.

A reader's index is at the end.


---

## FILE: `paper/audit_denominators.tex`

```latex
% audit_denominators.tex -- GENERATED, DO NOT EDIT BY HAND.
% Regenerate: python3 paper/tools/gen_denominator_macros.py --write
% Validate:   python3 paper/tools/gen_denominator_macros.py --check
%
% Source: results/audit_verdicts_rev3.csv (sealed 0444, single run, job 11591245)
% sha256: c85d6f8a5a25023389b27201a4165b79fbfdc6f274b89ca91e64182ab150082b
% Identity cross-checked against docs/audit_claim_table.csv (FROZEN).
% Margin: uniform 2 pp, registered. Planning size increasing in d, so the
% Q1 and Q3 columns bracket the whole atlas-IQR interval by monotonicity.
%
% Denominators. `Eligible` passes the frozen 3.1 inclusion rule;
% `Assessable` is eligible AND determinate and is the denominator of every
% threshold count.

\newcommand{\AuditFrozenCandidates}{17}
\newcommand{\AuditIneligible}{1}
\newcommand{\AuditEligible}{16}
\newcommand{\AuditAssessable}{11}
\newcommand{\AuditNotAssessable}{5}
\newcommand{\AuditNotAssessableInsufficient}{4}
\newcommand{\AuditNotAssessableOutsideFramework}{1}

% Threshold and sensitivity counts, all out of \AuditAssessable.
\newcommand{\AuditBelowThresholdAtMedian}{1}
\newcommand{\AuditAboveThroughout}{10}
\newcommand{\AuditChangesWithinIQR}{1}
\newcommand{\AuditBelowThroughout}{0}

% Per-item outputs, out of \AuditEligible. `TaskMatched` is outputs for the
% tasks that support the audited claim; `OtherTaskOnly` is a release that
% does not cover them.
\newcommand{\AuditPerItemTaskMatched}{0}
\newcommand{\AuditPerItemOtherTaskOnly}{3}
\newcommand{\AuditPerItemNone}{13}
\newcommand{\AuditPerItemOtherTaskClaims}{R08, R15, R16}

% Margin cross-tab, over the 16 eligible sources, reconciling the margin
% taxonomy with the statement that ten of sixteen contain no number at all.
% Rows: registered margin category. 1 = a prospective numerical decision
% margin is declared; 2 = equivalence asserted with sufficient numerical
% information to evaluate it; 3 = asserted without sufficient numerical
% information. Columns: descriptive evidence form. Qual = qualitative
% language only, no number anywhere in the qualifying claim; Retro = a
% retrospective numerical description of an observed result.
% \AuditXtabSufficientTotal is the 11 assessable sources plus R04, which
% reports enough numbers but scores a generation metric. It is NOT the
% withdrawn rev-2 count of twelve determinate claims, which was a
% different set of the same size.
\newcommand{\AuditXtabProspectiveQual}{0}
\newcommand{\AuditXtabProspectiveRetro}{0}
\newcommand{\AuditXtabProspectiveTotal}{0}
\newcommand{\AuditXtabSufficientQual}{7}
\newcommand{\AuditXtabSufficientRetro}{5}
\newcommand{\AuditXtabSufficientTotal}{12}
\newcommand{\AuditXtabInsufficientQual}{3}
\newcommand{\AuditXtabInsufficientRetro}{1}
\newcommand{\AuditXtabInsufficientTotal}{4}
\newcommand{\AuditXtabQualTotal}{10}
\newcommand{\AuditXtabRetroTotal}{6}
\newcommand{\AuditXtabGrandTotal}{16}
\newcommand{\AuditProspectiveNumericMargin}{0}

% Named claims and the registered margin.
\newcommand{\AuditMarginPP}{2}
\newcommand{\AuditIneligibleClaim}{R10}
\newcommand{\AuditOutsideFrameworkClaim}{R04}

% The single imputation-sensitive claim. The percentage is a descriptive
% fraction of correlated reference cells: not a probability, not a
% confidence level, not a p-value.
\newcommand{\AuditSensitiveClaim}{R01}
\newcommand{\AuditSensitiveN}{1{,}838}
\newcommand{\AuditSensitiveNReq}{2{,}010}
\newcommand{\AuditSensitiveReversalD}{0.118915}
\newcommand{\AuditSensitiveCellsBelow}{345}
\newcommand{\AuditSensitiveCellsTotal}{792}
\newcommand{\AuditSensitiveCellsPct}{43.6}

% Provenance of the numbers above.
\newcommand{\AuditVerdictsSha}{c85d6f8a5a25023389b27201a4165b79fbfdc6f274b89ca91e64182ab150082b}
\newcommand{\AuditVerdictsShaShort}{c85d6f8a\ldots{}b150082b}

% Per-claim values, addressed as \AuditVal{R01}{nreqMed}. Fields for an
% assessable claim: n, tier, nreqQOne, nreqMed, nreqQThree, dstar, cls.
% Fields for a non-assessable or ineligible claim: n, tier, kind, blocker.
% An undefined pair expands to nothing, so asking an ineligible claim for
% its classification silently yields empty; ask for `kind` instead.
\newcommand{\AuditVal}[2]{\csname AuditData#1#2\endcsname}
\expandafter\def\csname AuditDataR01cls\endcsname{changes classification within IQR}
\expandafter\def\csname AuditDataR01dstar\endcsname{0.118915}
\expandafter\def\csname AuditDataR01n\endcsname{1{,}838}
\expandafter\def\csname AuditDataR01nreqMed\endcsname{2{,}010}
\expandafter\def\csname AuditDataR01nreqQOne\endcsname{1{,}364}
\expandafter\def\csname AuditDataR01nreqQThree\endcsname{4{,}328}
\expandafter\def\csname AuditDataR01tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR02blocker\endcsname{no reported or imputable n, no baseline, no numeric delta}
\expandafter\def\csname AuditDataR02kind\endcsname{insufficient reporting}
\expandafter\def\csname AuditDataR02n\endcsname{---}
\expandafter\def\csname AuditDataR02tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR03cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR03dstar\endcsname{---}
\expandafter\def\csname AuditDataR03n\endcsname{18{,}300}
\expandafter\def\csname AuditDataR03nreqMed\endcsname{866}
\expandafter\def\csname AuditDataR03nreqQOne\endcsname{619}
\expandafter\def\csname AuditDataR03nreqQThree\endcsname{1{,}237}
\expandafter\def\csname AuditDataR03tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR04blocker\endcsname{qualifying quote asserts negligible loss on COCO CIDEr, a generation metric with no per-item correct/incorrect state; V1/V2 are flip-model quantities that do not apply to it}
\expandafter\def\csname AuditDataR04kind\endcsname{metric-incompatible}
\expandafter\def\csname AuditDataR04n\endcsname{1{,}319}
\expandafter\def\csname AuditDataR04tier\endcsname{family+bits+benchmark}
\expandafter\def\csname AuditDataR05cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR05dstar\endcsname{0.908491}
\expandafter\def\csname AuditDataR05n\endcsname{14{,}042}
\expandafter\def\csname AuditDataR05nreqMed\endcsname{2{,}255}
\expandafter\def\csname AuditDataR05nreqQOne\endcsname{1{,}525}
\expandafter\def\csname AuditDataR05nreqQThree\endcsname{3{,}865}
\expandafter\def\csname AuditDataR05tier\endcsname{bits+benchmark}
\expandafter\def\csname AuditDataR06cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR06dstar\endcsname{---}
\expandafter\def\csname AuditDataR06n\endcsname{18{,}904}
\expandafter\def\csname AuditDataR06nreqMed\endcsname{1{,}841}
\expandafter\def\csname AuditDataR06nreqQOne\endcsname{932}
\expandafter\def\csname AuditDataR06nreqQThree\endcsname{6{,}046}
\expandafter\def\csname AuditDataR06tier\endcsname{bits}
\expandafter\def\csname AuditDataR07cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR07dstar\endcsname{0.802904}
\expandafter\def\csname AuditDataR07n\endcsname{12{,}410}
\expandafter\def\csname AuditDataR07nreqMed\endcsname{1{,}841}
\expandafter\def\csname AuditDataR07nreqQOne\endcsname{932}
\expandafter\def\csname AuditDataR07nreqQThree\endcsname{6{,}046}
\expandafter\def\csname AuditDataR07tier\endcsname{bits}
\expandafter\def\csname AuditDataR08cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR08dstar\endcsname{---}
\expandafter\def\csname AuditDataR08n\endcsname{42{,}701}
\expandafter\def\csname AuditDataR08nreqMed\endcsname{742}
\expandafter\def\csname AuditDataR08nreqQOne\endcsname{371}
\expandafter\def\csname AuditDataR08nreqQThree\endcsname{1{,}052}
\expandafter\def\csname AuditDataR08tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR09cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR09dstar\endcsname{---}
\expandafter\def\csname AuditDataR09n\endcsname{42{,}701}
\expandafter\def\csname AuditDataR09nreqMed\endcsname{742}
\expandafter\def\csname AuditDataR09nreqQOne\endcsname{433}
\expandafter\def\csname AuditDataR09nreqQThree\endcsname{1{,}113}
\expandafter\def\csname AuditDataR09tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR10blocker\endcsname{quoted claim appears in neither prose nor a table caption (\S{}3.1): the recorded exact\_quote appears nowhere in the source; 98.6\% is a table cell}
\expandafter\def\csname AuditDataR10kind\endcsname{ineligible}
\expandafter\def\csname AuditDataR10n\endcsname{28{,}659}
\expandafter\def\csname AuditDataR10tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR11blocker\endcsname{no reported or imputable n, no baseline, no numeric delta}
\expandafter\def\csname AuditDataR11kind\endcsname{insufficient reporting}
\expandafter\def\csname AuditDataR11n\endcsname{---}
\expandafter\def\csname AuditDataR11tier\endcsname{bits}
\expandafter\def\csname AuditDataR12cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR12dstar\endcsname{0.908491}
\expandafter\def\csname AuditDataR12n\endcsname{14{,}042}
\expandafter\def\csname AuditDataR12nreqMed\endcsname{742}
\expandafter\def\csname AuditDataR12nreqQOne\endcsname{433}
\expandafter\def\csname AuditDataR12nreqQThree\endcsname{1{,}113}
\expandafter\def\csname AuditDataR12tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR13blocker\endcsname{no on-page baseline accuracy and no computable delta}
\expandafter\def\csname AuditDataR13kind\endcsname{insufficient reporting}
\expandafter\def\csname AuditDataR13n\endcsname{250}
\expandafter\def\csname AuditDataR13tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR14blocker\endcsname{no baseline accuracy stated (Figure 8 chart only)}
\expandafter\def\csname AuditDataR14kind\endcsname{insufficient reporting}
\expandafter\def\csname AuditDataR14n\endcsname{728}
\expandafter\def\csname AuditDataR14tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR15cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR15dstar\endcsname{---}
\expandafter\def\csname AuditDataR15n\endcsname{42{,}701}
\expandafter\def\csname AuditDataR15nreqMed\endcsname{866}
\expandafter\def\csname AuditDataR15nreqQOne\endcsname{619}
\expandafter\def\csname AuditDataR15nreqQThree\endcsname{1{,}237}
\expandafter\def\csname AuditDataR15tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR16cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR16dstar\endcsname{---}
\expandafter\def\csname AuditDataR16n\endcsname{42{,}701}
\expandafter\def\csname AuditDataR16nreqMed\endcsname{742}
\expandafter\def\csname AuditDataR16nreqQOne\endcsname{371}
\expandafter\def\csname AuditDataR16nreqQThree\endcsname{1{,}052}
\expandafter\def\csname AuditDataR16tier\endcsname{family+bits}
\expandafter\def\csname AuditDataR17cls\endcsname{above throughout}
\expandafter\def\csname AuditDataR17dstar\endcsname{---}
\expandafter\def\csname AuditDataR17n\endcsname{28{,}659}
\expandafter\def\csname AuditDataR17nreqMed\endcsname{2{,}081}
\expandafter\def\csname AuditDataR17nreqQOne\endcsname{1{,}332}
\expandafter\def\csname AuditDataR17nreqQThree\endcsname{3{,}644}
\expandafter\def\csname AuditDataR17tier\endcsname{bits+benchmark}
```

---

## FILE: `paper/abstract.tex`

```latex
% Atlas figures below are REV-2 (2026-07-21). Keep in sync with
% sections/{atlas,certification,audit,minigrid}.tex.
%
% SUMMARY-RESTATEMENT INVARIANT (paper/OUTLINE.md rule 4): this file contains no
% primary figures. Every number here appears in the section it summarises at
% coarser or equal precision.
%
% REWRITTEN 2026-08-05 (flagship narrative pass, docs/FLAGSHIP_NARRATIVE_PLAN.md
% §1). The abstract now performs the paper's five linked steps in order:
%   (a) the cancellation mechanism in plain language;
%   (b) atlas-scale evidence that it is not isolated;
%   (c) the reporting gap the audit found;
%   (d) paired certification as the instrument that closes it;
%   (e) the controlled consequence for method choice;
%   (f) the reporting standard, and the comparisons it covers beyond compression.
% It no longer OPENS on an audit count. That ordering read as a paper about
% other people's arithmetic; the mechanism is the contribution and the audit is
% the evidence that the field has no reporting convention for it.
%
% Carried forward from the 2026-07-31 rewrite, still binding:
%  - NO boldface. Six bolded spans once competed for emphasis here.
%  - Every audit count is an \Audit* macro from paper/audit_denominators.tex.
%    None is typed. The retired 4-of-12 and 5-of-17 headlines outlived the
%    verdicts that produced them, which is why the rule exists.
%  - "task-matched" stays in the SAME SENTENCE as the zero release count:
%    \AuditPerItemOtherTaskOnly{} sources do release per-item outputs, for other
%    task suites, so dropping the qualifier makes the sentence false.
%  - "no claim is called false" is retained verbatim.
%  - "The calibration seed alone reorders" stays replaced by what was observed.
%
% DROPPED HERE 2026-08-05, and where each survives:
%  - The $12.7\times$ controlled churn ratio. It has three homes left
%    (introduction, sections/minigrid.tex Result 1, conclusion) and did not fit
%    the character budget alongside step (f). Restore it in the mini-grid
%    sentence if a real measurement shows room.
%  - The \AuditAboveThroughout/\AuditChangesWithinIQR/\AuditBelowThroughout
%    sensitivity split. It is a §4 result with its own table; leading a reader
%    into the threshold arithmetic before the mechanism inverts the argument.
%  - "3B--405B" was WRONG, not dropped: 60 atlas cells sit on a 1.3B base model,
%    so the floor is 1.3B (docs/FLAGSHIP_NARRATIVE_PLAN.md D2).
%
% ARXIV ABSTRACT FIELD: the limit is 1,920 characters, confirmed from
% https://info.arxiv.org/help/prep.html. MEASURE, never eyeball -- see the
% measurement note at the end of this file.

\begin{abstract}
A fraction of a point of benchmark accuracy is the usual evidence that a
compressed model is equivalent to its original. That quantity is least
informative when two models are most alike: a net delta is what survives
cancellation between opposing per-item changes, and cancellation is most
complete in the regime equivalence claims occupy.

% SOURCE: \S\ref{sec:atlas:netgross}; \S\ref{sec:atlas:identical}.
% D4 CLOSED 2026-08-05 (docs/HEADLINE_CHURN_RATIO_DEFINITION.md). The
% $5.3\times$ headline is RETIRED: no unrounded derivation produces it. The
% aggregation is now named (ratio of medians) and the technical statement lives
% in \S\ref{sec:atlas:netgross}; the abstract and conclusion hedge to "roughly
% five times", which every candidate in the 5.19 to 5.45 band supports. The
% earlier note here said 5.3x was public in the Zenodo release and the blog: it
% is not. The blog already says "roughly five times" and the Zenodo v1.0 release
% asserts no ratio at all, shipping only the raw per-cell CSVs.
Across an atlas of 1{,}707 paired model-by-task cells mined from public
per-item evaluation dumps (1.3B--405B), churn runs roughly five times the net
accuracy delta, and cells scoring identically to their baseline still disagree
on individual items.

% SOURCE: \S\ref{sec:audit:taxonomy}; \S\ref{sec:audit:v3};
% \S\ref{sec:audit:results}; \S\ref{sec:audit:indeterminate}.
% AUDIT_REGISTRATION Amendment 2 (signed) retires "the margin they assert": no
% source asserts one. The claim here is about what is reported, not about what
% is true.
In a preregistered audit of \AuditFrozenCandidates{} equivalence claims from
three registered frames (method papers, model cards, vendor documentation),
\AuditEligible{} are eligible. None states a prospective numerical equivalence
margin, and none releases \emph{task-matched} per-item outputs, though
\AuditPerItemOtherTaskOnly{} release outputs for other tasks only;
\AuditNotAssessable{} report too little to assess numerically, so a reader
cannot check them at any sample size. We audit evidential sufficiency, not
truth: no claim is called false.

% SOURCE: \S\ref{sec:certification}; \S\ref{sec:minigrid:verdict};
% docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED).
% "Was sufficient to reverse", not "the seed reorders": the observed statement,
% not a sufficiency claim about a single factor.
We supply the missing instrument: paired equivalence testing at a declared
margin, with certification tables giving the items an evaluation needs,
computed from disagreement observed under compression, not from
independent-binomial variance. A controlled experiment pairs GPTQ and AWQ on
byte-identical calibration samples across five seeds. Under the frozen
eight-cell decision rule H3 is supported: changing the calibration draw was
sufficient to reverse the observed method ordering in 5 of 8 confirmatory
cells.

% SOURCE: \S\ref{sec:conclusion}, the five numbered lines.
{\sloppy
The reporting standard we propose is five lines: declare a margin, run the
paired test, report churn beside net delta, cite the sample size you met,
release per-item outputs. It applies to any comparison between two models alike
enough to be worth comparing. All per-item outputs, protocols and code are
released.\par}
\end{abstract}

% =====================================================================
% MEASUREMENT NOTE. The ARXIV ABSTRACT FIELD header above promises a
% "measurement note at the end of this file".
%
%   cd paper && python3 tools/measure_abstract.py abstract.tex
%
% Last MEASURED 2026-08-05, after the D4 ratio change:
%   ABSTRACT_CHARS 1879 / 1920  margin=41  words=283
% The D4 change ("5.3x" -> "roughly five times") cost 15 characters. An earlier
% draft of it also added "per-item" here and took the margin to 32, under the
% 40-character floor this note warns about; "per-item" was dropped again.
% Before D4 this measured 1864 / 1920, margin 56, 281 words.
% The 2026-08-05 rewrite was budgeted by hand at "roughly 1,860, margin near 60"
% by a session with no shell; the measurement confirms that estimate. The
% previous measurement was 2026-08-02, rev-3 narrative pass: 1,903 / 1,920,
% margin 17, 281 words.
%
% THE 56-CHARACTER MARGIN IS A LIVE DECISION, NOT SPARE ROOM. The
% $12.7\times$ controlled churn ratio is the first thing to restore if it is
% spent, in the mini-grid sentence. It is left out for now because 56 characters
% is the whole safety margin against a field that truncates silently, and
% $12.7\times$ still has three homes (introduction, mini-grid Result 1,
% conclusion).
%
% MEASURE AFTER EVERY EDIT -- the margin has been under 40 characters three
% times now, and the arXiv field truncates silently.
%
% The audit counts above are \Audit* macros from paper/audit_denominators.tex,
% NOT typed digits. measure_abstract.py expands them before counting; without
% that step every macro would have counted as zero characters and the
% measurement would have read ~30 characters short. Do not "simplify" the
% expander out of the tool, and do not replace a macro here with its value.
% =====================================================================
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

% REWRITTEN 2026-08-05 (flagship narrative pass,
% docs/FLAGSHIP_NARRATIVE_PLAN.md §§1, 4). Seven paragraphs, one per step of the
% argument: the claim and its statistical form; the cancellation mechanism,
% carried by Figure~\ref{fig:cancellation}; the atlas, which shows the mechanism
% is not isolated; the audit, which shows the field has no reporting convention
% for it; the controlled consequence for method choice; the instrument that
% closes the gap, with credit and positioning; and what the rest of the paper
% contains.
%
% Carried forward from the 2026-07-31 rewrite, still binding:
%  - No \paragraph{} labels. They made every paragraph read as an item in a
%    generated executive summary.
%  - Secondary numbers are cross-referenced, not restated. Each headline keeps
%    its three principal appearances (abstract, result section, conclusion).
%  - Field-wide language is scoped to the registered sampling frames.
%  - "The calibration seed alone reorders" stays replaced by what was observed.
%  - One \textbf{} span in the file, on the single headline quantity.
% This file remains DERIVATIVE: no primary figures originate here.

Compressed language models are frequently released with a sentence of the form
``negligible degradation'' or ``$99.x\%$ recovery'', supported by a difference of
a fraction of a point in aggregate accuracy on a fixed benchmark. That sentence
is an equivalence claim. Equivalence claims have a statistical form: a declared
margin, a test, and a sample size sufficient to reject the composite null that
the difference exceeds the margin. In the sources we audit, that form is almost
never present.

% SOURCE: Figure~\ref{fig:cancellation} and paper/figures/fig1_values.json, from
% the registered Qwen2.5-7B/GSM8K cell. Percentages are quoted here one digit
% coarser than the figure (9.12 -> 9.1, 8.54 -> 8.5), which the
% summary-restatement invariant permits; 0.58, 2,730 and 1,000 are exact.
% PANEL C WORDING IS LOAD-BEARING: 2,730 is a planning requirement computed at
% an assumed true difference of zero. It says the evaluation cannot support the
% claim. It is NOT evidence that the two methods differ, and no sentence here
% may imply that it is.
The missing test is the smaller half of the problem. A net accuracy delta is the
residue left after per-item changes in opposite directions cancel, so the
evidence is weakest exactly where it is offered: the more alike two models are,
the more completely their disagreements cancel.
Figure~\ref{fig:cancellation} shows one cell of our controlled experiment doing
this. Two 4-bit quantizations of the same model, GPTQ and AWQ, scored on the
same $1{,}000$ GSM8K items, land $0.58$ points apart. Underneath that gap,
$9.1\%$ of items go from correct to wrong and $8.5\%$ from wrong to correct, so
the reported difference is what is left of two large opposing quantities.
Certifying equivalence at a declared $\pm 2$-point margin at that disagreement
rate needs $2{,}730$ items, nearly three times the number run; that is a
planning requirement, and it says the evaluation cannot support the claim, not
that the two methods differ. The sign of the gap changes with the calibration
draw alone. The cell is the most extreme of the eight registered cells and is
shown because it is legible; all eight appear in panel~D.

\input{figures/fig1_cancellation}

% SOURCE: \S\ref{sec:atlas:netgross}; \S\ref{sec:atlas:identical};
% results/identical_score_churn_rev2.csv.
% D2 CORRECTION 2026-08-05: this read "3B to 405B". Sixty analysis cells sit on
% EleutherAI/gpt-neo-1.3B, so the floor is 1.3B, not 3B
% (docs/FLAGSHIP_NARRATIVE_PLAN.md §2 D2).
% D4 CLOSED 2026-08-05 (docs/HEADLINE_CHURN_RATIO_DEFINITION.md). The
% $5.3\times$ headline is RETIRED: no unrounded derivation produces it. The
% aggregation is now named (ratio of medians) and the technical statement lives
% in \S\ref{sec:atlas:netgross}; the abstract and conclusion hedge to "roughly
% five times", which every candidate in the 5.19 to 5.45 band supports. The
% earlier note here said 5.3x was public in the Zenodo release and the blog: it
% is not. The blog already says "roughly five times" and the Zenodo v1.0 release
% asserts no ratio at all, shipping only the raw per-cell CSVs.
One cell settles nothing about the field, so we measured the public record. An
atlas of $1{,}707$ paired model-by-task cells, mined from published per-item
evaluation dumps spanning 1.3B to 405B parameters, puts per-item churn at
roughly five times the net delta, and a substantial minority of its cells post
an accuracy identical to their baseline while still disagreeing on individual
items
(\S\ref{sec:atlas:identical}). Its two strata sit a generation apart in method
and give nearly the same ratio. The atlas is observational: it describes the
evidence the field circulates and supports no causal claim about quantization in
general.

% SOURCE: results/audit_verdicts_rev3.csv; \S\ref{sec:audit:taxonomy} and
% \S\ref{sec:audit:results}.
% Every count in this paragraph is a macro from paper/audit_denominators.tex.
% Do not type one back in: candidates, eligible, not-assessable, assessable and
% the above/changes/below sensitivity split all come from the sealed rev-3
% verdict CSV.
% THE SENSITIVITY SPLIT IS NOT RESTATED HERE (2026-08-05). It has a table and a
% result section of its own and is restated in the conclusion; the introduction
% points at it instead. If it is ever restored here, restore all three counts:
% stating two of the three invites a reader to subtract, and the subtraction is
% what the retired headlines were made of. The worked examples and the MDD
% ratios live only in \S\ref{sec:audit:results}.
% THE 2.0x-12.9x SHORTFALL RANGE IS WITHDRAWN, NOT RECOMPUTED. It divided by
% margins no source declared. At the registered 2 pp margin ten of the eleven
% assessable claims have no shortfall at all, so there is no range. Do not
% reintroduce this sentence with new numbers in it.
% TASK-MATCHED IS LOAD-BEARING AND STAYS IN THE SAME SENTENCE AS THE COUNT:
% R08, R15 and R16 do release per-item outputs, for other task suites. Dropping
% the qualifier makes the sentence false (\S\ref{sec:audit:v3}).
Could a reader check a published equivalence claim against any of this? We
enumerate \AuditFrozenCandidates{} such claims from three
registered sampling frames: method papers, official quantized model cards, and
inference-stack vendor documentation. \AuditIneligible{} of them,
\AuditIneligibleClaim{}, is ruled ineligible against the registered inclusion
rule, leaving \AuditEligible{}. Not one of the \AuditEligible{} declares a
numerical tolerance in advance, and not one releases \emph{task-matched}
per-item outputs, those covering the tasks its claim rests on;
\AuditPerItemOtherTaskOnly{} release outputs for other tasks only. So no
equivalence claim in the sample can be checked against a standard its author set
or rerun by a reader, and a further \AuditNotAssessable{} cannot be assessed
numerically at all from what they report. The remaining \AuditAssessable{} are
classified against an approximate planning threshold at a uniform
\AuditMarginPP{}\,pp margin, and that classification is reported together with
its sensitivity to the imputed disagreement rate (\S\ref{sec:audit:taxonomy},
\S\ref{sec:audit:results}). No claim is described as false: the audited property
is the evidential sufficiency of the reported evaluation, not the truth of the
underlying equivalence, and these are prevalences in this audited sample of
\AuditEligible{} eligible sources, not the literature at large.

% SOURCE: \S\ref{sec:minigrid:verdict}; docs/H3_EIGHT_CELL_DECISION_2026-07-26.md
% (SIGNED, 05c86f2); sections/minigrid.tex, Result 1 (the churn ratio), whose
% \label may move under the flagship reordering -- cite the file, not the label.
% CAUSAL WORDING 2026-07-31: "the calibration seed alone reorders the two
% methods" asserted sufficiency of a single factor. Replaced with the observed
% statement. Residual randomness is documented in \S\ref{sec:minigrid}.
The mechanism predicts something sharper, and a preregistered experiment tests
it. If cancellation grows with similarity, the least informative comparison is
not compressed against original but \emph{compressed against compressed}: two
methods at the same bit width, far closer to each other than either is to its
baseline. Pairing GPTQ and AWQ on byte-identical calibration samples across five
seeds and eight model-by-benchmark cells, we observe churn at a median of
$12.7\times$ the net delta, and under the frozen eight-cell decision rule H3 is
supported: within the controlled pipeline, changing the calibration sample was
sufficient to reverse the observed GPTQ--AWQ ranking in \textbf{5 of 8} cells,
at gaps that would ordinarily be reported as equivalence
(\S\ref{sec:minigrid:verdict}). The evidence problem is worst at the point where
a practitioner actually chooses.

Equivalence is a certification problem, so we compute certification tables
giving the number of items an evaluation needs to certify a compressed model
within $\pm m$ points of its baseline, from the per-item disagreement rates
observed under compression, not from independent-binomial variance. The paired
correction is large, and the requirement is set by churn rather than by task
difficulty (\S\ref{sec:certification}).
Per-item flips as a diagnostic for compressed models are due to
\citet{dutta2024flips}, and calibration-\emph{data} effects on quantization
quality are due to \citet{williamsaletras2024}; we claim neither. Our
contributions are (i) the certification tables and the paired-design correction
they quantify (\S\ref{sec:certification}); (ii) the atlas of the public record
and its measured cancellation ratio (\S\ref{sec:atlas}); (iii) the preregistered
audit and its verdict artifact (\S\ref{sec:audit}); and (iv) the seed-paired
experiment (\S\ref{sec:minigrid}). Relative to the closest existing work
\citep{llmaccuracystats2026}, which performs one-sided McNemar
\emph{detection}, ours is the shift from detection to certification: a declared
margin, TOST, and required-$n$ tables.

% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §§1, 7.
% RESOLVED 2026-07-30. Canonical DOI stated once here.
All of this assumes the evaluation itself holds still, and a small exploratory
study indicates it does not: on one fixed FP16 model, changing the
answer-extraction filter moved reported GSM8K accuracy from $0.232$ to $0.566$
without changing one token of model output. That is a scoring decision, not a
modelling one, and it is larger than every compression effect reported here; it
is also one model on one task and licenses no confirmatory reading
(\S\ref{sec:sensitivity}). Protocols were frozen before the analyses they
govern and deviations are dated amendments (\S\ref{sec:prereg}), the analyst
decisions that moved the headline are reported with the direction they moved it,
and every artifact is archived at \versiondoi{} (\S\ref{sec:artifacts}). The
limits of the exercise are in \S\ref{sec:limitations}.

% THE STANDARD, STATED EARLY (2026-08-05). The five lines were reachable only on
% the last page of the body, so the paper's deliverable arrived after all of its
% evidence. This is the same standard as \S\ref{sec:conclusion}, in one sentence
% per line and with no number attached: every figure that supports a line is
% argued in the section the line points at, and stating a bare number here would
% create a second home for it to rot in. The conclusion now RECAPS a standard
% the reader already has rather than introducing it; do not delete either copy,
% and if a line changes, change both.
% NARRATIVE CHANGE ONLY. No claim, quantity or scope moves with it.
What follows is organised around the standard those findings imply, so it is
worth stating up front. A compression claim should \textbf{declare a margin},
because ``equivalent'' without $\pm m$ is not testable
(\S\ref{sec:certification}); \textbf{run the paired test} at that margin rather
than reporting a failure to detect a difference (\S\ref{sec:certification});
\textbf{report churn beside net delta}, because they are different quantities
and the second does not summarise the first (\S\ref{sec:atlas});
\textbf{cite the sample size it met} against the count its benchmark family
requires (\S\ref{sec:certification}); and \textbf{release per-item outputs},
which is what converts an assertion into something a third party can check
(\S\ref{sec:audit}). \S\ref{sec:conclusion} returns to these five with the
evidence for each in hand. The rest of the paper is the case that all five are
needed, and the audit in \S\ref{sec:audit} is the measurement of how rarely they
are met today.
```

---

## FILE: `paper/figures/fig1_cancellation.tex`

```latex
% GENERATED by scripts/make_figure1.py. DO NOT EDIT BY HAND.
% Regenerate in the pinned image; the generator needs scipy for the planning
% requirement, which is computed by scripts/audit_stats.py and never typed.
%
% Requires \usepackage{tikz} and \usetikzlibrary{arrows.meta} in the preamble.
%
% Provenance for every number here is paper/figures/fig1_values.json.
% NOT RENDERED OR VISUALLY INSPECTED: there is no LaTeX on the machine that
% generated this (probe job 11675341), so the first person to compile it must
% check it for clipping, overlap and label legibility.
\definecolor{fharm}{RGB}{140,45,20}
\definecolor{fben}{RGB}{125,178,219}
\definecolor{fneutral}{RGB}{110,110,110}
\definecolor{frule}{RGB}{60,60,60}

\begin{figure}[!t]
\centering
\begin{tikzpicture}[
  x=1cm, y=1cm, line width=0.5pt,
  font=\scriptsize,
  panel/.style={draw=frule!35, rounded corners=1pt, line width=0.4pt},
  ttl/.style={font=\scriptsize\bfseries, anchor=west},
  lbl/.style={font=\scriptsize, anchor=west},
  num/.style={font=\scriptsize, anchor=west},
]
\node[panel, minimum width=6.0cm, minimum height=3.75cm, anchor=south west] at (0.0,6.15) {};
\node[ttl] at (0.18,9.6) {A\quad The aggregate view};
\node[lbl, font=\scriptsize\itshape, text width=5.5cm] at (0.18,9.120000000000001) {Two 4-bit methods, one model, one item set.};
\node[lbl] at (0.18,8.03) {GPTQ};
\draw[fill=frule!12, draw=frule!35] (1.32,7.87) rectangle (4.82,8.19);
\draw[fill=fneutral, draw=none] (1.32,7.87) rectangle (3.9198000000000004,8.19);
\node[num, anchor=west] at (4.9,8.03) {74.28\%};
\node[lbl] at (0.18,7.41) {AWQ};
\draw[fill=frule!12, draw=frule!35] (1.32,7.25) rectangle (4.82,7.57);
\draw[fill=fneutral, draw=none] (1.32,7.25) rectangle (3.8995000000000006,7.57);
\node[num, anchor=west] at (4.9,7.41) {73.70\%};
\draw[frule!55, line width=0.4pt] (1.32,6.87) -- (1.32,6.75) -- (4.82,6.75) -- (4.82,6.87);
\node[font=\scriptsize, anchor=north] at (3.0700000000000003,6.73) {0 to 100\% accuracy, $n=1{,}000$ per seed};
\node[font=\scriptsize\bfseries, anchor=west] at (0.18,8.530000000000001) {Gap: 0.58 pp};
\node[panel, minimum width=6.0cm, minimum height=3.75cm, anchor=south west] at (6.6,6.15) {};
\node[ttl] at (6.779999999999999,9.6) {B\quad The same items, paired};
\node[lbl, font=\scriptsize\itshape, text width=5.5cm] at (6.779999999999999,9.120000000000001) {Every item, going from GPTQ to AWQ.};
\draw[fill=fharm, draw=none] (7.0,8.4) rectangle (7.47424,8.82);
\draw[fill=fben, draw=none] (7.47424,8.4) rectangle (7.91832,8.82);
\draw[fill=frule!8, draw=none] (7.91832,8.4) rectangle (12.2,8.82);
\draw[draw=frule!45] (7.0,8.4) rectangle (12.2,8.82);
\node[font=\scriptsize, anchor=west] at (7.99832,8.610000000000001) {82.34\% unchanged};
\node[lbl, anchor=west] at (7.0,8.120000000000001) {\textcolor{fharm}{$\blacksquare$} 9.12\% correct $\to$ wrong};
\node[lbl, anchor=west] at (7.0,7.74) {\textcolor{fben}{$\blacksquare$} 8.54\% wrong $\to$ correct};
\node[lbl, anchor=west] at (7.0,7.34) {net delta $= 8.54 - 9.12 = -0.58$ pp};
\node[lbl, anchor=west, font=\scriptsize\bfseries] at (7.0,6.960000000000001) {churn $= 8.54 + 9.12 = 17.66$\%};
\node[lbl, anchor=west] at (7.0,6.6000000000000005) {28.66\% of answers change in all};
\node[panel, minimum width=6.0cm, minimum height=3.75cm, anchor=south west] at (0.0,1.55) {};
\node[ttl] at (0.18,5.0) {C\quad Could this evaluation certify?};
\node[lbl, font=\scriptsize\itshape, text width=5.5cm] at (0.18,4.52) {Planning requirement at a declared $\pm2$ pp margin.};
\node[lbl] at (0.18,3.76) {items run};
\draw[fill=fneutral, draw=none] (2.28,3.5999999999999996) rectangle (3.3715750915750915,3.9199999999999995);
\node[num] at (3.4515750915750916,3.76) {1{,}000};
\node[lbl] at (0.18,3.1399999999999997) {items required};
\draw[fill=fharm, draw=none] (2.28,2.9799999999999995) rectangle (5.26,3.2999999999999994);
\node[num] at (5.34,3.1399999999999997) {2{,}730};
\node[lbl, text width=5.55cm, anchor=north west] at (0.18,2.77) {Observed disagreement 17.66\%. A planning requirement, not evidence the methods differ.};
\node[panel, minimum width=6.0cm, minimum height=3.75cm, anchor=south west] at (6.6,1.55) {};
\node[ttl] at (6.779999999999999,5.0) {D\quad The calibration draw alone};
\node[lbl, font=\scriptsize\itshape, text width=5.5cm] at (6.779999999999999,4.52) {GPTQ minus AWQ, per calibration seed.};
\draw[frule!70, line width=0.5pt] (6.949999999999999,3.5) -- (11.7,3.5);
\node[font=\scriptsize, anchor=east] at (6.93,3.5) {0};
\draw[fill=fben, draw=none] (7.249999999999999,3.5) rectangle (7.6499999999999995,3.997391304347826);
\node[font=\scriptsize, anchor=south] at (7.449999999999999,4.037391304347826) {2.2};
\node[font=\scriptsize, anchor=north] at (7.449999999999999,2.55) {s0};
\draw[fill=fben, draw=none] (7.97,3.5) rectangle (8.37,3.8617391304347826);
\node[font=\scriptsize, anchor=south] at (8.17,3.9017391304347826) {1.6};
\node[font=\scriptsize, anchor=north] at (8.17,2.55) {s1};
\draw[fill=fharm, draw=none] (8.69,3.5) rectangle (9.089999999999998,2.98);
\node[font=\scriptsize, anchor=north] at (8.889999999999999,2.94) {-2.3};
\node[font=\scriptsize, anchor=north] at (8.889999999999999,2.55) {s2};
\draw[fill=fben, draw=none] (9.41,3.5) rectangle (9.809999999999999,3.5452173913043477);
\node[font=\scriptsize, anchor=south] at (9.61,3.5852173913043477) {0.2};
\node[font=\scriptsize, anchor=north] at (9.61,2.55) {s3};
\draw[fill=fben, draw=none] (10.129999999999999,3.5) rectangle (10.529999999999998,3.771304347826087);
\node[font=\scriptsize, anchor=south] at (10.329999999999998,3.811304347826087) {1.2};
\node[font=\scriptsize, anchor=north] at (10.329999999999998,2.55) {s4};
\node[font=\scriptsize, anchor=west] at (6.8999999999999995,1.9500000000000002) {all cells:};
\node[font=\scriptsize, text=fharm] at (8.18,1.9500000000000002) {$\bullet$};
\node[font=\scriptsize, text=frule!55] at (8.52,1.9500000000000002) {$\circ$};
\node[font=\scriptsize, text=frule!55] at (8.86,1.9500000000000002) {$\circ$};
\node[font=\scriptsize, text=fharm] at (9.2,1.9500000000000002) {$\bullet$};
\node[font=\scriptsize, text=frule!55] at (9.54,1.9500000000000002) {$\circ$};
\node[font=\scriptsize, text=fharm] at (9.879999999999999,1.9500000000000002) {$\bullet$};
\draw[frule!60, line width=0.4pt] (9.879999999999999,1.9500000000000002) circle (0.16);
\node[font=\scriptsize, text=fharm] at (10.219999999999999,1.9500000000000002) {$\bullet$};
\node[font=\scriptsize, text=fharm] at (10.56,1.9500000000000002) {$\bullet$};
\node[font=\scriptsize, anchor=west] at (10.76,1.9500000000000002) {\ \ $\bullet$ reversed};
\draw[frule!25, line width=0.4pt] (0.0,1.25) -- (12.6,1.25);
\node[anchor=north west, inner sep=0, text width=12.6cm, font=\scriptsize] at (0.0,1.1300000000000001) {\textbf{This is not one cell's problem.} Across 1{,}707 paired model-by-task cells mined from public per-item evaluation dumps, median per-item churn is about five times the median net accuracy delta. 145 of those cells post an aggregate accuracy identical to their baseline, and 128 of the 145 still change which items they get right. Ratios are undefined for a zero net delta, so those cells are counted here and excluded from the ratio.};
\end{tikzpicture}
\caption{\textbf{Near-equal aggregate accuracy does not certify interchangeable behavior.} One registered cell: Qwen2.5-7B on GSM8K, 4-bit GPTQ against 4-bit AWQ, paired on byte-identical calibration samples across five seeds. (A)~and~(B)~The aggregate gap of 0.58~pp is the small difference between two large opposing quantities summing to 17.66\%. (C)~The item count needed to certify equivalence at a declared $\pm2$~pp margin is a planning requirement computed at an assumed true difference of zero: it says the evaluation cannot support the claim, not that the methods differ. (D)~The sign changes with the calibration draw alone, and across the eight registered cells the winner reverses in 5 of 8. \textbf{Scope.} This cell is an illustrative example chosen because it is legible, and it is the most extreme of the eight: its churn-to-net-delta ratio is $30.4\times$ against a median of $12.7\times$ across the eight. All eight are shown in~(D) for that reason. The atlas figures in the panel above are observational and describe the public evaluation record rather than a census of compression.}
\label{fig:cancellation}
\end{figure}
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
%
% COMPRESSED 2026-08-04 (flagship narrative restructure, operation 1 and the
% §6 per-section target). The Paglieri reconciliation subsection moved WHOLE to
% sections/appendix_related_detail.tex (app:reconcile); nothing in it was
% deleted. The six subsection headings were dropped: at this length they were
% most of the section. Every citation that was here is still here.
%
% THE NO-PRIORITY-CLAIM SENTENCE AND ITS SOURCE COMMENT ARE UNTOUCHED AND MUST
% STAY VERBATIM -- it is a dated, author-affirmed statement about precedence.
% =====================================================================

\section{Related work and positioning}
\label{sec:related}

\citet{dutta2024flips} show that compressed models can match baseline aggregate
accuracy while flipping many individual answers, and propose flips and KL
divergence as complementary metrics. \textbf{The flips metric is theirs, and we
do not claim it.} What we add is the same decomposition measured across the
public record at scale (\S\ref{sec:atlas}), the use of the observed flip-rate
distribution as the \emph{variance model} for equivalence certification
(\S\ref{sec:certification}), and the audit that follows from it
(\S\ref{sec:audit}).

Concurrent work reaches the same premise independently.
\citet{rababah2026illusion}, posted two days before our preregistration froze
and unknown to us until the prior-art sweep of 2026-07-24, define
\emph{correctness agreement}, the per-item rate at which base and quantized
models are both correct on the same input. That statistic is the joint-correct
cell of the same $2\times2$ table our accuracy-state churn is built from, and
the two are interconvertible given the marginal accuracies. They study a
quantization family disjoint from ours (\texttt{llama.cpp} GGUF legacy and
$k$-quant rather than GPTQ and AWQ) and reach a conclusion consistent with
ours. We read this as
external corroboration of the premise, not competition on it, and we make no
priority claim over it: no committed artifact in this repository predates its
posting.
% SOURCE for the independence and no-precedence statements:
% docs/PRIOR_ART_CONCURRENT_2026-07-24.md, "Dated Amendments" (a)-(d),
% reviewed and affirmed by the author 2026-07-24.
What they do not supply, and what the rest of this paper is, is the machinery
that turns the shared premise into a decision: equivalence testing at a declared
margin, required-$n$, a test of whether the calibration seed reorders two
methods, and an audit of published claims. Two further concurrent studies
measure per-item change on adjacent objects.
Two further concurrent studies measure per-item change on adjacent
objects, on model versions and on community checkpoints
(Appendix~\ref{app:related:concurrent}).

\citet{williamsaletras2024} establish that the calibration \emph{data} affects
quantized model quality, finding substantial variation in downstream task
performance across calibration sets. \textbf{Calibration-data effects are
theirs.} Our question is orthogonal and finer-grained: holding the
calibration corpus fixed, does the calibration \emph{sample seed} change the
\emph{ranking} of two methods? The design pairs GPTQ seed $s$ and AWQ seed $s$ on
byte-identical calibration samples, so a seed-level ranking difference is
attributable to method-by-calibration interaction and not to the two methods
seeing different data (\S\ref{sec:minigrid}). The sweep found no prior work that
varies a calibration \emph{seed} with the corpus held fixed and asks whether the
resulting instability reorders two methods. The nearest antecedents vary the
calibration set itself and disagree with each other about how much that matters:
\citet{williamsaletras2024} find the effect substantial, and
\citet{paglieri2024outliers} find it diminishing on modern models, with
Mistral~7B close to immune. That disagreement is the strongest available
objection to this paper, since a field insensitive to the calibration set would
seem unlikely to reorder on the seed. Appendix~\ref{app:reconcile} answers it at
length: both results hold at once, because neither design measures the
\emph{gap between} two methods, which is the quantity a practitioner choosing
between them depends on, and our own eight cells show a seed-induced range at
least as large as that gap in 7 of 8.

\citet{helcig2026slq} occupy the phrase this paper is about: they define
losslessness for quantized LLMs and build a method reaching it. Their question
is the complement of ours, and they compute no equivalence test, power or
required $n$ (Appendix~\ref{app:related:lossless}).

The closest existing work is \citet{llmaccuracystats2026}, which brings
one-sided McNemar \emph{detection} to LLM accuracy comparisons and ships it in
the evaluation harness the field already uses. We agree with its diagnosis and
differ in the question asked. Detection asks whether there is evidence of a
difference; a non-significant result is not equivalence, and at the sample sizes
in \S\ref{sec:audit} it is frequently just an absence of resolution. Our deltas
are: (i) TOST certification at a \emph{declared} margin;
(ii) required-$n$ certification tables computed from empirical churn instead of
% SOURCE: results/certification_tables_rev2.csv column paired_advantage_at_median
% (GSM8K 2.25--2.26, MuSR 14.66--14.68). REV-2: the low end was 1.7 under rev-1;
% corrected 2026-07-26 with the abstract, introduction and the certification §.
from independent-binomial variance, with the $2.3$--$14.7\times$ correction that
implies; and (iii) the audit of published claims, which is the
empirical case that the distinction matters in practice. An anytime-valid
sequential extension, using confidence sequences that let a practitioner stop as
soon as the model is certified, is registered and in progress; it reports no results
here and is not claimed as a contribution of this paper.

The constructive-audit genre is well established
\citep{dodge2019showyourwork,marie2021mtaudit}, and has begun to adopt
preregistration directly, which is the precedent for \S\ref{sec:prereg}
(Appendix~\ref{app:related:genre}). We follow it in framing and in tone: the
finding is about what the field reports, not about whether individual authors
are right.

The audited claims span weight-only quantization, weight-and-activation
quantization and one-shot pruning; the methods and the honest non-claimers among
them are listed in Appendix~\ref{app:related:families}. We audit the equivalence
\emph{language} these papers use and the evidence offered for it, not the
methods themselves.
```

---

## FILE: `paper/sections/certification.tex`

```latex
% =====================================================================
% Section: Paired certification -- the paper's framework section.
%
% RESTRUCTURED 2026-08-04 (flagship narrative). This is now §3 of the body and
% the preregistration material is folded in behind it: main.tex inputs
% sections/preregistration.tex immediately after this file, and that file now
% opens at \subsection level. Do not reintroduce a \section there.
%
% PRIMARY SOURCES for every number in this section:
%   results/certification_tables_rev2.csv    (AUTHORITATIVE, 3 margins/family)
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §5 (registered metric set)
%   docs/CERTIFICATION_TABLES_2026-07-20.md  (narrative and rationale only)
%
% PRECEDENCE, SET 2026-08-02. The rev-2 CSV outranks the 2026-07-20 narrative
% document wherever they differ. That document was written against the REV-1
% atlas population and its numeric provenance is superseded: it derives
% "analysable cells 1,155 (1,254 non-excluded - 99 probe)", where the rev-2
% analysis population is 1,707. Its ARGUMENTS are still the source for this
% section's prose; its NUMBERS are not. Do not restore it as the authority.
%
% DISCREPANCY -- CLOSED 2026-07-26 as a wording mismatch, not a data mismatch.
% docs/CERTIFICATION_TABLES_2026-07-20.md line 4 describes the artifact as
% "12 benchmark families x 3 margins". Re-verified against
% results/certification_tables_rev2.csv on 2026-07-26: it holds ELEVEN named
% families (arc_challenge, bbh, gpqa, gsm8k, hellaswag, ifeval, math, mmlu,
% mmlu_pro, musr, winogrande) plus an "ALL (pooled)" row = 12 table ROWS at each
% of 3 margins (33 rows total). So the doc's "12 families" is loose wording for
% 12 rows; there is no missing or extra family and no number is affected.
% Nothing is outstanding for the paper; the doc's line-4 wording is the only
% artefact and it lies outside this tree.
% =====================================================================

\section{Paired certification: what an equivalence claim has to show}

% RESOLVED to rev-2 (2026-07-21) after the targeted second spot-check passed.
% SOURCE: results/certification_tables_rev2.csv, margin_pp = 2.0 rows.
\label{sec:certification}

\subsection{Detection is not certification}

The statistical question behind ``near-lossless'' is not the one usually
answered. A McNemar test, including the one-sided variant developed by the
closest existing work on LLM accuracy statistics
\citep{llmaccuracystats2026}, asks whether there is evidence that the
compressed model differs from its baseline. Failing to find such evidence is not
evidence of equivalence; with a small enough evaluation, nothing is detectable.
Our registration commits to this in advance: ``we will not interpret failure to
reject a difference as equivalence''.
% SOURCE: PREREGISTRATION.md §"Outcomes and Analysis".
Certification asks the other question: \emph{is the difference provably smaller
than a margin I declare in advance?} The standard instrument is TOST: two
one-sided tests at level $\alpha$ each, rejecting the composite null
$|\Delta| \geq m$ in favour of equivalence within $\pm m$. TOST converts an
equivalence claim into something with a sample-size requirement, and this
section computes that requirement empirically.

\subsection{Method}
\label{sec:cert:method}

% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §Method.
% CORRECTED 2026-07-31. This read "at 95% confidence and 80% power", which
% contradicted the paragraph below it: z_{1-alpha} = 1.6449 is ONE-sided at
% alpha = .05, and TOST at one-sided .05 corresponds to containment of a 90%
% two-sided interval, not a 95% one. The formula and every computed value are
% unchanged -- only the description of them was wrong. Four table captions
% carried the same error and are corrected with it.
% RETAIN-VERBATIM: the sentence below is one of the two body homes of
% qualification 17 and survives the 2026-08-04 compression unaltered.
For a discordance rate $p_d$ and margin $m$, under TOST at one-sided
$\alpha=.05$ (equivalent to requiring a 90\% two-sided confidence interval to
fall inside $\pm m$) with 80\% power,
\begin{align}
\mathrm{sd}_{\mathrm{paired}}      &= \sqrt{p_d}, &
\mathrm{sd}_{\mathrm{independent}} &= \sqrt{2p(1-p)}, \label{eq:sds}\\[2pt]
% WIDTH FIX 2026-08-05: the two equalities on one line ran 91pt past the
% measure. The numeric substitution moves to its own aligned line. The equation
% is unchanged.
n_{\mathrm{req}} &= \left\lceil \left(\frac{(z_{1-\alpha} + z_{1-\beta})\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil \label{eq:nreq}\\[2pt]
 &= \left\lceil \left(\frac{(1.6449 + 0.8416)\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil. \nonumber
\end{align}
The paired standard deviation follows from the flip model: the per-item accuracy
difference is $d_i \in \{-1,0,+1\}$, and under the null of no true difference
$\mathrm{Var}(d) = p_d$, the rate at which the two models disagree on
correctness. The independent form uses $p$, the family's median baseline
accuracy, because independent-binomial variance depends on accuracy and not on
churn. $z_{1-\alpha}$ is \textbf{one-sided}, since TOST rejects two one-sided
nulls at level $\alpha$ each (Appendix~\ref{app:prereg:choices}, interpretive
choice~5). The discordance rates are not modelled; they are read off the atlas
(\S\ref{sec:atlas}). For each benchmark family we take the 25th percentile,
median, and 75th percentile of the per-cell accuracy-state churn observed across
that family's atlas cells, giving optimistic, typical, and pessimistic
compression behaviour. Quartiles are \texttt{numpy}'s linear-interpolation
\texttt{np.quantile}.

% ADDED 2026-07-31. The design assumption was documented in the code
% (scripts/audit_stats.py::required_n_for_tost, "assumed true difference zero")
% but was never stated in the paper. Without it a reader may take these as the
% n that would certify an already-observed delta, which they are not.
Equation~\eqref{eq:nreq} is the standard TOST planning sample size under an
assumed \emph{true} paired accuracy difference of zero. It answers ``how many
items would this benchmark need for an equivalence test to have 80\% power,
given how much models of this kind disagree item-by-item''. It does
\emph{not} answer ``how many items would certify the delta this source
observed''. Under a true difference $\delta$, the quantity TOST must resolve is
the separation $m - |\delta|$ instead of $m$, so the requirement grows without
bound as $|\delta|$ approaches the margin. Every $n_{\mathrm{req}}$ reported in
this paper is therefore a \emph{lower bound} on what a non-zero true
difference would demand, and the tables are design tables, not retrospective
certification of any particular reported result.

\begin{table}[!t]
\centering
\small
\caption{Items required to certify equivalence within $\pm 2$\,pp under TOST at
one-sided $\alpha=.05$ (a 90\% two-sided interval) with 80\% power, assuming a
true difference of zero, by benchmark family, at the 25th/50th/75th
percentiles of the discordance rates the atlas observes for that family. The
naive column is the same requirement computed by treating the two runs as
independent samples. Eleven benchmark families plus the pooled row.}
\label{tab:certification}
% SOURCE: every cell cross-checked against results/certification_tables_rev2.csv
% rows with margin_pp = 2.0 (columns n_atlas_cells, discordance_p25/median/p75,
% required_n_p25/median/p75, required_n_independent_binomial,
% paired_advantage_at_median). The layout follows
% docs/CERTIFICATION_TABLES_2026-07-20.md §"The table at the registered 2 pp
% margin", a REV-1 narrative whose numbers are superseded by the rev-2 CSV.
% REPOINTED 2026-08-02: the cross-check pointer named the unsuffixed rev-1 CSV,
% which is not the file these cells were checked against.
% WIDTH FIX 2026-08-05: was {lrccrr} with two long free-running header phrases,
% running 126pt past the measure. The two wide headers wrap in fixed-width
% centred columns. No cell value changed.
% Set \small with tighter column separation so the p25/med/p75 triples fit on
% one line; at \normalsize they wrapped mid-triple and read badly.
\setlength{\tabcolsep}{2pt}
\small
\begin{tabular}{lr>{\centering\arraybackslash}p{2.6cm}>{\centering\arraybackslash}p{2.65cm}rr}
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
mmlu          & 1{,}311 & 0.093 / 0.140 / 0.259 & 1{,}432 / \textbf{2{,}164} / 4{,}005 & 7{,}727 & $3.6\times$ \\
winogrande    &  23 & 0.067 / 0.092 / 0.221 & 1{,}031 / \textbf{1{,}416} / 3{,}422 & 5{,}600 & $4.0\times$ \\
math          &  56 & 0.107 / 0.141 / 0.169 & 1{,}661 / \textbf{2{,}186} / 2{,}610 & 5{,}222 & $2.4\times$ \\
gsm8k         &  24 & 0.040 / 0.077 / 0.198 & 619 / \textbf{1{,}184} / 3{,}068 & 2{,}671 & $2.3\times$ \\
\midrule
\textbf{ALL (pooled)} & \textbf{1{,}707} & 0.064 / 0.120 / 0.225 & 994 / \textbf{1{,}855} / 3{,}478 & 7{,}722 & $\mathbf{4.2\times}$ \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Reading the table}

% SOURCE: results/certification_tables_rev2.csv, mmlu at margin_pp 1.0/2.0/3.0
% (required_n_median = 8656 / 2164 / 962; required_n_independent_binomial at
% 2 pp = 7727). The rev-1 8,491-vs-8,492 discrepancy against the rev-1 narrative
% doc is moot: both are superseded by rev-2, and the CSV remains authoritative.
Pick the benchmark family and the margin you intend to certify. The three
required-$n$ columns are the item counts you need under optimistic, typical and
pessimistic compression behaviour for that family; the naive column is the count
you would compute if you ignored pairing. \emph{MMLU, 2\,pp margin, typical
discordance $\Rightarrow$ evaluate at least 2{,}164 items.} Ignoring pairing
would have demanded 7{,}727, or $3.6\times$ the compute for the same conclusion.
Tightening the margin to 1\,pp raises the requirement to 8{,}656 items; relaxing
it to 3\,pp lowers it to 962. The margin is the practitioner's declaration, and
its cost is quadratic: parity within 1\,pp is four times as expensive to certify
as parity within 2\,pp.

The independent-binomial column is not a straw man. It is what you get by
treating the baseline and compressed evaluations as two unrelated samples and
comparing proportions, which is the default in most reporting, and it is wrong
in a specific, quantifiable way: the two runs are \emph{the same items through
two nearly identical models}, so they agree on the large majority of items, and
their difference has far less variance than independence implies.
% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md §"Why the naive column is in
% the table"; results/certification_tables_rev2.csv column
% paired_advantage_at_median (GSM8K 2.25--2.26, MuSR 14.66--14.68, pooled 4.16).
% Pointer corrected 2026-07-26: the values here are rev-2, but this comment
% named the rev-1 CSV, whose GSM8K entry is 1.7.
The advantage column is exactly that gap. It ranges from $2.3\times$
(GSM8K) to $14.7\times$ (MuSR) and sits at $4.2\times$ pooled
over 1{,}707 cells: a practitioner using the paired design reaches the same
equivalence conclusion on roughly a quarter of the evaluation budget. The
variation across families is informative in itself: low-churn families (MuSR,
BBH, GPQA) reward pairing most, while high-churn generative families (MATH,
MMLU) both need more items \emph{and} gain less from pairing.

\subsection{The requirement is driven by churn, not by difficulty}

The ordering in Table~\ref{tab:certification} is not the intuitive one, and this
is the section's main conceptual point.

% SOURCE: results/certification_tables_rev2.csv, mmlu vs gpqa at
% margin_pp = 2.0; the narrative argument is docs/CERTIFICATION_TABLES_
% 2026-07-20.md §"Why the naive column is in the table" (REV-1 narrative:
% its population and required-n figures are superseded, its reasoning is not).
% Baseline accuracies below are column median_baseline_accuracy: gpqa 0.3734,
% mmlu 0.4923. Discordances are column discordance_median: mmlu 0.14,
% gpqa 0.048397.
% REV-1 SURVIVOR, CORRECTED 2026-08-04. This paragraph read "MMLU's 0.390" and
% "MMLU's typical discordance is 0.137", which are the REV-1 entries in
% results/certification_tables.csv (0.39 and 0.13733). Table~\ref{tab:certification}
% four paragraphs above already printed the rev-2 discordance (0.140), so the
% section contradicted its own table. This is the sixth rev-1 figure found
% surviving into drafted prose on this project; same cause as the others, prose
% written against rev-1 tables that rev-2 replaced. The argument is unchanged
% and slightly stronger: 0.14 / 0.048397 = 2.89, still "nearly three times",
% and the baseline-accuracy gap it is contrasted against is now larger.
% REPOINTED 2026-08-02: these pointers named the unsuffixed rev-1 CSV while the
% prose already carried the REV-2 required-n (2,164; rev-1 was 2,123). A stale
% pointer under a corrected number is the harder defect to see, because the
% visible text is right.
MMLU needs about \textbf{2{,}164} items at a 2\,pp margin. GPQA needs
\textbf{749}. GPQA is by any ordinary account the harder benchmark, and its
median baseline accuracy in the atlas is 0.373 against MMLU's 0.492, on a task
designed to resist exactly the models that saturate MMLU. Difficulty is not what
sets the requirement. What sets it is how much the compressed model's per-item
correctness \emph{churns} relative to the baseline: MMLU's typical discordance
is 0.140 against GPQA's 0.048, so MMLU's paired variance is nearly three times
larger and its required sample size scales with it. A practitioner therefore
cannot reason about evaluation size from intuitions about task hardness,
headroom or score level. Two benchmarks with similar apparent difficulty can
differ by a factor of three in the evidence they require, and the only way to
know which is which is to measure churn. That is what the atlas is for, and it
is why these tables are empirical and not analytic.

\subsection{Scope and caveats}
\label{sec:cert:caveats}

% SOURCE: results/certification_tables_rev2.csv column n_atlas_cells for every
% count; the five caveats themselves are from
% docs/CERTIFICATION_TABLES_2026-07-20.md §"Scope and caveats", a REV-1
% narrative cited for its caveats only, its population figures superseded.
% PROSE-IFIED 2026-07-26 from a five-item list. All five caveats survive as
% content, in order: (1) <4-cell families omitted, (2) the two thin rows,
% (3) family aggregation mixes two variation sources, (4) the 99 probe cells,
% (5) certification n != detection n.
% TRIMMED 2026-07-27 (phase 4 trim, candidate 6). Caveats 2 (thin rows), 3
% (family aggregation) and 4 (probe-pair exclusion) moved VERBATIM to
% Appendix~\ref{app:cert:caveats-detail}. Caveats 1 and 5 stay in the body.
% MERGED 2026-08-04: the former "What this section does and does not support"
% subsection is folded in below, whole. Its content is mandatory; only the
% heading is gone (prose rule 6).
These caveats travel with the table, and any reuse of it should carry them.
Families with fewer than four analysable cells are omitted, because a quartile
over three points is not an empirical distribution; this drops nothing from the
registered set, and all surviving families appear in
Table~\ref{tab:certification}. Of those that survive, two rest on thin evidence
and are indicative only, \texttt{mmlu\_pro} (5 cells) and \texttt{ifeval}
(8), and should be treated as a starting hypothesis to be replaced by the
reader's own measured churn, not as a reference constant.
Appendix~\ref{app:cert:caveats-detail} covers the remaining two: that family
aggregation makes the quartile columns \emph{conservative} rather than
optimistic, and that both disclosed feasibility-probe pairs are excluded.
Finally, these are certification sample sizes, not
detection sample sizes: they certify equivalence within $\pm m$, the $n$ required
to \emph{detect} a difference at the same margin is larger, and reporting one as
the other is the error this section exists to prevent.

This section \emph{does not support}: extrapolation to benchmark families
absent from the atlas; extrapolation to compression methods absent from the
atlas population (\S\ref{sec:atlas:caveats}); or any claim that a model meeting
these counts is equivalent, because meeting the count makes the test
\emph{informative}, and the test still has to be run and to pass.
```

---

## FILE: `paper/sections/preregistration.tex`

```latex
% =====================================================================
% Subsections: Preregistration, freezes, and analyst degrees of freedom.
%
% RESTRUCTURED 2026-08-04 (flagship narrative, operations 4 and 5). This file
% is no longer a \section: it is folded into the framework section
% (sections/certification.tex, sec:certification) and opens at \subsection
% level. main.tex inputs it immediately after that file. Do not reintroduce a
% \section here.
%
% MOVED TO Appendix~\ref{app:prereg-detail} IN THE SAME COMMIT, NOTHING DELETED:
%   tab:freeze-timeline                          (whole table)
%   §"Disclosed pre-registration data contact"   (already there in full text,
%                                                 at app:prereg:contact)
%   §"Result-inspection discipline"              (moved verbatim)
%   §"The H3 reporting rule"                     (moved verbatim)
%   §"Atlas validation and population correction" narrative (already there in
%                                                 full, at app:prereg-spotcheck)
% WHAT STAYS HERE, AND WHY: the freeze summary, and the K = 1 -> 5 -> 4 ->
% 1-of-11 sequence, which is the body's canonical self-correction and does not
% move to an appendix.
%
% PRIMARY SOURCES:
%   PREREGISTRATION.md                        (frozen 2026-07-11)
%   docs/AUDIT_REGISTRATION_2026-07-15.md     (frozen; Amendments 1-4 appended)
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
% in the abstract, in §\ref{sec:atlas}, or anywhere in the blog post.
% =====================================================================

\subsection{What was frozen, and when}
\label{sec:prereg}

% SOURCE: PREREGISTRATION.md header lines 3-7;
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3 (commits b74fd58, d6e02dd, f06348f,
% 715a7ce); docs/AUDIT_VERDICTS_2026-07-20.md §Provenance (claim-table sha256).
Each artifact this paper depends on was committed before the analysis it
governs could run, and each frozen file carries a \emph{Dated Amendments}
section, so deviations are appended and never edited in, each recording whether
results had been inspected before the decision.
Table~\ref{tab:freeze-timeline} in Appendix~\ref{app:prereg-detail} dates every
freeze against its commit. The frozen claim table's content hash is recorded
with the verdicts (sha256 \texttt{842b9756...5af7b15}), as is the atlas
summary's (\texttt{98201ade...10a4712d}) and the container image's, so a reader
can confirm that the inputs to any reported number were the frozen ones.

Three properties of that arrangement do work in the paper. The mechanical parts
of the audit, meaning the inclusion trigger vocabulary, the extraction fields,
the verdict formulas and the robustness sweep, were fixed before any claim's
power was computed, so the audit cannot have selected its claims or its
statistics to produce a headline. The atlas pair list was fixed before any flip
statistic, so the atlas cannot have selected pairs to produce churn. And the H3
decision rule was fixed, in algebra, before the first compressed checkpoint
existed, so the paper reports whatever that rule returns. The appendix carries
the rest: the three disclosed points of pre-registration data contact, the seven
interpretive rulings in full, the inspection discipline observed during grid
execution, and the H3 rule as registered.

\subsection{The interpretive choice that moved the headline}
\label{sec:prereg:choices}

Frozen protocols do not eliminate analyst judgement; they make it visible and
datable. Seven passages of the audit registration were ambiguous enough to
require a ruling before verdicts could be computed. All seven were ruled on
2026-07-20, each is implemented in code, each is reversible by re-running with
the alternative, and all seven are stated in full in
Appendix~\ref{app:prereg:choices}. One carries a methodological point that
belongs in the main text.

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #1 (the
% SUPERSEDED record); resolved by docs/AUDIT_REGISTRATION_2026-07-15.md "Dated
% Amendments" Part 1, signed 2026-07-31. Current values from
% results/audit_verdicts_rev3.csv.
%
% RESOLVED, NOT OPEN. The previous version of this paragraph carried the
% reasoning "a source asserting parity within 0.15 pp has made a 0.15 pp claim",
% which is the error Amendment 2 exists to correct: R17's 0.15 is an OBSERVED
% DELTA (68.69 vs 68.54), not a declared tolerance. It must not be restated as
% the paper's position anywhere, in any file, in any wording.
The frozen §4 names the 2\,pp registered margin first, adds ``(and at the
claim's own margin when it states one)'', and labels the verdict
``underpowered for its own assertion'' \emph{at the applicable margin}. We took
that as two live readings and chose the claim-specific one. The choice was
wrong, and correcting it is the substance of Amendment~2
(Appendix~\ref{app:prereg-detail}).

The conditional decides it. \emph{When it states one}: no audited source states
one, so the applicable margin is the registered 2\,pp throughout, and what the
superseded implementation had substituted was each source's largest reported
delta. That substitution treats a measured outcome as a decision rule the source
never adopted. The sequence of values is reported plainly because it is the
disclosure: the first pass returned $K = 1$ of 12, the claim-specific reading
raised it to $K = 5$, the metric-compatibility ruling on R04 gave the $K = 4$
that was published, and the rev-3 recomputation at the registered margin returns
\textbf{1 of 11 assessable claims below the approximate planning threshold},
which is the claim the first pass had flagged. All readings ship in the released
CSV (\S\ref{sec:audit:results}).

\subsection{Atlas validation and population correction}
\label{sec:prereg-spotcheck}
% SOURCE: docs/ATLAS_REV2_CORRECTION_2026-07-21.md; the spot-check report of
% 2026-07-21 (10 cells, 262/262 fields); ruling R7. Full narrative, the two
% defects, and the rev-1 -> rev-2 delta at app:prereg-spotcheck and
% app:prereg:rev2delta.
% ONE SENTENCE KEPT IN THE BODY (operation 5). The label stays here because
% sections/limitations.tex, sections/atlas.tex and
% sections/appendix_artifacts_detail.tex all point at it.

The protocol required an independent spot-check before any atlas number could be
quoted externally. It re-derived ten stratified cells from a fresh
reimplementation of the registered definitions instead of a rerun of our own
code, and all 262 compared fields reconciled exactly: the arithmetic was right,
and the \emph{population} was not, because two defects had silently dropped
cells non-randomly. The repair executed a rule that was already binding and
under-implemented, it enlarged the analysable population by 44\%, it left the
audit's headline verdicts unmoved, and it was made \emph{after} results had been
inspected, which we disclose instead of presenting it as a pre-specified step.
Both revisions are published and the delta between them is reported
(Appendix~\ref{app:prereg:rev2delta}); a field whose near-lossless claims cannot
be rechecked, because per-item outputs are never released, is one whose
corrections cannot be seen either.
% CORRECTION TO THE RECORD (2026-07-22). Commit 272136b ("Update the paper's
% banner-marked figures to atlas rev-2") states: "Every \revtwoBanner and
% \revtwoTODO marker is resolved; none remain outside main.tex's macro
% definitions." That claim was false of the tree it described -- the rev-1 vs
% rev-2 delta marker survived it. The commit's substantive work was done; only
% the completeness claim in its message was wrong, and a second miss in the same
% commit is recorded at appendix_audit_table.tex (944 -> 962).
% The marker itself was CLOSED on 2026-07-26 by writing the delta narrative at
% app:prereg:rev2delta from docs/ATLAS_REV2_CORRECTION_2026-07-21.md §8.
```

---

## FILE: `paper/sections/atlas.tex`

```latex
% =====================================================================
% Section: The public-record flip atlas.
%
% RESTRUCTURED 2026-08-04 (flagship narrative). This section now runs BEFORE
% \S\ref{sec:audit}, which repairs a live logical defect: the audit's
% discordance imputation is defined over the atlas, and the atlas used to
% appear two sections after the audit that consumes it.
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
% remain in the record and the delta is reported in the preregistration
% subsections of \S\ref{sec:certification}.
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

\section{The atlas: cancellation at scale, and what certification costs}

% RESOLVED to rev-2 (2026-07-21) after the targeted second spot-check passed
% 14/14 cells, 126/126 fields. Every figure below is rev-2.
% SOURCE: results/atlas_cells_summary_rev2.csv, results/identical_score_churn_rev2.csv;
% delta table in docs/ATLAS_REV2_CORRECTION_2026-07-21.md section 8.
\label{sec:atlas}

\subsection{Construction, coverage, and the analysis population}
\label{sec:atlas:construction}

% TRIMMED 2026-07-27 (phase 4 trim, candidate 4) and again 2026-08-04
% (operation 15). The S1/S2 source descriptions, the descriptive-scope
% statement, the item-pairing mechanics and the three-way exclusion breakdown
% are all in Appendix~\ref{app:atlas-detail}, verbatim. The prompt-hash identity
% rule is RESTATED here rather than only relocated, because it is the admission
% control the rest of the section rests on.
The atlas mines paired per-item records from public evaluation dumps at zero GPU
cost. Its protocol was frozen on 2026-07-15, before any flip statistic was
computed beyond two feasibility probes that the registration discloses by name,
and the pair list itself was frozen as a machine-readable manifest, with dataset
URLs, run timestamps and task lists, before any flip statistic existed.
% SOURCE: docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §§1, 3.4; manifest freeze
% commit f06348f per docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3.
These analyses are descriptive by registration: they estimate flip and churn
magnitudes in the wild and feed the certification tables, they test no
registered hypothesis, and they cannot substitute for any H3 cell.
Two sources are in scope: \textbf{S1}, the Open LLM Leaderboard v1 archive of
community quantizations of 2023-era base models, and \textbf{S2}, the Neural
Magic / Red~Hat per-item dumps for quantized Llama-3.1 at 8B, 70B and 405B
(Appendix~\ref{app:atlas:sources}). An item enters the paired analysis
only if its full-prompt hash is identical across the pair, and a cell is
excluded if fewer than 99\% of joinable items pass that check, because
prompt-hash identity, not harness version, is the operative control
(Appendix~\ref{app:atlas:pairing}).

% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1, first bullet;
% results/atlas_cells_summary_rev2.csv, reason column.
% POPULATION: this paragraph (and only this paragraph) uses the 1,807 figure.
\label{sec:atlas:coverage}%
The enumeration yields 2{,}055 pair-task cells, of which 1{,}807 are analysed
and 248 are excluded or skipped, most often because no results file exists for
that task in any recorded run (Appendix~\ref{app:atlas:exclusions} breaks the
exclusions down by reason). One of those reasons is a finding in itself. An
empty join intersection means the two sides of the pair were evaluated on
\emph{different item sets}: the leaderboard's baseline run and its quantized run
do not share the items whose scores are being compared. The resulting difference
in reported accuracy is not a paired quantity at all, no per-item analysis of it
is possible, and this is invisible to anyone reading only the aggregate
leaderboard numbers.

An earlier revision overstated the exclusion counts behind that observation,
reporting 643 float-scored and 132 empty-join exclusions and attributing both to
upstream reporting practice. A spot-check established that most of those cells
were readable and that our own parser could not see them; the figures above are
what survives once that defect is fixed (\S\ref{sec:prereg-spotcheck}).

% SOURCE: results/atlas_cells_summary_rev2.csv (the 1,707-cell probe-excluded
% analysis population, S1 = 1,398 / S2 = 309); docs/ATLAS_REV2_CORRECTION_
% 2026-07-21.md §Verification; docs/ATLAS_MINING_REGISTRATION_2026-07-15.md
% §§1, 6.
% PARAMETER SPAN CORRECTED 2026-08-04 (defect D2). The paper said "3B to 405B"
% in three places. Parsing base-model names over the 1,707-cell analysis
% population gives {1.3, 3, 7, 8, 13, 20, 30, 33, 70, 405}B, with 60 cells on
% EleutherAI/gpt-neo-1.3B, so the floor is 1.3B. This is a statement about the
% population only; no claim about how any statistic varies with scale is made
% here or anywhere else in this section.
% REPOINTED 2026-08-02. This cited docs/CERTIFICATION_TABLES_2026-07-20.md
% §Provenance and its rev-1 arithmetic as the source for the 1,707 below. That
% document is the REV-1 narrative and its population figures are superseded by
% the rev-2 correction; a provenance comment that points a current number at a
% superseded source is the defect, even though the prose itself was already
% right. The rev-2 CSV is now the source of record.
Every statistic in the remainder of this section, in the certification tables of
\S\ref{sec:certification}, and in the discordance imputation of
\S\ref{sec:audit:rules} uses a single population: the \textbf{1{,}707} cells that
are neither excluded nor part of a disclosed feasibility probe
(S1 = 1{,}398, S2 = 309), spanning base models from 1.3B to 405B parameters. The
99 probe cells span the two pairs whose results were known before the
registration was written; the registration requires them in the atlas but not in
any headline aggregate, and they are tiny hand-built sanity pairs that would
distort any quartile (Appendix~\ref{app:atlas-detail}). The 1{,}807 figure above
is pipeline accounting and is never used as an analysis denominator.

\subsection{Net delta versus per-item churn}
\label{sec:atlas:netgross}

% SOURCE: Table~\ref{tab:atlas-strata} (results/atlas_cells_summary_rev2.csv,
% the 1,707-cell analysis population), as the ratio of the two medians, every
% figure dividing the medians AT FULL PRECISION:
%   POOLED 0.120000 / 0.0222222 = 5.4000 exactly.
%   S1     0.13745229 / 0.02631579 = 5.2232.
%   S2     0.04800000 / 0.00924214 = 5.1936.
%   Median of per-cell ratios, 1,562 cells with non-zero net delta: 3.8452;
%   4.2000 if the 128 zero-delta-with-churn cells are readmitted as unbounded.
% ALL OF THE ABOVE ARE NOW GENERATED. scripts/churn_ratio.py computes every
% value this section prints for this quantity, from the committed artifact, and
% tests/test_churn_ratio.py pins them. Run `python3 scripts/churn_ratio.py
% --check` after touching any of them. Before 2026-08-05 this number existed
% only as arithmetic in this comment, which is how it rotted twice (D4, D8).
%
% AGGREGATION NAMED AND FIXED 2026-08-05 (defect D4 closed;
% docs/HEADLINE_CHURN_RATIO_DEFINITION.md). The aggregation is RATIO OF MEDIANS.
% No frozen registration defines it -- the atlas registration fixes the per-cell
% metrics and the population and is silent on aggregation -- so it is named here
% explicitly and is a descriptive summary, not a registered quantity.
%
% PRECISION CONVENTION, ONE CONVENTION ONLY, fixed 2026-08-05. All three
% figures divide UNROUNDED medians: pooled 5.40, S1 5.22, S2 5.19. The earlier
% pair 5.27/5.33 divided the medians at the 3 dp the table then printed, which
% put two rounding conventions in one sentence. It is retired. Reproducibility
% is now supplied by PRECISION rather than by rounding: tab:atlas-strata prints
% the stratum medians to 6 dp, and dividing the printed cells reproduces 5.22
% and 5.19 (5.223134 and 5.193681 against the exact 5.223187 and 5.193600).
% Never reintroduce a ratio of pre-rounded inputs.
%
% THE RETIRED 5.3x. Every occurrence of $5.3\times$ as the atlas headline was
% replaced on 2026-08-05. No unrounded derivation produces 5.3; it arose only as
% an eyeball average of the two rounded stratum values, and D8 showed the S1
% input had additionally been mis-rounded. Do not reintroduce it.
% NOT THIS QUANTITY: certification.tex and appendix_audit_table.tex print
% $5.3\times$ in an ifeval row. That is the paired-versus-naive sample-size
% advantage (4,211/800 = 5.26), a different quantity that rounds the same way.
% ROUNDING CORRECTED 2026-08-05 (Wave 3 defect D8,
% docs/WAVE3_ADVERSARIAL_REVIEW_2026-08-05.md §1). The S1 numerator read 0.138
% and the quotient 5.3077. The S1 median accuracy-state churn over the analysis
% population (excluded_or_skipped false, contains_disclosed_probe_cell false,
% n=1,398) is 0.13745229. Every other cell of tab:atlas-strata reproduces
% exactly. Unrounded the two strata give 5.2232 and 5.1936, which is what the
% section now prints; the superseded ratio-of-rounded-medians reading gave
% 5.2692 and 5.3333. Both readings put the two strata at the same multiple to
% two significant figures, which is the claim this section makes, and the
% unrounded pair is the closer of the two.
% REV-1 SURVIVOR, CORRECTED 2026-07-27. This read "roughly five to six times"
% and cited docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1's "Reading" bullet, which
% sits under the REV-1 strata table (S1 = 846 cells). At rev-2 both strata land
% at 5.3.
% SCALE CLAIM DELETED 2026-08-04 (defect D3). This sentence continued "and that
% ratio holds at every scale represented, from 3B to 405B parameters". That is
% DISCONFIRMED: per-scale median ratios over the analysis population run from
% 4.25x (70B, 176 cells) to 8.88x (20B, 58 cells) across strata with meaningful
% n, and the single-cell 30B stratum gives 1.00. No replacement claim about
% scale is made. What the section reports is the two REGISTERED strata, S1 and
% S2, which are what tab:atlas-strata groups by.
% REPETITION (2026-08-04): the ratio had five homes across the paper. The
% headline and the S1/S2 preservation paragraph are merged here into one, so
% this section states it once.
Across the atlas, per-item accuracy-state churn runs several times the net
accuracy delta. The ratio of median accuracy-state churn to median absolute
accuracy change is \textbf{5.40} pooled over the 1{,}707 cells
($0.120000 / 0.022222$), and 5.22 and 5.19 within S1 and S2. All three divide
unrounded medians; Table~\ref{tab:atlas-strata} prints the stratum medians to
enough places that a reader can reproduce the stratum figures from it. These
are ratios of medians, not medians of cellwise ratios, and the two
summarise different things. The median among finite cellwise ratios is
\textbf{3.85}. Assigning $+\infty$ to the 128 zero-delta/nonzero-churn cells
raises the all-cell median to 4.20. The finite ratios are the 1{,}562 cells
whose net delta is non-zero; a cellwise ratio is undefined for the remaining 145
(\S\ref{sec:atlas:identical}), and the exclusion is not evenly spread, removing
6.8\% of S1 and 16.2\% of S2. The pooled figure describes the typical churn
against the typical net delta; the cellwise median describes the typical cell.
Neither is the headline on its own.
The net delta a model card reports is the residue left after
harmful and beneficial flips cancel; the churn is the quantity that describes how
much of the model's behaviour actually changed. They are different quantities and
both should be reported. The consequence for inference is direct: churn is the
variance term in Equations~\eqref{eq:sds}--\eqref{eq:nreq}, so a compressed model
whose net delta looks reassuringly small can still be sitting on the noisiest
possible evidence base for the claim that it is unchanged.

% SOURCE: Table~\ref{tab:atlas-strata}, dividing the unrounded medians.
% Median churn 0.13745229 -> 0.04800000 is a factor of 2.8636; median |net
% delta| 0.02631579 -> 0.00924214 is a factor of 2.8474; the two move together,
% which is why the ratio is preserved to two significant figures. Both factors
% were recomputed unrounded on 2026-08-05; from 3 dp inputs they read 2.854 and
% 2.889, a wider gap than the data actually show.
The ratio is preserved across a generational change in method. The two strata
differ by nearly a factor of three in how much behaviour they disturb, with
median accuracy-state churn falling by a factor of 2.86 from S1 to S2, and by
almost exactly the same factor, 2.85, in the net delta they report
(Table~\ref{tab:atlas-strata}), so the understatement ratio barely moves: 5.22
in S1 and 5.19 in S2. Two generations of
compression method, one of them three times gentler than the other, hide the
disturbance they do cause by the same multiple. Better methods have made the
difference smaller \emph{without making the evidence for equivalence any more
sufficient}, because the quantity that determines how much evidence is required
scales down in lockstep with the quantity being claimed small.

\begin{table}[!t]
\centering
% WIDTH FIX 2026-08-05. The stratum descriptions used to be the column headers,
% which made this tabular 244pt too wide: the whole S2 column rendered off the
% right edge of the page and no S2 value was visible to a reader of the PDF
% (docs/COMPILE_BASELINE_2026-08-05.md). They are prose, so they belong in the
% caption. No value changed.
\caption{The two atlas strata, on the 1{,}707-cell analysis population. S1 is
the Open LLM Leaderboard v1 archive of community quantizations of 2023-era base
models, TheBloke-era GPTQ and similar; S2 is the Neural Magic / Red~Hat
W4A16, INT8 and FP8 releases from 8B to 405B. Percentages are within-stratum
shares of cells. The two medians are given to six places because the ratios
quoted in the text divide them unrounded; dividing the printed cells reproduces
5.22 and 5.19.}
\label{tab:atlas-strata}
% SOURCE: results/atlas_cells_summary_rev2.csv, grouped by source.
% Population: 1,707 (S1 1,398 + S2 309) -- NOT the 1,807 figure.
\begin{tabular}{lrr}
\toprule
 & S1 & S2 \\
\midrule
Cells                                & 1{,}398        & 309 \\
Median accuracy-state churn          & 0.137452       & 0.048000 \\
Median $|$net accuracy delta$|$      & 0.026316       & 0.009242 \\
TOST-equivalent at 2\,pp             & 68 (4.9\%)     & 53 (17.2\%) \\
Exact McNemar $p < 0.05$             & 371 (26.5\%)   & 19 (6.1\%) \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:atlas-strata} contains the empirical core of the paper's
motivation. In S1, 4.9\% of cells can be certified equivalent at the registered
2\,pp margin and 26.5\% show a detectable difference, which leaves
967 cells (69.2\%) of the public record in a \textbf{gray zone}:
neither certifiable as equivalent at the margin the field implicitly uses, nor
detectably degraded, at the sample sizes actually evaluated. In S2 the shares
move to 17.2\% certifiable and 6.1\% detectably different, and
240 cells (77.7\%) remain in the same gray zone.%
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
evaluation practice, and should be read as one: a modern vendor quantization of
an 8B--405B instruction-tuned model perturbs per-item behaviour roughly a third
as much as a 2023 community quantization of a 7B base model, and its evaluations
are correspondingly more often certifiable. What does \emph{not} improve is the
evidential situation. The modal cell in \emph{both} strata is one where the
evaluation cannot answer the question the release note answers, for the reason
above: certifying a smaller margin requires \emph{more} items, not fewer.

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
% REV-2 CORRECTION 2026-07-26. This comment previously cited the REV-1 file and
% the 1,155-cell population while the prose beneath it had already been updated
% to rev-2. Two rev-1 restatements survived here and were corrected in the same
% pass: the nonzero-churn subset median (0.0919 is rev-1's 0.091868; rev-2 is
% 0.092215 -> 0.0922), and "more than 6% of individual items", which restated
% rev-1's churn_median 0.062176 where rev-2 gives 0.072000 -> "more than 7%".
% "ROUGHLY ONE IN TEN" RECONSIDERED AND TIGHTENED: it was near-exact for rev-1's
% 9.78% share and is a stretch for rev-2's 8.49% (= 1 in 11.8), rounding away
% from the true value in the direction that overstates the finding. Replaced
% with "about one in twelve". Do not restore "one in ten".
The clearest single demonstration that aggregate accuracy is not a summary of
behaviour is the subset of cells where the aggregate does not move at all. Of
the 1{,}707 analysable cells, \textbf{145 (8.49\%) post an exactly identical
accuracy} to their baseline. Not similar: identical, to machine precision.
Among those 145 cells, the median accuracy-state churn is 0.0720, the
mean is 0.0887, and the maximum is 0.3434; 128 of the 145 have nonzero
churn, with a median of 0.0922 among that subset. About one in twelve compressed
model evaluations in the public record reports a score identical to its
baseline, and half of those still disagree with the baseline on more than 7\% of
individual items.

% RELOCATED 2026-08-04 (operation 8, adapted). The field-by-field table of the
% most extreme zero-delta cell moved to Appendix~\ref{app:atlas:extreme}, whole
% and with every row. The plan asked for it to become a Figure 1 panel; the
% figure at paper/figures/fig1_cancellation.tex is generated by
% scripts/make_figure1.py from a different cell and is owned elsewhere, so the
% table was relocated instead of deleted. Nothing was lost.
% All four caveats are retained here: small n, symmetric flips easier at small
% n, S1 provenance, and illustration-not-magnitude.
The mechanism is concrete in the most extreme such cell
(Table~\ref{tab:identical-extreme}, Appendix~\ref{app:atlas:extreme}): a 2023-era
community GPTQ of a 7B base model on one MMLU subject, where exactly 17.17\% of
items broke and exactly 17.17\% healed. The rates being equal, the net delta is
exactly zero and the exact McNemar test returns $p = 1.0$, correctly: there is no
evidence of a directional difference. Meanwhile a third of the answers changed. A
model card would truthfully write ``no change in accuracy'' for a cell where one
item in three behaves differently. The caveats belong in the same breath: at
$n = 198$ symmetric flip counts are easier to hit by chance, and this is an S1
cell from the noisier stratum. It illustrates the mechanism, not a typical
magnitude; the finding to carry away is the 145 cells and their 7.20\% median
churn, not this cell's 34\%.

\subsection{Population caveats}
\label{sec:atlas:caveats}

% SOURCE: docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1, final bullet ("Population
% caveats (registered)"), reproduced here in substance;
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.
% COMPRESSED 2026-07-26. The census-vs-record distinction and the S1 license
% limitation are both retained verbatim in substance, as instructed.
% MERGED 2026-08-04: the former "What this section does and does not support"
% subsection is folded in below, whole. Its content is mandatory; only the
% heading is gone (prose rule 6).
These caveats are registered, and they are load-bearing. S1 is community
quantizations of 2023-era models conditioned on leaderboard coverage: a pair
exists only if someone chose to submit both the base model and its quantization
to the Open LLM Leaderboard, and that choice was not random with respect to
anything. S2 is one vendor's releases, evaluated by that vendor.
\textbf{This is the public record of compression evaluation, not a census of
quantization.} It is the right population for what this paper asks (what the
circulating evidence looks like, and how much would suffice) and the wrong one
for how quantization behaves on average, which would need a designed sample
rather than the record left by the field's own reporting choices; the controlled
experiment of \S\ref{sec:minigrid} exists precisely because the atlas cannot
answer causal questions. Two further limits: S1's archive carries no
declared license, recorded as a limitation in the datasheet
(\S\ref{sec:artifacts}), and per-cell statistics inherit the item counts of
whoever ran the original evaluation, which is why many cells are small, an
inheritance that is itself part of the finding.

% A REV-1 SURVIVOR died with the deleted "Supports" half of this closer in the
% 2026-07-27 pass: it read "five to six times", rev-1's ratio, where rev-2 gives
% 5.22 (S1) / 5.19 (S2) on the unrounded medians. S1 was corrected from 5.31 to
% 5.27 on 2026-08-05 (defect D8), then to 5.22 with the single unrounded
% convention later the same day.
The findings above are claimed at the population each was measured on and no
wider. This section does not support any statement about quantization methods in
general, about models or methods absent from the two sources, or about causal
attribution of churn to any design choice. Nothing here is evidence for or
against H3.
```

---

## FILE: `paper/sections/audit.tex`

```latex
% =====================================================================
% Section: Audit of published near-lossless claims.
%
% RESTRUCTURED 2026-08-04 (flagship narrative). This section now runs AFTER
% \S\ref{sec:atlas}, which repairs a live logical defect: the discordance
% imputation below is defined over the atlas, and the atlas used to appear two
% sections later.
% MOVED TO Appendix~\ref{app:audit-method} IN THE SAME COMMIT, NOTHING DELETED:
%   tab:audit-locus, tab:audit-mdd (both whole, every column kept)
% MOVED TO Appendix~\ref{app:prereg:choices}: the K = 5 -> K = 4 R04 history,
%   which that appendix already carried in full as interpretive choice 3.
%
% PRIMARY SOURCES for every number in this section:
%   results/audit_verdicts_rev3.csv     (AUTHORITATIVE, per-claim, machine-readable;
%                                        job 11591245, sha c85d6f8a...b150082b,
%                                        single run, chmod 0444 -- never re-run)
%   docs/audit_claim_table.csv          (frozen inputs, sha256 in the doc)
%   docs/AUDIT_REGISTRATION_2026-07-15.md (frozen protocol, §§3-5, + Amendment 2)
%   docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md (full-text review of all 17)
%
% REV-3 SUPERSESSION, 2026-07-31. Amendment 2 (signed, commit ab279b2) is in
% force. It (a) makes the registered UNIFORM 2 pp margin the primary yardstick
% for every claim, (b) forbids describing any quantity derived from a source's
% own reported results as that source's own/stated/declared margin, and (c)
% reopens §§3.1-3.2 for eligibility only, excluding R10. Consequences for this
% section, all carried below:
%   K = 4 of 12 "underpowered for their own assertion"  ->  1 of 11 below the
%     approximate planning threshold at 2 pp, and that one is imputation-
%     sensitive, so 0 of 11 are below it throughout the atlas IQR.
%   denominators 17 -> 16 eligible.
%   the 2.0x-12.9x shortfall range is WITHDRAWN, not recomputed: ten of eleven
%     claims have no shortfall at all at 2 pp, so there is no range to state.
% docs/AUDIT_VERDICTS_2026-07-20.md is the SUPERSEDED record (rev-1 atlas AND
% pre-Amendment-2 margins). Do not "restore" any value from it.
%
% SUPERSESSION NOTICE -- do not "fix" this section against the older doc.
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md line 54 states "only 1 of 17 claims
% has per-item outputs released". That line is SUPERSEDED by the 2026-07-20
% verdicts document, which records 0 yes / 3 partial / 14 no. This paper uses
% the rev-3 denominator; the three "partial" sources are the ones the older line
% was gesturing at.
%
% DISCREPANCY -- CLOSED 2026-07-26. THE FROZEN TABLE GOVERNS.
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md line 48 describes the frozen table as
% "7 method papers, 8 official model cards/blog, 2 vendor docs" (7/8/2). The
% frozen table itself gives F1=7, F2=7, F3=3, re-verified 2026-07-26 by counting
% the `frame` column of docs/audit_claim_table.csv (7/7/3, 17 rows total).
% docs/audit_claim_table.csv is a FROZEN artifact and is authoritative over the
% older narrative doc, so the prose below (7/7/3) is correct as written.
%
% REV-2 POINTER CORRECTION, 2026-07-27, RETAINED AS HISTORY. Every SOURCE
% comment in this tree that cited results/audit_verdicts.csv was repointed to
% the rev-2 file; the typeset values were already rev-2, so only the provenance
% pointers had been wrong, and they were instructing future sessions to
% "correct" correct values back to superseded rev-1 ones. That hazard is why the
% rev-2 -> rev-3 repointing was done comment by comment rather than by a blind
% replacement. Rev-2 -> rev-3 is a different kind of change: the yardstick
% itself moved (Amendment 2), so verdicts DID move.
% =====================================================================

\section{What published equivalence claims actually report}

% SOURCE: results/audit_verdicts_rev3.csv (job 11591245), computed once under
% Amendment 2 over the frozen claim table (sha 842b9756...) and the rev-2 atlas
% (sha b7cffc52...), both DECLARED on the command line, neither defaulted.
\label{sec:audit}

\subsection{What was audited, and what was not}

% STAGE A of the audit compression, 2026-08-06. Protected qualifications 1, 2,
% 3, 12, 13 and 18 all live in this subsection and are carried below.
% RELOCATED, NOT DELETED: the full-text review behind the R10 ruling and the
% source provenance detail (content hashes for 16 of 17, R13 empty) are in
% Appendix~\ref{app:audit:eligibility}.
% NEVER describe the two extraction passes as inter-rater or independent human
% verification. NEVER collapse 17 and 16 into one number.
The audit protocol was frozen on 2026-07-15, before any per-claim power
computation was run, and the claim list itself was frozen separately before any
verdict was computed.\footnote{%
% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md (status line, §3.4);
% freeze provenance reconfirmed on the rev-3 command line (job 11591245).
Registration frozen at commit \texttt{b74fd58}; claim table frozen at commit
\texttt{715a7ce} with its sha256 recorded in the verdicts document.}
Sources were enumerated exhaustively within three fixed frames: method papers
(F1), official quantized model cards (F2), and inference-stack vendor blogs and
documentation (F3). A source enters the pool if it asserts, in prose or a table
caption, that a compressed model's benchmark quality is
equivalent-or-negligibly-different from its uncompressed baseline, under a
trigger vocabulary fixed in advance. Every claim meeting the criterion is
audited; there is no discretionary sub-selection.

% SOURCE: docs/audit_claim_table.csv column `frame`: F1=7, F2=7, F3=3.
% BOTH DENOMINATORS ARE LOAD-BEARING AND MUST NOT BE COLLAPSED.
The frozen table contains \AuditFrozenCandidates{} candidate claims: 7 method
papers, 7 official model cards or blogs, and 3 vendor documents. A full-text
review of every source, conducted after the first verdicts were computed, found
that one candidate's recorded quotation appears nowhere in its source, having
been composed from a table cell. The registered rule requires the assertion to
appear in prose or a table caption, so \AuditIneligibleClaim{} is excluded by
applying that rule as registered, leaving \textbf{\AuditEligible{}} eligible
sources; every count in this section is over those \AuditEligible{}, and the
exclusion lowers no count reported here
(Appendix~\ref{app:audit:eligibility}).

% ADDED 2026-07-31, PROTECTED. The body must say WHAT the passes were.
Each claim's fields were extracted by two blinded automated passes, separate
language-model agent sessions with the second given no access to the first
pass's output, followed by human reconciliation of every disagreement before the
verdict stage (\S\ref{sec:prereg}). Separate sessions prevent the second pass
from copying the first; they do \emph{not} make the two passes statistically
independent, because both share a common model prior, and nothing here is
inter-rater agreement. Appendix~\ref{app:extraction} specifies the procedure and
reports what can and cannot be measured after the fact.

% SOURCE: docs/AUDIT_REGISTRATION_2026-07-15.md §4 closing paragraph.
% PROTECTED: evidential sufficiency, not truth. No claim is called false. The
% prevalence disclaimer is stated in full at the section close as well.
\textbf{No audited claim is described as false, and none of our findings implies
that any audited model is in fact degraded.} The audited property is the
\emph{evidential sufficiency of the reported evaluation}: whether the evaluation
offered in support of an equivalence claim was large enough to have detected the
difference the claim pronounces negligible. A claim can be perfectly correct and
still be unsupported by the evaluation offered for it, and several of the claims
below are very probably correct. Nor is any proportion reported here a
prevalence estimate for the field. What is missing from the audited sources is a
reporting standard: this section measures the gap such a standard would close,
and \S\ref{sec:certification} supplies the instrument.


\subsection{What the sources declare}
\label{sec:audit:taxonomy}

% ADDED 2026-07-31, carrying AUDIT_REGISTRATION Amendment 2 (signed, commit
% ab279b2) and docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md.
% SOURCE: results/audit_verdicts_rev3.csv columns eligible, eligibility_basis,
% margin_category, evidence_form. Job 11591245.
%
% DO NOT report the marginals of margin_category alone. "0 formal / 12 informal
% / 4 unquantified" is arithmetically right and rhetorically wrong: 7 of the 12
% category-2 claims contain NO NUMBER AT ALL, so calling them informal *margins*
% reads as contradicting the 0-of-16 headline in the same paragraph. The
% cross-tab is the honest presentation.
%
% STAGE A, 2026-08-06: the R10 eligibility ruling moved UP into
% \S\ref{sec:audit} (design and scope), where both denominators are now
% introduced together, and the full-text review behind it moved to
% Appendix~\ref{app:audit:eligibility}. Nothing was deleted.
Across the \AuditEligible{} eligible sources we distinguish two independent
properties: what form the source's evidence takes, and whether the reported
information suffices to assess it numerically at all.

\begin{table}[!t]
\centering
\caption{What the 16 eligible sources declare. Columns are the form of the
evidence offered; rows are whether the source reports enough for a numerical
assessment under the registered paired-outcome framework. \emph{Prospective
numerical decision margin} means a tolerance stated independently of the
observed result: a threshold that could have been written down before the
evaluation ran. That column is empty.}
\label{tab:audit-taxonomy}
% SOURCE: results/audit_verdicts_rev3.csv, cross-tabulating margin_category
% (2=assessable-informal, 3=unquantified) against evidence_form. Verified to
% sum to 16 on both margins: 7+5=12, 3+1=4, 7+3=10, 5+1=6.
% WIDTH FIX 2026-08-05: was {lccc} with three long free-running header phrases,
% which ran 133pt past the measure. Fixed-width centred header columns wrap the
% phrases instead. No cell value changed, and the empty prospective column that
% is this table's whole evidential point is untouched.
\setlength{\tabcolsep}{4pt}
\begin{tabular}{l>{\centering\arraybackslash}p{2.2cm}>{\centering\arraybackslash}p{2.4cm}>{\centering\arraybackslash}p{2.2cm}}
\toprule
 & Prospective numerical decision margin & Retrospective numerical description of a result & Qualitative language only, no number \\
\midrule
Numerically assessable     & 0 & 5 & 7 \\
Not numerically assessable & 0 & 1 & 3 \\
\midrule
\textbf{Total}             & \textbf{0} & \textbf{6} & \textbf{10} \\
\bottomrule
\end{tabular}
\end{table}

% SOURCE: docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md §§6-7.
% STAGE B, 2026-08-06: the sweep's contents (parity and percentage point absent
% from the corpus, every "margin" a layout artefact or the "by a large margin"
% idiom, the one vendor explicitly declining to fix a threshold) moved to
% Appendix~\ref{app:audit:sweep}. Nothing was deleted.
% PROTECTED: the zero, the 10, and that the remaining 6 cite a MEASURED OUTCOME
% rather than a declared tolerance. Do not report the margin_category marginals
% alone: 7 of the 12 category-2 claims contain no number at all, so calling them
% informal *margins* reads as contradicting the zero in the same paragraph.
\textbf{No audited source declares a prospective numerical equivalence margin}
(Table~\ref{tab:audit-taxonomy}). \AuditXtabQualTotal{} of the
\AuditEligible{} make the claim in purely qualitative terms (``negligible'',
``matches'', ``practically no accuracy decrease''), with no number attached to
the assertion at all. The remaining \AuditXtabRetroTotal{} cite a number, and in
every case it is a \emph{measured outcome}: a recovery percentage or an achieved
benchmark score, computed after the evaluation rather than set before it. This
is established over complete source text, not the quoted sentence: every source
was archived and searched in full, including tables, captions, footnotes and
appendices, for a registered vocabulary of tolerance language
(Appendix~\ref{app:audit:sweep}).

The consequence for this section is structural. An equivalence claim with no
declared margin cannot be evaluated against its own standard, because it has
set none; it can only be evaluated against a standard supplied from outside.
Everything below therefore uses the margin registered in advance
(\S\ref{sec:audit:rules}), and no quantity derived from a source's own reported
results is described anywhere in this paper as that source's margin.

\subsection{Where the claim is written}
\label{sec:audit:locus}

% STAGE B, 2026-08-06. The six-card comparison, the tier description and the
% retention judgement for the two boundary cases moved WHOLE to
% Appendix~\ref{app:audit:locus}, which already held tab:audit-locus.
% RETAINED HERE, PROTECTED: the consequence for the denominator (qualification
% 13's floor-not-census reading) and the author-re-verification disclosure
% (qualification 18). This locus review was a second automated pass by the same
% class of tool that produced the record it checked. It is NOT independent
% verification and must never be described as dual coding or inter-rater
% agreement anywhere in this paper.
% STILL OPEN (defect D6): the 3/2/1 tier counts and the six-card denominator are
% hand-typed in the appendix. They are not emitted by gen_denominator_macros.py,
% which is another session's active file. Do not add a second generator.
A second question turns out to matter as much as what form an assertion takes:
\emph{where in the document it is written}, and whether it is written in words at
all. Across six model cards from one publisher with the underlying evidence held
constant, the claim appears in prose in three, as a bare juxtaposition of two
scores in two, and only as a table cell in one
(Table~\ref{tab:audit-locus}, Appendix~\ref{app:audit:locus}). The registered
inclusion rule is keyed to a property that varies independently of the evidence,
so the claims do not become weaker as the locus moves from sentence to cell:
they stop being written down. The consequence is that
\AuditFrozenCandidates{} is a floor on the population and not a census of it,
with the shortfall concentrated in exactly the sources that state their claims
least explicitly. This bounds what the counts here can mean without weakening
them, since every reported quantity is computed over the sources that were
captured, and it means the true rate of unbounded equivalence claims in this
literature is understated here rather than overstated.

The locus review is author re-verification against the archived sources, not
independent verification by a second coder; the project has no second human, and
Appendix~\ref{app:extraction} states what that does and does not license. Every
archived source, its content hash, and the retrieval script needed to reproduce
these locations are released with the paper, so the classification is checkable
by any reader without re-fetching anything.

\subsection{Availability of per-item outputs}
\label{sec:audit:v3}

The most actionable finding requires no statistics at all.

% SOURCE: results/audit_verdicts_rev3.csv column v3_per_item_outputs over the 16
% ELIGIBLE rows: 0 "yes", 3 "partial" (R08, R15, R16), 13 "no". R10's row is
% "no" and is excluded here, which is why the count is 13 and not 14.
%
% THE QUALIFIER IS LOAD-BEARING AND MUST STAY IN THE SAME SENTENCE. Three
% sources DO release per-item outputs -- for other task suites. "None released
% per-item outputs" is false without "task-matched".
\begin{quote}
\textbf{\AuditPerItemTaskMatched{} of the \AuditEligible{} eligible sources
release \emph{task-matched} per-item outputs}, meaning the item-level results,
for the tasks the equivalence claim is actually about, that a third party would
need to rerun the paired comparison. The tally is \AuditPerItemTaskMatched{}
\emph{yes}, \AuditPerItemOtherTaskOnly{} \emph{partial}
(\AuditPerItemOtherTaskClaims{}), \AuditPerItemNone{} \emph{no}.
\end{quote}

% STAGE B, 2026-08-06: the suite-by-suite detail for the three partial sources
% and the repair-cost argument moved to Appendix~\ref{app:audit:v3detail}.
% PROTECTED AND RETAINED: the qualifier that the three DO release per-item
% outputs, for other suites. "None released per-item outputs" is false without
% "task-matched", and the zero above is meaningless without this sentence.
\AuditPerItemOtherTaskClaims{} come closest: they release per-item outputs for
other suites, but not for the tasks their audited equivalence claim is about, so
the released artifacts and the asserted claim do not intersect
(Appendix~\ref{app:audit:v3detail}). This finding is more actionable than any
power calculation because the two failures have different repair costs.
Underpowering is fixable by evaluating more items, and \S\ref{sec:certification}
says how many. Irreproducibility is not fixable downstream at all: with no
per-item outputs, nobody outside the releasing organisation can run the paired
test at \emph{any} sample size, cannot compute churn, and cannot check the
arithmetic. Per-item outputs for a benchmark of a few thousand items are a file
of a few megabytes, and the gap between that cost and its consequence is the
single clearest reporting-standards recommendation this paper makes.

\subsection{Verdict rules}
\label{sec:audit:rules}

% STAGE C, 2026-08-06. The three estimators, eq:tost-n and the one-sided/90%
% convention moved WHOLE to Appendix~\ref{app:audit:verdictrules}; the
% tier-by-tier imputation detail was already in
% Appendix~\ref{app:audit:imputation}. eq:tost-n has no reference outside this
% file, so it moved with the equation.
% RETAIN VERBATIM: the margin sentence below is the logical hinge of the section
% (mandatory qualification 5) and has now survived two compressions unaltered.
Because no source declares a margin, \textbf{the applicable margin throughout is
the uniform \AuditMarginPP{}\,pp registered in advance}; a source's reported
deltas are outcomes of its evaluation, not a decision rule it adopted, and are
never used as one.

For each claim, at its reported or rule-imputed sample size, the frozen protocol
computes three quantities: \emph{V1}, the minimum detectable difference under
the paired-flip model; \emph{V2}, the number of items TOST would require at the
applicable margin; and \emph{V3}, whether per-item outputs were released. A
claim is recorded as \emph{below the approximate planning threshold} iff its
reported $n$ falls below the V2 requirement.
Appendix~\ref{app:audit:verdictrules} gives the estimators and the one-sided
$z$ convention, under which the requirement is that a 90\% two-sided interval
fall inside the margin.
% WORDING RULE (Amendment 2 + carry checklist §8): a PROSPECTIVE PLANNING
% quantity, not a retrospective diagnosis. Do not reintroduce a definitive
% underpowered verdict here.
That requirement answers a question asked \emph{before} an evaluation is run,
namely how many items it would need, so falling below it is a statement about
how the evaluation was sized, not a diagnosis applied to its result.

% RELOCATED 2026-07-27: tier-by-tier match counts and the None-descent rule are
% in Appendix~\ref{app:audit:imputation}. Nothing was deleted.
The discordance rate $p_d$ is reported by no source, so it is imputed from the
atlas (\S\ref{sec:atlas}) by matching the nearest (method family, bit width,
benchmark) cell, most-specific tier first, taking the \emph{median} over the
first non-empty tier because per-cell discordance is right-skewed
(Appendix~\ref{app:audit:imputation}). Because $p_d$ is imputed and never
reported, each verdict is additionally recomputed at the first and third
quartiles of the same atlas cells that supplied its median.
% CHRONOLOGY DISCLOSURE, REQUIRED (carry checklist §8). Added 2026-07-31, AFTER
% the point-imputation result was seen. Saying so is not optional and it must
% not be phrased so as to imply it was planned.
This quartile sweep was added after the point-imputation results had been seen,
and is reported as post-hoc sensitivity, not as a registered analysis.
% Monotonicity, not cell-counting, is what makes the interval claim valid.
Because $n_{\mathrm{req}}$ is increasing in $p_d$, the two quartiles bracket the
whole interval: a claim above threshold at $Q_3$ is above it throughout, and one
below threshold at $Q_1$ is below it throughout. The interval statement is
established at its endpoints, not inferred from the scatter of observed cells.

\subsection{Results}
\label{sec:audit:results}

% SOURCE: results/audit_verdicts_rev3.csv columns eligible, indeterminate,
% v2_underpowered_paired_2pp, robustness. Counts over the 16 ELIGIBLE rows.
% DENOMINATOR LEDGER (carry checklist §9): 17 - 1 = 16; 11 + 5 = 16;
% 0 + 1 + 10 = 11. Every one of these is checkable in the CSV.
Of the \AuditEligible{} eligible claims, \AuditNotAssessable{} are \textbf{not
numerically assessable}: their reporting does not support a verdict under the
registered framework, leaving \AuditAssessable{} assessable claims. Of those
\AuditAssessable{}, \AuditBelowThresholdAtMedian{} falls below the
approximate planning threshold at the registered \AuditMarginPP{}\,pp margin
under the median discordance imputation, and that one claim's classification
does not survive the sensitivity analysis.

% SUPERSEDED TABLE, DO NOT RESTORE. This replaces tab:audit-underpowered, whose
% four rows were flagged at their own reported deltas and are ALL robustly above
% the threshold at 2 pp. The label itself was a stale claim, so it was renamed
% rather than recaptioned.
% A one-row successor table naming only R01 was considered and REJECTED: a table
% built around the single flag looks constructed to produce it. The main text
% carries the three-way classification; all 11 rows are in the appendix.
\begin{table}[!t]
\centering
\caption{Sensitivity classification of the 11 numerically assessable claims at
the registered 2\,pp margin. Each claim's required sample size is recomputed at
the first and third quartiles of the atlas cells that supplied its median
discordance; because required $n$ increases monotonically in the discordance
rate, the quartiles bracket the whole interval. Per-claim values are in
Appendix~\ref{app:audit-table}.}
\label{tab:audit-sensitivity}
% SOURCE: results/audit_verdicts_rev3.csv column `robustness` over the 11
% eligible determinate rows, via the generated \Audit* macros in
% paper/audit_denominators.tex: "robustly above threshold" =
% \AuditAboveThroughout, "imputation-sensitive" = \AuditChangesWithinIQR (R01),
% "robustly below threshold" = \AuditBelowThroughout.
% DEFECT D5, FIXED 2026-08-04: these three cells were HAND-TYPED as 10, 1, 0.
% No section of this paper types an audit count; that rule exists because the
% retired "4 of 12" headline outlived the verdicts that produced it.
\begin{tabular}{lr}
\toprule
Classification across the atlas-IQR interval & Claims \\
\midrule
Above the planning threshold throughout          & \AuditAboveThroughout{} \\
Changes classification within the interval       & \AuditChangesWithinIQR{} \\
Below the planning threshold throughout          & \AuditBelowThroughout{} \\
\midrule
\textbf{Total assessable}                        & \textbf{\AuditAssessable{}} \\
\bottomrule
\end{tabular}
\end{table}

% STAGE C, 2026-08-06: the reversal-point and quartile arithmetic moved to
% Appendix~\ref{app:audit:r01}; the detection-direction reading of
% tab:audit-mdd moved to Appendix~\ref{app:audit:fullrobustness}; the reasoning
% behind the two sensitivity directions was already in
% Appendix~\ref{app:audit:robustness}.
% THE 43.6% IS DESCRIPTIVE. It is the share of reference cells lying below the
% reversal point. It is NOT a posterior probability, NOT a confidence level and
% NOT a p-value, and the atlas cells are correlated (shared model pairs,
% benchmark families, sources and infrastructure), so they are not independent
% draws from anything. Never attach an inferential reading to it. The number and
% its framing stay in ONE sentence.
The single flagged claim is \AuditSensitiveClaim{}, the GPTQ paper, which
reports $n = \AuditSensitiveN{}$ against a requirement of
$\AuditSensitiveNReq{}$ items at an imputed discordance rate of $0.130$. Its
classification reverses at a rate of $0.1189$, and
$\AuditSensitiveCellsBelow{}$ of the $\AuditSensitiveCellsTotal{}$ atlas cells
supplying the imputation lie below that point
(Appendix~\ref{app:audit:r01}). This is a sensitivity-dependent planning flag,
not a verdict: the $\AuditSensitiveCellsPct{}\%$ is a descriptive share of
reference cells, not a probability that the claim is underpowered, and those
cells share models, benchmarks and infrastructure and are not independent
observations.

No assessable claim falls below the threshold throughout the interval.
Table~\ref{tab:audit-sensitivity} is therefore best read as a statement about
resolution, not about error: at the margin a reporting standard would plausibly
impose, ten of these eleven evaluations were sized to carry the claim made on
them, and the eleventh cannot be classified without committing to a discordance
rate its authors never reported. Nothing here says any model is degraded.

% CARE -- THE TWO SENSITIVITY DIRECTIONS ARE DIFFERENT FACTS AND MUST NEVER BE
% MERGED INTO ONE SENTENCE. Margin sensitivity is instability with respect to
% the yardstick; imputation sensitivity is instability with respect to an input
% the sources did not report. They coincide on R01, which is a coincidence.
The same conclusion appears in the detection direction, where the
independent-binomial columns are uniformly worse by roughly a factor of two
(Table~\ref{tab:audit-mdd}, Appendix~\ref{app:audit:fullrobustness}); an audit at
a \AuditMarginPP{}\,pp margin is a weak test and should be understood as one.
Second, \textbf{R04 and R14 carry no verdict}; their numbers are computable and
are retained in the released CSV for transparency, but they are excluded from
the assessable set (\S\ref{sec:audit:indeterminate}), and the appendix table
italicises them for that reason. Finally, \AuditSensitiveClaim{} is unstable in
two independent directions that must not be read as one finding: it is
\emph{margin-sensitive}, flipping across the registered
1\,pp\,$\to$\,3\,pp sweep, so it turns on where the yardstick is set, and
separately \emph{imputation-sensitive}, flipping across the interquartile range
of the atlas cells supplying its discordance rate, so it also turns on a
quantity its source never reported. No other assessable claim is sensitive in
either direction (Appendix~\ref{app:audit:robustness}).

\subsection{Claims that cannot be assessed}
\label{sec:audit:indeterminate}

% SOURCE: results/audit_verdicts_rev3.csv columns indeterminate,
% indeterminate_kind, indeterminate_reason, over the 16 eligible rows.
% DENOMINATOR: 5 of 16, not of 17. R10 is eligible-excluded, not indeterminate.
% THE 4 + 1 SPLIT IS MANDATORY AND MUST NOT COLLAPSE INTO ONE NUMBER.
% STAGE C, 2026-08-06: the per-claim blockers for R02, R11, R13 and R14 and the
% retained-components list moved to Appendix~\ref{app:audit:indeterminate}. The
% R14 trap paragraph below STAYS IN THE BODY (mandatory qualification 12) and is
% the body's only statement of it.
% NEVER write "incompatible with a paired framework" for R04: CIDEr supports
% paired resampling perfectly well; it is the flip model that does not apply.
\AuditNotAssessable{} of the \AuditEligible{} eligible claims cannot be assessed
numerically, in two kinds, each recorded with exactly one primary blocker.
\AuditNotAssessableInsufficient{} are cases of \emph{insufficient reporting},
where a registered input is genuinely absent: no sample size, no baseline, or
headline equivalence evidence existing only as a chart image with no extractable
numbers. The remaining \AuditNotAssessableOutsideFramework{},
\AuditOutsideFrameworkClaim{}, is \emph{outside the registered calculation}: it
reports enough, but about a quantity our registered \emph{binary paired-outcome}
model cannot score (\S\ref{sec:audit:r04}). The per-claim blockers are in
Appendix~\ref{app:audit:indeterminate}. Every non-assessable claim retains
whatever components its available inputs support, reported as supplementary
transparency only and \textbf{never verdict-bearing}.

% R14 IS THE TRAP THIS PARAGRAPH EXISTS TO CLOSE (carry checklist §10). Its
% imputed n = 728 sits just under the 742 that the 2 pp calculation would
% require, so a reader who sees the numbers and not the blocker will assume it
% was quietly dropped for being awkward. Say the number, then say why it does
% not count. A regression test enforces the same thing in the toolkit: an
% assessable = false row can never carry a threshold verdict.
% THIS PARAGRAPH STAYS IN THE BODY (mandatory qualification 12). The italicised
% no-verdict rows of tab:audit-mdd moved to the appendix in the same commit, so
% this is now the body's only statement of it.
R14 deserves a word, because its numbers look assessable and are not. Its
imputed sample size of $728$ falls just short of the $742$ the 2\,pp calculation
would require, close enough that a reader might suspect it was set aside for
being inconvenient. It is set aside because the missing baseline is a registered
input: without it there is no paired comparison to size, and the $742$ is a
requirement for a calculation that cannot be performed. The proximity is a
coincidence with no bearing on the count, and R14 does not enter the threshold
tally in either direction.

\emph{Outside the registered calculation} (\AuditNotAssessableOutsideFramework{}).
\AuditOutsideFrameworkClaim{} (AWQ) reports enough, but about a quantity our
registered \emph{binary paired-outcome} model cannot score; see below. Every
non-assessable claim retains whatever components its available inputs support,
listed in the CSV column \texttt{determinate\_components} and reported as
supplementary transparency only, never verdict-bearing: R13 retains V2 (the
paired standard deviation depends on discordance, not on baseline accuracy), R14
retains V1 (paired) and V2, and R04 retains V1 and V2 computed on a substituted
benchmark.

This category is itself a result. Two of the four insufficiently-reported claims
are among the most-cited results in the field, and their headline equivalence
evidence is a chart image with no extractable numbers. That a mechanical,
pre-registered audit cannot evaluate them is precisely the reporting-standards
problem this paper exists to address: the claim may well be true, but it has been
placed beyond the reach of checking.

\subsection{R04: outside the registered calculation}
\label{sec:audit:r04}

% SOURCE: results/audit_verdicts_rev3.csv row R04 columns indeterminate_kind,
% indeterminate_reason, notes.
% WORDING RULE (carry checklist §15): R04 is outside OUR REGISTERED BINARY
% PAIRED-OUTCOME CALCULATION. Do NOT write "incompatible with a paired
% framework" -- CIDEr supports paired resampling perfectly well; it is the
% flip model, not pairing, that does not apply.
% K-HISTORY RELOCATED 2026-08-04 (operation 14) to
% Appendix~\ref{app:prereg:choices}, interpretive choice 3, which already
% carried the K = 5 -> K = 4 transition and the 38.3x figure in full. Nothing
% was deleted; the body keeps the ruling and its cost.
R04 is recorded because excluding it removed what was, at the time, the audit's
largest single number. The AWQ paper's qualifying sentence, the one that meets
the frozen §3 inclusion trigger, asserts negligible loss on \emph{COCO
CIDEr}, a generation metric that assigns a graded score to a caption and has no
per-item correct/incorrect state. V1 and V2 are flip-model quantities defined on
$d_i \in \{-1,0,+1\}$, and there is no discordance rate to impute because there
is no per-item accuracy state to be discordant about. This is a limitation of
\emph{our registered calculation}, not of paired analysis: a graded metric
supports paired resampling on the same items perfectly well, and a certificate
for it would be a straightforward extension. It is simply not the model we
registered.

% STAGE D, 2026-08-06: the overruled first-pass GSM8K computation moved to
% Appendix~\ref{app:audit:r04detail}. The body keeps the ruling, that the number
% is not claimed as a result, and its cost.
Excluding it was not free. The first extraction pass had scored R04 on GSM8K,
the source's own accuracy benchmark, and reported it as the audit's largest
shortfall; that reading was overruled because computing a TOST requirement on
GSM8K audits a sentence the source wrote about a different benchmark, in
different and non-trigger language. The computation is retained in the released
CSV as a labelled transparency column, and \textbf{it is not claimed anywhere in
this paper as an audit result} (Appendix~\ref{app:audit:r04detail}). An audit's
currency is unimpeachability, and it is not spent on its own largest number.

% QUALIFICATION 17, PLACED IN THE BODY 2026-08-06. The K sequence is the
% section's canonical self-correction and MUST NOT live only in an appendix. It
% was previously in this file's header comment and in app:prereg:choices, so no
% reader of the paper could see it; the compression ledger caught that. The
% arithmetic of each step stays in the appendix; the sequence itself is here.
% SOURCE: sections/appendix_prereg_detail.tex, interpretive choice 1.
The count of claims below the planning threshold moved four times before it
settled, and the order in which the numbers arrived is itself part of the
disclosure. A first pass applying the registered \AuditMarginPP{}\,pp margin
uniformly returned $K = 1$ of 12. Re-reading the frozen label produced $K = 5$;
the R04 ruling above moved one claim out of the determinate set, giving the
$K = 4$ that was reported for ten days. Amendment~2 then returned the analysis
to the uniform registered margin, where the rev-3 recomputation gives
\textbf{\AuditBelowThresholdAtMedian{} of \AuditAssessable{}} assessable claims
below the threshold, the same claim the very first pass had flagged. The
claim-derived margins and the shortfall range computed under the superseded
reading are \textbf{withdrawn, not recomputed}, and are non-verdict-bearing
wherever they still appear as history
(Appendices~\ref{app:audit:history} and~\ref{app:prereg:choices}).

% TRIMMED 2026-07-27 (phase 4, low-cost). The "Establishes" half restated
% findings (i)-(iv) from \S\ref{sec:audit:v3} and \S\ref{sec:audit:results}
% verbatim; deleted as redundancy. The "Does not establish" half is what a
% reader must not overread and is kept whole, as is the granularity caveat.
% MERGED 2026-08-04: this was a separate closing subsection and is now the
% section's close (prose rule 6). Every clause is retained, including the only
% statement in the body of what "robust" means.
The findings above hold at the reported sample sizes and under the frozen
protocol as amended, and they are claims about evidence, not about models. This section \textbf{does not establish}: that any audited model is
degraded; that any audited claim is false; that the claims' authors reached a
wrong conclusion; or that any claim is underpowered in a sense that survives the
sensitivity analysis, and none is.
% SCOPE RULE (carry checklist §8 and §15). Two overreadings to block explicitly:
% (a) generalising 16 audited sources to a prevalence claim about the field,
% (b) reading "robust" as anything wider than the atlas-IQR interval actually
% swept. Both are cheap to write and expensive to retract.
% THE SECOND OF THOSE IS A SINGLE POINT OF FAILURE: mandatory qualification 9
% has no other home in the body. Do not delete or weaken the sentence beginning
% "Where a classification is called robust".
Nor does it establish a prevalence: \AuditEligible{} eligible sources within
three frozen frames are not a sample from which the field's reporting practice
can be estimated, and no proportion reported here should be read as one. Every
numerical result here also rests on a discordance rate that no source reported
and that is imputed from the atlas, which is why each verdict is recomputed
across the interquartile range of the cells supplying it and why the one flagged
claim is reported as sensitivity-dependent rather than as a finding. Where a
classification is called robust, that means only that it holds throughout the
interquartile range of the atlas cells supplying its discordance rate, not
across every plausible model of discordance. It also does not
establish anything about sources outside the three frozen frames, and it
operates at claim level and not at claim\,$\times$\,benchmark granularity,
because that is the granularity of the frozen claim table
(Appendix~\ref{app:prereg:choices}, interpretive choice~4).
```

---

## FILE: `paper/sections/minigrid.tex`

```latex
% =====================================================================
% Section: Controlled seed-paired experiment (H3).
%
% RESTRUCTURED 2026-08-04 (flagship narrative, operations 2, 3, 9, 10, 12, 13).
% MOVED TO Appendix~\ref{app:minigrid-detail}, NOTHING DELETED:
%   sections/minigrid_escalation.tex   (whole file, now app:escalation; the file
%                                       is deleted and its \input removed)
%   tab:h3-ds, tab:h3-resolution       (whole)
%   tab:h3-variance / tab:h3-bootstrap / tab:h3-flips -> tab:h3-supporting,
%                                       one float, three panels, no column lost
%   §"Deferred registered analyses"    (whole)
% FOLDED IN: sections/discriminant.tex, which is deleted. Its argument belongs
% in \S\ref{sec:minigrid:resolution}, where the figures it reads are reported;
% its historical pilot moved to Appendix~\ref{app:minigrid:pilot}. NOTHING IS
% COMPUTED HERE that was not already computed there.
%
% FILLED 2026-07-27. All eight registered confirmatory cells exist, the
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
%    discounting it, or constructing any reduced-cell variant is not.
%  - The registration forbids collapsing seed-level SD into item-level SE; they
%    are reported as separate variance components and must stay separate.
%  - The resolution analysis is POST-HOC and is labelled as such at every
%    appearance, with its provenance carried from the results document.
% =====================================================================

\section{Cancellation is worse where practitioners choose}
\label{sec:minigrid}

\subsection{Design}

% SOURCE: PREREGISTRATION.md §"Experimental Grid" and §"H3 Decision Rule";
% docs/MINIGRID_REGISTRATION_2026-07-15.md §§1-2.
% MANDATORY ENUMERATION (qualification 14): 8 cells, 2 tasks, 2 methods,
% 4 models, 4 bits, 5 seeds, and what it licenses no statement about. Compress
% around it, never through it.
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
interaction and not to the two methods having seen different data. Selected
document indices and token hashes are persisted. The chat template is on for
every method including the FP16 baselines; GSM8K uses one inline few-shot
example and test indices 0--999; MMLU uses the full test split.

% SOURCE: PREREGISTRATION.md §"H3 Decision Rule" and §"Hierarchical aggregation
% across calibration seeds".
Per cell, with $d_s = \mathrm{acc}_{\mathrm{GPTQ},s} - \mathrm{acc}_{\mathrm{AWQ},s}$:
a \emph{winner flip} occurs when two seeds give $d_s$ and $d_t$ of
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
each selected seed, items, with GPTQ and AWQ retaining the same sampled seed
labels and item indices.

% SOURCE: docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 3, 4;
% docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md (SIGNED);
% docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED).
The eight cells were built in two stages, and the second stage was authorized by
the first under a rule frozen before either ran. Four cells ran first; the 7B/8B
cells sat behind a mechanical escalation screen, described with its per-cell
outcomes in Appendix~\ref{app:escalation}. That screen fired, the deferred cells
were built and evaluated, and the frozen
Supported/Disconfirmed/Inconclusive rule was then applied once over all eight.
Two properties of that sequence matter for how the verdict should be read. The
screen decides only \emph{which cells to build} and states no H3 outcome, so the
confirmatory rule was never applied to a cell set chosen after its own result
was known. And the rule is defined over all eight cells and was applied only
when all eight existed. No reduced-cell variant was constructed at any point.

\subsection{The eight-cell verdict}
\label{sec:minigrid:verdict}

% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED 2026-07-26,
% commit 05c86f2), "Mechanical application of the rule" and "H3 VERDICT".
% Counts: winner flip 5/8 (threshold >=3), range/gap 7/8 (threshold >=4),
% max_range < 0.5*gap in 1/8 (disconfirm threshold >=6). Ties: 0 of 8 cells,
% 0 of 40 triples.
Applied once, mechanically, to all eight cells:
\textbf{H3 is supported.} The winner reverses across seeds in \textbf{5 of the 8}
cells against a threshold of 3, and the range/gap criterion holds in
7 of the 8 against a threshold of 4. The supported limb of the frozen
rule is a disjunction, and \emph{both disjuncts are satisfied independently}:
either one alone would have returned the same verdict. The disconfirming limb is
a conjunction, and both of its conjuncts fail. It requires winner flips in at
most 1 of 8, and there are 5, and it requires
$\max\mathrm{range} < 0.5\,\mathrm{gap}$ in at least 6 of 8, which holds in 1.
The two limbs cannot both hold and do not, so the frozen text classifies the
outcome with no interpretation required.

No exact accuracy tie occurs anywhere in the confirmatory set: 0 of 8
cells contain one, over 0 of 40 (model, task, seed) triples. The
registered tie convention, under which a tie is neither a flip nor a non-flip
and can neither create nor erase a flip between two non-tied seeds, therefore has no
effect on any cell's classification, and the denominator for both criteria
remains all eight cells.

What the verdict says is bounded by what was registered. Over the eight cells,
the choice between GPTQ and AWQ at 4 bits is not stable against
calibration-seed randomness alone. It licenses no statement about 3-bit
behaviour, ARC-Challenge, HellaSwag, calibration-\emph{dataset} effects, or any
cell outside the registered set; the FP16 baseline gate governs the baseline
only and says nothing about quantized accuracy.

% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md, "Per-cell registered
% quantities" (all eight cells) and "Mechanical application of the rule".
% Values are read from that record at the six decimals it publishes.
% The four mini-grid rows also reproduce the signed 2026-07-23 escalation record
% exactly (KNOWN_ANSWER: PASS, 4/4 cells) -- see app:escalation.
Table~\ref{tab:h3-eightcell} gives the two rule inputs per cell, and
Table~\ref{tab:h3-ds} in Appendix~\ref{app:minigrid:ds} gives the per-seed
differences $d_s$ behind the winner-flip column, so every flip determination is
checkable by inspection of sign.

\begin{table}[!t]
\centering
\small
\caption{The eight registered confirmatory cells. $\mathrm{gap}$ is the absolute
difference of the two five-seed mean accuracies; $\mathrm{range}_m$ is the
seed-wise spread of method $m$; the range/gap criterion holds when
$\max(\mathrm{range}_{\mathrm{GPTQ}},\mathrm{range}_{\mathrm{AWQ}}) \geq
\mathrm{gap}$. Values reproduce the signed decision record.}
\label{tab:h3-eightcell}
% WIDTH FIX 2026-08-05: this table overhung the right margin by 33pt. TeX emits
% no overfull warning for it because the tabular sits inside \centering, so it
% was found by measuring ink position per page rather than from the log.
\setlength{\tabcolsep}{3pt}
\small
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
% WIDTH FIX 2026-08-05: both summary rows spanned all seven columns on one line
% and reached 31pt into the right margin. One statement per row now. Every count
% and threshold is unchanged.
\multicolumn{7}{l}{Winner flip in 5 of 8 (threshold $\geq 3$: met)} \\
\multicolumn{7}{l}{Range/gap in 7 of 8 (threshold $\geq 4$: met)} \\
\multicolumn{7}{l}{$\max\mathrm{range} < 0.5\,\mathrm{gap}$ in 1 of 8 (disconfirm threshold $\geq 6$: not met)} \\
\multicolumn{7}{l}{Exact ties: 0 of 40} \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Supporting analyses}
\label{sec:minigrid:supporting}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, header paragraph and
% slots 2-4. All three tables are Table~\ref{tab:h3-supporting} in
% Appendix~\ref{app:minigrid:supporting}; the readings stay here.
Three further registered analyses were run once per cell as part of the same job
that produced the verdict, and none of them modifies the verdict: it is what the
frozen rule returned over winner flips and range/gap, and a weak bootstrap rate
or a poorly resolved cell is a limitation to report, not a second application of
the rule. Table~\ref{tab:h3-supporting} carries all three.

Variance components are reported side by side and never collapsed into a single
dispersion figure, as the registration requires. The two answer different
questions, namely how much a method's accuracy moves when the calibration seed
changes against how precisely a single seed's accuracy is estimated from the
items. On MMLU the calibration seed moves the number more than the sample of
items does, in every cell: taking per cell the larger of the two seed-level SDs
against its own item-level SE, the ratio runs $1.6$ to $5.9\times$
(Qwen2.5-7B $0.006224$ against $0.003983$; Llama-3.2-3B $0.024925$ against
$0.004214$). On GSM8K the two components are of the same order throughout, and
in \emph{five of the eight} method-by-cell entries the item-level SE is the
larger of the two, so the sample of items is moving the number as much as the
calibration seed is.
% Ratios are arithmetic on panel (a): MMLU per-cell larger-SD/its-SE =
% 4.54, 5.91, 1.56, 3.61 -> range 1.6-5.9. GSM8K SE > SD in 5 of 8 entries
% (qwen1.5b GPTQ+AWQ, llama3b GPTQ+AWQ, llama8b AWQ).

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slot 3 table and
% §"Reconciling winner flips with bootstrap rank-flip rates" (5/8 flips,
% 6/8 bootstrap < 0.05, 3/8 both; the two unstable-on-both cells 0.2575, 0.1260).
The bootstrap and the winner-flip criterion measure different things, and a
reader who assumes otherwise will read them as self-contradictory. A winner flip
asks whether two \emph{individual seeds} disagree on sign, which is H3's
registered question and a description of what happens when a practitioner runs
one calibration and takes the winner. The bootstrap rank-flip rate asks whether
the \emph{five-seed mean} ranking survives resampling seed labels and items
together. The combination is the sharpest form of the finding. Winner flips
occur in 5 of 8 cells; the bootstrap rate is below $0.05$ in 6 of 8; and
\textbf{3 cells have both}: Qwen2.5-1.5B/MMLU ($0.0445$),
Llama-3.2-3B/GSM8K ($0.0220$) and Llama-3.1-8B/MMLU ($0.0405$). In each, some
pair of individual seeds disagrees about which method wins while the five-seed
average ranking survives resampling in more than 95\% of replicates. The
practical reading is the one we intend a practitioner to take away: \emph{a
single calibration run can hand you the wrong winner}, and averaging over the
registered five seeds is substantially more stable than any one of them.

The limitation on that reading, stated plainly. With five seeds the
bootstrap resamples seed labels from a sample of five, so it has limited
resolution on the seed-level distribution. What the low rates bound is the
stability of \emph{this} observed mean under resampling; they do not establish
that five seeds suffice in general, and no result here should be read as
licensing five as a sufficient number. Two GSM8K cells are unstable on both
measures, Qwen2.5-7B/GSM8K at $0.2575$ (515 of 2{,}000 replicates) and
Llama-3.1-8B/GSM8K at $0.1260$ (252 of 2{,}000), and there even the five-seed mean
ranking does not survive resampling, and no amount of seed averaging at
$n = 1{,}000$ rescues the comparison.

\subsection{Cancellation is more complete between two methods than against FP16}
\label{sec:minigrid:churnratio}

% SOURCE: atlas regime from \S\ref{sec:atlas:netgross}
% (docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1). Controlled regime is arithmetic
% on panel (c) of Table~\ref{tab:h3-supporting}: churn / |net delta| per cell =
% 15.31, 3.04, 6.07, 11.72, 17.95, 30.45, 10.47, 13.70; min 3.04, max 30.45,
% median 12.71. The extreme cell is Qwen2.5-7B/GSM8K, read directly from the
% slot 4 row.
% TWO POINTS, NOT A CURVE. Do not restate this as a monotone relationship.
% AGGREGATIONS MADE LIKE-FOR-LIKE 2026-08-05 (defect D4;
% docs/HEADLINE_CHURN_RATIO_DEFINITION.md). This Result used to set the atlas
% $5.3\times$ against the controlled $12.7\times$. Those are DIFFERENT
% aggregations: 12.7 is the median of the eight per-cell ratios, while the atlas
% headline is a ratio of medians. Table~\ref{tab:churn-aggregations} now gives
% BOTH aggregations in BOTH regimes, so the comparison cannot be read off a
% mismatched pair, and the direction is shown to survive the choice.
% DO NOT REDUCE THIS TO WHICHEVER PAIRING GIVES THE LARGER CONTRAST. The
% like-for-like contrast (3.3x) happens to exceed the ratio-of-medians contrast
% (2.2x); quoting only the former would be selecting on the answer. Both are
% printed for that reason, and tests/test_churn_ratio.py fails if either
% direction reverses. Every value in the table is generated by
% scripts/churn_ratio.py --check.
\begin{result}\label{res:churnratio}
\emph{Descriptive; not a registered hypothesis and not an inferential test.}
The ratio of per-item churn to aggregate net delta is larger in the
controlled method-against-method contrast than in the observational
quantized-against-FP16 contrast. The ordering is stable across the two
aggregations, which is a robustness check on the choice of summary and not a
significance claim (Table~\ref{tab:churn-aggregations}). Comparing like with
like, the
median of the per-cell ratios is \textbf{3.85} across the atlas
(\S\ref{sec:atlas:netgross}) and \textbf{12.7} across the eight controlled
cells, where the per-cell ratios run \textbf{$3.0\times$ to $30.5\times$};
comparing medians instead, the atlas gives \textbf{5.40} against
\textbf{12.1}.
\end{result}

\begin{table}[!t]
\centering
% SOURCE: scripts/churn_ratio.py --check, over the same two artifacts the rest
% of the paper uses (results/atlas_cells_summary_rev2.csv and
% results/minigrid_supporting/minigrid_supporting.json). Values pinned by
% tests/test_churn_ratio.py. Never hand-edit a cell of this table.
\caption{The churn-to-net-delta ratio under both aggregations, in both regimes.
The two aggregations answer different questions, so the paper reports both
rather than choosing: a ratio of medians describes the typical churn against the
typical net delta, and a median of per-cell ratios describes the typical cell.
The controlled regime exceeds the observational one either way. All figures here
are descriptive summaries of the two populations; the comparison is not a
registered hypothesis and no inferential test is performed on it. The last row is
why the two columns are not exactly parallel: a cellwise ratio is undefined
where the net delta is exactly zero, which never happens in the eight controlled
cells and happens in 145 atlas cells, 6.8\% of S1 and 16.2\% of S2
(\S\ref{sec:atlas:identical}).}
\label{tab:churn-aggregations}
\begin{tabular}{lrr}
\toprule
 & Atlas (observational) & Controlled \\
\midrule
Ratio of medians                    & 5.40            & 12.1 \\
Median of per-cell ratios           & 3.85            & 12.7 \\
Cells entering the per-cell median  & 1{,}562 of 1{,}707 & 8 of 8 \\
\bottomrule
\end{tabular}
\end{table}

The extreme cell makes the size of the discrepancy concrete. On
Qwen2.5-7B/GSM8K the two methods differ by 0.58\,pp in aggregate
accuracy, a gap any reader would call equivalence, while 17.7\% of
items change correctness state between them and 28.7\% of answers
change outright. The mechanism is cancellation, and it follows from what the two
contrasts are. Two quantization methods at the same bit width are far closer to
each other in aggregate than either is to its FP16 baseline. Harmful and
beneficial flips are correspondingly better balanced, cancellation in the
aggregate is more complete, and the surviving net delta therefore hides a
proportionally larger amount of per-item movement.

We observe two regimes; we do not establish a curve. These are two
measured points, one observational contrast at 1{,}707 cells and one controlled
contrast at 8, and nothing here licenses reading the ratio as a monotone
function of aggregate closeness. What the two points support is the direction of
the effect and the fact that the regime in which equivalence claims are actually
made is the less favourable of the two.
% Atlas figures from \S\ref{sec:atlas:netgross}; controlled 3.04 / 12.71 / 30.45
% are the per-cell ratios of panel (c) of tab:h3-supporting. All of them are
% generated and pinned: scripts/churn_ratio.py, tests/test_churn_ratio.py.

\subsection{Which arm of the experiment carries the result}
\label{sec:minigrid:resolution}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, "Step 5 -- resolution
% analysis (POST-HOC)" table and §Disclosure. The disclosure below is carried
% from that document, not paraphrased. PROTECTED: do not drop it, and do not
% move the post-hoc label away from the figures it qualifies.
\textbf{This quantity was not registered.} It was requested on 2026-07-26,
\emph{after} the eight-cell verdict had been computed and signed, in response to
prior art identified the same day,%
\ \citet{paglieri2024outliers}, which reports calibration effects diminishing in
modern LLMs (Appendix~\ref{app:reconcile}). It is descriptive, it tests no
hypothesis, and it does not modify the verdict. It is recorded with its
provenance, not folded silently into the registered results.

Using the machinery of \S\ref{sec:certification} itself, with paired
$\mathrm{sd} = \sqrt{p_d}$ and paired $\mathrm{SE} = \sqrt{p_d/n}$ and $p_d$
the per-cell GPTQ-against-AWQ accuracy-state churn of
Table~\ref{tab:h3-supporting}, the two tasks separate sharply
(Table~\ref{tab:h3-resolution}, Appendix~\ref{app:minigrid:resolution}).

MMLU carries the result. All four MMLU cells satisfy the range/gap
criterion, their seed-induced ranges run $5.5$ to $17.5$ paired standard errors,
their mean gaps run $2.2$ to $8.5$, and their seed-level SD exceeds item-level
SE by $1.6$ to $5.9\times$. The instability is far larger than the measurement
noise, and the benchmark resolves it comfortably.

\textbf{GSM8K is under-resolved at $n = 1{,}000$.} There the ranges run roughly
two to three-and-a-half SE, seed-level SD is of the same order as item-level SE,
and in three of the four GSM8K cells the \emph{mean gap itself} sits at or below
$1.25$ SE ($0.44$, $0.98$, $1.23$), so the quantity the range/gap criterion
compares against is, in those cells, not resolved by the benchmark at the $n$
used. Any per-cell reading of GSM8K should say so, and
\S\ref{sec:limitations} does.

% FOLDED IN 2026-08-04 from sections/discriminant.tex, which is deleted. Nothing
% is computed here: every figure below is read from the resolution analysis
% already reported above and from Table~\ref{tab:h3-eightcell}.
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md step 5 table
% (gap/SE and max_range/SE per cell); docs/H3_EIGHT_CELL_DECISION_2026-07-26.md
% (gap column). qwen25-1p5b/gsm8k gap = 0.096800 = 9.68 pp at 5.65 SE.
The split is also the answer to an obvious objection, that a certification-first
framework demanding thousands of items will simply decline to conclude anything.
The fourth GSM8K cell is the sharp case: Qwen2.5-1.5B posts a GPTQ--AWQ gap of
\textbf{9.68\,pp}, which lands at $5.65$ paired SE, resolved on the same
benchmark, at the same $n = 1{,}000$, under the same test, where its three
siblings are not. Same items, same instrument, opposite verdicts, separated by
effect size and not by any threshold somebody chose. The machinery declines to
adjudicate where the evidence is thin and adjudicates where it is not,
\emph{within} one benchmark at one sample size. A framework that returned
``insufficient evidence'' everywhere could not produce that pattern, and neither
could one tuned to a convenient cut-off.
Appendix~\ref{app:minigrid:pilot} reports the same discriminant behaviour in the
project's earlier public-checkpoint pilot, which adds the case the eight cells
lack, a positive detection.

None of this weakens the verdict. The range/gap criterion holds in 7 of 8 cells
and winner flips occur in 5 of 8, both computed from the registered per-seed
accuracies by the frozen rule, and neither is a significance test. What it means
is that the GSM8K cells carry materially less resolving power than the MMLU
cells, which is a statement about where the evidence concentrates, not a
reweighting of the rule.

\subsection{Resolution of the confirmatory cells against the certification tables}
\label{sec:minigrid:selfaudit}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, §"The paper's own
% table predicted this"; results/certification_tables_rev2.csv, GSM8K rows at
% margin_pp = 2.0 (p25 0.039992 -> 619; median 0.076573 -> 1,184;
% p75 0.198446 -> 3,068). Observed p_d: 0.1766, 0.1808, 0.2086, 0.2940.
% NEUTRALISED 2026-07-31 (advisor review 3.3). The passage argued for its own
% trustworthiness ("a tool that catches its author is worth more than one that
% never had to"). The fact is stronger unadorned.
The certification table of \S\ref{sec:certification} requires, for GSM8K at a
2\,pp margin, about \textbf{1{,}184} items at median discordance and
\textbf{3{,}068} at the p75 discordance. The confirmatory GSM8K cells ran at
$n = 1{,}000$, already below the median requirement, and the discordance
actually observed in them is $p_d = 0.1766$, $0.1808$, $0.2086$ and $0.2940$,
at or above the table's p75, where the requirement is roughly three times the
$n$ used. The certification table therefore predicted this shortfall in advance,
and the same instrument applies to this experiment as to the audited claims.
One caveat bounds the comparison. The table's discordance percentiles describe a
quantized-against-FP16 contrast, while $p_d$ here is GPTQ-against-AWQ. The
required-$n$ column is a function of discordance whatever the pair, so reading
the observed $p_d$ against the table's brackets is legitimate; the percentile
labels are not strictly like-for-like and are used only to locate the magnitude.
```

---

## FILE: `paper/sections/harness_sensitivity.tex`

```latex
% =====================================================================
% Section: Harness-defaults sensitivity study.
%
% TRIMMED 2026-07-26. The "two live defects" motivation, the design /
% pre-named-ratio subsection (with the two-phase Qbar deferral and the declined
% early-inspection amendment), the full condition-B narrative and the MMLU
% C==D collapse argument moved VERBATIM to
% sections/appendix_harness_detail.tex. Nothing was deleted in the move.
%
% RESTRUCTURED 2026-08-04 (flagship narrative, operations 11 and 15):
%   tab:sensitivity-gsm8k + tab:sensitivity-mmlu -> ONE float, tab:sensitivity.
%     Same seven columns, every row kept, both denominators and both reference
%     accuracies carried in group headers. No column dropped, no font reduced.
%   The Bronder cross-domain paragraph moved VERBATIM to
%     Appendix~\ref{app:sensitivity:bronder}.
% BOTH RESULT ROWSETS STAY HERE -- they are the deliverable.
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

\section{Exploratory scoring-pipeline sensitivity}
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
It is a small, preregistered, \emph{exploratory} study on one model and the bridge
item subsets, frozen before any of its own results existed. The motivation is
not hypothetical: this campaign produced two live configuration defects inside
eight days on the pinned \texttt{lm\_eval}~0.4.12, one of which moved reported
GSM8K accuracy $0.232 \to 0.566$ with not one token of model output changed
(Appendix~\ref{app:harness-detail}).

% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.1 (R definition,
% "C_cond and Qbar always reported beside it", undefined-if-zero rule);
% docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md (Qbar(mmlu)=0.199000,
% Qbar(gsm8k)=0.287000); results/harness_sensitivity/qbar_qwen25-1p5b.json.
The headline statistic, fixed before any run, is
$R_{\mathrm{cond}} = C_{\mathrm{cond}}/\bar{Q}$: churn between the reference
configuration and a condition on the fixed FP16 model, over the mean churn of
the ten Qwen2.5-1.5B quantized variants against that model's FP16 cell on the
same items, giving $\bar{Q}(\text{MMLU}) = 0.199$ and
$\bar{Q}(\text{GSM8K}) = 0.287$. So $R$ asks directly how a
configuration change compares with swapping in a quantized model. The protocol
forbids printing the ratio without both inputs, and both appear in every row of
Table~\ref{tab:sensitivity}.

% RELOCATED 2026-08-05 (compression pass, relocation 1). The results table and
% the condition-by-condition reading moved to app:sensitivity:conditions whole.
% The protected Scope paragraph below is UNTOUCHED and stays in the body: every
% clause of it is mandatory.
Across the five conditions the ratio runs $R \in [0.836,\,1.585]$, so on a
fixed model a configuration change moves per-item correctness by as much as, or
more than, swapping in a quantized variant does. The condition-by-condition
table, the directional splits, and the MMLU cell whose net delta is positive
while its churn is on the quantization scale are in
Appendix~\ref{app:sensitivity:conditions}.

% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md (all R values, range
% 0.836--1.585); docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §2 (Llama
% added only after its canary pair passes), §7 (exploratory; licenses no
% confirmatory read; no gate/rule adjusted).
% PROTECTED PASSAGE: every clause of this scope statement is mandatory.
\paragraph{Scope.}
On a fixed FP16 model and matched items, harness configuration moves per-item
correctness by an amount comparable to quantization, with $R \in [0.836,\,1.585]$
across the five conditions and the scoring-filter choice ($R=1.585$) exceeding
the quantization denominator outright, so a compression comparison run under an
unstated or mismatched configuration can be dominated by the configuration.
These caveats travel with the numbers. This is \textbf{one model}
(Qwen2.5-1.5B-Instruct); the Llama-3.2-3B arm is admitted only after its seed-0
canary passes, which has not run, so no Llama $R$ is reported. The items are the
bridge subsets ($n=400$ MMLU, $n=200$ GSM8K), chosen so the study
touches no confirmatory item definition. And the study is
\textbf{exploratory}: it adjusts no gate, no escalation rule, and no
confirmatory analysis, and states no H3 outcome. It contextualises how a
compression score should be read; it decides nothing about the compression
methods themselves.
```

---

## FILE: `paper/sections/artifacts.tex`

```latex
% =====================================================================
% Section: Artifacts.
% TRIMMED 2026-07-26. The datasheet, metadata/identifiers and maintenance
% subsections moved VERBATIM to sections/appendix_artifacts_detail.tex.
% Nothing was deleted in the move.
%
% REWRITTEN 2026-07-27. Was "Five artifacts are released", listing the atlas
% first and omitting the per-item outputs entirely. The per-item outputs are
% not a sixth list item: \S\ref{sec:audit} reports that no ELIGIBLE source
% releases task-matched per-item outputs and \S\ref{sec:conclusion}'s fifth line
% asks the field to, so this section is where the paper's own recommendation is
% either met or not. Named first, with the relationship stated rather than
% implied.
%
% COMPRESSED 2026-08-04 (flagship narrative, operation 15). The per-row digest
% limits for R11 and R13 moved to Appendix~\ref{app:artifacts:datasheet}, which
% already carried them; the extra clauses the body held (expected-drift
% reporting, the not-hash-verified statement, and the fifteen clean re-fetches)
% were carried across in the same commit, so nothing was lost.
%
% COMPRESSED AGAIN 2026-08-05 (flagship narrative, §6 target 0.50 page).
% MOVED TO Appendix~\ref{app:artifacts:released} IN THE SAME COMMIT, NOTHING
% DELETED:
%   - the per-artifact detail (both-forms release of the per-item outputs and
%     the sealed run archives; the atlas's exclusion table and 59-pair manifest;
%     the flipeval function list; the audit artifacts' robustness and
%     transparency columns; the twelve rows per margin at 1, 2 and 3 pp; the
%     reproduction package's contents and the 28 recorded catches)
%   - the named four non-granting sources, the manifest and script filenames,
%     the short-excerpt/own-publisher sentence, and the R11/R13 pointer
%   - the \harnessissue sentence, moved with its "do not upgrade this wording"
%     comment to Appendix~\ref{app:artifacts:maintenance}
% The two \paragraph microheadings were removed under §9 rule 4; the passages
% they headed survive as body paragraphs and as appendix text.
%
% RULE, UNCHANGED: no URL, DOI, or version number may be written here until it
% exists.
%
% RULE, ADDED 2026-08-02, REPOINTED 2026-08-05: docs/audit_sources_20260731.tar.gz
% is a PRIVATE working copy. It must never be described here, or anywhere else
% in the paper, as released, shipped, published, mirrored or downloadable. The
% sentence beginning "The audit reads 17 sources in full" below is the only
% place in this file where the corpus is described, so any future edit that
% promotes the tarball has to pass through it.
% =====================================================================

\section{Artifacts}
\label{sec:artifacts}

% SOURCE: \S\ref{sec:audit:v3}; results/audit_verdicts_rev3.csv column
% v3_per_item_outputs over the 16 ELIGIBLE rows (0 yes, 3 partial, 13 no).
% Counts come from \Audit* macros, not typed here.
% "task-matched" must stay in the same sentence as the zero, or the sentence is
% false: three eligible sources do release per-item outputs, for other tasks.
Six artifacts are released, the first being the one this paper's own audit found
nobody publishes: the per-item outputs, 88 cell JSONL files spanning every cell
of the controlled experiment.
Section~\ref{sec:audit:v3} reports that \AuditPerItemTaskMatched{} of the
\AuditEligible{} eligible sources release \emph{task-matched} per-item outputs,
and Section~\ref{sec:conclusion} asks the field to close that gap. The other
five are the flip atlas, the \texttt{flipeval} package (Apache-2.0; everything
else CC-BY-4.0), the frozen 17-claim audit table and its verdict CSV, the
certification tables, and the reproduction package.

% ADDED 2026-08-02. Final rev-3 checklist §8, Option A, chosen by the author
% 2026-08-02: "if redistribution is not permitted, publish URLs, version
% identifiers, hashes, retrieval scripts, manifests, and compliant excerpts;
% keep full captures private".
% SOURCE, licensing: redistribution review of 2026-08-02, recorded in
% docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md §10. Four sources with no
% third-party republication grant (R11 Meta AI blog, R12 NVIDIA TensorRT-LLM
% doc, R13 and R14 vLLM pages) plus the arXiv default licence over R01-R07.
% SOURCE, provenance: docs/audit_sources_manifest.tsv status column (15 MATCH,
% R11 MISMATCH, R13 NO-BASELINE) and scripts/fetch_audit_sources.py, whose
% UNSTABLE map lists R11 and R12. Offline run 2026-08-02 over the private
% archive: 17 verified, 0 drifted, 0 expected-drift, 0 unverifiable, 0 failed.
% DO NOT write "no source permits redistribution" or any general statement of
% what is lawful. What is claimed here is what was checked and what it found.
% PROTECTED PASSAGE: "their full-text captures are in no release" is verbatim.
The audit reads 17 sources in full, and \textbf{their full-text captures are in
no release}: a redistribution review conducted on 2026-08-02 found four of them
carrying no grant permitting a third party to republish their text, and the
seven method papers under arXiv's default licence, which authorises arXiv rather
than us, so the working archive is kept private. What ships in its place is each
source's URL and pinned version identifier, a SHA-256 per captured file, the
manifest and a retrieval script (Appendix~\ref{app:artifacts:released}).

% RESOLVED 2026-07-30. All four identifiers now exist and are stated, routed
% through main.tex macros so the blind build suppresses them from one switch.
% VERIFIED against the live records, not against a plan document: the version /
% concept split was read from the Zenodo record API (doi vs conceptdoi -- they
% differ only in the final digit), and the dataset's public, ungated state and
% cc-by-4.0 metadata from an unauthenticated client.
% ANONYMITY 2026-07-31: every identifier below goes through a macro defined in
% main.tex. Do not write a URL, DOI or issue number directly into this paragraph.
The archived release is canonical: \textbf{\versiondoi}, which resolves to the
frozen v1.0.0 state this paper describes and not to the latest one. The package
is at \repourl, tag \texttt{v1.0.0}, and the data is mirrored at \dataseturl.
Appendix~\ref{app:artifacts-detail} describes every artifact in full, with the
datasheet, licensing findings, metadata and maintenance statement.
```

---

## FILE: `paper/sections/limitations.tex`

```latex
% =====================================================================
% Section: Limitations.
%
% REWRITTEN 2026-08-05 (flagship narrative pass,
% docs/FLAGSHIP_NARRATIVE_PLAN.md §9 rule 4). This file carried TEN consecutive
% \paragraph{} microheadings and read as a bulleted list in prose clothing. It
% is now two paragraphs: what the observational and audit material cannot
% support, then what the controlled experiment cannot support. NOTHING WAS
% DROPPED -- all ten concerns survive, each compressed to one to three
% sentences, and every number, appendix pointer and qualifier is retained.
%
% Concern -> source, in the order they appear.
%  1 atlas is a record, not a sample:
%      docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §1 population caveats;
%      docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.
%  2 status of the atlas numbers:
%      docs/RESULTS_2026-07-15_ATLAS_AUDIT.md lines 5-7 (the original
%      provisional marking); docs/ATLAS_REV2_CORRECTION_2026-07-21.md
%      §Verification (first spot-check 2026-07-21, 10 cells, 262/262 fields, 0
%      discrepancies, embers jobs 11338401/11338619/11338712/11338745) and
%      §"targeted second spot-check" (14/14 cells, 126/126
%      fields). Both spot-checks have passed, so the provisional marking is
%      lifted here rather than removed: the independent-check requirement is
%      what produced the rev-1 -> rev-2 correction.
%  3 discordance is imputed:
%      results/audit_verdicts_rev3.csv column discordance_match_tier;
%      \S\ref{sec:audit:rules}. REV-1 SURVIVOR, CORRECTED 2026-08-02: this once
%      read "two claims fall through to the global tier", which is rev-1
%      imputation behaviour. Rev-3 has no global tier and no claim matches
%      there; the coarsest tier reached is bit width alone.
%  4 family aggregation: results/certification_tables_rev2.csv column
%      n_atlas_cells (mmlu_pro 5, ifeval 8; all others >= 17), and the scope
%      caveats in \S\ref{sec:certification}. The rev-1 certification narrative
%      that this comment used to cite is superseded and is deliberately not
%      named here. REV-2: the prose read "four families" under rev-1;
%      corrected 2026-07-26.
%  5 claim-level granularity:
%      docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #4.
%  6 audit scope. SCOPE RULE (final rev-3 checklist §5): the counts are
%      prevalences IN THIS SAMPLE. Do not restate them as estimates of how
%      often the field as a whole fails to declare a margin or release outputs;
%      the frames were chosen for auditability, not drawn at random.
% =====================================================================

\section{Limitations}
\label{sec:limitations}

The atlas is a record, not a sample. S1 is community quantizations of 2023-era
models, conditioned on leaderboard coverage, and S2 is one vendor's releases
evaluated by that vendor, so statistics computed over the atlas describe the
evidence the field circulates and not the behaviour of quantization in general.
Its pipeline had two bugs found and fixed during the run, and its numbers were
held provisional pending an independent spot-check; that check has since been
completed twice, with 262 compared fields reconciled on the first pass, which
surfaced the population defect that produced rev-2, and 14 of 14 cells at 126 of
126 fields on the targeted second (\S\ref{sec:prereg-spotcheck}), so the figures
reported here are rev-2 and are no longer provisional, and the delta between the
two revisions is reported (Appendix~\ref{app:prereg:rev2delta}). The audit then
leans on that record: no audited source reports a per-item disagreement rate, so
the audit imputes one from the median of the nearest non-empty atlas tier, and
the tiers actually reached run from the most specific, matching model family,
bit width and benchmark together, down to bit width alone. A claim matched at a
coarse tier rests on a wider and less similar set of cells, so the match tier
and the number of atlas cells behind it are released per claim, the
independent-binomial robustness column bounds the effect of the imputation in
the conservative direction, and Appendix~\ref{app:audit:imputation} names the
weakest such match in the table explicitly. In the certification tables,
per-subject and per-subtask cells are collapsed into families, so a family's
quartile band mixes subject-level with model-level variation; this makes the
p25--p75 columns conservative, and two families rest on fewer than 12 cells and
are indicative only. Audit verdicts are computed per claim, at the pooled $n$
the frozen table records, because operating at a claim\,$\times$\,benchmark
granularity would require inventing rows the freeze does not contain. The three
frames fix the population: sources outside them are not audited, and claims
discovered after the table freeze would form a separately reported post-freeze
stratum. Every proportion reported here describes this audited sample of
\AuditEligible{} eligible sources and is not an estimate of prevalence in the
compression literature, which the three frames were never drawn to represent,
and the audit measures evidential sufficiency only, saying nothing about whether
an audited model is in fact equivalent.

% Concern -> source, continued.
%  7 experimental scope: docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 4;
%      docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED) §"What this verdict
%      does and does not say". RESOLVED 2026-07-27: escalation fired, the 7B/8B
%      cells completed, all eight confirmatory cells exist, so the executed
%      scope is stated rather than the deferred one. THE ENUMERATION AND WHAT
%      IT LICENSES NO STATEMENT ABOUT ARE BOTH MANDATORY -- compress around
%      them, never into them.
%  8 five seeds is few: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md,
%      §"Reconciling winner flips with bootstrap rank-flip rates" (3 of 8
%      cells: winner flip TRUE with bootstrap rate < 0.05) and the registered
%      parameters (2000 replicates, seed 0).
%  9 GSM8K under-resolved: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md,
%      step 5 table (POST-HOC) and §"The paper's own table predicted this";
%      results/certification_tables_rev2.csv GSM8K rows at margin_pp = 2.0.
%      MANDATORY: this is one of only two surviving homes for the GSM8K
%      under-resolution qualification.
% 10 benchmarks and languages: results/atlas_cells_summary_rev2.csv reason
%      column (33 cells, 13.3% of 248 exclusions, carry no binary correctness
%      metric). REV-2: this cited 643, the rev-1 float-scored count that the
%      spot-check retracted; corrected 2026-07-26. Never write "incompatible
%      with a paired framework": it is the flip model that does not apply.
The controlled experiment covers all 8 registered confirmatory cells (1.5B to
8B parameters, two benchmarks, 4 bits, two methods, five seeds) and nothing
beyond them, so the verdict licenses no statement about 3-bit behaviour,
ARC-Challenge, HellaSwag, calibration-\emph{dataset} effects, or any model or
benchmark outside the registered set. The atlas reaches 405B but is
observational; the controlled grid is causal but small, and eight cells is a
small number of cells however cleanly they were obtained. The experiment's
two-level bootstrap (\S\ref{sec:minigrid:supporting}) resamples seed labels from a sample
of five, so it has limited resolution on the seed-level distribution it draws
from, and where its rank-flip rate is low what that bounds is the stability of
the \emph{observed} five-seed mean under resampling. The three cells that
combine a winner flip with a rank-flip rate below $0.05$ should be read as
``one calibration run can mislead, and five were more stable here'', not as a
recommendation of five; a design aimed at the seed-level distribution itself
would need more seeds than the registration committed to. The four GSM8K
confirmatory cells ran at $n = 1{,}000$, where a post-hoc resolution analysis
puts the seed-induced range at roughly two to three-and-a-half paired standard
errors and the mean gap itself at or below $1.25$\,SE in three of the four cells
(\S\ref{sec:minigrid:resolution}), and seed-level SD and item-level SE are of
the same order there, where on MMLU the seed term dominates. This paper's own
certification table asked for about $1{,}184$ GSM8K items at median discordance
and $3{,}068$ at p75, and the discordance observed in these cells sits at or
above p75, so the shortfall was predicted by \S\ref{sec:certification} before it
was measured (\S\ref{sec:minigrid:selfaudit}); the verdict is unaffected, being
a count over the frozen rule and not a significance test, but the MMLU cells
carry the evidence and any per-cell reading of GSM8K should say so. Finally, all
benchmarks are English and predominantly multiple-choice or short-answer, with
per-item correctness defined by the original harness, and float-scored
generation tasks are outside the flip model entirely: 33 atlas cells were
excluded for exactly this reason, so nothing here applies to quality claims
about open-ended generation, including the CIDEr-style metric that put
\AuditOutsideFrameworkClaim{} outside our registered binary paired-outcome
calculation (\S\ref{sec:audit:r04}). That is a limit of the flip model we
registered, not of paired analysis, which handles graded metrics perfectly well.
```

---

## FILE: `paper/sections/conclusion.tex`

```latex
% =====================================================================
% Section: Conclusion. The proposed reporting standard is the part a reader
% should be able to copy into a model card, so keep it short, concrete, and
% free of hedging.
%
% REWRITTEN 2026-08-05 (flagship narrative pass,
% docs/FLAGSHIP_NARRATIVE_PLAN.md §1). The close now returns to the cell the
% paper opened on, Figure~\ref{fig:cancellation}, so the argument ends where it
% started. The five numbered lines are unchanged in substance and are the
% deliverable.
%
% EMPHASIS: the \textbf{} spans on the five list items are run-in headings for
% a copyable checklist, not emphasis competing inside prose, and they stay. The
% one \textbf{} span that WAS in prose (on the audit counts, first paragraph) is
% removed, per §9 rule 5.
%
% D4: the $5.3\times$ site in item 3 is EXISTING and is reproduced unchanged.
% New prose states the same fact as "about five times", which holds under every
% derivation of it; do not introduce $5.3\times$ at a new site.
% =====================================================================

\section{Conclusion: a reporting standard for compression claims}
\label{sec:conclusion}

% SOURCE: Figure~\ref{fig:cancellation} and paper/figures/fig1_values.json.
% SCOPE, from the figure caption: this cell is illustrative and is the most
% extreme of the eight. The sentence below says so. The 2,730 figure is a
% planning requirement at an assumed true difference of zero; it must never be
% written as evidence that the two methods differ.
Figure~\ref{fig:cancellation} is one evaluation of one model, and it is the
argument in miniature. Two 4-bit quantizations of Qwen2.5-7B that sit $0.58$
points apart on GSM8K disagree on $17.7\%$ of the items; certifying equivalence
at a declared $\pm 2$-point margin needs $2{,}730$ items and the evaluation ran
$1{,}000$; and which of the two comes out ahead changes with the calibration
draw. None of that is visible in the two aggregate scores. The cell is the most
extreme of the eight registered cells, but the mechanism is not peculiar to it:
across the $1{,}707$ cells of the public record, median churn is about five
times the median net accuracy delta.

% Counts are \Audit* macros from paper/audit_denominators.tex. The
% task-matched qualifier and the three other-task releases stay in the same
% sentence as the zero: without them the claim is false (\S\ref{sec:audit:v3}).
The claim ``near-lossless'' is cheap to write and expensive to support. This
paper measured the gap, and what the measurement mostly found was absence, not
error. Across \AuditEligible{} eligible sources, none declares a
prospective numerical equivalence margin and none releases \emph{task-matched}
per-item outputs, though \AuditPerItemOtherTaskOnly{} release outputs for other
tasks only; \AuditNotAssessable{} cannot be assessed at all from what they
report. Of the \AuditAssessable{} that can, \AuditAboveThroughout{} stay above
the approximate planning threshold at a uniform \AuditMarginPP{}\,pp margin
throughout the interquartile range of the imputed discordance rate, and
\AuditChangesWithinIQR{} cannot be classified without committing to a discordance
rate its source never reported; \AuditBelowThroughout{} stay below the threshold
throughout that interval. These are prevalences in this audited sample of
\AuditEligible{} eligible sources, not estimates for the literature. The
apparatus that closes the gap is equivalence certification at a declared margin,
with sample-size tables computed from observed churn and not from assumed
variance.

% Sequential certification was a full section in earlier drafts. It is a
% registered-but-unrun component and a results-free section reads as padding, so
% it is reduced to this sentence (2026-07-26). Restore the section only when the
% dated registration document exists under docs/ AND the component has run.
The same apparatus is being extended to anytime-valid sequential certification,
in which a confidence sequence lets an evaluation be monitored continuously and
stopped as soon as the model is certified; that component is registered but has
not yet been run, and no results for it are reported here.

% RECAP, NOT INTRODUCTION (2026-08-05). The five lines are now stated in outline
% at the end of \S\ref{sec:intro}; this is where they are stated in full, with
% the evidence for each in hand. Keep both. The early copy carries no numbers
% and the full copy carries them, so there is exactly one home for each figure.
The five lines named in \S\ref{sec:intro} can be stated in full now that the
evidence for each is in hand. A model card or method paper can adopt them
directly.

\begin{enumerate}
  \item \textbf{Declare a margin.} ``Equivalent'' without $\pm m$ is not a
  testable statement. State the margin before evaluating.
  \item \textbf{Run the paired test.} Report TOST at your margin, not just a
  non-significant difference test. Failing to detect a difference is not
  equivalence.
  \item \textbf{Report churn next to net delta.} They are different quantities;
  in the public record churn runs roughly five times the net delta, and about one
  evaluation cell in twelve posts an identical score while still disagreeing on
  items.
  % "ONE IN TEN" CORRECTED 2026-07-27. \S\ref{sec:atlas:identical} retired that
  % phrasing on 2026-07-26: it was near-exact for rev-1's 9.78% share and
  % overstates rev-2's 8.49% (= 1 in 11.8). The atlas comment says explicitly
  % "do not restore one in ten"; this restatement in the conclusion was missed.
  % REV-1 SURVIVOR, CORRECTED 2026-07-27: read "five to six times", which was
  % the rev-1 ratio. See \S\ref{sec:atlas:netgross}.
  \item \textbf{Cite the sample size you met.} Table~\ref{tab:certification}
  gives the count your benchmark family requires at your margin; say which
  column you are in and what you actually ran.
  \item \textbf{Release per-item outputs.} A few megabytes converts an assertion
  into something a third party can check. No eligible source we audited did this
  for the tasks its own claim covers, and the \AuditPerItemOtherTaskOnly{} that
  publish item-level results publish them for other suites.
\end{enumerate}

% CLOSED 2026-07-27. The \TODO's precondition -- all eight registered cells
% exist -- was met on 2026-07-26, and the verdict is signed
% (docs/H3_EIGHT_CELL_DECISION_2026-07-26.md), so the closing paragraph is
% written and may state the outcome. It states nothing the signed record does
% not contain.
% SOURCE: \S\ref{sec:minigrid:verdict} (5 of 8); sections/minigrid.tex Result 1
% (the churn ratio), whose \label may move under the flagship reordering --
% cite the file, not the label.
The controlled experiment says where this standard actually bites, and it is not
where the five lines above suggest. Every one of them is written as though the
comparison at issue were a compressed model against its original. The cell in
Figure~\ref{fig:cancellation} is not that comparison: H3 puts two
\emph{compressed} models side by side, GPTQ against AWQ at the same bit width,
which is the choice a practitioner makes after deciding to compress at all. The
evidence problem is strictly worse there, at a median per-cell churn of
$12.7\times$ the net delta against roughly four times in the atlas on the same
aggregation, and with the winner reversing on nothing but
the calibration seed in 5 of 8 registered cells. The reason is the same
mechanism in its sharpest form: two compressed models are more alike than either
is to the original, so cancellation is more complete and the aggregate hides
more.

That generalises the standard past its own framing. Nothing in the five lines is
about quantization. They are about comparing two models similar enough that
somebody thought the comparison worth making: compressed against original,
method against method, checkpoint against checkpoint, version against version.
Aggregate accuracy is least informative in the regime where these comparisons
are made, and what makes such a comparison checkable is the per-item evidence
and a declared margin.
```

---

## FILE: `paper/sections/appendix_related_detail.tex`

```latex
% =====================================================================
% Appendix: Related-work detail.
% CREATED 2026-08-04 (flagship narrative restructure, operation 1). Content
% moved from sections/related_work.tex §"Prior findings on calibration
% sensitivity". NOTHING WAS DELETED IN THE MOVE: the five paragraphs, their
% % SOURCE comments and every qualification appear here verbatim.
%
% The body keeps the one-sentence statement that the two antecedents disagree
% and points here; the reconciliation argument, which is what the objection
% needs answering at length, lives here.
%
% LABEL CHANGE: sec:related:reconcile -> app:reconcile. The two pointing sites
% (sections/related_work.tex, sections/minigrid.tex) were repaired in the same
% commit.
% =====================================================================

\section{Reconciling the calibration-sensitivity antecedents}
\label{app:reconcile}

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
across sets differing in quality, content and language: a
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
is the \emph{gap between} two methods at the same bit width, a quantity neither
antecedent's design measures.

\paragraph{Individual robustness plus a small method gap implies ranking
instability.} This is the reconciliation proper, and it is what
\S\ref{sec:minigrid} measures. Each method is individually
stable in absolute accuracy, much as they report, and the seed-induced range is
at least as large as the mean GPTQ--AWQ gap in 7 of our 8 confirmatory cells.
% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md (SIGNED), "Mechanical
% application of the rule": range/gap holds in 7 of 8. Wording follows that
% record's own "at least as large as"; do not tighten it to "smaller than".
Those two facts together \emph{are} ranking instability. We are not
contradicting their robustness finding; we are showing it has a consequence they
did not test for. A field that reads ``calibration choice barely moves accuracy''
as licence to compare two methods from one calibration run each has drawn the
wrong inference from a correct result.

\paragraph{The magnitude question.} Robustness claims are
claims about size, so the reconciliation has to be quantitative. The figures
that follow come from a \emph{post-hoc} resolution analysis, prompted by this
very paper and labelled as such wherever it appears (\S\ref{sec:minigrid}); it
is descriptive and modifies no verdict. On MMLU our seed-induced ranges run 5.5
to 17.5 paired standard errors, a spread no robustness claim reaches, and one
the benchmark resolves comfortably at $n = 14{,}042$.
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, step 5 table,
% max_range/SE column, MMLU rows: 11.07, 17.45, 5.53, 11.19.
On GSM8K at $n = 1{,}000$ the same ranges run roughly two standard errors, and
we say so instead of averaging the two tasks together: that arm of the
experiment does not resolve the effect it was built to measure
(\S\ref{sec:minigrid:resolution}, \S\ref{sec:limitations}).
% SOURCE: same table, GSM8K rows: 1.92, 2.35, 3.61, 2.45.

\paragraph{What the disagreement was about.} Read this way, the two antecedents
are not really in conflict. \citet{williamsaletras2024} and
\citet{paglieri2024outliers} both measure how much a \emph{single} method's
absolute accuracy moves when the calibration data changes, and they disagree
about the size of that movement on the model generations each studied. Neither
measures what a practitioner comparing two methods actually depends on, namely that the
\emph{ordering} survives, and a quantity nobody measured is one the field has no
basis to assume stable. Our design does not settle their disagreement. It shows
that settling it would not have answered the question either way.

\subsection{Adjacent concurrent measurements}
\label{app:related:concurrent}

% RELOCATED FROM sections/related_work.tex 2026-08-05 (compression pass,
% relocation of extended related work). Moved whole; nothing deleted.
% SOURCE: docs/PRIOR_ART_CONCURRENT_2026-07-24.md §§3-4, both verified against
% the raw arXiv HTML rendering.
\citet{cacioli2026beyondmean} adapts the clinical Reliable Change Index to
per-item comparisons between model \emph{versions} rather than precisions, and
likewise recommends reporting a churn rate beside the mean;
\citet{nikolic2026displacement} extend the flips metric into a leapfrog/drop
decomposition over community-published quantized checkpoints, and find
that KL-divergence proxies lose their ranking signal in precisely the
near-baseline region our certification tables adjudicate.

\subsection{Losslessness definitions and fidelity metrics}
\label{app:related:lossless}

% RELOCATED FROM sections/related_work.tex 2026-08-05.
\citet{helcig2026slq} occupy the phrase this paper is about. They formalise
notions of losslessness for quantized LLMs (task-lossless and the stricter
distribution-lossless), propose the Expected Acceptance Rate as an interpretable
fidelity metric, and ship SLQ, a method that reaches those targets at low bit
widths. Their question and ours are different, and the difference is the whole
of \S\ref{sec:certification}. \emph{They define losslessness and build a method
to achieve it.} \emph{We audit whether existing published claims of losslessness
have the evidence to support them, and compute how many items it would take to
certify one.} Their paper contains no equivalence test at a declared margin, no
power or required-$n$ computation, and no audit of others' claims; ours contains
no quantization method. A practitioner who adopts EAR as a fidelity target still
needs to know how large an evaluation must be before the accuracy half of a
losslessness claim means anything, and that number is what our certification
tables supply.

\subsection{The constructive-audit genre, and preregistration precedent}
\label{app:related:genre}

% RELOCATED FROM sections/related_work.tex 2026-08-05.
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

\subsection{The compression families the audited claims span}
\label{app:related:families}

% RELOCATED FROM sections/related_work.tex 2026-08-05.
The audited claims span the two dominant post-training families: weight-only
quantization, represented by GPTQ \citep{gptq2022}, AWQ \citep{awq2023} and
SqueezeLLM \citep{squeezellm2023}; weight-and-activation quantization, by
LLM.int8() \citep{llmint82022} and SmoothQuant \citep{smoothquant2022}; and
one-shot pruning, by SparseGPT \citep{sparsegpt2023} and Wanda
\citep{wanda2023}. We audit the equivalence \emph{language} these papers use
and the evidence offered for it, not the methods themselves, and the audit's
verdicts are about reporting practice, not about whether a method works.
Two of the most aggressive methods in the set are also the most restrained in
what they assert: SpinQuant \citep{spinquant2024} and QuIP\#
\citep{quipsharp2024} report their accuracy deltas without equivalence
language, and are cited here as positive examples alongside the Qwen quantized
model cards and the \texttt{llama.cpp} documentation.
% SOURCE for the honest-non-claimer list:
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §2, "Honest non-claimers" bullet.
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

This appendix holds the full text of six items summarised in
\S\ref{sec:prereg}: the freeze timeline, the disclosed pre-registration data
contact, the seven interpretive choices, the result-inspection discipline, the
H3 reporting rule as registered, and the spot-check narrative.

\subsection{The freeze timeline}
\label{app:prereg:timeline}

% RELOCATED 2026-08-04 (flagship narrative, operation 4) from
% sections/preregistration.tex. The table and its caption are moved verbatim;
% nothing was deleted, and the body keeps a pointer to it.
% SOURCE: PREREGISTRATION.md header lines 3-7;
% docs/RESULTS_2026-07-15_ATLAS_AUDIT.md §3 (commits b74fd58, d6e02dd, f06348f,
% 715a7ce); docs/AUDIT_VERDICTS_2026-07-20.md §Provenance (claim-table sha256).
\begin{table}[!t]
\centering
\small
\caption{Freeze timeline. Each artifact was committed before the analysis it
governs could be run, and each frozen file carries a \emph{Dated Amendments}
section: deviations are appended, never edited in, and each records whether
results had been inspected before the decision.}
\label{tab:freeze-timeline}
% WIDTH FIX 2026-08-05: tightened column separation and wrapped the widest
% text column. No cell value changed and no row was dropped.
\setlength{\tabcolsep}{4pt}
\small
\begin{tabular}{lll>{\raggedright\arraybackslash}p{4.6cm}}
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

\subsection{Result-inspection discipline}
\label{app:prereg:discipline}

% RELOCATED 2026-08-04 (operation 4) from sections/preregistration.tex §3.4,
% moved verbatim.
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
registered analysis is tuned after results are seen: not the calibration
builder, not the paired bootstrap, not the verdict rule.

\subsection{The H3 reporting rule, stated before the results exist}
\label{app:prereg:h3rule}

% RELOCATED 2026-08-04 (operation 4) from sections/preregistration.tex §3.5,
% moved verbatim except for one repointed cross-reference
% (sec:minigrid:escalation -> app:escalation).
% SOURCE: PREREGISTRATION.md §"H3 Decision Rule";
% docs/MINIGRID_REGISTRATION_2026-07-15.md §§1, 3, 4.
% THIS SUBSECTION STATES NO H3 OUTCOME. That is deliberate and survives the
% signed verdict of 2026-07-26: this is the protocol, §\ref{sec:minigrid} is the
% result.
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
undecided under the registered rule, never supported or disconfirmed on four
cells, and no reduced-cell variant of the rule is constructed after results are
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
Appendix~\ref{app:escalation} and the verdict in
\S\ref{sec:minigrid:verdict}; this subsection states neither.

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

\paragraph{Choice 1: which margin is ``the applicable margin'', and the
$K = 1 \to 5 \to 4$ correction.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #1 (the
% SUPERSEDED record); resolution in docs/AUDIT_REGISTRATION_2026-07-15.md
% "Dated Amendments" Part 1, signed 2026-07-31; values in
% results/audit_verdicts_rev3.csv.
%
% THIS CHOICE IS RETIRED. Amendment 2 resolved it, and this paragraph is now a
% record of a resolved ambiguity rather than a live interpretive option. The
% previous version argued FOR the own-margin reading in the present tense,
% including the "0.15 pp" sentence the advisor review identified as the
% load-bearing error. That sentence is retained ONLY as the quoted reasoning
% that was found wrong; it must never be restated as the paper's position.
The frozen §4 names the 2\,pp registered margin first, adds ``(and at the
claim's own margin when it states one)'', and then labels the verdict
``underpowered for its own assertion'' \emph{at the applicable margin}. We read
that as leaving two live options, and chose the second. That was an error, and
Amendment~2 corrects it.

The conditional in the frozen text is the whole of it: \emph{when it states
one}. No audited source states one (\S\ref{sec:audit:taxonomy}). What the
superseded implementation substituted was each source's largest reported
$|\Delta|$, and the reasoning it ran on was that ``a source asserting parity
within 0.15\,pp has made a 0.15\,pp claim''. It has not. A reported delta is an
outcome of an evaluation that has already been run; a margin is a tolerance
fixed before it runs, and a claim cannot be held to a decision rule its authors
never adopted. Treating the one as the other inverted the direction of the
inference and, because a measured delta is typically far tighter than any
tolerance a author would have declared, it also made the test far harsher than
the registration authorised.

% The sequence of values is the evidence. Reported plainly, with no argument
% about what the analyst believed at each step (advisor review 3.3).
The sequence is reported exactly, because the order in which the numbers arrived
is itself the disclosure. The first pass applied the 2\,pp margin uniformly and
returned $K = 1$ of 12. Re-reading the frozen label produced $K = 5$; ruling on
choice~3 below moved one claim out of the determinate set, giving the $K = 4$
that was reported for ten days. Amendment~2 returns the analysis to the uniform
registered margin, where the rev-3 recomputation gives \textbf{1 of 11
assessable claims below the approximate planning threshold}, the same claim the
very first pass had flagged.

\paragraph{Choice 2: what counted as the claim's own margin (withdrawn).}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #2 (the
% SUPERSEDED record). Retained as the construction Amendment 2 withdraws.
%
% THE 2.0x-12.9x SHORTFALL RANGE IS WITHDRAWN HERE, NOT RECOMPUTED. It was
% required-n over reported-n AT THE RESULT-DERIVED MARGINS, so recomputing it at
% 2 pp does not produce a corrected version of the same quantity: ten of the
% eleven assessable claims have no shortfall at all, so there is no range to
% state. Do not reintroduce the sentence with new numbers in it.
This choice is withdrawn with the margins it operated on, and is recorded
because the withdrawn quantities were reported publicly.

Most claims cover several benchmarks with different deltas, so the superseded
implementation defined the claimed margin as the largest $|\Delta|$ the source
reports. Within its own frame that was the reading most favourable to the
source, granting the claim the widest margin its sentence could bear and
therefore the smallest required sample size. The point Amendment~2 makes is that
the frame was wrong to begin with: no choice among a source's reported deltas
yields a margin, because none of them is one.

Two published quantities fall with it. The shortfall range of $2.0\times$ to
$12.9\times$ was required $n$ over reported $n$ at those derived margins, and it
is \textbf{withdrawn rather than recomputed}; at the registered 2\,pp margin ten
of the eleven assessable claims have no shortfall at all, so there is no range
to restate. The MDD-to-margin ratios are likewise recomputed against the
registered margin in Table~\ref{tab:audit-mdd}, where the values themselves are
unchanged and only the denominators move.

What survives the withdrawal is the disposition of the remaining choices, which
were and remain resolved in the source's favour: pairing rather than independent
binomial variance (the paired assumption is the generous one, and
Table~\ref{tab:audit-mdd} shows the independent bound is uniformly worse), and
imputation by \emph{median} discordance from the most specific matching atlas
tier rather than by any upper quantile.

\paragraph{Choice 3: R04 is indeterminate rather than scored on a substituted
benchmark.}
% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #3 and the
% R04 bullet in §Indeterminate; results/audit_verdicts_rev3.csv row R04.
% The K and shortfall figures below are PRE-AMENDMENT-2 HISTORY, quoted as what
% was decided at the time. Do not update them to rev-3 values.
Discussed in full at \S\ref{sec:audit:r04}, and unaffected by Amendment~2: R04
sits outside the registered binary paired-outcome calculation whichever margin
is applied. It is recorded here as a ruling because it is the second correction
that cost the paper a number. Under the rules then current it removed what the
first pass had reported as the audit's largest shortfall ($38.3\times$) and
moved the headline from $K = 5, J = 4$ to $K = 4, J = 5$; those figures are
quoted as history and are not current results. The GSM8K computation is retained
in the released CSV as a labelled transparency column so that the set-aside
quantity is inspectable rather than deleted.

\paragraph{Choice 5: TOST uses the one-sided $z$.}
% SOURCE: scripts/audit_stats.py::required_n_for_tost (Z_ONE_SIDED) and
% ::minimum_detectable_delta (two-sided), which are the implementation of
% record; \S\ref{sec:cert:method}. The rationale was first written up in
% docs/AUDIT_VERDICTS_2026-07-20.md §"Interpretive choices" #5 and
% docs/CERTIFICATION_TABLES_2026-07-20.md §Method, both REV-1 narratives whose
% numeric provenance is superseded; the z-choice argument they make is not
% population-dependent and is unaffected, but they are not the source for any
% number here.
The project's own helper, \texttt{flipeval.required\_n\_for\_effect}, uses the
two-sided $z_{1-\alpha/2}$. That is correct for \emph{detection} and wrong for
TOST, which rejects two one-sided nulls at level $\alpha$ each. Reusing the
helper unchanged would have inflated every required $n$ in this paper by about
27\%, in the conservative direction, under the name ``TOST'', and with no
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

\subsection{Atlas validation and population correction}
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
registered definitions}, deliberately not a rerun of our own pipeline, since
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
recomputing our own numbers, which is the natural and useless form of
self-check, we would have confirmed all of them and shipped the selection bias intact. What
caught it was reconstructing the measurement from the protocol text rather than
from the code.

Preregistration did the work it is supposed to do. The registration
text was frozen before any statistic existed, and it fully determined the
direction of the repair: we did not choose a rule that flattered a result, we
executed a rule that was already binding and had been under-implemented. That
is why the fix is a correction rather than a post-hoc adjustment, and it is why
we can say so without asking to be trusted. The correction was nevertheless made
\emph{after} results had been inspected, and we disclose that plainly rather
than presenting the repair as a pre-specified step.

Both revisions are public. We publish rev-1 and rev-2 and report the
delta between them, rather than replacing the record with its corrected version.
A field in which near-lossless claims cannot be rechecked because per-item
outputs are never released, which is the finding of Section~\ref{sec:audit}, is
a field whose corrections are invisible. Ours is not, and the difference is the point of
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
rises sharply from 17.5\% to 26.5\%, because the recovered pairs are larger-$n$
cells, which resolve more differences. Every S2 field is identical across revisions.

% HISTORY, PRE-AMENDMENT-2, AND SUPERSEDED. This paragraph reports what the
% rev-1 -> rev-2 population change did to the headline AS IT THEN STOOD. Both
% the count and the "underpowered for their own assertion" construction are
% retired by Amendment 2 and are quoted here as the superseded reading, never
% asserted. The current result is \AuditBelowThresholdAtMedian of
% \AuditAssessable at the registered uniform margin; see \S\ref{sec:audit:results}.
% Do NOT update these figures to rev-3 -- the point of the paragraph is that the
% rev-2 population change moved nothing, which is a statement about rev-2.
The headline verdicts did not move under the rev-2 population change. On the
own-margin reading then in force, since superseded by Amendment~2, the audit
stood at $K = 4$ of 12 determinate claims and $J = 5$ indeterminate, identical
to rev-1 under the rev-2 discordance imputation, with the uniform-2\,pp
secondary reading unchanged at 1 of 12. Those counts are quoted as the state of
the analysis at that date and are not current results: the eligible denominator
later changed with R10's exclusion, and the own-margin reading was withdrawn
outright. What survives is the finding that enlarging the atlas moved no
verdict. No new verdict computation was triggered. In the
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

## FILE: `paper/sections/appendix_audit_table.tex`

```latex
% =====================================================================
% Appendix: the full audit table -- SKELETON.
% The three tables here are GENERATED by paper/tools/gen_audit_tables.py from
% results/audit_verdicts_rev3.csv (identity from the FROZEN
% docs/audit_claim_table.csv). Do not hand-transcribe them: they sat at rev-2
% for ten days after Amendment 2 precisely because they were hand-typed.
% Validate the generator with --check before trusting it on anything.
% NOTE: the certification tables further down cite certification_tables_rev2.csv,
% which is a DIFFERENT artifact and is correctly at rev-2. Do not repoint those.
% =====================================================================

\section{Full audit table}
\label{app:audit-table}

\begin{table}[!t]
\centering
\scriptsize
\caption{The 17 audited claims: identity and frame. \textbf{F1} is a research-paper claim, \textbf{F2} a vendor model card or official documentation page, \textbf{F3} a vendor blog post. Source URLs, version dates and the exact quoted sentence per claim are in the frozen claim table \texttt{docs/audit\_claim\_table.csv}, which is part of the released artifact.}
\label{tab:audit-identity}
% GENERATED from docs/audit_claim_table.csv (FROZEN, read-only). Source
% names are taken from there and NOT from the verdicts CSV, which
% truncates source_name at 80 characters, several rows ending mid-word.
\begin{tabular}{@{}llp{10.2cm}@{}}
\toprule
Claim & Frame & Source \\
\midrule
R01 & F1 & GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers (Frantar, Ashkboos, Hoefler, Alistarh) \\
R02 & F1 & LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale (Dettmers, Lewis, Belkada, Zettlemoyer) \\
R03 & F1 & SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models (Xiao, Lin, Seznec, Wu, Demouth, Han) \\
R04 & F1 & AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration (Lin, Tang, Tang, Yang, Chen, Wang, Xiao, Dang, Gan, Han) \\
R05 & F1 & SqueezeLLM: Dense-and-Sparse Quantization (Kim, Hooper, Gholami, Dong, Li, Shen, Mahoney, Keutzer) \\
R06 & F1 & A Simple and Effective Pruning Approach for Large Language Models [Wanda] (Sun, Liu, Bair, Kolter) \\
R07 & F1 & SparseGPT: Massive Language Models Can Be Accurately Pruned in One-Shot (Frantar, Alistarh) \\
R08 & F2 & RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w4a16 model card (Neural Magic / Red Hat AI) \\
R09 & F2 & RedHatAI/Meta-Llama-3.1-8B-Instruct-FP8 model card (Neural Magic / Red Hat AI) \\
R10 & F2 & RedHatAI/Qwen2.5-7B-Instruct-quantized.w4a16 model card (Neural Magic / Red Hat AI) \\
R11 & F2 & Meta AI blog: ``Introducing quantized Llama models with increased speed and a reduced memory footprint'' \\
R12 & F3 & NVIDIA TensorRT-LLM official blog: ``Speed up inference with SOTA quantization techniques in TRT-LLM'' \\
R13 & F3 & vLLM official docs: ``FP8 W8A8'' (LLM Compressor quantization guide) \\
R14 & F3 & vLLM Blog: ``The State of FP8 KV-Cache and Attention Quantization in vLLM'' (Kübler, Kurtić, Wilkinson, Bonanni, Goin, Marques, Budhathoki) \\
R15 & F2 & RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8 (model card) \\
R16 & F2 & RedHatAI/Meta-Llama-3.1-70B-Instruct-quantized.w4a16 (model card) \\
R17 & F2 & RedHatAI/Meta-Llama-3-8B-Instruct-quantized.w8a16 (model card) \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[!t]
\centering
\caption{Per-claim characterisation and sensitivity classification, at the registered 2\,pp margin. $n$ is the reported or imputed item count, with its basis recorded in the released CSV. $p_d$ is the discordance imputed from the atlas and \emph{tier} the match tier it came from. \emph{V3} is whether the source releases per-item outputs for the tasks its claim rests on. \emph{Classification} is evaluated across the interquartile range of the atlas cells supplying $p_d$: \emph{above throughout} and \emph{below throughout} hold at both quartiles, and \emph{sensitive} changes within the interval. R10 keeps its row and is marked ineligible rather than removed.}
\label{tab:audit-characterisation}
% GENERATED by paper/tools/gen_audit_tables.py from
% results/audit_verdicts_rev3.csv. Values read, not retyped. The generator is
% validated by --check, which regenerates tab:audit-identity and diffs it
% against the committed table. DO NOT HAND-EDIT: this table was stale at rev-2
% for ten days precisely because it was hand-transcribed.
% The retired version carried a claimed-margin column and a verdict column
% reading 'underpowered'. Both are gone with Amendment 2.
% WIDTH FIX 2026-08-05, THIRD AND FINAL FORM: SPLIT INTO TWO PANELS.
% Nine columns of reference data do not fit \textwidth at any legible size. The
% history is worth keeping because each attempt failed differently:
%   free-running Classification            141pt over
%   Classification wrapped, \footnotesize   82pt over (the widest box in the doc)
%   Benchmark and Tier also wrapped          fixed the width, but every row
%                                            became 2-3 lines and the PDF grew
%                                            by two pages
%   \scriptsize, single-line rows            34pt over, and the header itself
%                                            overflowed its own column
% Splitting by role is what tab:h3-supporting already does for the same reason.
% Both panels are keyed by claim id, so no row is separated from its identity,
% and every field of the nine-column version survives in exactly one panel.
% Nothing was dropped, summarised, recomputed or reordered, and the table is
% back at \footnotesize with single-line rows.
% GENERATED: table_characterisation_panels() in the generator emits both panels.
\setlength{\tabcolsep}{4pt}
\footnotesize
\textbf{(a) What the claim is, and what it measured}\par\medskip
\begin{tabular}{@{}lllll@{}}
\toprule
Claim & Family & Bits & Benchmark & $n$ \\
\midrule
R01 & gptq & 4 & piqa & 1{,}838 \\
R02 & w8a8\_int8 & 8 & (mixed/unmatched) & --- \\
R03 & w8a8\_int8 & 8 & (mixed/unmatched) & 18{,}300 \\
R04 & awq & 4 & gsm8k & 1{,}319 \\
R05 & squeezellm & 4 & mmlu & 14{,}042 \\
R06 & pruning & --- & (mixed/unmatched) & 18{,}904 \\
R07 & pruning & --- & (mixed/unmatched) & 12{,}410 \\
R08 & w4a16 & 4 & mmlu & 42{,}701 \\
R09 & w8a8\_fp8 & 8 & mmlu & 42{,}701 \\
R10 & w4a16 & 4 & mmlu & 28{,}659 \\
R11 & spinquant & 4 & (mixed/unmatched) & --- \\
R12 & w8a8\_fp8 & 8 & mmlu & 14{,}042 \\
R13 & w8a8\_fp8 & 8 & gsm8k & 250 \\
R14 & w8a8\_fp8 & 8 & (mixed/unmatched) & 728 \\
R15 & w8a8\_int8 & 8 & mmlu & 42{,}701 \\
R16 & w4a16 & 4 & mmlu & 42{,}701 \\
R17 & w8a16 & 8 & mmlu & 28{,}659 \\
\bottomrule
\end{tabular}

\medskip
\textbf{(b) How it was assessed, at the registered 2\,pp margin}\par\medskip
\begin{tabular}{@{}lllll@{}}
\toprule
Claim & $p_d$ & Tier & V3 & Classification \\
\midrule
R01 & 0.130 & family+bits & no & \textbf{sensitive} \\
R02 & 0.056 & family+bits & no & not assessable (reporting) \\
R03 & 0.056 & family+bits & no & above throughout \\
R04 & 0.074 & family+bits+benchmark & no & not assessable (metric) \\
R05 & 0.146 & bits+benchmark & no & above throughout \\
R06 & 0.119 & bits & no & above throughout \\
R07 & 0.119 & bits & no & above throughout \\
R08 & 0.048 & family+bits & partial & above throughout \\
R09 & 0.048 & family+bits & no & above throughout \\
R10 & 0.048 & family+bits & no & \emph{ineligible} \\
R11 & 0.133 & bits & no & not assessable (reporting) \\
R12 & 0.048 & family+bits & no & above throughout \\
R13 & 0.048 & family+bits & no & not assessable (reporting) \\
R14 & 0.048 & family+bits & no & not assessable (reporting) \\
R15 & 0.056 & family+bits & partial & above throughout \\
R16 & 0.048 & family+bits & partial & above throughout \\
R17 & 0.135 & bits+benchmark & no & above throughout \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[!t]
\centering
\scriptsize
\caption{Power quantities per claim at the registered 2\,pp margin. MDD is the minimum detectable difference in percentage points, under the paired and the independent-binomial variance models. Required $n$ is the item count needed under TOST at one-sided $\alpha=.05$ (a 90\% two-sided confidence interval) with 80\% power, assuming a true difference of zero, under the paired model; it is given at the first quartile, median and third quartile of the atlas cells supplying the claim's discordance rate, which bracket the interval because required $n$ increases monotonically in that rate. $d^{*}$ is the discordance rate at which the classification would reverse; it falls inside the swept interval for R01 alone, and is blank where no reversal is attainable. \textbf{Numbers on ineligible and non-assessable rows are not verdicts}; they are retained so a reader can see what the analysis could and could not evaluate.}
\label{tab:audit-power}
% GENERATED by paper/tools/gen_audit_tables.py from
% results/audit_verdicts_rev3.csv. Q1/Q3 required-n are recomputed from
% discordance_p25/p75 by the same ceil((z*sqrt(d)/m)^2) the pipeline uses.
% The retired version carried m* and n@m*, which divided by result-derived
% margins. Those columns are withdrawn, not recomputed.
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
Claim & $n$ & MDD (paired) & MDD (indep.) & $n_{\mathrm{req}}$@Q1 & @median & @Q3 & $d^{*}$ \\
\midrule
R01 & 1{,}838 & 2.36 & 3.62 & 1{,}364 & 2{,}010 & 4{,}328 & 0.1189 \\
R02 & --- & --- & --- & 619 & 866 & 1{,}237 & --- \\
R03 & 18{,}300 & 0.49 & 1.38 & 619 & 866 & 1{,}237 & --- \\
R04 & 1{,}319 & 2.09 & 3.77 & 1{,}137 & 1{,}137 & 1{,}137 & --- \\
R05 & 14{,}042 & 0.90 & 1.63 & 1{,}525 & 2{,}255 & 3{,}865 & 0.9085 \\
R06 & 18{,}904 & 0.70 & 1.36 & 932 & 1{,}841 & 6{,}046 & --- \\
R07 & 12{,}410 & 0.87 & 1.63 & 932 & 1{,}841 & 6{,}046 & 0.8029 \\
R08 & 42{,}701 & 0.30 & 0.84 & 371 & 742 & 1{,}052 & --- \\
R09 & 42{,}701 & 0.30 & 0.84 & 433 & 742 & 1{,}113 & --- \\
R10 & 28{,}659 & 0.36 & 1.04 & 371 & 742 & 1{,}052 & --- \\
R11 & --- & --- & --- & 1{,}314 & 2{,}051 & 3{,}682 & --- \\
R12 & 14{,}042 & 0.52 & 1.53 & 433 & 742 & 1{,}113 & 0.9085 \\
R13 & 250 & 3.88 & --- & 433 & 742 & 1{,}113 & --- \\
R14 & 728 & 2.27 & --- & 433 & 742 & 1{,}113 & --- \\
R15 & 42{,}701 & 0.32 & 0.84 & 619 & 866 & 1{,}237 & --- \\
R16 & 42{,}701 & 0.30 & 0.69 & 371 & 742 & 1{,}052 & --- \\
R17 & 28{,}659 & 0.61 & 1.09 & 1{,}332 & 2{,}081 & 3{,}644 & --- \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:audit-identity} gives the claim-to-source mapping the
\texttt{R}\emph{nn} identifiers used throughout the paper refer to;
Table~\ref{tab:audit-characterisation} the per-claim characterisation and
sensitivity classification; Table~\ref{tab:audit-power} the power quantities.
They are split by content rather than presented as one sheet because the
released CSV has 53 columns, more than a page can carry legibly.

% SOURCE: results/audit_verdicts_rev3.csv header. Count checked against the file
% (53), not carried over from the rev-2 description, which said 45.
The released CSV carries, per claim: identity and frame; method family, bit
width and benchmark; the reported or imputed $n$ with its \texttt{n\_basis};
eligibility with its basis; the margin category, its basis and the form the
source's evidence takes; the imputed discordance with its match tier and the
number of atlas cells behind it, together with the first and third quartiles of
those cells; assessability status, kind and reason; the components that remain
computable for non-assessable claims; the V3 reproducibility value; V1 as
paired and independent-binomial MDD; V2 required-$n$ at 1, 2 and 3\,pp under
both variance models; the reversal discordance with the count and share of
supporting cells below it; the margin-sensitivity flag; and the threshold
classification with its robustness across the quartile interval.

% The retired schema is worth naming, because a reader holding the earlier
% released CSV will look for columns that no longer exist.
Three groups of columns present in the superseded rev-2 release are absent here:
every quantity computed at a source's own reported delta, the applicable-margin
pair that selected between the two readings, and the verdict column that
recorded ``underpowered for its own assertion''. They were withdrawn with
Amendment~2 rather than recomputed, and the rev-2 file remains published as the
superseded record.

\paragraph{Reading the transparency columns.} Rows marked ineligible or
non-assessable carry numbers in some V1/V2 columns. Those numbers are \emph{not}
verdicts; they are retained so that a reader can see exactly what the analysis
could and could not evaluate. R14 is the case to watch: its imputed $n = 728$
sits just below the $742$ its row reports as required, which looks like a
threshold failure and is not one, because the missing baseline means there is no
paired comparison to size. R04's GSM8K computation is the largest such quantity
and is discussed in \S\ref{sec:audit:r04}.

\section{Audit method detail}
\label{app:audit-method}

% RELOCATED 2026-07-27 (phase 4 trim, candidates 1 and 3). Moved VERBATIM in
% content from sections/audit.tex; nothing was deleted in the move. The body
% keeps both findings and points here for the mechanism.
% RELOCATED AGAIN 2026-08-04 (flagship narrative, operations 6, 7 and 14):
% tab:audit-locus and tab:audit-mdd, both whole. No column was dropped, no font
% reduced. The plan asked for tab:audit-mdd to be consolidated INTO
% tab:audit-power; that was not done, because tab:audit-power is GENERATED by
% paper/tools/gen_audit_tables.py from results/audit_verdicts_rev3.csv and
% hand-adding two columns to it would reintroduce exactly the hand-transcription
% that left it stale at rev-2 for ten days. The table is relocated instead, and
% the saving is correspondingly smaller. Reported as a deviation.

\subsection{Where the equivalence claim is written}
\label{app:audit:locus}

% RELOCATED 2026-08-04 from sections/audit.tex §\ref{sec:audit:locus}, which
% keeps the finding, the selection-effect argument, the retention judgement for
% the two boundary cases, and the author-re-verification disclosure, all as
% prose.
% STILL OPEN (defect D6): the 3 / 2 / 1 tier counts and the six-card denominator
% are hand-typed here and in the body. They are not emitted by
% paper/tools/gen_denominator_macros.py, and macro-ising them would mean editing
% that generator's validated three-layer check from a branch that does not own
% it. Do not add a second generator.
\begin{table}[!t]
\centering
\caption{Where the equivalence claim is written, across six model cards from one
publisher with the underlying evidence held constant. Every card reports the
same recovery column; the tiers differ only in whether, and where, the card
states the comparison in words. Read by \S\ref{sec:audit:locus}.}
\label{tab:audit-locus}
% SOURCE: docs/AUDIT_SELF_RECHECK_2026-08-02.md §4.1, controlled prose-vs-cell
% sweep over the six archived cards. Tier assignment is from the archived
% source text, not from the frozen exact_quote field.
\begin{tabular}{llc}
\toprule
Locus of the claim & Form it takes in the card & Cards \\
\midrule
Prose assertion      & states recovery percentages outright & 3 \\
Prose juxtaposition  & states two scores, characterises neither & 2 \\
Table cell only      & no comparative sentence anywhere & 1 \\
\bottomrule
\end{tabular}
\end{table}

% STAGE B, 2026-08-06: the locus discussion moved here from
% \S\ref{sec:audit:locus}, which keeps the finding, the selection-effect
% consequence for the denominator, and the author-re-verification disclosure.
The taxonomy of \S\ref{sec:audit:taxonomy} asks what form a source's assertion
takes. A second question turns out to matter as much: \emph{where in the
document the assertion is written}, and whether it is written in words at all.

Six of the eligible sources are quantized-model cards from a single publisher.
They run the same benchmark suite, present the same results table with the same
recovery column, declare no margin, and release no task-matched per-item
outputs. The evidence behind them is, for present purposes, identical. What
differs is where each one puts its equivalence claim
(Table~\ref{tab:audit-locus}): three cards assert recovery in prose, two report
the quantized and the unquantized score in adjacent clauses and stop,
characterising the gap neither as small nor as acceptable, and one makes no
comparative statement in prose at all, its claim existing solely as a recovery
figure in a table cell under a column header with no caption. That last card is
the excluded one (\AuditIneligibleClaim{}), and the exclusion is legible as the
endpoint of a gradient rather than an isolated extraction defect.

% DO NOT restate this as a defect count. The finding is that the locus VARIES
% with the evidence held constant; a tally of "3 cards are deficient" invites
% the reading that the other three are fine, which is not the claim.
The registered inclusion rule is reasonable, and it is the same rule any
comparable audit would need. It is also keyed to a property that varies
independently of the evidence. A reader encountering all six cards would take
all six as near-lossless claims; an inclusion rule keyed to prose vocabulary
captures the first tier cleanly, must exercise judgement on the second, and
cannot see the third. The claims do not become weaker as the locus moves from
sentence to cell. They stop being written down.

The two prose-juxtaposition cards were kept. They carry no trigger vocabulary in
their prose, and the recovery figures that would qualify them appear only as
table cells, which is the position that excluded \AuditIneligibleClaim{}. They
were retained on the judgement that a bare juxtaposition of two scores differing
by less than a point, in a document whose purpose is to offer the quantized
model as a substitute for the unquantized one, is an equivalence assertion in
substance even where it is not one in vocabulary. Excluding them instead would
have moved the eligible denominator to 14 and the assessable count to 9 without
changing which claims fall below the planning threshold, and it would have moved
the headline proportion in the direction favourable to this paper's thesis. The
conservative choice is to keep them and report the ambiguity.

\subsection{Detection resolution per claim}
\label{app:audit:mdd}

% RELOCATED 2026-08-04 from sections/audit.tex §\ref{sec:audit:results}, whole.
% The body keeps both readings of it: that the independent-binomial columns are
% uniformly worse by roughly a factor of two, and that R04 and R14 carry no
% verdict.
\begin{table}[!t]
\centering
\caption{Detection resolution (V1) at the registered 2\,pp margin: the smallest
difference each evaluation could have detected, and its ratio to that margin. A
ratio below $1$ means the evaluation resolves differences finer than the margin.
The independent-binomial columns are the same quantities computed without the
paired-design benefit. Rows are the 11 assessable claims; the two italicised
rows carry no verdict and are shown only for transparency. The MDD columns
repeat those of Table~\ref{tab:audit-power}; the ratio columns appear only here.}
\label{tab:audit-mdd}
% SOURCE: results/audit_verdicts_rev3.csv columns v1_mdd_pp_paired and
% v1_mdd_pp_independent; ratio columns are those values divided by the
% REGISTERED 2 pp margin, replacing v1_mdd_over_margin_*, which divided by the
% source's reported delta and are retired with Amendment 2.
% The MDD values themselves are UNCHANGED from rev-2 -- MDD depends on n and the
% imputed discordance, not on the margin. Only the denominators moved.
% R04 and R14 are italicised because they are NOT ASSESSABLE: numbers
% computable, retained for transparency, carrying no verdict.
\begin{tabular}{lrrrr}
\toprule
      & \multicolumn{2}{c}{MDD} & \multicolumn{2}{c}{MDD / 2\,pp} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Claim & paired & indep.\ binomial & paired & indep.\ binomial \\
\midrule
R01 & 2.36\,pp & 3.62\,pp & $1.18\times$ & $1.81\times$ \\
R05 & 0.90\,pp & 1.63\,pp & $0.45\times$ & $0.82\times$ \\
R07 & 0.87\,pp & 1.63\,pp & $0.43\times$ & $0.81\times$ \\
R06 & 0.70\,pp & 1.36\,pp & $0.35\times$ & $0.68\times$ \\
R17 & 0.61\,pp & 1.09\,pp & $0.30\times$ & $0.54\times$ \\
R12 & 0.52\,pp & 1.53\,pp & $0.26\times$ & $0.76\times$ \\
R03 & 0.49\,pp & 1.38\,pp & $0.25\times$ & $0.69\times$ \\
R15 & 0.32\,pp & 0.84\,pp & $0.16\times$ & $0.42\times$ \\
R16 & 0.30\,pp & 0.69\,pp & $0.15\times$ & $0.35\times$ \\
R09 & 0.30\,pp & 0.84\,pp & $0.15\times$ & $0.42\times$ \\
R08 & 0.30\,pp & 0.84\,pp & $0.15\times$ & $0.42\times$ \\
\midrule
\textit{(R04)} & \textit{2.09\,pp} & \textit{3.77\,pp} & \textit{$1.05\times$} & \textit{$1.89\times$} \\
\textit{(R14)} & \textit{2.27\,pp} & \textit{---} & \textit{$1.14\times$} & \textit{---\ (no baseline)} \\
\bottomrule
\end{tabular}
\end{table}

% STAGE C, 2026-08-06: the three estimators and the TOST convention moved here
% from \S\ref{sec:audit:rules}, which keeps the registered-margin sentence
% verbatim, the planning-not-diagnosis wording, the post-hoc disclosure and the
% monotonicity argument. eq:tost-n moves with them; it has no reference outside
% audit.tex.
\subsection{The three registered verdict quantities}
\label{app:audit:verdictrules}

For each claim, at its reported or rule-imputed sample size $n$, the frozen
protocol computes three quantities.

\emph{V1, detection resolution.} The minimum detectable difference (MDD) at 80\%
power and two-sided $\alpha = 0.05$, under the paired-flip model. The per-item
accuracy difference is $d_i \in \{-1, 0, +1\}$; under the null of no true
difference, $\mathrm{Var}(d) = p_d$, the discordance rate, so
$\mathrm{sd} = \sqrt{p_d}$. Both the MDD and its ratio to the registered margin
are reported (Table~\ref{tab:audit-mdd}).

\emph{V2, equivalence support.} The number of items required for TOST at the
applicable margin,
\begin{equation}
n_{\mathrm{req}} \;=\; \left\lceil \left(\frac{(z_{1-\alpha} + z_{1-\beta})\,\mathrm{sd}}{m}\right)^{\!2} \right\rceil ,
\label{eq:tost-n}
\end{equation}
with $z_{1-\alpha}$ \emph{one-sided} ($1.6449$), because TOST rejects two
one-sided nulls at level $\alpha$ each. At $\alpha=.05$ per bound this is
operationally the requirement that a \textbf{90\% two-sided} confidence interval
fall inside $\pm m$, not a 95\% one; V1 above is the quantity that takes the
two-sided $z$. A claim is recorded as \emph{below the approximate planning
threshold} iff its reported $n$ is below $n_{\mathrm{req}}$ at the registered
margin.

\emph{V3, reproducibility.} Binary, read from the frozen
\texttt{per\_item\allowbreak\_outputs\allowbreak\_released} column and
cross-checked against the extraction reconciliation memo.

Every quantity is additionally recomputed under the independent-binomial bound
$\mathrm{sd} = \sqrt{2p(1-p)}$ and swept over 1\,pp and 3\,pp margins; a verdict
that changes across that sweep is \emph{margin-sensitive}.

\subsection{Discordance imputation}
\label{app:audit:imputation}

% SOURCE: docs/AUDIT_VERDICTS_2026-07-20.md §Method, imputation-tier table.
The discordance rate $p_d$ is not reported by any audited source, so it is
imputed from the atlas (\S\ref{sec:atlas}) by matching the nearest (method
family, bit width, benchmark) cell, most-specific tier first, taking the
\emph{median} over the first non-empty tier because per-cell discordance is
right-skewed. One claim matched at tier~1 (family + bits + benchmark), 11 at
tier~2 (family + bits), 2 at tier~3 (bits + benchmark), and 3 at tier~4 (bits);
\textbf{no claim reached the global tier}. A tier whose target field is
\texttt{None} cannot match, so a pruning claim with no bit width descends
automatically rather than being forced into a wrong cell. The two pruning claims
descend to tier~4 and match there, over 183 cells.

% DISCLOSURE ADDED 2026-08-02 (carry checklist §0.2). Found while building the
% checklist against the data, and it is a limitation rather than a defect to
% repair: the imputation is REGISTERED, Amendment 2 does not reopen it, and
% results are inspected, so it MUST NOT be changed now. Neither verdict moves
% (R06 n = 18,904 and R07 n = 12,410 against 6,046 required even at Q3).
% Two code comments assert the opposite and are wrong, and are corrected in the
% same commit: nearest_cell_discordance's docstring claims a None target "can
% never match", which is false for 183 cells, and CLAIM_PROFILES["R06"].notes
% says imputation descends to the global tier, which is the REV-1 behaviour and
% the eighth rev-1 survivor found in this project, the first one in a comment.
\paragraph{What the tier-4 match for R06 and R07 actually rests on.} That match
deserves stating plainly, because it is weaker than the tier label suggests.
R06 and R07 are 50\% unstructured \emph{pruning} claims with no bit width, and
the 183 cells they match are \texttt{bnb-4bit}, \texttt{QLoRA-4bit} and
\texttt{bnb-4bit(DPO-FT)} cells, all of which are 4-bit \emph{quantization}.
Those cells carry a null bit width only because their method labels are absent
from the parser's profile table, not because they lack one. The match is
therefore on a field being missing on both sides rather than on any similarity
of method, and a pruning claim is being assigned a discordance rate measured on
quantized models. We report it rather than repair it: the imputation rule is
registered, this appendix is not the place to change a registered rule after
results are visible, and neither claim's classification depends on it, since
both sit far above the threshold even at the third quartile. A reader who
distrusts the substitution should read R06 and R07 as resting on the weakest
imputation in the table.
% CORRECTED 2026-07-30 -- SEVENTH rev-1 survivor. This sentence read "1 at
% tier~4 (bits), and 2 fell through to the global tier", which is the REV-1
% distribution (results/audit_verdicts.csv: bits 1, global 2). Rev-2 is
% {family+bits+benchmark 1, family+bits 11, bits+benchmark 2, bits 3, global 0}.
% Cause: rev-1's parser had dropped the bit-width-less pruning cells, so R06/R07
% had nothing to match at tier 4 and fell to global over 1,155 cells; rev-2
% matches them at tier 4 over 183. Counts read from
% results/audit_verdicts_rev3.csv column discordance_match_tier, where the
% distribution is unchanged from rev-2.
% NOTE: docs/AUDIT_VERDICTS_2026-07-20.md predates rev-2 (2026-07-21) and still
% carries the rev-1 reading on this point -- do not "restore" from it. Both disclosed feasibility-probe pairs (99
atlas cells) are excluded from the imputation pool, per the atlas registration.

\subsection{The two robustness readings}
\label{app:audit:robustness}

% SOURCE: results/audit_verdicts_rev3.csv columns margin_sensitive and
% robustness.
% CARE -- THE TWO SENSITIVITIES ARE DIFFERENT FACTS. First: the classification
% is unstable across the MARGIN sweep (1 pp -> 3 pp). Second: it is unstable
% across the IMPUTATION interval (atlas Q1 -> Q3). Both land on R01, which is a
% coincidence and MUST NEVER be merged into one sentence.
% THE PARAGRAPH THIS REPLACES restated the "judging a 0.15 pp parity claim
% against a 2 pp yardstick audits a claim nobody made" reasoning, which is the
% error Amendment 2 corrects: R17's 0.15 is an observed delta. Do not restore it
% in any wording.

The choice this appendix used to defend no longer exists. Amendment~2 settles
the applicable margin at the registered 2\,pp for every claim, because the
frozen text makes the claim-specific reading conditional on a source stating a
margin and none does. What was previously presented as a factor-of-four
interpretive gap was a comparison against quantities that were never margins,
and it is withdrawn rather than restated. The reasoning is at
Appendix~\ref{app:prereg:choices}.

The surviving sensitivities are two, and they are independent of each other.
\textbf{Margin sensitivity} asks whether a classification depends on where the
yardstick is set: R01's flips across the registered 1\,pp\,$\to$\,3\,pp sweep,
and R04 and R14 also flip but carry no classification to qualify.
\textbf{Imputation sensitivity} asks whether it depends on a quantity no source
reported: R01's flips across the interquartile range of the atlas cells
supplying its discordance rate, reversing at $d = 0.118915$, with 345 of the 792
supporting cells below that point. No other assessable claim is sensitive in
either direction, and R01 is the only claim sensitive in both. That coincidence
is worth stating precisely because it is a coincidence: the two properties
answer different questions and neither implies the other.

% =====================================================================
% DESTINATIONS CREATED 2026-08-06 for the audit body compression.
%
% Created BEFORE any body deletion, per the standing rule and
% docs/AUDIT_COMPRESSION_PROTECTION_LEDGER_2026-08-06.md: body text is removed
% only once its destination exists, compiles, and is referenced successfully.
% An earlier attempt at this compression cut body prose first and failed
% PAPER_CHECK with eight dangling refs to appendix labels that had never been
% created.
%
% Every subsection below carries material MOVED from sections/audit.tex. No
% value, count or qualification is altered in transit; the counts remain the
% generated \Audit* macros and are never retyped.
% =====================================================================

\subsection{Eligibility, and the full-text source review}
\label{app:audit:eligibility}

% MOVED from \S\ref{sec:audit:taxonomy}. The body keeps the ruling, the rule it
% applies, and both denominators; the review that produced it lives here.
The eligibility correction rests on a full-text review of every one of the
\AuditFrozenCandidates{} archived sources, conducted after the first verdicts had
been computed and reported as such. Each source was searched complete, including
tables, captions, footnotes, appendices and reference lists, with model cards
searched as raw Markdown rather than as rendered pages.

The review found that one candidate's recorded quotation appears nowhere in its
source: the sentence had been composed from a table cell rather than quoted from
prose. The registered inclusion rule requires the assertion to appear in prose or
a table caption. It appears in neither, so \AuditIneligibleClaim{} is excluded by
applying the registered rule rather than by a new judgement, and the eligible
denominator moves from \AuditFrozenCandidates{} to \AuditEligible{}. The
exclusion cannot flatter any result reported in \S\ref{sec:audit}:
\AuditIneligibleClaim{} was above the planning threshold at
\AuditMarginPP{}\,pp and recorded \emph{no} on per-item outputs, so removing it
lowers neither the threshold tally nor the reproducibility count. Its row remains
in the released claim table and in Table~\ref{tab:audit-characterisation}.

Source provenance: content hashes were recorded for 16 of the
\AuditFrozenCandidates{} sources. R13's was left empty, and the consequence for
provenance is stated in \S\ref{sec:artifacts}. Every archived source, its hash,
and the retrieval script needed to reproduce these locations are released with
the paper, so every classification here is checkable without re-fetching
anything.

\subsection{The complete-text margin sweep}
\label{app:audit:sweep}

% MOVED from \S\ref{sec:audit:taxonomy}. The body keeps the finding and that it
% was established over complete source text; the sweep's contents live here.
The finding that no source declares a prospective numerical equivalence margin is
established over complete source text rather than over the quoted sentence. The
registered vocabulary of tolerance language was swept across all
\AuditFrozenCandidates{} archived sources in full.

The terms \emph{parity} and \emph{percentage point} do not occur anywhere in the
corpus. Every occurrence of \emph{margin} is a page-layout artefact, a stylesheet
declaration, or the idiom ``by a large margin'' describing superiority rather
than tolerance. One vendor document comes closest to a declared tolerance by
explicitly declining to fix one, observing that ``users might have different
tolerances on accuracy impact'', which states the absence of a threshold rather
than a threshold.

\subsection{Per-item outputs: what the three partial sources release}
\label{app:audit:v3detail}

% MOVED from \S\ref{sec:audit:v3}. The body keeps the zero, the task-matched
% qualifier in the same sentence, and the three claim ids; the suite-by-suite
% detail and the repair-cost argument live here.
\AuditPerItemOtherTaskClaims{}, all Red~Hat AI model cards, are the closest the
record comes to reproducibility, and they illustrate why the task-matched count
is nonetheless \AuditPerItemTaskMatched{}. They release per-item outputs for
Arena-Hard, OpenLLM~v2 and HumanEval, but \emph{not} for the OpenLLM~v1 tasks
that the audited equivalence claim is actually about. The released artifacts and
the asserted claim do not intersect. These three sources are ahead of the field
in disclosure practice and the correction they need is small: publish the
per-item outputs for the suite the claim quotes.

The reason this finding is more actionable than any power calculation is that the
two failures have different repair costs. Underpowering is fixable after the fact
by evaluating more items, and \S\ref{sec:certification} says how many.
Irreproducibility is not fixable downstream at all: with no per-item outputs,
nobody outside the releasing organisation can run the paired test at \emph{any}
sample size, cannot compute churn, and cannot check the arithmetic. Per-item
outputs for a benchmark of a few thousand items are a file of a few megabytes.

\subsection{The non-assessable claims, one by one}
\label{app:audit:indeterminate}

% MOVED from \S\ref{sec:audit:indeterminate}. The body keeps the 4+1 split, the
% R14 trap paragraph and the category-is-itself-a-result argument. The
% per-claim blockers and the retained-components list live here.
Each non-assessable claim is recorded with exactly one primary blocker.

\emph{Insufficient reporting} (\AuditNotAssessableInsufficient{}). R02
(LLM.int8()) and R11 (Meta's quantized-Llama blog) state no sample size, no
baseline and no numeric delta, and their headline equivalence evidence exists
only as a chart image. R13 (vLLM FP8 documentation) states $n = 250$ but shows no
on-page baseline run at all. R14 (vLLM FP8 KV-cache blog) reports an observed
0.7\,pp difference and permits $n$ to be imputed, but reports no baseline; its
comparison lives in a figure.

\emph{Outside the registered calculation}
(\AuditNotAssessableOutsideFramework{}). \AuditOutsideFrameworkClaim{} (AWQ)
reports enough, but about a quantity the registered binary paired-outcome model
cannot score (\S\ref{sec:audit:r04}).

Every non-assessable claim retains whatever components its available inputs
support. These are listed in the CSV column \texttt{determinate\_components} and
are reported as supplementary transparency only, \textbf{never verdict-bearing}:
R13 retains V2, because the paired standard deviation depends on discordance and
not on baseline accuracy; R14 retains V1 (paired) and V2; and R04 retains V1 and
V2 computed on a substituted benchmark.

\subsection{R01: the planning values behind the single flag}
\label{app:audit:r01}

% MOVED from \S\ref{sec:audit:results}. The body keeps the flag, that it is a
% sensitivity-dependent planning flag and not a verdict, and the 43.6%
% descriptive-share sentence with its framing intact. The arithmetic lives here.
% SOURCE: results/audit_verdicts_rev3.csv row R01: n=1838, imputed_discordance
% 0.13, v2_required_n_paired_2pp 2010, discordance_p25 0.0882 -> 1364,
% discordance_p75 0.2800 -> 4328, reversal_discordance 0.118915,
% tier_cells_below_reversal 345, discordance_n_cells 792.
\AuditSensitiveClaim{}, the GPTQ paper, reports $n = \AuditSensitiveN{}$ against
a requirement of $\AuditSensitiveNReq{}$ items at the imputed discordance rate of
$0.130$. The gap is one part in twelve of that requirement, and it closes
entirely if the imputed rate is a little lower: the classification reverses at a
discordance rate of $0.1189$, and $\AuditSensitiveCellsBelow{}$ of the
$\AuditSensitiveCellsTotal{}$ atlas cells supplying the imputation lie below that
point. Across the interquartile range of those cells the requirement moves from
$1{,}364$ items to $4{,}328$, so \AuditSensitiveClaim{} is adequately sized at
the first quartile and undersized at the third.

\subsection{R04: the overruled first-pass computation}
\label{app:audit:r04detail}

% MOVED from \S\ref{sec:audit:r04}. The body keeps the ruling, why CIDEr is
% outside the REGISTERED CALCULATION rather than incompatible with paired
% analysis, and that the number is not claimed as an audit result. The history
% of the overruled computation lives here.
The first extraction pass scored R04 on GSM8K, the source's own accuracy
benchmark ($-0.30$\,pp at $n = 1{,}319$), and reported it as the audit's largest
shortfall. On review this was overruled, because computing a TOST requirement on
GSM8K audits a sentence the source wrote about a different benchmark, in
different and non-trigger language.

That ruling moved the headline and removed the audit's biggest number. The counts
and the ratio it moved are quoted as history in
Appendix~\ref{app:prereg:choices}, computed under the superseded reading that
took each source's reported delta as its margin, and \textbf{they are not current
results}. The GSM8K computation is retained in the released CSV as a labelled
transparency column so a reader can see exactly what was set aside and why. It is
not claimed anywhere in this paper as an audit result.

\subsection{Interpretive rulings and superseded verdicts}
\label{app:audit:history}

% Index, not new content: the histories already live in app:prereg:choices and
% in the dated records. This exists so the compressed body has one pointer to
% reach all of them, instead of repeating the chronology.
The audit's interpretive history is recorded in full elsewhere and is indexed
here so the main text needs only one pointer.

The four interpretive rulings, each with the direction it moved the headline, are
Appendix~\ref{app:prereg:choices}: which margin is ``the applicable margin'' and
the $K = 5 \to K = 4$ correction; the R04 benchmark-substitution ruling; the
claim-level rather than claim-by-benchmark granularity; and the treatment of
sources that state no sample size.

The superseded verdict record is \texttt{docs/AUDIT\_\allowbreak{}VERDICTS\_\allowbreak{}2026-07-20.md}, which
predates both the rev-2 atlas and Amendment~2. \textbf{No value may be restored
from it.} Amendment~2 (signed, commit \texttt{ab279b2}) makes the registered
uniform \AuditMarginPP{}\,pp margin the primary yardstick for every claim,
forbids describing any quantity derived from a source's own reported results as
that source's declared margin, and reopens \S\S3.1--3.2 for eligibility only. The
claim-derived margins and the shortfall range computed under the superseded
reading are \textbf{withdrawn, not recomputed}, and are non-verdict-bearing
wherever they still appear as history.

\subsection{Both robustness directions in full}
\label{app:audit:fullrobustness}

% MOVED from \S\ref{sec:audit:results}, the detection-direction paragraph. The
% body keeps the two-directions distinction and that they must never be merged.
% The reading of tab:audit-mdd lives here, next to that table.
Two features of Table~\ref{tab:audit-mdd} matter for how the audit should be
read.

First, the independent-binomial columns are uniformly \emph{worse}, by roughly a
factor of two. Pairing is the generous modelling assumption, and the one
evaluation that is coarser than the registered margin under pairing is coarser
still without it.

Second, the ordering makes the audit's reach visible. Only
\AuditSensitiveClaim{}'s evaluation is coarser than the registered margin, and
the other ten resolve differences between a sixth and a half of it. An audit at a
\AuditMarginPP{}\,pp margin is a weak test and should be understood as one. The
sources were not asked to meet a standard this permissive, because they were not
asked to meet any stated standard at all, and what the table shows is that ten
evaluations would already satisfy a reporting requirement none of them was given.


\section{Certification tables at 1\,pp and 3\,pp}
\label{app:certification-margins}

The 2\,pp margin is Table~\ref{tab:certification} in the main text; the
1\,pp margin is Table~\ref{tab:certification-1pp} and the 3\,pp margin
Table~\ref{tab:certification-3pp}. Note the quadratic margin scaling: MMLU's median
requirement is 8{,}656 items at 1\,pp, 2{,}164 at 2\,pp, and 962 at 3\,pp, a
factor of nine across a three-fold change in margin.

\begin{table}[!t]
\centering
\small
\caption{Items required to certify equivalence within $\pm 1$\,pp under TOST at one-sided $\alpha=.05$ (a 90\% two-sided interval) with 80\% power, assuming a true difference of zero, by benchmark family, at the 25th/50th/75th percentiles of the discordance rates the atlas observes for that family. The naive column is the same requirement computed by treating the two runs as independent samples. Eleven benchmark families plus the pooled row. Row order matches Table~\ref{tab:certification} so the three margins compare row-by-row.}
\label{tab:certification-1pp}
% GENERATED from results/certification_tables_rev2.csv, rows margin_pp = 1.0.
% Values are read from the CSV, never retyped. Row order matches
% Table~\ref{tab:certification} so the margins compare row-by-row.
% WIDTH FIX 2026-08-05: the two long header phrases wrap in fixed-width centred
% columns, matching tab:certification so the three margins still compare
% row-by-row. No cell value changed.
% Set \small with tighter column separation so the p25/med/p75 triples fit on
% one line; at \normalsize they wrapped mid-triple and read badly.
\setlength{\tabcolsep}{2pt}
\small
\begin{tabular}{lr>{\centering\arraybackslash}p{2.6cm}>{\centering\arraybackslash}p{2.65cm}rr}
\toprule
Benchmark & Atlas cells & Discordance p25/med/p75 & Required $n$ p25/\textbf{med}/p75 & Naive & Advantage \\
\midrule
musr & 24 & 0.015 / 0.034 / 0.044 & 928 / \textbf{2{,}076} / 2{,}721 & 30{,}468 & $14.7\times$ \\
gpqa & 24 & 0.035 / 0.048 / 0.067 & 2{,}180 / \textbf{2{,}993} / 4{,}138 & 28{,}931 & $9.7\times$ \\
bbh & 192 & 0.024 / 0.044 / 0.060 & 1{,}484 / \textbf{2{,}721} / 3{,}710 & 25{,}967 & $9.5\times$ \\
mmlu\_pro & 5 & 0.048 / 0.053 / 0.059 & 2{,}955 / \textbf{3{,}305} / 3{,}649 & 30{,}778 & $9.3\times$ \\
hellaswag & 23 & 0.031 / 0.045 / 0.099 & 1{,}905 / \textbf{2{,}777} / 6{,}151 & 19{,}618 & $7.1\times$ \\
arc\_challenge & 17 & 0.072 / 0.079 / 0.099 & 4{,}447 / \textbf{4{,}870} / 6{,}141 & 29{,}451 & $6.0\times$ \\
ifeval & 8 & 0.048 / 0.052 / 0.072 & 2{,}943 / \textbf{3{,}200} / 4{,}429 & 16{,}842 & $5.3\times$ \\
mmlu & 1{,}311 & 0.093 / 0.140 / 0.259 & 5{,}725 / \textbf{8{,}656} / 16{,}019 & 30{,}906 & $3.6\times$ \\
winogrande & 23 & 0.067 / 0.092 / 0.221 & 4{,}124 / \textbf{5{,}661} / 13{,}688 & 22{,}397 & $4.0\times$ \\
math & 56 & 0.107 / 0.141 / 0.169 & 6{,}642 / \textbf{8{,}741} / 10{,}439 & 20{,}888 & $2.4\times$ \\
gsm8k & 24 & 0.040 / 0.077 / 0.198 & 2{,}473 / \textbf{4{,}735} / 12{,}270 & 10{,}684 & $2.3\times$ \\
\midrule
\textbf{ALL (pooled)} & \textbf{1{,}707} & 0.064 / 0.120 / 0.225 & 3{,}974 / \textbf{7{,}420} / 13{,}909 & 30{,}887 & $\mathbf{4.2\times}$ \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[!t]
\centering
\small
\caption{Items required to certify equivalence within $\pm 3$\,pp under TOST at one-sided $\alpha=.05$ (a 90\% two-sided interval) with 80\% power, assuming a true difference of zero, by benchmark family, at the 25th/50th/75th percentiles of the discordance rates the atlas observes for that family. The naive column is the same requirement computed by treating the two runs as independent samples. Eleven benchmark families plus the pooled row. Row order matches Table~\ref{tab:certification} so the three margins compare row-by-row.}
\label{tab:certification-3pp}
% GENERATED from results/certification_tables_rev2.csv, rows margin_pp = 3.0.
% Values are read from the CSV, never retyped. Row order matches
% Table~\ref{tab:certification} so the margins compare row-by-row.
% WIDTH FIX 2026-08-05: the two long header phrases wrap in fixed-width centred
% columns, matching tab:certification so the three margins still compare
% row-by-row. No cell value changed.
% Set \small with tighter column separation so the p25/med/p75 triples fit on
% one line; at \normalsize they wrapped mid-triple and read badly.
\setlength{\tabcolsep}{2pt}
\small
\begin{tabular}{lr>{\centering\arraybackslash}p{2.6cm}>{\centering\arraybackslash}p{2.65cm}rr}
\toprule
Benchmark & Atlas cells & Discordance p25/med/p75 & Required $n$ p25/\textbf{med}/p75 & Naive & Advantage \\
\midrule
musr & 24 & 0.015 / 0.034 / 0.044 & 104 / \textbf{231} / 303 & 3{,}386 & $14.7\times$ \\
gpqa & 24 & 0.035 / 0.048 / 0.067 & 243 / \textbf{333} / 460 & 3{,}215 & $9.7\times$ \\
bbh & 192 & 0.024 / 0.044 / 0.060 & 165 / \textbf{303} / 413 & 2{,}886 & $9.5\times$ \\
mmlu\_pro & 5 & 0.048 / 0.053 / 0.059 & 329 / \textbf{368} / 406 & 3{,}420 & $9.3\times$ \\
hellaswag & 23 & 0.031 / 0.045 / 0.099 & 212 / \textbf{309} / 684 & 2{,}180 & $7.1\times$ \\
arc\_challenge & 17 & 0.072 / 0.079 / 0.099 & 495 / \textbf{542} / 683 & 3{,}273 & $6.0\times$ \\
ifeval & 8 & 0.048 / 0.052 / 0.072 & 327 / \textbf{356} / 493 & 1{,}872 & $5.3\times$ \\
mmlu & 1{,}311 & 0.093 / 0.140 / 0.259 & 637 / \textbf{962} / 1{,}780 & 3{,}434 & $3.6\times$ \\
winogrande & 23 & 0.067 / 0.092 / 0.221 & 459 / \textbf{629} / 1{,}521 & 2{,}489 & $4.0\times$ \\
math & 56 & 0.107 / 0.141 / 0.169 & 738 / \textbf{972} / 1{,}160 & 2{,}321 & $2.4\times$ \\
gsm8k & 24 & 0.040 / 0.077 / 0.198 & 275 / \textbf{527} / 1{,}364 & 1{,}188 & $2.2\times$ \\
\midrule
\textbf{ALL (pooled)} & \textbf{1{,}707} & 0.064 / 0.120 / 0.225 & 442 / \textbf{825} / 1{,}546 & 3{,}432 & $\mathbf{4.2\times}$ \\
\bottomrule
\end{tabular}
\end{table}
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

\subsection{Scope caveats carried from the main text}
\label{app:cert:caveats-detail}

% RELOCATED 2026-07-27 (phase 4 trim, candidate 6) from
% sections/certification.tex §"Scope and caveats", caveats 2, 3 and 4, moved
% VERBATIM in content. Caveats 1 and 5 remain in the body.
% SOURCE: results/certification_tables_rev2.csv column n_atlas_cells (the cell
% counts below are all rev-2). The caveat list itself comes from
% docs/CERTIFICATION_TABLES_2026-07-20.md §"Scope and caveats", a REV-1
% narrative whose population figures are superseded; it is cited for the
% caveats, not for any count.

\paragraph{Cell counts behind each family.} Rev-2 moved
\texttt{arc\_challenge} to 17 cells, \texttt{gsm8k} to 24, \texttt{hellaswag}
to 23 and \texttt{winogrande} to 23, taking those out of the thin category;
\texttt{mmlu} (1{,}311), \texttt{bbh} (192) and \texttt{math} (56) are well
supported. Only \texttt{mmlu\_pro} (5) and \texttt{ifeval} (8) remain thin, as
the main text states.

\paragraph{Family aggregation mixes two sources of variation.} The atlas
collapses MMLU's 57 per-subject cells and BBH/MATH/MuSR/GPQA's per-subtask cells
into families, so a family's spread combines subject-level with model-level
variation. This widens the p25--p75 band relative to what a single practitioner
evaluating a single model would see, and therefore makes the quartile columns
\emph{conservative} rather than optimistic.

\paragraph{Feasibility-probe pairs are excluded.} Both disclosed
feasibility-probe pairs (99 cells) are excluded per the atlas registration §6,
as tiny hand-built sanity pairs ($n$ as low as 10, discordance up to
0.9) that would distort every quartile.

% MOVED 2026-07-31. This file used to end with a \TODO asking for the frozen
% protocol documents to be "reproduced verbatim ... or linked at the archived
% commit". Reproduction was chosen: the link option de-anonymises the TMLR
% submission, so it could not be the same text in both builds. The documents now
% live in sections/appendix_registrations.tex, which is GENERATED from the frozen
% files and machine-checked word-for-word against them, and carries
% \label{app:registrations}.
```

---

## FILE: `paper/sections/appendix_atlas_detail.tex`

```latex
% =====================================================================
% Appendix: Atlas construction detail.
% CREATED 2026-07-27 (phase 4 trim, candidate 4). Content moved from
% sections/atlas.tex §§"Construction" and "Coverage, and what the exclusions
% reveal". NOTHING WAS DELETED IN THE MOVE.
%
% What deliberately did NOT move, and must not: the prompt-hash identity
% control (it is the operative admission rule and is cited from §5), the
% empty-join observation (it is a finding, not mechanics), and the paragraph
% recording that rev-1 overstated the exclusions (self-correction the paper is
% partly about).
% =====================================================================

\section{Atlas construction detail}
\label{app:atlas-detail}

\subsection{The two sources}
\label{app:atlas:sources}

% SOURCE: docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §§1, 3.4.
\textbf{S1} is the Open LLM Leaderboard v1 archive: community quantizations
(GPTQ, AWQ, GGUF, 8-bit and 4-bit bitsandbytes) of 2023-era base models, paired
with their base model's details dataset whenever one exists. \textbf{S2} is the
Neural Magic / Red~Hat per-item dumps for quantized Llama-3.1, covering W4A16,
W8A8-INT8 and W8A8-FP8 at 8B, 70B and 405B.

The registration exists to prevent source- or pair-selection after seeing
results, and it labels these analyses descriptive: they estimate flip and churn
magnitudes in the wild and feed the certification tables, they test no registered
hypothesis, and they cannot substitute for any H3 cell.

\subsection{Item pairing}
\label{app:atlas:pairing}

Item pairing is mechanical: items join on the source's own item key, duplicated
keys are dropped entirely on both sides, and an item enters the paired analysis
only if its full-prompt hash is identical across the pair. A pair-task cell is
excluded if fewer than 99\% of joinable items pass that identity check. Differing
harness commits do not exclude a cell, since prompt-hash identity is the operative
control, but are recorded per cell and disclosed.

\subsection{Exclusion breakdown}
\label{app:atlas:exclusions}

% SOURCE: results/atlas_cells_summary_rev2.csv, reason column;
% results/atlas_exclusions_rev2.csv.
% REPOINTED 2026-08-02: the unsuffixed results/atlas_exclusions.csv is the
% superseded rev-1 exclusion table. The rev-2 file is the one these counts were
% read from, and the rev-1 name is a prefix of it, which is why the stale
% pointer survived alongside a correct rev-2 pointer on the line above.
% POPULATION NOTE: these figures (and only these) use the 1,807 count, which is
% the analysed set BEFORE the 99 disclosed probe cells and the float-scored
% remainder are removed to reach the 1,707 analysis population of §5.3.
The enumeration yields \textbf{2{,}055} pair-task cells, of which
\textbf{1{,}807 are analysed} (S1 = 1{,}459, S2 = 348) and \textbf{248} are
excluded or skipped. The exclusions break down as \textbf{179} cells (72.2\%)
for which no results file exists for that task in any recorded run,
\textbf{36} (14.5\%) whose join intersection is empty, and \textbf{33}
(13.3\%) whose task carries no binary correctness metric in the data at all
(genuinely float-scored tasks, which the flip model does not describe).

The full exclusion table ships with the release, one row per excluded cell with
its reason, so the admitted population is auditable rather than asserted.

% RELOCATED FROM sections/atlas.tex 2026-08-05 (compression pass). The body
% keeps the statement that the probe cells would distort a quartile; the
% magnitudes that make that true live here.
The 99 disclosed probe cells are removed for a reason the body states but does
not quantify: they are hand-built sanity pairs with item counts as low as
$n = 10$ and discordance rates as high as $0.9$, so admitting them would move
any quartile of the discordance distribution that the certification tables of
\S\ref{sec:certification} are computed from.

\subsection{The most extreme zero-delta cell}
\label{app:atlas:extreme}

% RELOCATED 2026-08-04 (flagship narrative, operation 8, adapted). Moved from
% sections/atlas.tex §\ref{sec:atlas:identical} with every row intact. The plan
% asked for this to become a panel of Figure 1; the figure is generated by
% scripts/make_figure1.py from a different cell (Qwen2.5-7B / GSM8K) and is
% owned by another workstream, so the table was relocated rather than deleted.
% The body keeps the mechanism, the 17.17/17.17 split, the p = 1.0 and all four
% caveats in prose.
\begin{table}[!t]
\centering
\caption{The most extreme zero-delta cell in the atlas: identical accuracy,
symmetric flips, $p = 1.0$. Read by \S\ref{sec:atlas:identical}, which carries
the caveats that travel with it.}
\label{tab:identical-extreme}
% SOURCE: results/identical_score_churn_rev2.csv, rank 1 row; reproduced in
% docs/IDENTICAL_SCORE_CHURN_2026-07-21.md §"Most extreme zero-delta cell".
% The rank-1 row is byte-identical between rev-1 and rev-2 (pair_index 35,
% high_school_geography_5, churn 0.343434); the citation was repointed to rev-2
% on 2026-07-26 for consistency, not because the values moved.
% WIDTH FIX 2026-08-05: the Value column ran 85pt past the measure on the long
% identifier rows. It wraps now. No value changed.
\begin{tabular}{l>{\raggedright\arraybackslash}p{7.6cm}}
\toprule
Field & Value \\
\midrule
pair\_index / source & 35 / S1 \\
Task                 & \texttt{harness\_\allowbreak{}hendrycksTest\_\allowbreak{}high\_\allowbreak{}school\_\allowbreak{}geography\_\allowbreak{}5} (MMLU) \\
Base model           & \texttt{project-baize/baize-v2-7b} \\
Quantized model      & \texttt{TheBloke/\allowbreak{}Project-Baize-v2-7B-GPTQ} (GPTQ) \\
$n$                  & 198 \\
Baseline accuracy    & 0.429293 \\
Compressed accuracy  & 0.429293 \quad (net delta $= 0.000000$) \\
Accuracy-state churn & \textbf{0.343434} \\
Harmful / beneficial flips & 0.171717 / 0.171717 \\
Exact McNemar $p$    & 1.0 \\
\bottomrule
\end{tabular}
\end{table}
```

---

## FILE: `paper/sections/appendix_minigrid_detail.tex`

```latex
% =====================================================================
% Appendix: Controlled-experiment detail.
% CREATED 2026-08-04 (flagship narrative restructure, operations 2, 3, 9, 10,
% 12 and 13). Content moved from sections/minigrid_escalation.tex (whole file),
% sections/minigrid.tex (tab:h3-ds, the three supporting tables,
% tab:h3-resolution and the deferred-analyses subsection) and
% sections/discriminant.tex (the public-checkpoint pilot).
% NOTHING WAS DELETED IN THE MOVE. Every table keeps every column, every
% caption keeps every qualification, and each % SOURCE comment travels with the
% content it documents.
%
% LABEL CHANGES made in the same commit, with every pointing site repaired:
%   sec:minigrid:escalation -> app:escalation
%   tab:h3-variance / tab:h3-bootstrap / tab:h3-flips -> tab:h3-supporting
%     (one float, three panels; no column dropped, no table shrunk)
%   tab:h3-ds, tab:h3-resolution, tab:minigrid-escalation keep their labels.
%
% HARD RULES INHERITED FROM THE DONOR FILES:
%  - The escalation screen states NO H3 outcome. It is a screening rule.
%  - The registration forbids collapsing seed-level SD into item-level SE; they
%    stay separate variance components in panel (a).
%  - The resolution analysis is POST-HOC and is labelled as such at every
%    appearance.
%  - The pilot is exploratory and its caveats travel with it.
% =====================================================================

\section{Controlled experiment: supporting detail}
\label{app:minigrid-detail}

\subsection{The mechanical escalation screen}
\label{app:escalation}

% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md (SIGNED decision
% record); results/minigrid_escalation/escalation_summary.json.
The four executed cells, $\{$Qwen2.5-1.5B-Instruct, Llama-3.2-3B-Instruct$\}
\times\{$MMLU, GSM8K$\}$, 4-bit GPTQ against 4-bit AWQ at seeds
$\{0,1,2,3,4\}$, with GPTQ and AWQ receiving byte-identical calibration samples
at each seed (\S\ref{sec:minigrid}), feed a pre-committed screen that decides
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

\begin{table}[!t]
\centering
\small
\caption{The mechanical escalation screen over the four completed mini-grid
cells. Outcomes are reproduced verbatim from the signed decision record; the
per-seed accuracies that produce them are not restated here. ``Winner flip''
and ``range/gap holds'' are the two \S3 predicates; the counts beneath drive the
decision.}
\label{tab:minigrid-escalation}
% WIDTH FIX 2026-08-05: tightened column separation and wrapped the widest
% text column. No cell value changed and no row was dropped.
\setlength{\tabcolsep}{4pt}
\small
\begin{tabular}{ll rr >{\raggedright\arraybackslash}p{2.4cm}}
\toprule
Cell & Winner flip & $\mathrm{gap}$ & $\max\mathrm{range}$ & Range/gap holds \\
\midrule
Qwen2.5-1.5B / MMLU  & \textbf{TRUE}  & 0.012292 & 0.040521 & \textbf{TRUE} \\
Qwen2.5-1.5B / GSM8K & FALSE          & 0.096800 & 0.033000 & FALSE \\
Llama-3.2-3B / MMLU  & FALSE          & 0.030922 & 0.063809 & \textbf{TRUE} \\
Llama-3.2-3B / GSM8K & \textbf{TRUE}  & 0.017800 & 0.034000 & \textbf{TRUE} \\
\midrule
% WIDTH FIX 2026-08-05: this summary spanned all five columns on one line and
% was the widest remaining box in the document at 114pt. Split into two rows.
% Both thresholds and both counts are unchanged.
\multicolumn{5}{l}{Winner flip in \textbf{2 of 4} cells (threshold $\geq 1$: met)} \\
\multicolumn{5}{l}{Range/gap holds in \textbf{3 of 4} cells (threshold $\geq 2$: met)} \\
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
The four cells stayed sealed, with no accuracy read by anyone, until the registered
validator passed over the complete 44-JSONL expected set (job \texttt{11375247},
409/409 checks), which is the first mini-grid accuracy inspection the
registration permits. The FP16 gate failure that preceded the run was resolved
\emph{before} any inspection, the gates being re-derived under Amendment~3
(committed \texttt{bd565bd}), so the screen fired on a grid whose reference
gates were already settled rather than tuned to its result.

\paragraph{This screen is not the H3 verdict.}
% SOURCE: docs/MINIGRID_ESCALATION_DECISION_2026-07-23.md, "Decision" paragraph
% ("No H3 verdict is stated here ... the confirmatory rule is defined over all
% eight cells"); docs/MINIGRID_REGISTRATION_2026-07-15.md §4.
Escalation is a screening decision about \emph{which cells to build}, not a
conclusion about H3. The confirmatory verdict is the frozen
Supported/Disconfirmed/Inconclusive rule applied once, mechanically, over all
eight cells, this grid plus the 7B/8B cells, and it is defined only when all
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

\subsection{Per-seed differences behind the winner-flip column}
\label{app:minigrid:ds}

% SOURCE: docs/H3_EIGHT_CELL_DECISION_2026-07-26.md, "Per-cell registered
% quantities" (all eight cells). Values are read from that record at the six
% decimals it publishes.
Table~\ref{tab:h3-ds} gives the per-seed differences $d_s$ behind the
winner-flip column of Table~\ref{tab:h3-eightcell}, so every flip determination
is checkable by inspection of sign.

\begin{table}[!t]
\centering
\small
\caption{Per-seed differences $d_s = \mathrm{acc}_{\mathrm{GPTQ},s} -
\mathrm{acc}_{\mathrm{AWQ},s}$ on byte-identical calibration samples. A winner
flip is two seeds of opposite, nonzero sign; the five cells with a flip are
those whose row is not sign-constant. No entry is zero, which is the 0-of-40 tie
count stated in \S\ref{sec:minigrid:verdict}.}
\label{tab:h3-ds}
% WIDTH FIX 2026-08-05: 47.8pt past the measure. \small plus tighter column
% separation. No cell value changed and no row was dropped.
\setlength{\tabcolsep}{2pt}
\small
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

\subsection{The three registered supporting analyses}
\label{app:minigrid:supporting}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slots 2, 3 and 4.
% RELOCATED 2026-08-04: these were three separate body floats
% (tab:h3-variance, tab:h3-bootstrap, tab:h3-flips). They are now three panels
% of one float. No column was dropped and no font was reduced; the three tables
% were already \small in the body and remain \small here.
The three analyses were run once per cell at the registered parameters
(2{,}000 bootstrap replicates, RNG seed 0) as part of the same job that produced
the verdict, and \S\ref{sec:minigrid:supporting} reads them. None of them
modifies the verdict, and none can.

\begin{table}[!t]
\centering
\small
\caption{The three registered supporting analyses over the eight confirmatory
cells. \textbf{(a)}~Variance components, reported separately as registered: SD
is across the five calibration seeds, SE is the item-level standard error within
a cell, and MMLU cells run at $n = 14{,}042$ against GSM8K's $n = 1{,}000$,
which is what drives the SE columns. \textbf{(b)}~Two-level paired bootstrap,
2{,}000 replicates at RNG seed 0, both registered; tie replicates are reported
separately and are included in the rank-flip denominator, per the registered
convention, and the final column repeats the registered winner-flip outcome,
which is a different question and not a consistency check.
\textbf{(c)}~Flip statistics, GPTQ against AWQ, means over the five paired
seeds: net delta is
$\mathrm{acc}_{\mathrm{AWQ}} - \mathrm{acc}_{\mathrm{GPTQ}}$, harmful and
beneficial are the two directions of correctness change, accuracy-state churn is
their sum, and total answer churn adds items that change answer without changing
correctness state.}
\label{tab:h3-supporting}

\textbf{(a) Variance components, kept separate}\par\medskip
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

\medskip
\textbf{(b) Two-level paired bootstrap}\par\medskip
% WIDTH FIX 2026-08-05: 54.1pt past the measure. Values unchanged.
\setlength{\tabcolsep}{2pt}\small
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

\medskip
\textbf{(c) Flip statistics, GPTQ against AWQ}\par\medskip
% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, slot 4 table.
% base = GPTQ, method = AWQ, so net delta = acc_AWQ - acc_GPTQ (= -d_s in the
% decision record's sign convention). Churn quantities are direction-symmetric.
% Metrics from flipeval.core.compute_pair_metrics -- the same function behind
% the atlas population of \S\ref{sec:atlas}.
% WIDTH FIX 2026-08-05: tightened column separation and wrapped the widest
% text column. No cell value changed and no row was dropped.
\setlength{\tabcolsep}{2.5pt}
\footnotesize
\begin{tabular}{llrrrrrr}
\toprule
Model & Task & Net $\Delta$ & Harmful & Benef. & Churn & W$\to$w & Ans.\ churn \\
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

Panel~(c) applies the atlas metrics of \S\ref{sec:atlas} to the controlled
cells, computed by the same function over the same definitions, so the two
populations can be read against each other. Here the contrast is \emph{method
against method at one bit width}, where the atlas contrast is quantized against
FP16.

\subsection{Post-hoc resolution analysis}
\label{app:minigrid:resolution}

% SOURCE: docs/MINIGRID_SUPPORTING_RESULTS_2026-07-26.md, "Step 5 -- resolution
% analysis (POST-HOC)" table.
\begin{table}[!t]
\centering
\small
\caption{Post-hoc resolution analysis, read by \S\ref{sec:minigrid:resolution}.
Ranges of the two ratios across the four cells of each task. $p_d$ is computed
per cell from panel~(c) of Table~\ref{tab:h3-supporting} and is \emph{not} the
harness study's $\bar{Q}$, which is a quantized-against-FP16 contrast on a
different pair. This quantity was not registered; it was requested after the
eight-cell verdict was computed and signed, it tests no hypothesis, and it
modifies no verdict.}
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

\subsection{Deferred registered analyses}
\label{app:minigrid:deferred}

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

\subsection{The earlier public-checkpoint pilot}
\label{app:minigrid:pilot}

% RELOCATED 2026-08-04 from sections/discriminant.tex, which is deleted. The
% discriminant argument now lives in \S\ref{sec:minigrid:resolution}, where the
% figures it reads are reported; the pilot is historical corroboration and its
% caveats travel with it unchanged.
% SOURCE: results/PILOT_RESULTS.md (archive
% pilot_outputs_20260711T000427Z.tar.gz, sha256 a72ff2fd...898a72ecb8).
The project's earlier public-checkpoint pilot shows the same discriminant
behaviour under worse conditions, and adds the case the eight cells lack, a
positive detection: MMLU with a public GPTQ checkpoint at $n = 400$ gave
$-4.25$\,pp at exact McNemar $p = 0.036$, while GSM8K at $n = 200$ gave
$p = 0.672$ and $p = 0.880$ on churn of $0.250$ and $0.220$, two correct
declinations where detection would have needed 4{,}923 and 17{,}347 items.
\emph{The smaller evaluation is the one that detected nothing.} Its caveats
bound it entirely (raw-text prompts with no chat template, an unpinned Kaggle
image modified in place, two public checkpoints with fixed or undocumented
calibration so it cannot test H3, and wide intervals at $n = 400$ and $200$),
and it is exploratory evidence for discriminant behaviour and nothing else.
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

\subsection{Two observed defects}
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
reference (chat template on, three inline GSM8K exemplars, zero-shot for MMLU,
and \texttt{flexible-extract} scoring), which is the configuration the mini-grid's
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
the reference and a condition, meaning the fraction of items whose
correct/incorrect state changes, on the same churn definition the atlas uses
(\S\ref{sec:atlas}), on the FP16 model over the item set above, and the
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
\texttt{MINIGRID\_REGISTRATION} \S5 permits had been authorized, so the
denominator is not an early look at the confirmatory grid under another name.
% SOURCE: docs/HARNESS_SENSITIVITY_QBAR_2026-07-23.md (validator 11375247,
% 409/409, first inspection authorized 2026-07-23);
% docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §5.2 (two-phase deferral).
A shortcut that would have produced the ratio roughly five weeks earlier, a
dated amendment permitting an early partial inspection of the bridge quantized
deltas, was considered and declined, on the ground that the registered
blindness is not weakened to obtain a number sooner.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §9.1
% (option considered and declined by Amogh 2026-07-22).

\subsection{Condition B in full}
\label{app:sensitivity:condB}

Condition~B is the sharpest result and deserves isolating, because it holds the
generations fixed. It costs zero GPU time: the stock \texttt{gsm8k} task applies
both \texttt{strict-match} and \texttt{flexible-extract} to the same outputs in a
single run, so B is read out of the reference run's own samples file, a genuine
rescore of \emph{identical} generations, not a second pass.
% SOURCE: docs/HARNESS_SENSITIVITY_REGISTRATION_2026-07-22.md §3.1 (B is a filter
% rescore of REF, zero GPU); docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md
% (B derived from REF samples).
Its correctness churn is therefore the pure effect of the extraction filter:
$C_B = 0.455$ ($91$ of $200$ items), with a directional split of
$\textbf{91}/\textbf{0}$: every changed item went correct$\to$incorrect, so the
$0.455$ accuracy drop equals the churn exactly and \texttt{strict-match} accepts
a strict subset of what \texttt{flexible-extract} accepts here. The resulting
$R_B = 0.455/0.287 = \textbf{1.585}$: on these items, choosing one of two
built-in scoring filters that ship with the same task moves the fixed model's
per-item correctness \emph{more than half again as much} as quantization does.
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, GSM8K row B (C_cond
% 0.4550, 91/200, dir 91/0, R 1.585); results JSON per_task.gsm8k.conditions.B_strict_match.
No compression method in the comparison set produces a swing of that kind from a
choice a practitioner never records.

\subsection{The same move, in another domain}
\label{app:sensitivity:bronder}

% RELOCATED 2026-08-04 (flagship narrative, operation 15) from
% sections/harness_sensitivity.tex, moved verbatim. The body keeps a one-clause
% pointer.
Holding the system fixed and varying the instrument is not specific to
compression. \citet{bronder2026instrument} do it for language-model
\emph{honesty} evaluation: with the player model held fixed, four instrument
choices (outcome grammar, criterion disclosure, budget rendering and register
presence) substantially changed what the evaluation would have reported, under
decision rules recorded before results were read. That study and this one share
a design and a conclusion on different objects, which is the reason to expect
the effect wherever an evaluation is treated as a fixed instrument.

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

\subsection{Condition-by-condition results}
\label{app:sensitivity:conditions}

% RELOCATED FROM sections/harness_sensitivity.tex 2026-08-05 (compression
% pass, relocation 1 of the agreed order). The table and the
% condition-by-condition reading move here whole; the body keeps the question,
% the R range, and the protected Scope paragraph verbatim. Nothing was deleted
% and no value changed. tab:sensitivity had no reference outside its own
% section, so the move breaks no cross-reference.
% SOURCE: docs/HARNESS_SENSITIVITY_RESULTS_2026-07-23.md, GSM8K table
% (n=200, REF acc 0.5750, Qbar 0.287) and MMLU table (n=400, REF acc 0.4150,
% Qbar 0.199; C==D acc 0.4600, net +0.0450, C_cond 0.2100 (84/400), dir 33/51,
% R 1.055); every cell cross-checked against
% results/harness_sensitivity/sensitivity_results_qwen25-1p5b.json
% per_task.{gsm8k,mmlu}.conditions (acc_cond, net_acc_delta, C_cond,
% correctness_changed, answer_churn, dir_correct_to_incorrect,
% dir_incorrect_to_correct, R_cond).
% C and D are byte-identical for MMLU (registration §3.3); the argument is at
% app:sensitivity:mmlu-collapse.
\begin{table}[!t]
\centering
\small
\caption{Configuration sensitivity on FP16 Qwen2.5-1.5B, against the
quantization denominator $\bar{Q}$ for each task. $C_{\mathrm{cond}}$ is
correctness-state churn versus the reference; $R=C_{\mathrm{cond}}/\bar{Q}$ is
reported only with both inputs in view. The
$\text{c}{\to}\text{i}/\text{i}{\to}\text{c}$ column splits churned items by
direction so churn is never read as net degradation. Conditions~C and~D are
byte-identical for MMLU and are reported once as $C\equiv D$ (registration
\S3.3).}
\label{tab:sensitivity}
% WIDTH FIX 2026-08-05: tightened column separation and wrapped the widest
% text column. No cell value changed and no row was dropped.
\setlength{\tabcolsep}{2pt}
\small
\begin{tabular}{l>{\raggedright\arraybackslash}p{2.7cm}rrrrr}
\toprule
Cond & Configuration vs.\ reference & Acc & Net $\Delta$ & $C_{\mathrm{cond}}$ & c$\to$i / i$\to$c & $R=C_{\mathrm{cond}}/\bar{Q}$ \\
\midrule
\multicolumn{7}{l}{\emph{GSM8K}, $n=200$, reference accuracy $0.575$, $\bar{Q}=0.287$} \\
A & exemplars as separate turns   & 0.515 & $-0.060$ & \textbf{0.240} & 30 / 18 & \textbf{0.836} $=0.240/0.287$ \\
B & \texttt{strict-match} rescore & 0.120 & $-0.455$ & \textbf{0.455} & 91 / 0  & \textbf{1.585} $=0.455/0.287$ \\
C & chat template off, 3-shot     & 0.475 & $-0.100$ & \textbf{0.320} & 42 / 22 & \textbf{1.115} $=0.320/0.287$ \\
D & stock defaults (chat off, 5-shot) & 0.495 & $-0.080$ & \textbf{0.300} & 38 / 22 & \textbf{1.045} $=0.300/0.287$ \\
\midrule
\multicolumn{7}{l}{\emph{MMLU}, $n=400$, reference accuracy $0.415$, $\bar{Q}=0.199$} \\
$C\equiv D$ & chat template off, zero-shot & 0.460 & $\mathbf{+0.045}$ & \textbf{0.210} & 33 / 51 & \textbf{1.055} $=0.210/0.199$ \\
\bottomrule
\end{tabular}
\end{table}

Three of the four GSM8K conditions (turning the chat template off, accepting
every stock default at once, and switching the extraction filter) have
$R \geq 1$: each moves a fixed model's per-item correctness by \emph{as much as
or more than} swapping in one of ten quantized variants moves it. Only
condition~A, the multiturn exemplar placement, stays below the quantization
scale. The net accuracy deltas understate the movement in every case, because
they net directional churn that the
$\text{c}{\to}\text{i}/\text{i}{\to}\text{c}$ column keeps separate.
Condition~B is sharpest because it holds the generations fixed: the stock task
applies both filters to the same outputs, so B is a rescore of \emph{identical}
generations at zero GPU cost, and its $91/0$ split means \texttt{strict-match}
accepts a strict subset of what \texttt{flexible-extract} accepts here
(Appendix~\ref{app:sensitivity:condB}).

The MMLU cell makes a point the net delta hides. Turning the chat template off
\emph{raises} reported accuracy by $+4.5$\,pp ($0.415 \to 0.460$), with a
directional split of $33/51$, meaning more items recovered than lost. The
harness default is therefore not uniformly worse than the reference: on MMLU it
is better, on GSM8K worse, and either way \emph{different}. The churn behind the
$+4.5$\,pp is $0.210$ ($84$ of $400$ items), giving $R=1.055$, again on the
quantization scale. The movement is real, signed differently on the two tasks,
and of a kind compression papers do not report: the setting that almost never
appears in a model card is precisely the one silently moving the number a
``near-lossless'' claim rests on. Holding the system fixed and varying the
instrument is not specific to compression, and
Appendix~\ref{app:sensitivity:bronder} records the same design and the same
conclusion on a different object.
```

---

## FILE: `paper/sections/appendix_artifacts_detail.tex`

```latex
% =====================================================================
% Appendix: Artifact detail (datasheet, metadata, maintenance)
% -- Relocated from sections/artifacts.tex on 2026-07-26 as part of the
%    structural trim. NOTHING WAS DELETED IN THE MOVE.
% -- Datasheet TODO resolved 2026-07-27 in the \citet{gebru2021datasheets}
%    format. Every required item from the TODO appears below, marked (*).
%
% D&B hygiene. Required in full if NeurIPS Datasets & Benchmarks is the target
% venue; for COLM/ACL the main text keeps one paragraph (sections/artifacts.tex)
% and the detail lives here.
%
% RULE, UNCHANGED: no URL, DOI, or version number may be written here until it
% exists. The version string v1.0.0 is pinned by the release checklist; the DOI
% and dataset URL remain \TODO until Amogh has minted them.
% =====================================================================

\section{Artifact detail}
\label{app:artifacts-detail}

\subsection{The six released artifacts}
\label{app:artifacts:released}

% RELOCATED 2026-08-05 (flagship narrative, §6 target for sections/artifacts.tex)
% from sections/artifacts.tex. The per-artifact descriptions and the detail of
% the redistribution review are moved here whole; the body keeps a one-sentence
% summary of each and a pointer to this subsection. NOTHING WAS DELETED.
% SOURCE for the per-item counts: \S\ref{sec:audit:v3};
% results/audit_verdicts_rev3.csv column v3_per_item_outputs over the 16
% ELIGIBLE rows (0 yes, 3 partial, 13 no). Counts come from \Audit* macros.
The \textbf{per-item outputs} are 88 cell JSONL files, one row per evaluation
item, for every model $\times$ method $\times$ seed $\times$ task in the
controlled experiment, carrying the per-item correctness state that the paired
test consumes. \S\ref{sec:audit:v3} reports that \AuditPerItemTaskMatched{} of
the \AuditEligible{} eligible sources release \emph{task-matched} per-item
outputs, those covering the tasks their own equivalence claim is about, and that
\AuditPerItemOtherTaskOnly{} (\AuditPerItemOtherTaskClaims{}) release outputs for
other tasks only; the fifth line of the reporting standard in
\S\ref{sec:conclusion} asks the field to close that gap, and withholding ours
would leave that recommendation untestable against the paper making it. They
ship in both forms deliberately: the extracted files are directly loadable, and
the two sealed run archives carry the same bytes with a per-file SHA-256
manifest and an archive checksum recorded when the runs completed, so the
loadable copy can be checked against the record made at run time instead of
trusted.

The \textbf{flip atlas} gives per-cell paired statistics for every enumerated
pair-task cell, with the exclusion table and the frozen 59-pair manifest.
\texttt{flipeval} is the analysis package: flip rates, the churn family, exact
McNemar, TOST at a declared margin, bootstrap intervals, item-bootstrap
rank-flip rates, minimum detectable difference, required-$n$, and the
certification-table generator (Apache-2.0; everything else is CC-BY-4.0). The
audit artifacts are the frozen 17-claim table with source content hashes and the
per-claim verdict CSV, with every robustness and transparency column, plus the
source manifest and retrieval script described below; the captured source text
itself is not among them. The certification tables ship twelve rows per margin
at 1, 2 and 3\,pp. The reproduction package holds registrations and their dated
amendments, signed decision records, configs, the container image SHA-256 and
build recipe, scheduler scripts, per-run manifests, the source-state freeze
fingerprints, and the campaign incident log, which is included on purpose: a
pipeline with 28 recorded catches is better evidence that it was verified than
one presenting a clean surface.

% RELOCATED 2026-08-05 from sections/artifacts.tex, where a one-sentence summary
% of the review's finding remains. Option A, chosen by the author 2026-08-02.
% SOURCE, licensing: redistribution review of 2026-08-02, recorded in
% docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md §10. Four sources with no
% third-party republication grant (R11 Meta AI blog, R12 NVIDIA TensorRT-LLM
% doc, R13 and R14 vLLM pages) plus the arXiv default licence over R01-R07.
% SOURCE, provenance: docs/audit_sources_manifest.tsv status column (15 MATCH,
% R11 MISMATCH, R13 NO-BASELINE) and scripts/fetch_audit_sources.py, whose
% UNSTABLE map lists R11 and R12. Offline run 2026-08-02 over the private
% archive: 17 verified, 0 drifted, 0 expected-drift, 0 unverifiable, 0 failed.
% DO NOT write "no source permits redistribution" or any general statement of
% what is lawful. What is claimed here is what was checked and what it found.
The redistribution review of 2026-08-02 examined the terms attached to each
audited source before any copy was published. It found four sources, the Meta AI
blog post, the NVIDIA TensorRT-LLM documentation page and two vLLM pages,
carrying no grant that would permit a third party to republish their text, and
it found the seven method papers under arXiv's default licence, which authorises
arXiv to distribute them rather than authorising us to. Publishing the corpus was
therefore never an option that was open to us, and the working archive of it is
kept private. What ships instead is what makes the corpus rebuildable and
checkable: the source URL and pinned version identifier for every claim, a
SHA-256 for every captured file, the per-file manifest
\texttt{docs/\allowbreak{}audit\_sources\_\allowbreak{}manifest.tsv} carrying
both digests and a per-row provenance status, and
\texttt{scripts/\allowbreak{}fetch\_\allowbreak{}audit\_sources.py}, a
standard-library script that re-fetches each source by the retrieval method
recorded for it and compares the result against the recorded digest. Quoted text
appears in this paper as short excerpts with their locations, and a reader who
runs the script obtains each source from its own publisher. Two of the
seventeen, R11 and R13, bound what a digest can establish at all; the manifest
records that per row, neither is described anywhere in this paper as
hash-verified, and \S\ref{app:artifacts:datasheet} states what each limit is.

\subsection{Datasheet}
\label{app:artifacts:datasheet}

Following \citet{gebru2021datasheets}.

\paragraph{Motivation.} The artifacts exist to make the paper's own
recommendation checkable against the paper. \S\ref{sec:audit} reports that no
audited source releases per-item outputs; withholding ours would make the
recommendation unfalsifiable. They were created by the author, with no external
funding beyond a university compute allocation.

\paragraph{Composition.} Three kinds of record. (i) \textbf{Per-item outputs}:
88 cell JSONL files, one row per evaluation item, covering every model $\times$
method $\times$ seed $\times$ task in the controlled experiment. (ii)
\textbf{Derived per-cell statistics}: the atlas, at one row per pair-task cell,
with flip and churn quantities, McNemar and TOST outcomes. (iii)
\textbf{Provenance records}: registrations, signed decisions, configs, receipts,
fingerprints and the incident log. \textbf{(*) The atlas contains no
human-subject data and no personally identifying information}; its rows describe
model behaviour on public benchmark items. \textbf{(*) The population is the
public record of compression evaluation, not a census of quantization}
(\S\ref{sec:atlas:caveats}): it is conditioned on what was published and
leaderboard-indexed, so it describes the evidence the field circulates rather
than how quantization behaves in general.

\paragraph{Collection.} S1 cells were mined from public per-item evaluation
dumps; S2 from vendor-published evaluations; the controlled cells were generated
by us inside a pinned container, under protocols frozen before the runs
(\S\ref{sec:prereg}). Pair enumeration was frozen in a manifest before any
statistic was computed.

\paragraph{Preprocessing.} A pair-task cell is admitted only when both sides
carry a binary per-item correctness state and full-prompt hashes match across the
pair. Exclusions are released as a table with a reason per row rather than
summarised, so the admitted population is auditable and not merely asserted.

\paragraph{Distribution and licensing.} Released under \textbf{CC-BY-4.0};
the \texttt{flipeval} package under \textbf{Apache-2.0}.
\textbf{(*) S1's Open LLM Leaderboard v1 archive carries no declared license},
which is recorded as a limitation rather than worked around: we redistribute
\emph{our derived per-cell statistics} and \textbf{not} the raw upstream
per-item files. The frozen pair manifest records the upstream dataset
identifiers and run timestamps per pair, so a third party can re-derive S1 from
the original sources.
% SOURCE for the S1 license limitation:
% docs/ATLAS_MINING_REGISTRATION_2026-07-15.md §2.
\textbf{(*) S2 is Apache-2.0} upstream. Site-specific identifiers (absolute
paths, charge account, usernames, cluster hostnames) were replaced with
placeholders before publication; no accuracy, hash, count, seed, timestamp, job
ID or decision value was altered, and the sealed archives were not rewritten, so
their recorded checksums still verify.
% ADDED 2026-08-02. Final rev-3 checklist §8, Option A. Keep this consistent
% with sections/artifacts.tex; that paragraph is the primary statement and this
% is the datasheet's licensing entry for the same decision.
\textbf{(*) The 17 audited sources are not redistributed.} A redistribution
review on 2026-08-02 found four of them with no third-party republication grant
and the seven method papers under arXiv's default licence, which authorises
arXiv rather than us to distribute them, so the release carries source URLs,
pinned version identifiers, per-file SHA-256 digests, the manifest and a
retrieval script in place of the captured text, and the full-text captures are
kept private (\S\ref{sec:artifacts}). \textbf{(*) Two sources carry provenance
limits no digest can close}, and the manifest records that per row rather than
averaging it away.
% RELOCATED 2026-08-04 (flagship narrative, operation 15) from
% sections/artifacts.tex. The body keeps the fact that two of the seventeen
% bound what a digest can establish and points here; the per-source detail,
% including the expected-drift handling and the fifteen clean re-fetches, is
% carried across whole so nothing was lost in the move.
R11 is served with per-response content: two fetches made seconds apart returned
different bytes, so the digest recorded for it was never a valid fingerprint of
the page, and the retrieval script reports it as expected drift rather than as a
verification failure. R13 does carry a digest for the archived capture, so a
re-fetch can be checked against that capture; what is absent is any digest
recorded \emph{before} the capture was made, so the capture itself was never
corroborated against an independent earlier record. Provenance for these two is
documentary rather than cryptographic, neither is described anywhere in this
paper as hash-verified, and the other fifteen reproduced their recorded digests
exactly when re-fetched on 2026-07-31.

\paragraph{Revision history.} Both revisions are published and the delta is
reported. Rev-1 carried a population defect found by an independent spot-check
that reconciled all 262 compared fields: the arithmetic was right and the
population was not (\S\ref{sec:prereg-spotcheck},
Appendix~\ref{app:prereg:rev2delta}). Rev-2 is what the paper cites; rev-1 is
retained rather than overwritten, because a corrected artifact whose correction
remains visible is this paper's argument applied to itself.

\subsection{Metadata and identifiers}
\label{app:artifacts:metadata}

Released at version \textbf{v1.0.0}, the string shared by the source tag, the
archived release and the dataset revision. The archived DOI is canonical for
citation; the dataset repository is a convenience mirror.

% RESOLVED 2026-07-30 -- see the head of sections/artifacts.tex for how each
% identifier was verified. The version/concept distinction matters here more
% than anywhere: they differ only in the final digit.
% Value column is p{} rather than l: the mirror path used to be hand-split
% across two rows to fit an l column, which a macro cannot do. A p column wraps
% at the \allowbreak points \datasetpath carries.
\begin{tabular}{@{}l p{0.56\linewidth}@{}}
\toprule
Identifier & Value \\
\midrule
% ANONYMITY 2026-07-31: routed through main.tex macros for the TMLR build.
Version DOI (canonical) & \versiondoi \\
Concept DOI (latest) & \conceptdoi \\
Source package & \repopath, tag \texttt{v1.0.0} \\
Dataset mirror (secondary) & \datasetpath \\
Container image SHA-256 & \texttt{8260d04c\ldots1db2007} \\
\bottomrule
\end{tabular}

\medskip
\noindent The \textbf{version DOI is what this paper cites}: it resolves to one
frozen state, which is the only thing the reported numbers describe. The concept
DOI is correct only when referring to the artifact series. A
\textbf{Croissant record} is served by the dataset repository at its standard
\texttt{/croissant} endpoint and carries the CC-BY-4.0 licence through to the
machine-readable metadata.

\subsection{Maintenance}
\label{app:artifacts:maintenance}

Maintained by the author for \textbf{at least 12 months} from release, via the
source repository's issue tracker, with a target first response of two weeks.
Fixes ship as new tagged versions with a changelog; released versions are never
edited in place, and a superseded revision stays published beside its
replacement. \textbf{Adding atlas pairs requires a dated amendment to the atlas
registration}, not a silent extension. The frozen pair manifest is what makes
the population auditable, so growing it quietly would remove the property the
artifact exists to demonstrate.

% RELOCATED 2026-08-05 from sections/artifacts.tex, moved verbatim with the
% comment that governs it.
% The harness sentence is deliberately SMALL. There is no pull request. What
% exists is a comment on an open issue (2026-07-21, followed up 2026-07-24) and
% no maintainer reply. "Submitted", "contributed" and "upstream patch" would all
% be false. Do not upgrade this wording without re-running that search.
% ANONYMITY 2026-07-31: the issue identifier goes through a macro defined in
% main.tex. Do not write a URL, DOI or issue number directly into this paragraph.
The paired-comparison layer described in \S\ref{sec:artifacts} has been
\textbf{proposed} to the \texttt{lm-evaluation-harness} maintainers, in a comment
on \harnessissue; no integration has been merged, and none should be inferred.
```

---

## FILE: `paper/sections/appendix_extraction.tex`

```latex
% =====================================================================
% Appendix: the automated extraction procedure, its reliability, and the
% AI-use statement.  ADDED 2026-07-31.
%
% Motivated by advisor review: the paper described the claim extraction only as
% "two mutually blind passes" and never said the passes were language-model
% agent sessions. The only disclosure was inside the reproduced registration
% (Amendment 1), which is not where a reader looks.
%
% RULE FOR THIS FILE: nothing here may be inferred. Every specification item is
% either read from a committed artifact (cited inline) or explicitly listed as
% NOT RECORDED. Do not fill a gap in the specification table with a plausible
% value -- an invented model ID or temperature is worse than an admitted gap,
% because it cannot be checked and it misrepresents the provenance the rest of
% the paper is built on.
% =====================================================================

\section{Automated claim extraction: procedure, reliability, and AI use}
\label{app:extraction}

\subsection{Why this appendix exists}

The claim table underlying \S\ref{sec:audit} was populated by language-model
agent sessions rather than by human reading. That is a provenance fact a reader
needs in order to weigh the audit, and it was previously stated only inside the
reproduced audit registration (Amendment~1,
\S\ref{app:reg:audit}). This appendix states it directly, specifies as much of
the procedure as the record supports, and is explicit about the parts the
record does not support.

\subsection{The procedure as executed}

% SOURCE: docs/AUDIT_RECONCILIATION_2026-07-15.md; commits 8a16722 (pass 1)
% and 43ce229 (frozen table); docs/AUDIT_REGISTRATION_2026-07-15.md Amendment 1.
\begin{enumerate}
\item \textbf{Pass 1} enumerated the registered source frames and extracted the
  registered fields for each qualifying claim, producing 13 rows
  (\texttt{docs/\allowbreak{}audit\_\allowbreak{}claim\_\allowbreak{}table\_\allowbreak{}pass1.csv}, committed 2026-07-15 as an
  explicitly unfrozen artifact). Some pass-1 fields were derived from a
  summarised reading of the source rather than from the source text directly;
  those rows are flagged in the reconciliation memo.
\item \textbf{Pass 2} ran as a fresh session with the pass-1 file withheld,
  instructed not to read it or recover it from version history, and given only
  the frozen protocol and the source frames. It produced 23 rows (17 claims
  plus 6 logged exclusions) and recorded a SHA-256 of each fetched source
  (\texttt{docs/\allowbreak{}audit\_\allowbreak{}claim\_\allowbreak{}table\_\allowbreak{}pass2.csv}).
\item \textbf{Human reconciliation} merged the two passes into
  \texttt{docs/\allowbreak{}audit\_\allowbreak{}claim\_\allowbreak{}table.csv} (17 claims), resolving inclusion
  disagreements against the registered trigger vocabulary, choosing the quote
  anchored in that vocabulary, and re-reading the cited table wherever the
  passes differed numerically. The merged table was frozen by commit
  \texttt{43ce229} before any verdict, power or required-$n$ computation ran.
  The adjudication is recorded claim-by-claim in
  \texttt{docs/\allowbreak{}AUDIT\_\allowbreak{}RECONCILIATION\_\allowbreak{}2026-07-15.md}.
\end{enumerate}

This replaced the registration's original ``extracted twice on different days''
independence mechanism. Amendment~1 records both the substitution and its
rationale: temporal separation was a proxy for extractor independence calibrated
to human memory, and a fresh session carries no memory of pass~1 at all. The
amendment also records that it was made after pass-1 results were known but
before any verdict computation, and that the \S3.1--3.2 inclusion and extraction
rules were unchanged.

\paragraph{What separate sessions do and do not buy.}
They prevent direct leakage: pass~2 cannot copy pass~1 because it never saw it.
They do \emph{not} deliver the property dual coding is normally used for. Two
sessions of the same model share a prior, so a systematic misreading, such as a
tendency to treat a reported delta as a declared bound or to prefer the
abstract's phrasing over a table footnote, will recur in both passes and will
survive reconciliation looking like agreement. We therefore do not describe
these passes as independent coders, and we do not report an inter-rater
reliability coefficient, which would imply an independence the design does not
have.

\subsection{Specification: what is on record and what is not}

% Every NOT RECORDED row below is a real gap in the 2026-07-15 provenance. They
% are listed rather than omitted so a reader can see the exact boundary of what
% is checkable.
\begin{tabular}{@{}p{0.36\linewidth}p{0.58\linewidth}@{}}
\toprule
Item & Status \\
\midrule
Execution date & 2026-07-15, both passes (commit timestamps
  \texttt{8a16722}, \texttt{43ce229}) \\
Tool family & Command-line coding agent, operated under the repository's
  committed agent guardrails (\texttt{AGENTS.md}, \texttt{CLAUDE.md}) \\
Browsing / retrieval & Enabled; pass 2 fetched each source and recorded its
  SHA-256 \\
Input documents & The registered source frames; per-source SHA-256 in
  \texttt{audit\_\allowbreak{}claim\_\allowbreak{}table\_\allowbreak{}pass2.csv} \\
Output schema & The registered \S3.2 extraction fields; both raw pass files
  are released \\
Human adjudication & Documented per claim in
  \texttt{docs/\allowbreak{}AUDIT\_\allowbreak{}RECONCILIATION\_\allowbreak{}2026-07-15.md} \\
\midrule
Exact model ID and version & \textbf{Not recorded} \\
System and extraction prompts & \textbf{Not recorded; not released} \\
Temperature, seed, reasoning setting & \textbf{Not recorded} \\
Retry policy & \textbf{Not recorded} \\
Whether prompts varied across sources & \textbf{Not recorded} \\
\bottomrule
\end{tabular}

\medskip
\noindent
The lower block is a genuine limitation and we state it as one rather than
reconstructing plausible values after the fact. The consequence is specific:
the extraction is \textbf{auditable but not re-executable}. A reader can check
every extracted field against the released source hashes and the released raw
pass files, and can re-do the extraction by any means they choose; they cannot
reproduce \emph{our} extraction run. Prompt and model-identifier logging is a
requirement we would register in advance if this study were run again, and it is
part of the reporting standard \S\ref{sec:conclusion} proposes.

\subsection{Agreement between the two passes}

Eleven sources were extracted by both passes. Two were reached only by pass~1
and twelve only by pass~2; the union was adjudicated by hand, and one source
(QuIP\#) was included by pass~2 and excluded on adjudication because neither of
its candidate phrases is in the registered trigger vocabulary.

% SOURCE: computed over docs/audit_claim_table_pass1.csv and
% docs/audit_claim_table_pass2.csv, joined on normalised source_url.
On the eleven jointly extracted sources, the two categorical registered fields
agree exactly:

\begin{tabular}{@{}lr@{}}
\toprule
Field & Agreement \\
\midrule
\texttt{per\_item\_outputs\_released} (yes / no / partial) & 11 / 11 \\
\texttt{statistical\_\allowbreak{}test\_\allowbreak{}or\_\allowbreak{}interval\_\allowbreak{}reported} (any / none) & 11 / 11 \\
\bottomrule
\end{tabular}

\medskip
\noindent
\textbf{The free-text numeric fields cannot be scored this way, and we do not
report a number for them.} The two passes recorded different \emph{scope} by
design rather than different values: pass~1 tended to record every task in the
source's table, pass~2 the single anchor task attached to the quoted sentence.
For GPTQ, for example, pass~1 recorded deltas for five OPT-175B tasks and
pass~2 recorded the PIQA figure alone, which is the same underlying numbers at
different granularity. A string-equality comparison scores that as a disagreement and
would put ``exact agreement'' at 11\%, which would misdescribe the record. A
value-level comparison is equally unreliable, because these fields are prose
containing incidental numbers.

What is on record is the reconciliation memo's finding, made at merge time by
re-reading the cited table for every discrepancy: \emph{every} numeric
disagreement between the passes was a difference of scope, not of value. We
report that as the qualitative finding it is. A quantitative inter-pass
agreement rate on numeric fields was not computed at extraction time and cannot
be reconstructed now without imposing a scoring rule that did not exist then.

\paragraph{Validation against human reading was not performed.}
No random subset was independently extracted by a second human without sight of
the agent output. That check would materially strengthen the audit and it is the
first thing we would add.

\subsection{AI-use statement}

% Wording constraint: this must not claim human authorship of agent-produced
% steps, and must not claim artifacts (prompts, model IDs) that are not released.
Language-model tools were used in this work for two blinded structured
extraction passes over the audited sources, and for copy-editing. The author
designed the study, wrote the preregistrations and froze them before execution,
wrote and verified the analysis code, adjudicated every extraction disagreement
by re-reading the cited sources, checked the reported results against the
released artifacts, and takes responsibility for the whole manuscript. The
claim table produced by the extraction passes is released in both raw
(per-pass) and reconciled form, together with per-source content hashes and the
claim-by-claim adjudication record. Model identifiers, prompts and generation
settings for the extraction sessions were not logged at the time and are
therefore not released; see the specification table above.
```

---

## FILE: `paper/sections/appendix_registrations.tex`

```latex
% =====================================================================
% Appendix: the frozen preregistration documents, reproduced.
%
% GENERATED -- do not hand-edit. Regenerate with the session script
% gen_registrations.py and re-check with verify_registrations.py, which
% diffs the word stream of this file against the four frozen sources.
%
% Sources are FROZEN and are read READ-ONLY:
%   PREREGISTRATION.md
%   docs/MINIGRID_REGISTRATION_2026-07-15.md
%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md
%   docs/AUDIT_REGISTRATION_2026-07-15.md
%
% Faithfulness: markdown structure becomes LaTeX structure and inline
% markup becomes LaTeX inline markup. No word is added, dropped or
% reordered; the verifier proves that. Verbatim environments were
% rejected because PREREGISTRATION.md has unwrapped lines up to 967
% characters, which would be clipped at the page edge.
%
% This appendix is IDENTICAL in the arXiv and TMLR builds: reproducing
% the text rather than linking it is what keeps the frozen rules
% readable under double-blind review.
% =====================================================================

\section{Preregistration documents}  % NON-SOURCE
\label{app:registrations}  % NON-SOURCE

\label{app:reg:note}  % NON-SOURCE
% NON-SOURCE-BLOCK-BEGIN
This appendix reproduces the four frozen protocol documents that
\S\ref{sec:prereg} describes, so that the rule text can be read without
leaving the paper. Each is reproduced in full, including its dated
amendments. Formatting is typeset rather than plain-text, but no wording
has been changed: the conversion is generated and machine-checked
word-for-word against the frozen files. The authoritative copies are the
files themselves in the archived source package
(\S\ref{sec:artifacts}).
% NON-SOURCE-BLOCK-END

\subsection{FlipEval Main-Grid Pre-Registration}
\label{app:reg:main}  % NON-SOURCE
\emph{Reproduced from \texttt{PREREGISTRATION.md}; see \S\ref{app:reg:note}.}  % NON-SOURCE

Changelog: 2026-07-11 --- resolved all TBDs and tightened the H3 decision rules prior to any main-grid execution; frozen by the commit containing this line.

Created: 2026-07-10. Status: locked before the first main-grid job.

After the first main-grid job starts, this file will not be edited. Any deviation or clarification will be appended under \textbf{Dated Amendments}, with its date, rationale, and whether results were inspected before the decision.

\subsubsection{Claims}
\begin{itemize}
\item \textbf{H1 (net vs gross):} aggregate accuracy delta measures NET change and can be near zero because harmful and beneficial flips cancel, while GROSS behavioral churn on the same inputs stays large. Different quantities; report both.
\item \textbf{H2 (underpowered, unstable ranking):} at common benchmark sizes, power to detect degradation and to order methods is low; rankings shift under resampling, seed, and calibration data.
\item \textbf{H3 (calibration-seed instability, the ``spike''):} the calibration set used to fit the quantizer may change the method ranking as much as or more than the choice of method. If true, current single-run compression comparisons are effectively not reproducible. THIS is the potential main-track-caliber finding and the thing to hunt hardest in the pilot.
\end{itemize}
\subsubsection{Experimental Grid}
Models:

\begin{itemize}
\item Qwen2.5-1.5B-Instruct
\item Qwen2.5-7B-Instruct
\item Llama-3.2-3B-Instruct
\item Llama-3.1-8B-Instruct
\end{itemize}
Llama-3.2-3B-Instruct is used rather than the 1B model because near-floor GSM8K accuracy at 1B would make flip analysis degenerate and leave insufficient performance headroom across the four benchmarks.

Compression cells:

\begin{itemize}
\item RTN at 4 and 3 bits; seed-free control
\item GPTQ at 4 and 3 bits; calibration seeds \texttt{\{0, 1, 2, 3, 4\}} per model/bit cell
\item AWQ at 4 and 3 bits; calibration seeds \texttt{\{0, 1, 2, 3, 4\}} per model/bit cell
\item Wanda at 2:4 sparsity; calibration seeds \texttt{\{0, 1, 2, 3, 4\}}. Wanda is selected for its lower checkpoint-construction cost, documented implementation, and calibration dependence. SparseGPT is an explicitly out-of-scope pruning alternative.
\item Calibration datasets: C4 for the full grid; C4 and WikiText-2 on Qwen2.5-1.5B-Instruct to separate sample-seed variance from calibration-distribution variance
\end{itemize}
For the full-grid C4 condition, each calibration set contains 128 samples of exactly 2,048 tokens from \texttt{allenai/\allowbreak{}c4}, configuration \texttt{en}, train split. For seed \texttt{s}, shuffle the complete C4 train-split document-index array using \texttt{numpy.random.default\_rng(s).shuffle}; visit documents in that order, tokenize each document without adding special tokens, skip documents shorter than 2,048 tokens, and retain the first 2,048 tokens from each eligible document until 128 samples have been collected. Persist the selected document indices and token hashes. GPTQ seed \texttt{s} and AWQ seed \texttt{s} receive the identical ordered calibration samples. This pairing makes a seed-\texttt{s} ranking difference attributable to method-by-calibration interaction rather than the methods seeing different data. The Qwen2.5-1.5B-Instruct WikiText-2 distribution analysis will use the same seeds, sample count, token length, eligibility rule, and method pairing, with dataset-specific indices retained.

Benchmarks:

\begin{itemize}
\item MMLU
\item ARC-Challenge
\item HellaSwag, using the first 2,000 validation items in dataset index order (indices 0 through 1,999)
\item GSM8K, at least 1,000 fixed test items
\end{itemize}
The model-family chat template is ON for every benchmark and method, including the FP16 baseline. GSM8K few-shot examples are inline within the user message. All paired methods receive identical item sets, prompt construction, and decoding/scoring settings.

\subsubsection{Outcomes and Analysis}
Primary per-pair metrics are net accuracy delta \texttt{(c-\allowbreak{}b)/\allowbreak{}n}, harmful flip rate \texttt{b/\allowbreak{}n}, beneficial flip rate \texttt{c/\allowbreak{}n}, accuracy-state churn \texttt{(b+c)/\allowbreak{}n}, wrong-to-different-wrong churn, and total answer churn. The primary inferential outputs are bootstrap 95\% confidence intervals, exact McNemar tests, TOST equivalence, minimum detectable difference at 80\% power, required n at 80\% power for the observed effect, and item-bootstrap rank-flip rates.

The TOST equivalence margin is fixed at \textbf{2 percentage points} (\texttt{0.02}) for accuracy delta. We will not interpret failure to reject a difference as equivalence. McNemar tests are two-sided and exact. Bootstrap seeds, item IDs, calibration sample indices, and environment fingerprints will be retained. Family-wise multiple comparisons will use Holm correction within each benchmark/model family of planned method contrasts.

\paragraph{Hierarchical aggregation across calibration seeds}
\mbox{}\\
Calibration seeds are treated as a random effect. Item-level bootstrap intervals from a single seed do not represent between-seed uncertainty. For every model/benchmark/bit/method cell, we will report (1) item-bootstrap uncertainty separately within each seed, (2) the standard deviation of the five seed-level accuracy estimates, and (3) a two-level paired bootstrap interval. Each replicate of the two-level bootstrap samples the five seed labels with replacement and, within every selected seed, samples the common evaluation items with replacement; GPTQ and AWQ retain the same sampled seed labels and item indices. We will report seed-level SD and item-level SE as separate variance components rather than collapsing them into an item-only interval.

FlipEval's rank-instability metric will be reported both within each seed using item resampling, for comparison with the pilot, and across the paired seed-by-item joint bootstrap, which is the H3-relevant estimate. The joint procedure uses the same two-level resamples described above and reports exact-tie replicates separately.

\subsubsection{H3 Decision Rule}
The primary confirmatory analysis is restricted to 4-bit GPTQ and AWQ over the fixed set

\texttt{S = \{Qwen2.5-\allowbreak{}1.5B-\allowbreak{}Instruct, Qwen2.5-\allowbreak{}7B-\allowbreak{}Instruct, Llama-\allowbreak{}3.2-\allowbreak{}3B-\allowbreak{}Instruct, Llama-\allowbreak{}3.1-\allowbreak{}8B-\allowbreak{}Instruct\} $\times$ \{MMLU, GSM8K\}},

which contains eight model-by-benchmark cells. MMLU is the registered likelihood-based benchmark and GSM8K the registered generative benchmark in the confirmatory set. ARC-Challenge and HellaSwag are secondary. The identical H3 analyses at 3 bits are pre-declared secondary/exploratory analyses and will be reported regardless of outcome. Four-bit results are primary because 4-bit quantization is the deployment-relevant setting; 3-bit instability is expected to be larger and is interpreted only as a dose-response check, not as a second opportunity for confirmatory significance.

For seed \texttt{s}, GPTQ-\texttt{s} is compared with AWQ-\texttt{s} using the paired calibration set. Let

\texttt{d\_s(model, benchmark, bit) = acc\_GPTQ,s -\allowbreak{} acc\_AWQ,s}.

A winner flip occurs in a cell if there are registered seeds \texttt{s} and \texttt{t} for which \texttt{sign(d\_s) != sign(d\_t)} and both differences are nonzero. An exact accuracy tie (\texttt{d\_s = 0}), which can occur because item counts are discrete, is counted as neither a flip nor a non-flip and is reported separately. Thus a tie cannot create or erase a flip between two non-tied seeds.

Define the absolute mean method gap as

\texttt{gap(model, benchmark, bit) = |mean\_s(acc\_GPTQ,s) -\allowbreak{} mean\_s(acc\_AWQ,s)|},

and, for method \texttt{m} in \texttt{\{GPTQ, AWQ\}}, define the seed-induced range as

\texttt{range\_m(model, benchmark, bit) = max\_s(acc\_m,s) -\allowbreak{} min\_s(acc\_m,s)}.

The range/gap criterion holds in a cell exactly when

\texttt{max(range\_GPTQ, range\_AWQ) >= gap}.

\textbf{Supported:} H3 is supported if winner flips occur in at least 3 of the 8 confirmatory cells, or the range/gap criterion holds in at least 4 of the 8 confirmatory cells.

\textbf{Disconfirmed:} H3 is disconfirmed if winner flips occur in at most 1 of the 8 confirmatory cells and \texttt{max(range\_GPTQ, range\_AWQ) < 0.5 $\times$ gap} in at least 6 of the 8 confirmatory cells.

\textbf{Inconclusive:} Every outcome satisfying neither the support rule nor the disconfirmation rule is reported as inconclusive, without post-hoc promotion. Calibration-dataset effects, 3-bit results, ARC-Challenge, and HellaSwag are reported separately and cannot substitute for the eight-cell confirmatory rule.

H1 and H2 will be reported as estimated effects with confidence intervals rather than converted into new post-hoc binary thresholds. The preregistered pilot-motivated diagnostics are cancellation (\texttt{harmful} and \texttt{beneficial} both nonzero relative to net delta), required-n relative to benchmark size, and bootstrap method-rank flips.

\subsubsection{Exclusions and Missing Runs}
An item is excluded only for a benchmark loader/scorer failure that affects all compared methods; exclusions and reasons are logged before analysis. Failed checkpoint builds or jobs are rerun with the same registered seed and calibration indices. Backend changes create a new environment cell and do not silently replace prior results.

\subsubsection{Dated Amendments}
\paragraph{2026-07-20 --- WikiText-2 document definition (Decision Point A)}
\mbox{}\\
\textbf{Decision owner:} \authorname{}, alone.

\textbf{Results inspected before this decision:} No main-grid or mini-grid accuracy result has been inspected, and none exists. The only evidence seen is calibration-eligibility data, recorded below.

The 2026-07-13 calibration preflight failure recorded in \texttt{docs/\allowbreak{}WIKITEXT2\_PROTOCOL\_BLOCKER.md}: on \texttt{Salesforce/\allowbreak{}wikitext}, \texttt{wikitext-\allowbreak{}2-\allowbreak{}raw-\allowbreak{}v1}, train split, dataset revision \texttt{b08601e04326c79dfdd32d625aee71d232d685c3}, tokenized with \texttt{Qwen/\allowbreak{}Qwen2.5-\allowbreak{}1.5B-\allowbreak{}Instruct} revision \texttt{989aa7980e4cf806f80c7fef2b1adb7bc71aa306} under the pinned runtime (torch 2.13.0, transformers 5.13.0, datasets 5.0.0), seed 0, no added special tokens: \textbf{0 of 36,718 rows contain at least 2,048 tokens}, against a registered requirement of 128. No calibration artifact or checkpoint was produced. This is a property of the corpus layout, not of the seed --- WikiText-2 raw distributes each article across many short rows --- so no reseeding can make the registered row-level reading executable.

The 2026-07-20 eligibility probe, run \textbf{before} this decision was taken, on the same pinned dataset revision, tokenizer revision, and runtime, applying the reconstruction rule below verbatim (SLURM job \texttt{11303825}, embers CPU, in-image; algorithm \texttt{wikitext2-\allowbreak{}level1-\allowbreak{}heading-\allowbreak{}articles-\allowbreak{}v1}): \textbf{629 articles reconstructed from 36,718 rows, of which 425 contain at least 2,048 tokens} against the registered requirement of 128 --- verdict SUFFICIENT, a 3.3$\times$ pool. Token-length distribution across the 629 reconstructed articles: min 10, p25 1,703, median 2,857, p75 5,320, p90 8,577, max 21,295, mean 4,002.0; 2,517,232 tokens total. Eligibility is a property of the articles and not of the seed, so this single count satisfies all five registered seeds. The probe script is persisted at \texttt{scripts/\allowbreak{}wikitext2\_article\_probe.py} and is the \textbf{reference implementation} of the reconstruction rule: the builder's reconstruction must match its \texttt{reconstruct\_articles} and \texttt{is\_level1\_heading} functions verbatim.

\textbf{Rationale:} The preregistration requires the WikiText-2 condition to sample 128 \emph{documents} of 2,048 tokens. It did not operationalize ``document'' for a corpus whose Hugging Face rows are line fragments rather than documents. This amendment supplies that definition. It changes no other registered parameter.

\textbf{Amended rule.} For the Qwen2.5-1.5B-Instruct WikiText-2 calibration condition, a \emph{document} is one article, reconstructed deterministically from the raw corpus as follows:

\begin{enumerate}
\item Read the train split in source row order at the pinned dataset revision.
\item An article begins at each row that is a level-1 heading --- a row whose text, after stripping surrounding whitespace, matches a single \texttt{=}-delimited title (\texttt{= Title =}) and not a deeper heading (\texttt{= = Subtitle = =} or lower). All rows up to but excluding the next level-1 heading belong to that article. Rows preceding the first level-1 heading form no article and are discarded.
\item An article's text is its member rows concatenated in source order, joined exactly as stored, with no normalization beyond that already present in the raw corpus.
\item The reconstruction algorithm is versioned and persisted with the artifact, together with the ordered article index array and a hash of each reconstructed article, so the reconstruction is independently checkable.
\end{enumerate}
The registered sampling rule then applies unchanged to that article array: for seed \texttt{s}, shuffle the complete reconstructed-article index array using \texttt{numpy.random.default\_rng(s).shuffle}; visit articles in that order; tokenize each without adding special tokens; skip articles shorter than 2,048 tokens; retain the first 2,048 tokens from each eligible article until 128 samples are collected. Persist the selected article indices and token hashes. GPTQ seed \texttt{s} and AWQ seed \texttt{s} receive the identical ordered calibration samples, as for C4.

Seeds \texttt{\{0,1,2,3,4\}}, sample count 128, token length 2,048, the eligibility threshold, method pairing, and index retention are \textbf{unchanged} from the frozen protocol.

\textbf{Fail-closed condition.} The builder continues to fail closed on the WikiText-2 condition until this rule is implemented and tested. If the reconstruction yields fewer than 128 eligible articles for any seed, the builder must raise rather than relax any registered parameter, and the shortfall returns here as a new dated amendment.


\subsection{Mini-Grid Registration: Scope, Escalation Rule, and Reporting}
\label{app:reg:minigrid}  % NON-SOURCE
\emph{Reproduced from \texttt{docs/\allowbreak{}MINIGRID\_REGISTRATION\_2026-\allowbreak{}07-\allowbreak{}15.md}; see \S\ref{app:reg:note}.}  % NON-SOURCE

Status: \textbf{FROZEN 2026-07-15}, by the commit containing this line, before any mini-grid job exists and before any mini-grid accuracy result was inspected. Deviations require a dated entry under Dated Amendments stating whether results were inspected before the decision.

This document does not amend \texttt{PREREGISTRATION.md} (frozen 2026-07-11). It constrains the experimenter for a staged subset of the registered grid. The registered H3 protocol, metrics, and decision rule are unchanged.

\subsubsection{1. Scope}
The mini-grid executes exactly 4 of the 8 registered confirmatory H3 cells:

\texttt{\{Qwen2.5-\allowbreak{}1.5B-\allowbreak{}Instruct, Llama-\allowbreak{}3.2-\allowbreak{}3B-\allowbreak{}Instruct\} $\times$ \{MMLU, GSM8K\}}

at 4-bit, GPTQ and AWQ, calibration seeds \{0,1,2,3,4\}, paired C4 calibration sets per the registered sampling algorithm. Pinned model, dataset, and benchmark revisions are those in \texttt{configs/\allowbreak{}main\_grid\_manifest.yaml}. The 7B/8B cells (Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct $\times$ MMLU, GSM8K) are deferred and executed only if the escalation rule in \S{}3 fires.

\subsubsection{2. Benchmark execution parameters not fixed by the preregistration}
\begin{itemize}
\item GSM8K few-shot count for all mini-grid (and any later confirmatory) cells: \textbf{1 few-shot example, inline in the user message --- matching the validated bridge configuration \texttt{configs/\allowbreak{}pace\_bridge\_chat.yaml}}.
\item GSM8K items: test indices 0--999 in dataset order. MMLU: full test split.
\item Chat template ON for every method including FP16 baselines (registered).
\item Llama-3.2-3B FP16 operational acceptance ranges: to be derived from a trusted lm-evaluation-harness reference run on the pinned snapshot (procedure of \texttt{docs/\allowbreak{}MMLU\_REFERENCE\_RUN.md}) and committed into the mini-grid config \textbf{before any quantized Llama-3.2-3B result exists}. This registration deliberately freezes the derivation procedure, not the values; the values are recorded in the mini-grid config commit and are operational gates only.
\end{itemize}
\subsubsection{3. Escalation rule (mechanical, pre-committed)}
Compute, per the frozen algebra of \texttt{PREREGISTRATION.md}, for each of the 4 cells at 4-bit: winner flips across seeds (ties counted separately, per the registered tie rule) and the range/gap criterion \texttt{max(range\_GPTQ, range\_AWQ) >= gap}.

\textbf{Escalate} to the deferred 7B/8B seed cells iff:

\begin{itemize}
\item winner flips occur in \textbf{at least 1 of the 4 cells}, OR
\item the range/gap criterion holds in \textbf{at least 2 of the 4 cells}.
\end{itemize}
If neither condition holds, the 7B/8B cells are not built, and no other result (3-bit, other benchmarks, atlas findings) can substitute to trigger escalation.

\subsubsection{4. Relation to the frozen H3 decision rule}
The registered Supported/Disconfirmed/Inconclusive rule is defined over all 8 confirmatory cells. Therefore:

\begin{enumerate}
\item If escalation fires and all 8 cells complete, the frozen rule is applied exactly as registered.
\item If escalation does not fire (or the 7B/8B cells are otherwise not run), the paper reports the 4 completed cells \textbf{descriptively}, and H3 is reported as \textbf{formally inconclusive under the registered rule} --- never as supported or disconfirmed on 4 cells. No reduced-cell variant of the rule will be constructed after results are seen.
\item The registered secondary analyses (3-bit dose-response, ARC-Challenge, HellaSwag, WikiText-2 calibration-distribution contrast) remain deferred with the rest of the main grid and are not part of the mini-grid.
\end{enumerate}
\subsubsection{5. Analysis and inspection discipline}
\begin{itemize}
\item During fan-out, only job health, checksums, expected-file coverage, and receipt pairing are inspected (runbook grid discipline). First accuracy inspection happens only after the mini-grid validator passes over the complete 44-JSONL expected set.
\item The registered hierarchical analysis (\texttt{flipeval paired-\allowbreak{}seeds}, 2000 replicates, bootstrap seed 0) is run once per cell; the escalation rule in \S{}3 is then applied mechanically and a dated escalation decision record is written the same day.
\item The paired-bootstrap rank-flip denominator convention (tie replicates included in the denominator, ties also reported separately) is the one implemented and documented in \texttt{flipeval/\allowbreak{}core.py} as of commit \texttt{a8ba9f0}; it is hereby fixed in words and will not be re-chosen after inspection.
\end{itemize}
\subsubsection{Dated Amendments}
\paragraph{Amendment 2 (2026-07-21, \authorname{}): GSM8K few-shot binding}
\mbox{}\\
\S{}2 states GSM8K uses ``1 few-shot example, inline in the user message --- matching the validated bridge configuration.'' These two clauses conflict: the validated bridge configuration (\texttt{configs/\allowbreak{}pace\_bridge\_chat.yaml}, \texttt{fewshot: 1}) is implemented in \texttt{pilot\_eval/\allowbreak{}tasks.py} as a boolean switch that emits the fixed 3-example \texttt{GSM8K\_FEWSHOT} block, so the bridge canary that passed was validated with 3 inline examples. The operative binding for the mini-grid is the validated bridge configuration: 3 inline few-shot examples, byte-identical prompt path to the bridge. The literal count ``1'' in \S{}2 was a drafting error. The config key \texttt{fewshot} retains its existing boolean semantics (truthy $\Rightarrow$ the fixed 3-example block; the integer is not a count).

Results-blind status: no mini-grid accuracy results exist or have been inspected as of this amendment; the bridge canary results that were inspected are operational validation runs outside the mini-grid's confirmatory set.


\subsection{Public Per-Item Atlas Mining Registration}
\label{app:reg:atlas}  % NON-SOURCE
\emph{Reproduced from \texttt{docs/\allowbreak{}ATLAS\_MINING\_REGISTRATION\_2026-\allowbreak{}07-\allowbreak{}15.md}; see \S\ref{app:reg:note}.}  % NON-SOURCE

Status: \textbf{FROZEN 2026-07-15}, by the commit containing this line --- before any flip statistic from these sources was computed beyond the two feasibility probes disclosed in \S{}1. Deviations require a dated entry under Dated Amendments stating whether results were inspected before the decision.

Purpose: extend the Compression Flip Atlas with paired per-item records mined from public evaluation dumps, at zero GPU cost. These analyses are \textbf{descriptive/exploratory}: they estimate flip and churn magnitudes in the wild and feed the certification tables. They test no registered hypothesis and cannot substitute for any H3 cell. This protocol is registered to prevent source- or pair-selection after seeing results.

\subsubsection{1. Disclosure of pre-registration data contact}
Two feasibility probes were run on 2026-07-15 before this draft was written, and their results are known: (a) TheBloke/Llama-2-7B-GPTQ vs meta-llama/Llama-2-7b-hf on ARC-Challenge (74/1,170 flips, net $-$1.03 pp), and (b) neuralmagic Llama-3.1-8B baseline vs W4A16 on bbh\_boolean\_expressions (17/250 flips, net +1.2 pp). These two cells are flagged \texttt{probe=true} in the atlas and excluded from any aggregate statistic quoted in the paper's abstract or headline claims.

\subsubsection{2. Sources (fixed; no additions after freeze without a dated amendment)}
\begin{itemize}
\item \textbf{S1 --- Open LLM Leaderboard v1 archive} (\texttt{open-\allowbreak{}llm-\allowbreak{}leaderboard-\allowbreak{}old} details datasets; public, ungated; no declared license --- recorded as a limitation in the datasheet).
\item \textbf{S2 --- Neural Magic/Red Hat per-item dumps}: \texttt{neuralmagic/\allowbreak{} quantized-\allowbreak{}llama-\allowbreak{}3.1-\allowbreak{}leaderboard-\allowbreak{}v2-\allowbreak{}evals} (Apache-2.0) and, if their per-item schema validates, the companion arena-hard and humaneval datasets.
\end{itemize}
\subsubsection{3. Pair enumeration rule (run BEFORE any flip computation)}
\begin{enumerate}
\item Enumerate all S1 details datasets whose model name matches, case-insensitive, any of: \texttt{GPTQ}, \texttt{AWQ}, \texttt{GGUF}, \texttt{8bit}, \texttt{4bit}, \texttt{bnb}. For each, identify the base model from the quantizer's model card; include the pair iff a details dataset exists for that exact base model.
\item Within a pair, use the latest run timestamp per task for each side unless prompt-hash agreement (rule \S{}4.2) fails, in which case try earlier run combinations in reverse-chronological order and record the choice.
\item S2 pairs are the nine baseline$\times$\{W4A16, W8A8-INT8, W8A8-FP8\} combinations at 8B/70B/405B, all tasks present in the dump.
\item The frozen pair list (a machine-readable manifest with dataset URLs, run timestamps, and task lists) is committed as \texttt{docs/\allowbreak{}atlas\_pair\_manifest.json} \textbf{before} flip statistics are computed. Pairs discovered later require a dated amendment here.
\end{enumerate}
\subsubsection{4. Item pairing validity rules (mechanical)}
\begin{enumerate}
\item Join key: S1 \texttt{hashes.example}; S2 \texttt{doc\_id} with byte-identical \texttt{doc} (or \texttt{doc\_hash} where present). Duplicated join keys within a file are dropped entirely (both occurrences) and counted.
\item An item enters the paired analysis iff its full-prompt hash (S1 \texttt{hashes.full\_prompt}; S2 \texttt{prompt\_hash}) is identical across the pair. A pair-task cell is \textbf{excluded} iff fewer than \textbf{99\%} of joinable items pass this identity check; exclusions are reported with their rates.
\item Per cell, record both sides' harness identity (lighteval/lm-eval git SHA, model args, dtype) verbatim from the results JSON. Differing harness SHAs do not exclude a cell (prompt-hash identity is the operative control) but are recorded and disclosed per cell.
\end{enumerate}
\subsubsection{5. Metrics (identical to the controlled-atlas suite)}
Per cell: net accuracy delta, harmful/beneficial flip rates, accuracy-state churn, total answer churn where raw predictions exist, exact two-sided McNemar, TOST at the registered 2 pp margin, minimum detectable difference at 80\% power, and required-n. Primary correctness column: \texttt{acc\_norm} where present, else \texttt{acc} (S1); the task's primary metric as logged (S2); the choice is recorded per cell. No cell-level results drive inclusion/exclusion decisions.

\subsubsection{6. Reporting}
All enumerated, non-excluded cells are reported in the atlas regardless of outcome. Aggregates over cells are accompanied by the cell count and the exclusion table. The \texttt{probe=true} cells of \S{}1 appear in the atlas but not in headline aggregates.

\subsubsection{Dated Amendments}
None.


\subsection{Published-Claim Audit Registration}
\label{app:reg:audit}  % NON-SOURCE
\emph{Reproduced from \texttt{docs/\allowbreak{}AUDIT\_REGISTRATION\_2026-\allowbreak{}07-\allowbreak{}15.md}; see \S\ref{app:reg:note}.}  % NON-SOURCE

Status: \textbf{FROZEN 2026-07-15}, by the commit containing this line --- before any per-claim power computation was run. The claim list itself must also be frozen (\S{}3.4) before verdicts are computed. Deviations require a dated entry under Dated Amendments stating whether results were inspected before the decision.

Purpose: systematically assess whether published ``near-lossless'' compression claims are statistically supported at their reported evaluation sizes. Framing is constructive --- the field lacks reporting standards; flipeval and the certification tables are the proposed fix --- not an indictment of specific papers. Every verdict is mechanical and recomputable.

\subsubsection{1. Disclosure of pre-registration data contact}
Five candidate claims were collected with exact quotes on 2026-07-15 (GPTQ, LLM.int8(), SmoothQuant abstracts; the RedHatAI W4A16 Llama-3.1-8B model card; Meta's quantized Llama 3.2 blog) during a feasibility sweep. No power computation has been run on any of them. They enter the pool through the same \S{}3 criteria as later-collected claims.

\subsubsection{2. Population and sampling frame (fixed)}
Claim sources, enumerated exhaustively within each frame:

\begin{itemize}
\item \textbf{F1 --- Method papers:} the published versions of GPTQ, AWQ, SmoothQuant, LLM.int8(), SpinQuant, QuIP\#, SqueezeLLM, Wanda, and SparseGPT, plus any paper citing one of these that appears in the related-work sweep (\texttt{docs/\allowbreak{}related\_work\_checklist.md}) and makes an equivalence-type claim.
\item \textbf{F2 --- Official quantized model cards:} Meta, Qwen, Mistral, and Red Hat AI/Neural Magic quantized releases of models in the Llama-2/3.x and Qwen2.5 families on Hugging Face.
\item \textbf{F3 --- Inference-stack vendor posts:} vLLM, TensorRT-LLM, and llama.cpp official blog/docs pages making quantization-quality claims.
\end{itemize}
Target: \textbf{at least 10} claims; all claims meeting \S{}3 inclusion are audited (no discretionary sub-selection).

\subsubsection{3. Claim inclusion and extraction (mechanical)}
\begin{enumerate}
\item \textbf{Inclusion:} the source asserts, in prose or a table caption, that a compressed model's benchmark quality is equivalent-or-negligibly-different from its uncompressed baseline (trigger vocabulary: ``near-lossless'', ``negligible'', ``no (significant) degradation'', ``matches'', ``preserves accuracy'', ``X\% recovery'' with X $\geq$ 98, or an explicit $\leq$1 pp delta framed as parity). Perplexity-only claims are included only if a benchmark-accuracy claim also appears.
\item \textbf{Extraction fields (per claim):} exact quote ($\leq$15 words), source and version/date, benchmark(s), reported n per benchmark (as stated, else the benchmark's standard size, recorded as \texttt{imputed}), reported baseline accuracy, reported delta, whether per-item outputs are released, whether any statistical test or interval is reported.
\item \textbf{Double extraction:} each claim's fields are extracted twice on different days (solo-author substitute for dual coding) and discrepancies resolved before the verdict stage.
\item \textbf{Freeze:} the completed claim table is committed as \texttt{docs/\allowbreak{}audit\_claim\_table.csv} before any verdict is computed. Claims found after that commit go into a separately reported ``post-freeze'' stratum.
\end{enumerate}
\subsubsection{4. Verdict rules (mechanical, computed only after \S{}3.4 freeze)}
For each claim $\times$ benchmark, at the claim's reported n and baseline accuracy:

\begin{itemize}
\item \textbf{V1 --- Detection power:} minimum detectable accuracy delta at 80\% power, two-sided $\alpha$=0.05, under the paired-flip model with the discordance rate imputed from the atlas's empirical flip-rate distribution for the nearest (method family, bit width, benchmark) cell --- sensitivity-checked against the independent-binomial bound. Report MDD/claimed-margin ratio.
\item \textbf{V2 --- Equivalence support:} the n required for TOST at margin \textbf{2 pp} --- matching the registered main-grid TOST margin --- (and at the claim's own margin when it states one). A claim is labeled \textbf{``underpowered for its own assertion''} iff reported n < required n at the applicable margin.
\item \textbf{V3 --- Reproducibility:} binary --- could a third party run a paired test from released artifacts (per-item outputs public)?
\end{itemize}
Headline statistic: the fraction of audited claims labeled underpowered under V2, reported with its count and the full claim table. No claim is described as ``false'' or ``wrong''; the audited property is the evidential sufficiency of the reported evaluation, not the truth of the underlying equivalence.

\subsubsection{5. Robustness reporting}
Verdicts are recomputed under (a) the independent-binomial bound instead of the atlas-imputed discordance rate and (b) a margin sweep over 1 pp and 3 pp; a claim's verdict is called margin-sensitive if it changes across the sweep, and the count of margin-sensitive verdicts accompanies the headline number.

\subsubsection{Dated Amendments}
\textbf{2026-07-15 --- Amendment 1 (\S{}3.3 independence mechanism).} The requirement that the two extractions occur ``on different days'' is replaced by an extractor-independence requirement: the second extraction is performed in a fresh agent session with \textbf{no access to pass-1 outputs} --- the extractor is withheld \texttt{docs/\allowbreak{}audit\_claim\_table\_pass1.csv}, instructed not to read it or retrieve it from git history, and receives only the frozen protocol and the source frames. Rationale: temporal separation was a proxy for extractor independence calibrated to human memory; a fresh agent session carries no memory of pass 1, so blind same-day extraction provides at least the intended independence; the source-stability benefit of a second-day fetch is instead obtained by recording source content hashes in both passes where feasible. Decision context: made after pass-1 extraction results were known, but before any verdict, power, MDD, or required-n computation was run; the \S{}4 verdict rules and the \S{}3.1--3.2 inclusion/extraction rules are unchanged.

\textbf{2026-07-31 --- Amendment 2 (\S{}4 V2, the applicable margin).}

\emph{Defect.} \S{}4 V2 computes the required \$n\$ ``at margin 2 pp \dots{} (and at the claim's own margin when it states one)''. The phrase ``when it states one'' was never operationalised in this registration, and \S{}3.2 does not extract a margin: the frozen claim table \texttt{docs/\allowbreak{}audit\_claim\_table.csv} has no margin field. The implementation in \texttt{scripts/\allowbreak{}audit\_verdicts.py} supplied one after the freeze, by taking the largest delta the source reports and treating it as the margin the source states. Those are different quantities. A reported delta is an outcome of the evaluation; a margin is a threshold against which an outcome is judged. Every \texttt{margin\_basis} value in \texttt{results/\allowbreak{}audit\_verdicts\_rev2.csv} cites an observed quantity --- for example ``max |delta| over the 5 OPT-175B tasks'' (R01), ``the larger of the two stated deltas'' (R06), ``+0.15pp (68.69 vs 68.54)'' (R17). Verdicts labelled ``underpowered for its own assertion'' therefore rest, for those claims, on a margin the source did not assert.

\emph{Amendment.} The applicable margin is determined by the following rule, which replaces the parenthetical in \S{}4 V2. Each audited claim is assigned to exactly one category:

\begin{enumerate}
\item \textbf{Formal equivalence claim} --- the source states a numeric tolerance that is logically prior to the observed result: a threshold that could have been written down before the evaluation was run. Qualifying forms include ``within \$X\$'', ``no more than \$X\$'', ``at most \$X\$'' used as a requirement, ``a tolerance of \$X\$'', and equivalent constructions that bound what the source would accept.
\item \textbf{Informal near-lossless claim} --- the source reports a result and characterises it as negligible, but states no threshold prior to it. This includes deltas subsequently described as small, recovery percentages computed from the result, and phrases such as ``at most \$X\$'' used to describe the spread of observed differences rather than to set a bound.
\item \textbf{Unquantified claim} --- the source uses equivalence language without sufficient numerical information to evaluate either way. This category does not change; it continues to be handled by the \S{}4 indeterminacy rules.
\end{enumerate}
The determination is made against the frozen \texttt{exact\_quote} for each claim and, where the quote alone is inconclusive, against the source at the version and content hash recorded in the frozen claim table. It is recorded per claim, with the quoted text supporting it, in a new column of the verdicts CSV. \textbf{No claim is re-extracted and no source is re-fetched for extraction purposes}; the frozen claim table is unchanged. Sources were re-fetched for verification only, under the eligibility-and-provenance scope recorded below.

Verdicts are then computed as follows:

\begin{itemize}
\item The \textbf{primary verdict for every claim} is at the registered 2 pp margin, which \S{}4 already names first. The headline count is the number of determinate claims underpowered at 2 pp.
\item A claim in category 1 is \textbf{additionally} evaluated at its declared margin, reported alongside the primary verdict, and never in place of it.
\item Claims in category 2 are reported against the registered 1 pp / 2 pp / 3 pp sweep of \S{}5. \textbf{No margin derived from a claim's own reported results is described as that claim's stated, declared, asserted or own margin}, in the paper or in any released artifact.
\end{itemize}
\emph{Consequential quantities.} Every reported quantity that divides by the applicable margin is recomputed with it and re-reported: the V1 MDD-to-claimed-margin ratios, the required-\$n\$-to-reported-\$n\$ shortfall ratios, and the \S{}5 margin-sensitivity flag. Values previously reported against a result-derived margin are withdrawn, not silently updated; both the superseded and the corrected values remain in the released artifacts.

\emph{Analysis discipline.} The recomputation is run \textbf{once}, over the frozen claim table, and whatever it returns is reported --- including if the headline count falls, rises, or reaches zero. No variant of this rule is constructed after the recomputed values are seen.

\emph{Eligibility correction (R10).} A full-text review of every source, run 2026-07-31 and recorded in \texttt{docs/\allowbreak{}AUDIT\_SOURCE\_VERIFICATION\_2026-\allowbreak{}07-\allowbreak{}31.md}, established that R10's recorded \texttt{exact\_quote} --- ``average recovery percentage across all benchmarks is 98.6\%'' --- appears nowhere in its source. The card contains no prose equivalence claim; \texttt{98.6\%} is a table cell, and the extraction composed a sentence from tabular data and recorded it as a quotation. \S{}3.1 requires the assertion to appear ``in prose or a table caption'', and it appears in neither. \textbf{R10 is therefore excluded from the eligible population by applying the inclusion rule already registered in \S{}3.1, not by any new criterion.} The eligible population becomes 16. The frozen claim table is not edited; the exclusion is recorded in the verdicts CSV with the verification finding beside it, and the original row remains in the immutable frozen file and in the published v1.0.0 artifact.

This correction moves the eligible denominator. It changes neither the number of claims below the planning threshold nor the V3 per-item-outputs result: R10 was adequately powered at the registered 2 pp margin and recorded \texttt{no} on V3, so its removal cannot reduce the count of flagged claims. \textbf{The correction did not improve any count in the direction favourable to the audit's thesis.}

\emph{Scope.} This amendment changes the applicable margin, and reopens \S{}\S{}3.1--3.2 \textbf{only} to correct eligibility and provenance --- that is, to apply the existing inclusion rule to R10 and to record source provenance. No inclusion criterion is added, widened or narrowed, no claim is re-extracted, and no source is re-fetched for extraction purposes. Unchanged and not reopened: the frozen claim table itself; the \S{}4 V1 detection-power formula; the \S{}4 V3 reproducibility verdict; the indeterminacy rules and the claims currently indeterminate; the discordance imputation and its tier matching; the atlas; and every registration other than this one.

\emph{Reporting the surviving power result.} The claim below the planning threshold at the registered 2 pp margin is reported as a \textbf{sensitivity-dependent planning flag, not a stable binary verdict}, and never without its reversal point. The required \$n\$ is a planning quantity computed under an assumed true difference of zero and a point imputation of discordance; for the single flagged claim the classification reverses at approximately \$d = 0.1189\$ against an imputed \$d = 0.13\$, and 43.6\% of the 792 atlas cells supplying that imputation fall below the reversal point. Any report of this flag states the imputed value, the reversal point, and that fraction.

\emph{Decision context.} \textbf{Results were inspected before this decision, and so was the full-text classification.} The audit verdicts were computed on 2026-07-20, revised to rev-2 on 2026-07-21, reported in the paper, and released in the v1.0.0 artifact; the headline \$K = 4\$ of 12 has been public since 2026-07-30. The full-text verification of all 17 sources was run on 2026-07-31, \textbf{before this amendment was signed and at the decision owner's direction}, and its classification of every claim --- including the finding that no source declares a margin --- was known at signature. The rule in this amendment was not constructed against that classification: it was written and committed on 2026-07-31 at \texttt{19d485c}, before the verification ran, and that committed draft names R14 as its hard case and resolves it by the same priority test the verification later applied. The rule is unchanged from that commit. The eligibility correction was made by applying \S{}3.1 as already registered, and is verdict-neutral in the sense recorded above. The original immutable version of every superseded value remains accessible in the frozen claim table and the published v1.0.0 artifact.

\emph{Signed.} \authorname{}, 2026-07-31. Drafted by Claude Code at \texttt{19d485c}, revised at \texttt{bb45528} after the full-text source verification, and appended on the verbatim instruction ``sign and append''. The rule in the \emph{Amendment} clause above is unchanged from \texttt{19d485c}.

\textbf{2026-08-03 --- Amendment 3 (\S{}3.1 inclusion, applied to R09 and R17).}

\emph{Occasion.} Amendment 2 excluded R10 from the eligible population by applying \S{}3.1 as registered: the recorded quotation appeared nowhere in the source, and the assertion appeared in neither prose nor a table caption. That correction rested on a full-text review which, as recorded in \texttt{docs/\allowbreak{}AUDIT\_SOURCE\_VERIFICATION\_2026-\allowbreak{}07-\allowbreak{}31.md}, verified quotation \emph{accuracy} for all seventeen sources but quotation \emph{location} for R10 alone. The remaining sixteen therefore carried an unexamined \S{}3.1 basis. An author re-verification of the four claims named in that document's open items, recorded in \texttt{docs/\allowbreak{}AUDIT\_SELF\_RECHECK\_2026-\allowbreak{}08-\allowbreak{}02.md}, examined location directly against the archived sources.

\emph{Finding.} Three of the six quantized-model cards in the population, R09, R10 and R17, contain no \S{}3.1 trigger vocabulary anywhere in their prose. In each, the recovery percentage that would satisfy the trigger list exists only as a table cell, beneath a column header, and none of the three files contains a table caption element of any kind. R08, R15 and R16 are unaffected: each states a recovery percentage in prose at or above the registered threshold of 98. With respect to those recovery figures R09 and R17 occupy the same structural position that excluded R10, which is what makes their eligibility a live question. They differ from R10 in another respect, addressed below.

\emph{Determination.} \textbf{R09 and R17 remain in the eligible population.} The ground for retaining them is that \S{}3.1 does not decide the case, not that it decides the case in their favour.

\S{}3.1 admits a claim on ``an explicit $\leq$1 pp delta framed as parity''. That trigger has two limbs, and R09 and R17 satisfy the first without satisfying the second. Each card contains exactly one comparative sentence in prose, and it states both the compressed and the uncompressed score: 73.44 against 73.79 for R09 and 68.69 against 68.54 for R17, differences of 0.35 pp and 0.15 pp. A delta below one percentage point is therefore explicit on the face of the prose. Neither sentence characterises that difference. ``Whereas'' is a neutral contrastive, no trigger term appears in the prose of either card, and the recovery figures that would qualify outright, 99.52\% and 99.8\%, exist only as table cells beneath a \texttt{<th>Recovery} header in files carrying no table caption element at all. The registration does not say what follows when a source supplies the quantity and withholds the characterisation. \textbf{That is a gap in a rule \S{}3 declares to be mechanical, and it was not anticipated when the protocol was frozen on 2026-07-15.}

\textbf{R10 is excluded on a ground that does not depend on how that gap is resolved.} Its card contains no comparative sentence of any kind: the strings ``whereas'', ``unquantized'', ``baseline'' and ``compared'' do not occur anywhere in it, its evaluation section is a single table with no accompanying prose, and the sentence recorded for it in the frozen claim table was composed from tabular data and appears nowhere in the source. R10 therefore fails the first limb as well as the second, and its exclusion under Amendment 2 stands under the strict and the permissive reading alike. The difference in outcome between R10 and these two rests on a difference between the documents, not on this determination. Verified against the sealed source archive \texttt{a912a1e7\dots{}40259} on 2026-08-03, by a route independent of the vocabulary sweep recorded in \texttt{docs/\allowbreak{}AUDIT\_SELF\_RECHECK\_2026-\allowbreak{}08-\allowbreak{}02.md} \S{}4.1.

Two resolutions of the gap were therefore available, and both are defensible. The strict reading requires both limbs and excludes R09 and R17. The permissive reading treats an explicit sub-point delta, stated in prose in a document whose function is to offer the compressed model in place of the uncompressed one, as an assertion of negligible difference in substance, and retains them. \textbf{The tie is broken against the interest of this audit.} The strict reading shrinks the eligible and assessable populations and raises the proportion of assessable claims falling below the planning threshold; the permissive reading leaves every published count exactly where it stands. Where a frozen rule is genuinely silent and the author is choosing after having seen results, the only choice a reader can credit without also having to credit the author is the one that cannot improve the author's own finding. \textbf{This is an interpretation of a registered rule that is silent, not an extension of a rule that speaks}, and it is recorded here so that a reader sees the reasoning rather than inferring it from a denominator.

\emph{Quantities unchanged.} The eligible population remains 16 and the numerically assessable population remains 11. No verdict, no threshold classification, no per-item-outputs result and no imputation changes. The frozen claim table is not edited.

\emph{The alternative, and its direction.} Excluding R09 and R17 by the strict reading was available and was declined. It would have moved the eligible population from 16 to 14 and the assessable population from 11 to 9, left the count below the planning threshold at 1, and moved that count as a proportion of the assessable population from 9.1\% to 11.1\%. \textbf{That is the direction favourable to this audit's thesis.} Amendment 2 recorded that the R10 correction did not improve any count in that direction; this determination likewise does not, and it is the conservative of the two readings available. The quantities in this paragraph are recorded so that the choice is auditable rather than merely asserted.

\emph{Reporting.} The locus finding is reported in the paper as a result in its own right rather than as an eligibility adjustment: across the six cards, with the underlying evidence held constant, three assert recovery in prose, two state two scores and characterise neither, and one makes no comparative statement at all. The consequence reported alongside it is that an inclusion rule keyed to prose, which \S{}3.1 is, captures equivalence claims non-randomly, so the frozen candidate count of 17 is a floor on the population rather than a census of it. Any report of the eligible population states that the boundary cases were retained under this amendment.

\emph{Verification status.} The locus review supporting this amendment is author re-verification against archived sources, by a second automated pass of the same class of tool that produced the record it checked. It is \textbf{not} independent verification, and neither it nor any agreement between it and the 2026-07-15 passes may be reported as dual coding or inter-rater reliability. \S{}3.3 and Amendment 1 are unchanged.

\emph{Scope.} This amendment applies \S{}3.1 to two claims and records the reasoning. No inclusion criterion is added, widened or narrowed; no claim is re-extracted; no source is re-fetched for extraction purposes; the frozen claim table, the \S{}4 verdict rules, the indeterminacy rules, the discordance imputation, the atlas, and every other registration are unchanged and not reopened. Amendment 2 remains in force in full.

\emph{Decision context.} \textbf{Results were inspected before this decision.} The rev-3 verdicts were computed on 2026-07-31 and the locus classification on 2026-08-02, and both were known at signature. The determination reached is the one that leaves every published count where it stood and declines the change that would have improved the headline proportion. The superseded and the current readings of \S{}3.1 as applied to R09 and R17 are both recorded above.

\emph{Signed.} \authorname{}, 2026-08-03. Drafted by Claude Code at \texttt{2857cd0}; its \emph{Determination} was redrafted at \texttt{adaf263}, after the distinction it rests on was verified directly against the sealed source archive, to concede that \S{}3.1 is silent at this boundary rather than to assert that it is satisfied. Appended on the verbatim instruction ``sign it and append''.

\textbf{2026-08-04 --- Amendment 4 (provenance remap; no protocol change).}

\emph{Occasion.} \texttt{docs/\allowbreak{}audit\_sources\_20260731.tar.gz}, holding the full-text captures of all seventeen audited sources, entered the repository at \texttt{cc357db} and was never deleted, so every commit from there to HEAD carries it. \texttt{origin} is a public GitHub repository, so pushing any commit in that range publishes the corpus. That contradicts the redistribution review of 2026-08-02, which found four of the seventeen carry no grant permitting a third party to republish their text, and the seven method papers sitting under arXiv's default licence, which authorises arXiv to distribute them rather than authorising us to. It also contradicts \texttt{README.md}, which states the captures are not redistributed. The repository has therefore been unpushable since 2026-08-02, and the resolution of record was to leave it so.

\emph{Finding.} Removing the blob rewrites 54 commits. \texttt{bb45528} is one of them, and Amendment 2 cites it in its own signature line above. The rewrite was computed on a throwaway clone and verified there before this amendment was drafted: 251 commits before and after with nothing pruned, author, email, date and subject byte-identical for every commit, and the only tree difference across the entire range the removed tarball. \texttt{19d485c}, also cited in that signature line, is an ancestor of \texttt{cc357db} and does not change. \texttt{987377a}, tag \texttt{v1.0.0}, is likewise an ancestor, so the release tag and its Zenodo archive lie outside the rewrite. The private sealed copy hashes \texttt{a912a1e7af0efd58459dcf57ade84be96cfea8337147a13d336dacfdb9240259}, identical to the blob in git, so removal loses nothing.

\emph{Determination.} \textbf{The tarball is removed from the repository's history, and \texttt{bb45528} is superseded by \texttt{ed92ae8} on the record rather than in the text.} The corpus remains identified and digest-checkable: the \texttt{.sha256} and \texttt{docs/\allowbreak{}audit\_sources\_manifest.tsv} are retained, and \texttt{scripts/\allowbreak{}fetch\_audit\_sources.py} rebuilds it from each publisher. The signature line of Amendment 2 is to be read as citing \texttt{ed92ae8} wherever it cites \texttt{bb45528}, and the full mapping at \texttt{docs/\allowbreak{}audit\_source\_tarball\_hash\_map\_20260804.tsv} governs any other stale identifier. \textbf{The original text of Amendment 2 is not edited.} The superseded identifier stays exactly as signed, because correcting it in place would leave a record reading as though the chain never broke, and that it broke is what this amendment exists to preserve.

\emph{The alternative, and its direction.} The alternative was abandoning the rewrite and never pushing, which was the resolution of record from 2026-08-02. It is rejected because it makes the repository permanently unpublishable, and the artifact link in a submitted paper cannot point at a repository that does not exist. The cost of the rewrite is borne once and is documented in the mapping file; the cost of not pushing recurs indefinitely. What the rewrite concedes is that it is irreversible once pushed, and that 54 commit hashes cited anywhere outside the mapping file go stale without warning.

\emph{Quantities unchanged.} No inclusion rule, eligibility rule, verdict rule, indeterminacy rule, discordance imputation, denominator or count is reopened. The eligible population remains 16. Amendments 1, 2 and 3 remain in force in full, and every published number stands.

\emph{Scope.} This amendment records a change to commit identifiers and to what the repository distributes. It changes no analysis and no audited property.

\emph{Decision context.} \textbf{Results were inspected before this decision.} The rev-3 verdicts were computed on 2026-07-31, the locus classification on 2026-08-02, and Amendment 3 was signed on 2026-08-03; all were known at signature. This amendment changes no analysis, no count and no verdict, so there is no outcome for that knowledge to have biased. It is recorded because the standing requirement applies to every amendment to a frozen protocol, not only to those that could move a number.

\emph{Signed.} \authorname{}, 2026-08-04. Drafted by Claude Code at \texttt{df1615b} after the rewrite was computed and verified on a throwaway clone; its \emph{Determination} and \emph{Decision context} were completed on the verbatim instruction ``i read the draft, fill in the two sections as approved and append''. The rewrite itself was not applied at the time of signature.
```
---

## Reader's index

Sections in reading order (numbered as the compiled paper numbers them; front matter and appendix marked).

| # | Section | File |
|---|---|---|
| 1 | paper/audit_denominators.tex | `paper/audit_denominators.tex` |
| — | Abstract | `paper/abstract.tex` |
| 2 | Introduction | `paper/sections/introduction.tex` |
| ↳ | (subsection) paper/figures/fig1_cancellation.tex | `paper/figures/fig1_cancellation.tex` |
| 3 | Related work and positioning | `paper/sections/related_work.tex` |
| 4 | Paired certification: what an equivalence claim has to show | `paper/sections/certification.tex` |
| ↳ | (subsection) What was frozen, and when | `paper/sections/preregistration.tex` |
| 5 | The atlas: cancellation at scale, and what certification costs | `paper/sections/atlas.tex` |
| 6 | What published equivalence claims actually report | `paper/sections/audit.tex` |
| 7 | Cancellation is worse where practitioners choose | `paper/sections/minigrid.tex` |
| 8 | Exploratory scoring-pipeline sensitivity | `paper/sections/harness_sensitivity.tex` |
| 9 | Artifacts | `paper/sections/artifacts.tex` |
| 10 | Limitations | `paper/sections/limitations.tex` |
| 11 | Conclusion: a reporting standard for compression claims | `paper/sections/conclusion.tex` |
| App. | Reconciling the calibration-sensitivity antecedents | `paper/sections/appendix_related_detail.tex` |
| App. | Preregistration detail | `paper/sections/appendix_prereg_detail.tex` |
| App. | Full audit table | `paper/sections/appendix_audit_table.tex` |
| App. | Atlas construction detail | `paper/sections/appendix_atlas_detail.tex` |
| App. | Controlled experiment: supporting detail | `paper/sections/appendix_minigrid_detail.tex` |
| App. | Harness-sensitivity detail | `paper/sections/appendix_harness_detail.tex` |
| App. | Artifact detail | `paper/sections/appendix_artifacts_detail.tex` |
| App. | Automated claim extraction: procedure, reliability, and AI use | `paper/sections/appendix_extraction.tex` |
| App. | Preregistration documents | `paper/sections/appendix_registrations.tex` |
