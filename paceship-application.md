# EVPR-PACESHIP Application: Statistically Sound Evaluation of Compressed Language Models

Applicant: Amogh Singh (asingh3206@gatech.edu)
Status: Undergraduate, Computer Science, College of Computing. Enrolled full-time; expected graduation May 2029.
Application type: Individual student project (no faculty advisor for this project).
GitHub: github.com/amoghsingh130

---

## Project summary (plain language)

Large language models are routinely "compressed" so they can run on cheaper hardware: their numerical weights are stored with less precision (quantization) or partially removed (pruning). Before a compressed model is deployed, engineers check that its benchmark accuracy is close to the original model's, and if the difference is a point or two, the compressed model is declared safe to use.

My project tests whether that standard check is trustworthy, and builds public tools so anyone can do the check correctly. In a pilot study I completed this month on free cloud GPUs, I found early evidence that it is not trustworthy: a compressed model matched the original's overall math-benchmark score within 1-2 points, yet changed its answer on nearly two thirds of the individual questions, and roughly a quarter of the questions flipped between right and wrong. The overall score looked stable only because errors introduced and errors fixed happened to cancel. My statistical analysis also showed that the benchmark sizes commonly used in practice would need to be 8x to 87x larger to reliably detect the differences I measured, and that the ranking of two popular compression methods flipped in 42% of statistical resamples of the same data.

The full study will answer one more question the pilot could not: compression methods are tuned using a small random sample of text called a calibration set. If simply re-drawing that random sample changes which compression method looks best, then many published comparisons of compression methods are effectively irreproducible. Testing this requires building many compressed model variants myself with controlled random seeds, which is the main computational cost of this project.

The project releases three public artifacts: (1) a dataset of per-question records showing exactly which questions every compressed model variant got right, wrong, or changed; (2) an open-source analysis tool that plugs into the community-standard evaluation framework (lm-evaluation-harness) and reports the correct statistics; and (3) practical reference tables telling engineers how many test questions are needed to certify a compressed model to a given tolerance. Target publication venue: NeurIPS Datasets & Benchmarks, with COLM as an alternative.

## Alignment with my studies and experience

I am a CS undergraduate concentrating in machine learning and systems. I work as an ML research assistant in Georgia Tech's Systems for AI Lab on a quantization pipeline (this proposal is independent of and separate from my lab work), and I have prior industry internship experience deploying INT8-quantized models with TensorRT, where the "is the compressed model really as good?" question arose in practice. I have one prior first-author publication (deep-learning image classification). This project is the centerpiece of my independent research training: experiment design, statistical analysis, reproducibility engineering, and open-source release.

## What Georgia Tech and the broader community gain

- Open-source tooling and a public dataset that any research group evaluating compressed or otherwise modified models can use, including groups at Georgia Tech; the evaluation-statistics tool is general beyond compression.
- A reproducibility contribution consistent with Georgia Tech's visibility in ML systems research, and a planned peer-reviewed publication crediting PACE and the PACESHIP program.
- Practical guidance (sample-size tables) for engineers deploying compressed models on constrained hardware, a topic of wide industrial relevance.
- A written report to the PACESHIP committee, and I am glad to present the work to PACE or student groups if useful.

## Why PACE is needed

The pilot ran on free Kaggle GPUs (2x NVIDIA T4) and exhausted what that environment can do. Two hard blockers make PACE necessary for the full study. First, the main experiment requires building roughly 110 compressed model checkpoints with controlled random seeds; the required quantization software does not install reliably in Kaggle's fixed environment (documented in my pilot logs), and the environment cannot be pinned or containerized for reproducibility. Second, the study includes 7-8B-parameter models and one 70B-parameter validation run that exceed Kaggle's memory and session limits. PACE Phoenix provides the pinnable, containerized (Apptainer), SLURM-scheduled environment with suitable GPUs that this work requires.

## Computational plan and resource request

All time estimates are extrapolated from measured pilot timings on Kaggle T4 GPUs (e.g., 13.6 seconds per generated math answer for a 1.5B model; 2.5-4.3 multiple-choice items scored per second), scaled by standard T4-to-A100 throughput ratios, then padded 2x for failures, debugging, and re-runs.

Workload:

1. Checkpoint construction: ~110 compressed variants of four models (Qwen2.5 1.5B/7B, Llama 3.2 small / 3.1 8B) across four compression methods, two precision settings, and five calibration seeds each where applicable. Estimated 100 A100-hours.
2. Evaluation: each variant plus baselines evaluated on four standard benchmarks (MMLU, ARC-Challenge, HellaSwag, GSM8K) with per-question logging. Estimated 340 A100-hours; generation-based benchmarks dominate.
3. One 70B-parameter validation run (original vs. publicly available compressed version, evaluation only) to check whether findings hold at scale. Estimated 60 A100-hours; requires one 80GB-class GPU (A100 80GB or H100/H200) or two 40GB GPUs for the uncompressed baseline.
4. Statistical analysis and packaging: CPU-only, negligible.

Requested allocation:

- Compute: 1,000 A100-equivalent GPU-hours (approximately 500 estimated + 2x contingency), usable flexibly across Phoenix GPU types; the majority of jobs fit a single 32-40GB GPU, with a small number of 80GB-class jobs for the 70B validation run. I am happy to use preemptable/backfill queues for the embarrassingly parallel evaluation jobs, which are checkpointed per-item and restart cleanly.
- Storage: 1 TB project storage at peak (model checkpoints, ~5-15 GB each, deleted after evaluation; per-question logs and archives are small), plus normal scratch usage. I will release final artifacts externally (HuggingFace/Zenodo) and free PACE storage at project end.
- Duration: 6 months, with usage concentrated in months 2-5.

## Timeline

- Month 1: environment setup (Apptainer container, pinned dependencies), bridge run reproducing the pilot in the controlled environment, pre-registered analysis plan committed publicly.
- Months 2-3: calibration-seed experiment on the two small models (the core new result); checkpoint construction for larger models.
- Months 4-5: full evaluation grid, 70B validation run, dataset assembly.
- Month 6: analysis, open-source releases, paper writing; PACE storage cleanup and final report to the PACESHIP committee.

## Software and technical readiness

All pipeline code exists and is smoke-tested end to end (per-item evaluation runner, statistical analyzer, packaging scripts), validated in the completed pilot with archived, checksummed outputs. Stack: Python, PyTorch, HuggingFace Transformers, GPTQModel/AutoAWQ, lm-evaluation-harness, SLURM batch jobs, Apptainer containers. I have prior experience with batch scheduling and reproducible environment management from ML systems internships and lab work.

## Reporting

I will provide the required written report on outcomes and PACE usage, acknowledge PACE and the EVPR-PACESHIP program in the resulting publication and released artifacts, and am available to share the experience with PACE as requested.
