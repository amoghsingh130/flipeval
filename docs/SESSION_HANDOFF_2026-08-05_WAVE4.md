# Session handoff, 2026-08-05: Wave 3 done, Wave 4 blocked on spend

Supersedes `SESSION_HANDOFF_2026-08-05.md` for status. The instructions are still
`docs/FLAGSHIP_NARRATIVE_PLAN.md`; the Wave 3 findings are in
`docs/WAVE3_ADVERSARIAL_REVIEW_2026-08-05.md`.

**Branch `flagship-narrative`, worktree `.claude/worktrees/flagship`, HEAD
`097a7a0`. Not pushed. Working tree clean. All runnable gates green.**

## 1. What this session did

| commit | what |
|---|---|
| `e436436` | Wave 3 adversarial review, all six checks |
| `8d96b31` | Defect D8: the S1 median churn correction |
| `bf05691` | Three Figure 1 geometry defects fixed, guard added |
| `4092307` | Freeze refresh after the generator change |
| `b148a4a` | Narrative spine compression (coordinator's own files) |
| `097a7a0` | Artifacts detail moved to its appendix |

Wave 3 ran and is complete. Five of its six checks passed, including the two
that matter most for a reviewer: the flagship cell is honestly framed as an
illustrative maximum in three places, and neither panel C nor the abstract
overstates what certification concludes. It found one new numeric defect (D8)
and three Figure 1 geometry defects, all now fixed.

## 2. Gate state at `097a7a0`

```
PAPER_CHECK: 24 files, 104 labels, 164 refs, 23 cite keys, 12 environments,
             24 tabulars (232 rows)
PAPER_CHECK: OK -- 0 dangling refs, 0 unresolved cites, environments balanced
STALE_CLAIM: OK
REGISTRATIONS_VERBATIM: OK -- 7,103 words across 4 documents
gen_denominator_macros --check: OK on all three layers
ABSTRACT_CHARS 1864 / 1920, margin 56, 281 words   (measured)
in-image pytest, job 11691406: 325 passed, 0 skipped
freeze_prepace --verify: passed
```

The in-image expectation in `CLAUDE.md` is 325 and is correct. No tests were
added this session, so the count did not move.

## 3. Wave 4 died on the monthly spend limit

All four compression agents terminated mid-edit with the same API error that
killed the two Wave 3 reviewers. **This is now a repeat failure mode, not an
accident: two consecutive waves have been lost to it.** Plan around it.

Their partial output is preserved at **`40b71ba` on branch
`wave4-partial-20260805`**. Nothing was lost. It is not merged, and it must not
be merged as it stands, because three of the four agents cut body prose without
relocating any of it:

| file | body delta | its appendix |
|---|---|---|
| `audit.tex` | -1,739 words | +0 |
| `minigrid.tex` | -626 words | +0 |
| `related_work.tex` | -483 words | +0 |
| `preregistration.tex` | -138 words | +0 |
| `artifacts.tex` | -455 words | **+558, correct** |

About 2,990 words were removed from the body with no destination. The agents
were cutting first and relocating second and the limit landed in between. Only
the artifacts pair completed both halves, and only that pair was taken (`097a7a0`,
after verifying Option A survived and all gates passed).

## 4. The audit.tex reconstruction is well specified. Do this next.

This is the single biggest remaining lever, and the dead agent left a usable map.
Its `audit.tex` cut the body to 1,568 words **and kept every mandatory
qualification** (checked: Q2, Q3, Q4, Q8, Q9, Q12, Q13 all present, and the
forbidden "incompatible with a paired framework" phrasing absent). What it never
did was create the appendix targets it had already written references to.

Applying its `audit.tex` alone gives `PAPER_CHECK: FAIL` with exactly these
dangling refs:

```
app:audit:indeterminate   app:audit:margins   app:audit:peritem
app:audit:protocol        app:audit:rules     app:audit:r04
eq:tost-n                 sec:audit:locus
```

So the job is bounded: create six `\subsection`s in
`paper/sections/appendix_audit_table.tex` carrying those six labels, populate
them from the removed text, and resolve the two other labels. The removed
material includes three whole subsections, which map onto the targets naturally:

- `\subsection{What was audited, and what was not}` to `app:audit:protocol`
- `\subsection{Where the claim is written}` (`sec:audit:locus`) to a relocated
  home. **Careful:** `appendix_audit_table.tex:191` still says "Read by
  \S\ref{sec:audit:locus}", so that reference must be repointed, not orphaned.
- `\subsection{R04: outside the registered calculation}` to `app:audit:r04`
- `eq:tost-n` must land somewhere that `\eqref` can still reach.

Recover the removed text with:

```bash
git diff flagship-narrative wave4-partial-20260805 -- paper/sections/audit.tex \
  | grep '^-' | grep -v '^---' | sed 's/^-//'
```

That is 307 lines, about 3,167 words of raw removed text before accounting for
lines that were reworded rather than deleted.

**Do not take the cut without building the appendix homes.** Deleting evidence
is a defect, not a saving, and this project's whole convention is that detail
moves rather than disappears.

## 5. The page target: measured, and still not met

The body is **12,724 prose words** across 12 sections, down from 13,246 at the
start of this session. Plus 14 floats and Figure 1.

**No page count is measured and none can be.** There is no LaTeX on this host or
in the pinned image (probe job 11675341), so every page figure anyone has quoted
for this manuscript, including the previous handoff's "about 40", is an estimate.
At 480 to 550 words per article-11pt page, 12,724 words is roughly 23 to 27 pages
of text before floats, so call it 28 to 33 pages total. The brief's target is 12
to 16.

Closing that gap means removing roughly 6,000 more body words into appendices.
The realistic distribution, given what each section can actually give up:

| section | now | plausible target |
|---|---|---|
| `audit.tex` | 3,307 | ~1,000 (the Wave 4 draft reached 1,568) |
| `minigrid.tex` | 1,991 | ~1,200 |
| `related_work.tex` | 991 | ~450 |
| `certification.tex` | 1,072 | ~850, worked example to appendix |
| `harness_sensitivity.tex` | 593 | ~120, study to appendix |
| `preregistration.tex` | 599 | ~350 |
| `limitations.tex` | 779 | ~500 |
| `atlas.tex` | 1,316 | ~1,100 |

**What the coordinator's own files proved.** The narrative spine gave up only 67
words between them. The introduction, abstract and conclusion were rewritten
around the thesis in Wave 2 and are at their floor: the abstract sits at the
arXiv limit with 56 characters of margin, and the conclusion's five-line standard
is the paper's deliverable. There is no slack there, and looking for it again
would be wasted effort. All remaining slack is in the four sections above.

## 6. Still open from the previous handoff

- **D4, the 5.3x headline.** Unchanged and still the top author decision. Wave 3
  sharpened it: the derivations are 5.22 (S1 unrounded), 5.19 (S2 unrounded),
  5.27 and 5.33 (rounded, S1 now corrected by D8), 5.40 (pooled), 3.85 (median
  of per-cell ratios). 5.3 remains a fair rounding of the two stratum ratios.
  It is public in the Zenodo release and the blog post, so correcting the paper
  alone desynchronises the released record.
- **Wave 3's S2 finding.** Prose rule 5 was applied to the sections Wave 2
  rewrote but not to the ones it only restructured. Prose `\textbf` spans:
  `minigrid.tex` 17, `audit.tex` 14, `harness_sensitivity.tex` 7, `atlas.tex` 7,
  against a target of 3. Fold this into the compression rather than doing it as
  a separate pass.
- `paper/READING_COPY.md` still needs its single regeneration at the end.
- Figure 1 has still never been rendered. The three geometry defects were found
  and fixed by reading TikZ source, and `fits_in_panel()` now fails the build on
  a gross overrun, but that guard uses estimated Computer Modern widths and is
  not a substitute for looking at a page.

## 7. Blocked gates, stated plainly

These are from the brief's required-verification list and **cannot** be run here.
Do not record them as passed.

- Compile from clean: no LaTeX available.
- Main-body page count before references, and total PDF page count.
- Overfull and underfull box lists.
- Visual inspection of the abstract page, Figure 1, every main table, the
  section transitions, the first appendix page and the conclusion.

## 8. Standing constraints observed

Nothing pushed. No PR. No upload to arXiv, TMLR, Zenodo or Hugging Face. No
history rewritten. No source tarball touched. No signed amendment or frozen
registration altered. No audited source re-fetched. No private capture published.
Option A intact and re-verified this session against the artifacts relocation.
`appendix_registrations.tex` byte-identical and still verifying at 7,103 words.

## 9. Branches

```
flagship-narrative          097a7a0   integration, clean, gates green
wave4-partial-20260805      40b71ba   Wave 4 partial output, DO NOT MERGE AS IS
wave2-frontback             94aaabc   merged into flagship, removable
wave2-body                  b7b8b1c   merged into flagship, removable
worker-a .. worker-e        various   all five landed on main already, removable
```
