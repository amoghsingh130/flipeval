# Project Handoff: Independent Research Paper on Compressed-LLM Evaluation

Last updated: 2026-07-10. This document is a self-contained context primer. Reading only this should be enough to understand the project's goal, every decision made so far and why, the current paper concept, the literature landscape, the compute and venue plan, the code now in the repo, and the exact next steps.

---

## 1. Who and what

**Person:** Amogh Singh, CS undergraduate at Georgia Tech (expected graduation May 2028). ML Research Assistant at Georgia Tech's Systems for AI Lab (SAIL). Contact: asingh3206@gatech.edu, GitHub github.com/amoghsingh130, LinkedIn linkedin.com/in/amoghsingh41.

**Relevant background/assets:**
- ML systems: LLM quantization, TensorRT/INT8 inference.
- Systems software: Rust, distributed systems, deterministic distributed-systems testing, reproducibility engineering.
- At SAIL: works on a GPTQ quantization pipeline and ablations (this is his lab work and is SEPARATE from the project below).
- Existing first-author publication: emotion detection via deep-learning image classification (comparing CNN, ResNet-50, DenseNet-121, ViT on the FER2013 dataset), mentored by Yiqiao Yin (then a Columbia instructor, now an industry AI engineer). This is a solid first, student-tier applied study, and is not the paper below.

**Goal:** Produce an INDEPENDENT research paper (separate from SAIL and from the emotion-detection paper) and get it published at a top-tier venue (NeurIPS/ICML class, or the realistic equivalents identified below).

---

## 2. How the topic was chosen (decision trail)

The framing narrowed in stages. Each step was a deliberate decision:

1. **Not "getting into ML."** He is already an active researcher; the real move was converting research momentum into an independent publication, not building a study plan.
2. **Lane chosen: evaluation methodology** (over quantization/efficiency, reproducibility studies, and systems-for-ML infra). Reasoning: cheapest compute, best effort-to-acceptance ratio for a solo author, and it plays to a finding he already saw at SAIL (evaluation conclusions reversing between small-sample and full-benchmark runs). Evaluation is a lane where cleverness beats compute.
3. **Within eval methodology, Route D chosen: evaluation of compressed/quantized models.** Reasoning: uses his quantization expertise as a moat that pure eval researchers lack, while staying independent of SAIL's specific method.
4. **Specific concept:** originally "behavioral churn + statistical power." After a critical review and a literature check, reframed to be collision-aware (see Sections 4 and 5).
5. **Solo author.** He explicitly decided against an advisor or coauthor, including declining to bring in his prior mentor Yin, choosing ownership and independence over the higher acceptance odds a coauthor would provide. Consequence: the novelty-collision check is entirely his responsibility (see Section 8).

---

## 3. Two exemplar papers that define the genre he's aiming for

These are the templates for "the measurement was wrong" eval-methodology papers, and were studied as models:

- **Card et al., "With Little Power Comes Great Responsibility"** (EMNLP 2020). Argues much NLP evaluation is statistically underpowered: test sets too small to reliably detect the effects claimed. Underpowering both hides real gains and inflates the significant results that survive. Example: a 2,000-sentence MT test set has ~75% power to detect a 1 BLEU difference. Ships power-analysis notebooks.
- **Schaeffer et al., "Are Emergent Abilities of LLMs a Mirage?"** (NeurIPS 2023). Argues "emergent abilities" are largely an artifact of harsh, nonlinear metrics; the underlying per-token improvement is smooth. Switching to linear metrics erases the apparent jumps. They even induce fake "emergence" in vision models by choosing a nonlinear metric.

Common template: take a widely trusted claim, show it's an artifact of power or metric, back it with clean controlled experiments plus a turn-it-on-and-off demonstration.

---

## 4. Critical novelty collision (the most important thing in this document)

**A prior paper already did the naive version of the idea.** Dutta et al., **"Accuracy is Not All You Need"** (NeurIPS 2024, Microsoft Research), established that compressed models can preserve aggregate accuracy while changing many individual answers, named the phenomenon "flips," proposed flips and KL-divergence as metrics, and studied it across six quantization schemes, multiple model families, and seven benchmarks. It also covers free-form generation (MT-Bench, GPT-4 judge).

**Implication:** the paper CANNOT claim to discover churn/flips. Doing so would be desk-rejected or savaged on novelty. This collision was verified directly against the paper, not assumed.

**Secondary collisions:** recent eval-statistics papers (paired-evaluation "resolution diagnostics," and a package called evalci) are bringing paired tests, confidence intervals, and power analysis to LLM evaluation in general. So the generic "we brought statistical rigor to eval" angle is also getting crowded. Surviving novelty must be the specific intersection: rigor applied to the compression-ranking problem.

**Adjacent work to cite and differentiate from:** LLMC (a quantization-benchmarking toolkit; adjacent, not the same contribution); the older "prediction churn" literature (churn from training randomness, predictive churn under model updates, cross-sample churn); and the compression-trust/safety wave (e.g., "Decoding Compressed Trust," and alignment-aware quantization work noting perplexity is a misleading proxy).

---

## 5. Current paper concept (v2, collision-aware)

**Working title:** "Ranking Quantized LLMs Is Harder Than It Looks: Statistical Power, Calibration-Seed Instability, and Behavioral Churn in Compressed-Model Evaluation." (The earlier catchy title "When Accuracy Lies" was retired for sounding bloggy and echoing the prior paper's thesis.)

**Positioning:** not "flips exist." The contribution is (1) a net-versus-gross decomposition, (2) ranking instability across calibration seeds as a first-class result, (3) power and certification requirements for compression comparisons, and (4) a released per-item artifact for reanalysis.

**Claims:**
- **H1 (net vs gross):** aggregate accuracy delta measures NET change and can be near zero because harmful and beneficial flips cancel, while GROSS behavioral churn on the same inputs stays large. Different quantities; report both.
- **H2 (underpowered, unstable ranking):** at common benchmark sizes, power to detect degradation and to order methods is low; rankings shift under resampling, seed, and calibration data.
- **H3 (calibration-seed instability, the "spike"):** the calibration set used to fit the quantizer may change the method ranking as much as or more than the choice of method. If true, current single-run compression comparisons are effectively not reproducible. THIS is the potential main-track-caliber finding and the thing to hunt hardest in the pilot.

**Metric decomposition** (paired baseline vs compressed, n items; b = baseline-correct/compressed-wrong = harmful flip; c = baseline-wrong/compressed-correct = beneficial flip):
- net accuracy delta = (c − b) / n
- accuracy-state churn (gross) = (b + c) / n
- wrong-to-different-wrong churn: both wrong, different answer (invisible to accuracy)
- total answer churn: any change in emitted answer

**Contribution deliverables:** churn decomposition + paired powered protocol; ranking-stability analysis; power/certification tables (test size needed to detect a given degradation and to certify below a margin); released per-item logs and code.

---

## 6. Statistical plan (the credibility core)

- Never say "statistically equal." Use **TOST equivalence testing** within a pre-specified margin to claim accuracy-preservation.
- **McNemar's test** for paired binary accuracy differences.
- **Bootstrap CIs** for all deltas and churn rates; **hierarchical bootstrap** over items and calibration seeds.
- **Multiple-comparison correction** across the model x method x benchmark grid.
- **Pre-register** the analysis choices before running the full sweep. Because he is solo, there is no second reader to catch a stats decision made after seeing results, so this is a hard rule.

---

## 7. The pilot (the go/no-go gate) and full-study scope

**Pilot (~2 weeks, free-GPU path now available through Kaggle; ICE/PACE remains the cleaner full-study route):**
- Models: Qwen2.5 1.5B and 7B.
- Methods: FP16 baseline, GPTQ 4-bit, AWQ 4-bit.
- Benchmarks: MMLU subset (multiple choice) + GSM8K (generative).
- Measure: net accuracy delta and full churn decomposition per pair; bootstrap CIs and minimum detectable difference; recompute GPTQ-vs-AWQ ranking across bootstrap resamples and across 3 calibration seeds.
- **PASS if at least two hold:** accuracy delta within ~1-2 points while total churn is materially higher (roughly >=8-10%); harmful and beneficial flips substantially cancel; GPTQ-vs-AWQ ranking changes in >=20-30% of resamples or across calibration seeds; at least one benchmark needs 2x-5x more items to detect the observed degradation.
- **If it fails** (methods look similar and churn is low): downgrade to a workshop or tooling paper rather than a main-track submission.

**Pilot code status:** pilot code now exists. It is a per-item logging pipeline plus an analyzer:
- `pilot_eval/run.py` runs configured baseline/compressed methods and writes JSONL records per method/task.
- `pilot_eval/tasks.py` loads MMLU and GSM8K and performs simple answer extraction.
- `pilot_eval/modeling.py` loads Hugging Face causal LMs, scores multiple-choice answers by log likelihood, and runs deterministic GSM8K generation.
- `pilot_eval/analyze.py` consumes JSONL logs and writes `pair_summary.csv` and `rank_instability.csv`.
- The analyzer reports net accuracy delta, harmful/beneficial flips, gross accuracy-state churn, wrong-to-different-wrong churn, total answer churn, bootstrap CIs, McNemar p-values, TOST equivalence outputs, rough minimum detectable difference, required n for the observed delta, item-bootstrap rank flip rates, and seed-wise method winner changes.

**Important pilot caveat:** the strongest claim, H3 calibration-seed instability, cannot be established from public quantized checkpoints alone. The quantized checkpoints must be built locally with known calibration seeds. The helper script `scripts/build_quantized.py` supports GPTQ/AWQ checkpoint construction, but depends on optional quantization backends (`auto-gptq`, `autoawq`) and may need backend-specific fixes once run on the actual GPU environment.

**Full study scope (kept disciplined for a solo author, depth over breadth):**
- Families: Qwen2.5 and Llama-3 (or 3.1); sizes: one small + one 7B/8B each.
- Methods: RTN, GPTQ, AWQ. Bit widths: 4-bit and 3-bit.
- Benchmarks: MMLU, ARC-Challenge, HellaSwag, GSM8K.
- 5 calibration seeds per method; exact per-item logs released.
- Appendix only if time allows: NF4, Pythia scaling, TruthfulQA, one open-ended generation eval (any LLM-as-judge result kept secondary).

---

## 8. Biggest risk

Novelty collision, and it is entirely on him because he chose to go solo. Required mitigation before committing past the pilot: a thorough related-work sweep on compressed-model evaluation, flips, prediction churn, and eval statistics, plus a written positioning section against the closest three papers. This is the check a coauthor would have provided.

---

## 9. Compute plan

All work is inference/quantization only (running models and building compressed checkpoints, not training), so it is cheap. He is NOT paying for cloud; the plan is free resources.

- **Immediate pilot path:** Kaggle Notebooks with free GPUs. This is now implemented as a practical first path because it is quick to access. Use Kaggle for the Qwen2.5 1.5B pilot and treat 7B as opportunistic depending on assigned GPU memory/quota. Kaggle is not the final full-study compute plan.
- **Original pilot path:** Georgia Tech ICE (Instructional Cluster Environment) / AI Makerspace. Free, no application, course-gated access, shared and lower-priority but fine for the small pilot.
- **Full study:** **PACESHIP** (EVPR-PACE Student HPC Innovation Program) on the Phoenix research cluster. This is the route for students without a faculty sponsor, which fits an independent project. Program facts: administrator Grigori Yourganov; cycle listed 2025-2026; unlimited awardees; $200k total pool; up to 5 applications per applicant; ~2-week review.
- **Confirmed by Grigori (via email):** compute credits do NOT expire, and the cycle is open now. So there is no deadline pressure and no risk of credits expiring before the spring 2027 submission window.
- **Grigori's role:** he is the COMPUTE ally, not a paper reviewer. His background is neuroimaging and HPC facilitation, not LLM evaluation, so he is not the person to vet novelty or advise on the research.
- Reference numbers used so far are placeholders (a few hundred GPU-hours). These must be replaced with real per-model timings from the pilot before submitting the PACESHIP application.

**Kaggle implementation details:**
- `KAGGLE.md` is the runbook.
- `notebooks/kaggle_pilot.ipynb` is a Kaggle-ready notebook.
- `configs/kaggle_smoke_tiny.yaml` and `configs/kaggle_qwen_1p5b.yaml` use `/kaggle/working` paths so outputs survive when saving a Kaggle version.
- `scripts/kaggle_bootstrap.py` copies the project from read-only `/kaggle/input` into writable `/kaggle/working/compression-eval`, installs requirements, and optionally installs quantization backends.
- `scripts/kaggle_pack_outputs.py` packages result files into a tarball.
- `scripts/make_kaggle_bundle.py` builds a clean private Kaggle Dataset upload bundle. It has already produced `dist/kaggle_dataset.zip`.

**Sequencing decision:** run the pilot FIRST, preferably on Kaggle for speed and/or ICE if Kaggle quota/backend issues get in the way, then submit PACESHIP with measured timings. Reasons: no credit expiry means no rush; a measured estimate is more credible to the review committee; and the pilot is the go/no-go, so applying before it risks requesting for a study that may change shape or not run. (Applying now is harmless given no expiry, but it's the weaker move.)

---

## 10. Venue strategy and rules

**Targets, in order:**
- **Primary: COLM 2027** (Conference on Language Modeling). Evaluation protocols/metrics/benchmarks and efficiency are explicitly core topics, so it's the most natural home. Deadline historically late March (2026 was Mar 31), so expect ~late March 2027. Comfortable runway.
- **Backup: NeurIPS 2027 Datasets & Benchmarks track.** Built for evaluation/benchmark methodology; shares the main deadline (~May).
- **Floor: a workshop** (non-archival), as an early citable result.
- **ICML 2027** (deadline ~late January 2027) is possible only if the pilot comes together fast.
- **ICLR 2027** (deadline ~late September 2026) is too soon; skip.
- **NeurIPS 2026** already closed (May 2026).
(2027 dates are predicted from historical patterns and must be verified on each venue's site.)

**Submission rules (verified):**
- Dual/concurrent submission to two archival venues is PROHIBITED and enforced (desk rejection). Submit to one at a time.
- Sequential is fine: rejected or withdrawn from A, then submit to B. Normal practice.
- A non-archival workshop version can run in parallel with a main submission.
- arXiv preprints are allowed and don't count as dual submission.
- Cannot slice one contribution into two overlapping papers.

**Odds context (calibrated, not precise):** top venues run ~25-35% overall acceptance; a solo first paper is below that per submission (roughly mid-teens if strong), but review is double-blind so seniority is invisible, and cumulative odds across 2-3 submission cycles over 12-18 months are much better. Treat publication as a multi-cycle process, not one coin flip.

---

## 11. Files produced so far

- `compression-eval-proposal.md` (v1) — SUPERSEDED.
- `compression-eval-proposal-v2.md` — CURRENT proposal (collision-aware reframe).
- `PILOT.md` — local/ICE-oriented pilot runbook and critique.
- `KAGGLE.md` — Kaggle setup/runbook.
- `requirements.txt` — core Python runtime requirements.
- `.gitignore` — excludes venvs, caches, results, checkpoints, and generated bundles.
- `pilot_eval/` — pilot evaluation package:
  - `config.py` loads YAML configs.
  - `tasks.py` loads MMLU/GSM8K and extracts answers.
  - `modeling.py` loads models and evaluates individual items.
  - `run.py` writes per-item JSONL logs.
  - `analyze.py` computes churn/ranking/power statistics.
- `configs/` — run configs:
  - `smoke_tiny.yaml` and `kaggle_smoke_tiny.yaml` for plumbing tests.
  - `pilot_qwen_1p5b.yaml` for local/ICE paths.
  - `kaggle_qwen_1p5b.yaml` for Kaggle paths.
- `scripts/build_quantized.py` — local GPTQ/AWQ checkpoint builder for calibration-seed sweeps.
- `scripts/kaggle_bootstrap.py` — Kaggle staging/install helper.
- `scripts/kaggle_pack_outputs.py` — Kaggle result packaging helper.
- `scripts/make_kaggle_bundle.py` — local helper to create a clean Kaggle Dataset upload zip.
- `notebooks/kaggle_pilot.ipynb` — Kaggle notebook template.
- `kaggle/kernel-metadata.json` — Kaggle notebook metadata template.
- `dist/kaggle_dataset.zip` — generated clean upload bundle for Kaggle. This is ignored by git and can be regenerated.
- `scripts/slurm/` — SLURM helper files are present for cluster execution (`env.sh`, `build_quantized.sbatch`, `run_pilot.sbatch`, `README.md`).
- `paceship-application.md` — DRAFT application text was referenced earlier, but it is not currently present in this workspace. If needed, recreate/update it after measured GPU timings.
- Email to Grigori (sent and answered) and a drafted thank-you reply.
- `handoffv1.md` — this document.

---

## 12. Next steps (in order)

1. **Upload and smoke-test on Kaggle.** Upload `dist/kaggle_dataset.zip` as a private Kaggle Dataset, create a GPU notebook, attach the dataset, open/use `notebooks/kaggle_pilot.ipynb`, and run the smoke test. This verifies package installs, dataset downloads, model downloads, and per-item logging.
2. **Build a minimal quantized pair.** On Kaggle, build `gptq_s0` and `awq_s0` for Qwen2.5-1.5B using `scripts/build_quantized.py`. If either backend fails, fix backend-specific API issues before scaling seeds.
3. **Evaluate the minimal pair.** Run `pilot_eval.run` with `--only-method fp16 --only-method gptq_s0 --only-method awq_s0` or temporarily narrow `configs/kaggle_qwen_1p5b.yaml`; then run `pilot_eval.analyze`. This confirms the real model path before spending quota on all seeds.
4. **Build the remaining 1.5B seeds.** Build GPTQ/AWQ seeds 1 and 2, saving Kaggle versions after successful phases so outputs are preserved.
5. **Run the full 1.5B pilot analysis.** Run `python -m pilot_eval.run --config configs/kaggle_qwen_1p5b.yaml`, then `python -m pilot_eval.analyze --run-dir /kaggle/working/results/kaggle_qwen25_1p5b_pilot --baseline fp16 --bootstrap 2000`.
6. **Record timings and failure modes.** Save runtime, GPU type, memory pressure, dependency fixes, and whether Kaggle is sufficient for 7B. These numbers replace placeholder compute estimates.
7. **Do the related-work sweep** and draft the positioning section against the closest three papers (solo-author risk mitigation).
8. **Pre-register** the analysis choices before any full run beyond the pilot.
9. **Update/recreate the PACESHIP application** with real per-model timings from the pilot, then submit if the pilot passes.
10. **Run the full study** if the pilot passes; if it fails go/no-go, pivot to a workshop/tooling paper.
11. **Target COLM (~late March 2027)** as the primary submission, NeurIPS D&B (~May) as backup, workshop as floor.

**Immediate open question at handoff time:** run the Kaggle smoke test and first quantized-checkpoint build, then inspect whether `auto-gptq`/`autoawq` work cleanly on Kaggle's current GPU image.
