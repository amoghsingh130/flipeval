# Paper Revision Handoff — 2026-07-31

State of the paper revision after external advisor review. Written for whoever
picks this up next, human or agent. Supersedes nothing; adds to the record.

**Plan: arXiv preprint first, then TMLR.** TMLR is double-blind AND explicitly
permits an arXiv preprint of a submission (JMLR editorial policies, read
2026-07-31). One source, two builds, differing only by a flag.

---

## 1. The blocking item — read this before touching the audit

**The audit's "claim's own margin" is, for most claims, the largest delta the
source REPORTED, not a margin the source DECLARED.**

Evidence, all verifiable without running anything:

- `docs/audit_claim_table.csv` (FROZEN, commit `715a7ce`) has **18 columns and
  no margin field**. Registered §3.2 extraction fields do not include a margin.
- `claimed_margin_pp` / `margin_basis` originate in `scripts/audit_verdicts.py`,
  written after the freeze.
- Every `margin_basis` in `results/audit_verdicts_rev2.csv` cites an observed
  quantity: R01 "max |delta| over the 5 OPT-175B tasks", R06 "the larger of the
  two stated deltas", R09 "the largest per-task delta on the card", R17
  "+0.15pp (68.69 vs 68.54)".
- Frozen §4 V2: "the n required for TOST at margin 2 pp … (and at the claim's
  own margin **when it states one**)."

**Why this framing matters:** correcting it is **not** an amendment to a frozen
rule. It corrects an unregistered post-freeze implementation back toward the
registration's own words. That is a far better sentence in a response letter
than "we changed our protocol after seeing results." Do not lose this framing.

**Status:** blocked on Amogh's dated amendment. Draft prepared for signature at
`docs/AUDIT_AMENDMENT2_DRAFT_2026-07-31.md` (UNSIGNED; the frozen file is
untouched). Nothing recomputed. **The impact on K has deliberately NOT been
computed** — computing it before the amendment is signed would undercut the
amendment's own decision context.

**Two paper sites still carry the bad reasoning**, marked with LaTeX comments
for the recompute pass:
- `paper/sections/preregistration.tex`
- `paper/sections/appendix_prereg_detail.tex`

Both say "a source asserting parity within 0.15 pp has made a 0.15 pp claim".
R17's 0.15 is the observed delta.

**Downstream of the margin, so all of it moves with K:** V1
MDD-to-claimed-margin ratios, the required-n-to-reported-n shortfall range
(currently "2.0x to 12.9x"), and the §5 margin-sensitivity flag (R01).

**Untouched by it:** J = 5 indeterminate, **V3 = 0 of 17** (no margin involved —
the paper's own "most actionable" finding), the discordance imputation, the
atlas, all of H3.

---

## 2. Done and committed

| Commit | What |
|---|---|
| `260c66b` | Registrations appendix (reproduced, word-checked); `\ifanon` arXiv/TMLR switch |
| `6589d89` | Advisor items 1.2, 1.3, 2.x, 3.1–3.7, 5, 1.8 |
| `b561f06` | READING_COPY regenerated |

**1.3 — TOST confidence level.** Five sites said "95% confidence" while the
formula uses one-sided α = .05 (a 90% two-sided interval). `certification.tex`
contradicted itself — the prose under the formula already said z is one-sided.
No computed value changed.

**1.2 — the δ = 0 design assumption is now stated.** It was in
`scripts/audit_stats.py` and nowhere in the paper. Every reported n_req is now
labelled a lower bound, with the m − |δ| point made explicitly.

**2.x — AI use was disclosed NOWHERE in the rendered paper.** Verified by grep
over every section. The body said only "extracted twice by mutually blind
passes"; the sole disclosure was inside the *reproduced* Amendment 1 in the
appendix. New `paper/sections/appendix_extraction.tex`.

Two decisions in that appendix that must not be quietly reversed:

- **It lists what was NOT recorded** — exact model ID, system/extraction
  prompts, temperature/seed/reasoning settings, retry policy, whether prompts
  varied by source — as gaps. **Do not reconstruct plausible values later.** An
  invented spec sheet cannot be checked and misrepresents the provenance the
  audit rests on. The honest framing, already in the text, is "auditable but not
  re-executable".
- **No agreement rate is reported for the free-text numeric fields.** String
  equality gives 11%, which misdescribes the record: the passes recorded
  different *scope* by design (pass 1 every task in the source table, pass 2 the
  anchor task of the quoted sentence — GPTQ is five tasks vs PIQA alone, the
  same numbers at different granularity). What IS reported: 11 sources extracted
  by both passes, both categorical registered fields agreeing 11/11, and the
  reconciliation memo's merge-time finding that every numeric disagreement was
  scope not value. Also disclosed: no human validation subset exists.

**Prose pass.** Introduction rewritten (11,142 → 8,217 chars; all eight
`\paragraph` labels removed; map reduced to one sentence). Abstract rewritten
(1,715 chars / 256 words, zero boldface; **arXiv margin 8 → 205 characters**).
15 section titles neutralised. 4 self-vindicating passages replaced. 11 bolded
assertion-headings unbolded, 8 bolded prose counts de-emphasised. Causal wording
1.8 fixed in abstract and introduction. Field-wide claims scoped to the
registered frames.

**3.2 is partial by choice.** "rather than" appears 77 times; most are
substantive methodological contrasts whose removal costs precision. The four
constructions the review named by example are fixed. Do not run a blanket
regex over the rest.

---

## 3. Still open

**Needs the signed amendment first:** 1.1 margin categories (and every
downstream number), 1.5 imputation uncertainty, 1.6 cell dependence /
cluster bootstrap.

**New work, not corrections:** 1.4 simulation validation of the normal
approximation; 1.2's δ-parameterised required-n table (0, 0.25m, 0.5m, 0.75m);
item 6's figures.

**Verify before restructuring:** 1.7 assumes 5.3× and 12.7× are ratio-of-medians.
Confirm which the paper already reports — the fix may be smaller than the review
implies.

**Judgement calls, no right answer:** item 4 restructure to 22–28 main-text
pages; whether to cut the harness study to an appendix; item 9 title (advisor
prefers "Auditing Equivalence Claims for Compressed Language Models").

**Practical, decide with the amendment:** the v1.0.0 Zenodo artifact
(`10.5281/zenodo.21708923`) is public with the current verdicts. Once the paper
reports revised numbers, paper and citable artifact disagree. Either cut v1.1
and cite the new version DOI, or add an explicit mapping note in the artifacts
section.

---

## 4. Formatting and the page count

The 78-page PDF was built with plain `article` at 11pt. **TMLR mandates
`tmlr.sty`** (https://github.com/JmlrOrg/tmlr-style-file): single-column,
6.5in × 9in text block — roughly **55% more text per page**, so expect ~50
pages on the same content. Swap the style in and re-measure **before** deciding
what to cut.

TMLR's length warning excludes appendices: *"papers that are unusually long
(not counting any Appendices) are likely to result in reviewing delays."*
Appendices are ~40% of this document (body 114,946 chars vs appendices 75,843).
**Judge the body only.**

Style-file options map onto the two builds: `\usepackage[preprint]{tmlr}` for
arXiv (named), `\usepackage{tmlr}` bare for the TMLR submission (anonymous).
`tmlr.sty` anonymises the author block only — it knows nothing about the URLs,
DOIs, or the author name inside the reproduced registrations, so `\ifanon` is
still required.

---

## 5. The anonymity switch

`paper/main.tex` carries `\newif\ifanon`; `\anonfalse` is arXiv. **Eight**
de-anonymising sites are routed through macros defined beside the switch:
repo URL and dataset mirror (in both `artifacts.tex` and the appendix table),
both Zenodo DOIs, `\authorname` (the reproduced registrations name the decision
owner twice), and `\harnessissue` (the lm-eval-harness issue number leaks the
GitHub handle via its comment).

**Any new URL, DOI, handle or acknowledgement written directly into a section
silently breaks the blind build.** Route it through a macro.
`paper/tools/check_paper.py` fails if an identifier renders outside `main.tex` —
that check is the only thing standing between a pasted link and a
de-anonymised submission.

---

## 6. Tooling and gates

`paper/tools/` (committed 2026-07-31; deliberately NOT `scripts/`, which is
fingerprinted and would trigger the in-image gate for code that touches nothing
cluster-side):

| Tool | Purpose |
|---|---|
| `gen_registrations.py` | Regenerate the registrations appendix from the frozen docs |
| `verify_registrations.py` | Word-for-word check vs the frozen docs (currently 3,959 words) |
| `check_paper.py` | Refs, cites, environments, and the anonymous-build leak check |
| `gen_reading_copy.py` | Regenerate `READING_COPY.md` — run AFTER committing content |

**Negative-control any checker before believing a finding.** This has now caught
four checker bugs that each looked like a document defect: a column-spec regex
truncating at the first `}`, a one-level `\input` walk, a parking-token
collision corrupting quoted digits, and a heading "1." eaten as a list marker.

Current state: 22 files, 99 labels, 0 dangling refs, 23/23 cite keys,
environments balanced, anonymous build clean. Paper and docs are outside the
source-state fingerprint, so no freeze refresh is needed for these changes;
`freeze_prepace.py --verify` passes unchanged. All six frozen files are
byte-identical.

---

## 7. Recommended order

1. Amogh reviews, edits and signs `AUDIT_AMENDMENT2_DRAFT_2026-07-31.md`;
   appends Part 1 only to the frozen registration.
2. Recompute the audit **once**; carry every downstream number, table and
   sentence, including the two marked sites in §1 above.
3. Decide the artifact-version question.
4. Swap in `tmlr.sty`, re-measure the page count, then decide on item 4.
5. Remaining new work: 1.4, 1.5, 1.6, figures.
6. Production pass (item 7): PDF metadata is currently empty, `Draft \today` on
   the title page, overfull boxes, URL/DOI check.
7. Build both packages and run the identifier sweep over the final PDF and ZIP.
