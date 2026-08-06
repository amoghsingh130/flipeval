# Flagship revision handoff, 2026-08-05

**This file is the source of truth after context compaction. Do not reconstruct
decisions from the compacted conversation.** Every number below was re-verified
against the repository immediately before this file was written; where a
previously reported figure was stale, the verified value is used and the
discrepancy is noted.

---

## 1. Repository state

| | |
|---|---|
| worktree | `/storage/project/ps-compressedlm-0/asingh3206/flipeval/.claude/worktrees/flagship` |
| main checkout | `/storage/project/ps-compressedlm-0/asingh3206/flipeval` (also `~/ps-compressedlm-0/flipeval`) |
| branch | `flagship-narrative` |
| HEAD | `ed54d4d` (was `9612a12` when this file was written) |
| status | **clean**, 0 modified files |
| pushed? | **no.** Branch is local only. `origin` is a PUBLIC GitHub remote; nothing on this branch has been sent to it |

### Other branches to know about

- `wave4-partial-20260805` at `40b71ba` — partial output of four compression
  agents that died on a spend limit. **DO NOT MERGE AS IS**: three of them cut
  ~2,990 body words without creating appendix destinations. Preserved only so
  nothing is lost. Its `audit.tex` is a usable *map* (it kept every mandatory
  qualification and wrote references to six appendix labels it never created:
  `app:audit:indeterminate`, `app:audit:margins`, `app:audit:peritem`,
  `app:audit:protocol`, `app:audit:rules`, `app:audit:r04`, plus dangling
  `eq:tost-n` and `sec:audit:locus`).
- `wave2-frontback`, `wave2-body` — merged into this branch, removable.
- `worker-a` … `worker-e` — all landed on `main` already, removable.

### Commits created during the flagship revision, oldest first

```
695d33d Flagship narrative plan
764076f Flagship Figure 1: generated TikZ
751bbf5 Freeze refresh after the figure generator
2e6ee01 Session handoff: Wave 1
c4eb110 Abstract and introduction on one thesis
94aaabc Limitations as prose, conclusion returns to the same cell
b15df26 Integrate the front and back narrative rewrite
b7b8b1c Restructure the body around the thesis
a180b12 Integrate the main-body restructure
e3f4290 Session handoff: Waves 1 and 2
e436436 Wave 3 adversarial review
8d96b31 D8: S1 median churn correction
bf05691 Three Figure 1 geometry defects fixed
4092307 Freeze refresh
b148a4a Compress the narrative spine
097a7a0 Artifacts detail to appendix              <- relocation
18b2db1 Session handoff: Wave 4 lost to spend limit
3cf4526 First compile, real baseline recorded
b7d1144 Figure 1 placement + 10 visual defects + strata table
2134741 Freeze refresh
a7e63d2 D4 resolved as a definition question
7d50cf5 Harness-sensitivity detail to appendix    <- relocation
43b3fa7 Final measured state after fixes
d8ddb90 D4 closed: aggregation named, 5.3x retired
b55fe8f Layout: 58 overfull -> 18
9141d30 Freeze refresh after README D4 correction
2470d9c Measured page map
110e125 Extended related work to appendix         <- relocation
9612a12 Clear the body margins: 4 pages -> 1
86b2b52 Compaction handoff (this file)
48872d2 One rounding convention: 5.40 / 5.22 / 5.19, all unrounded   <- P1A
c63616b Churn-ratio generator + zero-denominator policy              <- P1B/1C
09045ca Freeze refresh
f0ab36c Layout triage: 16 overfull boxes -> 2                        <- P2
494eb57 Freeze refresh
ed54d4d Reporting standard stated in the introduction                <- P3
```

---

## 2. Binding constraints

### From `CLAUDE.md` / `AGENTS.md`

**`AGENTS.md` and `CLAUDE.md` are byte-identical** (226 lines each, verified by
`diff`). Reading either is sufficient; both exist at the repository root and in
this worktree.

- **Frozen files, never edit registered content**: `PREREGISTRATION.md`,
  `docs/MINIGRID_REGISTRATION_2026-07-15.md`,
  `docs/ATLAS_MINING_REGISTRATION_2026-07-15.md`,
  `docs/AUDIT_REGISTRATION_2026-07-15.md`, `docs/atlas_pair_manifest.json`,
  `docs/audit_claim_table.csv`. Changes happen only as dated amendments written
  by Amogh. `paper/sections/appendix_registrations.tex` is frozen verbatim and
  is verified at **7,103 words**.
- **Result-inspection discipline**: LIVE since 2026-07-22. Do not read accuracy
  from confirmatory cells outside the registered tools. (The confirmatory sets
  are complete and signed, so verifying already-published paper numbers against
  committed artifacts is permitted and is what this work does.)
- **Verification gates by change type**: Python/tests changes need the in-image
  pytest gate; shell changes need `bash -n` + `shellcheck`; doc-only changes
  need no test gate. Anything landing in a fingerprinted tree needs
  commit → freeze → commit.
- **Fingerprinted trees**: `configs`, `flipeval`, `pilot_eval`, `scripts`,
  `tests`, plus `INCLUDED_PATHS` in `scripts/freeze_prepace.py`. **`README.md`
  is inside the fingerprint** — this caught us once already. `paper/` and most
  of `docs/` are NOT fingerprinted.
- **No default grid for any job script**; **every `sbatch` option must precede
  the script path**; **scheduler flags are not in effect until independently
  observed**.
- No computation on login nodes; submit via `sbatch -A $ACCOUNT -q inferno`.

### Hard prohibitions for this work

- **No push. No PR. No upload** to arXiv, TMLR, Zenodo or Hugging Face.
- **No history rewrite.** No touching the source-tarball history.
- **No re-fetching audited sources.**
- **Option A is non-negotiable**: the release contains publish URLs, pinned
  identifiers, hashes, a manifest and a retrieval script. The **full-text
  captures remain PRIVATE and are never redistributed**. `artifacts.tex`
  contains the protected sentence that the audited sources' full-text captures
  are in no release. Never write or imply otherwise.
- **No claim of independent second-human verification.** The two extraction
  passes are automated and not statistically independent; the re-verification
  was by the author.
- **No em dashes in paper prose.** `---` inside a table cell meaning "no value"
  is table notation and stays. `appendix_registrations.tex` is exempt.
- Do not obtain a page target through smaller fonts, narrower margins,
  illegible tables or layout tricks.

---

## 3. Build environment

Full detail in `docs/PAPER_BUILD_ENVIRONMENT.md`. Summary:

```bash
export PATH=$HOME/scratch/texlive/bin/x86_64-linux:$PATH
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

| | |
|---|---|
| TeX Live | 2026, `scheme-small`, installed at `~/scratch/texlive` |
| engine | pdfTeX 3.141592653-2.6-1.40.29 |
| pgf/TikZ | 3.1.12 |
| latexmk | present but deliberately **not** used |

**This is not part of the pinned computational environment.** The Apptainer
image `~/scratch/flipeval/flipeval.sif` remains the only thing that runs
analysis code. Scratch is purged at 60 days, so the TeX install is disposable
and may need recreating from the recorded profile.

Two traps: `array` is a required package (the wide-table column specs depend on
it), and `arrows.meta` resolves through pgf's `pgflibraryarrows.meta.code.tex`
fallback because `scheme-small` ships no `tikzlibrary` variant.

Line-breaking settings in `main.tex`: `\emergencystretch` 3em globally, 6em
locally around the frozen registrations appendix. **These change no font, no
margin and no measure.** The local one exists because the frozen file cannot be
edited to add break points.

In-image gate:
```bash
PROJECT_DIR=<this worktree> SCRATCH_DIR=$HOME/scratch/flipeval \
  sbatch -A paceship-compressedlm -q inferno -p cpu-small --export=ALL \
  scripts/slurm/run_tests.sbatch
```

---

## 4. Measured state (verified at `ed54d4d`, clean build)

| quantity | first baseline | at `9612a12` | **now** |
|---|---|---|---|
| **Main content, before references** | 1-35 | 1-35 | **1-35** |
| **Total PDF** | 96 | 96 | **99** |
| Figure 1 page | 87 | 3 | **3** |
| Overfull hbox | 58 | 16 (worst 82.0pt) | **2** (worst 5.16pt) |
| Overfull vbox | 0 | 1 (2.69pt) | **0** |
| Underfull hbox | 11 | 34 | 34 |
| Undefined refs / cites | 0 / 0 | 0 / 0 | **0 / 0** |
| Body pages with ink past the text block | 4 | 1 | **0** |

The PDF grew from 96 to 99 in the appendix, not the body: +2 from splitting
`tab:audit-characterisation` into two panels (the fix for the widest box in the
document) and +1 from the introduction's reporting standard. The body boundary
has not moved.

**The 2.69pt overfull vbox the brief asked to inspect before accepting no longer
exists.** It was the same defect as Figure 1's 6.2pt hbox: one node overflowing
the output routine. `inner sep=0` cleared both.

### Section page map (verified at `ed54d4d`)

| # | section | starts | span |
|---|---|---|---|
| 1 | Introduction + Fig 1 | 2 | 3 |
| 2 | Related work | 5 | 2 |
| 3 | Paired certification | 7 | 5 |
| 4 | Atlas | 12 | 4 |
| 5 | **Audit** | **16** | **10** |
| 6 | Mini-grid | 26 | 6 |
| 7 | Harness sensitivity | 32 | 1 |
| 8 | Artifacts | 33 | 0 |
| 9 | Limitations | 33 | 2 |
| 10 | Conclusion | 35 | 1 |

**CORRECTION, repository over document.** There are **ten** body sections, not
eleven. `preregistration.tex` is three *subsections* inside §3 (Paired
certification), folded in by `b7b8b1c`; it has not been its own section since
that commit. Both `docs/PAGE_MAP_2026-08-05.md` and the first version of this
file listed it as section 4 with its own page span, which is why §3 looks
like it grew from 3 pages to 5. It did not. Trust this table.

**The audit is now 10 body pages of 35, not 9.** It is more than a quarter of
the body and remains by far the dominant compression target.

### Float placement (all `[!t]`; verify after any change to a float's height)

`fig:cancellation` p3 - `tab:certification` p9 - `tab:atlas-strata` p14 -
`tab:audit-taxonomy` p18 - `tab:audit-sensitivity` p23 - `tab:h3-eightcell` p28 -
`tab:churn-aggregations` p29 (new).

**Float placement is fragile.** Figure 1 originally sat on page 87, and making
three body tables taller once pushed them to pages 85-86. `[!t]` is what holds
them. Any new float must be `[!t]` from the start.

## 5. Gates currently passing (exact, at `ed54d4d`)

```
in-image pytest, job 11702653 : 348 passed, 0 skipped   (was 325; +23 new tests)
check_layout.py               : OK, 1 accepted violation with a recorded reason
PAPER_CHECK                   : OK, 0 dangling refs, 0 unresolved cites
                                24 files, 110 labels, 183 refs, 26 tabulars
STALE_CLAIM                   : OK
REGISTRATIONS_VERBATIM        : OK, 7,103 words across 4 documents
gen_denominator_macros --check: OK on all three layers
gen_audit_tables --check      : OK, 17 rows reproduce byte for byte
churn_ratio.py --check        : OK, 25 printed values reproduce
freeze_prepace --verify       : passed
ABSTRACT_CHARS                : 1879 / 1920, margin 41, 283 words
prose em dashes               : 0
```

**The expected in-image count in `CLAUDE.md` and `AGENTS.md` is now 348** and was
updated in the same commit that added the tests, as the rule requires. The two
files remain byte-identical.

### Two new gates this session

- **`paper/tools/check_layout.py`** - run after every build, from `paper/`. Two
  halves: overfull boxes from the log, and glyph `xMax` per page from
  `pdftotext -bbox`. **The log half alone is not sufficient**: a `tabular` wider
  than `\textwidth` inside `\centering` is set silently, which is how the whole
  S2 column of the strata table came to be rendering off the page with a clean
  log. Body pages must be completely clean; accepted violations are keyed to a
  string in the offending page's own text, never to a page number.
- **`scripts/churn_ratio.py --check`** - run after touching any churn-ratio
  figure. 25 values, both regimes, both aggregations.

## 6. Figure 1

| | |
|---|---|
| generator | `scripts/make_figure1.py` (**fingerprinted**; needs scipy, so a compute node) |
| output | `paper/figures/fig1_cancellation.tex` (generated TikZ, do not hand-edit) |
| provenance | `paper/figures/fig1_values.json`, one entry per value with source file and key path |
| tests | `tests/test_figure1.py`, 27 tests |
| current page | **3** |

Canonical data sources: `results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json`,
`results/h3_eight_cell/h3_eight_cell_summary.json`,
`results/minigrid_supporting/minigrid_supporting.json`,
`results/identical_score_churn_rev2.csv`, `results/atlas_cells_summary_rev2.csv`,
and `scripts/audit_stats.py` for the planning quantities.

Regenerate with the `fig_and_gate` pattern (regenerate + in-image pytest in one
job). **`fig1_values.json` must come back byte-identical** unless a value is
deliberately changing; that is the check that only geometry moved.

Thirteen defects have been fixed in it (three from source reading, ten from the
first render). It has been rendered and visually inspected at 250 dpi.

---

## 7. The headline ratio: RESOLVED

Full analysis: `docs/HEADLINE_CHURN_RATIO_DEFINITION.md`. Policy:
`docs/CHURN_RATIO_ZERO_DENOMINATOR_POLICY.md`. Both are current.

**No frozen registration defines this ratio.** The atlas registration fixes the
per-cell metrics and the population and is silent on aggregation, so the paper
names its aggregation openly.

**One convention now, unrounded, everywhere** (commit `48872d2`):

| | value | printed as |
|---|---|---|
| pooled, 1,707 cells | 0.120000 / 0.0222222 = 5.4000 | **5.40** |
| S1, 1,398 cells | 0.13745229 / 0.02631579 = 5.2232 | **5.22** |
| S2, 309 cells | 0.04800000 / 0.00924214 = 5.1936 | **5.19** |
| median of per-cell ratios, 1,562 cells | 3.8452 | **3.85** |
| ... 128 zero-delta cells readmitted | 4.2000 | 4.20 |
| controlled, ratio of medians | 12.1415 | **12.1** |
| controlled, median of per-cell ratios | 12.7080 | **12.7** |
| answer churn / net delta, pooled | 13.5000 | (README only) |

The retired 5.27/5.33 divided medians pre-rounded to 3 dp. `tab:atlas-strata`
now prints the four medians to six places so the printed ratios are reproducible
from the printed cells, and the caption says so.

**Zero-denominator policy, settled (commit `c63616b`).** 145 of 1,707 cells have
an exactly zero net delta; 128 of those have non-zero churn; 17 are true 0/0.
The ratio of medians is unaffected. The per-cell median excludes all 145, which
is **conservative**: readmitting the 128 as unbounded raises the median from
3.85 to 4.20, so 3.85 is a lower bound and cannot be a flattering choice. Zero
is defined at 1e-12, the same definition `sec:atlas:identical` already uses. One
rule, both strata; the removal rate differs (6.8% of S1, 16.2% of S2) and is
published.

**The cross-regime comparison is like-for-like both ways**, in the new
`tab:churn-aggregations`: controlled exceeds observational under the ratio of
medians (2.2x) and under the median of per-cell ratios (3.3x). Both are printed
deliberately, because quoting only the larger contrast would be selecting on the
answer, and a test requires both to point the same way.

**Everything above is generated and pinned.** `scripts/churn_ratio.py` computes
all of it from committed artifacts; `--check` verifies 25 printed values;
`tests/test_churn_ratio.py` adds 23 tests. Before this session the number
existed only as arithmetic in a LaTeX comment, which is how it rotted twice.

**Do not touch** the `$5.3\times$` in `certification.tex` and
`appendix_audit_table.tex`: that is the ifeval paired-versus-naive sample-size
advantage (4,211/800 = 5.26), a different quantity that rounds the same way.

**Public surfaces need no action.** The blog says "roughly five times" (fine);
Zenodo v1.0 asserts no ratio at all; `README.md` was corrected in `d8ddb90` and
is **not pushed**. No upload, DOI action or v1.1 bundle is required.

## 8. Layout: DONE

16 overfull hboxes and 1 vbox reduced to **2 hboxes, 0 vboxes**; body pages with
ink outside the text block **1 to 0**. Commit `f0ab36c`. Both survivors are
accepted with recorded reasons:

| pt | where | why accepted |
|---|---|---|
| 5.16 | `appendix_registrations.tex` | a 64-character revision hash with no break point, inside verbatim frozen text that cannot be edited. `\emergencystretch` 6em is already applied from outside. |
| 0.32 | `appendix_artifacts_detail.tex` | below the width of a rule; invisible |

Techniques used, all content-preserving: `\allowbreak` after `/` and escaped `_`
in long typewriter paths (zero-width, no hyphen printed); tighter `\tabcolsep`;
`\small`/`\footnotesize` matching neighbouring tables; two fixed-width columns
narrowed; one table split into two panels; `inner sep=0` on Figure 1's
full-width node. **No font was reduced to reach a page number, no margin or
measure changed, and no value, row or column was dropped.**

**Three things the Figure 1 generator's width guard cannot see**, now recorded in
the guard itself: vertical overflow, label collisions, and the inner sep TeX adds
*outside* a declared text width. The last one put the flagship figure 6.2pt into
the margin while every checked width fitted. Render the figure after any geometry
change; the guard is not a substitute.

## 9. Work completed and work remaining

### Relocations done (3 of 8)

| # | what | commit | body words |
|---|---|---|---|
| — | artifacts detail | `097a7a0` | 662 → 207 |
| 1 | harness-sensitivity detail | `7d50cf5` | 593 → 385 |
| 2 | extended related work | `110e125` | 991 → 741 |

Pattern that works, and must be repeated: **create the appendix destination
first, move whole, then remove from the body and leave a pointer.** Never cut
first. That ordering is why Wave 4 lost ~2,990 words.

### Relocations remaining, in the author's order

1. registration and amendment chronology (`preregistration.tex`)
2. **audit source-level cases and interpretive history (`audit.tex`)** ← the big one
3. mini-grid escalation mechanics (`minigrid.tex`)
4. full certification tables (`certification.tex`)
5. per-cell controlled tables (`minigrid.tex`)

**Measured finding to carry forward:** `preregistration.tex` is at 616 words
across three subsections, each already one paragraph with an appendix pointer,
and the K-sequence self-correction in it is a protected passage. It has ~100
words of slack at most. Do not expect a page from it.

**A relocation smaller than a page does not move the reference boundary.** The
related-work move pulled every later section forward one page and the boundary
stayed at 35, because the conclusion simply ends mid-page. Savings accumulate
before they register.

### Other pending work

- **Priority 3, DONE** (`ed54d4d`). The five lines are stated in outline at the
  end of the introduction, one sentence each, each pointing at the section that
  argues it, and **carrying no numbers** so no figure gets a second home to rot
  in. The conclusion states them in full and now says it is returning to lines
  the reader already has. Keep both copies; if a line changes, change both.
- **Priority 4, relocations: NOT STARTED.**
- **Priority 5, audit compression: NOT STARTED.** See §12.
- `paper/READING_COPY.md` still needs its single regeneration at the very end
  (`paper/tools/gen_reading_copy.py`).

## 10. Protected audit qualifications (must survive in the BODY)

From `docs/FLAGSHIP_NARRATIVE_PLAN.md` §8 and the author's Priority 5 list.
Locate each by its text; line numbers have shifted repeatedly.

1. The three frozen sampling frames and the inclusion rule.
2. **17** frozen candidates and **16** eligible. Both numbers, never collapsed.
3. Why **R10** is excluded.
4. **0** prospective numerical equivalence margins.
5. **10** qualitative/no-number claims, with the remaining category correctly
   defined (a measured outcome, not a declared tolerance).
6. **0** task-matched per-item output releases, with "task-matched" in the SAME
   SENTENCE as the zero, and the qualification that R08, R15 and R16 release
   outputs for other task suites.
7. **5** non-assessable: **4** insufficient reporting **+ 1** outside the
   registered binary paired-outcome calculation. Keep the explicit 4+1 split.
   **Never write "incompatible with a paired framework"**: it is the flip model
   that does not apply, not pairing.
8. **11** assessable claims at the registered uniform 2 pp margin.
9. The **10 above / 1 changes within / 0 below** atlas-IQR sensitivity split,
   and that no assessable claim falls below the threshold throughout.
10. **R01**'s sensitivity qualification; it is **not** robustly underpowered.
    There is exactly one outright statement of this, in the section close.
11. **43.6%** is a descriptive share of reference cells, not a probability,
    confidence level or p-value. Keep the number and its framing in one sentence.
12. Evidential sufficiency, **not truth**. **No claim is called false.**
13. **Not a prevalence estimate** for the literature.
14. **"Robust" means only** stable across the stated atlas-IQR interval. This is
    a SINGLE POINT OF FAILURE with no other home in the body: do not delete or
    weaken the sentence beginning *"Where a classification is called robust"*.
15. **R14** stays non-assessable and does not enter K. The trap paragraph stays
    in the body; "R04 and R14 carry no verdict" must re-attach to surviving prose.
16. **R04** is outside the registered calculation, not incompatible with paired
    analysis generally.
17. Claim-derived margins and the old shortfall range remain **withdrawn and
    non-verdict-bearing**. The **K = 1 → 5 → 4 → 1-of-11** sequence is the body's
    canonical self-correction and **must not move to an appendix**.
18. Also protected by project record: the two extraction passes are automated
    and **not statistically independent** (never "inter-rater verification");
    the re-verification was by the **author**, not independent.

**Deletion-only compression is not accepted.** Every removed evidentiary detail
must be redundant or have a named appendix destination.

---

## 11. Files to reread after compaction

In this order:

1. `CLAUDE.md` (project root; also present in the worktree).
   `AGENTS.md` is byte-identical to it, so reading one covers both.
2. **this file**
3. `docs/PAGE_MAP_2026-08-05.md`
4. `docs/HEADLINE_CHURN_RATIO_DEFINITION.md`
5. `docs/FLAGSHIP_NARRATIVE_PLAN.md` §§8, 9 (protected qualifications, prose rules)
6. `docs/PAPER_BUILD_ENVIRONMENT.md`
7. `docs/COMPILE_BASELINE_2026-08-05.md`
8. `docs/WAVE3_ADVERSARIAL_REVIEW_2026-08-05.md`
9. `paper/sections/atlas.tex` §`sec:atlas:netgross` (the ratio sites to change)
10. `paper/sections/audit.tex` (the compression target)

Then: `git status`, `git log --oneline af4d07e..HEAD`, and a clean compile.
**If the repository disagrees with this file, trust the repository and update
this file.**

---

## 12. Next command to execute

Reorient first (§11), confirm the state matches §4 and §5, then:

**Priority 4, the relocations, and Priority 5, the audit compression.** Neither
has been started. Priorities 1, 2 and 3 are complete, verified and committed.

### Why they were not started, so the next session does not repeat the mistake

The audit compression needs 18 protected qualifications held against 665 lines
of `sections/audit.tex` while several new appendix destinations are created and
verified. It is the one operation in this plan that cannot be safely left
half-finished: Wave 4 died mid-edit having cut ~2,990 body words with no
appendix destinations, and recovering from that cost a branch and a revert. It
should be started only with enough budget to finish a whole relocation, and each
relocation committed on its own.

### The rule that Wave 4 broke, restated

**Create the appendix destination FIRST, move the material whole, then remove it
from the body and leave a pointer.** Never cut first. A body edit that references
an appendix label that does not exist yet fails `PAPER_CHECK` with dangling
refs, which is how the earlier `audit.tex` attempt was caught.

### The audit's shape, measured (`sections/audit.tex`, 665 lines, 10 body pages)

| line | subsection |
|---|---|
| 68 | What was audited, and what was not |
| 130 | What the sources declare |
| 218 | Where the claim is written |
| 294 | Availability of per-item outputs |
| 337 | Verdict rules |
| 421 | Results |
| 546 | Claims that cannot be assessed |
| 598 | R04: outside the registered calculation |

**Destinations that already exist**, so relocating into them needs no new label:
`app:audit-table`, `app:audit-method`, `app:audit:locus` (already holds
`tab:audit-locus`), `app:audit:mdd`, `app:audit:imputation`,
`app:audit:robustness`, `app:extraction`.

**One safe, already-scoped move, identified but not made:** the retention
judgement for the two prose-juxtaposition cards, the paragraph beginning *"The
two prose-juxtaposition cards were kept"* (`audit.tex`, in
`sec:audit:locus`). Its table is already in `app:audit:locus`. It is roughly a
third of a page and is not one of the 18 protected items. The selection-effect
paragraph before it and the author-re-verification disclosure after it are both
load-bearing and stay in the body.

**Known open defect D6, do not try to fix it here:** the 3/2/1 locus tier counts
and the six-card denominator are hand-typed in both the body and the appendix.
They are not emitted by `gen_denominator_macros.py`, which is another session's
active file, and macro-ising them would mean editing that generator's validated
three-layer check from a branch that does not own it. **Do not add a second
generator.** Report it as still open.

### Order

1. Priority 4 relocations, each in its own commit, destination first.
   `preregistration.tex` has ~100 words of slack at most; do not expect a page
   from it. A relocation smaller than a page does not move the reference
   boundary, so savings accumulate before they register.
2. Priority 5, audit compression, 10 body pages toward 3-4, preserving all 18
   qualifications in §10 verbatim in substance. **Deletion-only compression is
   not accepted.**
3. Priority 6, final QA. Regenerate `paper/READING_COPY.md` last.

### After every change

```bash
cd paper
python3 tools/check_paper.py && python3 tools/gen_denominator_macros.py --check \
  && python3 tools/gen_audit_tables.py --check
python3 ../scripts/churn_ratio.py --check
export PATH=$HOME/scratch/texlive/bin/x86_64-linux:$PATH
pdflatex -interaction=nonstopmode main.tex && bibtex main \
  && pdflatex -interaction=nonstopmode main.tex \
  && pdflatex -interaction=nonstopmode main.tex
python3 tools/check_layout.py          # NOT optional; the log alone is not enough
python3 tools/measure_abstract.py
```

Anything touching `scripts/`, `tests/`, `configs/`, `flipeval/`, `pilot_eval/`
or `README.md` additionally needs the in-image gate (**expect 348 passed, 0
skipped**) and a freeze refresh after the commit.


---

# 2026-08-06 addendum: audit compression, and where the page target stands

## Done

- **Three wording checks** on the ratio result (`d0d460f`): "lower bound"
  retired everywhere in favour of the exact two-medians statement; the
  cross-regime comparison labelled descriptive and not a registered hypothesis;
  the 6.8% / 16.2% stratum exclusion rates placed beside the cellwise result.
  **The ratio machinery is closed. Do not reopen it.**
- **Protection ledger** (`59868de`), 18 rows, committed before any audit edit.
- **Eight appendix destinations created before any deletion** (`4879ed5`), plus
  `app:audit:verdictrules` in Stage C.
- **Stages A, B, C, D** (`cbd868b`, `9dc0c13`, `2679f97`, `48e77b1`). All 18
  qualifications verified **at source** after each stage.

## Two findings worth carrying

1. **Qualification 17 was not being met before this work.** The
   K = 1 → 5 → 4 → 1-of-11 sequence existed only in a LaTeX *comment* and in
   `app:prereg:choices`, so no reader of the compiled paper could see it. It is
   now body prose. Building the ledger is what surfaced it.
2. **`pdftotext` without `-layout` silently drops `\emph{}` runs.** It produced
   extracted text asserting that the two extraction passes *are* statistically
   independent, the exact opposite of a protected qualification. Verify
   protected phrasing against the LaTeX source.

## Where the page target stands, measured

**Main content is 34 pages; references begin on page 35.** The target is 20-24.
The audit went 10 → 8 pages and 3,307 → 2,630 prose words. Getting the audit to
3-4 pages requires removing about 1,200 more words from text that is now almost
entirely protected qualifications, and every paragraph with an appendix
destination has already been moved.

**All four remaining relocations were already complete**, verified not assumed.

The next 10 pages, if they are to be found at all, are in **mini-grid (6 pages,
target 3)**, **certification (5, target 4)**, **related work (2, target 1)** and
**conclusion (3, target 1.5)** — not in the audit. Whether that is worth doing
against the risk to load-bearing material is the author's call.


---

# 2026-08-06 addendum 2: body compression, four stages

**`audit.tex` is frozen** until the rest of the body has been compressed and
remeasured. That instruction is still in force; the next session must not edit it
without approving the proposal below.

| stage | section | result | commit |
|---|---|---|---|
| 1 | conclusion | 3 pages -> 1.5 | `fd64ddf` |
| 2 | related work | reorganised, 740 -> 505 words | `771be51` |
| 3 | certification | 5 pages -> 4 | `35a3d37` |
| 4 | mini-grid | 6 pages -> 5 | `c67ea5a` |

**Body 34 -> 32 pages. Target 26-29. Still three above.**

## Open item: the audit line edit, proposed and NOT executed

`docs/AUDIT_LINE_EDIT_PROPOSAL_2026-08-06.md` maps all 18 protected
qualifications to the sentence that carries each one after the edit. Fourteen are
untouched; four are shortened by merging elaboration around them, and none of the
four has its own sentence changed. Expected outcome: audit 8 -> ~6, body -> ~30.
**26-29 is not reachable from the audit alone**; the proposal's §6 says where the
rest would have to come from and recommends stopping at about 30.

## Two things this round established

1. **The layout gate caught a defect I introduced** (stage 3, an over-wide
   equation line putting ink in the page-7 margin). It was fixed before the
   commit. This is the case the gate was built for and it works.
2. **Related work had a duplicated sentence** shipped in the compiled PDF, fixed
   in stage 2. Prose defects of that kind are not caught by any gate; only
   reading is.

## State at this addendum

Body 1-32, references p33, total 100 pages. All gates pass, including in-image
pytest **348 passed, 0 skipped** (job 11705552). Two overfull boxes remain, both
in appendices, both classified in the QA report. Zero body pages have ink outside
the measure. Zero main floats leak into the appendices.
