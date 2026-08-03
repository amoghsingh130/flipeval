# Session handoff, 2026-08-03

Read this first. It covers the audit self-recheck, one finding that is escalated
and deliberately unapplied, a strategic decision about what the paper leads with,
and one thing that is currently wrong and public.

**This session ran alongside a second agent session in the same worktree.** Of
the 14 commits since `546a1f6`, only **two are this session's**: `53bcf5f` and
`a216cf7`. Everything else belongs to the concurrent session. Run `git log`
before assuming HEAD is yours, and see §5.

Companion documents:

- `docs/AUDIT_SELF_RECHECK_2026-08-02.md`, the worksheet this session produced.
- `docs/SESSION_HANDOFF_2026-08-02.md`, the previous state.
- `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md`, the full-text review this
  extends.

---

## 1. What this session was asked to do

Finish the self-recheck worksheet left unstarted at §4 of the 2026-08-02
handoff: verify R01, R10, R09 and R17 against the archived sources using
character-window matching, with a negative control for every search method, and
record exact locations.

The gap being closed: the 2026-07-31 review verified quote **accuracy** for all
17 sources but quote **location** for R10 only, which is how R10's defect was
found. The other 16 carried a bare `meets §3.1 inclusion` with no recorded
location, so the same defect class was unruled-out.

## 2. What landed

| Commit | What |
|---|---|
| `53bcf5f` | The worksheet, plus `\subsection{Where the claim is written}` in `paper/sections/audit.tex` |
| `a216cf7` | READING_COPY regen |

Gates at `a216cf7`: paper structural check **OK**, 25 tabulars, columns
consistent, 0 dangling refs, anonymous build clean. Neither touched path is in
the source fingerprint, so no freeze refresh applies and no in-image suite was
required. **Not pushed**, per the standing 2026-08-02 decision.

### The method, because a negative result was the point

`grep` is line-based and these sources are single-line HTML and Markdown blobs,
so a line-oriented search silently returns nothing on a string that is present.
A whole-file character-window matcher was used instead, with four normalizers
(`literal`, `whitespace`, `markdown_links`, `html_text`) and a `splice` matcher
for ellipsis quotes that requires fragments to be found **in order**.

Every method carried three controls, and no result was reported unless all three
passed: a **positive** (a span from the file must be found), a **mutation
negative** (the same span with one character changed must not be), and a
**differential** (a span crossing markup must be found by the normalizer and
MISSED by `literal`).

The differential is the one that earned its keep. R10's first probe was also
matched by `literal`, because that text occurs unlinked elsewhere in the file,
so it never exercised link handling. That is **inconclusive, not passing**, and
it was replaced rather than accepted. `--limit 250` in R13 is the live
demonstration of the whole apparatus: absent under a literal search because tags
break it, present under `html_text`.

The matcher itself is **not committed**. It sits in a scratchpad. Committing it
to `scripts/` would put it in a fingerprinted tree and require the in-image gate
plus a freeze refresh. It is a natural companion to
`scripts/fetch_audit_sources.py` for deliverable (D). Ask before doing it.

### Findings

- **R01** verbatim in the abstract, chars 4625-4694, inside
  `<div class="ltx_abstract">`. Prose. The claim carrying the surviving power
  flag holds.
- **R09** accurate, but found only after resolving a Markdown link. Prose.
- **R10** defect reproduced independently: the recorded sentence appears
  nowhere, and `98.6%` is two table cells under a `<th>Recovery` header. **No
  `<caption>` exists in any of the three cards.** Also confirmed the source's own
  arithmetic error: the Average recovery cell is a copy of the MMLU row
  (72.69/73.16 = 99.36%, printed as 98.6%).
- **R17** is an ellipsis splice of real prose. The card contradicts itself on the
  **sign**, and its own recovery cell settles it against the prose:
  68.54/68.69 = 99.78% matches the printed 99.8%, while the reverse would print
  100.2%. Magnitude is 0.15 pp either way so nothing computed moves.
- **All five non-assessability decisions confirmed** against the sources. R04's
  quote is in the **Table 5 caption** and that table is COCO CIDEr, which
  validates both its eligibility and its `metric-incompatible` kind.

## 3. The escalated finding, NOT applied

**R09 and R17 carry no §3.1 trigger vocabulary in prose at all.** Their
qualifying recovery figures exist only as table cells, which is exactly the
structural position that excluded R10. R08, R15 and R16 are unaffected: each
states "X% recovery" in prose with X >= 98.

Excluding R09 and R17 would move eligible 16 to 14 and assessable 11 to 9,
leaving K at 1, and would move K/assessable from 9.1% to 11.1%. **That is the
direction favourable to this paper's thesis**, and Amendment 2 specifically
certified that R10's correction was not. Amendment 2's scope clause also reopens
§3.1 only "to apply the existing inclusion rule to R10".

So it needs a dated amendment from Amogh either way, including a decision to
leave them in. **It is escalated, not taken.**

**The paper no longer depends on the answer.** Rather than move a denominator,
`sec:audit:locus` reports the pattern: across six cards from one publisher with
the evidence held constant, three assert recovery in prose, two juxtapose two
scores and characterise neither, one says nothing comparative at all.
Auditability therefore tracks documentation style rather than evidence quality,
a prose-keyed inclusion rule undercounts non-randomly, and 17 is a floor rather
than a census. That is a selection effect in this audit's own method, reported as
a finding. It costs no denominator, needs no amendment, and states openly that
the two boundary cases were kept and why.

## 4. Strategic decision: what the paper leads with

Amogh is targeting **J2C certification at TMLR**. Checked rather than recalled:
J2C is awarded on "strong support from the Action Editor and reviewers", is
expected to go to about **10% of accepted papers**, has no published rubric, and
requires the work not be an extension of a prior conference publication by the
same authors.

**The paper should not rest on the K count.** After Amendment 2 the quantitative
headline is one flagged claim out of eleven, and the paper itself reports that
the one does not survive sensitivity. A reviewer asking TMLR's first question
will read that as close to null. The durable contribution is the
reporting-standards result: no source declares a margin, almost none releases
per-item outputs, and whether a claim is auditable at all depends on where it was
written. That argument survives the headline collapsing. The count does not.

Checklist item 10, the J2C-facing validation case, is now mostly written.
`sec:audit:locus` is its spine. Build on it rather than starting fresh.

## 5. Concurrent-session hazards observed

Twelve of the fourteen commits since `546a1f6` are another session's. Two things
were observed mid-flight and left alone deliberately:

1. **`freeze_prepace.py --verify` was failing** during this session, reporting
   `README.md`, `scripts/freeze_prepace.py` and three unrecorded `tests/` files.
   That session had hardened the fingerprint to catch **added** files, not only
   changed ones (`667a251`), and its own new tests then tripped it before the
   freeze was refreshed. Not this session's to fix.
2. **The in-image expected count moved 207 to 297** (`16389cb`, and `377a686`
   found `AGENTS.md` stale at 201). If you are about to cite the gate, re-read
   `CLAUDE.md` rather than trusting any count quoted in an older document,
   including this one.

`paper/sections/audit.tex` was edited by both sessions. It merged cleanly, and
that was **verified rather than assumed**: the diff against their latest commit
was +100 insertions and 0 deletions, which proves their macro wiring survived
underneath. Do that check rather than trusting the file looks right.

## 6. Open items

### Needs Amogh

- **The R09/R17 amendment**, §3 above. No longer blocking, still unresolved.
- **The blog correction**, §7 below. Offered, not commissioned.
- **A machine with LaTeX.** Unchanged from 2026-08-02 and still blocking every
  §12 gate. The new `tab:audit-locus` has never been typeset.

### Agent work

1. **Macro-ise the tier counts.** `sec:audit:locus` hand-types 3, 2, 1 and the
   six-card denominator, against the rule that no section types a count by hand.
   They belong in `paper/tools/gen_denominator_macros.py`, which was another
   session's active file at the time. A comment in `audit.tex` says so. Do not
   add a second generator.
2. **The two missing tests** from the previous handoff, if the concurrent session
   has not already landed them (check `4e47b44`, which added the atlas-revision
   golden test).
3. **Option A's paperwork**, still open from 2026-08-02 §6.

## 7. Currently wrong and public

`paper/blog/2026-07-21-identical-scores-different-answers.md` is published and
still asserts **"4 of the 12"**, **"5 of the 17"**, **"0 of the 17"**, the
**`2.0x-12.9x` shortfall range**, and **"the margin they assert"**. All five were
withdrawn by Amendment 2.

The stale-claim linter catches every one: of its 18 live failures, **7 are this
blog post** and the other 11 are `paper/OUTLINE.md`, which is planning material
that never reaches the PDF. The linter has been failing on these since it landed
at `7a62b27`; it is correct to, and neither group is this session's doing.

**This is the only place a withdrawn number is currently public.** It is the
highest-priority open item for that reason, ahead of anything in §6.
