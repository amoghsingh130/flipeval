# Paper Proposal v3: FlipEval — A Benchmark, Atlas, and Tool for Statistically Sound Compression Evaluation

Target venue: NeurIPS Datasets & Benchmarks (primary), COLM (backup), workshop (floor).
Author: Amogh Singh, Georgia Tech. Solo-authored.
Status: pilot passed (Kaggle public-checkpoint run, 2026-07-10). This proposal supersedes compression-eval-proposal-v2.md.

---

## 1. One-sentence pitch

Point-accuracy deltas are the standard evidence that a compressed LLM is "near-lossless," but they are statistically incapable of supporting that claim at common benchmark sizes; we release the first large-scale per-item atlas of compression-induced behavioral change, a drop-in statistical toolkit integrated with lm-evaluation-harness, and empirically derived sample-size tables that tell practitioners exactly how much evaluation is enough.

## 2. Why this is a D&B paper, not a findings paper

D&B reviewers reward artifacts with a life after the paper. The findings (churn, underpowered benchmarks, seed instability) are the motivation and validation; the contributions are three reusable artifacts:

1. **The Compression Flip Atlas (dataset).** Per-item paired records for every cell of the study grid: prompt hash, gold answer, prediction, correctness state, logprobs/answer scores, model, method, bit width, calibration seed, software environment fingerprint. Every claim in the paper is recomputable from the atlas, and the atlas supports questions we never asked (item-level fragility prediction, cross-family transfer of flips, calibration-data attribution).
2. **flipeval (tool).** A pip-installable package plus an lm-evaluation-harness integration that takes two (or N) per-item result files and emits: harmful/beneficial flip rates, accuracy-state churn, wrong-to-different-wrong churn, total answer churn, McNemar tests, TOST equivalence at a declared margin, bootstrap CIs, item-bootstrap rank-flip rates, minimum detectable difference, and required-n. Goal state at submission time: an open or merged PR into lm-evaluation-harness adding a `compare` mode.
3. **Certification tables (reference).** Empirically derived lookup tables: "to certify a compressed model within delta points of baseline on benchmark B at 95% confidence, evaluate at least N items." Computed from observed flip-rate distributions rather than idealized binomial assumptions, per benchmark and per margin.

## 3. Scientific claims (kept from v2, now with pilot evidence)

- **H1 (net vs gross):** aggregate accuracy delta measures net change and can be near zero while gross per-item churn is large. Pilot: GSM8K net delta +1 to +2 points while 22-25% of items flipped correctness state and 62-63% of generations changed answers.
- **H2 (underpowered, unstable ranking):** common benchmark sizes cannot detect observed deltas or stably order methods. Pilot: detecting the observed GSM8K deltas at 80% power requires 4,900-17,300 items (25-87x the evaluated subset); GPTQ-vs-AWQ winner flips in 42% of item bootstraps on GSM8K and flips across tasks.
- **H3 (calibration-seed instability, the headline if it lands):** the calibration sample used to fit the quantizer changes method rankings as much as or more than the method choice, making single-run comparisons effectively non-reproducible. Untested in the pilot (public checkpoints have fixed calibration); this is the core new experiment.
- **Discriminant validity:** the framework distinguishes real damage from noise. Pilot: MMLU GPTQ-Int4 showed statistically significant degradation (McNemar p=0.036) under the same analysis that certified GSM8K deltas as noise. This preempts the reviewer objection that the method labels everything as noise.

## 4. Study design (impact-maximized; time budget explicitly deprioritized)

### 4.1 Grid

- **Families/sizes (4 models):** Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct (or 3B), Llama-3.1-8B-Instruct.
- **Scale anchor (1 model, evaluation only):** one 70B-class model (Llama-3.1-70B-Instruct) at FP16 vs public INT4, on a benchmark subset. This does not extend the seed grid; it exists solely to answer "does this hold at scale?" with data instead of hand-waving. Single most valuable addition per GPU-hour for reviewer defense.
- **Methods (4):** RTN (seed-free control), GPTQ, AWQ, plus one pruning method (SparseGPT or Wanda, 2:4 sparsity). Pruning generalizes the artifact from "quantization eval" to "compression eval" and doubles the audience for one integration.
- **Bit widths:** 4-bit and 3-bit for quantizers; one sparsity setting for pruning.
- **Calibration seeds:** 5 per calibration-dependent method/bit/model cell. Additionally, 2 calibration *datasets* (e.g., C4 vs WikiText-2 samples) on one model to separate seed variance from calibration-distribution variance — this is a distinct, quotable H3 sub-result.
- **Benchmarks:** MMLU (full or large stratified subset), ARC-Challenge, HellaSwag (subset), GSM8K (>= 1,000 items — the pilot's power analysis says small GSM8K subsets are the least informative, so spend generation budget here).

Checkpoint count: per model, GPTQ (2 bits x 5 seeds) + AWQ (2 bits x 5 seeds) + RTN (2) + pruning (1 x 5 seeds where calibration-dependent) ≈ 27; x4 models ≈ 108 compressed checkpoints + 4 baselines. Every checkpoint's calibration sample indices, seed, and environment lockfile are recorded in the atlas.

### 4.2 Rigor requirements (non-negotiable, learned from the pilot)

- Chat template applied correctly per family (pilot ran raw prompts; absolute accuracy was ~15 points below published numbers — acceptable for paired pilot evidence, unacceptable for the atlas).
- Pinned environment: containerized (Apptainer on PACE), lockfile published, GPU kernel/backend recorded per run (the pilot's GPTQ ran via GPTQModel TorchLinear after v1-to-v2 conversion — exactly the kind of detail the atlas must capture, since kernels are a nuisance variable).
- Manifest merging bug fixed; manifests are append-only records of every method/task run.
- Pre-registered analysis plan committed to the repo before the main grid runs (reviewers reward this; it also protects against garden-of-forking-paths criticism).

### 4.3 Audit component (teeth, framed constructively)

Re-analyze 5-10 published "near-lossless" compression claims (papers and model cards) at their reported sample sizes using flipeval's power analysis: what fraction of published comparisons could not have detected their own claimed equivalence? Framed as "the field lacks reporting standards and here is the fix," not "these papers are wrong." One memorable number for the abstract.

## 5. D&B hygiene checklist (graded explicitly by reviewers)

- Datasheet for the atlas (Gebru et al. format).
- Croissant metadata; hosted on HuggingFace Datasets with DOI via Zenodo.
- License: CC-BY-4.0 for the atlas, Apache-2.0 for flipeval.
- Maintenance statement (12-month commitment, issue tracker, versioned releases).
- Full reproducibility package: configs, lockfiles, SLURM scripts, per-run manifests.
- Author statement addressing dual-use and dataset limitations honestly (small-to-8B models, English benchmarks, instruct variants only).

## 6. What was cut and why

- LLM-as-judge / open-ended generation evals: subjective, adds reviewer attack surface, not needed for the claims.
- More small models on the same benchmarks: adds compute without changing the paper.
- NF4/bitsandbytes and Pythia scaling: appendix-only if trivially cheap, else cut.

## 7. Risks and mitigations

- **H3 shows stability (seeds don't matter):** the paper survives as atlas + tool + power tables + "seeds are safe, sample sizes are not" — still a D&B paper. This proposal is deliberately robust to H3's outcome.
- **Scooped on seed instability:** post an arXiv preprint as soon as the H3 grid completes on the two small models, before the full grid finishes.
- **Solo-author blind spots:** recruit 2-3 rounds of pre-submission review from a GT professor or senior PhD student (not co-authorship; acknowledged reviewers). Budget 3 weeks for this before the deadline.
- **Harness PR not merged in time:** an open PR with maintainer engagement is still citable evidence of adoption path; also publish the standalone package regardless.

## 8. Milestones

1. Bridge run: rerun pilot config in pinned PACE environment with chat template fix; confirm churn signals survive. Go/no-go for the grid.
2. H3 mini-grid: 2 small models x GPTQ/AWQ x 4-bit x 5 seeds. If instability appears, preprint immediately.
3. Full grid + atlas assembly.
4. 70B anchor run + audit component.
5. flipeval release + harness PR.
6. Writing, external review rounds, D&B checklist, submit.

## 9. Honest odds assessment

Base D&B acceptance ~25-30%. This design, well executed with the atlas + tool + certification tables + discriminant-validity story, is estimated at 35-45%. H3 landing positively adds headline value but the paper no longer depends on it. The binding constraints on the upside are solo-author framing risk (mitigated by external review rounds) and model scale (mitigated by the 70B anchor).
