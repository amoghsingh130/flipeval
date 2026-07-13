# Related-Work Sweep Checklist

Human review is required for relevance, novelty judgments, and final citations.

## Sources and Venues

- [ ] arXiv `cs.CL`, 2025-2026
- [ ] arXiv `cs.LG`, 2025-2026
- [ ] ACL, EMNLP, NAACL, EACL, COLM proceedings
- [ ] NeurIPS, ICML, ICLR, MLSys proceedings
- [ ] NeurIPS Datasets & Benchmarks track
- [ ] TMLR and JMLR
- [ ] EleutherAI lm-evaluation-harness issues, pull requests, and release notes
- [ ] Model compression library papers/model cards for GPTQModel, AutoAWQ, SparseGPT, and Wanda
- [ ] Forward and backward citation search from every directly overlapping paper

## Queries

- [ ] `("flip rate" OR "prediction flip" OR "answer churn") AND (quantization OR compressed language model)`
- [ ] `("calibration set" OR "calibration data") AND sensitivity AND (GPTQ OR AWQ)`
- [ ] `(calibration seed OR sample seed) AND quantization AND LLM`
- [ ] `benchmark statistical power AND (LLM OR language model evaluation)`
- [ ] `McNemar AND LLM evaluation`
- [ ] `equivalence test OR TOST AND language model evaluation`
- [ ] `paired bootstrap AND model ranking instability`
- [ ] `minimum detectable difference AND benchmark evaluation`
- [ ] `compression evaluation per-item logs`
- [ ] `SparseGPT OR Wanda AND calibration sensitivity`

For each query, record the exact search date, database, filters, result count, screened count, and exclusion reason. Search title/abstract variants for "behavioral consistency," "disagreement," "prediction instability," and "rank robustness," since directly relevant work may not use "flip."

## Evidence Table

| Paper | What it shows | Overlap with H1/H2/H3 | Our differentiation |
|---|---|---|---|
| Dutta et al., *Accuracy is Not All You Need* (NeurIPS 2024) | Compressed models can match baseline accuracy while flipping many individual answers; proposes flips and KL divergence as complementary metrics. | Direct H1 antecedent; motivates per-item analysis. Does not establish our H2 power/rank-stability protocol or H3 calibration-seed effect. | Do not claim that flips are novel. Contribute net-versus-gross decomposition, calibration-seed ranking instability, paired power/certification requirements, and a released reanalysis artifact. |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## Completion Checks

- [ ] Verify title, author list, venue, year, DOI/arXiv ID from primary sources.
- [ ] Read methods and limitations, not only abstracts.
- [ ] Separate compression-specific work from general evaluation-statistics work.
- [ ] Identify any paper with controlled calibration seeds or datasets.
- [ ] Identify any existing equivalence-testing or sample-size certification tool.
- [ ] Update positioning and preregistration only through a dated amendment if the main grid has begun.
