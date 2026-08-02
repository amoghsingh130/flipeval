# Audit Source Verification — 2026-07-31

Full-document verification of all 17 audited claim sources, performed to test
whether the statement **"no audited source declared an equivalence margin"**
survives inspection of complete source text rather than the one-sentence
`exact_quote` fields in `docs/audit_claim_table.csv`.

Run by Claude Code at Amogh's direction, 2026-07-31. **This document changes no
frozen file and no computed verdict.** It is evidence for a decision that has
not yet been taken (`docs/AUDIT_AMENDMENT2_DRAFT_2026-07-31.md`, unsigned).

**Not independently verified by a second human.** See §7.

---

## 1. Why this was needed

The 2026-07-15 extraction recorded a `source_sha256` per claim but **archived no
source documents**. Nothing in the repository or in `~/scratch/flipeval` held a
copy of any of the 17 sources. A hash without the artifact it fingerprints
cannot be checked against anything, so the audit's provenance chain was, until
today, unverifiable in principle.

The sources are now archived: `docs/audit_sources_20260731.tar.gz`
(570,035 bytes, sha256 `a912a1e7af0efd58459dcf57ade84be96cfea8337147a13d336dacfdb9240259`,
checksum in `.sha256`, per-file manifest in `docs/audit_sources_manifest.tsv`).
Round-trip verified: extracted and re-hashed all 17 files against the manifest,
0 mismatches.

> **Status correction, 2026-08-02.** That archive is a **private working copy**
> and stays private. It is not released, published, mirrored or downloadable, and
> nothing in the paper, the README or any release note may describe it as an
> artifact. The redistribution review in §10 is why. What is published is the
> manifest, the digests, the pinned version identifiers and
> `scripts/fetch_audit_sources.py`.

## 2. The hashing method, recovered

`source_sha256` was never a registered §3.2 extraction field, no script in the
repository computes it, and `AUDIT_RECONCILIATION_2026-07-15.md` says only that
"Pass 2 recorded sha256 of fetched". The method was therefore unknown, which
made any mismatch uninterpretable.

It has been recovered by reproduction:

| Source class | Hashed artifact |
|---|---|
| arXiv papers (R01–R07) | ar5iv full-text HTML, `ar5iv.labs.arxiv.org/html/<id>` |
| HF model cards (R08–R10, R15–R17) | raw `README.md` bytes |
| GitHub-hosted docs (R12) | raw Markdown from `raw.githubusercontent.com` |

Each was confirmed by exact reproduction of the recorded digest. For R01 the
candidates were tested explicitly: PDF `35e33917…`, extracted text `a9110853…`,
abs page `9f2c644d…`, ar5iv `5f8745bf…` — the last matching the recorded value.

## 3. Retrieval and hash results

**15 of 17 byte-identical to the 2026-07-15 capture. 1 mismatch. 1 no baseline.**

| Claims | Result | Basis |
|---|---|---|
| R01–R07 | **MATCH** | All seven arXiv papers pinned to the version current on 2026-07-15; every latest version predates the audit fetch, so today's fetch is the version pass 2 saw. |
| R08–R10, R15–R17 | **MATCH** | HF READMEs pinned by commit. None was modified after 2026-07-15; the two closest (R08, R15) were last touched 2026-07-10, five days before the fetch. |
| R12 | **MATCH** | TensorRT-LLM Markdown unchanged on `main`. |
| R14 | **MATCH** | vLLM blog, live fetch, stable. |
| R11 | **MISMATCH** | See below. |
| R13 | **NO BASELINE** | `source_sha256` is empty in the frozen claim table, so today's fetch has no *prior* digest to check against. See the 2026-08-02 note below: a digest of today's capture **is** recorded in the manifest. |

**R11 (Meta blog) — the mismatch is not evidence of drift.** Two fetches made
seconds apart produced different digests (`4afd4da2…` / `5dba7ea7…`) and
different lengths (187,169 / 187,178 bytes). The page carries per-response
dynamic content, so its recorded hash was never a reproducible fingerprint. It
can neither confirm nor refute a content change. The claim text is present in
both fetches. Treat R11 as substantively verified, cryptographically unverified,
and record it that way.

## 4. Quote re-verification

All 17 `exact_quote` values were re-checked against complete source text.
**Sixteen are present in the source. One is not.**

**The five `pass1 summarizer-derived` quotes all verified exact** — R01, R02,
R03, R06, R11. This is the provenance gap flagged as the sharpest open risk, and
it did not materialise. In particular **R01 (GPTQ), which carries the entire
`K = 1` reading at the registered 2 pp margin, is confirmed verbatim.**

Four required normalization or disclosure:

- **R04** — exact, modulo an ar5iv rendering artifact: the source renders `4×`
  as `4×\times`, so a literal string match fails on `4x`.
- **R09** — exact, modulo Markdown link syntax inside the quoted span
  (`on the [OpenLLM](…) benchmark`).
- **R17** — exact. The `…` in the recorded quote elides a Markdown link; the
  full sentence reads "It achieves an average score of 68.69 on the [OpenLLM](…)
  benchmark (version 1), whereas the unquantized model achieves 68.54." A quote
  containing an ellipsis is a splice and should be marked as such.
- **R10 — DEFECT. The quote does not appear in the source.** Recorded as
  "average recovery percentage across all benchmarks is 98.6%" and marked
  `pass1 raw-verified`, but the card contains no such sentence and no prose
  equivalence claim at all. `98.6%` is a table cell. The extractor composed a
  sentence from tabular data and recorded it as a quotation.

## 5. Two source defects found in passing

Neither changes any verdict; both are reportable observations about the sources.

**R17 contradicts itself.** Its prose says the quantized model achieves 68.69
and the unquantized 68.54. Its table is headed `Benchmark | Meta-Llama-3-8B-Instruct
| …quantized.w8a16 (this model) | Recovery` and its Average row reads
`68.69 | 68.54 | 99.8%`, i.e. baseline 68.69 and quantized 68.54 — the opposite
assignment, confirmed by the recovery figure (68.54/68.69 = 99.78%). The audit
extracted the prose faithfully; the source's own two statements disagree on the
sign of the delta. Magnitude is 0.15 pp either way, so no computed quantity moves.

**R10's Average recovery cell is internally inconsistent.** Average row reads
`73.16 | 72.69 | 98.6%`, but 72.69/73.16 = 99.4%, and the mean of the six
per-task recoveries is also 99.4%. The `98.6%` appears to be a copy of the MMLU
row. Reported for completeness.

## 6. Full-text keyword sweep

The registered vocabulary — *margin, tolerance, equivalent, equivalence,
negligible, acceptable, parity, within, degradation, difference, delta,
percentage point, confidence, significance* — was run over complete text of all
17 sources, including tables, captions, footnotes, appendices and reference
lists. Model cards were searched as **raw Markdown**, not rendered output.

Findings on the decisive terms:

- **`parity`: zero occurrences across all 17 sources.**
- **`percentage point`: zero occurrences across all 17 sources.**
- **`margin` (25 hits): none is an equivalence margin.** Every hit is CSS
  (`style="margin: 0"` in Red Hat card headers), the idiom "outperforms … by a
  large margin", or ar5iv page-layout warnings (`topmargin has been altered`).
- **`tolerance` (2 hits): neither declares one.** R13's is a code-module index
  in the docs navigation sidebar. R12's is substantive and points the other way:
  *"users might have different tolerances on accuracy impact and calibration
  time"* — the source explicitly declines to fix a threshold.
- **`acceptable` (1 hit):** R01, *"maintain acceptable runtimes"* — about
  runtime, not accuracy.
- **`equivalent`/`equivalence` (14 hits): all mathematical**, describing
  transformations that preserve a function (SmoothQuant's "mathematically
  equivalent transformation", LLM.int8()'s scaling identities). None is
  statistical equivalence.

A second sweep for numeric-bound constructions (`within X`, `at most X`, `no
more than X`, `less than X points`, `threshold/criterion/tolerance of X`)
returned only post-hoc descriptions of observed results: R01's perplexity
figures ("less than 1.5 points", "a less than 1 point drop" — perplexity, not
benchmark accuracy), R02's "maximum of 0.3%" describing an ablation outcome,
R07's "up to 60%" and "at most 10%" which are *sparsity levels* rather than
accuracy tolerances, and R14's "at most 0.7 points" describing measured spread.

No model card states an acceptance criterion. Every `recovery` figure is a
reported outcome, and "Validated on: RHOAI 2.20, RHAIIS 3.0, RHELAI 1.5" refers
to software platform versions, not accuracy validation.

## 7. Classification

Applying the three-way distinction — prospectively declared tolerance /
post-hoc description of an observed delta / generic adjective without a
numerical bound:

| Category | Count | Claims |
|---|---|---|
| **(a) Prospectively declared tolerance** | **0 of 17** | — |
| (b) Post-hoc description of an observed delta | 7 of 17 | R08, R09, R10, R14, R15, R16, R17 |
| (c) Generic adjective, no numerical bound | 10 of 17 | R01, R02, R03, R04, R05, R06, R07, R11, R12, R13 |

**The full-document claim holds.** No source in the audited population declares
an equivalence margin. Category (a) is empty, so the "formal equivalence claim"
branch of the draft amendment does not fire for any claim, and every
`claimed_margin_pp` in `results/audit_verdicts_rev2.csv` is a quantity the
analysis constructed from the source's reported results.

R14 remains the closest case and resolves to (b), as the draft amendment
anticipated in writing before this verification ran: "at most 0.7 points"
appears as *"shows negligible accuracy impact (at most 0.7 points)"* — a
parenthetical characterising a measured outcome, not a bound the source
undertakes to stay within.

**Verification status of this classification.** Single automated pass, at
Amogh's direction, with all supporting text quoted above and every source
archived for re-checking. It is **not** independent human dual coding. The
project has no second human; `AUDIT_REGISTRATION_2026-07-15.md` §3.3 calls
double extraction a "solo-author substitute for dual coding" for that reason.
Any agreement statistic computed between this pass and the 2026-07-15 passes
would measure one model against another, and must not be reported as
inter-coder reliability.

## 8. Open items this creates

1. **R10's quote is not a quote.** The frozen claim table is frozen; correcting
   it requires a dated amendment, and the correction is to the `exact_quote`
   field, not to any margin. R10's inclusion under §3.1 also needs review, since
   inclusion requires an assertion "in prose or a table caption" and R10's is in
   neither.
2. **R13 has no recorded source hash** *in the frozen claim table*, and cannot
   be pinned to its July state. It is not hashless: `audit_sources_manifest.tsv`
   records `92cf7d8e…` for the 2026-07-31 capture, so a re-fetch verifies
   against that capture. What is missing is a *pre-capture* baseline. Stated
   this way from 2026-08-02; the shorter form above reads as "no hash exists",
   which is false and was written into a draft docstring before being caught.
3. **R11 cannot be cryptographically verified** and never could have been.
4. Whether §3.2 should be extended to require **archiving** sources, not just
   hashing them. This gap cost nothing here only because 15 of 17 sources
   happened to be independently version-pinnable.

## 9. Sensitivity of the surviving power flag (added 2026-07-31)

Computed after §7, to test whether "K = 0 under plausible sensitivity" is a real
possibility or a technicality. Reproduced in pure Python — the login node has no
scipy, so `audit_stats` cannot be imported there. The reproduction returns 792
cells with median 0.1300, matching the `discordance_n_cells` and
`imputed_discordance` recorded for R01 in `results/audit_verdicts_rev2.csv`,
which is what validates it.

R01's imputation is the **median** over the 792 atlas cells matching at tier
`family+bits` (GPTQ, 4-bit). That distribution, with the required *n* each value
implies at the registered 2 pp margin:

| | discordance | required n | R01, n = 1,838 |
|---|---|---|---|
| min | 0.0000 | — | — |
| p10 | 0.0572 | 885 | adequate |
| p25 | 0.0882 | 1,364 | **adequate — K = 0** |
| **median (imputed)** | **0.1300** | **2,010** | underpowered — K = 1 |
| p75 | 0.2800 | 4,328 | underpowered — K = 1 |
| p90 | 0.5481 | 8,472 | underpowered |
| max | 0.7402 | — | underpowered |

Required *n* is proportional to discordance — `paired_flip_sd` returns
`sqrt(d)` and `required_n_for_tost` squares it — so the classification reverses
where required *n* falls to R01's reported 1,838: at **d ≈ 0.1189**
(d = 0.1188 → 1,837, adequate; d = 0.1190 → 1,840, underpowered). Integer
ceilings make the exact boundary slightly rough, so it is reported as
approximate.

**345 of the 792 supporting cells — 43.6% — lie below the reversal point.** The
interquartile range is [0.088, 0.280], a factor of 3.2, with p10 = 0.057 and
p90 = 0.548.

The single surviving power flag is therefore close to a coin flip on which point
statistic is drawn from a highly dispersed distribution. It must be reported as a
**sensitivity-dependent planning flag, not a stable binary verdict**, and never
without its reversal point and this fraction. This makes advisor item 1.5
(imputation uncertainty) load-bearing rather than optional polish: it is now the
item that determines whether the audit has a quantitative power finding at all.

## 10. Redistribution review and the published package (added 2026-08-02)

Closes open item 4 of §8 and the two licensing lines of the final rev-3
checklist §8. Amogh chose **Option A** on 2026-08-02.

### What was checked

The terms attached to each of the 17 sources were examined before any copy was
published, which is the order the checklist requires ("audit redistribution
licenses **before** publishing archived copies").

| Sources | Finding |
|---|---|
| R11 (Meta AI blog), R12 (NVIDIA TensorRT-LLM doc), R13 and R14 (vLLM pages) | **No redistribution right granted.** Nothing attached to these four pages permits a third party to republish their text. |
| R01–R07 (arXiv method papers) | **arXiv default licence.** It grants arXiv the right to distribute; it does not extend that right to third parties. |

### What was concluded

**"Publish everything" was never an available option.** Four sources alone are
sufficient to rule out republishing the corpus, and the arXiv default licence
rules out the seven papers independently. Because the corpus cannot be published
as a whole, the remaining sources were not individually cleared for
redistribution: clearing them would change nothing about the outcome.

**This is a record of what was checked and what it found. It is not legal
advice and asserts nothing about what redistribution is lawful in general.**

### What is published instead (Option A)

Everything needed to rebuild the corpus and confirm it is the same one the audit
read, and nothing that republishes the sources:

1. **Source URL per claim.** `docs/audit_claim_table.csv`, frozen, column
   `source_url`.
2. **Pinned version identifier, byte count, SHA-256 and provenance status per
   source.** `docs/audit_sources_manifest.tsv`.
3. **Retrieval script.** `scripts/fetch_audit_sources.py`. `--manifest`,
   `--claims` and `--out` are all required with no defaults; `--offline`
   verifies a directory already on disk and fetches nothing.
4. **Compliant excerpts.** The recorded `exact_quote` values, with their
   locations, in the paper.

**Kept private:** `docs/audit_sources_20260731.tar.gz`, its `.sha256`, and the
sealed copy outside the repository. The tarball remains committed in git history
and cannot be removed without rewriting 21 commits, one of which (`bb45528`) is
cited in the signed Amendment 2. That rewrite is **blocked pending a dated
amendment only Amogh can sign**, and the branch therefore stays unpushed. See
`SESSION_HANDOFF_2026-08-02.md` §3.

### Provenance limits, stated precisely

Verified 2026-08-02 against `docs/audit_sources_manifest.tsv`,
`docs/audit_claim_table.csv` and the code of `scripts/fetch_audit_sources.py`,
plus an offline run of the script over the archive (`17 verified, 0 drifted,
0 expected-drift, 0 unverifiable, 0 failed`, exit 0).

**R11 is `MISMATCH`, and the drift is expected.** The page is served with per-response
content: the two fetches of 2026-07-31 differed by 9 bytes. The digest recorded
in the frozen claim table (`81ba9d09…`) was therefore **never a valid
fingerprint** of the page, and it can neither confirm nor refute a content
change. `fetch_audit_sources.py` lists R11 in its `UNSTABLE` map, so a live run
prints `EXPECTED-DRIFT` and does not fail. R11 is substantively verified,
cryptographically unverified, and must be described that way.

**R13 is `NO-BASELINE`, which is not the same as "no hash".** The manifest
records `92cf7d8eb55f5d5d900d15633919ff57f0deec9e5fcbf6d78ba108fd6c9784d1` for
the 2026-07-31 capture, so a re-fetch **can** be checked against the archived
capture, and the offline run above verifies it. What is missing is a digest
recorded *before* that capture (`source_sha256` is empty for R13 in the frozen
claim table), so **the capture itself was never independently corroborated**.
Verifying against it proves you hold the bytes the audit read; it does not prove
those bytes were the page as it stood when the claim was extracted.

Neither limitation is to be softened. Provenance for these two is documentary,
not cryptographic, and neither may be described anywhere as hash-verified. The
first draft of the script's docstring claimed R13 had no recorded hash at all;
the offline run contradicted it and it was corrected before commit.

### Where this is stated in the shipped material

- `paper/sections/artifacts.tex`, paragraph "The audited sources are identified,
  not redistributed". The primary statement.
- `paper/sections/appendix_artifacts_detail.tex`, datasheet "Distribution and
  licensing". The same decision as a datasheet entry.
- `README.md`, "Audited source corpus". The reader-facing rebuild instructions.
- `paper/sections/audit.tex`. The extraction sentence now says hashes were
  recorded for 16 of 17, not for all of them.
