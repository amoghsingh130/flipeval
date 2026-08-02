# Final Rev-3 Paper Checklist

Use this as the single carry checklist. Do not release the arXiv revision or submit to TMLR until every **release blocker** is checked.

## Canonical rev-3 results

These are the invariants every manuscript section, table, figure, artifact, and README must reproduce:

- [ ] 17 frozen candidate sources.
- [ ] R10 is ineligible under the registered inclusion rule.
- [ ] 16 eligible sources.
- [ ] 11 numerically assessable sources.
- [ ] 5 non-assessable sources: 4 insufficiently reported and 1 outside the registered binary paired-outcome framework.
- [ ] At the uniform 2-percentage-point margin, 1 of 11 is below the approximate planning threshold at the median discordance imputation.
- [ ] No claim remains below the threshold throughout the atlas-IQR sensitivity interval.
- [ ] Ten of 11 remain above the threshold throughout that interval; R01 changes classification within it.
- [ ] R01: reported `n = 1,838`; median-imputation requirement `n_req = 2,010`; reversal point `d* = 0.118915` under the implemented rounding convention.
- [ ] R01 is classified as adequate under 345 of 792 reference-cell imputations (43.6%); this fraction is descriptive, not a probability.
- [ ] No eligible source reports an a priori numerical equivalence margin.
- [ ] No eligible source releases task-matched per-item outputs; R08, R15, and R16 release outputs for other tasks only.
- [ ] The margin taxonomy and the “10 of 16 contain no number” statement are reconciled in a cross-tab with explicit definitions.

## 1. Freeze and preserve the evidence

- [ ] Create a clean rev-3 branch/tag and record the commit used for every final calculation.
- [ ] Preserve all earlier registrations, releases, and Zenodo v1.0.0 unchanged.
- [ ] Record the exact rev-2 atlas path, revision, SHA-256, schema version, and row count (`792`) used by rev-3.
- [ ] Record hashes for the rev-3 audit table, source manifest, configuration, generated tables, and final PDF.
- [ ] Confirm the 17-source frozen candidate population has not been silently changed.
- [ ] Document every post-registration change in one dated amendment/change log.

## 2. Complete the audit adjudication

- [ ] Apply the frozen inclusion rule to all 17 candidates, not only R10.
- [ ] Recheck the inclusion basis and exact source location for R09, R13, and R17.
- [ ] Record R10 as ineligible because the synthesized sentence appears in neither prose nor a table caption.
- [ ] Confirm that removing R10 changes the eligible denominator but does not change the below-threshold count or task-matched-output finding.
- [ ] Record R17's internal prose/table direction contradiction and state that the magnitude-based calculation is unchanged.
- [ ] Give each non-assessable source exactly one primary blocker and supporting evidence.
- [ ] Make `assessable = false` programmatically prevent assignment of any threshold verdict.
- [ ] Add a regression test ensuring R14 cannot enter `K`, even though its visible `n = 728` is near the hypothetical `742` requirement.
- [ ] Have a genuine second human verify eligibility, quotation accuracy, source locations, margin classification, output-task matching, and non-assessability reasons.
- [ ] Record disagreements and their resolutions; do not describe two automated passes as human inter-rater verification.

## 3. Lock the statistical interpretation

- [ ] Use the registered uniform 2-percentage-point margin for the primary audit calculation.
- [ ] Retain result-derived/claim-derived-margin calculations only as clearly labeled, non-verdict-bearing sensitivity history, or remove them from the main paper.
- [ ] Withdraw rather than recompute the old `2.0x-12.9x` shortfall claim.
- [ ] Define “robust” only relative to the stated atlas-IQR sensitivity interval.
- [ ] Label the IQR sensitivity analysis post-registration/post-verdict if that is the true chronology.
- [ ] Establish continuous-IQR robustness through the monotonic relationship and endpoint checks, not only observed cell counts.
- [ ] State that the 792 atlas cells may be dependent and are not a posterior sample for R01.
- [ ] Report Q1, median, Q3, and `d*` with an explicit rounding/ceiling convention.
- [ ] Validate the required-sample-size calculation against an independent implementation or hand derivation, including nonzero true deltas.
- [ ] Correct the TOST wording: one-sided `alpha = 0.05` corresponds to a 90% two-sided confidence interval, not a 95% two-sided interval.
- [ ] State the assumptions behind the paired binary planning approximation and distinguish prospective planning from retrospective diagnosis.
- [ ] Test exact-boundary, `d* < 0`, `d* = 0`, `d* = 1`, `d* > 1`, missing-value, and integer-ceiling cases.

## 4. Make the toolkit fail closed

- [ ] Require `--atlas` and `--output`; do not provide silent defaults.
- [ ] Remove the superseded rev-1 atlas default from every script, test, Make target, notebook, README example, and paper-generation command.
- [ ] Remove all legacy `own_margin` output columns and downstream references.
- [ ] Treat unattainable reversal points outside `[0,1]` as stable classifications rather than passing them to numerical routines.
- [ ] Emit the atlas revision and digest, audit-table digest, toolkit commit, schema version, margin, imputation rule, and complete configuration with every certificate/table.
- [ ] Make a certificate fail validation when calibration-data identity or procedure version is missing.
- [ ] Add a golden test showing that rev-1 produces the expected `1,936` value and rev-2 the expected `2,010` value for R01.
- [ ] Generate every paper table from one pinned, logged command.
- [ ] Run the complete test suite from a clean checkout/environment.
- [ ] Save the successful command log and output hashes in the release manifest.

## 5. Replace every stale manuscript claim

- [ ] Rewrite the abstract; remove “four claims are underpowered for the margin they assert.”
- [ ] Replace `tab:audit-underpowered`, its LaTeX label, caption, header, body, and every reference to it.
- [ ] Do not use “Stated margin” for a quantity no source stated.
- [ ] Use a main-text sensitivity summary with counts: 10 above throughout, 1 sensitive, 0 below throughout.
- [ ] Provide all 11 assessable claims in an appendix table with reported `n`, imputation stratum, `n_req` at Q1/median/Q3, attainable `d*`, and sensitivity classification.
- [ ] Provide the five non-assessable claims separately with exact blockers.
- [ ] Replace “none released per-item outputs” with “none released task-matched per-item outputs,” and disclose the three task-mismatched releases in the same sentence.
- [ ] Describe R04 as outside the registered **binary paired-outcome calculation**, not as incompatible with paired analysis generally.
- [ ] Avoid a definitive “underpowered” verdict; use “below the approximate planning threshold under the median imputation.”
- [ ] Avoid generalizing prevalence beyond this audited sample of 16 eligible sources.
- [ ] Align the title, abstract, contribution list, introduction roadmap, audit section, discussion, limitations, conclusion, captions, footnotes, and supplement with the canonical results.

## 6. Run a stale-claim and stale-pointer audit

- [ ] Review every hit—not a blind replacement—for: `4 of 12`, `four claims`, `5 of 17`, `2.0x`, `12.9x`, `own margin`, `claim-specific margin`, `margin they assert`, `Stated margin`, `audit-underpowered`, `underpowered`, and the old R17/R07/R06/R15 group.
- [ ] Inspect all `% SOURCE:` comments individually.
- [ ] Remove or update every pointer to `audit_verdicts_rev2.csv`, rev-1 atlas files, superseded generated tables, and old artifact paths.
- [ ] Search LaTeX, Markdown, CSV, JSON, scripts, notebooks, tests, captions, alt text, appendices, supplementary files, and READMEs.
- [ ] Add a manuscript linter/CI check for forbidden old counts, labels, filenames, and withdrawn claims.
- [ ] Generate shared LaTeX result macros from the canonical rev-3 table instead of manually typing counts in multiple sections.

## 7. Write the amendment transparently

- [ ] State that the full-text verification and sensitivity analysis occurred after the original verdicts were visible.
- [ ] Do not claim results-blind classification or imply the amendment was prospective.
- [ ] Explicitly reopen the affected inclusion/extraction sections to apply the frozen rule to R10.
- [ ] Explain why R10 is excluded and why the correction does not improve the number of flagged claims.
- [ ] Explain why result-derived margins no longer support primary verdicts: observed deltas are outcomes, not declared decision margins.
- [ ] Disclose the rev-1 default defect, its numerical effect, its lack of effect on the R01 point classification, and the fail-closed repair.
- [ ] Include a precise old-result to rev-3-result mapping.
- [ ] Keep the prior public artifact immutable and visibly superseded rather than silently corrected.

## 8. Release the corrected reproducibility artifact

- [ ] Publish a new immutable Zenodo version (for example v1.1.0), not a replacement of v1.0.0.
- [ ] Include a change log, rev-2-to-rev-3 mapping note, exact commands, hashes, schema version, and regenerated outputs.
- [ ] Cite the version-specific DOI when exact reproducibility is required; use the concept DOI only for discovery/latest-version routing.
- [ ] Verify that the paper, README, release notes, and artifact all report the same canonical results.
- [ ] Audit redistribution licenses before publishing archived copies of papers, model cards, or web pages.
- [ ] If redistribution is not permitted, publish URLs, version identifiers, hashes, retrieval scripts, manifests, and compliant excerpts; keep full captures private.
- [ ] Document the non-cryptographic provenance limitations for R11 and R13 accurately.

## 9. Improve the paper's presentation and human voice

- [ ] Lead with the scientific problem: aggregate parity does not certify item-level behavioral preservation.
- [ ] Use the audit to establish missing decision criteria and missing paired evidence, not to accuse individual authors of bad statistics.
- [ ] Make the toolkit and its evidence-binding certificate the constructive centerpiece.
- [ ] State the key design principle explicitly: a certificate that does not identify its evaluation and calibration evidence is invalid.
- [ ] Reduce repeated “registered,” “frozen,” “rather than,” and defensive procedural language where it is not needed for reproducibility.
- [ ] Replace formulaic bold microheadings and repeated contrast constructions with normal narrative transitions.
- [ ] Remove or rewrite phrases such as “fresh agent session”; disclose automated assistance factually in the methods/artifact documentation where relevant.
- [ ] Have a human edit every paragraph for cadence, specificity, and genuine authorial judgment.
- [ ] Shorten the main paper aggressively; move provenance detail, full audit rows, extra derivations, and operational logs to appendices/supplement.

## 10. Add the strongest J2C-facing validation feasible

- [ ] Include a clear case where baseline and compressed models have nearly identical aggregate accuracy but materially different per-item behavior.
- [ ] Show how a conventional aggregate-delta analysis and the paired certificate reach different conclusions.
- [ ] Demonstrate stable certification, sensitivity-dependent classification, and insufficient evidence as distinct outcomes.
- [ ] Cover more than one model/compression/task setting if resources permit.
- [ ] Include one memorable figure connecting aggregate delta, discordance/churn, declared margin, and certification outcome.
- [ ] Explain the practical decision affected by the certificate: deployment, subgroup reliability, safety slice, benchmark interpretation, or reproducibility.
- [ ] Keep this validation separate from the literature-audit denominator and amendment logic.

## 11. Build separate arXiv and TMLR packages

### Named arXiv package

- [ ] Include author identity and the corrected version-specific public artifact link.
- [ ] Ensure the arXiv PDF, source archive, and artifact version agree.
- [ ] Add a clear version/change note if an earlier public draft exists.

### Anonymous TMLR package

- [ ] Use the mandatory, unmodified TMLR style.
- [ ] Remove names, affiliations, acknowledgements, grants, usernames, absolute paths, and identifying metadata.
- [ ] Do not link the anonymous submission to the named arXiv, GitHub, or Zenodo release.
- [ ] Build an anonymous supplementary ZIP without Git history, remotes, author metadata, or identity-bearing logs.
- [ ] Search the anonymous PDF and ZIP contents for `Amogh`, `Georgia Tech`, `/Users/`, usernames, repository URLs, DOI links, and acknowledgements.
- [ ] Confirm that anonymous artifact hashes do not function as an explicit identity link in the manuscript.

## 12. Final release gates

- [ ] Rebuild the paper and every table from a clean checkout using only documented commands.
- [ ] Run all unit, integration, golden, schema, denominator, stale-claim, and anonymization tests.
- [ ] Verify every number in the abstract, main tables, conclusion, and artifact against the canonical rev-3 output.
- [ ] Render the full PDF and visually inspect every page, table, caption, equation, footnote, link, and appendix transition.
- [ ] Fix overflowing paths, illegible tables, broken references, awkward page breaks, and blank/identifying PDF metadata.
- [ ] Run spelling, grammar, citation, duplicate-reference, and unresolved-LaTeX-reference checks.
- [ ] Have the second human review the final compiled PDF—not only the source or CSV.
- [ ] Confirm the public artifact can be reproduced from its own instructions in a clean environment.
- [ ] Freeze final hashes for the PDF, source package, supplemental package, and artifact release.
- [ ] Only then post arXiv and prepare the separately anonymized TMLR submission.

## Recommended canonical headline

> Across 16 eligible sources, none reported an a priori numerical equivalence margin or released task-matched per-item outputs. Five could not be assessed under the registered binary paired-outcome framework. Among the remaining 11, ten remained above the approximate planning threshold throughout the atlas-IQR sensitivity interval, while one changed classification within it; no claim remained below the threshold throughout that interval. These results motivate certificates that bind equivalence claims to declared margins, paired evidence, calibration data, and procedure versions.
