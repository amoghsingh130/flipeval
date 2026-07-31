# Paper carry checklist — rev-2 → rev-3 audit verdicts

Built 2026-07-31 from the paper text and `results/audit_verdicts_rev3.csv`
(job `11591245`, sha `c85d6f8a…b150082b`, single run under Amendment 2).

Work top to bottom. **Nothing here is a judgement call about framing** — that is
§7 below and is Amogh's. Items 1–6 are carrying computed values.

## The rev-3 numbers, in one place

| Quantity | rev-2 (in the paper now) | rev-3 (correct) |
|---|---|---|
| Population | 17 audited | 17 candidates, **16 eligible** (R10 out) |
| Not assessable | $J = 5$ of 17 | $J = 5$ of 16 (4 insufficient + 1 metric-incompatible) |
| Assessable | 12 determinate | **11** |
| Headline | $K = 4$ of 12 underpowered for their own assertion | **$K = 1$ of 11** below the planning threshold at 2 pp |
| Which claims | R17, R07, R06, R15 | **R01 only** |
| Robustness | not reported | **0 robustly below / 10 robustly above / 1 imputation-sensitive** |
| Margin categories | not reported | **0 formal / 12 informal / 4 unquantified**; 10 state no number |
| Per-item outputs | 0 of 17 | 0 yes / 3 partial / 13 no, of **16** |
| Shortfall range | $2.0\times$–$12.9\times$ | **withdrawn** (see item 3) |

**R01 detail, needed wherever it is reported:** $n = 1{,}838$ against required
$2{,}010$ at imputed $d = 0.13$; reverses at $d = 0.118915$; **345 of 792**
tier cells (43.6%) below the reversal point.

---

## 1. `abstract.tex` — the audit sentence

Current: *"…5 cannot be evaluated from what they report, 4 of the remaining 12
are underpowered for the margin they assert, and none of the 17 releases the
per-item outputs…"*

Three defects: the count, the denominator, and **"the margin they assert"** —
which is the exact phrase Amendment 2 forbids, since no source asserts one.

Replace with Amogh's agreed text (2026-07-31), which leads with the reporting
findings:

> Across 16 eligible sources drawn from 17 frozen candidates, none reported an
> a priori numerical equivalence margin or released per-item outputs for the
> tasks supporting the audited claim. Five could not be assessed under our
> registered binary paired-outcome framework. At a uniform 2-percentage-point
> margin, one of 11 assessable claims fell below the point-estimate planning
> threshold, although this classification was sensitive to the imputed
> discordance rate.

**Re-measure the arXiv character count after editing.** The limit is 1,920,
confirmed from info.arxiv.org, and the current margin is 37 characters. Measure,
never eyeball — the file's own closing note says how.

## 2. `sections/audit.tex` — the results subsection

- **L193–195** — "Of the 17 claims, 5 are indeterminate … Of those 12, $K = 4$
  are underpowered for their own assertion." Rewrite to 16 eligible / 5 not
  assessable / 11 assessable / $K = 1$. Drop "for their own assertion" everywhere.
- **L196–216, `tab:audit-underpowered`** — **the whole table is now wrong.** Its
  four rows (R17, R07, R06, R15) are all *robustly above* the threshold at 2 pp;
  its caption says "at the margin the claim itself asserts is negligible", and
  its "Stated margin" column heading names a quantity no source stated. Replace
  with a single-row table for R01 carrying $n$, required $n$, the imputed $d$,
  the reversal point and the 43.6%, or fold it into prose — one row does not
  need a table.
- **L237–246, the MDD-ratio table** — divides by the withdrawn margin. Either
  recompute against 2 pp or move to the superseded-values appendix.
- **L275–284, the sensitivity paragraph** — currently says the uniform-2 pp
  reading is *secondary* and gives "1 of 12". Under Amendment 2 that reading is
  **primary**, and the count is 1 of 11. The paragraph's careful distinction
  between "underpowered under an alternative yardstick" and "margin-sensitive"
  still holds and is worth keeping — both still land on R01.
- **L115** — "0 of the 17 audited sources release the per-item outputs" → 16.
- **L293** — "$J = 5$ of the 17 claims" → of 16.
- **L336–340** — the rev-1 narrative ("$38.3\times$", "$K = 5, J = 4$ to
  $K = 4, J = 5$"). Now describes a superseded chain. Keep as history but mark it
  as pre-Amendment-2.
- **23 `% SOURCE:` comments across `sections/` cite `audit_verdicts_rev2.csv`.**
  Repoint to `_rev3.csv`. This exact class of stale pointer previously told a
  session to revert correct numbers — check each, don't sed blindly.

## 3. The shortfall range `2.0\times`–`12.9\times`

Appears in `introduction.tex` (L45–46 comment), `appendix_prereg_detail.tex`
(L146, "$2$–$13\times$"), and the audit tables. It is the ratio of required $n$
to reported $n$ **at the result-derived margins**, so it is withdrawn wholesale.
Do not recompute it at 2 pp and reuse the sentence: at 2 pp ten of eleven claims
have no shortfall at all, so the quantity has no range to report.

## 4. `sections/conclusion.tex` L11–12

"4 of 12 determinate claims underpowered for their own assertion, 5 of 17
unevaluable, 0 of 17 …" — all three, plus the forbidden phrase.

## 5. `sections/preregistration.tex` and `appendix_prereg_detail.tex`

- **`preregistration.tex` L125–130** and **`appendix_prereg_detail.tex`
  L109, L117, L160, L275** carry the $K = 5 \to K = 4$ derivation, which is now
  a history of a superseded rule.
- **The two marked bad-reasoning sites** flagged in the 2026-07-31 handoff —
  `preregistration.tex:128` and `appendix_prereg_detail.tex:115`, both reading
  *"a source asserting parity within 0.15 pp has made a 0.15 pp claim"*. R17's
  0.15 is the observed delta. **These are the sentences Amendment 2 exists to
  correct; they must not survive.**

## 6. `sections/appendix_audit_table.tex` — the three claim tables

- **R10 row (L32, L63, L94)** must be marked ineligible with its basis, not
  deleted. An exclusion you cannot see is not auditable, and the amendment
  requires the original row to remain accessible.
- The power table (L63) has a `margin` column and an `adequate` verdict column
  in the old vocabulary. Regenerate from `_rev3.csv`.
- **L167** — "Margin-sensitive (1 of 12 determinate)" → of 11.
- **Regenerate, do not hand-edit.** The generator that built these lives in a
  session scratchpad and was never committed; rebuilding it is part of this item.
  Validate it the way the certification generator was validated: regenerate a
  table you already trust and diff before trusting it on one you don't.

## 7. Framing — Amogh's call, not mechanical

The ordering agreed 2026-07-31 (advisor: *make the audit support the toolkit*):

1. 0 of 16 reported an a priori numerical equivalence margin.
2. 0 of 16 released per-item outputs for the tasks supporting the claim.
3. 5 of 16 not assessable under the registered framework.
4. 1 of 11 below the planning threshold under point imputation, reversing to 0
   under plausible sensitivity.

**The strongest available sentence, and it was not predictable before the run:**
*no claim is robustly below the threshold.* Ten of eleven hold their verdict
across the entire interquartile range; the single flag is the only unstable one.
Consider leading item 4 with that rather than with $K = 1$.

## 8. Traps

- **R14 sits at $n = 728$ against 742 required at 2 pp** — 14 items short. It is
  *not* counted, because it is indeterminate for insufficient reporting. If any
  future amendment resolves its indeterminacy, $K$ changes. Do not let a later
  session "notice" this and quietly add it.
- **Three sources released per-item outputs** (R08, R15, R16) — for Arena-Hard,
  OpenLLM v2 and HumanEval, but not for the OpenLLM v1 tasks their claims rest
  on. "None released" is true only with the task-matched qualifier. State it in
  the same sentence or a reviewer who finds those datasets will think the claim
  was overstated.
- **Do not describe R04 as "incompatible with a paired framework."** CIDEr
  supports paired resampling. It is outside *our registered binary
  paired-outcome calculation*.
- **The artifact disagreement is now live.** v1.0.0 (`10.5281/zenodo.21708923`)
  is public with rev-2 verdicts. Either cut v1.1 citing a new version DOI, or add
  an explicit mapping note in `artifacts.tex` saying which figures come from which
  revision. Unresolved either way, paper and citable record contradict each other.
- **Every new URL/DOI must route through a `main.tex` macro** or the anonymous
  build silently de-anonymises. `paper/tools/check_paper.py` is the only guard.

## 9. Gates for this work

`paper/` is outside the source fingerprint: plain commits, no freeze, no test
gate. After content edits run `paper/tools/check_paper.py` (refs, cites,
environments, anonymous-build leak check) and regenerate `READING_COPY.md`
**after** the content commit, in a separate commit, or the hash it names is stale
on arrival.

Negative-control any checker before believing a finding — that has now caught
four checker bugs that each looked like a document defect.
