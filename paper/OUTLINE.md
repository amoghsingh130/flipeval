# FlipEval paper outline — "Certifying Compressed Language Models: An Audit and a Statistical Toolkit"

Status: drafting, updated 2026-07-27. Solo author: Amogh Singh, Georgia Tech.
Venue order: COLM 2027 (~March), ACL 2027, NeurIPS D&B 2027 (~May).

> **⚠️ HISTORICAL PLANNING RECORD. DO NOT QUOTE ITS NUMBERS.**
>
> This file is not compiled into the paper and is not `\input` by `main.tex`. It
> records what the paper was planned to argue as of the Status line above, and
> several counts below have since been **withdrawn** by Amendment 2 to the audit
> registration (signed 2026-07-31): the K count, the shortfall range, and the
> pre-exclusion denominator of 17. They are deliberately left as written, because
> editing them to current values would destroy the only record of what changed.
>
> **Current numbers live in `paper/audit_denominators.tex`**, generated from the
> sealed `results/audit_verdicts_rev3.csv`. The venue line above is also stale:
> the target is now an arXiv preprint followed by TMLR. See
> `docs/ARXIV_TMLR_ROADMAP_2026-08-03.md`.
>
> `paper/tools/check_paper.py` lists this file as review-only for that reason, so
> its stale hits are reported but do not fail the run.

**Rules this outline enforces.**

1. Every number in the paper is traceable to a committed file; each LaTeX
   number carries a `% SOURCE:` comment naming that file.
2. ~~Every H3 quantity is a `\minigridTODO{}` slot.~~ **SUPERSEDED 2026-07-26.**
   The escalation screen fired, all **8 of 8** registered confirmatory cells
   completed, and the frozen decision rule of `PREREGISTRATION.md`
   §"H3 Decision Rule" was applied once over the full set. The verdict is
   **SUPPORTED**, recorded and signed in
   `docs/H3_EIGHT_CELL_DECISION_2026-07-26.md` (commit `05c86f2`).

   The rule that replaces the old one: **no section of this paper may state an
   H3 outcome the signed record does not contain.** §7 reports the verdict, §3
   reports the protocol and deliberately still states no outcome, and no
   reduced-cell variant of the rule exists anywhere. The `\minigridTODO` macro
   remains defined in `main.tex` but no slot survives; do not reintroduce one.
3. The audit is constructive: no claim is described as false. The audited
   property is the evidential sufficiency of the reported evaluation.
4. **The summary-restatement invariant** (adopted 2026-07-26). `abstract.tex`
   and `sections/introduction.tex` are *derivative*: they contain no primary
   figures. Therefore —

   > **Every number in the abstract and introduction must appear in the section
   > it summarises, and must be the same number at a coarser or equal
   > precision.**

   A summary figure may round (§ 8.49 % → abstract 8.5 %). It may **never** be
   a different revision, a different statistic, or a rounding of a superseded
   value. Verify by walking both files figure-by-figure against the body
   section — they are ~1,400 words together, so this is bounded — and record the
   walk in the commit that changes any headline number.

   *Why this rule and not a token grep.* On 2026-07-26 a `grep` for rev-1
   tokens (`643`, `1155`, `113`, `9.78`, `6.22`, `1.7`) passed the abstract
   clean while it still read "a median of 6.2 % of items" — the rev-1 churn
   median 0.062176, **rounded**, and therefore invisible to any search for the
   unrounded form. Rounded restatements are exactly what a summary contains, so
   token search is structurally unable to police summaries. It is retained only
   as a secondary sweep, and when run it must include the rounded forms of
   *both* revisions.

---

## Section map

| § | File | Status |
|---|---|---|
| Abstract | `abstract.tex` | drafted, with three bracketed H3 variants |
| 1 Introduction | `sections/introduction.tex` | outline + skeleton prose |
| 2 Related work and positioning | `sections/related_work.tex` | outline + skeleton prose |
| 3 Preregistration, freezes, and analyst degrees of freedom | `sections/preregistration.tex` | **complete draft** |
| 4 Audit of published near-lossless claims | `sections/audit.tex` | **complete draft** |
| 5 Certification tables | `sections/certification.tex` | **complete draft** |
| 6 The public-record flip atlas | `sections/atlas.tex` | **complete draft** |
| ~~7 Anytime-valid sequential certification~~ | ~~`sections/sequential.tex`~~ | **REMOVED 2026-07-26** — a results-free `\section` with no registration document. Reduced to one sentence in the conclusion. Restore only when a dated registration exists under `docs/` **and** the component has run. Its removal is why every section below shifted down by one. |
| 7 Controlled seed-paired experiment (H3) | `sections/minigrid.tex` | **complete**; verdict + 5 tables + Result 1, filled 2026-07-27 |
| ↳ (subsection) The mechanical escalation screen | `sections/minigrid_escalation.tex` | **complete** |
| 8 Harness-defaults sensitivity study | `sections/harness_sensitivity.tex` | **complete draft** (was missing from this map) |
| 9 Discriminant validity | `sections/discriminant.tex` | skeleton, pilot numbers wired |
| 10 Artifacts, datasheet, licensing | `sections/artifacts.tex` | skeleton (D&B hygiene) |
| 11 Limitations | `sections/limitations.tex` | skeleton |
| 12 Conclusion | `sections/conclusion.tex` | skeleton |
| A Full audit table | `sections/appendix_audit_table.tex` | skeleton, points at `results/audit_verdicts.csv` |

---

## 1. Introduction

Argument order (three moves, in this order, because the audit is what earns the
toolkit its audience):

1. **The practice.** "Near-lossless" is asserted from a point difference in
   aggregate accuracy on a fixed benchmark, without a margin, without a test,
   and usually without released per-item outputs.
2. **The audit.** At their own reported sample sizes, 4 of the 12 determinate
   claims we audited could not have detected the difference they pronounce
   negligible; 5 of 17 cannot be evaluated at all from what is reported; and
   0 of 17 release the per-item outputs a third party would need to run the
   paired test themselves.
3. **The fix.** Equivalence *certification*, not degradation *detection*: TOST
   at a declared margin, required-$n$ certification tables computed from
   observed churn rather than idealised binomial variance, and anytime-valid
   sequential certification so evaluation can stop when the model is certified.
4. **The evidence.** A 1,155-cell atlas of the public record of compression
   evaluation, and a preregistered seed-paired controlled experiment (H3).

Contributions list (final wording to mirror the section order above):
audit + verdict artifact; certification tables; `flipeval` toolkit incl.
sequential certification; the atlas; the preregistration itself as an
artifact (frozen protocols, dated amendments, disclosed analyst choices).

Explicit non-claims to state in the intro so no reviewer has to ask:
- Flips as a metric are not ours: `\cite{dutta2024flips}`.
- Calibration-*data* effects are not ours: `\cite{williamsaletras2024}`.
- Ours: seed-level pairing of GPTQ/AWQ calibration sets, ranking instability,
  equivalence certification (incl. required-$n$ tables and sequential
  certification), and the published-claim audit.

## 2. Related work and positioning

- **Per-item behaviour under compression.** `\cite{dutta2024flips}` — flips and
  KL as complementary metrics; direct H1 antecedent. We add the net/gross
  decomposition at scale over the public record and the certification apparatus.
- **Calibration sensitivity.** `\cite{williamsaletras2024}` own calibration-data
  effects; our registered contrast is calibration *seed* at fixed data, with
  GPTQ and AWQ receiving byte-identical calibration samples per seed
  (`PREREGISTRATION.md` §"Experimental Grid").
- **Statistics of LLM evaluation.** Amazon LLM-Accuracy-Stats
  (`\cite{llmaccuracystats2026}`, arXiv 2602.10144) is the closest tool: it does
  **one-sided McNemar detection**. Position explicitly and repeatedly: detection
  answers "is there evidence of a difference?", certification answers "is the
  difference provably smaller than a declared margin?" — a non-significant
  detection result is not equivalence, and the registration says so in advance
  (`PREREGISTRATION.md`: "We will not interpret failure to reject a difference
  as equivalence"). Our deltas over it: TOST at a declared margin, required-$n$
  tables from empirical churn, anytime-valid sequential certification, and the
  audit.
- **Reporting-standards audits as a genre.** `\cite{dodge2019showyourwork}`,
  `\cite{marie2021mtaudit}` — the constructive precedent we echo.
- **Compression methods audited.** GPTQ, AWQ, SmoothQuant, LLM.int8(),
  SqueezeLLM, Wanda, SparseGPT, SpinQuant, QuIP\#.

## 3. Preregistration, freezes, and analyst degrees of freedom — **drafted**

Frozen-rule timeline; the K-correction story told as $K=1 \to 5 \to 4$;
interpretive choices #1, #2, #3, #5 (and #4/#6/#7 in brief); disclosed
pre-registration data contact, including the retired 6.3\% anecdote, which
appears **only** here.

## 4. Audit — **drafted**

Lead: reproducibility zero. Then $K=4$ of 12, $J=5$ of 17, uniform-2\,pp
secondary, margin sensitivity, R04 exclusion.

## 5. Certification tables — **drafted**

Paired advantage 1.7x–14.7x, 4.4x pooled; churn-not-difficulty ordering;
worked MMLU example; the twelve-row table; scope caveats.

## 6. Atlas — **drafted**

2,055 enumerated / 1,254 analysed / 1,155 probe-excluded analysis population;
S1 vs S2 gray-zone contrast; identical-score churn; population caveats.

## 7. (removed — was anytime-valid sequential certification)

- Motivation: fixed-$n$ tables tell you how much to buy; confidence sequences
  let you stop early when the evidence arrives sooner.
- Construction: confidence sequence on the paired per-item difference
  $d_i \in \{-1,0,+1\}$; stop when the sequence is contained in $(-m,+m)$
  (certify) or excludes 0 (detect degradation).
- Evaluation: replay over atlas cells — expected item savings vs the fixed-$n$
  requirement, and empirical coverage/false-certification rate.
- **Process gate:** this component needs its own dated registration under
  `docs/` (drafted by the paper writer, frozen by the human) *before* it runs.
  Nothing from this section may be reported until that doc exists.

## 8. → NOW §7. Controlled seed-paired experiment (H3) — COMPLETE

- Design recap: `{Qwen2.5-1.5B-Instruct, Llama-3.2-3B-Instruct} x {MMLU, GSM8K}`,
  4-bit, GPTQ and AWQ, seeds {0,1,2,3,4}, byte-identical paired C4 calibration
  sets, chat template on.
- Reported quantities, per registered algebra: winner flips (ties reported
  separately), `gap`, `range_GPTQ`, `range_AWQ`, range/gap criterion,
  seed-level SD vs item-level SE as separate variance components, two-level
  paired bootstrap rank-flip rate.
- **Status paragraph, fixed in advance:** the mini-grid executes 4 of the 8
  registered confirmatory cells; the frozen Supported/Disconfirmed/Inconclusive
  rule is defined over all 8; the four completed cells are therefore reported
  descriptively and H3 is undecided under the registered rule. No reduced-cell
  variant of the rule is constructed after results are seen.
- Escalation: the §3 mini-grid rule is mechanical and pre-committed; whether it
  fired, and the dated escalation record, are reported either way.

## 9. Discriminant validity

Pilot evidence that the framework does not label everything noise: MMLU
GPTQ-public showed McNemar $p = 0.036$ at $n = 400$ under the same analysis that
returned $p = 0.672$ / $0.880$ on GSM8K at $n = 200$
(`results/PILOT_RESULTS.md`). Carries the pilot's own caveats (no chat template,
unpinned Kaggle environment, small $n$) and is explicitly not evidence for H3.
Replace or supplement with mini-grid cells if and when they exist.

## 10. Artifacts, datasheet, licensing, maintenance (D&B hygiene)

Atlas (CC-BY-4.0) + `flipeval` (Apache-2.0); datasheet in the Gebru et al.
format; Croissant metadata; Zenodo DOI; 12-month maintenance statement;
reproducibility package (configs, image sha256, SLURM scripts, per-run
manifests, freeze fingerprints).

## 11. Limitations

Atlas population is the public record, not a census; S1 leaderboard-coverage
conditioning; S2 single vendor; discordance imputation for audit claims; family
aggregation mixing subject- and model-level variance; audit operates at
claim-level granularity; mini-grid scope; English benchmarks; models up to 8B in
the controlled grid (up to 405B in the atlas).

## 12. Conclusion

Reporting standard, stated in one paragraph a model-card author can copy:
declare a margin; run the paired test; report churn alongside net delta; release
per-item outputs; cite the required $n$ you met.

---

## Figures and tables planned (each needs a `% SOURCE:` comment)

| id | content | source file |
|---|---|---|
| T1 | Underpowered claims, shortfall factors | `results/audit_verdicts.csv` |
| T2 | MDD / claimed margin ratios | `results/audit_verdicts.csv` |
| T3 | Certification table at 2 pp | `results/certification_tables_rev2.csv` |
| T4 | S1 vs S2 gray-zone contrast | `results/atlas_cells_summary_rev2.csv` |
| T5 | Identical-score churn | `results/identical_score_churn_rev2.csv` |
| F1 | Churn vs net delta scatter, atlas cells | `results/atlas_cells_summary_rev2.csv` |
| F2 | Required $n$ vs margin, by family | `results/certification_tables_rev2.csv` |
| F3 | Sequential certification stopping-time replay | pending §7 registration |
| F4 | H3 seed dispersion vs method gap | `\minigridTODO` |

## Open items for the human

- Independent spot-check of the atlas pipeline must be recorded in
  `docs/RESULTS_2026-07-15_ATLAS_AUDIT.md` before any atlas number is quoted
  externally (that doc, lines 5–7). The blog post is stamped `DO-NOT-PUBLISH`
  until then.
- Two source discrepancies surfaced during drafting; see the `% DISCREPANCY`
  comments in `sections/audit.tex` and `sections/certification.tex`.
- Sequential-certification registration doc: to be drafted under `docs/` and
  frozen before that component runs.
