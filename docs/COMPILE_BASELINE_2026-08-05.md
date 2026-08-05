# First compiled baseline, 2026-08-05

**This manuscript had never been compiled.** Every page figure ever quoted for
it, including "about 21", "about 40" and my own "28 to 33", was an estimate from
word counts. All of them were wrong. This document records the first real
measurement, taken at commit `18b2db1` with the manuscript **unchanged**.

## How the blocker was removed

The previous sessions concluded there was no LaTeX. That conclusion was correct
about the two places they looked (the login node PATH and the pinned Apptainer
image, probe job 11675341) and wrong as a general claim, because neither had
checked whether one could be installed.

TeX Live 2026 `scheme-small` is now installed at `~/scratch/texlive`
(`bin/x86_64-linux/pdflatex`), from `mirror.ctan.org`, which the login node can
reach. It is **not** part of the pinned computational environment and does not
touch it: it is a document build tool living in scratch, and scratch is subject
to the 60-day purge, so it may need reinstalling. `\usetikzlibrary{arrows.meta}`
resolves through pgf 3.1.12's `pgflibraryarrows.meta.code.tex` fallback.

Build command, from `paper/`:

```bash
export PATH=$HOME/scratch/texlive/bin/x86_64-linux:$PATH
pdflatex main; bibtex main; pdflatex main; pdflatex main
```

## Page counts, measured

| quantity | pages |
|---|---|
| **Main content, before references** | **1 to 35** |
| References | 36 to 38 |
| Appendices | 39 to 96 |
| **Total PDF** | **96** |

Against the brief's target of 12 to 16 for the flagship argument, and 18 to 22
treated as acceptable. **The main body is 35 pages.** The gap is larger than any
prior estimate suggested: my own word-count estimate of 28 to 33 was low, and
the earlier "about 40" was high, but only because it was guessing at the total
rather than the body.

Boundaries were measured by compiling an instrumented **copy** in scratch with
`\label`s at `\bibliography` and `\appendix`. The repository copy was not
modified.

## Diagnostics

```
Overfull  \hbox : 58     (worst 244.40pt too wide)
Overfull  \vbox : 0
Underfull \hbox : 11
Underfull \vbox : 0
Undefined references : 0
Undefined citations  : 0
Multiply-defined labels : 0
bibtex : clean, 0 errors, 0 warnings
```

Overfull hboxes by source file (57 of 58 attributable):

| count | file |
|---|---|
| 31 | inside float/output routine, file not attributable from the log |
| 5 | `appendix_minigrid_detail.tex` |
| 3 | `appendix_registrations.tex` |
| 3 | `audit.tex` |
| 2 each | `appendix_prereg_detail.tex`, `appendix_audit_table.tex`, `appendix_extraction.tex`, `minigrid.tex` |
| 1 each | `atlas.tex`, `harness_sensitivity.tex`, `appendix_atlas_detail.tex`, `appendix_harness_detail.tex` |

## Float placement: the worst finding

```
p8   tab:certification          p27  tab:h3-eightcell
p13  tab:atlas-strata           p31  tab:sensitivity
p17  tab:audit-taxonomy         p41  tab:freeze-timeline
p21  tab:audit-sensitivity
p87  fig:cancellation   <-- declared on page 2
p88-96  tab:audit-identity, audit-characterisation, audit-power, audit-locus,
        audit-mdd, certification-1pp, certification-3pp, identical-extreme,
        minigrid-escalation, h3-ds, h3-supporting, h3-resolution
```

**Figure 1 is on page 87.** It is `\input` from the introduction and is the
figure the entire flagship argument is built on, and it lands 85 pages after the
text that discusses it, past the references, deep inside the appendices.

The cause is height. The `tikzpicture` is about 8.75cm tall and the caption runs
about 14 lines, so the float exceeds what `\topfraction` (0.7 by default) allows
in a `[t]` slot, on every page. LaTeX deferred it, and once deferred it queued
behind nothing until the final flush. The twelve appendix tables did the same
thing for the same reason and piled up at pages 88 to 96.

Body tables 1 to 6 place correctly, so this is specifically a float-height
problem, not a general placement failure.

## Figure 1: visual defects, first inspection ever

Rendered at 260 dpi with `pdftoppm` and inspected. The generated file's own
header said it had never been looked at. It has ten defects, none of which
source-reading found, because they are all consequences of how text actually
wraps and how wide glyphs actually are.

| id | panel | defect |
|---|---|---|
| F1 | whole | floats to page 87 (above) |
| F2 | A | `GPTQ` and `AWQ` row labels are overlapped by the bars, rendering as `GPT` and `AWC` |
| F3 | A | `Gap: 0.58 pp` collides with the AWQ row it is drawn over |
| F4 | A | the italic subtitle wraps to two lines where one was budgeted, pushing everything below |
| F5 | B | `9.12\%` is anchored inside the harmful bar, but that bar is 9.12% of 5.2cm = 0.47cm wide and the label needs about 0.9cm, so only `%` is visible |
| F6 | B | `8.54\%` sits above the bar, detached, level with the subtitle |
| F7 | C | `items run` and `items required` labels are overlapped by their bars, the second rendering as `items req` |
| F8 | C | the body text block overflows the panel border downward |
| F9 | D | the seed labels, the `all cells:` dot row and the `reversed` key all collide with the sentence above them |
| F10 | D | the panel title touches the right panel border |

The Wave 3 geometry fixes (G1 to G3) were correct as far as they went and are
still in place. They fixed horizontal overruns past panel and text-block edges.
The defects above are a different class: vertical overflow of wrapped text and
labels colliding with the bars they annotate. `fits_in_panel()` cannot see
either, because it checks only a declared horizontal width against a panel edge.

## Tables: `tab:atlas-strata` is unreadable

The 244.40pt overfull hbox is `atlas.tex:178`. Rendered, the S2 column runs off
the right edge of the page: the header is cut mid-phrase at "S2 (Neural Magic
W4A16" and **every S2 value is off the page**. A reader of the PDF cannot see
309 cells, 0.048, 0.009, 53 (17.2%) or 19 (6.1%).

The section's own prose calls this table "the empirical core of the paper's
motivation".

The D8 correction from earlier today does render correctly: the table shows
`0.137` and the prose shows "5.27 in S1 and 5.33 in S2".

## What is now unblocked

Priorities 3 and 4 asked for a compile after each relocation and real page
counts rather than estimates. Both are now possible. No page claim in this
project needs to be an estimate again.
