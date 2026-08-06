# Artifact synchronization and arXiv compilation preview, 2026-08-06

Both performed **entirely offline and locally**. Nothing was uploaded, pushed,
re-fetched, or submitted. No audited source was contacted.

---

# Part 1: artifact synchronization

Every externally-checkable artifact claim in `sections/artifacts.tex` and
`sections/appendix_artifacts_detail.tex` was reconciled against what is
committed. **All reconcile. No paper edit was required.**

| claim in the paper | committed reality | verdict |
|---|---|---|
| per-item outputs, **88 cell JSONL files**, every cell of the controlled experiment | `minigrid_run_20260722.tar.gz` 44 + `escalation_run_20260726.tar.gz` 44 = **88** | **match** |
| the flip atlas | `results/atlas_cells_summary_rev2.csv`, 2,055 rows, of which the registered analysis population is 1,707 | **match** |
| the `flipeval` package under Apache-2.0 | `LICENSE` is Apache-2.0; README states it | **match** |
| the frozen 17-claim audit table and its verdict CSV | `docs/audit_claim_table.csv` + `results/audit_verdicts_rev3.csv` | **match** |
| the certification tables | `results/certification_tables_rev2.csv` | **match** |
| the reproduction package | `docs/RELEASE_CHECKLIST_v1.0.0.md` | **match** |
| version DOI `10.5281/zenodo.21708923` | same in the release checklist, marked canonical | **match** |
| concept DOI `10.5281/zenodo.21708922` | same in the release checklist | **match** |
| container image SHA-256 `8260d04c…1db2007` | full digest `8260d04cf1f76cb5961b6538dbeb9178006b29c5d8c93d2c639976bcd1db2007` in two dated records | **match** |

## Option A, verified intact

The release publishes URLs, pinned identifiers, hashes, the manifest and a
retrieval script; the **full-text captures stay private**.

- `docs/audit_sources_manifest.tsv`: **17 rows, and all 17 carry a valid 64-hex
  sha256**, alongside pinned version, retrieval method and a per-row provenance
  status.
- `scripts/fetch_audit_sources.py` is present and is the standard-library
  re-fetch script the paper describes.
- **No full-text capture is tracked in git.** A search over the whole index for
  capture/full-text files and for `sources/*.pdf|html|md` returns nothing.

**A correction to my own first pass.** I initially reported that 0 of 17 rows
carried a sha256. That was a bug in my check, which read the last column
(`pinned_version`) instead of the `sha256` column. All 17 are present. The
artifact was never wrong; the check was.

## The two provenance limits, and their disclosure

| claim | manifest status | disclosed in the paper? |
|---|---|---|
| R11 | `MISMATCH` (live fetch 2026-07-31, no history available) | **yes**, in `app:artifacts:datasheet`: the recorded digest was never a valid fingerprint |
| R13 | `NO-BASELINE` (live fetch 2026-07-31, no baseline hash) | **yes**, in both `sec:artifacts` and the audit section, which says content hashes exist for 16 of the 17 |

The licensing findings also reconcile: four sources with no third-party
republication grant (Meta AI blog, NVIDIA TensorRT-LLM doc, two vLLM pages) and
seven method papers under arXiv's default licence, exactly as
`sections/appendix_artifacts_detail.tex` states.

## What could not be checked offline, and is not claimed to have been

The **Hugging Face mirror's file count** and the **live resolution of both
DOIs** require network access. Re-fetching audited sources is forbidden and
contacting the mirrors was out of scope, so neither was attempted. They are
recorded in `docs/RELEASE_CHECKLIST_v1.0.0.md` from the release date and are
unchanged since; this synchronization neither confirms nor disputes them.

---

# Part 2: arXiv compilation preview

**No upload. No submission. Nothing left this machine.** This is a local
rehearsal of what arXiv's build would do.

## The submission tree

26 files, 480 KB, assembled into a clean directory containing nothing else:

```
main.tex  abstract.tex  audit_denominators.tex  references.bib  main.bbl
figures/fig1_cancellation.tex
sections/*.tex   (20 files)
```

`main.bbl` is shipped deliberately: arXiv prefers a supplied `.bbl` to running
BibTeX, and the clean-room build below never invokes BibTeX.

## Result

| | |
|---|---|
| build | `pdflatex` x3, no BibTeX, no shell-escape, no external tooling |
| **pages** | **100** |
| undefined references / citations | **0** |
| missing files | **0** |
| LaTeX errors | **0** |
| overfull boxes | 2, both known and classified in the QA report |
| author block | `Amogh Singh, Georgia Institute of Technology` |

The clean-room PDF matches the working-tree build at 100 pages, so no input is
being picked up from outside the submission tree.

**Figure 1 needs no graphics file.** It is generated TikZ compiled from source,
so there is no `.png`/`.pdf` asset to lose in transit, which removes the most
common arXiv figure failure.

## The anonymity switch, exercised both ways

Both builds were compiled from identical sources with only `\anonfalse` /
`\anontrue` changed.

| | arXiv (`\anonfalse`) | TMLR blind (`\anontrue`) |
|---|---|---|
| pages | 100 | 100 |
| undefined | 0 | 0 |
| author block | named, with affiliation | "Anonymous authors / Paper under double-blind review" |

**Identifier leak check on the blind PDF, extracted text, all zero:**

```
amoghsingh130        0
AmoghSingh123        0
Amogh Singh          0
Georgia Institute    0
10.5281/zenodo       0
3831                 0
```

The switch does what it claims: every de-anonymising item is routed through the
preamble macros, and the blind build leaks none of them.

## Two things to decide before an actual submission

1. **`\date{Draft \today}`.** The title page will carry the word "Draft" and
   whatever date the build runs on. See `docs/MANUSCRIPT_FREEZE_2026-08-06.md`.
2. **Which switch.** `\anonfalse` is committed. A TMLR submission needs
   `\anontrue`, and that is a one-line change, not a rebuild of anything.

Neither is done here.
