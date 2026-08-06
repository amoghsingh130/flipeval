# The zero-denominator policy for the churn-to-net-delta ratio

Written 2026-08-05, closing the second half of defect D4. The first half named
the aggregation (`docs/HEADLINE_CHURN_RATIO_DEFINITION.md`); this one settles
what happens to the cells for which one of the two aggregations is undefined,
and puts every affected number under a generator and a test.

Everything below is recomputed from the committed artifacts by
`scripts/churn_ratio.py` and pinned by `tests/test_churn_ratio.py`. No number
here is carried over from prose.

## 1. Where the problem arises, and where it does not

The paper quotes two aggregations, and only one of them can divide by zero.

| aggregation | formula | zero deltas |
|---|---|---|
| ratio of medians | `median(churn) / median(abs net delta)` | **no effect.** A zero delta is an ordinary value inside a median. Every cell contributes. |
| median of per-cell ratios | `median(churn_i / abs net delta_i)` | **undefined per cell.** Needs a stated policy. |

So the headline 5.40 is untouched by any of this. The exposure is confined to
the per-cell figure, 3.85, and to the controlled 12.7 that it is compared with.

`ratio_of_medians()` raises `ZeroDivisionError` if the *median* denominator is
zero, rather than returning infinity. A population that cancels at the median
has no ratio, and a silent `inf` would print as a headline.

## 2. The population, and how many cells are affected

Registered analysis population: 1,707 cells (S1 1,398, S2 309), after the two
registered exclusions. Zero-delta is **exact equality**, `abs(net delta) < 1e-12`,
with no rounding tolerance. That is not a new definition: it is the one
`docs/IDENTICAL_SCORE_CHURN_2026-07-21.md` and
`results/identical_score_churn_rev2.csv` already use for the 145 identical-score
cells reported in §`sec:atlas:identical`. A test asserts the strict and tolerant
readings select the same cells, so the two parts of the paper cannot drift apart.

| | cells | share |
|---|---|---|
| analysis population | 1,707 | |
| non-zero net delta, per-cell ratio defined | **1,562** | 91.5% |
| exactly zero net delta | **145** | 8.5% |
| ... of those, **with non-zero churn** | **128** | 7.5% of the population |
| ... of those, churn also zero (a true 0/0) | 17 | 1.0% |

By stratum, one rule applied identically:

| | cells | zero delta | share of stratum |
|---|---|---|---|
| S1 | 1,398 | 95 | 6.8% |
| S2 | 309 | 50 | 16.2% |

The policy does **not** differ by stratum. The *rate* does, and proportionally
more of S2 is removed, which is a fact about the data rather than a choice. It is
published rather than smoothed over.

## 3. The policy, and why it is the conservative one

**Reported policy (`ZeroPolicy.EXCLUDE`).** The per-cell median is taken over the
1,562 cells with a defined ratio. The paper states the denominator, states the
145, and cross-references the subsection that analyses them.

The obvious objection is that dropping 8.5% of the population could flatter the
result. It cannot, and the direction is worth being explicit about.

A cell with non-zero churn and an exactly zero net delta is the **most complete
cancellation the atlas contains**: behaviour changed and the aggregate did not
move at all. Its ratio does not fail to exist because the effect is absent, but
because the effect is total. Under any convention that readmits those 128 cells
they sort above every finite ratio, and the median can only rise:

| policy | cells in the median | atlas median |
|---|---|---|
| `EXCLUDE` (reported) | 1,562 | **3.85** |
| `EXTENDED` (128 readmitted as unbounded, 17 true 0/0 still dropped) | 1,690 | **4.20** |

So **3.85 is a lower bound** on the per-cell ratio under either treatment. The
reported figure is the smaller one. A future change that made the reported figure
the larger of the two would be a change in the paper's favour and would need
explaining; `test_readmitting_the_zero_delta_cells_raises_the_ratio` is where that
surfaces.

The 17 genuine 0/0 cells are dropped under both policies. Zero churn against zero
delta is undefined in every extended sense too, and is never quietly called zero.

## 4. The controlled regime uses the same policy, vacuously

All eight confirmatory cells have a non-zero net delta, so the per-cell
aggregation drops none of them: 8 of 8 enter the median, against 1,562 of 1,707
on the atlas side. The policy is identical; it simply has nothing to do.

That asymmetry is the reason the comparison needs stating rather than assuming,
and `tab:churn-aggregations` carries it as its last row.

## 5. The cross-regime comparison, both ways

| aggregation | atlas | controlled | contrast |
|---|---|---|---|
| ratio of medians | 5.40 | 12.14 | 2.2x |
| median of per-cell ratios | 3.85 | 12.71 | 3.3x |

**The direction survives the choice of aggregation**, which is the only reason the
comparison is reportable at all. Both are printed. The like-for-like pairing gives
the larger contrast, so quoting only that one would be selecting on the answer;
`test_the_direction_holds_under_both_aggregations` requires both to point the same
way, and the retired framing (atlas 5.3 ratio-of-medians against controlled 12.7
median-of-ratios) is exactly the mismatched pairing this replaces.

The two aggregations nearly agree in the controlled regime (12.14 against 12.71)
and diverge in the atlas (5.40 against 3.85). That is a consequence of dispersion,
not of policy: eight cells of similar size behave like their own median, while
1,707 heterogeneous cells do not.

## 6. What is now generated rather than typed

`scripts/churn_ratio.py` computes every value the paper prints for this quantity
and `--check` verifies 25 of them against the manuscript in one pass.
`tests/test_churn_ratio.py` adds 23 tests covering the population, both
aggregations, both zero policies, the stratum split, the cross-regime direction,
and the failure modes.

This closes the root cause recorded as Recommendation 4 of
`docs/HEADLINE_CHURN_RATIO_DEFINITION.md`: before today this number existed only
as arithmetic inside a LaTeX comment, and it rotted twice, as D8 (a median
hand-copied as 0.138 for 0.13745229) and D4 (two rounding conventions in one
sentence). The project already forbids hand-typing audit counts for this reason;
the atlas ratio is now held to the same rule.

The generator caught three incorrect pinned values during its own construction,
which were mine, computed by hand from the rounded table. That is the argument
for it in one line.

## 7. What this document does not change

No accuracy figure, no registered quantity, no verdict, and no public artifact.
The population, the exclusions and the per-cell metrics are all as registered;
only the aggregation and the zero-denominator handling are settled here, and both
were always outside the registrations. Nothing here is a reason to re-upload, to
touch the source tarball, or to amend a frozen document.
