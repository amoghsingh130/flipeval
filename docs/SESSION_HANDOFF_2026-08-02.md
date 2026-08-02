# Session handoff — 2026-08-02

Read this first. It covers the rev-3 carry work, four decisions Amogh made, one
hard blocker, and the traps found along the way.

Companion documents:

- `docs/PAPER_REV3_CARRY_CHECKLIST_2026-07-31.md` — the numbers reference.
  **Superseded as a plan** by a revised 12-section checklist Amogh gave in chat
  on 2026-08-01. That revision was never committed; ask him for it.
- `docs/PAPER_REVISION_HANDOFF_2026-07-31.md` — the advisor-review state.
- `docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md` — the full-text source review.

---

## 1. Decisions Amogh made this session

| # | Decision | Verbatim / date |
|---|---|---|
| 1 | **No em dashes**, in the paper and in chat prose | "i don't like em dashes, get rid of them", 2026-08-01 |
| 2 | **Option A** for redistributing the 17 audit sources | 2026-08-02 |
| 3 | **Do not push.** The branch stays local | "don't push then", 2026-08-02 |
| 4 | **C + D** for the second-human gap, scoped to **4 load-bearing items** | 2026-08-02 |

Decision 4 in full: Amogh has **no second human and will not get one**. He chose
(C) to self-recheck, disclosed as *author re-verification* rather than
independent verification, plus (D) ship exact quotes with locations and the
retrieval script so readers can check for themselves. Scope is **R01, R10, R09,
R17**, not all 17.

**Nothing in C or D licenses an independence claim.** The paper must never
describe two automated passes, or an author recheck, as inter-rater
verification.

---

## 2. What landed

All gates clean. Two in-image runs, both **207 passed, 0 skipped**
(jobs `11621633`, `11622232`). `freeze_prepace.py --verify` passes.
**34 commits ahead of `origin`, deliberately unpushed.**

| Commit | What |
|---|---|
| `9189aab` | Carry checklist item 2: `sections/audit.tex` to rev-3 |
| `a205c31` | READING_COPY regen |
| `1137964` | Item 3: shortfall range withdrawn; both bad-reasoning sites removed; 137 em dashes cleared; registrations appendix resynced |
| `c6c937e` | READING_COPY regen |
| `2b2ff4a` | Item 6: audit appendix tables regenerated from rev-3; §0.2 disclosed |
| `896431b` | READING_COPY regen |
| `b3fdfde` | Two imputation comments corrected in `scripts/` |
| `0549e1f` | Freeze refresh |
| `5adf2fb` | `scripts/fetch_audit_sources.py` |
| `2e9c411` | Freeze refresh |

### Substance

- **`tab:audit-underpowered` is gone, label included.** All four of its rows
  were flagged at their own reported deltas and are robustly above threshold at
  2 pp. Replaced by `tab:audit-sensitivity` (10 above throughout / 1 changes
  within / 0 below throughout). A one-row R01 successor was **considered and
  rejected**: a table built around the single flag looks constructed to produce
  it.
- **The `2.0x-12.9x` shortfall range is WITHDRAWN, never recomputed.** It
  divided by margins no source declared. Ten of eleven claims have no shortfall
  at 2 pp, so there is no range. Comments at every former site say so, because
  the natural repair is to reach for new numbers.
- **Both "0.15 pp parity = 0.15 pp claim" sites are dead**
  (`preregistration.tex`, `appendix_prereg_detail.tex`), plus a third
  restatement in `appendix_audit_table.tex`. Each now quotes the sentence as the
  reasoning that was found wrong.
- **New generator `paper/tools/gen_audit_tables.py`.** `--check` regenerates the
  trusted `tab:audit-identity` and diffs it against the committed table before
  the generator is used on anything else.
- **§0.2 disclosed, not repaired.** R06/R07 match 183 cells that are all 4-bit
  *quantization*, on `bits=None` being absent from `_METHOD_PROFILE` rather than
  on method similarity. Registered rule, results inspected, so it is disclosed
  as the weakest imputation in the table.

---

## 3. 🔴 The blocker: the source-tarball rewrite

**Do not attempt this without a signed amendment.**

`docs/audit_sources_20260731.tar.gz` enters at `cc357db` and was never deleted,
so **all 21 commits from there to HEAD carry the blob in their trees**. Removing
it rewrites all of them.

**`bb45528` is inside that range and is cited in the FROZEN, SIGNED Amendment 2**
at `docs/AUDIT_REGISTRATION_2026-07-15.md:228`. The rewrite would make a
signature's provenance chain point at a nonexistent commit, and only Amogh may
append a dated amendment.

There is no workaround. `bb45528`'s own tree contains the tarball, so it cannot
be published intact either. An archive tag preserves the hash only if unpushed,
which defeats the purpose.

**Amogh's resolution: don't push.** This costs nothing — no current work needs
pushing — and touches no frozen content.

Safe and unaffected: `19d485c`, and **`v1.0.0` / `987377a` is an ANCESTOR of
`cc357db`**, so the release tag and its Zenodo archive are outside the rewrite
entirely.

### Prep already done, all reversible

- Private sealed copy at
  `/storage/project/ps-compressedlm-0/asingh3206/private/audit_sources_20260731/`
  — verified `a912a1e7…40259`, 17 sources, `0444` on the directory and files.
  **Not in `~/scratch`**, which is purged at 60 days.
- Local tag `pre-source-tarball-removal-20260802` at `0549e1f`.
  **NEVER PUSH IT** — its history contains the blob.
- The `.sha256` records the path `docs/audit_sources_20260731.tar.gz`, so
  `sha256sum -c` works only from the repo root.

---

## 4. 🟡 Unfinished: the self-recheck worksheet

Started, **not delivered**. It should give Amogh, for each of R01, R10, R09 and
R17: the exact recorded quote, the archived file, where the string actually
occurs, and whether that location is prose, a table caption, or a bare table
cell (the §3.1 requirement).

**The gap it addresses.** The 2026-07-31 review verified quote *accuracy* for
all 17 but verified quote *location* for **R10 only** — which is exactly how
R10's defect was found. The other 16 carry a bare `meets §3.1 inclusion` with no
recorded location, so the same defect is unruled-out. R09 and R17 are the
priority: their quotes are score reports ("achieves an average score of 73.44"),
not equivalence assertions.

**Known trap for whoever finishes it:** `grep` is line-based and these sources
are single-line HTML and Markdown blobs, so `grep -o '.\{140\}…'` silently
returns nothing. Use a Python matcher over the whole file with a character
window, and confirm it finds a string you know is present before trusting a
negative.

Extract the sources from the private copy; do not re-fetch for this.

---

## 5. Traps and mechanisms found this session

**Three silent gates, all the same shape as a stale expected test count.**

1. `paper/tools/check_paper.py`'s docstring promised a **tabular column check
   that was never implemented** — it existed in the scratchpad script the tool
   was assembled from and was lost in the move. Now implemented, brace-aware and
   multicolumn-aware, reporting `24 tabulars (227 rows)`.
2. `paper/tools/verify_registrations.py` **had been exiting 1 since `ab279b2`
   and nobody was reading it.** `appendix_registrations.tex` was generated at
   `260c66b`, before Amendment 2 was appended, so the paper was reproducing a
   **superseded version of a frozen document** while claiming a verbatim
   machine-checked reproduction. Regenerated, 3,959 → 5,206 words.
3. `gen_registrations.py` failed closed on U+2026 — Amendment 2 is the first
   frozen text with an ellipsis. Added to **both** maps: a codepoint the
   generator maps and the verifier does not gives a false MISMATCH on a correct
   appendix, which misleads exactly as much as a missed real one.

**`CLAIM_PROFILES[...].notes` is DATA, not a comment.** It is emitted verbatim
into the output CSV, and R06's string is byte-identical in the **sealed,
paper-cited** `results/audit_verdicts_rev3.csv`. R06's note is factually wrong
(says imputation descends to the global tier, which is rev-1 behaviour, the
eighth rev-1 survivor and the first found in a comment). It is **deliberately
left wrong**, with a comment saying why: correcting it would mean HEAD no longer
reproduces a released artifact, to fix a field nothing reads. The correction is
published in the audit appendix instead.

**Validate a generator against a table you already trust.** `gen_audit_tables.py
--check` failed on its first run and was right to: it was not converting
straight quotes to LaTeX directional quotes, which four source names need. That
failure happened *before* it touched the two tables that were actually wrong.

**Negative-control every checker before believing it.** Done for all three
checkers this session. That is now five checker bugs caught this way across the
project, each of which first looked like a document defect.

**Em dashes: rewrite each site, never blind-replace.** 137 prose sites cleared
across 21 files. **Twelve `---` remain on purpose** — they are "no value" table
cells, which is table notation, not prose punctuation.
**`paper/sections/appendix_registrations.tex` is excluded permanently**: it
reproduces frozen documents verbatim and is machine-checked against them, so
"fixing" its dashes falsifies the reproduction and breaks the gate.

---

## 6. What is left

### Needs Amogh, not an agent

- **Finish the self-recheck** of R01/R10/R09/R17 once the worksheet exists.
- **A dated amendment**, if he ever wants the tarball removed and the branch
  pushed.
- **A machine with LaTeX.** Every §12 gate is blocked on this, not on drafting:
  render the PDF, inspect every page, scrub metadata, scan the anonymous build
  for identifiers. Phoenix has no TeX, and the new tables have never been
  typeset. `tmlr.sty` is single-column 6.5×9in and reflows everything.

### Agent work, in the order I would take it

1. **Denominator macros** generated from `results/audit_verdicts_rev3.csv`, with
   the arithmetic-identity tests (17−1=16, 11+5=16, 0+1+10=11, 0+3+13=16) and
   the structural invariant that an `assessable = false` row can never carry a
   threshold verdict. Do this **before** more prose edits, so no section types a
   count by hand.
2. **Stale-claim linter** in `check_paper.py` (forbidden tokens: `4 of 12`,
   `own margin`, `audit-underpowered`, `audit_verdicts_rev2`, `2.0x`, `12.9x`,
   `Stated margin`). Review every hit; some uses of "underpowered" remain
   correct in background discussion.
3. **Items 4 and 5 finish.** `conclusion.tex` and `limitations.tex` are only
   partly swept; the narrative-consistency pass across title, contributions,
   introduction roadmap and discussion is not done.
4. **The two missing tests** — golden (rev-1 → 1,936 vs rev-2 → 2,010) and the
   R14 trap (n=728 against a hypothetical 742, must stay out of K). These touch
   fingerprinted `tests/`, so they need the in-image gate, a freeze refresh, and
   **the expected count updated in CLAUDE.md in the same commit**.
5. **Option A's paperwork.** `sections/artifacts.tex` and the release notes
   still describe the tarball as a released artifact, and the licensing
   rationale is unwritten. This is also where (D) lands: exact quotes with
   locations, plus a pointer to `scripts/fetch_audit_sources.py`.

### Not started

Checklist items 8 (Zenodo v1.1.0), 9 (presentation and voice), 10 (the
J2C-facing validation case), 11 (separate arXiv and TMLR packages).

---

## 7. The retrieval script

`scripts/fetch_audit_sources.py`, stdlib only, python 3.9 compatible for the
login node. `--manifest`, `--claims`, `--out` are **all required, no defaults**,
per the same rule as `--atlas`/`--output` and the grid variables.

Retrieval is per-source and **not interchangeable**: ar5iv full-text HTML for
arXiv (the PDF, extracted text and `/abs` page all hash differently), raw
`README.md` **at a pinned HF commit** for the model cards,
`raw.githubusercontent` Markdown for R12, live page for R11/R13/R14.

Validated three ways on 2026-08-02: 17/17 VERIFIED offline against the archive;
negative control (one byte appended to R03) gives DRIFT and exit 1 while the
same byte on R11 is correctly EXPECTED-DRIFT and does not fail; and a **live
fetch of R08 and R17 reproduced their recorded hashes exactly**, which is the
actual evidence that Option A works.

Two limits it reports rather than hides. R11 serves per-response content, so its
recorded hash was never a valid fingerprint. R13's manifest status is
`NO-BASELINE`: a hash **is** recorded, so a re-fetch verifies against the
archived capture, but no pre-capture baseline exists, so the capture itself was
never independently corroborated. *The first draft of that docstring claimed R13
had no recorded hash at all; the offline run contradicted it and it was
corrected before commit.*
