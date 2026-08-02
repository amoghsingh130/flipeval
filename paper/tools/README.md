# Paper tooling

Run from the repository root. Python 3.9 on the login node is enough: these use
only the standard library, deliberately, so they run where the pinned image is
not available.

These live under `paper/` rather than `scripts/` on purpose. `scripts/` is a
fingerprinted tree (`scripts/freeze_prepace.py`), so a change there triggers the
in-image pytest gate and a freeze refresh; these touch no cluster-side code and
are not part of the analysis pipeline. Earlier table generators were left in
session scratchpads and lost, which is why these are committed.

| tool | what it does |
|---|---|
| `gen_registrations.py` | Regenerates `sections/appendix_registrations.tex` from the four FROZEN registration documents. Read-only against them. |
| `verify_registrations.py` | Proves that appendix reproduces the frozen text word-for-word, by diffing word streams. Exits non-zero on any mismatch. |
| `check_paper.py` | Two checks. **Structural:** stand-in for a LaTeX build (recursive `\input` expansion, then labels, refs, cite keys, tabular columns, environment balance, anonymous-build leak). **Stale-claim linter:** forbidden rev-2 counts, retired wording and superseded artifact pointers, over the whole tree. |
| `gen_reading_copy.py` | Regenerates `READING_COPY.md`. Run it *after* committing content, so the recorded commit is the state it reflects. |
| `gen_denominator_macros.py` | Regenerates `paper/audit_denominators.tex`, the single ledger of every repeated rev-3 audit count, from the sealed `results/audit_verdicts_rev3.csv`. `--check` validates the input digest, the canonical invariants and the committed ledger. |

Order after editing paper content:

```bash
python3 paper/tools/gen_registrations.py     # only if a frozen doc gained an amendment
python3 paper/tools/verify_registrations.py
python3 paper/tools/check_paper.py
git commit ...
python3 paper/tools/gen_reading_copy.py
git commit paper/READING_COPY.md ...
```

## The stale-claim and stale-pointer linter

Section 6 of `docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md`. Both checks run by
default; `--stale-only` and `--structure-only` select one. Exit code is `1` for
a structural failure, `2` for a stale-claim failure, `3` for both, so a caller
can tell them apart.

Scope is the whole tree, not the `\input` graph: LaTeX, Markdown, CSV, JSON,
scripts, tests, notebooks, configs, READMEs and `% SOURCE:` comments. A
withdrawn count sits just as happily in a script docstring as in a section.
`results/` is excluded because it holds generated and sealed outputs, which are
regenerated rather than edited.

**Two severities.** `stale` is asserted wrong and fails the run. `review` is
flagged for a human and does not: `underpowered` is still the right word in
background and related-work discussion, and the linter is not entitled to
decide which use is which.

**Every hit is printed**, including exempt ones, with the reason that exempted
it. An exemption that has grown too broad is therefore visible in the output
rather than invisible in the code.

**Each hit carries a context class**, because a bare token match cannot tell a
manuscript defect from a historical note from a generated echo:

| context | meaning |
|---|---|
| `prose` | renders in the PDF |
| `provenance-comment` | a `% SOURCE:`/`Population:` comment. Never renders, and can cite a superseded artifact as the source for a number the prose below it already corrected. `sections/atlas.tex:102` is exactly that, and it is the one the 2026-07-26 correction pass in the same file missed |
| `comment` | any other comment |
| `code`, `not-compiled`, `planning-not-compiled`, `dated-post`, `generated-echo`, `dated-record` | does not reach the PDF; the right response differs for each |

**Exemptions**, narrowest first:

1. *By construct, comments.* A comment run that states the withdrawal or the
   rev-1 correction ("WITHDRAWN, NOT RECOMPUTED", "REV-2 CORRECTION 2026-07-26",
   "SEVENTH rev-1 survivor"). The withdrawal commit left such a comment at every
   former shortfall site on purpose, so those comments legitimately hold the
   withdrawn numbers. This is per-comment, not per-file: a stale claim added to
   the same file later is still caught.
2. *By construct, prose.* A sentence that states the withdrawal, and a
   supersession mapping (`1{,}254 to 1{,}807`, `2{,}123 $\to$ 2{,}164`).
3. *By construct, quotation.* Retired wording inside `` `` '' `` is quoted, not
   asserted. Wording rules only: quoting a dead file path does not revive it.
4. *By path, allowlisted with a written reason.* `appendix_registrations.tex`
   (verbatim machine-checked reproduction of frozen documents), the frozen
   documents themselves, and this linter plus its tests, which state every
   forbidden token as a literal.
5. *Downgraded to `review`, never hidden.* `docs/` is a dated append-only record
   archive; `READING_COPY.md` is generated.

### Validation

Negative-controlled before it was believed, as required after five checker bugs
on this project that each first looked like a document defect.

- `tests/test_check_paper_stale.py`, 33 tests. Every rule has a literal sample
  and must fire on it; clean text and the checklist's canonical rev-3 results
  block must produce silence; `10 of 16` must never read as `5 of 17`;
  `atlas_cells_summary_rev2.csv` must never read as the rev-1 file it is a
  prefix of; a token planted 4 kB into a single-line blob must still be found.
- Mutation-tested: thirteen deliberate breakages of the linter were introduced
  one at a time and the suite caught every one that was not a no-op, including
  dropping the U+00D7 and `\times` spellings, dropping the LaTeX `1{,}155`
  spelling, making the matcher line-oriented, turning an allowlist into a
  blanket file skip, widening `5 of 17` until it flagged the new `10 of 16`,
  making the withdrawal marker match everything, and collapsing the scan scope.
- CLI-level: a token planted in `sections/limitations.tex` is found and exits
  `2`; a new file of clean canonical text adds a scanned file and zero hits.

## The anonymous build

`paper/main.tex` carries `\newif\ifanon`. `\anonfalse` is the arXiv preprint;
`\anontrue` is the TMLR submission. Every de-anonymising item is routed through
a macro defined next to the switch. `check_paper.py` fails if an identifier
appears in rendered text anywhere outside `main.tex`, which is the only thing
that stops a raw URL pasted into a section from silently breaking the blind
build.

## Validation these tools were given

- `verify_registrations.py` was negative-controlled: it detects a changed
  number, a changed word ending, and a deleted `\item`.
- `check_paper.py`'s leak check was negative-controlled with a planted name.
- `gen_denominator_macros.py --check` was negative-controlled on each of its
  three layers separately: a tampered committed ledger, a tampered canonical
  literal, and a tampered recorded digest each fail alone, with the other two
  still reporting OK. Its counts are additionally re-derived from the CSV by
  `tests/test_audit_denominators.py`, which is the fingerprinted gate.
- `gen_reading_copy.py` was validated by regenerating `READING_COPY.md` at
  `b4b2d99` in a detached worktree and diffing against the committed file:
  **zero content lines differ**. The only differences are whitespace, and they
  are intentional — the previous generator separated index-table rows with
  blank lines, which terminates the markdown table after its header.
