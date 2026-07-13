# Ranking Quantized LLMs Is Harder Than It Looks: Statistical Power, Calibration-Seed Instability, and Behavioral Churn in Compressed-Model Evaluation

**Amogh Singh** · Georgia Tech CS · asingh3206@gatech.edu
Solo-author research proposal · v2 (collision-aware reframe)

## Problem

Compressed LLMs are almost always compared by a single aggregate benchmark score. This proposal argues that practice cannot reliably rank compression methods or certify that a compressed model preserves the original's behavior, and it shows why with statistics rather than anecdotes.

Two things are already known and are *not* claimed as novel here. Dutta et al., "Accuracy is Not All You Need" (NeurIPS 2024), established that compressed models can match baseline accuracy while flipping many individual answers, and proposed flips and KL-divergence as metrics. Separately, recent work has begun bringing paired tests, confidence intervals, and power analysis to LLM evaluation in general. This proposal sits at the intersection those two lines leave open: a statistically rigorous, compression-specific protocol that decomposes behavioral change, quantifies how unstable method rankings actually are, and states the sample sizes needed to make a defensible claim.

## Positioning (what is new)

Relative to Dutta et al., the contribution is not "flips exist." It is: (1) a net-versus-gross decomposition that separates cancellation from true stability, (2) ranking instability across calibration seeds as a first-class result, (3) power and certification requirements for compression comparisons, and (4) a released per-item artifact enabling reanalysis. Relative to the general eval-statistics work, the contribution is applying that rigor specifically to the compression-ranking problem, which those papers do not address.

## Claims (testable)

- **H1 (net vs gross).** Aggregate accuracy delta measures net change and can be near zero because harmful and beneficial flips cancel, while gross behavioral churn on the same inputs remains large. The two are different quantities and should be reported separately.
- **H2 (underpowered, unstable ranking).** At common benchmark sizes, the power to detect compression degradation and to order methods is low; method rankings shift under resampling, seed, and calibration-data choice.
- **H3 (calibration-seed instability, the spike).** The calibration set used to fit the quantizer changes the method ranking as much as or more than the choice of method itself. If this holds, current single-run compression comparisons are not reproducible in a way the field has not acknowledged.

## Metric decomposition

For paired baseline-vs-compressed evaluation on n items, with b = baseline-correct/compressed-wrong (harmful flip) and c = baseline-wrong/compressed-correct (beneficial flip):

- net accuracy delta = (c − b) / n
- accuracy-state churn = (b + c) / n  (gross movement that accuracy nets out)
- wrong-to-different-wrong churn: both wrong, different answer (invisible to accuracy, behaviorally real)
- total answer churn: any change in emitted answer

The money insight: two configurations can be "accuracy-equivalent" yet far apart in gross churn, and their ranking by net delta can be an artifact of noise.

## Contribution

1. A churn decomposition (harmful / beneficial / wrong-to-wrong) plus a paired, adequately-powered evaluation protocol for compressed models.
2. A ranking-stability analysis quantifying how often method order flips under resampling, seed, and calibration set.
3. Power and certification tables: the benchmark size required to detect a given degradation and to certify degradation below a chosen margin.
4. Released per-item outputs and code so results are reproducible and reanalyzable.

## Pilot (first ~2 weeks, go/no-go)

Confirm the effect on a minimal slice before committing.

- Models: Qwen2.5 1.5B and 7B.
- Methods: FP16 baseline, GPTQ 4-bit, AWQ 4-bit.
- Benchmarks: MMLU subset (multiple choice) and GSM8K (generative).
- Measure: net accuracy delta and full churn decomposition for each pair; bootstrap the test set to get CIs and the minimum detectable accuracy difference; recompute the GPTQ-vs-AWQ ranking across bootstrap resamples and across 3 calibration seeds.

**Pass if at least two hold:** accuracy delta within ~1-2 points while total churn is materially higher (roughly >=8-10%); harmful and beneficial flips substantially cancel; GPTQ-vs-AWQ ranking changes in >=20-30% of resamples or across calibration seeds; at least one benchmark needs 2x-5x more items to detect the observed degradation. If only "methods look similar and churn is low," downgrade to a workshop or tooling paper.

## Full study scope (disciplined for a solo author)

- Model families: Qwen2.5 and Llama-3 (or 3.1).
- Sizes: one small + one 7B/8B per family.
- Methods: RTN, GPTQ, AWQ.
- Bit widths: 4-bit and 3-bit.
- Benchmarks: MMLU, ARC-Challenge, HellaSwag, GSM8K.
- 5 calibration seeds per method, exact per-item logs released.
- Appendix (only if time allows): NF4, Pythia scaling, TruthfulQA, one open-ended generation eval. Keep any LLM-as-judge result secondary.

Depth over breadth: more replication, not more benchmarks.

## Statistical plan

- Do not say "statistically equal." Use TOST equivalence testing within a pre-specified margin to claim accuracy-preservation.
- McNemar's test for paired binary accuracy differences.
- Bootstrap CIs for all deltas and churn rates; hierarchical bootstrap over items and calibration seeds.
- Multiple-comparison correction across the model-method-benchmark grid.

Rigor is the paper's credibility, so this section carries the most weight. As a solo author you have no second reader to catch a stats error, so pre-register the analysis choices before running the full sweep and do not adjust them after seeing results.

## Compute

Inference only, no training. Pilot fits comfortably on Georgia Tech ICE for free. Full study: an estimated few hundred GPU-hours, requestable through PACESHIP (no credit expiry, cycle open) so out-of-pocket cost is near zero. Update the estimate with real per-model timings from the pilot before requesting.

## Target venues and timeline

Primary: **COLM** (evaluation and efficiency are core topics; deadline historically late March). Backup: **NeurIPS Datasets & Benchmarks** track (deadline ~May). Floor: a workshop version as an early, citable result. Sequence one archival venue at a time (dual submission is prohibited), with a non-archival workshop in parallel.

## Solo-author risk note

The one failure mode that most needs a human is novelty collision, and going solo means it is entirely on you. Before committing past the pilot, run a thorough related-work sweep on compressed-model evaluation, flips, prediction churn, and eval statistics, and write the positioning section against the closest three papers. That is the check a coauthor would have provided; do it deliberately.
