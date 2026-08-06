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
| HEAD | `9612a124b9429a1511d7653afc9d0b210801bfc6` (`9612a12`) |
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

## 4. Measured state (verified at `9612a12`, clean build)

| quantity | first baseline (`18b2db1`) | **now** |
|---|---|---|
| **Main content, before references** | 1–35 | **1–35** |
| References | 36–38 | **36–38** |
| Appendices | 39–96 | **39–96** |
| **Total PDF** | 96 | **96** |
| Figure 1 page | 87 | **3** |
| Overfull hbox | 58 | **16**, worst 82.0pt |
| Overfull vbox | 0 | **1**, 2.69pt |
| Underfull hbox | 11 | **34** (cost of `\emergencystretch`; loose lines, no ink in margin) |
| Undefined refs / cites | 0 / 0 | **0 / 0** |
| Body pages with ink past the text block | 4 | **1** (p9, +5.2pt) |

**Correction to a previously reported figure:** total PDF is **96**, not 95. It
was 95 before the related-work relocation; relocation grows the appendix faster
than it shrinks the body, which is expected and fine.

### Section page map (verified)

| section | starts | span |
|---|---|---|
| Introduction + Fig 1 | 2 | 3 |
| Related work | 5 | 2 |
| Paired certification | 7 | 3 |
| Preregistration | 10 | 2 |
| Atlas | 12 | 4 |
| **Audit** | **16** | **9** |
| Mini-grid | 25 | 6 |
| Harness sensitivity | 31 | 1 |
| Artifacts | 32 | 0 |
| Limitations | 32 | 2 |
| Conclusion | 34 | 2 |

Fuller map with prose word counts, float inventory and target budgets:
`docs/PAGE_MAP_2026-08-05.md`.

### Float placement (all `[!t]`; verify after any change to a float's height)

`fig:cancellation` p3 · `tab:certification` p9 · `tab:atlas-strata` p14 ·
`tab:audit-taxonomy` p18 · `tab:audit-sensitivity` p22 · `tab:h3-eightcell` p27.

**Float placement is fragile.** Figure 1 originally sat on page 87, and making
three body tables taller once pushed them to pages 85–86. `[!t]` is what holds
them. Any new float must be `[!t]` from the start.

---

## 5. Gates currently passing (exact)

```
in-image pytest, job 11697689 : 325 passed, 0 skipped
PAPER_CHECK                   : OK, 0 dangling refs, 0 unresolved cites
                                24 files, 109 labels, 171 refs, 23 cite keys,
                                12 environments, 24 tabulars (234 rows)
STALE_CLAIM                   : OK
REGISTRATIONS_VERBATIM        : OK, 7,103 words across 4 documents
gen_denominator_macros --check: OK on all three layers
  INPUT_DIGEST                : audit_verdicts_rev3.csv sha256 matches
  CANONICAL_INVARIANTS        : 27 values reproduce the final checklist
  COMMITTED_LEDGER            : 190 lines reproduce audit_denominators.tex
freeze_prepace --verify       : passed
ABSTRACT_CHARS                : 1879 / 1920, margin 41, 283 words
prose em dashes               : 0
undefined refs / cites        : 0 / 0
bbox margin check             : 1 of 35 body pages, p9 at +5.2pt
```

The expected in-image count in `CLAUDE.md` is **325** and is correct. No tests
were added this session.

---

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

## 7. The headline ratio: state and the unresolved question

Full analysis: **`docs/HEADLINE_CHURN_RATIO_DEFINITION.md`**. Read it in full.

**No frozen registration defines this ratio.** The atlas registration §5 fixes
the per-cell metrics, §6 fixes the population, and both are silent on
aggregation. It is a descriptive summary, named explicitly in the paper.

Verified values over the registered 1,707-cell population
(`excluded_or_skipped` false, `contains_disclosed_probe_cell` false):

| quantity | value |
|---|---|
| pooled median churn | 0.120000 |
| pooled median abs net delta | 0.0222222 |
| **pooled ratio of medians, unrounded** | **5.4000 exactly** |
| S1 (n=1,398) medians | 0.137452 / 0.026316 |
| S1 ratio unrounded | **5.2232** |
| S1 ratio from 3dp-rounded medians | 5.2692 → 5.27 |
| S2 (n=309) medians | 0.048000 / 0.009242 |
| S2 ratio unrounded | **5.1936** |
| S2 ratio from 3dp-rounded medians | 5.3333 → 5.33 |
| median of per-cell ratios (1,562 cells) | 3.8452 |
| mean of per-cell ratios | 7.4125 |
| answer churn / net delta, pooled | 13.5000 |

**THE UNRESOLVED CONSISTENCY PROBLEM, and the next task.** The manuscript
currently prints pooled **5.40** (unrounded) alongside stratum **5.27/5.33**
(computed from 3dp-rounded medians). That is two rounding conventions in one
sentence. The author has directed:

- use **one convention, unrounded, from canonical artifacts**: pooled 5.40,
  S1 **5.22**, S2 **5.19**;
- do **not** keep 5.27/5.33 merely because they reproduce from the printed
  table; instead either print more digits in `tab:atlas-strata` or give the
  exact medians in a note;
- abstract/introduction/conclusion keep "roughly five times";
- technical prose names the aggregation, "the ratio of median accuracy-state
  churn to median absolute accuracy change", and says explicitly it is not the
  median of cellwise ratios.

**Sites to change** (`sections/atlas.tex` only, for the stratum figures):
the prose "5.27 in S1 and 5.33 in S2", the SOURCE comment block at the head of
`sec:atlas:netgross`, and the comment near the section close. The retired
`5.3\times` is already gone from all six former headline sites.

**Do not touch** the `$5.3\times$` in `certification.tex:136` and
`appendix_audit_table.tex:370,399`. That is the ifeval paired-versus-naive
sample-size advantage (4,211/800 = 5.26), a different quantity that rounds the
same way.

### Also unresolved: zero-denominator policy (Priority 1B)

The 3.85 figure excludes the **145 exact-zero-delta cells** because the per-cell
ratio is undefined there. Those cells are the subject of `sec:atlas:identical`
and 128 of them have non-zero churn, so they must not vanish silently from a
metric meant to summarise cancellation. Required: document how zero-delta and
zero-churn cells are handled, whether the policy differs by stratum, how many
cells enter the median, whether the controlled calculation uses the same policy,
and **add tests**. Then make the atlas-vs-controlled comparison like-for-like,
or drop the numeric 3.85-vs-12.7 comparison entirely.

`minigrid.tex` Result 1 currently compares 3.85 (atlas, median of per-cell
ratios) against 12.7 (controlled, median of per-cell ratios) and gives 5.40
separately. That comparison is like-for-like on aggregation but its zero policy
is undocumented, which is exactly what 1B must settle.

### Public surfaces

- Blog (`paper/blog/2026-07-21-...md:121`) says "roughly **five times**". **No
  correction needed.**
- Zenodo v1.0 asserts **no ratio at all**; it ships raw per-cell CSVs. **No
  upload, no DOI action, no v1.1 bundle required.**
- `README.md` was corrected in commit `d8ddb90` (it had attributed the ratio to
  *answer* churn, whose true value is 13.50). **Not pushed.** README.md is
  inside the source fingerprint, so any further edit needs a freeze refresh.

---

## 8. Layout: remaining warnings

All 16 overfull hboxes, verified at `9612a12`:

| pt | page | source | line |
|---|---|---|---|
| 82.0 | 48 | `appendix_audit_table.tex` | 75 |
| 59.4 | 69 | (output routine) | 47 |
| 54.1 | 60 | `appendix_minigrid_detail.tex` | 248 |
| 47.8 | 60 | `appendix_minigrid_detail.tex` | 179 |
| 36.2 | 60 | `appendix_minigrid_detail.tex` | 274 |
| 33.2 | 63 | `appendix_harness_detail.tex` | 201 |
| 28.2 | 57 | `appendix_atlas_detail.tex` | 97 |
| 21.9 | 67 | (output routine) | 196 |
| 11.9 | 69 | (output routine) | 95 |
| 10.7 | 54 | (output routine) | 382 |
| 9.9 | 57 | `appendix_atlas_detail.tex` | 102 |
| 7.7 | 54 | (output routine) | 418 |
| **7.7** | **7** | **`certification.tex`** | **136** |
| **6.2** | **1** | (output routine) | 96 |
| 5.2 | 92 | (output routine) | 369 |
| **1.7** | **26** | (output routine) | 154 |

**Only four are in the main body** (pages 1, 7, 26 and the p9 bbox hit), and all
are ≤7.7pt. Everything ≥28pt is in an appendix. The 2.69pt overfull vbox is on
page 2 and has not yet been visually checked; the author has asked that it be
accepted only after that check.

**A warning about method.** Three of the worst offenders found earlier produced
*no* LaTeX warning at all, because a `tabular` inside `\centering` that exceeds
`\textwidth` is set silently. They were found with:

```bash
pdftotext -bbox -f 1 -l 35 main.pdf /tmp/bb.html
# then compare max xMax per page against the modal text-block right edge (484.5pt)
```

**Keep this bounding-box check. The log alone is not sufficient.** The author has
asked for it to become a build gate.

---

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

- **Priority 3, narrative**: move a compact five-line reporting standard to the
  end of the introduction or just after the certification framework, so the
  flagship argument completes early. The conclusion then recaps rather than
  introduces. Authorized as a narrative change, not a scientific one.
- **Priority 5, audit compression**: 9 body pages → target 3–4.
- `paper/READING_COPY.md` still needs its single regeneration at the very end
  (`paper/tools/gen_reading_copy.py`).

---

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

**Priority 1A — the ratio-consistency gate. Do this before touching the audit.**

Edit `paper/sections/atlas.tex` only:

- replace the prose "5.27 in S1 and 5.33 in S2" with the unrounded
  **5.22** and **5.19**;
- update the SOURCE comment block at the head of `sec:atlas:netgross` so the
  recorded derivation is the unrounded one;
- make the stratum medians reproducible: either print more decimal places in
  `tab:atlas-strata` or add a note giving 0.137452 / 0.026316 / 0.048000 /
  0.009242;
- keep pooled 5.40 and the "not the median of cellwise ratios" sentence;
- verify with:

```bash
cd paper && python3 tools/check_paper.py && python3 tools/gen_denominator_macros.py --check
export PATH=$HOME/scratch/texlive/bin/x86_64-linux:$PATH
pdflatex -interaction=nonstopmode main.tex && bibtex main \
  && pdflatex -interaction=nonstopmode main.tex \
  && pdflatex -interaction=nonstopmode main.tex
```

Then **Priority 1B**, the zero-denominator policy, with tests, before any audit
compression. Commit the ratio correction separately.
