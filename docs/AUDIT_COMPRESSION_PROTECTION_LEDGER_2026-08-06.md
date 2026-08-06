# Audit compression: protected-qualification ledger

Written 2026-08-06, **before any prose in `paper/sections/audit.tex` is changed**.
Source list: `docs/FLAGSHIP_NARRATIVE_PLAN.md` §8 and
`docs/SESSION_HANDOFF_FLAGSHIP_2026-08-05.md` §10.

`sections/audit.tex` is **665 lines, 10 body pages** at `048ccd3`, starting on
page 16. Target: approximately 3 to 4 body pages across four committed stages.

## How to read this

- **Body?** `YES` means the qualification must be readable in the main body
  after compression. `POINTER` means the body keeps a one-clause statement and
  the supporting detail moves to an appendix.
- **Current location** is a line number at `048ccd3`. **These shift on every
  edit.** Locate each qualification by its quoted text, never by line number.
- **Verification** is filled in per stage, in this file, in the same commit as
  the stage.

## Standing rules that apply to every row

1. **Destination before deletion.** No body text is removed until its appendix
   destination exists, compiles, and is referenced successfully. A body edit
   citing a label that does not exist yet fails `PAPER_CHECK` with dangling
   refs, which is exactly how an earlier attempt at this file was caught.
2. **No hand-typed audit count, ever.** Every count is an `\Audit*` macro from
   `paper/audit_denominators.tex`, generated from
   `results/audit_verdicts_rev3.csv` (job 11591245, single run, `0444`). If a
   compressed sentence needs a number, it uses the macro.
3. **Deletion-only compression is not accepted.** Every removed evidentiary
   detail is redundant with surviving text or has a named destination in the
   `destination` column.
4. **Every subsection label survives.** All eight are referenced from outside
   `audit.tex` (`sec:audit` 10 times, `sec:audit:v3` 7, `sec:audit:results` 7,
   `sec:audit:taxonomy` 4, `sec:audit:rules` 3, `sec:audit:r04` 3,
   `sec:audit:locus` 2, `sec:audit:indeterminate` 1). A label may move into an
   appendix only if every referring site still reads correctly. `eq:tost-n` has
   **zero** external references and is the one label free to move.

## The ledger

| # | Qualification, exactly | Body? | Current location | Appendix destination | Compact body location | Numerical source | Verified |
|---|---|---|---|---|---|---|---|
| 1 | The three frozen sampling frames (F1 method papers, F2 official model cards, F3 vendor blogs/docs) and the registered inclusion rule: assertion in prose or a table caption, trigger vocabulary fixed in advance, exhaustive, no discretionary sub-selection | **YES** | 84-92 | trigger vocabulary already in `app:registrations` and the released claim table | Stage A | `docs/audit_claim_table.csv` col `frame` (7/7/3) | **Stage A** |
| 2 | **17** frozen candidates and **16** eligible. Both numbers, never collapsed | **YES** | 97-101 | none; both stay | Stage A | `\AuditFrozenCandidates`, `\AuditEligible` | **Stage A** |
| 3 | Why **R10** is excluded: its recorded quotation appears nowhere in its source, having been composed from a table cell, so the registered inclusion rule excludes it; the row stays in the released table | **YES** | 148-157 | `app:audit:eligibility` (new) for the full-text-review detail | Stage A | `\AuditIneligibleClaim`, `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md` §4 | **Stage A** |
| 4 | **0** audited sources declare a prospective numerical equivalence margin, established over complete source text | **YES** | 195-209 | `app:audit:sweep` (new) for the keyword-sweep detail (parity/percentage point absent, "margin" only as layout artefact, the one vendor declining to fix a threshold) | Stage B | `\AuditProspectiveNumericMargin`, `\AuditXtabProspectiveTotal` | pending |
| 5 | **10** of 16 make the claim in purely qualitative terms with no number attached, and the remaining **6** cite a number that is in every case a **measured outcome**, not a declared tolerance | **YES** | 196-201 | none; both halves stay | Stage B | `\AuditXtabQualTotal`, `\AuditXtabRetroTotal` | pending |
| 6 | **0** sources release **task-matched** per-item outputs. "task-matched" must appear in the SAME SENTENCE as the zero, and R08/R15/R16 release outputs for other suites | **YES** | 306-313, 315-325 | `app:audit:v3detail` (new) for which suites each releases | Stage B | `\AuditPerItemTaskMatched`, `\AuditPerItemOtherTaskOnly`, `\AuditPerItemOtherTaskClaims`, `\AuditPerItemNone` | pending |
| 7 | **5** non-assessable, as an explicit **4 + 1** split: 4 insufficient reporting, 1 outside the registered binary paired-outcome calculation. **Never** "incompatible with a paired framework" | **YES** | 553-554, 556, 581-583 | `app:audit:indeterminate` (new) for the per-claim R02/R11/R13 detail | Stage C | `\AuditNotAssessable`, `\AuditNotAssessableInsufficient`, `\AuditNotAssessableOutsideFramework` | pending |
| 8 | **11** assessable claims, at the registered **uniform 2 pp** margin. The sentence "Because no source declares a margin, the applicable margin throughout is the uniform 2 pp registered in advance" is marked RETAIN VERBATIM in the file | **YES** | 352-355, 428-430 | none; the verbatim sentence stays | Stage C | `\AuditAssessable`, `\AuditMarginPP` | pending |
| 9 | **10** above / **1** changes within / **0** below throughout the atlas-IQR interval, and **no assessable claim falls below the threshold throughout** | **YES** | 460-470 (`tab:audit-sensitivity`), 497 | none; table and sentence both stay in body | Stage C | `\AuditAboveThroughout`, `\AuditChangesWithinIQR`, `\AuditBelowThroughout` | pending |
| 10 | **R01**'s sensitivity qualification: a sensitivity-dependent planning flag, **not** a verdict, and **not robustly underpowered**. Exactly one outright statement of the latter, in the section close | **YES** | 482-495, 644-648 | `app:audit:r01` (new) for the reversal-point and quartile arithmetic | Stage C (flag) + Stage D (the one outright statement) | `\AuditSensitiveClaim`, `\AuditSensitiveN`, `\AuditSensitiveNReq`, `\AuditSensitiveCellsBelow/Total/Pct` | pending |
| 11 | **43.6%** is a descriptive share of reference cells, **not** a probability, confidence level or p-value; the cells are correlated and are not independent draws. Number and framing in one sentence | **YES** | 489-495 | none; stays whole | Stage C | `\AuditSensitiveCellsPct` (= 345/792) | pending |
| 12 | Evidential sufficiency, **not truth**. **No claim is called false**, and no finding implies any audited model is degraded | **YES** | 120-128, 645-648 | none | Stage A (framing) + Stage D (the does-not-establish list) | `docs/AUDIT_REGISTRATION_2026-07-15.md` §4 | **Stage A** |
| 13 | **Not a prevalence estimate**: 16 eligible sources in three frozen frames are not a sample from which the field's practice can be estimated | **YES** | 656-658 | none | Stage A (one clause) + Stage D (full) | `\AuditEligible` | **Stage A** |
| 14 | **"Robust" means only** that a classification holds throughout the interquartile range of the atlas cells supplying its discordance rate. **SINGLE POINT OF FAILURE**: the sentence beginning *"Where a classification is called robust"* has no other home in the body | **YES, VERBATIM** | 658-661 | **none permitted** | Stage D | prose rule, not a count | pending |
| 15 | **R14** stays non-assessable and does not enter K. The trap paragraph (imputed n = 728 against 742) stays in the body, and "R04 and R14 carry no verdict" must re-attach to surviving prose | **YES** | 512-514, 572-579 | none for the trap paragraph | Stage C | `results/audit_verdicts_rev3.csv` row R14 | pending |
| 16 | **R04** is outside **our registered binary paired-outcome calculation**, not incompatible with paired analysis generally: CIDEr supports paired resampling; it is the flip model that does not apply | **YES** | 611-621 | `app:audit:r04detail` (new) for the overruled first-pass GSM8K history | Stage D | `results/audit_verdicts_rev3.csv` row R04 | pending |
| 17 | Claim-derived margins and the old shortfall range remain **withdrawn and non-verdict-bearing**. The **K = 1 → 5 → 4 → 1-of-11** sequence is the body's canonical self-correction and **must not move to an appendix** | **YES** | 21-34 (header), 623-635 | the K = 5 → K = 4 R04 *history* is already in `app:prereg:choices`; the **sequence itself** stays in the body | Stage D | `\AuditBelowThresholdAtMedian`, `\AuditAssessable` | pending |
| 18 | The two extraction passes are **automated** language-model sessions and **not statistically independent** (common model prior); never "inter-rater" or "dual coding". The locus re-verification was by the **author**, not an independent second coder | **YES** | 107-117, 287-293 | `app:extraction` already holds the procedure | Stage A (extraction) + Stage B (locus disclosure) | `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md` §1, AUDIT_REGISTRATION §3.3 | **Stage A** |

## Appendix destinations to create before any deletion

Existing and reusable: `app:audit-table`, `app:audit-method`, `app:audit:locus`,
`app:audit:mdd`, `app:audit:imputation`, `app:audit:robustness`,
`app:extraction`, `app:prereg:choices`.

To create:

| label | holds | ledger rows served |
|---|---|---|
| `app:audit:eligibility` | source-by-source cases and the full-text review that produced the R10 ruling; source provenance and verification detail | 3, 18 |
| `app:audit:sweep` | the complete-text keyword sweep behind the zero-margin finding | 4 |
| `app:audit:v3detail` | which suites R08/R15/R16 release, and the repair-cost argument | 6 |
| `app:audit:indeterminate` | per-claim detail for R02, R11, R13; the retained-components list | 7 |
| `app:audit:r01` | R01 planning values, reversal point, quartile arithmetic | 10 |
| `app:audit:r04detail` | the overruled first-pass GSM8K computation and the ruling's cost | 16 |
| `app:audit:history` | interpretive ruling history and superseded verdict history | 17 |
| `app:audit:fullrobustness` | full robustness results, both sensitivity directions | 9, 10 |

`app:audit:locus` already exists and already holds `tab:audit-locus`; the claim-locus
discussion relocates into it rather than into a new label.

## Verification to run after every stage

```bash
cd paper
python3 tools/check_paper.py                     # dangling refs = the destination-first check
python3 tools/gen_denominator_macros.py --check   # every audit count still generated
python3 tools/gen_audit_tables.py --check
python3 ../scripts/churn_ratio.py --check         # run from the repo root
pdflatex … bibtex … pdflatex … pdflatex
python3 tools/check_layout.py
python3 tools/measure_abstract.py
```

Then: record the actual page-count change, re-walk this ledger and update the
`Verified` column, inspect the affected pages and float placement in the
rendered PDF, and commit before starting the next stage.

**A stage is not accepted if any row above has neither a body location nor a
live appendix destination.**

## Stage log

### Stage A, design and scope (commit below)

`\S`"What was audited, and what was not" rewritten; the duplicate R10 ruling
removed from `sec:audit:taxonomy`, which now points at
`app:audit:eligibility`. Rows 1, 2, 3, 12, 13 and 18 verified present in the
body against the source and in the rendered PDF on pages 16-17.

**Measured: audit 10 body pages to 9. Body still 1-35.** One page, which is what
a 62-line-to-46-line rewrite of one subsection buys; the large reductions are in
Stages B and C, where the method detail and the per-claim cases move.

**Method note, learned here.** `pdftotext` without `-layout` silently DROPPED
`\emph{not}` from "they do \emph{not} make the two passes statistically
independent", producing extracted text that asserted the exact opposite of a
protected qualification. The PDF itself is correct; the extraction is not.
**Verify protected phrasing against the LaTeX source, and use `-layout` for any
rendered check.** A ledger walk driven by plain `pdftotext` output would have
raised a false alarm here, and could equally miss a real inversion.
