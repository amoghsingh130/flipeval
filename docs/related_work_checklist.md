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

## Sweep Record

**This section is the audit trail for the `\TODO` that `sections/related_work.tex`
carried until 2026-07-27.** It records what was actually screened, by whom, on
what date, against which database, with counts. It deliberately also records what
was *not* done, so that a reader can tell the difference between a screen that
found nothing and a screen that was never run. Paper-side prose may claim absence
only over the rows below.

### Pass A — concurrent-work sweep, 2026-07-24

Recorded in full in `docs/PRIOR_ART_CONCURRENT_2026-07-24.md`; summarised here so
the counts live in one place.

| date | database | target | screened | admitted | method |
|---|---|---|---|---|---|
| 2026-07-24 | arXiv (`cs.CL`, `cs.LG`, `cs.AI` listings) + web search | concurrent work on the five FlipEval legs | 4 read in full | 4 | raw arXiv HTML fetched directly, trigger terms (`TOST`, `equivalen*`, `power analys*`, `required…sample`, `mcnemar`, `seed`, `calibrat`) grepped exhaustively over extracted text |
| 2026-07-24 | OpenReview `pfw3saHzGU` | calibration-data selection paper | 1 | 0 (blocked) | Cloudflare-walled; every quote in that section remains `[to-verify]` and none may enter the paper |

Admitted from pass A: `2607.08734` (cited, §2.1), `2604.27405`, `2606.19558`,
`pfw3saHzGU`. **Not cited as of 2026-07-27:** `2604.27405` (Beyond the Mean) and
`2606.19558` (Displacement Is Not Direction) — both verified, both relevant as
adjacent corroboration, both left out of the current draft for length. Open
decision for the author, not an oversight.

### Pass B — citation verification, 2026-07-27

Every key in `paper/references.bib` was read from a primary source on this date.
Per-entry source URLs are in the comment above each entry. Hosts refusing the
cluster: `dl.acm.org`, `cacm.acm.org` (HTTP 403) — one entry affected
(`gebru2021datasheets`), its workaround recorded in the file.

| checked | count |
|---|---|
| placeholder keys resolved to verified entries | 15 |
| new entries added | 6 |
| entries whose *venue* changed from the placeholder | 9 (all preprint→published) |
| entries whose *title* was materially wrong in the placeholder | 2 (`llmaccuracystats2026`, `awq2023` — see below) |
| entries with an author list that was a stub (`X and others`) | 4 |
| fields left omitted rather than guessed | AWQ page range; Dutta page range |

Two corrections worth carrying forward:

- **`llmaccuracystats2026`.** The placeholder titled it *LLM-Accuracy-Stats*.
  That is the released tooling; the paper is *When LLMs get significantly worse:
  A statistical approach to detect model degradations* (Kübler et al.,
  ICLR 2026, arXiv:2602.10144). The arXiv ID recorded in the placeholder was
  correct.
- **`awq2023`.** The published MLSys 2024 title inserts "On-Device" where the
  arXiv title does not. `docs/audit_claim_table.csv` R04 quotes the arXiv form,
  which is the version it audited, and is correct as frozen; the bibliography
  cites the published form.

### Pass C — forward-citation sweep, 2026-07-27

Backward sweep: the reference lists of the two directly overlapping papers
(`dutta2024flips`, `williamsaletras2024`) plus `paglieri2024outliers` were the
source of the method citations already in the tree; no new admission.

Forward sweep, run against the Semantic Scholar citation graph:

| date | database | seed paper | returned | screened | admitted |
|---|---|---|---|---|---|
| 2026-07-27 | Semantic Scholar Graph API, `citations` endpoint, limit 100 | arXiv:2407.09141 (Dutta et al.) | 20 | 20 (title-level) | 0 new |
| 2026-07-27 | Semantic Scholar Graph API, `citations` endpoint, limit 100 | arXiv:2311.09755 (Williams & Aletras) | 55 | 55 (title-level) | 0 new |

**Total forward-screened: 75.** Two already-known papers reappeared in the Dutta
set and confirm the graph is live (`2607.08734`, `2602.10144`); one already-known
paper reappeared in the Williams & Aletras set (`2405.20835`).

Titles flagged and resolved:

- 14 calibration-*data* papers in the Williams & Aletras set (selection,
  curation, coverage, multilinguality, calibration-free methods). All vary the
  calibration **corpus**; none varies a **seed** with the corpus held fixed, and
  none reports a ranking flip between two quantization methods. This is the
  screen behind the absence sentence in `related_work.tex` §"Calibration
  sensitivity"; that sentence must not be widened beyond it.
- *Reliability Scaling Laws for Quantized Large Language Models* (2026,
  OpenReview `QhkW8xPH1v`) — checked directly because the title reads close to
  the certification leg. It is uncertainty and perturbation-robustness scaling
  across bit widths; no equivalence testing, no required-*n*, no calibration
  seeds, no audit. Excluded.
- *SINQ: Sinkhorn-Normalized Quantization … Calibration-Free* (2025) — a method
  that removes calibration rather than studying its variance. Excluded.

**Screening depth, stated plainly: title-level, with targeted full-text checks on
flagged items only.** A title-level screen can miss a per-seed ranking table
buried in an appendix. It is sufficient to support "the sweep found no prior work
that does X" and is not sufficient to support "no such work exists"; the paper
uses the former.

### Still open

- [ ] Venue-by-venue proceedings sweep (rows under "Sources and Venues" above)
      beyond what the two citation graphs surfaced.
- [ ] `lm-evaluation-harness` issues/PRs/release notes as a literature source.
- [ ] The OpenReview `pfw3saHzGU` verbatim-quote checklist (V1–V7 in
      `docs/PRIOR_ART_CONCURRENT_2026-07-24.md` §1) — needs a browser pass from
      outside the cluster. No quote from it appears in the paper, so nothing in
      the current draft depends on it.

## Evidence Table

| Paper | What it shows | Overlap with H1/H2/H3 | Our differentiation |
|---|---|---|---|
| Dutta et al., *Accuracy is Not All You Need* (NeurIPS 2024) | Compressed models can match baseline accuracy while flipping many individual answers; proposes flips and KL divergence as complementary metrics. | Direct H1 antecedent; motivates per-item analysis. Does not establish our H2 power/rank-stability protocol or H3 calibration-seed effect. | Do not claim that flips are novel. Contribute net-versus-gross decomposition, calibration-seed ranking instability, paired power/certification requirements, and a released reanalysis artifact. |
| Williams & Aletras, *On the Impact of Calibration Data in Post-training Quantization and Pruning* (ACL 2024) | Calibration **data** choice produces substantial variation in downstream task performance, contrasting prior claims of robustness. | Owns calibration-data effects. Does not pair methods on identical samples, and asks nothing about ranking. | We hold the corpus fixed and vary only the sample seed, pairing GPTQ seed *s* with AWQ seed *s* on byte-identical samples, and ask whether the **ranking** moves. |
| Paglieri et al., *Outliers and Calibration Sets have Diminishing Effect on Quantization of Modern LLMs* (arXiv:2405.20835) | Modern LLMs (Llama-2/3, Command-R, Mistral) are robust to calibration-set choice where OPT is not; sets vary in quality, content and language. | The strongest objection to H3's premise, and it points the opposite way from Williams & Aletras. Reports GPTQ, AWQ, SmoothQuant and naive W8A8 **separately**; no head-to-head, no ranking flips, no seed-only variation. | Reconciled in a dedicated subsection: individual-method robustness **plus** a method gap smaller than the seed-induced range **implies** ranking instability. Both results hold; theirs has a consequence they did not test for. |
| Helcig, Kurtic & Alistarh, *Statistically-Lossless Quantization of LLMs* (arXiv:2605.02404) | Defines task-lossless and distribution-lossless, proposes Expected Acceptance Rate, proves a γ² variance law, ships SLQ. Occupies the phrase "statistically lossless". | Nearest neighbour to §5 by vocabulary, not by question. Zero occurrences of TOST, equivalence testing, McNemar, power, or required sample size; no audit of others' claims. | They define losslessness and build a method to reach it; we audit whether published claims have the evidence, and compute the *n* required to certify one. |
| Rababah, Akcora & Leung, *The Illusion of Equivalency* (arXiv:2607.08734) | "Correctness agreement" — the per-item both-correct rate — diverges under moderate quantization even where accuracy looks preserved. Layer-level Q/K vs V/O sensitivity. | Premise-level overlap with the atlas leg; CA is algebraically interconvertible with our churn. No statistical testing, no sample-size machinery, no audit, no seeds. | Cited as concurrent corroboration with an explicit no-priority statement. We supply the decision machinery it does not. |
| Kübler et al., *When LLMs get significantly worse* (ICLR 2026, arXiv:2602.10144) | One-sided McNemar **detection** for LLM accuracy comparisons, shipped in lm-evaluation-harness. | The closest existing tool. | Detection is not certification: we add TOST at a declared margin, required-*n* from empirical churn, and the audit. |
| Bronder, *Instrument Effects in Language-Model Honesty Evaluation* (arXiv:2607.14399) | Player model held fixed; four instrument factors (outcome grammar, criterion disclosure, budget rendering, register presence) substantially move measured behaviour. Not quantization. | Parallel design to the harness-sensitivity study in a different domain. | Cited as convergent evidence in the harness section, not as an antecedent for any FlipEval leg. |
| Gringras & Salahshoor, *Frontier Lag* (arXiv:2605.04135); Thomas, Gligoric & Shah, *Mitigating LLM-based p-Hacking* (arXiv:2606.27687) | Preregistered bibliometric audit of which models the literature tests; preregistering an analysis against an unreleased model. | Genre precedent for §3 only. | One sentence each; no overlap with any FlipEval result. |

## Completion Checks

- [x] Verify title, author list, venue, year, DOI/arXiv ID from primary sources.
      *(Pass B, 2026-07-27; per-entry provenance in `paper/references.bib`.)*
- [x] Read methods and limitations, not only abstracts. *(For the papers the
      paper makes claims about: `2405.20835`, `2605.02404`, `2607.14399`
      full-text HTML; `2607.08734`, `2604.27405`, `2606.19558` in pass A.
      Not done for the 75 title-level screened citations — see pass C.)*
- [x] Separate compression-specific work from general evaluation-statistics work.
      *(Reflected in the §2 subsection split.)*
- [x] Identify any paper with controlled calibration seeds or datasets.
      *(Datasets: Williams & Aletras, Paglieri et al. Seeds with the corpus held
      fixed: none found in 75 forward-screened citations.)*
- [x] Identify any existing equivalence-testing or sample-size certification tool.
      *(`llmaccuracystats2026` is detection, not certification; no equivalence or
      required-*n* tool found.)*
- [ ] Update positioning and preregistration only through a dated amendment if the main grid has begun.
