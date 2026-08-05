# The headline churn-to-net-delta ratio: definition, candidates, and recommendation

Written 2026-08-05 to resolve defect D4 before any headline ratio is changed.
Everything below is recomputed this session from the committed artifact; no
number is carried over from prose.

## 1. The finding that decides this

**No frozen registration defines this ratio.** Checked, in full:

| document | what it says about the ratio |
|---|---|
| `PREREGISTRATION.md` | nothing |
| `docs/ATLAS_MINING_REGISTRATION_2026-07-15.md` | nothing |
| `docs/MINIGRID_REGISTRATION_2026-07-15.md` | nothing |
| `docs/AUDIT_REGISTRATION_2026-07-15.md` | nothing |

The atlas registration §5 registers the **per-cell** metrics ("net accuracy
delta, harmful/beneficial flip rates, accuracy-state churn, total answer churn
where raw predictions exist, ..."). §6 registers only that "aggregates over
cells are accompanied by the cell count and the exclusion table" and that probe
cells "appear in the atlas but not in headline aggregates".

So the registration fixes the **inputs** and the **population**, and is silent
on the **aggregation**. The ratio is a post-hoc descriptive summary. The
instruction to "follow the registered definition rather than choosing the most
favorable value" therefore cannot be executed literally: there is nothing to
follow. What follows instead is the rule the registration *does* impose, which
is the population, plus a choice of aggregation that has to be made openly and
stated in the paper.

## 2. Population and exclusions, which *are* registered

Every candidate below uses the same analysis population, and no candidate is
allowed to differ on it:

```
results/atlas_cells_summary_rev2.csv
  excluded_or_skipped == False
  contains_disclosed_probe_cell == False
  net_accuracy_delta non-empty
    -> 1,707 cells   (S1 = 1,398, S2 = 309)
```

The 99 disclosed probe cells are excluded by registration §1 and §6. The 1,807
figure is pipeline accounting and is never an analysis denominator.

## 3. Every candidate value

Numerator is a median over cells; denominator is a median of the **absolute**
net accuracy delta over the same cells. `churn` below means
`accuracy_state_churn` unless stated.

| value | formula | population | aggregation |
|---|---|---|---|
| **5.4000** | median(churn) / median(abs net) | all 1,707 | ratio of pooled medians, unrounded |
| 5.4545 | round(median churn,3) / round(median abs net,3) | all 1,707 | ratio of pooled medians, rounded first |
| 5.2232 | 0.137452 / 0.026316 | S1, 1,398 | ratio of stratum medians, unrounded |
| 5.1936 | 0.048000 / 0.009242 | S2, 309 | ratio of stratum medians, unrounded |
| 5.2692 | 0.137 / 0.026 | S1, 1,398 | ratio of stratum medians, **rounded to 3dp first** |
| 5.3333 | 0.048 / 0.009 | S2, 309 | ratio of stratum medians, **rounded to 3dp first** |
| 3.8452 | median(churn / abs net) per cell | 1,562 of 1,707 | median of per-cell ratios |
| 7.4125 | mean(churn / abs net) per cell | 1,562 of 1,707 | mean of per-cell ratios |
| 13.5000 | median(total answer churn) / median(abs net) | all 1,707 | different numerator, see §6 |

The per-cell aggregations drop the 145 zero-delta cells, for which the ratio is
undefined. That is not a free choice: those cells are the subject of
§`sec:atlas:identical`, and any aggregation that silently discards them is
discarding the paper's own strongest example.

**5.3 is not on this list.** No unrounded derivation produces it. It arises only
from the round-to-3dp-then-divide path, and only as an eyeball average of the
two stratum values that path gives (5.2692 and 5.3333). Rounding the inputs
before dividing throws away precision for no reason and is what produced the D8
defect corrected earlier today, where the S1 numerator had additionally been
mis-rounded from 0.137452 to 0.138, yielding 5.3077 and the printed "5.31".

## 4. Generating script and artifact

- Artifact of record: `results/atlas_cells_summary_rev2.csv`, one row per cell,
  columns `accuracy_state_churn`, `total_answer_churn`, `net_accuracy_delta`,
  `excluded_or_skipped`, `contains_disclosed_probe_cell`, `source`.
- The per-cell quantities are computed by `flipeval/core.py::compute_pair_metrics`.
- **No committed script computes the headline ratio.** It has only ever existed
  as arithmetic in a `% SOURCE:` comment. That is the root cause of D4 and D8
  both: a number with no generator cannot be regression-tested, and the paper's
  own rule is "never hand-type an audit count" for exactly this reason.
  **Recommendation 4 below fixes this.**

## 5. Every occurrence

### Manuscript, compiled prose (the atlas headline)

| file | line | text |
|---|---|---|
| `abstract.tex` | 58 | `churn runs $5.3\times$ the net accuracy delta` |
| `sections/introduction.tex` | 77 | `puts churn at $5.3\times$ the net delta` |
| `sections/atlas.tex` | 147 | `runs \textbf{5.3 times the net accuracy delta}` |
| `sections/atlas.tex` | 158 | `5.27 in S1 and 5.33 in S2` (corrected today, D8) |
| `sections/minigrid.tex` | 240 | `\textbf{$5.3\times$} net delta` |
| `sections/conclusion.tex` | 78 | `churn runs $5.3\times$ the net delta` |
| `sections/conclusion.tex` | 111 | `against the atlas's $5.3\times$` |

### Figure

`paper/figures/fig1_cancellation.tex` says **"about five times"**, deliberately,
and `tests/test_figure1.py::test_emitted_tikz_never_prints_the_disputed_ratio`
fails the build if any spelling of 5.3 enters it. That test should stay.

### Public surfaces

| surface | says | needs correction? |
|---|---|---|
| `paper/blog/2026-07-21-...md:121` | "per-item churn runs roughly **five times** the net accuracy delta" | **No.** Compatible with every candidate in the 5.19 to 5.45 band. |
| `README.md:30` (GitHub, public) | "**answer** churn runs about 5.3x the net accuracy delta" | **Yes, and for a second reason.** See §6. |
| Zenodo v1.0 release | `docs/RELEASE_CHECKLIST_v1.0.0.md` asserts no ratio anywhere; the release ships the raw per-cell CSVs, which contain no aggregate | **No.** |

**This materially shrinks the D4 problem.** Previous handoffs recorded that 5.3x
"is public in the Zenodo release and the published blog post" and that
correcting the paper alone would desynchronise the released record. That is not
the case. The blog hedges to "roughly five times", and the Zenodo release
asserts no ratio at all. The only public assertion of an exact value is the
README, which is a repository file and can be corrected in place without any
DOI, versioning or upload action.

### Not this quantity, do not "harmonise"

`sections/certification.tex:136` and `sections/appendix_audit_table.tex:370,399`
each print `$5.3\times$` in an **ifeval** row. That is the paired-versus-naive
sample-size advantage for that benchmark family, 4,211 / 800 = 5.26. It is a
different quantity that coincidentally rounds to the same two digits. Leave it
alone, and do not let a search-and-replace touch it.

## 6. A second defect in the README, independent of D4

`README.md:30` attributes the ratio to **answer churn**. The 5.3 (really 5.40)
figure is computed from `accuracy_state_churn`. The answer-churn ratio over the
same 1,707 cells is:

```
median(total_answer_churn) / median(abs net_accuracy_delta)
  = 0.300000 / 0.022222 = 13.5000
```

So the README understates its own named quantity by a factor of about 2.5, on a
public repository. This is a naming error rather than an arithmetic one: the
number belongs to a real quantity, just not the one the sentence names. It
should be fixed whichever way D4 is resolved.

## 7. Recommendation

**Adopt the ratio of pooled medians over the 1,707-cell analysis population,
unrounded, as the canonical definition: 5.40.**

Reasons, in order:

1. It uses the population the registration does fix, and the same population as
   every other atlas statistic in the paper. Nothing about it is chosen to
   flatter the result.
2. It involves no rounding of inputs. Every defect this number has had, D4 and
   D8, came from rounding before dividing.
3. It is one number, not a pair, so it cannot drift between strata the way the
   printed 5.31/5.33 did.
4. It is not the largest candidate available (7.41 is), nor the smallest (3.85),
   so adopting it is not a choice of the most favorable value.

**Consequences, stated plainly:**

- The headline becomes **5.4x**, not 5.3x. Six manuscript sites change.
- **"Approximately 5.3x" may not remain.** The instruction permits it only if
  the canonical calculation supports that rounding, and 5.4000 rounds to 5.4.
  The hedge "about five times" *is* supported and is already what the figure and
  the blog say; adopting it everywhere is the lower-risk option and is my second
  choice if a single unhedged digit is not wanted.
- **The per-cell median, 3.85, must be disclosed** in the atlas section, not
  buried. A reader who hears "churn runs 5.4 times the net delta" will
  reasonably picture the typical cell, and the typical cell's ratio is 3.85. The
  gap between 5.40 and 3.85 is the difference between a ratio of medians and a
  median of ratios, it is large, and disclosing it costs one sentence. Failing
  to disclose it is the kind of thing this paper audits other people for.
- The S1/S2 preservation claim survives and gets stronger: unrounded, the two
  strata are 5.2232 and 5.1936, which are closer together than the rounded
  5.2692 and 5.3333 the paper currently prints.

**Recommendation 4: give the number a generator.** Add the ratio to a committed
script that reads `atlas_cells_summary_rev2.csv` and emits every candidate in
§3, with a test pinning the canonical one, exactly as
`paper/tools/gen_denominator_macros.py` does for the audit counts. The paper's
own rule against hand-typed counts exists because hand-typed counts rot, and
this number has now rotted twice.

## 8. On the public record

No upload, no DOI action and no v1.1 bundle is required, because no released
artifact asserts an exact ratio. What is needed is a correction to `README.md`
in the repository, covering both the value and the answer-churn/accuracy-state
churn misnaming of §6.

If a v1.1 note is later wanted for completeness, it should say that v1.0
asserted no ratio and that the repository README, which is not part of the
deposited bundle, carried an incorrect one. **Nothing here is a reason to
rewrite history, re-upload, or touch the source tarball.**

## 9. What has not been done

This document does not change any value. The six manuscript sites still say 5.3
and `atlas.tex` still prints the per-stratum pair. **The change is deliberately
left for the author**, because it moves the paper's most repeated headline and
because the choice between "5.4x" and "about five times" is an editorial one
that the analysis above narrows but does not settle.
