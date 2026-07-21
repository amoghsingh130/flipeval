<!--
DO-NOT-PUBLISH
==============
STATUS: DRAFT, BLOCKED FROM PUBLICATION AS OF 2026-07-21.

REASON: every atlas number in this post is marked provisional for external
quoting at docs/RESULTS_2026-07-15_ATLAS_AUDIT.md, lines 5-7 ("Pending an
independent spot-check of the same-day pipeline (two bugs were found and fixed
during the run), treat as provisional for external quoting"). That spot-check is
running now as a separate task.

THE STAMP LIFTS ONLY WHEN docs/RESULTS_2026-07-15_ATLAS_AUDIT.md ITSELF RECORDS
THE SPOT-CHECK AS COMPLETED. Not when the spot-check finishes; when that document
says so. Removing this banner is a decision for Amogh, not for any agent.

Also blocked on: artifact URLs and DOI (all links below are TODO placeholders).
-->

> # DO NOT PUBLISH — DRAFT
>
> **This post is blocked from publication.** The atlas numbers it quotes are
> marked *provisional for external quoting* in
> `docs/RESULTS_2026-07-15_ATLAS_AUDIT.md` (lines 5–7), pending an independent
> spot-check of the analysis pipeline. The block lifts only when that document
> records the spot-check as completed. Every link below is a placeholder.

---

# 113 compressed models scored *exactly* the same as their baselines. Most of them changed their answers.

*Draft — Amogh Singh, Georgia Tech*

## The finding

I mined the public record of compression evaluation — per-item outputs from the
Open LLM Leaderboard v1 archive and Neural Magic's per-item dumps for quantized
Llama-3.1 — and built paired comparisons for every model/task cell where the
baseline and the compressed model were evaluated on the same items with
byte-identical prompts. That gives 1,155 analysable cells, from 3B up to 405B
parameters.

**113 of those 1,155 cells (9.8%) post an accuracy that is *exactly* identical
to the baseline's** — not close, identical to machine precision. Among those
cells, the median share of items where the two models disagree on correctness is
**6.22%**. 96 of the 113 have nonzero churn.

Roughly one in ten compressed-model evaluations in the public record reports "no
change in accuracy," and half of those still disagree with the baseline on more
than 6% of individual items.

*(Numbers: `docs/IDENTICAL_SCORE_CHURN_2026-07-21.md`, computed from
`results/atlas_cells_summary.csv`; the derivation script is stdlib-only and
included in that note, so you can rerun it.)*

## A concrete example you can check

The most extreme zero-delta cell in the atlas, rank 1 of
`results/identical_score_churn.csv`:

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
  versus 0.133 for the leaderboard archive).
- **This is an illustration of the mechanism, not a typical magnitude.** The
  median among the 113 zero-delta cells is 6.22%, not 34%. If you quote one
  number from this post, quote 6.22%, not 34%.

## Why this happens, and why "net delta" is the wrong summary

Aggregate accuracy is a **net** quantity. Compression breaks some items and
fixes others, and the reported delta is what survives the cancellation. Across
all 1,155 cells, per-item churn runs roughly **five to six times** the net
accuracy delta, at every scale from 3B to 405B.

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
| HellaSwag | 14 | 688 | 4,992 |
| GPQA | 24 | 749 | 7,233 |
| GSM8K | 11 | 750 | 1,236 |
| IFEval | 8 | 800 | 4,211 |
| MMLU-Pro | 5 | 827 | 7,695 |
| ARC-Challenge | 8 | 1,211 | 7,524 |
| Winogrande | 15 | 1,879 | 6,267 |
| MMLU | 798 | 2,123 | 7,355 |
| MATH | 56 | 2,186 | 5,222 |
| **pooled** | **1,155** | **1,739** | 7,663 |

The "atlas cells" column is there so you can discount appropriately: MMLU (798
cells), BBH (192) and MATH (56) rest on a lot of evidence; MMLU-Pro (5), IFEval
(8), ARC-Challenge (8) and GSM8K (11) are thin and should be treated as a
starting hypothesis, not a constant. The quartile spread within a family also
mixes per-subject with per-model variation, which makes these numbers
conservative rather than optimistic.

Two things to notice.

**Pairing is worth a lot.** The right-hand column is what you get by treating the
two runs as independent samples, which is the default. They are not independent
— they are the same items through two nearly identical models — and using the
paired variance cuts the requirement by 1.7× (GSM8K) to 14.7× (MuSR), 4.4×
pooled. That is roughly a quarter of the evaluation budget for the same
conclusion.

**The ordering is not about difficulty.** MMLU needs ~2,123 items at ±2pp; GPQA,
which is much harder, needs 749. What drives the requirement is how much the
compressed model's per-item correctness *churns*, not how hard the task is. You
cannot guess your evaluation size from intuitions about task difficulty. You
have to measure churn.

Margins are quadratic, so they are expensive: MMLU needs 944 items at ±3pp,
2,123 at ±2pp, and 8,492 at ±1pp. If you want to claim parity within a tenth of
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

One more artifact of the record worth knowing about: of the 2,055 pair-task
cells I enumerated, 132 were dropped because the two sides had **no items in
common** — the leaderboard evaluated different item sets across the two runs.
The aggregate numbers were still compared. Nothing on the leaderboard tells you
that.

## Links

- Paper: TODO
- `flipeval` (Apache-2.0), the analysis tool — paired flip rates, churn,
  McNemar, TOST, required-n, certification tables: TODO
- The atlas (CC-BY-4.0), per-cell statistics for every enumerated pair: TODO
- Preregistrations, dated amendments, and the frozen claim table: TODO

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
