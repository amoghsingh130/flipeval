# Session handoff, 2026-08-04: flagship narrative revision, Wave 1 only

Read `docs/FLAGSHIP_NARRATIVE_PLAN.md` first. This document records what that
plan does **not** contain, so the next session does not have to rediscover it.

**Branch `flagship-narrative`, worktree `.claude/worktrees/flagship`, based at
`bcc1afc`, one commit: `4d5f7b3`.** Not pushed. `main` has since moved to
`af4d07e` (Amendment 4 signed, the source-tarball hash remap), so this branch is
three commits behind and must be rebased before any paper edit lands.

## 1. What this session was asked to do, and how far it got

Asked: implement a flagship narrative, build a central Figure 1, and reduce the
main paper to 12 to 16 pages before references, using parallel agents with
separate file ownership.

Reached: **Wave 1 (analysis) only.** Waves 2 (implementation) and 3 (adversarial
QA) did not start. The plan document is the whole deliverable.

Stopped because the user raised a credit concern and, in the same minute, the
figure-verification agent died on a real API session limit. Nothing was
abandoned mid-edit; the tree is clean.

## 2. The blocker that shapes everything

**There is no LaTeX on the login node and none inside the pinned image.**
Confirmed by probe job `11675341`, not assumed: `pdflatex`, `latexmk`, `xelatex`,
`lualatex`, `tectonic` and `kpsewhich` are all MISSING in both. The image also
has **no matplotlib** (it has numpy 2.2.6, pandas 2.3.3, scipy 1.15.3).

Consequences, all of which the next session inherits:

- The manuscript cannot be compiled. No page count, no overfull/underfull box
  report, no float placement check, no visual inspection of anything.
- Figure 1 must be **generated TikZ**, not matplotlib, so that it is vector at
  build time on whatever machine eventually has LaTeX.
- Any claim that the page target or visual QA passed would be false. Do not make
  one.

This is the same standing blocker recorded in `SESSION_HANDOFF_2026-08-02` and
`_2026-08-03` ("a machine with LaTeX"). It is now measured rather than assumed.

## 3. Baseline gate state at `bcc1afc`

All green, recorded so a later failure can be localised:

| gate | result |
|---|---|
| in-image pytest (job `11675341`) | **297 passed, 0 skipped** |
| `check_paper.py` structural | OK, 23 files, 103 labels, 150 refs, 23 cite keys, 25 tabulars, 0 dangling |
| `check_paper.py` stale-claim | OK, 206 files, 608 hits, 0 stale |
| `verify_registrations.py` | OK, 6,452 words across 4 documents |
| `gen_denominator_macros.py --check` | OK on all three layers |

**Caution on the test count.** A concurrent session was editing the parent
worktree during this session and bumped the `CLAUDE.md` expectation to **298**
while the suite measured **297** here. Re-measure before citing either number.

## 4. Wave 1 agent outcomes

| agent | scope | outcome |
|---|---|---|
| A, narrative architect | thesis, claims-to-evidence map, structure, cuts, prose defects | **Completed.** Distilled into the plan. |
| C, compression and structure | page allocation, cut/move table, cross-ref migration, qualification risk | **Completed.** Distilled into the plan. |
| B, figure and numerical verification | Figure 1 provenance, sign conventions, wireframe, caption, test plan | **FAILED before producing anything.** |

**Agent transcripts are not recoverable.** They were written to a session-scoped
scratchpad under `/tmp` and are gone. Everything retained from A and C is in the
plan document; what was not transcribed is lost, and the affected items are
noted in section 6 below.

## 5. What Agent B never delivered, and must be redone

This is the single largest gap. Wave 2's figure agent cannot start without it.

1. **Sign conventions.** Partially resolved by the coordinator and recorded here
   so it is not lost: in
   `results/minigrid_supporting/minigrid_supporting.json`,
   `slot4_flip_statistics[cell].cell_mean.net_accuracy_delta` is
   **AWQ minus GPTQ**, while `full_sample_accuracy_delta` in
   `results/h3_eight_cell/h3_eight_cell_summary.json` and `accuracy_delta` in
   the `paired_seeds_*.json` files are **GPTQ minus AWQ**, i.e. the opposite
   sign. For Qwen2.5-7B/GSM8K: slot4 net is `-0.0058` and equals
   `beneficial - harmful` = `0.0854 - 0.0912`; the h3 summary gives `+0.0058`.
   **This was inferred from the artifacts and has not been confirmed against the
   code that wrote them.** Confirm before it reaches a figure label.
2. **The Panel C planning requirement.** Must be computed **through
   `scripts/audit_stats.py`** (`paired_flip_sd`, `required_n_for_tost`,
   `ALPHA`, `POWER`), not by hand. That module imports scipy, so it does not run
   on the login node; it needs an sbatch job into the image. Never computed this
   session.
3. **The panel wireframe, colour choice with stated grayscale separation, and
   the caption draft.** Not produced.
4. **The generation script and test plan.** Not produced.

## 6. Verified values available for Figure 1

Checked by the coordinator directly against the artifacts, so these do not need
redoing.

Flagship cell, **Qwen2.5-7B / GSM8K, GPTQ versus AWQ**, from the registered
eight:

| quantity | value | source |
|---|---|---|
| GPTQ full-sample accuracy | 0.7428 | `h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json` |
| AWQ full-sample accuracy | 0.7370 | same |
| method gap | 0.0058 (0.58 pp) | same |
| n per seed | 1,000 | same |
| harmful flip rate | 0.0912 | `minigrid_supporting.json` slot4 cell_mean |
| beneficial flip rate | 0.0854 | same |
| accuracy-state churn | 0.1766 | same |
| total answer churn | 0.2866 | same |
| seed-wise GPTQ minus AWQ | +0.022, +0.016, -0.023, +0.002, +0.012 | `paired_seeds_*.json` per_seed |
| observed discordance p_d | 0.1766 | `minigrid_supporting.json` step5 |

Grid-level: **winner flip in 5 of 8**, range/gap in 7 of 8, **0 ties across all
40 (model, task, seed) triples**, median churn-to-net ratio **12.71x** across
the eight cells.

**The flagship cell's own ratio is 30.45x, the maximum of the eight**, against
that 12.71x median. The caption must say it is an illustrative example and the
most extreme of the eight, and the figure must show all eight cells, or a
reviewer will correctly call it cherry-picked. This constraint is binding and is
also recorded in the plan.

Atlas context, exact: **1,707** analysable cells, **145** with exactly unchanged
aggregate accuracy, **128** of those with nonzero correctness-state churn
(`results/identical_score_churn_rev2.csv`). **Do not put 5.3x in the figure**;
see defect D4 in the plan.

## 7. Ordered next steps

1. **Rebase onto `af4d07e`** so the work sits on top of Amendment 4.
2. **Redo Agent B's verification** (section 5 above), including the sbatch job
   that computes the planning requirement in the image.
3. **Wave 2, three agents on disjoint file ownership:**
   - figure: `scripts/make_figure1.py`, `tests/test_figure1.py`,
     `paper/figures/`, and an sbatch runner. **This touches `scripts/` and
     `tests/`, which are fingerprinted**, so that commit needs the in-image
     gate, the `CLAUDE.md` count updated in the same commit, and a freeze
     refresh after.
   - front and back: `abstract.tex`, `introduction.tex`, `limitations.tex`,
     `conclusion.tex`.
   - body: `main.tex` and every other section and appendix file.
   Only the body agent touches `main.tex`, so the branches merge cleanly.
4. **Wave 3**, scientific adversary and narrative/layout adversary.
5. **Fix the seven defects** D1 to D7 in the plan, respecting the disposition on
   each. D4 is escalated to Amogh and must not be changed on the branch.

## 8. Decisions waiting on Amogh

1. **D4, the 5.3x headline.** It divides rounded medians; the direct ratios are
   5.22 (S1) and 5.19 (S2), and `tab:atlas-strata` prints 0.138 where the
   artifact rounds to 0.137. The number is public in the Zenodo release and the
   blog, so the paper cannot be corrected alone. **Highest-priority decision.**
2. **Geometry.** `main.tex` is `article` 11pt and there is no `tmlr.sty` in the
   tree. The body is about 58 pages in article geometry and about 30 under the
   TMLR style the release checklist mandates. "12 to 16 pages" means different
   work under each. The plan's program lands near 21 article pages, about 11 to
   12 TMLR pages. Neither is measured.
3. **Whether to macro-ise the locus tier counts** (D6), which touches
   `gen_denominator_macros.py` and its validated three-layer check.
