# H3 Supporting Analyses — Results, 2026-07-26

**These do not modify the signed verdict, and cannot.** H3 is SUPPORTED per
`docs/H3_EIGHT_CELL_DECISION_2026-07-26.md` (SIGNED, commit `05c86f2`). That
verdict was determined by the frozen rule over winner flips and range/gap, both
computed and recorded there. **Nothing in this document is grounds to revisit
it.** A weak bootstrap rate or a poorly-resolved cell is a limitation to report,
not a re-litigation of the rule — stated here explicitly so that no later reader
mistakes these tables for a second bite at the decision.

Three of the four analyses below are **registered** (the `\minigridTODO` slots
`minigrid.tex` has carried since drafting). The fourth is **post-hoc and labelled
as such** throughout.

---

## Bootstrap parameters, and why nothing was re-run

**2000 replicates, bootstrap seed 0 — registered**, not chosen here:

> `docs/MINIGRID_REGISTRATION_2026-07-15.md` § 5: "The registered hierarchical
> analysis (`flipeval paired-seeds`, **2000 replicates, bootstrap seed 0**) is
> **run once per cell**; the escalation rule in §3 is then applied mechanically…"

That analysis **has already been run once per cell** — job `11511724`, at exactly
those parameters — and its complete output for all eight cells was committed at
`264095f` under `results/h3_eight_cell/paired_seeds_*.json`. Slots 2 and 3 are
read from those artifacts. They were never unrun; they were unwritten.

**No second bootstrap pass was made, at any replicate count.** Re-running would
violate § 5's "run once per cell" clause independently of the count used, and
choosing a replicate count after seeing output is exactly the analyst degree of
freedom this project does not spend. A 10,000-replicate pass was considered and
**declined by Amogh**: Monte Carlo error at 2000 replicates is ±1.1 pp for a rate
near 0.5 and ±0.11 pp for a rate near 0.0025, so every qualitative reading below
is stable at the registered count, and a second pass would add only a paragraph
explaining why it was run twice.

Steps 4 and 5 consume **no replicate count and no RNG seed** — step 4 is
deterministic counting, step 5 is arithmetic on step 4 — so no analyst degree of
freedom is spent by either.

**Pairing verified before use** (registered requirement, `PREREGISTRATION.md`
§ 53–55). `flipeval/core.py::draw_two_level_indices` yields one `seed_positions`
array and one `item_draws` tuple per replicate; the consuming loop applies the
same seed label and the same item indices to both methods. Neither method
receives an independent draw of anything, and item-ID sets are asserted identical
across methods and across seeds before any resampling. The rank-flip denominator
convention — tie replicates **included** in the denominator, ties **also**
reported separately — is fixed in words by the registration "as of commit
`a8ba9f0`"; `git diff a8ba9f0 HEAD -- flipeval/core.py` shows no change to any
flip or tie line, so the prose and the code still agree.

**Output discipline** (incident 26): job `11512141`, `--out-dir` required with no
default, refusing to overwrite any existing target and refusing any path inside a
sealed run directory or colliding with `results/h3_eight_cell/` or
`results/minigrid_escalation/`. `PATH_AUDIT: PASS`.

---

## The four tables

Cells are ordered mini-grid first, then escalation. Slot 4 compares **GPTQ seed
*s* against AWQ seed *s*** — the registered paired calibration contrast — with
`base = GPTQ` and `method = AWQ`, so net delta is `acc_AWQ − acc_GPTQ`, i.e.
`−d_s` in the H3 record's sign convention. Churn quantities are
direction-symmetric. Values are the mean over the five paired seeds; per-seed
values are in the artifact.

### Slot 2 — variance decomposition

| cell | SD across seeds, GPTQ | SD across seeds, AWQ | item-level SE, GPTQ | item-level SE, AWQ |
|---|---:|---:|---:|---:|
| qwen25-1p5b/mmlu | 0.019130 | 0.006897 | 0.004215 | 0.004212 |
| qwen25-1p5b/gsm8k | 0.006340 | 0.015116 | 0.015796 | 0.015658 |
| llama32-3b/mmlu | 0.024925 | 0.011157 | 0.004214 | 0.004216 |
| llama32-3b/gsm8k | 0.004615 | 0.012300 | 0.015154 | 0.015308 |
| qwen25-7b/mmlu | 0.006224 | 0.004537 | 0.003983 | 0.004002 |
| qwen25-7b/gsm8k | 0.019267 | 0.014195 | 0.013815 | 0.013922 |
| llama31-8b/mmlu | 0.015100 | 0.010520 | 0.004183 | 0.004163 |
| llama31-8b/gsm8k | 0.014307 | 0.010654 | 0.013874 | 0.013640 |

### Slot 3 — two-level paired bootstrap

| cell | rank-flip rate | flip replicates | exact-tie rate | tie replicates | registered winner flip |
|---|---:|---:|---:|---:|---|
| qwen25-1p5b/mmlu | 0.0445 | 89 / 2000 | 0.0005 | 1 / 2000 | **TRUE** |
| qwen25-1p5b/gsm8k | 0.0000 | 0 / 2000 | 0.0000 | 0 / 2000 | FALSE |
| llama32-3b/mmlu | 0.0000 | 0 / 2000 | 0.0000 | 0 / 2000 | FALSE |
| llama32-3b/gsm8k | 0.0220 | 44 / 2000 | 0.0000 | 0 / 2000 | **TRUE** |
| qwen25-7b/mmlu | 0.0025 | 5 / 2000 | 0.0000 | 0 / 2000 | FALSE |
| qwen25-7b/gsm8k | 0.2575 | 515 / 2000 | 0.0100 | 20 / 2000 | **TRUE** |
| llama31-8b/mmlu | 0.0405 | 81 / 2000 | 0.0000 | 0 / 2000 | **TRUE** |
| llama31-8b/gsm8k | 0.1260 | 252 / 2000 | 0.0030 | 6 / 2000 | **TRUE** |

### Slot 4 — flip statistics against the atlas

| cell | net delta | harmful | beneficial | accuracy-state churn | wrong→diff-wrong | total answer churn |
|---|---:|---:|---:|---:|---:|---:|
| qwen25-1p5b/mmlu | +0.012292 | 0.087965 | 0.100256 | 0.188221 | 0.091924 | 0.280145 |
| qwen25-1p5b/gsm8k | +0.096800 | 0.098600 | 0.195400 | 0.294000 | 0.273800 | 0.567800 |
| llama32-3b/mmlu | +0.030922 | 0.078465 | 0.109386 | 0.187851 | 0.098049 | 0.285899 |
| llama32-3b/gsm8k | -0.017800 | 0.113200 | 0.095400 | 0.208600 | 0.155800 | 0.364400 |
| qwen25-7b/mmlu | -0.006267 | 0.059393 | 0.053126 | 0.112520 | 0.045250 | 0.157770 |
| qwen25-7b/gsm8k | -0.005800 | 0.091200 | 0.085400 | 0.176600 | 0.110000 | 0.286600 |
| llama31-8b/mmlu | +0.017163 | 0.081270 | 0.098433 | 0.179704 | 0.090956 | 0.270659 |
| llama31-8b/gsm8k | +0.013200 | 0.083800 | 0.097000 | 0.180800 | 0.096400 | 0.277200 |

### Step 5 — resolution analysis (POST-HOC)

| cell | p_d | n | paired SD | paired SE | gap / SE | max_range / SE |
|---|---:|---:|---:|---:|---:|---:|
| qwen25-1p5b/mmlu | 0.188221 | 14,042 | 0.433845 | 0.003661 | 3.36 | 11.07 |
| qwen25-1p5b/gsm8k | 0.294000 | 1,000 | 0.542218 | 0.017146 | 5.65 | 1.92 |
| llama32-3b/mmlu | 0.187851 | 14,042 | 0.433418 | 0.003658 | 8.45 | 17.45 |
| llama32-3b/gsm8k | 0.208600 | 1,000 | 0.456727 | 0.014443 | 1.23 | 2.35 |
| qwen25-7b/mmlu | 0.112520 | 14,042 | 0.335439 | 0.002831 | 2.21 | 5.53 |
| qwen25-7b/gsm8k | 0.176600 | 1,000 | 0.420238 | 0.013289 | 0.44 | 3.61 |
| llama31-8b/mmlu | 0.179704 | 14,042 | 0.423915 | 0.003577 | 4.80 | 11.19 |
| llama31-8b/gsm8k | 0.180800 | 1,000 | 0.425206 | 0.013446 | 0.98 | 2.45 |

---

## Reconciling winner flips with bootstrap rank-flip rates

The two columns measure different things, and a reader who assumes they measure
the same thing will read the table as self-contradictory. Stating the
reconciliation here, before anyone reaches that conclusion.

**A winner flip asks whether two individual seeds disagree on sign.** It is H3's
actual question, and it describes what happens when a practitioner runs *one*
calibration and takes the winner.

**The bootstrap rank-flip rate asks whether the mean ranking survives resampling
seeds and items together.** It describes what happens when a practitioner
averages over *five* calibrations.

A cell can have a winner flip and a near-zero bootstrap rank-flip rate, and that
combination is not a contradiction. It is the sharpest form of the finding:

| | cells |
|---|---|
| registered winner flip | **5 of 8** |
| bootstrap rank-flip rate < 0.05 | **6 of 8** |
| **both** — single calibration unstable, five-seed mean stable | **3 of 8** |

The three cells in the last row are `qwen25-1p5b/mmlu` (flip TRUE, bootstrap
0.0445), `llama32-3b/gsm8k` (TRUE, 0.0220) and `llama31-8b/mmlu` (TRUE, 0.0405).
In each, *some pair of individual seeds disagrees about which method wins*, while
the five-seed average ranking survives resampling in more than 95% of replicates.

**This is the practical contribution, and it is a finding rather than a caveat.**
It says something a practitioner can act on: a single calibration run can hand
you the wrong winner, and averaging over the registered five seeds is
substantially more stable than any one of them. That is a stronger and more
useful statement than "method rankings are unreliable", because it names what to
do instead of only what not to trust.

Two cells are unstable on *both* measures — `qwen25-7b/gsm8k` (flip TRUE,
bootstrap 0.2575, 515 of 2000 replicates) and `llama31-8b/gsm8k` (TRUE, 0.1260,
252 of 2000). In those, even the five-seed mean ranking does not survive
resampling, and no amount of seed averaging at n = 1,000 rescues the comparison.
Three cells show no winner flip and a bootstrap rate at or below 0.0025.

## Step 5 — resolution analysis

### Disclosure

**This quantity was not registered.** It was requested on **2026-07-26**, *after*
the eight-cell verdict had been computed and signed, in response to prior art
identified the same day — **arXiv:2405.20835**, which reports calibration effects
diminishing in modern LLMs. It is descriptive, it tests no hypothesis, and it
does not modify the verdict. It is recorded with its provenance rather than
folded silently into the registered results.

### What it says: the split is by task, and it is stark

Using § 5's own machinery — paired SD = `sqrt(p_d)`, paired SE = `sqrt(p_d / n)`,
with `p_d` the per-cell GPTQ-vs-AWQ accuracy-state churn from slot 4 (computed
per cell, **not** reused from the harness study's Q̄, which is a
quantized-vs-FP16 contrast and a different pair):

| task | max_range in paired SE | gap in paired SE |
|---|---|---|
| **MMLU** (n = 14,042) | 5.53 – 17.45 | 2.21 – 8.45 |
| **GSM8K** (n = 1,000) | 1.92 – 3.61 | 0.44 – 5.65 |

**MMLU comes back strong and GSM8K comes back weak.** On MMLU the seed-induced
range is 5.5 to 17.5 paired standard errors — the instability is far larger than
the measurement noise, and the cells resolve it comfortably. On GSM8K the range
is roughly two to three-and-a-half SE, and in three of the four GSM8K cells the
*mean gap itself* sits at or below 1.25 SE (`0.44`, `0.98`, `1.23`) — the
quantity H3's range/gap criterion compares against is, in those cells, not
resolved by the benchmark at the n used.

This is the honest finding, and it belongs in the paper's own limitations rather
than in a reviewer's comment. It does not weaken the verdict: the range/gap
criterion holds in 7 of 8 cells and winner flips occur in 5 of 8, both computed
from the registered per-seed accuracies, and neither is a significance test. But
it does mean the GSM8K cells carry materially less resolving power than the MMLU
cells, and any per-cell reading of GSM8K should say so.

### The paper's own table predicted this

`results/certification_tables_rev2.csv` (§ 5 certification) gives GSM8K, at a
2 pp margin:

| statistic | discordance | required n |
|---|---:|---:|
| p25 | 0.039992 | 619 |
| **median** | **0.076573** | **1,184** |
| p75 | 0.198446 | 3,068 |

**The H3 GSM8K cells ran at n = 1,000** — already below the 1,184 the table
requires at *median* discordance. And the discordance actually observed in these
cells is far above that median: `p_d` = 0.1766, 0.1808, 0.2086 and 0.2940, i.e.
at or above the table's **p75**, where the requirement is 3,068 — roughly three
times the n used.

So the under-resolution is not a surprise: **the paper's own § 5 table predicted
it, and predicted it conservatively.** One caveat on the comparison, stated
plainly: the certification table's discordance percentiles describe a
quantized-vs-FP16 contrast, while `p_d` here is GPTQ-vs-AWQ. The required-n
column is a function of discordance whatever the pair, so reading the observed
`p_d` against the table's brackets is legitimate; the percentile labels are not
strictly like-for-like and are used here only to locate the observed values.

## Provenance

| | |
|---|---|
| Job | `11512141` (`SUPPORTING_EXIT: 0`), `logs/minigrid_supporting_11512141.out` |
| Driver | `~/scratch/flipeval/work/minigrid_supporting.{py,sbatch}` |
| Artifact | `results/minigrid_supporting/minigrid_supporting.json` |
| Slots 2–3 source | `results/h3_eight_cell/paired_seeds_*.json`, job `11511724`, commit `264095f` — **not re-run** |
| Bootstrap parameters | 2000 replicates / seed 0, `MINIGRID_REGISTRATION_2026-07-15.md` § 5 |
| Flip metrics | `flipeval.core.compute_pair_metrics` — the same function behind the atlas § 6 population |
| Verdict (unchanged) | `docs/H3_EIGHT_CELL_DECISION_2026-07-26.md`, SIGNED `05c86f2` |

**No paper edits were made in this pass.** No `\minigridTODO` is filled; that is
a separate job once these numbers have been read.

## Downstream wording adjustment (2026-07-27)

The abstract's pre-drafted H3 variant (A) ended *"…so a single-calibration
comparison of compression methods is **not reproducible**."* On selecting that
variant, **"not reproducible" was changed to "unreliable"**, because it
over-claims against the bootstrap result in this document: three cells combine a
winner flip with a rank-flip rate below 0.05, so individual seeds disagree while
the five-seed mean survives resampling — which is unreliability of a single run,
not irreproducibility. The registered artifacts are the decision rule and the
verdict, not the drafted abstract prose, so no amendment to a frozen file is
implicated; the change is recorded here because the reason for it is a result in
this document. Nothing about the verdict, the rule, or any number changed.
