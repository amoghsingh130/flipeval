# QA report: body compression, four stages, 2026-08-06

Clean build from a removed `.aux`/`.log`/`.pdf`/`.bbl`. Every figure below is
measured, not estimated.

## 1. Page counts

| | before stage 1 | **after stage 4** |
|---|---|---|
| **Main body, before references** | 34 | **32** |
| References begin on | 35 | **33** |
| Total PDF | 101 | **100** |

Target was 26-29. **The body is 32.** It is above the range, which under the
brief triggers `docs/AUDIT_LINE_EDIT_PROPOSAL_2026-08-06.md` rather than an
edit to `audit.tex`.

## 2. Section map, clean build

| section | start | span | stage target | outcome |
|---|---|---|---|---|
| Introduction + Fig 1 | 2 | 3 | — | at its floor |
| Related work | 5 | 2 | ~1 | **over by 1** |
| Paired certification | 7 | 4 | 3-3.5 | **over by 0.5** |
| Atlas | 11 | 4 | — | untouched this round |
| **Audit** | **15** | **8** | — | **untouched, as instructed** |
| Mini-grid | 23 | 5 | 3-4 | **over by 1** |
| Harness sensitivity | 28 | 1 | — | at its floor |
| Artifacts | 29 | 1 | — | at its floor |
| Limitations | 30 | 1 | — | at its floor |
| Conclusion | 31 | 2 | 1-1.5 | **met** (1.5, rounded up by the section head) |

Related work and mini-grid both ended mid-page, so their prose reductions (740 →
505 words and 2,089 → ~1,400) did not fully convert into page boundaries. That is
the accumulate-then-register behaviour every relocation in this campaign has
shown.

## 3. Where the principal evidence concludes

| beat | section | concludes |
|---|---|---|
| cancellation mechanism | Introduction + Fig 1 | p5 |
| reporting standard, in outline | end of Introduction | **p5** |
| paired certification method | Certification | p11 |
| atlas scale | Atlas | p15 |
| audit reporting gap | Audit | **p23** |
| controlled seed reversal | Mini-grid | **p28** |
| standard recapped with evidence in hand | Conclusion | p32 |

**The principal evidence concludes on page 28.** The argument is *stated* by p5
and the two large evidential sections finish at p23 and p28; limitations,
artifacts and the conclusion follow. A reader who stops at p15 has the mechanism,
the method and the scale; one who stops at p23 has everything except the
controlled experiment.

## 4. Gates, all passing

```
in-image pytest, job 11705552  : 348 passed, 0 skipped, exit 0
PAPER_CHECK                    : OK, 0 dangling refs, 0 unresolved cites
                                 24 files, 120 labels, 208 refs, 26 tabulars
STALE_CLAIM                    : OK
gen_denominator_macros --check : OK on all three layers
gen_audit_tables --check       : OK, 17 rows byte for byte
REGISTRATIONS_VERBATIM         : OK, 7,103 words across 4 documents
ABSTRACT_CHARS                 : 1879 / 1920, margin 41
churn_ratio.py --check         : OK, 25 printed values
freeze_prepace --verify        : passed
check_layout.py                : OK
prose em dashes                : 0
undefined refs / cites         : 0 / 0
```

## 5. Bounding-box layout verification

Every body page measured with `pdftotext -bbox`. Maximum glyph `xMax` is
**exactly 484.5pt on all 32 body pages**, which is the text-block right edge:
**no body page has ink outside the measure**. The single accepted violation is on
page 90, inside the frozen registrations appendix.

## 6. The two remaining overfull boxes, classified

| pt | location | classification |
|---|---|---|
| 5.16 | `appendix_registrations.tex` lines 369-370 | **ACCEPTED, permanent.** A 64-character model revision hash with no break point, inside text reproduced verbatim and machine-checked at 7,103 words. The file cannot be edited to add a break point without falsifying the reproduction, and `main.tex` already applies `\emergencystretch` 6em around it from outside. Recorded in `check_layout.py`'s `ACCEPTED_INK`, keyed to the hash string rather than to a page number. |
| 0.32 | `appendix_artifacts_detail.tex` lines 196-208 | **HARMLESS.** Below the width of a rule and below the gate's 1pt reporting threshold. Not visible at any rendering. No action. |

Neither is in the main body.

## 7. Float verification

| float | page | in body? |
|---|---|---|
| `fig:cancellation` | 3 | yes |
| `tab:certification` | 8 | yes |
| `tab:atlas-strata` | 14 | yes |
| `tab:audit-taxonomy` | 17 | yes |
| `tab:audit-sensitivity` | 20 | yes |
| `tab:h3-eightcell` | 25 | yes |
| `tab:churn-aggregations` | 26 | yes |

**Zero main floats leak into the appendices**, and placement order matches
declaration order with no float overtaking another. All seven are `[!t]`.

## 8. Visual inspection

All 32 body pages were rendered to PNG at 90 dpi and screened mechanically for
ink past the right edge, ink below the text block, and sparse pages; nothing was
flagged beyond the page folio, which sits at the same position on every page by
design.

Pages carrying a float, a section boundary, or prose changed by this round were
additionally opened and read at 100 dpi:

- **p3**, Figure 1: four panels legible, no overlap or clipping, atlas context
  strip inside the measure after the `inner sep=0` fix.
- **p7**, certification opening: both display equations inside the measure after
  the width regression the layout gate caught mid-stage was fixed.
- **p17**, `tab:audit-taxonomy`: every column visible including the empty
  prospective-margin column that is the table's evidential point.
- **p20**, `tab:audit-sensitivity`: 10 / 1 / 0 with the total, and the 43.6%
  sentence intact below it with its not-a-probability framing attached.
- **p26**, `tab:churn-aggregations` and Result 1: three rows correct, the
  descriptive-not-registered label present on both the Result and the caption,
  and the 6.8% / 16.2% exclusion rates in the caption.
- **p31**, conclusion opening: recaps rather than reintroduces; no second
  presentation of the five-line standard anywhere in the section.

**Scope of this inspection, stated honestly:** every body page was rendered and
mechanically screened; six pages were read closely. Pages of unchanged prose in
untouched sections were not read line by line in this round.

## 9. What was not done, and why

`paper/sections/audit.tex` was **not edited**, as instructed. It remains the
largest body section at 8 pages. The proposal to take it to about six is
`docs/AUDIT_LINE_EDIT_PROPOSAL_2026-08-06.md`, which maps all 18 protected
qualifications to the sentence that would carry each one afterwards, and is not
executed.
