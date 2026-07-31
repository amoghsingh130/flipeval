# Paper carry checklist — rev-2 → rev-3 audit verdicts

Built 2026-07-31 from the paper text and `results/audit_verdicts_rev3.csv`
(job `11591245`, sha `c85d6f8a…b150082b`, single run under Amendment 2).
**Revised the same day** with twelve additions from advisor review, plus two
defects that review surfaced (§0).

Items 1–6 carry computed values. §7 is framing and is Amogh's. §§8–17 are the
safeguards. **§0 must be read first: it changes what some of the other items
should say.**

---

## 0. Two defects found while building this checklist

### 0.1 The margin taxonomy contradicts itself as currently named

`AUDIT_MARGIN_CATEGORY formal=0 informal=12 unquantified=4` and "10 of 16 state
no number at all" are both correct and cannot both be reported in those words:
**7 of the 12 "informal" claims contain no number at all.** Calling them
*informal margins* implies a quantitative claim made loosely, and reads as
inconsistent with the 0-of-16 headline.

The two are different axes. Report the cross-tab, not the marginals:

| | qualitative only | retrospective number | **total** |
|---|---|---|---|
| **assessable** (cat 2) | 7 — R01,R03,R04,R05,R06,R07,R12 | 5 — R08,R09,R15,R16,R17 | **12** |
| **not assessable** (cat 3) | 3 — R02,R11,R13 | 1 — R14 | **4** |
| **total** | **10** | **6** | **16** |

Prospective numerical decision margin: **0**, the empty row that is the finding.

Rename the constructs so the axes cannot be confused:
*prospective numerical decision margin* / *retrospective numerical description*
/ *qualitative equivalence language only*. Never "informal margin".

### 0.2 R06 and R07 impute from 4-bit quantization cells, via a parser artifact

Both are 50% unstructured **pruning** claims with no bit width. Both match at
tier `bits` over 183 atlas cells. Those 183 cells are `bnb-4bit(unclear)` (61),
`QLoRA-4bit` (61) and `bnb-4bit(DPO-FT)` (61) — **all 4-bit quantization**. They
carry `bits=None` only because their labels are absent from `_METHOD_PROFILE`,
not because they lack a bit width. The match is on *missingness in the parser*,
shared by claim and cell, and is not substantive.

Two pieces of documentation state the opposite and are wrong:

- `nearest_cell_discordance` docstring: *"A tier whose target field is None can
  never match (`cell.bits == None` is false for every real cell)"*. It is true
  for every cell whose method label is mapped, and false for 183 that are not.
- `CLAIM_PROFILES["R06"].notes`: *"the atlas contains no pruning cells, so
  imputation descends to the global tier by construction."* Under rev-2 it
  descends to `bits`, not global. This is a **rev-1 survivor in a code comment**
  — the eighth found in this project.

**Do not change the imputation.** It is registered, Amendment 2 explicitly does
not reopen it, and results are inspected. Neither verdict moves (R06 n = 18,904
and R07 n = 12,410 against 6,046 required even at Q3, robustly above). This is a
**disclosure and limitations item**: fix the two comments, and state in the paper
which claims matched at which tier and that two matched on absent bit width
rather than on method similarity.

---

## The rev-3 numbers, in one place

| Quantity | rev-2 (in the paper now) | rev-3 (correct) |
|---|---|---|
| Frozen candidates | 17 audited | 17 |
| Ineligible after verification | — | **1** (R10) |
| Eligible | 17 | **16** |
| Numerically assessable | 12 determinate | **11** |
| Not assessable | 5 | 5 (4 insufficient + 1 metric-incompatible) |
| Below threshold at median imputation | $K = 4$ | **1** (R01) |
| **Below throughout the atlas IQR** | not reported | **0** |
| Changes classification within IQR | not reported | **1** |
| Above throughout IQR | not reported | **10** |
| Task-matched per-item outputs | 0 of 17 | **0** of 16 |
| Outputs for other tasks only | 3 | 3 |
| No identified outputs | 14 | **13** |
| Shortfall range | $2.0\times$–$12.9\times$ | **withdrawn** (§3) |

**R01 detail, required wherever it is reported:** $n = 1{,}838$ against $2{,}010$
at imputed $d = 0.13$; reverses at $d = 0.118915$; **345 of 792** tier cells
(43.6%) below the reversal point.

**Per-claim IQR sensitivity, for the appendix table §11 requires:**

| Claim | $n$ | tier | $n_{req}$@Q1 | @median | @Q3 | classification |
|---|---|---|---|---|---|---|
| R01 | 1,838 | family+bits | 1,364 | 2,010 | 4,328 | **changes within IQR** |
| R03 | 18,300 | family+bits | 619 | 866 | 1,237 | above throughout |
| R05 | 14,042 | bits+benchmark | 1,525 | 2,255 | 3,865 | above throughout |
| R06 | 18,904 | bits *(see §0.2)* | 932 | 1,841 | 6,046 | above throughout |
| R07 | 12,410 | bits *(see §0.2)* | 932 | 1,841 | 6,046 | above throughout |
| R08 | 42,701 | family+bits | 371 | 742 | 1,052 | above throughout |
| R09 | 42,701 | family+bits | 433 | 742 | 1,113 | above throughout |
| R12 | 14,042 | family+bits | 433 | 742 | 1,113 | above throughout |
| R15 | 42,701 | family+bits | 619 | 866 | 1,237 | above throughout |
| R16 | 42,701 | family+bits | 371 | 742 | 1,052 | above throughout |
| R17 | 28,659 | bits+benchmark | 1,332 | 2,081 | 3,644 | above throughout |

---

## 1. `abstract.tex` — the audit sentence

Current: *"…5 cannot be evaluated from what they report, 4 of the remaining 12
are underpowered for the margin they assert, and none of the 17 releases the
per-item outputs…"*

Wrong count, wrong denominator, and **"the margin they assert"** is the exact
construction Amendment 2 exists to retire. Replace with the agreed text,
amended per §8 to avoid the unbounded robustness claim:

> Across 16 eligible sources drawn from 17 frozen candidates, none reported an
> a priori numerical equivalence margin or released per-item outputs for the
> tasks supporting the audited claim. Five could not be assessed under our
> registered binary paired-outcome framework. Among the remaining 11, ten stayed
> above the approximate planning threshold throughout an atlas-IQR sensitivity
> interval at a uniform 2-percentage-point margin; one changed classification
> within it.

**Re-measure the arXiv character count after editing** — limit 1,920, current
margin 37 characters. Measure, never eyeball.

## 2. `sections/audit.tex`

- **L193–195** — rewrite to 16 eligible / 5 not assessable / 11 assessable.
  Drop "for their own assertion" everywhere it appears.
- **L196–216, `tab:audit-underpowered`** — **all four rows are now above
  threshold, robustly.** Do not replace with a one-row R01 table: a single row
  looks constructed around the only flag. Use the three-row summary (§11), with
  all 11 claims in the appendix.
  **Rename the label**, not just the caption — `tab:audit-underpowered` is
  itself a stale claim (§14).
- **L237–246, MDD-ratio table** — divides by the withdrawn margin. Recompute at
  2 pp or move to the superseded-values appendix.
- **L275–284** — says the uniform-2 pp reading is *secondary*. It is now
  **primary**; count is 1 of 11. The paragraph's distinction between "underpowered
  under an alternative yardstick" and "margin-sensitive" still holds and both
  still land on R01 — keep it.
- **L115** "0 of the 17" → 16, with the task-matched qualifier (§15).
- **L293** "$J = 5$ of the 17" → of 16.
- **L336–340** — the rev-1 narrative ($38.3\times$, $K=5,J=4 \to K=4,J=5$). Keep
  as history, mark explicitly as pre-Amendment-2.
- **23 `% SOURCE:` comments cite `audit_verdicts_rev2.csv`.** Repoint to
  `_rev3.csv`. **Check each individually** — this class of stale pointer
  previously instructed a session to revert correct numbers.

## 3. The shortfall range $2.0\times$–$12.9\times$

In `introduction.tex` (L45–46), `appendix_prereg_detail.tex` (L146), and the
audit tables. It is required-$n$ over reported-$n$ **at the result-derived
margins**, so it is withdrawn wholesale. **Do not recompute at 2 pp and reuse the
sentence** — ten of eleven claims have no shortfall at all, so there is no range.

## 4. `sections/conclusion.tex` L11–12

All three counts plus the forbidden phrase.

## 5. `preregistration.tex` / `appendix_prereg_detail.tex`

- `preregistration.tex` L125–130 and `appendix_prereg_detail.tex` L109, L117,
  L160, L275 carry the $K=5 \to K=4$ derivation: now history of a superseded rule.
- **The two marked bad-reasoning sites** — `preregistration.tex:128` and
  `appendix_prereg_detail.tex:115`, both *"a source asserting parity within
  0.15 pp has made a 0.15 pp claim"*. R17's 0.15 is the observed delta. **These
  are what Amendment 2 exists to correct; they must not survive.**

## 6. `appendix_audit_table.tex`

- **R10 (L32, L63, L94)** — mark ineligible with its basis, **do not delete**.
  The amendment requires the original row to remain accessible.
- Power table (L63) uses the old margin vocabulary. Regenerate from `_rev3.csv`.
- **L167** "Margin-sensitive (1 of 12 determinate)" → of 11.
- **Regenerate, never hand-edit.** The generator was never committed; rebuilding
  it is part of this item. Validate it by regenerating a table already trusted
  and diffing, before trusting it on one that is not.

## 7. Framing — Amogh's call

Ordering agreed 2026-07-31 (*make the audit support the toolkit*):

1. 0 of 16 reported an a priori numerical equivalence margin.
2. 0 of 16 released task-matched per-item outputs.
3. 5 of 16 not assessable under the registered framework.
4. Among 11 assessable, none stayed below the threshold throughout the
   sensitivity interval; one changed classification within it.

---

# Safeguards

## 8. Say exactly what "robust" means, and no more

**Do not write "no claim is robustly underpowered."** Write:

> No claim remained below the approximate planning threshold throughout the
> atlas-IQR sensitivity interval.

The paper must also state, wherever the classification is used:

- Robustness is evaluated **only over the atlas-IQR interval**, not over every
  plausible discordance model.
- **The IQR analysis was added after the point-imputation result was seen.**
  That is the actual chronology (2026-07-31) and it must be disclosed.
- **43.6% is a descriptive fraction of reference cells** — not a posterior
  probability, not a confidence level, not a p-value.
- **Atlas cells are correlated** (shared model pairs, benchmark families,
  sources, infrastructure) and are **not** independent draws. This is the same
  limitation §1.6 of the advisor review raises; keep the two consistent.
- The interval claim is established **at the endpoints by monotonicity** —
  required $n$ is increasing in $d$, so Q1 and Q3 bracket the whole interval.
  Say so; do not let it read as inferred from the scatter of observed cells.

## 9. One machine-checked denominator ledger

Generate LaTeX macros from `_rev3.csv`; **the manuscript must never type these
numbers itself.** Test every identity:

- $17 - 1 = 16$
- $11 + 5 = 16$
- $4 + 1 = 5$ (insufficient + metric-incompatible)
- $0 + 3 + 13 = 16$ (task-matched + other-task-only + none)
- $0 + 1 + 10 = 11$ (below throughout + changes within + above throughout)
- cross-tab §0.1 sums to 16 both ways

Plus the structural invariant that closes the R14 trap programmatically:
**an `assessable = false` row can never carry a threshold verdict.**

## 10. Make R14's exclusion executable

Regression test: R14 has $n = 728$ against a hypothetical 742 required, **but
`assessable = false`, so verdict = NA and $K$ is unchanged.** The output must
explain why it is non-assessable *despite having a visible $n$* — otherwise a
reviewer, or a later script, will reasonably ask why it was dropped.

## 11. Three-row main table, eleven-row appendix

Main text:

| Sensitivity classification | Count |
|---|---|
| Above throughout atlas IQR | 10 |
| Changes classification within atlas IQR | 1 |
| Below throughout atlas IQR | 0 |

Appendix: all 11 assessable claims with reported $n$, imputation stratum,
$n_{req}$ at Q1/median/Q3, $d^*$ where attainable, and classification — the
table already built above. List the 5 non-assessable claims separately with
their exact blockers.

## 12. Bind every table to provenance

Every generated table or certificate records: atlas filename **and revision**,
atlas sha256, audit-data sha256, toolkit commit, schema version, margin,
imputation rule **and stratum**, full command, output digest.

Add tests that: omitting `--atlas` fails; omitting `--output` fails; **rev-1 and
rev-2 produce their different, expected R01 required $n$** (1,936 vs 2,010); no
legacy `own_margin` field survives; $d^* < 0$ and $d^* > 1$ render as
unattainable boundaries; integer/ceiling boundaries behave consistently.

## 13. **The rev-1 default becomes a toolkit requirement, not a footnote**

The most transferable thing found this session. State it as a property of the
method:

> A certificate that does not identify its calibration evidence is invalid.

A required-$n$ figure is meaningless without the discordance corpus, revision and
stratum that produced it. The tool must refuse to emit an uncalibrated
certificate. Treating this as an implementation bug wastes it — it belongs in
the certification section as a design rule, with the near-miss as its evidence.

## 14. Stale-claim linter over the whole source

Search source, captions, footnotes, **comments**, appendices and supplement for:
`4 of 12`, `four claims`, `2.0×`, `12.9×`, `own margin`, `claim-specific
margin`, `margin they assert`, `Stated margin`, `audit-underpowered`,
`audit_verdicts_rev2`, `R17, R07, R06, R15`, `underpowered`.

**Review every hit individually — no blind replacement.** Some uses of
"underpowered" remain correct in background discussion. **Rename the LaTeX label
`tab:audit-underpowered`**, not merely its caption.

## 15. Narrative consistency check

Every major section must tell this story:

> Sixteen eligible sources were audited. None reported an a priori numerical
> equivalence margin or task-matched per-item outputs. Five were not assessable
> under the registered binary paired framework. Among the remaining eleven, ten
> remained above the approximate planning threshold throughout the atlas-IQR
> sensitivity interval; R01 changed classification within it. No claim was
> consistently below the threshold across the specified sensitivity analysis.

Inspect specifically: title, abstract, contribution list, introduction roadmap,
audit-results opening, discussion, limitations, conclusion.

Two standing wording rules: **three sources released per-item outputs for other
tasks** — "none released" is true only with the task-matched qualifier, in the
same sentence. And **R04 is outside our registered binary paired-outcome
calculation**, not "incompatible with a paired framework" — CIDEr supports
paired resampling.

## 16. Artifact, licensing, and the second human

**Zenodo.** Publish a new immutable version; never alter v1.0.0. Include a
rev-2 → rev-3 mapping note, changelog, regenerated commands, input/output
hashes, withdrawn and replacement claims, and a version-specific DOI. Cite the
version DOI where exact reproducibility matters.

**Redistribution.** Before publishing `docs/audit_sources_20260731.tar.gz`,
verify every source permits redistribution — papers, model cards and company
pages carry different licences. If any does not, release URLs, version
identifiers, hashes, retrieval scripts, manifests and short permitted excerpts,
and keep the full-text captures private. **This is not yet checked and the
tarball is already committed** — resolve before any public release.

**Second human.** Before submission, a real person other than Amogh verifies:
eligibility for all 17; exact quotations and locations; margin classification;
task-to-output matching; the five non-assessability reasons; R17's source
contradiction; R01's calculation and reversal point. Record disagreements and
resolutions. **Two model passes are not independent human verification** and
must never be described as such.

## 17. Anonymity for the TMLR build

Because the named arXiv version goes first: no links to the named arXiv, GitHub
or Zenodo artifact; anonymous supplementary archive; no author names, usernames
or absolute local paths; no identifying git history or remotes; no
acknowledgements, institutions or grants; scrubbed PDF **and ZIP** metadata;
check generated manifests and command logs for home-directory paths; and ensure
**artifact hashes do not themselves point reviewers at an identity-bearing
public release** — the source archive's digests are now published in
`audit_sources_manifest.tsv` and would resolve to the named repository.

Every new URL/DOI must route through a `main.tex` macro or the blind build
breaks silently. `paper/tools/check_paper.py` is the only guard.

## 18. Gates

`paper/` is outside the source fingerprint: plain commits, no freeze, no test
gate. Run `paper/tools/check_paper.py` after content edits; regenerate
`READING_COPY.md` **after** the content commit, separately, or the hash it names
is stale on arrival. Negative-control any checker before believing it — that has
caught four checker bugs that each looked like a document defect.
