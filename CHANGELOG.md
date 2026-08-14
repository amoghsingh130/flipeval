# Changelog

Release versions (`v1.x.y`) name the **artifact**: the git tag, the archived
Zenodo deposit and the dataset-mirror revision all carry the same string, and
that is what `paper/sections/artifacts.tex` and
`paper/sections/appendix_artifacts_detail.tex` cite.

The Python distribution version in `pyproject.toml` is a **different number**
and moves on its own schedule; it tracks the importable API, not the archive.
Do not synchronise the two.

Released versions are never edited in place. A superseded version stays
published beside its replacement, so that each correction remains visible.

## v1.2.0 — unreleased

Version DOI: `10.5281/zenodo.21939143` (reserve on Zenodo before the paper cites
it; see the release checklist). Ships distribution version `0.3.0`.

Post-review synchronisation of the artifact with the manuscript. **No audit
verdict, atlas cell, certification row or controlled-run value changes in this
release**; v1.1.0's numbers are v1.2.0's numbers.

Added

- `flipeval/report.py` and `flipeval report`: the paper's five-line reporting
  standard emitted for one model pair from two per-item files. Lines 1–4 are
  computed; line 5 is a release action, so it is reported unmet unless a
  publication location is supplied and silence is never read as compliance.
- `flipeval/certification.py` and `flipeval required-n`: required-*n* lookup by
  benchmark family and declared margin over the released certification table,
  plus `required_n_from_discordance` for families the table does not cover.
- `flipeval/data/certification_tables_rev2.csv`: a byte-identical copy of the
  released `results/certification_tables_rev2.csv`, shipped inside the package
  so the lookup works from an installed distribution where `results/` is
  absent. `tests/test_certification_lookup.py` fails if the two copies drift.
- `examples/`: a runnable end-to-end walkthrough against
  `lm-evaluation-harness` `--log_samples` output, with a deterministic
  synthetic fixture, so the workflow reproduces with no GPU, no model download
  and no harness install. The fixture is a simulation of the shape the toolkit
  measures; no number in the paper comes from it.
- Top-level exports `five_line_report`, `FiveLineReport`,
  `required_n_for_benchmark`, `required_n_from_discordance`, `RequiredN`.
- Paper: Figure 2 (the five lines applied to one registered cell beside the
  aggregate report of the same run), Figure 3 (the certification table drawn
  for lookup), their generators `scripts/make_figure2.py` and
  `scripts/make_figure3.py`, and Appendix H
  (`paper/sections/appendix_continuous.tex`) on continuous and graded metrics,
  which is stated as mathematics and is explicitly not validated.

Changed

- `flipeval/io.py` accepts an `lm-evaluation-harness` output *directory* as
  well as a samples file, and handles generative tasks alongside
  loglikelihood ones: for generative tasks the prediction is the harness's own
  filtered answer, so scoring stays the harness's decision.
- Manuscript revisions in response to TMLR reviewer feedback across the
  introduction, certification, preregistration, atlas, audit, mini-grid and
  limitations sections. Scope statements were not weakened; see the dated
  comment blocks in each file for what moved and why.

Not changed

- The audit population and its rev-3 verdicts, the rev-2 atlas, the
  certification tables, and every controlled-run artifact and its seal.

## v1.1.0 — 2026-08-09

Version DOI: [10.5281/zenodo.21829570](https://doi.org/10.5281/zenodo.21829570).
Source tag `v1.1.0`.

The first archive containing the rev-3 audit. v1.0.0 was deposited on
2026-07-30 and the verdicts were recomputed the following day under Amendment 2
of the audit registration, so v1.0.0 carries the superseded rev-2 verdicts
while the paper reports rev-3.

Added

- `results/audit_verdicts_rev3.csv` and the denominator ledger generated from
  it, with the CSV's SHA-256 recorded in the ledger header.
- The rev-3 eligibility correction (R10 excluded by the inclusion rule already
  registered in §3.1; the eligible population is 16, not 17), recorded in the
  verdicts CSV rather than by editing the frozen claim table.
- Full-text source verification, the public source manifest and
  `scripts/fetch_audit_sources.py`.

Changed

- The full-text captures of the audited sources were removed from git history
  under Amendments 4 and 5 after the 2026-08-02 redistribution review, and are
  in no release. The hash-remap records ship with the archive.

## v1.0.0 — 2026-07-30

Version DOI: [10.5281/zenodo.21708923](https://doi.org/10.5281/zenodo.21708923).
Source tag `v1.0.0`.

First public archive. Carries the rev-2 audit verdicts, and the verdict script
archived with it predates the eligibility and margin-category logic Amendment 2
introduces, so it cannot reproduce rev-3. Left published deliberately as the
historical record.

---

Concept DOI [10.5281/zenodo.21708922](https://doi.org/10.5281/zenodo.21708922)
always resolves to the latest version. Cite the **version** DOI for any claim
about a frozen state.
