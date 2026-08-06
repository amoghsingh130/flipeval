# Proposal: a body-level line edit of the audit, eight pages to about six

**Not executed.** `paper/sections/audit.tex` is unchanged and stays unchanged
until this proposal is approved. Written 2026-08-06 because the four body
compression stages left the main body at **32 pages** against a 26-29 target,
which the brief says triggers this proposal rather than an edit.

## 1. Where the 32 pages are, measured from a clean build

| section | start | span | after this proposal |
|---|---|---|---|
| Introduction + Fig 1 | 2 | 3 | 3 |
| Related work | 5 | 2 | 2 |
| Paired certification | 7 | 4 | 4 |
| Atlas | 11 | 4 | 4 |
| **Audit** | **15** | **8** | **~6** |
| Mini-grid | 23 | 5 | 5 |
| Harness sensitivity | 28 | 1 | 1 |
| Artifacts | 29 | 1 | 1 |
| Limitations | 30 | 1 | 1 |
| Conclusion | 31 | 2 | 2 |
| **body** | **1-32** | **32** | **~30** |

Two pages off the audit lands the body at about **30**, which is still one page
above the range. The honest reading is that 26-29 is not reachable from the
audit alone; §6 says where the rest would have to come from.

## 2. What this proposal is, and is not

It is a **line edit**: shortening sentences that are already carrying their
qualification, removing connective and restating prose, and merging paragraphs
that make one point in two passes. **It moves no material to an appendix**,
because every paragraph in `audit.tex` that had a destination has already gone
to one across stages A-D. There is nothing left to relocate.

It is **not** a removal of any qualification. Every one of the 18 is mapped
below with the sentence that will carry it after the edit.

## 3. The eight audit subsections, and where the two pages come from

Prose word counts at the current HEAD, tables excluded.

| subsection | words | after | how |
|---|---|---|---|
| What was audited, and what was not | 413 | 300 | merge the freeze-provenance sentence into its footnote; drop the restatement of "every count in this section is over those 16", which the results subsection states again |
| What the sources declare | 197 | 170 | the "consequence for this section is structural" paragraph makes one point in four sentences |
| Where the claim is written | 243 | 150 | the floor-not-census consequence is stated twice, once as mechanism and once as consequence; keep the consequence |
| Availability of per-item outputs | 186 | 150 | the repair-cost contrast is stated in the body and again in `app:audit:v3detail`; keep the body's two sentences and let the appendix carry the elaboration |
| Verdict rules | 306 | 230 | the imputation paragraph re-explains what the atlas is; one clause suffices |
| Results | 363 | 300 | the "best read as a statement about resolution, not about error" sentence and the "an audit at 2 pp is a weak test" sentence make the same point |
| Claims that cannot be assessed | 344 | 250 | "This category is itself a result" restates the two-of-four chart-image finding already given in the preceding paragraph |
| R04 and the section close | 578 | 450 | the R04 ruling is stated once as mechanism and once as cost; the does-not-establish list and the prevalence sentence overlap in their first clause |
| **total** | **2,630** | **2,000** | |

630 words is about 1.3 pages of prose. The remaining 0.7 comes from the two
paragraph merges freeing partial lines across eight subsections, which is
recoverable only in a real build and is the reason the target is stated as
"about six" rather than exactly six.

## 4. Every protected qualification, and the sentence that carries it after the edit

**No row below loses its body location.** "Unchanged" means the sentence is not
touched at all by this edit.

| # | Qualification | Status after the line edit | Carrier sentence |
|---|---|---|---|
| 1 | Three frozen frames + registered inclusion rule, exhaustive, no discretionary sub-selection | **unchanged** | "Sources were enumerated exhaustively within three fixed frames..." and "Every claim meeting the criterion is audited; there is no discretionary sub-selection." |
| 2 | 17 candidates and 16 eligible, never collapsed | **unchanged** | "The frozen table contains \AuditFrozenCandidates{} candidate claims: 7 method papers, 7 official model cards or blogs, and 3 vendor documents... leaving \AuditEligible{} eligible sources" |
| 3 | Why R10 is excluded | **unchanged** | "one candidate's recorded quotation appears nowhere in its source, having been composed from a table cell... so \AuditIneligibleClaim{} is excluded by applying that rule as registered" |
| 4 | 0 prospective numerical margins, over complete source text | **unchanged** | "\textbf{No audited source declares a prospective numerical equivalence margin}" plus "This is established over complete source text, not the quoted sentence" |
| 5 | 10 qualitative / 6 measured-outcome, correctly defined | **unchanged** | "\AuditXtabQualTotal{} of the \AuditEligible{} make the claim in purely qualitative terms... The remaining \AuditXtabRetroTotal{} cite a number, and in every case it is a \emph{measured outcome}" |
| 6 | 0 task-matched releases, qualifier in the same sentence; R08/R15/R16 other suites | **unchanged** | the quote block, and "\AuditPerItemOtherTaskClaims{} come closest: they release per-item outputs for other suites, but not for the tasks their audited equivalence claim is about" |
| 7 | 5 non-assessable as 4 + 1; never "incompatible with a paired framework" | **unchanged** | "\AuditNotAssessableInsufficient{} are cases of \emph{insufficient reporting}... The remaining \AuditNotAssessableOutsideFramework{}, \AuditOutsideFrameworkClaim{}, is \emph{outside the registered calculation}" |
| 8 | 11 assessable at the registered uniform 2 pp; RETAIN VERBATIM sentence | **unchanged, verbatim** | "Because no source declares a margin, \textbf{the applicable margin throughout is the uniform \AuditMarginPP{}\,pp registered in advance}..." |
| 9 | 10 above / 1 within / 0 below; none below throughout | **unchanged** | `tab:audit-sensitivity` and "No assessable claim falls below the threshold throughout the interval." |
| 10 | R01 sensitivity-dependent planning flag, not a verdict; not robustly underpowered, stated once | **unchanged** | "This is a sensitivity-dependent planning flag, not a verdict" and, in the close, "or that any claim is underpowered in a sense that survives the sensitivity analysis, and none is" |
| 11 | 43.6% descriptive, number and framing in one sentence | **unchanged** | "the $\AuditSensitiveCellsPct{}\%$ is a descriptive share of reference cells, not a probability that the claim is underpowered, and those cells share models, benchmarks and infrastructure and are not independent observations" |
| 12 | Evidential sufficiency, not truth; no claim called false | **shortened, not weakened** | the bolded "No audited claim is described as false..." sentence is untouched; the following two sentences of elaboration merge into one |
| 13 | Not a prevalence estimate | **unchanged in the close**, the one-clause echo in §5.1 is what merges | "Nor does it establish a prevalence: \AuditEligible{} eligible sources within three frozen frames are not a sample from which the field's reporting practice can be estimated" |
| 14 | "Robust" means only across the atlas-IQR interval. **SINGLE POINT OF FAILURE** | **UNCHANGED, VERBATIM. This sentence is not eligible for editing at all.** | "Where a classification is called robust, that means only that it holds throughout the interquartile range of the atlas cells supplying its discordance rate, not across every plausible model of discordance." |
| 15 | R14 out of K; the trap paragraph stays in the body | **unchanged** | "R14 deserves a word, because its numbers look assessable and are not... the $742$ is a requirement for a calculation that cannot be performed" |
| 16 | R04 outside our registered calculation, not incompatible with paired analysis | **unchanged** | "This is a limitation of \emph{our registered calculation}, not of paired analysis: a graded metric supports paired resampling on the same items perfectly well" |
| 17 | Claim-derived margins withdrawn; K = 1 → 5 → 4 → 1-of-11 stays in the body | **unchanged** | "A first pass applying the registered \AuditMarginPP{}\,pp margin uniformly returned $K = 1$ of 12..." through "...are \textbf{withdrawn, not recomputed}" |
| 18 | Two automated passes, not statistically independent; author re-verification | **unchanged** | "they do \emph{not} make the two passes statistically independent, because both share a common model prior" and "author re-verification against the archived sources, not independent verification by a second coder" |

**Fourteen of the eighteen are untouched. Four are shortened by merging
elaboration around them, and in none of those four does the qualification's own
sentence change.**

## 5. Verification the edit must pass before it is committed

Identical to the stage protocol already used, plus one addition: because this
edit touches sentences rather than moving blocks, the ledger walk must be run
**at source with exact-string matching** on all 18 carrier sentences above, not
on rendered text. `pdftotext` without `-layout` drops `\emph{}` runs and has
already produced extracted text asserting the opposite of qualification 18.

```
python3 tools/check_paper.py                    # 0 dangling refs
python3 tools/gen_denominator_macros.py --check  # every count still generated
python3 tools/check_layout.py                    # ink, not just the log
python3 ../scripts/churn_ratio.py --check
```

## 6. Where the remaining pages would have to come from, if 29 is required

After this edit the body is about 30. The remaining page is **not** in the audit.
The candidates, in order of how defensible removing them is:

1. **Mini-grid, 5 pages.** `tab:churn-aggregations` could move to an appendix
   with its two rows restated in Result 1's prose, saving roughly a third of a
   page. It is the frozen ratio work, so this needs explicit approval.
2. **Atlas, 4 pages.** The identical-score subsection and the strata narrative
   overlap in their framing paragraphs.
3. **Certification, 4 pages.** Now at its floor: one equation, one table, one
   example, and the scope list.
4. **Introduction, 3 pages.** At its floor and load-bearing for the "argument
   visible early" requirement.

**Recommendation: execute this proposal, land at about 30, and stop.** The
difference between 30 and 29 is one page, and every remaining page costs either
a frozen deliverable or a load-bearing qualification. The brief's own instruction
is to report the defensible number rather than delete load-bearing material.
