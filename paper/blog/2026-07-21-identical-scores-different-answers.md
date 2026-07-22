<!--
DO-NOT-PUBLISH
==============
STATUS: DRAFT, BLOCKED FROM PUBLICATION AS OF 2026-07-22.

REVISED TO ATLAS REV-2 ON 2026-07-22. Every atlas, certification and
identical-score figure below is read from the rev-2 artifacts
(results/atlas_cells_summary_rev2.csv, results/identical_score_churn_rev2.csv,
results/certification_tables_rev2.csv). The rev-1 figures this post previously
carried (1,155 cells / 113 zero-delta / 6.22% median / 1,739 pooled required-n /
4.4x pooled advantage) are superseded. See docs/ATLAS_REV2_CORRECTION_2026-07-21.md.

THE ORIGINAL BLOCKING REASON IS NOW SATISFIED, BUT THE STAMP IS NOT MINE TO LIFT.
The earlier banner said the stamp lifts only when
docs/RESULTS_2026-07-15_ATLAS_AUDIT.md itself records the spot-check as completed.
It now does (line 6: "SPOT-CHECK COMPLETED 2026-07-21"), and rev-2 has since
passed its targeted second spot-check (14/14 cells, 126/126 fields, commit
8b3e0de). So the condition that document set has been met.

WHAT STILL BLOCKS PUBLICATION, as of this revision:
  1. Every link below is still a TODO placeholder. The links can only stop being
     TODOs when the repo and artifacts are made public, which is an unmade
     decision (coupled to the H3 read).
  2. Removing this banner is a decision for Amogh, not for any agent. That was
     true when the stamp went on and is still true now.
-->

> # DO NOT PUBLISH — DRAFT
>
> **This post is blocked from publication.** Its numbers are current as of atlas
> rev-2 and the spot-check condition that originally blocked it has been met —
> but every link below is still a placeholder, and those resolve only when the
> repo and artifacts are made public. That decision has not been taken.

---

# 145 compressed models scored *exactly* the same as their baselines. Most of them changed their answers.

*Draft — Amogh Singh, Georgia Tech*

## The finding

I mined the public record of compression evaluation — per-item outputs from the
Open LLM Leaderboard v1 archive and Neural Magic's per-item dumps for quantized
Llama-3.1 — and built paired comparisons for every model/task cell where the
baseline and the compressed model were evaluated on the same items with
byte-identical prompts. That gives 1,707 analysable cells, from 3B up to 405B
parameters.

**145 of those 1,707 cells (8.5%) post an accuracy that is *exactly* identical
to the baseline's** — not close, identical to machine precision. Among those
cells, the median share of items where the two models disagree on correctness is
**7.20%**. 128 of the 145 have nonzero churn.

Roughly one in twelve compressed-model evaluations in the public record reports
"no change in accuracy," and half of those still disagree with the baseline on
more than 7% of individual items.

*(Numbers: `docs/ATLAS_REV2_CORRECTION_2026-07-21.md` §8, computed from
`results/atlas_cells_summary_rev2.csv`; the derivation script is stdlib-only and
included in `docs/IDENTICAL_SCORE_CHURN_2026-07-21.md`, so you can rerun it.)*

## A concrete example you can check

The most extreme zero-delta cell in the atlas, rank 1 of
`results/identical_score_churn_rev2.csv`:

| field | value |
|---|---|
| task | `harness_hendrycksTest_high_school_geography_5` (MMLU) |
| base model | `project-baize/baize-v2-7b` |
| quantized model | `TheBloke/Project-Baize-v2-7B-GPTQ` (GPTQ) |
| n | 198 |
| baseline accuracy | 0.429293 |
| quantized accuracy | 0.429293 (net delta 0.000000) |
| accuracy-state churn | **0.343434** |
| harmful / beneficial flips | 0.171717 / 0.171717 |
| exact McNemar p | 1.0 |

Both models score 0.429293. The difference is zero — not rounded to zero,
*zero*.

And 34.3% of the items changed correctness state. Exactly 17.17% of items that
the base model got right, the quantized model got wrong. Exactly 17.17% that the
base model got wrong, the quantized model got right. The two rates are equal, so
they cancel perfectly, and the aggregate score does not move at all.

McNemar's test returns p = 1.0 on this cell, and it is *right* to. There is no
evidence of a **directional** difference between these two models: the breakage
and the healing are symmetric. That is the correct answer to the question
McNemar asks. It is not an answer to the question "does this quantized model
behave like the original," because a third of the answers changed.

**Caveats, in the same breath:**

- n = 198 is small, and symmetric flip counts are easier to land by chance at
  small n.
- This is an S1 cell: a 2023-era community GPTQ of a 7B base model, which is the
  noisier of the two strata I mined. Modern vendor quantizations churn about a
  third as much (median accuracy-state churn 0.048 for the Neural Magic dumps,
  versus 0.138 for the leaderboard archive).
- **This is an illustration of the mechanism, not a typical magnitude.** The
  median among the 145 zero-delta cells is 7.20%, not 34%. If you quote one
  number from this post, quote 7.20%, not 34%.

## Why this happens, and why "net delta" is the wrong summary

Aggregate accuracy is a **net** quantity. Compression breaks some items and
fixes others, and the reported delta is what survives the cancellation. Across
all 1,707 cells, per-item churn runs roughly **five times** the net accuracy
delta, at every scale from 3B to 405B — median churn 0.138 against median
absolute net delta 0.026 in the leaderboard archive, and 0.048 against 0.009 in
the vendor dumps.

So a model card reporting "−0.1 points on MMLU" is reporting the residue of a
much larger amount of behavioural change. That is not dishonest, and it is not a
bug in the metric — net delta is a perfectly good summary of *aggregate task
performance*. It is just not a summary of *behaviour*, and "near-lossless" is a
claim about behaviour.

None of this says the compressed models are worse. In the example above, exactly
as many items got better as got worse.

## The second finding: nobody can check any of this

I also ran a preregistered audit of 17 published "near-lossless" compression
claims — method papers, official quantized model cards, and inference-stack
vendor documentation. The protocol was frozen before any number was computed.

**0 of the 17 sources release the per-item outputs a third party would need to
run the paired comparison the claim asserts.** The tally is 0 yes, 3 partial, 14
no. The three partial cases are all Red Hat AI model cards, and they are the
closest the field comes: they publish per-item outputs for Arena-Hard, OpenLLM
v2 and HumanEval — but not for the OpenLLM v1 tasks the equivalence claim is
actually about. The released artifacts and the asserted claim do not intersect.

This is the finding I would most like fixed, because it is the cheapest to fix.
Underpowered evaluation is repairable by evaluating more items. Irreproducible
evaluation is not repairable downstream at all: with no per-item outputs, nobody
outside the releasing organisation can run the paired test at any sample size,
compute churn, or check the arithmetic. Per-item outputs for a few-thousand-item
benchmark are a few megabytes.

**To be explicit: no claim is being called false.** The audit measures whether
the evaluation offered for a claim was large enough to have detected the
difference the claim calls negligible. A claim can be entirely correct and still
be unsupported by the evidence published with it, and I expect several of these
are. The problem is a missing reporting standard, not dishonesty.

The audit also found that 4 of the 12 claims whose reporting permits a verdict
are underpowered for their own assertion — their evaluations could not have
resolved the margin they assert, by factors of 2.0× to 12.9× — and that 5 of the
17 cannot be evaluated at all, because their equivalence evidence exists only as
a chart image, or has no baseline run on the page. Details in the paper.

## The practical part: how many items do you actually need?

If you want to say "this quantized model is within ±2 points of the original,"
that is a testable claim (TOST at a declared margin), and it has a sample-size
requirement. I computed those requirements from the disagreement rates the atlas
actually observes, per benchmark family:

| benchmark | atlas cells | required n at ±2pp (typical churn) | if you ignore pairing |
|---|---|---|---|
| MuSR | 24 | 519 | 7,617 |
| BBH | 192 | 681 | 6,492 |
| HellaSwag | 23 | 695 | 4,905 |
| GPQA | 24 | 749 | 7,233 |
| IFEval | 8 | 800 | 4,211 |
| MMLU-Pro | 5 | 827 | 7,695 |
| GSM8K | 24 | 1,184 | 2,671 |
| ARC-Challenge | 17 | 1,218 | 7,363 |
| Winogrande | 23 | 1,416 | 5,600 |
| MMLU | 1,311 | 2,164 | 7,727 |
| MATH | 56 | 2,186 | 5,222 |
| **pooled** | **1,707** | **1,855** | 7,722 |

The "atlas cells" column is there so you can discount appropriately: MMLU (1,311
cells), BBH (192) and MATH (56) rest on a lot of evidence; MMLU-Pro (5) and
IFEval (8) are thin and should be treated as a starting hypothesis, not a
constant. The quartile spread within a family also mixes per-subject with
per-model variation, which makes these numbers conservative rather than
optimistic.

Two things to notice.

**Pairing is worth a lot.** The right-hand column is what you get by treating the
two runs as independent samples, which is the default. They are not independent
— they are the same items through two nearly identical models — and using the
paired variance cuts the requirement by 2.3× (GSM8K) to 14.7× (MuSR), 4.2×
pooled. That is roughly a quarter of the evaluation budget for the same
conclusion.

**The ordering is not about difficulty.** MMLU needs ~2,164 items at ±2pp; GPQA,
which is much harder, needs 749. What drives the requirement is how much the
compressed model's per-item correctness *churns*, not how hard the task is. You
cannot guess your evaluation size from intuitions about task difficulty. You
have to measure churn.

Margins are quadratic, so they are expensive: MMLU needs 962 items at ±3pp,
2,164 at ±2pp, and 8,656 at ±1pp. If you want to claim parity within a tenth of
a point — and several published claims do — the requirement is in the hundreds of
thousands of items.

Full tables at 1, 2 and 3 points, for 11 benchmark families plus a pooled row,
are in the release. TODO: link.

## What the data is, and what it isn't

The two sources are the Open LLM Leaderboard v1 archive (community
quantizations of 2023-era models — GPTQ, AWQ, GGUF, bnb 4-bit and 8-bit) and
Neural Magic / Red Hat's per-item dumps for quantized Llama-3.1 at 8B, 70B and
405B (W4A16, W8A8-INT8, W8A8-FP8).

**This is the public record of compression evaluation, not a census of
quantization.** A pair exists in it only because someone chose to publish both
sides, and that choice was not random with respect to anything. The S2 stratum
is one vendor's releases, evaluated by that vendor. These are the right data for
the question "what does the evidence that circulates look like, and how much
evidence would be enough," and the wrong data for "how does quantization behave
on average." For that you need a designed experiment, which is what the rest of
the project is.

One more thing worth knowing, and it is a correction to an earlier draft of this
post. Of the 2,055 pair-task cells I enumerated, 248 were excluded: **179 because
no per-item file could be found for that task at all, 36 because the two sides
shared no join keys, and 33 because the task is genuinely float-scored with no
binary correctness column.** An earlier version of this post reported a larger
empty-join count and attributed it to the leaderboard having evaluated different
item sets across runs. **That was wrong, and the fault was mine:** an independent
spot-check of my own pipeline found that my parser could not read the join key in
a newer results schema, and was recording its own failure as a property of the
upstream data. The corrected population is what this post now reports; both
revisions of the atlas are published, and the delta between them is documented.
I am leaving this paragraph in rather than quietly deleting the claim, because a
post arguing that the field should make its evaluations recheckable should show
what happens when someone rechecks mine.

## Links

- Paper: TODO
- `flipeval` (Apache-2.0), the analysis tool — paired flip rates, churn,
  McNemar, TOST, required-n, certification tables: TODO
- The atlas (CC-BY-4.0), per-cell statistics for every enumerated pair, rev-1 and
  rev-2: TODO
- Preregistrations, dated amendments, the correction memo, and the frozen claim
  table: TODO

Every number in this post is recomputable from the released artifacts. If you
find one that isn't, that's a bug and I want to hear about it.

## If you release compressed models, five lines

1. Declare a margin. "Equivalent" without a ±m is not a testable statement.
2. Run the paired test at that margin (TOST), not just a difference test. Not
   detecting a difference is not equivalence.
3. Report churn next to net delta. They are different quantities.
4. Say which sample size you met, and against which requirement.
5. Release the per-item outputs, for the tasks your claim is about. This is the
   cheap one, and right now nobody is doing it.
