# Second-pass trim candidates — audit / atlas / certification

**Produced 2026-07-26**, on the author's ruling that the second pass is **held**
until the H3 verdict lands, but the candidate list is stable now and should be
prepared in advance.

**Why the list is stable while the decision is not.** None of the three sections
covered here changes when H3 lands. The verdict adds material to `abstract.tex`,
`sections/introduction.tex`, `minigrid.tex`, `minigrid_escalation.tex`,
`conclusion.tex` and `limitations.tex` — and to none of `audit.tex`,
`atlas.tex` or `certification.tex`. So this list can be costed now and acted on
after.

**Baseline.** Main text after `eaf4962` is 11,673 words by the counter in this
document's method note (the commit's own counter says 11,192; the two differ in
tokenisation, not in ratio). The three sections here hold **5,304 words, 45% of
the main text**, and were cut by 1.9%, 1.9% and 0.0% respectively in the first
pass. All of the first pass's reduction came from `preregistration.tex`,
`harness_sensitivity.tex`, the deleted `sequential.tex`, and `artifacts.tex`.

**Ranking is by cost-to-value**: cheapest (least lost per word saved) first.
Word counts are paragraph-level and approximate (±5%).

---

## Tier A — recommended, low cost

### A1. `certification.tex` §"Scope and caveats" → appendix — **~230 w saved**

- **Passage.** L190, 261 w, beginning "These caveats travel with the table".
- **What is lost.** Nothing, if a one-sentence pointer stays in the main text
  ("Five caveats govern reuse of this table; see App. X"). The block is already
  prose-ified from a five-item list (2026-07-26) and reads as reference matter.
- **Numbers that relocate.** `mmlu_pro` 5, `ifeval` 8, `arc_challenge` 17,
  `gsm8k` 24, `hellaswag` 23, `winogrande` 23, `mmlu` 1,311, `bbh` 192,
  `math` 56, and the 99 probe cells. **All ten restate the `n_atlas_cells`
  column of Table~\ref{tab:certification}, which stays in the main text** — so
  the summary-restatement invariant is unaffected in either direction.
- **SOURCE comments.** One block comment (`% PROSE-IFIED 2026-07-26…`) moves
  verbatim with the text. No SOURCE is orphaned.
- **Risk.** Low. The one judgement call is the "conservative rather than
  optimistic" clause about family aggregation, which is a defensive point a
  reviewer may raise; keeping it in the main-text pointer sentence costs ~20 w.

### A2. `atlas.tex` §"Population caveats" → appendix, **partial** — **~145 w saved**

- **Passage.** L275, 181 w.
- **What is lost.** The census-vs-record distinction is the load-bearing part
  and is already flagged as retained-verbatim-as-instructed in the first pass.
  **Recommend keeping the bolded sentence** ("This is the public record of
  compression evaluation, not a census of quantization") plus its one-clause
  justification in the main text (~35 w) and moving the rest.
- **Numbers that relocate.** None. This passage carries no figures.
- **SOURCE comments.** Two lines pointing at
  `docs/ATLAS_MINING_REGISTRATION_2026-07-15.md` §2 move with the text.
- **Risk.** Low-moderate. The S1-no-declared-license limitation is a D&B
  reviewing concern; it is already duplicated in the datasheet
  (`\S\ref{sec:artifacts}`), so moving it to an appendix loses no coverage.

### A3. `audit.tex` §"What was audited" — trigger vocabulary + double extraction → `appendix_prereg_detail.tex` — **~80 w saved**

- **Passage.** L40, 188 w total; the movable parts are the trigger-vocabulary
  enumeration (~45 w) and the mutually-blind double-extraction sentence (~35 w).
- **What is lost.** Nothing in the main text's argument — the enumeration is
  protocol detail, and `appendix_prereg_detail.tex` already exists and already
  holds exactly this class of material.
- **Numbers that relocate.** `X ≥ 98`, `≤ 1 pp`. Neither is a result.
  **The `% SOURCE: docs/audit_claim_table.csv column frame: F1=7, F2=7, F3=3`
  comment must stay** with the "17 claims: 7 / 7 / 3" sentence, which stays.
  Do not let the SOURCE travel with the vocabulary list by accident.
- **Risk.** Low. Keep the sentence "Every claim meeting the criterion is
  audited; there is no discretionary sub-selection" in the main text — it is the
  anti-cherry-picking guarantee and is worth more than its 14 words.

---

## Tier B — available, moderate cost

### B1. `atlas.tex` §"The gray zone" — S1→S2 contrast paragraph — **~40 w saved**

- L174, 126 w. Restates Table~\ref{tab:atlas-strata} (0.138→0.048,
  0.026→0.009) in prose before interpreting it. Compressible to ~85 w by
  interpreting without restating.
- **Numbers.** All four restate the table, which stays. No SOURCE moves.
- **Cost.** The "better methods have made the difference smaller without making
  the evidence sufficient" conclusion must survive intact; it is the section's
  thesis.

### B2. `atlas.tex` §"Construction" — two-source description — **~40 w saved**

- L52, 130 w. Needed to read Table~\ref{tab:atlas-strata}; compressible to ~90 w.
- **Numbers.** W4A16/INT8/FP8, 8B/70B/405B — all needed, all stay.
- **Cost.** Low value *and* low saving. Do this only if hunting the last 100 w.

### B3. `audit.tex` §"The reproducibility zero" — interpretation paragraph — **~40 w saved**

- L102, 97 w, "more actionable than any power calculation because…".
  Compressible to ~60 w.
- **Numbers.** None; the `0 of 17` figure is in the preceding paragraph (L85)
  and stays.
- **Cost.** Moderate — this paragraph is what converts the zero from a
  statistic into a recommendation.

---

## Tier C — argued against; recorded so the decision is explicit

### C1. `audit.tex` §"R04: an exclusion we argue against our own interest" — 225 w

**Do not cut.** For an audit paper this passage *is* the credibility: it
documents removing the paper's own largest number (38.3×) and taking the
headline from K=5,J=4 to K=4,J=5. Cutting it to ~120 w would drop the
"an audit's currency is unimpeachability, and it is not spent on its own largest
number" close, which is the sentence a skeptical reviewer will quote back
approvingly. Numbers involved (38.3×, n=1,319, −0.30 pp, K/J transitions) appear
nowhere else in the main text, so any cut is deletion, not relocation.

### C2. The three "What this section does and does not support/establish" blocks — ~280 w combined

**Do not cut.** `audit.tex` L325+L332 (127 w), `atlas.tex` L294 (79 w), and
certification's equivalent. These are a deliberate repeated device and the
clearest epistemic-hygiene signal in the paper. They are also the cheapest
possible defence against a reviewer over-reading a result.

### C3. `audit.tex` §"Two robustness notes" — 212 w

**Do not cut further.** Already merged from two paragraphs in `eaf4962`, and
that merge deliberately kept the two distinct "1 of 12" facts in separate
sentences to prevent conflation. Further compression re-opens exactly the
failure the first pass avoided.

---

## Totals, and the honest answer on 16% vs 23%

| Tier | Saving | Cumulative main-text reduction from pre-trim |
|---|---|---|
| Already banked (`eaf4962`) | — | **15.8%** |
| + Tier A (A1+A2+A3) | ~455 w | **~19.1%** |
| + Tier B (B1+B2+B3) | ~120 w | **~20.0%** |
| + Tier C | ~717 w | ~25.2% |

**Tier A + Tier B lands at ~20%, not 23%.** Reaching 23% requires taking
roughly 350 w out of Tier C — that is, cutting the R04 self-incrimination
passage, the does/does-not blocks, or the robustness notes.

That is the substantive answer to why the first pass stopped at 16%: the
remaining compressible mass in these three sections is small, and past ~20% the
only material left is the material that makes the paper credible rather than
merely shorter. If the venue is TMLR (no page limit), Tier A alone is the
defensible stopping point and even that is optional.

## Method note

Word counts: comments stripped, `\input`/`\label`/`\bibliography*` removed,
remaining LaTeX control sequences and `{}$&\` stripped, whitespace-split. This
undercounts nothing and overcounts table cell contents slightly, which is why
table-heavy sections read a little high.
