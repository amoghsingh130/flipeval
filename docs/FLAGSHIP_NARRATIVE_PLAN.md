# Flagship narrative plan, 2026-08-04

The committed instruction set for the flagship revision. Three Wave-1 analysis
agents produced independent reports; this document reconciles them and is what
the implementation agents follow. Where the reports disagreed, the reconciliation
below is what governs.

Branch: `flagship-narrative`, worktree `.claude/worktrees/flagship`, based at
`bcc1afc`. Nothing here is pushed.

**A concurrent agent session was editing the parent worktree while this branch
was cut.** That is why the work is isolated. Run `git log` before assuming HEAD
is yours.

---

## 1. The thesis

> A small aggregate accuracy gap is not evidence that two models are
> interchangeable, because opposing item-level changes cancel. Paired
> certification reveals the hidden change and whether an evaluation can actually
> support equivalence.

Five linked steps, and every main section must advance one of them:

1. **Mechanism.** Harmful and beneficial item-level changes cancel in aggregate
   accuracy.
2. **Scale.** The 1,707-cell public atlas shows this is not isolated.
3. **Reporting gap.** Audited sources generally omit prospective margins and
   task-matched item-level evidence.
4. **Practical consequence.** Calibration-sample randomness can change which
   compression method appears better.
5. **Solution.** Declare a margin, measure churn, use paired equivalence
   testing, meet the planning requirement, release per-item outputs.

The audit supports this narrative. It is not a paper claiming widespread
falsehood, and it is not a paper claiming robust widespread underpowering.

### Three-sentence summary a reviewer should be able to retell

Compressed models are declared equivalent to their originals on the strength of
a fraction of a point of aggregate accuracy, but a net delta is only the residue
left after harmful and beneficial per-item changes cancel, and cancellation is
most complete in exactly the near-identical regime an equivalence claim occupies.
Across an atlas of 1,707 paired model-by-task cells mined from public per-item
evaluation dumps, per-item churn runs several times the net delta and 145 cells
post a numerically identical score while still disagreeing on individual items,
while a preregistered audit of 16 eligible published equivalence claims finds
that none declares a prospective numerical margin and none releases task-matched
per-item outputs, so a reader cannot check them at any sample size. The paper
supplies the missing instrument, equivalence testing at a declared margin with
required-item counts computed from observed churn rather than
independent-binomial variance, and a preregistered controlled experiment shows
the problem is worse where practitioners actually choose, because pairing GPTQ
and AWQ on byte-identical calibration samples reversed the observed method
ordering in 5 of 8 registered cells.

---

## 2. Verified defects found during Wave 1

These were found by recomputation against committed artifacts, not by reading
prose. Each has a disposition. **No implementation agent may change a disposition.**

### D1. `certification.tex` cites two rev-1 numbers. FIX.

`certification.tex:206-213` states GPQA median baseline `0.373` against MMLU's
`0.390`, and MMLU discordance `0.137` against GPQA's `0.048`.

Checked against `results/certification_tables_rev2.csv`: GPQA baseline `0.3734`
is right, but MMLU baseline is **`0.4923`** and MMLU `discordance_median` is
**`0.14`**. Both wrong values are exactly the rev-1 entries in
`results/certification_tables.csv` (`0.39`, `0.13733`). The section's own
`tab:certification` already prints the rev-2 values, so the section contradicts
its own table.

This is the sixth rev-1 survivor found on this project. **Fix it**, and note in
the SOURCE comment that it is a rev-1 survivor, matching the convention at
`atlas.tex:129-136`. The conceptual argument survives and strengthens: a larger
baseline-accuracy gap makes "difficulty is not what sets the requirement" more
striking, and `0.14 / 0.048397 = 2.89` still supports "nearly three times".

### D2. The atlas parameter range understates its own population. FIX.

Three sites say the atlas spans "3B to 405B": `abstract.tex:63`,
`introduction.tex:88`, `atlas.tex:138`.

Parsing base-model names over the 1,707-cell analysis population gives
`{1.3, 3, 7, 8, 13, 20, 30, 33, 70, 405}`B, with **60 cells on
`EleutherAI/gpt-neo-1.3B`**. The floor is 1.3B.

**Fix all three sites to 1.3B.** Watch the abstract character budget.

### D3. "The ratio holds at every scale represented" is disconfirmed. FIX.

`atlas.tex:137-139` claims the churn-to-net-delta ratio "holds at every scale
represented, from 3B to 405B parameters".

Per-scale median ratios over the analysis population:

| params | cells | median churn | median abs net delta | ratio |
|---|---|---|---|---|
| 1.3B | 60 | 0.0880 | 0.0112 | 7.88 |
| 3B | 181 | 0.1327 | 0.0184 | 7.21 |
| 7B | 426 | 0.2077 | 0.0453 | 4.59 |
| 8B | 78 | 0.0600 | 0.0109 | 5.49 |
| 13B | 487 | 0.1250 | 0.0245 | 5.09 |
| 20B | 58 | 0.1845 | 0.0208 | 8.88 |
| 30B | 1 | 0.3442 | 0.3442 | 1.00 |
| 33B | 2 | 0.1043 | 0.0308 | 3.39 |
| 70B | 176 | 0.0536 | 0.0126 | 4.25 |
| 405B | 114 | 0.0400 | 0.0081 | 4.96 |

The ratio does not hold at every scale. It varies by roughly a factor of two
across strata with meaningful n, and a single-cell 30B stratum gives 1.00.

**Delete the "holds at every scale" clause.** Replace with what is supported:
the ratio is well above one in every stratum with more than two cells, and the
two registered strata (S1, S2) give the near-identical values the section
already reports. Do not substitute a new numeric claim about scale invariance.

### D4. The 5.3x headline is a ratio of rounded medians. ESCALATED, DO NOT CHANGE.

`atlas.tex:126-128` derives the headline as `0.138 / 0.026 = 5.3077` (S1) and
`0.048 / 0.009 = 5.3333` (S2), dividing the values as printed in
`tab:atlas-strata`.

Recomputed from `results/atlas_cells_summary_rev2.csv` over the 1,707-cell
analysis population:

| stratum | median churn | median abs net delta | direct ratio | ratio of printed values |
|---|---|---|---|---|
| S1 (1,398) | 0.137452 | 0.026316 | **5.2232** | 5.2692 |
| S2 (309) | 0.048000 | 0.009242 | **5.1936** | 5.3333 |
| pooled (1,707) | 0.120000 | 0.022222 | **5.4000** | |

Two separate problems. First, `tab:atlas-strata` prints S1 median churn as
`0.138`, but `0.137452` rounds to `0.137`; the `0.1375` recorded in
`docs/ATLAS_REV2_CORRECTION_2026-07-21.md` was already a rounding, and `0.138`
is a second rounding of it. Second, neither stratum's direct ratio rounds to
5.3.

**This is escalated to Amogh and is not changed on this branch.** The headline
appears in `abstract.tex`, `introduction.tex`, `atlas.tex`, `minigrid.tex` and
`conclusion.tex`, and it is public in the Zenodo release and in the published
blog post, so correcting it in the paper alone would desynchronise the released
record. Implementation agents:

- **Do not change any existing 5.3x site's value.** Reduce repetition only.
- **Do not introduce 5.3x anywhere new**, including Figure 1.
- Where a new sentence needs the fact, write it as "median churn is about five
  times the median net accuracy delta", which is true under every derivation
  (5.19 to 5.40) and asserts no false precision.

### D5. `tab:audit-sensitivity` hand-types its counts. FIX.

`audit.tex:484-486` types `10`, `1`, `0` instead of `\AuditAboveThroughout`,
`\AuditChangesWithinIQR`, `\AuditBelowThroughout`. This violates the project's
own rule that no section types an audit count, which is the rule that exists
because the retired "4 of 12" headline outlived the verdicts that produced it.
Replace with the macros.

### D6. `sec:audit:locus` hand-types its tier counts. FIX IF CHEAP, ELSE LEAVE.

`audit.tex:225-228` records in a comment that the 3 / 2 / 1 tier counts and the
six-card denominator are typed by hand. They belong in
`paper/tools/gen_denominator_macros.py`. Do not add a second generator. If the
locus table moves to an appendix and the counts survive only as prose, macro-ise
them there. If this cannot be done without touching the generator's validated
three-layer check, leave the comment in place and report it as still open.

### D7. `minigrid.tex:504` "one part in twelve". CHECK ON REWRITE.

For R01, `172 / 2010 = 8.6%`, one part in 11.7 of the requirement, but
`172 / 1838` is one part in 10.7. The sentence reads correctly against
`n_req` and incorrectly against `n`. If that sentence is rewritten, make the
denominator explicit.

---

## 3. Open questions carried, not resolved

- **Geometry.** `paper/main.tex:14` is `\documentclass[11pt]{article}`, but
  `docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md` mandates the unmodified TMLR
  style for submission, and no `tmlr.sty` is in the tree. The same content is
  about 58 pages in article geometry and about 30 in TMLR geometry. The 12 to 16
  page target is met at TMLR geometry after the program below; in article
  geometry the same program lands near 21. **Both estimates are reported. No
  page count is measured, because there is no LaTeX on this machine or in the
  pinned image.**
- **R09 / R17 eligibility** remains unsigned (`SESSION_HANDOFF_2026-08-03` §3).
  Denominators are not touched. The `\paragraph{The boundary cases were kept.}`
  content must survive somewhere, because it is the only record of the retention
  judgement.
- **D4 above.**

---

## 4. Target main-body structure

Reordered so the paper runs mechanism, scale, gap, consequence, solution. The
most consequential reordering is that **the atlas now precedes the audit**,
which also repairs a live logical defect: the audit's discordance imputation is
defined over the atlas, but the atlas currently appears two sections after the
audit that consumes it.

| § | Title | Steps served |
|---|---|---|
| 1 | Introduction, with Figure 1 | 1, and a map of 2 to 5 |
| 2 | Related work and positioning | context |
| 3 | Paired certification: what an equivalence claim has to show | 1, 5 |
| 4 | The atlas: cancellation at scale, and what certification costs | 2, 5 |
| 5 | What published equivalence claims actually report | 3 |
| 6 | Cancellation is worse where practitioners choose | 4 |
| 7 | A reporting standard, its limits, and the artifacts | 5 |

`sections/discriminant.tex` is folded into §6 and deleted.
`sections/minigrid_escalation.tex` moves whole into a new mini-grid appendix and
is deleted from the body.

Appendix order after the move:

```
A  appendix_related_detail.tex     (new)
B  appendix_prereg_detail.tex
C  appendix_audit_table.tex
D  appendix_atlas_detail.tex
E  appendix_minigrid_detail.tex    (new)
F  appendix_harness_detail.tex
G  appendix_artifacts_detail.tex
H  appendix_extraction.tex
I  appendix_registrations.tex      IMMUTABLE, GENERATED, LAST
```

---

## 5. The ordered compression program

Relocations first, nothing deleted; prose compression second. Page figures are
article-11pt estimates with a +/-12% band, skewed high.

| # | Operation | Save |
|---|---|---|
| 1 | `related_work.tex:84-164` (Paglieri reconciliation) to appendix A | 1.89 |
| 2 | `minigrid_escalation.tex` whole file to appendix E | 2.05 |
| 3 | `minigrid.tex:195-348` three supporting tables to appendix E, consolidated to one | 2.37 |
| 4 | `preregistration.tex` §§3.2, 3.4, 3.5 and `tab:freeze-timeline` to appendix B | 1.73 |
| 5 | `preregistration.tex:204-250` spot-check narrative to appendix B, one sentence kept | 0.77 |
| 6 | `tab:audit-mdd` consolidated into appendix C `tab:audit-power` | 0.58 |
| 7 | `tab:audit-locus` to appendix C, finding stays as prose | 0.32 |
| 8 | `tab:identical-extreme` becomes a Figure 1 panel; table deleted | 0.43 |
| 9 | `tab:h3-ds` to appendix E | 0.41 |
| 10 | `tab:h3-resolution` to appendix E | 0.26 |
| 11 | `tab:sensitivity-mmlu` consolidated into one harness table | 0.24 |
| 12 | `discriminant.tex` folded into §6; pilot to appendix E; file deleted | 0.84 |
| 13 | `minigrid.tex:478-490` deferred analyses to appendix E | 0.35 |
| 14 | `audit.tex` V1/V3/robustness detail to appendix C; §4.8 K-history to appendix B | 0.95 |
| 15 | `atlas.tex` construction detail to appendix D; harness design and Bronder to appendix F; artifact digest limits to appendix G | 3.05 |
| 16-26 | Prose compression per the per-section table in §6 | ~21 |

Nothing above reduces a font, narrows a margin, shrinks a table, or drops a
table column. The four retained `\small` tables stay `\small`; the retained
full-size tables stay full size.

Resulting body floats: **seven**. Figure 1, `tab:audit-taxonomy`,
`tab:audit-sensitivity`, `tab:certification`, `tab:atlas-strata`,
`tab:h3-eightcell`, and the consolidated `tab:sensitivity`.

---

## 6. Per-section compression targets

Article-11pt page estimates, before and after.

| Section | File | Now | Target |
|---|---|---|---|
| Abstract | `abstract.tex` | 0.82 | 0.75 |
| 1 Introduction | `introduction.tex` | 2.67 | 1.40 + 0.50 figure |
| 2 Related work | `related_work.tex` | 5.60 | 0.85 |
| 3 Preregistration, folded into the framework section | `preregistration.tex` | 4.36 | 0.60 |
| 4 Audit | `audit.tex` | 12.28 | 3.60 |
| 5 Certification | `certification.tex` | 4.46 | 1.75 |
| 6 Atlas | `atlas.tex` | 5.40 | 1.50 |
| 7 Mini-grid | `minigrid.tex` + escalation | 11.43 | 2.50 |
| 8 Harness sensitivity | `harness_sensitivity.tex` | 2.62 | 0.55 |
| 9 Discriminant | `discriminant.tex` | 0.99 | 0.00 |
| 10 Artifacts | `artifacts.tex` | 2.55 | 0.50 |
| 11 Limitations | `limitations.tex` | 2.64 | 0.85 |
| 12 Conclusion | `conclusion.tex` | 1.66 | 0.95 |
| **Body total** | | **57.8** | **~21** |

At TMLR single-column geometry the same end state is about **11 to 12 pages**,
and the mid-program stopping point (after operation 21 of Agent C's ordering) is
about 15. **Neither number is measured.**

---

## 7. Cross-reference migration

Every moved `\label` and every site that points at it. Execute mechanically and
then confirm with `python3 paper/tools/check_paper.py` reporting 0 dangling refs.

| Moved label | New home | Pointing sites to repair |
|---|---|---|
| `tab:freeze-timeline` | appendix B | none; add one body pointer |
| `tab:audit-locus` | appendix C | `audit.tex:314` |
| `tab:audit-mdd` | merged into `tab:audit-power` | `audit.tex:566`, `appendix_prereg_detail.tex:165`, `:171` |
| `tab:identical-extreme` | deleted, becomes `fig:cancellation` | `atlas.tex:288` |
| `tab:h3-ds` | appendix E | `minigrid.tex:138` |
| `tab:h3-variance` | appendix E `tab:h3-supporting` | `minigrid.tex:210`, `:429` |
| `tab:h3-bootstrap` | appendix E `tab:h3-supporting` | `minigrid.tex:257` |
| `tab:h3-flips` | appendix E `tab:h3-supporting` | `minigrid.tex:317`, `:406`, `:413` |
| `tab:h3-resolution` | appendix E | none; add pointer at `minigrid.tex:426` |
| `tab:minigrid-escalation` | appendix E | internal, travels with the file |
| `tab:sensitivity-gsm8k`, `tab:sensitivity-mmlu` | merged to `tab:sensitivity` | `harness_sensitivity.tex:93` |
| `sec:minigrid:escalation` | appendix E `app:escalation` | `minigrid.tex:80`, `preregistration.tex:201` |
| `sec:related:reconcile` | appendix A `app:reconcile` | `minigrid.tex:399`, `related_work.tex:82` |
| `sec:prereg:choices` | appendix B, label already exists | `audit.tex:400`, `:721`, `certification.tex:80`, `appendix_audit_table.tex:239` |
| `sec:prereg-spotcheck` | appendix B, label already exists | `atlas.tex:95`, `limitations.tex:147`, `appendix_artifacts_detail.tex:91` |
| `sec:minigrid:supporting` | appendix E | `limitations.tex:86` |
| `sec:discriminant` | deleted with the file | none; remove the `\input` in `main.tex` |

Labels with zero reference sites that may be dropped when their subsection is
folded away: `sec:prereg:contact`, `sec:prereg:discipline`, `sec:prereg:h3rule`,
`sec:prereg:timeline`, `sec:atlas:construction`, `sec:atlas:population`,
`sec:atlas:grayzone`, `sec:cert:method`, `sec:cert:table`,
`sec:cert:churn-not-difficulty`, `sec:cert:caveats`, `sec:minigrid:scope`,
`sec:minigrid:percell`, `sec:minigrid:churnratio`, `sec:audit:locus`,
`sec:related`, `sec:intro`, `res:churnratio`.

**Caution.** `sec:minigrid:churnratio` and `sec:audit:taxonomy` are cited in
`% SOURCE:` comments at `abstract.tex:39-40`, `:61` and `introduction.tex:96`.
Those are comments and will not break the build, but a comment pointing at a
deleted label is exactly the class of stale pointer this project's linter
exists to catch. Update them in the same commit.

Labels that must survive because they are referenced from outside their block:
`sec:audit`, `sec:atlas`, `sec:certification`, `sec:minigrid`, `sec:prereg`,
`sec:sensitivity`, `sec:artifacts`, `sec:conclusion`, `sec:limitations`,
`sec:atlas:identical`, `sec:atlas:netgross`, `sec:atlas:caveats`,
`sec:audit:taxonomy`, `sec:audit:results`, `sec:audit:rules`, `sec:audit:v3`,
`sec:audit:r04`, `sec:audit:indeterminate`, `sec:minigrid:verdict`,
`sec:minigrid:selfaudit`, `sec:minigrid:resolution`, `eq:sds`, `eq:nreq`,
`eq:tost-n`. Where a compressed subsection loses its heading, keep the `\label`
attached to the surviving paragraph. `sec:audit:v3` is referenced from
`artifacts.tex:36` and must not evaporate.

---

## 8. Qualifications that must survive, and where they are at risk

Seventeen mandatory qualifications, their current homes, and the operation that
threatens each. **A compression that removes one of these is a defect, not a
saving.**

| # | Qualification | Homes | Danger |
|---|---|---|---|
| 1 | 17 frozen candidates, 16 eligible after the registered exclusion | `audit.tex:96-100`, `:150-159`; abstract; intro; conclusion; `limitations.tex:62` | Both numbers are load-bearing and must not collapse into one |
| 2 | No eligible source declares a prospective numerical equivalence margin | `audit.tex:194-208`; `tab:audit-taxonomy` | The empty prospective column is the evidence. Do not move that table |
| 3 | No eligible source releases **task-matched** per-item outputs; three release for other tasks only | `audit.tex:330-349`; abstract; intro; conclusion; `artifacts.tex:37-40` | "task-matched" must stay in the same sentence as the zero, or the sentence is false |
| 4 | Five non-assessable: four insufficient reporting, one outside the registered binary paired-outcome calculation | `audit.tex:614-654`; `limitations.tex:119-126` | Keep the explicit 4+1 split. Never write "incompatible with a paired framework": it is the flip model that does not apply, not pairing |
| 5 | Eleven assessable at the registered uniform 2 pp margin | `audit.tex:374-377`, `:453-459` | `:374-377` is the logical hinge of the section and sits inside a block compressed 70%. Retain verbatim |
| 6 | Ten above throughout, one changes within, zero below throughout | `tab:audit-sensitivity`; `audit.tex:515-521` | Keep "no assessable claim falls below the threshold throughout the interval". See D5 |
| 7 | The sensitive claim is not robustly underpowered | `audit.tex:456-459`, `:509-513`, `:702-707` | `:702-707` is the only outright statement. If §4.9 merges, it must land in the surviving close |
| 8 | The 43.6% is a descriptive share of reference cells, not a probability | `audit.tex:506`, `:510-513` | Keep the number and its disclaimer in the same sentence, or cut the number |
| 9 | "Robust" means only stable across the stated atlas-IQR interval | `audit.tex:714-717` | **Single point of failure.** Not restated anywhere else in the body |
| 10 | The audit evaluates evidential sufficiency, not truth | `audit.tex:117-127`, `:702-707`; abstract; intro; `limitations.tex:64-65` | Five homes, robust. Keep at least two |
| 11 | The audited sample is not a prevalence estimate for the literature | `audit.tex:712-714`; intro; conclusion; `limitations.tex:59-64` | At least two must survive, and one must be in §4 or §11 |
| 12 | R14 stays non-assessable and does not enter K | `audit.tex:624-636`, `:560-573` | Moving `tab:audit-mdd` removes the italicised no-verdict rows. The trap paragraph must stay in the body and "R04 and R14 carry no verdict" must re-attach to surviving prose |
| 13 | Claim-derived margins and the old shortfall range are withdrawn | `audit.tex:374-377`, `:677-694`; `preregistration.tex:127-144` | The K = 1 to 5 to 4 to 1-of-11 sequence is the body's canonical self-correction and must not move to an appendix |
| 14 | The controlled experiment is 8 cells, 2 tasks, 2 methods, 4 models, 4 bits, 5 seeds | `limitations.tex:74-80`; `minigrid.tex:31-35`, `:122-127` | Keep the enumeration intact including what it licenses no statement about. Compress around it |
| 15 | GSM8K is under-resolved; MMLU carries the stronger evidence | `minigrid.tex:426-445`; `limitations.tex:96-110`; and two homes being deleted or moved | `minigrid.tex:432-438` and `limitations.tex:100-110` must both survive |
| 16 | The atlas is observational and establishes no population-wide causal claim | `atlas.tex:52-54`, `:318-324`, `:340-344`; `limitations.tex:12-15` | `atlas.tex:318-319` is retain-verbatim |
| 17 | TOST at one-sided alpha .05 corresponds to a 90% two-sided confidence interval | `audit.tex:392-396`; `certification.tex:65-67`, `:79-81` | Both body homes are being compressed. This was corrected on 2026-07-31 from a wrong 95% statement. `certification.tex:65-67` is retain-verbatim |

Additional protected passages, by project record rather than by the mandatory
list: `related_work.tex:43-46` and its SOURCE comment (the no-priority-claim
statement, author-affirmed, verbatim); `audit.tex:692-694`;
`audit.tex:105-115` (the two extraction passes are automated and **not**
statistically independent, and must never be described as inter-rater
verification); `audit.tex:309-315` (author re-verification, not independent
verification); `artifacts.tex:87-96` ("their full-text captures are in no
release"); `minigrid.tex:380-385` ("two measured points, not a curve") and
`:395-401` (the post-hoc disclosure); `harness_sensitivity.tex:155-173`;
`atlas.tex:89-96`.

---

## 9. Prose rules

Derived from what Wave 1 found in the current draft.

1. **"Rather than" appears 60+ times in body prose.** It does the same
   rhetorical job every time: asserting that the honest option was taken.
   Target: no more than ten uses in the whole body. Rewrite each to a plain
   declarative.
2. **"Registered", "frozen" and "preregistered" appear about 120 times in body
   prose.** Say it once per section, at the point where the reader needs to know
   a quantity was fixed in advance. Everywhere else the framework section and
   the appendix carry it.
3. **Delete self-justification.** The paper argues for its own virtue in at
   least seventeen places. Representative: "An audit paper is only as good as its
   own protocol discipline"; "Three points follow, and none is that we were
   unlucky"; "We state the limit of the exercise before its results"; "We state
   this carefully because an earlier revision of this work overstated it"; "None
   of them modifies the verdict, and none can"; "This does not weaken the
   verdict"; "the judgement is recorded rather than buried". Keep the underlying
   fact, delete the argument for it. `minigrid.tex:462-465` records a previous
   pass making exactly this correction; apply the same rule everywhere.
4. **44 `\paragraph{}` microheadings in the body.** The introduction had its
   eight removed on 2026-07-31 because "they made every paragraph read as an
   item in a generated executive summary". Extend that ruling. `limitations.tex`
   has ten consecutive ones and becomes two paragraphs.
5. **200 `\textbf{}` spans in the body.** The abstract had all six removed for
   the same reason. Target: no more than three per section, reserved for the
   section's single headline quantity.
6. **Delete the three near-identical "what this section does and does not
   support" subsections** (`atlas.tex:330-344`, `certification.tex:255-266`,
   `audit.tex:696-721`) as *subsections*. Their content is mandatory and folds
   into §7.3 or the section close.
7. **No em dashes in prose.** Rewrite each site individually. The `---` in
   "no value" table cells is table notation and stays. `appendix_registrations.tex`
   is exempt and untouched.
8. **Never hand-type an audit count.** Use the `\Audit*` macros.
9. **Duplicated statements to collapse:** the required-n equation (2 sites), the
   one-sided z / 90% CI fact (3), the H3 decision rule (3), the winner-flip
   definition (3), GSM8K under-resolution (5, keep 2), the atlas ratio (5, keep
   3), "no source declares a margin" (6, keep 3), R10's exclusion (2), the atlas
   population caveat (2), the escalation-screen authorship discipline (3).

---

## 10. Figure 1

Specified separately by Agent B and implemented by Agent D. Binding constraints
set here:

- **The cell is Qwen2.5-7B / GSM8K, GPTQ versus AWQ, from the registered eight.**
  Its churn-to-net ratio is **30.45x, the maximum of the eight cells**, against a
  median of 12.71x. The caption must say plainly that it is an illustrative
  example and the most extreme of the eight, not a typical cell, and the figure
  must show all eight cells so the selected example cannot be mistaken for the
  evidence base.
- **No LaTeX exists on this machine or in the pinned image**, and the image has
  no matplotlib. The figure is therefore **generated TikZ**, emitted by a
  checked-in script from canonical artifacts, and is vector at build time. A PNG
  preview cannot be produced here. **The figure has not been rendered or
  visually inspected, and no claim that it has may be made.**
- The Panel C planning requirement is computed **through the project's own
  implementation** (`scripts/audit_stats.py`), not by hand.
- **D4 applies: 5.3x does not appear in the figure.**
- Panel C is labelled a planning requirement and an insufficient-evidence
  result. It must not say the methods are inequivalent.

---

## 11. Gates

`paper/` and `docs/` are outside the source fingerprint, so paper edits need no
freeze refresh and no in-image suite. The figure generator and its tests land in
`scripts/` and `tests/`, which **are** fingerprinted, so that commit requires:

1. the in-image pytest gate via `scripts/slurm/run_tests.sbatch`,
2. the expected count updated in `CLAUDE.md` in the same commit,
3. `python3 scripts/freeze_prepace.py` after committing, then commit the freeze.

Baseline at `bcc1afc`: **297 passed, 0 skipped** (job 11675341).

After every paper commit:

```
python3 paper/tools/check_paper.py            # OK, 0 dangling refs, 0 stale
python3 paper/tools/verify_registrations.py   # OK
python3 paper/tools/gen_denominator_macros.py --check
cd paper && python3 tools/measure_abstract.py abstract.tex   # if abstract changed
```

`paper/tools/gen_reading_copy.py` runs once at the end, not per commit.

**Blocked and reported as blocked:** compiling the manuscript, the main-body and
total page counts, overfull and underfull box reports, float placement, and all
visual inspection. There is no LaTeX available.
