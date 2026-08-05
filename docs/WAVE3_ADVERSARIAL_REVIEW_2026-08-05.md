# Wave 3: adversarial review of the integrated manuscript, 2026-08-05

Branch `flagship-narrative`, reviewed at `e3f4290` (content identical to
`a180b12`; the tip commit adds only the handoff document).

Run against the six checks recorded in `SESSION_HANDOFF_2026-08-05.md` §6, the
list the two reviewers that died on a spend limit had been given. Run inline in
one session rather than as two subagents.

**What this review could not do:** compile the document. There is no LaTeX on
this host or in the pinned image (probe job 11675341), so no page count, no
overfull-box list, and no rendered figure. Figure geometry below is read from
the TikZ source and from `scripts/make_figure1.py`, with widths estimated from
Computer Modern metrics at `\scriptsize` = 8pt. Those estimates are the basis
for G1 to G3 and are stated as estimates.

`required_n_for_tost` could not be recomputed here either: the login node has no
scipy. It is covered by the in-image suite (325 passed) and by
`paper/figures/fig1_values.json` provenance.

---

## 1. Findings

### D8. `tab:atlas-strata` prints the wrong S1 median churn. NEW, CONFIRMED.

The S1 median accuracy-state churn over the analysis population is
**0.137452**, which prints as **0.137**. `sections/atlas.tex:177` prints
**0.138**.

Population used: `results/atlas_cells_summary_rev2.csv`, `excluded_or_skipped`
false and `contains_disclosed_probe_cell` false, giving S1 n=1,398 and S2 n=309.
That is exactly the population the table's own SOURCE comment declares, and both
counts reproduce.

Every other cell of that table reproduces exactly:

| quantity | S1 | S2 |
|---|---|---|
| cells | 1,398 | 309 |
| median churn | **0.137452 (paper: 0.138)** | 0.048000 |
| median abs net delta | 0.026316 | 0.009242 |
| TOST-equivalent at 2 pp | 68 (4.9%) | 53 (17.2%) |
| exact McNemar p < .05 | 371 (26.5%) | 19 (6.1%) |
| neither (gray zone) | 967 (69.17%) | 240 (77.67%) |

**What it propagates to.** The 0.138 is the numerator of the S1 ratio wherever
it appears:

- `atlas.tex:127` SOURCE comment, `S1 0.138 / 0.026 = 5.3077`. With the correct
  median: `0.137 / 0.026 = 5.2692`.
- `atlas.tex:151-153` SOURCE comment, `median churn 0.138 -> 0.048 is a factor
  of 2.875`. Correct factor: 2.864.
- `atlas.tex:156` prose, "median churn falling from $0.138$ in S1".
- `atlas.tex:158` prose, "the understatement ratio barely moves: 5.31 in S1 and
  5.33 in S2". The 5.31 comes from the wrong numerator; corrected it is 5.27.

**Bearing on D4.** This changes what D4 actually is. The handoff describes 5.3x
as a ratio of rounded medians against a direct 5.22/5.19 and a pooled 5.40. The
fuller picture, all reproduced this session:

| derivation | value |
|---|---|
| S1, unrounded medians | 5.2232 |
| S2, unrounded medians | 5.1936 |
| S1, rounded medians as the paper does it, **corrected** | 5.2692 |
| S2, rounded medians | 5.3333 |
| S1, rounded medians **as printed** (0.138) | 5.3077 |
| pooled over all 1,707 cells | 5.4000 |
| median of per-cell ratios (n=1,562, zero-delta undefined) | 3.8452 |

So "both strata land at 5.3" (the `atlas.tex:130-131` justification for the
headline) rests on the mis-rounded S1 value. Corrected, the two strata land at
5.27 and 5.33 rounded, or 5.22 and 5.19 unrounded. The qualitative claim that
the ratio barely moves across a generational change in method **survives, and
is stronger unrounded** (5.22 against 5.19). The printed digits do not.

The headline itself is not destroyed: 5.3 remains a fair rounding of the two
stratum ratios computed the paper's way. But the specific printed quantities
0.138 and 5.31 are wrong, and they are the evidence the headline cites.

This is a numeric defect in a body table, not a change to the escalated D4
decision. It is reported, not fixed: D4 is escalated to the author and this sits
inside it.

### G1. Figure 1 panel D overflows the text block. SERIOUS.

`fig1_cancellation.tex:95`:

```
\node[font=\scriptsize, anchor=west] at (12.16,1.85) {\ \ $\bullet$ reversed};
```

`make_figure1.py:435` computes that x as `sx + 1.02 + 8 * 0.55 - 0.18`, i.e. one
dot-pitch past the eighth dot, with no width check. The figure is 12.6cm wide
and `\textwidth` at article 11pt is about 12.66cm.

`\ \ $\bullet$ reversed` at 8pt is roughly 1.6cm, so the label runs to about
**13.8cm**, past the panel border at 12.6 and past `\textwidth` by about 1.1cm.
Expect an overfull hbox and a label sitting in the right margin.

The generator has no clearance check on this node. The eight dots consume
`1.02 + 7 * 0.55 = 4.87cm` of the panel's 6.0cm before the legend starts.

### G2. Figure 1 panel B legend collides with the panel subtitle. MODERATE.

Panel B places its italic subtitle at y=9.12 and its colour legend at y=9.05,
**0.07cm apart**. Both are `anchor=west`, so y is the vertical centre of each
text box, and at 8pt each box is roughly 0.28cm tall. They will overlap
substantially.

The cause is in the generator: the subtitle y is derived from the panel top
(`ty + ph - 0.78`, `make_figure1.py:326`) but the legend y is derived from the
bar (`byy + 0.92`, `:348`), so the two are not coordinated. Panel A has no
legend and does not show the problem.

The `8.54\%` callout above the bar (anchor south at y=8.59) clears the legend,
just.

### G3. Figure 1 panel A accuracy labels overrun the panel border. MINOR.

`74.28\%` and `73.70\%` are `anchor=west` at x=5.38. At 8pt they are about
0.92cm wide, so they end near x=6.30 against a panel border drawn at x=6.00.
They will sit across that border, in the 0.6cm gutter. No collision with panel
B, which starts at 6.6, so this is cosmetic rather than an overfull box.

### S1. The abstract's measurement note is stale. MINOR.

`abstract.tex:106-112` still reads "NOT MEASURED for the 2026-08-05 flagship
rewrite ... RUN THE TOOL BEFORE SUBMITTING". It has since been measured:

```
ABSTRACT_CHARS 1864 / 1920  margin=56  words=281
```

The note should record that measurement. It also says the `12.7\times`
controlled churn ratio is the first thing to restore "if the real figure leaves
room". A margin of 56 characters does leave room, so that is now a live
decision rather than a conditional.

### S2. Prose rule 5 was applied to the front and back, not to the body.

Plan §9 rule 5 targets at most three `\textbf{}` spans per section. Counting
prose spans only, excluding table cells and captions:

| section | prose `\textbf` | |
|---|---|---|
| abstract | 0 | ok |
| introduction | 1 | ok |
| related_work | 2 | ok |
| limitations | 0 | ok |
| preregistration | 1 | ok |
| conclusion | 5 | close |
| certification | 5 | close |
| atlas | 7 | over |
| harness_sensitivity | 7 | over |
| audit | 14 | **over** |
| minigrid | 17 | **over** |

The pattern is clean: the sections Wave 2 *rewrote* comply, the sections it only
*restructured* were never given the pass. Body total is 93 spans against the
plan's starting count of 200.

Rule 2 (`registered`/`frozen`/`preregistered`, "once per section") is at 98
across the body against a starting ~120, concentrated in `audit.tex` (36) and
`minigrid.tex` (19). Some of those are load-bearing ("the registered 2 pp
margin"), so the count alone is not the defect; it is a candidate for the next
compression pass, not a finding.

---

## 2. What passed

**Check 1, numeric claims recomputed.** Every Figure 1 value reproduces exactly
from the committed artifacts:

- `results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json`: GPTQ 0.7428, AWQ
  0.7370, delta 0.0058, seed deltas +0.022 / +0.016 / -0.023 / +0.002 / +0.012.
- `results/h3_eight_cell/h3_eight_cell_summary.json`: verdict SUPPORTED, 5 of 8
  winner flips, 8 cells.
- `results/minigrid_supporting/minigrid_supporting.json`, slot4 cell mean for
  qwen25-7b/gsm8k: n=1,000, harmful 0.0912, beneficial 0.0854, churn 0.1766,
  answer churn 0.2866, net -0.0058.
- Churn-to-net ratios across the eight: 3.04, 6.07, 10.47, 11.72, 13.70, 15.31,
  17.96, **30.45**. The flagship cell is the maximum, median 12.708. The
  caption's `30.4\times` against `12.7\times` is correct and the claim that it
  is the most extreme of the eight holds.
- `results/identical_score_churn_rev2.csv`: 1,707 analysable, 145 zero-delta,
  128 of those with non-zero churn. Figure 1's atlas strip is correct.
- Panel C bar scale is proportional (1,000 and 2,730 on one linear axis).
- Internal arithmetic: 74.28 - 73.70 = 0.58; 8.54 - 9.12 = -0.58;
  8.54 + 9.12 = 17.66; 100 - 17.66 = 82.34. All as printed.

The one exception is D8 above.

**Check 2, is the flagship cell honestly presented.** Yes, in three places and
without hedging: `introduction.tex:63-64` ("the most extreme of the eight
registered cells and is shown because it is legible; all eight appear in
panel~D"), the figure caption's Scope sentence (which gives 30.4x against the
12.7x median), and `introduction.tex:75` ("One cell settles nothing about the
field, so we measured the public record"). All eight cells are plotted in panel
D, so a reader cannot mistake the example for the population. This was flagged
as the most likely real-reviewer attack and it is well defended.

**Check 3, does panel C or the abstract overstate certification.** No. The
"planning requirement at an assumed true difference of zero ... not evidence
that the methods differ" qualification appears in the panel C body text, in the
caption, and in the introduction. The abstract claims only that the paper
supplies the instrument and the item counts, and does not claim any audited
comparison was certified or refuted.

**Check 4, TOST corresponds to a 90% two-sided interval.** Correct at all six
sites: `audit.tex:366-370`, `certification.tex:69-70` and `:111-112`,
`appendix_audit_table.tex:88`, `:355`, `:384`. `appendix_prereg_detail.tex:285-301`
explains the choice. The single two-sided alpha in the body, `audit.tex:354`, is
V1 *detection*, which correctly takes the two-sided z, and `audit.tex:370` says
so explicitly. No 95% statement survives anywhere. Mandatory qualification 17 is
intact.

**Check 6, em dashes and stale claims.** Zero em dashes in prose across the
abstract, `main.tex`, all sections and the figure. Every `---` hit is a "no
value" table cell, which the rule permits. `check_paper.py` and the stale-claim
linter are clean, `verify_registrations.py` matches 7,103 words across four
documents, and `gen_denominator_macros.py --check` passes all three layers.

Prose rules 1 and 4 are met: "rather than" is down to 8 uses in the body against
a target of 10 and a starting count above 60; `\paragraph{}` is down to 3 from
44.

**Mandatory qualifications spot-checked after the restructure.** Q3
(task-matched, five homes), Q8 (43.6% descriptive, now a macro and still in the
same sentence as its framing), Q9 (the "robust means only across the atlas IQR"
sentence, the single point of failure, survives verbatim at `audit.tex:654-657`),
Q12 (R04 and R14 carry no verdict) and Q17 (TOST 90%) all survive. D7 is
correctly fixed: "one part in twelve **of that requirement**", and 172/2,010 =
1/11.7 supports the phrase.

---

## 3. Recommended disposition

1. **D8**: fix `tab:atlas-strata` to 0.137, and the two SOURCE comments and the
   prose 5.31 that depend on it. This is a mechanical correction to a printed
   number, but it touches the evidence for the 5.3x headline, so it belongs
   with the D4 decision rather than ahead of it.
2. **G1**: regenerate the figure with the panel D legend moved. Placing it under
   the dot row, or dropping it in favour of a caption sentence, both fit. The
   generator should gain a clearance assertion so this cannot recur silently.
3. **G2**: coordinate the panel B legend y with the panel top rather than the
   bar.
4. **G3**: optional. Move the panel A numbers inside the bar, or shorten the bar.
5. **S1**: update the abstract's measurement note, and decide whether to spend
   the 56-character margin on restoring `12.7\times`.
6. **S2**: a `\textbf` pass over `minigrid.tex`, `audit.tex`,
   `harness_sensitivity.tex` and `atlas.tex`, if the author wants rule 5 applied
   uniformly.

Nothing here changes a registered quantity, a frozen document or a signed
verdict. G1 to G3 are generator changes and would require the in-image gate and
a freeze refresh; D8 and S1 are `paper/` edits and do not.
