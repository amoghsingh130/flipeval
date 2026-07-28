# Phase 4 trim — ranked candidate list (2026-07-27)

> ## ✅ EXECUTED 2026-07-27. Target revised 11,000–12,000 → **~13,000**.
>
> **Amogh's decision, same day.** The 12 non-risky candidates were applied and
> the two MED-HIGH ones (13, 14) were **skipped**: 234 words is not worth a cut
> the analysis flagged against itself.
>
> **Why the target moved.** TMLR has no page limit, so this was always a
> readability cut rather than a compliance one. Reaching 11,000–12,000 required
> opening the do-not-cut list — the passages that demonstrate the paper's
> honesty — and trading those for roughly four pages is the wrong trade. **A
> later pass should not reopen this hunting the missing 770.** The decision is
> recorded here so it is not silently reversed.
>
> **Outcome: body 14,451 → 13,992 (−459).** See "What actually happened" at the
> end, which reports the shortfall against my own estimates rather than
> restating them.

## Measurement, and why it disagrees with 15,044

Counted with markup stripped, comments removed, and `tabular`/`table`/`figure`
environments excluded (table *cells* are not prose). One consistent metric is
used throughout this document.

| | words |
|---|---:|
| **Body** (abstract + non-appendix sections) | **14,451** |
| Appendices | 3,782 |
| Total | 18,233 |

The brief's figure of 15,044 came from an earlier ad-hoc count and is ~600 above
this one; the difference is almost entirely table-cell content, which that count
appears to have included. **Nothing was cut to close that gap** — it is a
measurement difference, not a trim. All deltas below are against 14,451.

Distance to target: **−2,451** to reach 12,000; **−3,451** to reach 11,000.

Relocation to an appendix counts as a body reduction and is marked **[R]**.
Deletion is marked **[D]**.

---

## Part 1 — APPLIED (low cost, authorized without asking)

| # | File | Passage | −w | Lost | Numbers relocate? |
|---|---|---|---:|---|---|
| A1 | `atlas.tex` | "What this section does and does not support", *Supports* half **[D]** | −56 | Nothing — it restated the section's four findings verbatim | No. Killed a **rev-1 survivor** in passing (see below) |
| A2 | `audit.tex` | "…does and does not establish", *Establishes* half **[D]** | −36 | Nothing — restated (i)–(iv) from §4.2/§4.5 | `2.0`–`12.9` survive in `tab:audit-underpowered` |
| A3 | `certification.tex` | "…does and does not support", *Supports* half **[D]** | −42 | Nothing — restated the section's own three findings | `2.3`–`14.7`, `4.2` survive in `tab:certification` |

The *"Does not support"* half of all three was kept whole. It is the half that
tells a reader what not to overread, and it is not restatement.

**Net from Part 1: −134 words.** Offsetting additions in the same pass:
`artifacts.tex` +209 (item 2 of the brief), `introduction.tex` +177 (the two
TODOs, B4), `abstract.tex` −18 (arXiv tightening). Body moved 14,215 → 14,451.

---

## Part 2 — NOT APPLIED. Ranked by cost-to-value, best value first.

Cost ratings: **LOW-MED** = mechanical, judgement-free. **MED** = a real
editorial choice. **MED-HIGH** = touches material the do-not-cut list was
written to protect, in spirit if not by name.

| # | File | Passage | w now | −w | What is lost | Numbers / SOURCE | Cost |
|---|---|---|---:|---:|---|---|---|
| 1 | `audit.tex` | "Discordance imputation" **[R]** → `appendix_audit_table` | 120 | −120 | Nothing; it is method detail, and the appendix already documents the CSV's imputation columns | Match-tier detail moves with it | LOW-MED |
| 2 | `related_work.tex` | "Losslessness, defined and achieved versus audited" **[D]** to ~70 w | 183 | −113 | The enumeration of Helcig's three losslessness notions and EAR. Positioning survives; the contrast is already made twice elsewhere | None | LOW-MED |
| 3 | `audit.tex` | "Two robustness notes" **[R]** | 202 | −202 | Nothing if relocated. Body keeps the one-clause statement that conclusions hold under the independent-binomial bound | Independent-binomial column values move | MED |
| 4 | `atlas.tex` | "Construction" + "Coverage, and what the exclusions reveal" **[R]** → new atlas appendix | 474 | −200 | Nothing if relocated; mining mechanics and the exclusion taxonomy | Exclusion counts move; `1,707` must stay in body | MED |
| 5 | `harness_sensitivity.tex` | Body section, given `appendix_harness_detail` already carries 791 w **[R]** | 492 | −160 | Nothing if relocated — the body duplicates the appendix's design description | `0.232`→`0.566` must stay in body | MED |
| 6 | `certification.tex` | "Scope and caveats": relocate caveats 2/3/4, keep 1 and 5 **[R]** | 259 | −150 | Body keeps the omission rule and the certification≠detection warning; thin-row and family-aggregation detail moves | Cell counts (5, 8, 17, 23, 24, 1311, 192, 56) move | MED |
| 7 | `related_work.tex` | "Per-item behaviour under compression": compress the three concurrent-work paragraphs | 379 | −150 | The churn↔CA algebraic identity and Nikolic/Cacioli detail | **The no-priority-claim sentence and its SOURCE comment must stay verbatim** | MED |
| 8 | `audit.tex` | "What was audited, and what was not": frame enumeration **[R]** | 297 | −110 | Body keeps 7/7/3 and the frame definitions in one sentence | Frozen-table hash citation stays in body | MED |
| 9 | `atlas.tex` | "The gray zone, and how it differs between the two strata" **[D]** | 207 | −60 | Compression only; the stratum contrast survives | None | MED |
| 10 | `preregistration.tex` | "Disclosed pre-registration data contact" — appendix carries 327 w of the same | 131 | −70 | Detail already duplicated in the appendix | None | MED |
| 11 | `limitations.tex` | "Status of the atlas numbers" — overlaps §3's spot-check | 97 | −40 | Duplication only | rev-1→rev-2 delta pointer | MED |
| 12 | `minigrid_escalation.tex` | "The screen ran on sealed cells" **[D]** to ~40 w | 92 | −50 | Compression of a process-integrity statement | Job IDs stay | MED |
| 13 | `preregistration.tex` | "The spot-check found a selection bias in our own pipeline" — appendix carries 501 w | 292 | −140 | ⚠️ This is §3's self-audit. §7's is explicitly protected; this is the same *kind* of evidence | 262-field reconciliation figure must survive | **MED-HIGH** |
| 14 | `minigrid.tex` | "The two-level paired bootstrap, and what a winner flip is not" **[R]** | 295 | −120 | ⚠️ The corrected bootstrap framing was a Phase-2 deliverable. Only the method exposition would move; the result and the "what a winner flip is not" distinction stay | Bootstrap CI values stay in body | **MED-HIGH** |

**Part 2 totals:** items 1–12 (nothing above MED) = **−1,425**.
Adding 13–14 = **−1,685**.

---

## The arithmetic, stated plainly

| Scenario | Body |
|---|---:|
| Now | 14,451 |
| + all MED and below (items 1–12) | **13,026** |
| + the two MED-HIGH items (13–14) | **12,766** |
| Target | 11,000–12,000 |

**Every cut in this document, including the two flagged risky, leaves the body
~770 words above the top of the target range.**

Closing that last 770 means going into: Result 1 and its hedge, the Paglieri
reconciliation, §7's self-audit, the post-hoc disclosure, the five-seed and
GSM8K limitations, the R04 exclusion narrative, or the K = 1→5→4 correction.
**Those are the do-not-cut list.** There is no path to 11,000–12,000 that does
not open it.

### Recommendation

Take items 1–12 and stop at **~13,000**. Reasons:

1. The brief calls this a **readability** cut and notes TMLR has no page limit.
   13,000 with the appendices carrying the machinery reads well; the marginal
   reader-minutes bought by the last 1,000 words are small.
2. Items 13 and 14 trade the paper's main asset — visible self-correction — for
   260 words. The do-not-cut list exists because that asset is what a reviewer
   cites as evidence the paper is honest. §3's spot-check and §7's self-audit
   are the same argument told twice about two different failures; cutting one
   because the other is protected is a technicality.
3. Most of items 1–12 are **[R]** relocations. Nothing is deleted, so nothing
   is at risk if the judgement is later reversed.

If 11,000–12,000 is firm, the decision needed is *which* protected passage
goes — and that is Amogh's, not mine.

---

## Found while surveying — three defects, all fixed, none of them trims

These are correctness fixes made in the same pass. They are recorded here
because a trim pass is exactly when a number can silently move.

1. **`atlas.tex` closer read "five to six times"** — rev-1's ratio, where rev-2
   gives 5.31 (S1) / 5.33 (S2). The 2026-07-27 A1 sweep corrected
   §"Net delta understates…", the introduction and the conclusion, and missed
   this one. **Fifth rev-1 survivor.** It died with the deleted *Supports* half.
2. **`conclusion.tex` read "roughly one evaluation cell in ten"** —
   §`sec:atlas:identical` retired that phrasing on 2026-07-26 for overstating
   rev-2's 8.49% share (= 1 in 11.8), and its comment says explicitly *"do not
   restore one in ten"*. The conclusion's restatement was missed.
   **Sixth rev-1 survivor.** Corrected to "about one in twelve".
3. **`introduction.tex` attached the wrong numbers to the right quantity** — it
   read *"the smallest difference their evaluation could resolve exceeds the
   difference they pronounce negligible, by 2.0× to 12.9×"*. That sentence
   describes the **MDD ratio** (`tab:audit-mdd`, range **1.60×–4.05×**) but
   quotes the **sample-size shortfall** (`tab:audit-underpowered`, range
   **2.0×–12.9×**), inflating the stated MDD gap roughly threefold. The
   description now matches the numbers. **The abstract was already correct**
   ("by factors of"), and its SOURCE comment already cited the right table — so
   a token-level check would have found nothing. This is the class of error the
   cross-reference invariant exists for, and only a quantity-level read catches
   it.

Plus one provenance fix: **every SOURCE comment citing
`results/audit_verdicts.csv` now cites `results/audit_verdicts_rev2.csv`.** The
typeset values were already rev-2 and did not change, but rev-1 and rev-2
disagree on numbers this paper prints (R06 77,282→81,780; R07
131,482→139,134), so the comments were instructing a future session to
"correct" correct values back to superseded ones. This includes the
typesetting instruction in `appendix_audit_table.tex`, which is unrendered but
is what that appendix would be built from. No verdict column moved between
revisions, so K = 4 and J = 5 are unaffected.

---

## Open, needing Amogh — not acted on

**`discriminant.tex` carries a live `\TODO` whose precondition is now met.** It
reads: *"replace or supplement with controlled cells from §7 once they exist,
keeping the pilot as the historical record."* The eight cells now exist and the
verdict is signed.

**I have not acted on it, and it should not be closed casually.** Running a
discriminant analysis over the eight confirmatory cells would be a *new
analysis on confirmatory data*, and no such analysis is in
`docs/H3_EIGHT_CELL_DECISION_2026-07-26.md`. Under the standing rule against
post-hoc analysis of registered cells, that needs a dated registration before
it runs — not a paper edit. The alternatives are to leave §9 on the pilot and
delete the TODO as superseded, or to register the analysis. Both are decisions,
not edits.

---

# What actually happened (2026-07-27, after execution)

## The estimates were optimistic by roughly 2.7×

| | estimated | actual |
|---|---:|---:|
| Candidates 1–12 | −1,425 | **−521** |
| `discriminant.tex` rewrite | (expected to shorten) | **+67** |
| Abstract tightening | — | −5 |
| **Net** | **−1,425** | **−459** |
| **Body** | 13,026 | **13,992** |

**Why the gap, stated plainly rather than explained away.** The per-candidate
estimates were made from heading-level word counts. On reading each passage in
full, cutting to the estimate would in most cases have removed content, not
redundancy — so the cuts landed shorter than promised. Specifically:

- **Candidate 3** (audit robustness notes, est. −202, actual ≈ −110). The
  estimate assumed the whole paragraph relocates. It cannot: the paragraph
  carries **two distinct findings** whose own source comment forbids merging
  them. Both stayed in the body; only the reasoning moved.
- **Candidate 6** (certification caveats, est. −150, actual ≈ −85) and
  **candidate 4** (atlas construction, est. −200, actual ≈ −160) both had to
  leave a pointer sentence behind, which eats a third of the saving.
- **Candidate 5** (harness body, est. −160, actual ≈ −60). The section had
  already been trimmed on 2026-07-26; the remaining duplication was smaller than
  the heading count suggested.

**Lesson for any future trim: estimate from the passage, not from the heading.**
A heading-level count cannot distinguish restatement from content, and
restatement is the only thing that is actually free to cut.

## `discriminant.tex` grew, and that was the right outcome

The brief expected the rewrite to shorten the section and to count against the
trim. It did the opposite: **277 → 344 words (+67)**. The content the rewrite was
asked to lead with — the MMLU and GSM8K resolution figures, and the
within-benchmark contrast on the fourth GSM8K cell — is new material that the
old single-paragraph version did not contain. Compressing the Kaggle pilot to
its two-sentence core recovered part of the cost but not all of it. The section
is better and longer; the expectation that it would shrink was simply wrong, and
is recorded as wrong rather than met on paper by cutting something else.

## Where the remaining ~992 words would have to come from

Reaching ~13,000 exactly would need one of:

- The two MED-HIGH candidates (−260), explicitly skipped.
- `minigrid.tex` (2,208 w, the largest section, untouched — its only candidate
  was the risky bootstrap one).
- `related_work.tex` (1,713 w) beyond the two candidates already applied.
- The do-not-cut list.

**None was taken.** 13,992 is the honest landing point of the authorized set.

---

# The cross-reference invariant, amended (2026-07-27)

**The version specified before this pass is insufficient, and there is a defect
that proves it.**

The introduction asserted *"the smallest difference their evaluation could
resolve exceeds the difference they pronounce negligible, by 2.0× to 12.9×."*
Both numbers are real, both appear in §4, and a value-only check passes. But
2.0×–12.9× is the **sample-size shortfall** ($n_{req}/n_{reported}$,
`tab:audit-underpowered`), while the sentence describes the **MDD ratio**
(`tab:audit-mdd`), whose range is **1.60×–4.05×**. The figure was correct about
the wrong thing, and overstated the gap it named roughly threefold.

### The amended rule

> **EVERY SUMMARY FIGURE IS CHECKED AS A PAIR — the value AND the quantity it is
> asserted to measure — against its source section. Value-only matching passes
> on figures that are correct about the wrong thing.**

### It cannot be automated

A token or multiset check compares values. The defect above is a mismatch
between a value and the *English description* attached to it, which means
deciding what a sentence claims. **Reading is what found it**, on a pass whose
stated purpose was cutting words, not checking numbers. The automated checks all
passed, before and after.

### Six figure-level defects have now survived multiple passes

Each was caught by a **different** method, which is the point:

| # | Defect | Caught by |
|---|---|---|
| 1 | 1.7× GSM8K paired advantage (rev-1) | Reconciling prose against the rev-2 CSV |
| 2 | 643 float-scored cells (rev-1) | Independent spot-check of the pipeline |
| 3 | Four thin families (rev-1) | Re-reading the caveat against `n_atlas_cells` |
| 4 | "five to six times" in §5.4, intro, conclusion | Targeted A1 sweep for the ratio |
| 5 | "five to six times" surviving in §5's closer | Reading the closer while trimming it |
| 6 | "one cell in ten" surviving in the conclusion | Grepping the retired phrasing across the tree |
| 7 | MDD ratio described, shortfall quoted | Reading the sentence's claim, not its numbers |

**That is evidence no single check covers the class, not evidence of
carelessness.** Each new method found what the previous ones structurally could
not see: a sweep for a value cannot find a value attached to the wrong quantity;
a check of one section cannot find a stale restatement in another; an automated
diff cannot read a sentence. The working assumption should be that a seventh
defect exists and will need a method not yet used.
