# Road to arXiv, then TMLR

Supersedes `docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md` as the working
carry list. That checklist stays authoritative for *what correctness means*;
this one is ordered by *what is left and in what order*. Where they disagree on
a requirement, the rev-3 checklist wins. Where they disagree on status, this
file wins, because status here was verified against the repo on 2026-08-03 and
not copied forward.

Baseline: HEAD `2857cd0`, 21 commits ahead of `origin/main`, deliberately
unpushed. Working tree clean apart from `.claude/worktrees/`.

---

## Part I: what is already finished

Verified by running the gates, not by reading the previous checklists.

### Done and holding

| Area | Evidence |
|---|---|
| **Canonical rev-3 numbers** | All 22 invariants are generated into `paper/audit_denominators.tex` from `results/audit_verdicts_rev3.csv` (sealed 0444, job `11591245`, sha `c85d6f8a...b150082b`), including the margin cross-tab that reconciles the taxonomy with "10 of 16 contain no number". No section types a denominator by hand. |
| **Audit adjudication (rev-3 §2)** | Inclusion rule applied to all 17, not only R10. R09, R13 and R17 locations rechecked character-by-character with positive, mutation and differential controls (`docs/AUDIT_SELF_RECHECK_2026-08-02.md`). R10 recorded ineligible. R17's prose/table sign contradiction recorded and shown not to move any magnitude. R14 cannot enter K, with a regression test. |
| **Manuscript claim replacement (rev-3 §5)** | Abstract rewritten, `tab:audit-underpowered` gone, "Stated margin" gone, task-matched wording in, R04 described as outside the binary paired-outcome framework, macros wired through the narrative at `241713a`. Zero failing stale hits anywhere under `paper/sections/`. |
| **Toolkit fail-closed (rev-3 §4)** | Golden test pins rev-1 to 1,936 and rev-2 to 2,010 (`4e47b44`). Boundary cases for `d* < 0`, `= 0`, `= 1`, `> 1` and integer ceiling covered (`tests/test_reversal_boundary.py`). Source fingerprint now fails on an *added* file, not only a changed one (`667a251`). |
| **Stale-claim linter exists** | `paper/tools/check_paper.py` with an allowlist, review-only paths, and negative-control tests. It is correct and it is currently red. |
| **Three of four local gates green** | `PAPER_CHECK: OK` (0 dangling refs, 0 unresolved cites, 25 tabulars consistent, anonymous build clean), `REGISTRATIONS_VERBATIM: OK` (5,206 words across 4 documents), `IDENTITY_REGEN: OK` (17 rows byte-for-byte). |
| **Amendment 2** | Signed 2026-07-31, in force. |
| **The empirical result the paper rests on** | H3 SUPPORTED and signed, 5 of 8 flips, 7 of 8 range-gap. Mini-grid and escalation sets archived, sealed and cited. Nothing here is reopened. |
| **v1.0.0 artifact** | Published, immutable, Zenodo version DOI `10.5281/zenodo.21708923`, HF dataset live at 209/209. |
| **Option A source paperwork** | Landed at `20a3b72`: the audited sources are identified, not redistributed. |
| **Anonymous build switch** | `\ifanon` present in `paper/main.tex` and exercised by `check_paper.py`. |

### Partly done

- **§10 J2C validation case.** `sec:audit:locus` is written and is the spine.
  The empirical half (identical aggregate, divergent per-item) exists as the
  escalation result but is not yet framed as *the* validation case with the
  contrast figure the checklist asks for.
- **§9 voice.** Several passes done, but the "human edits every paragraph" item
  has not happened and cannot be delegated.
- **§8 artifact.** v1.0.0 is immutable and correct as a v1.0.0. v1.1.0 has not
  been started.

### Not done

- Freeze fingerprint is **red**: 5 changed files (`README.md`, `STATUS.md`,
  `scripts/audit_verdicts.py`, `scripts/certification_tables.py`,
  `scripts/freeze_prepace.py`) and 5 unrecorded test files.
- Stale-claim linter is **red**: 18 live hits, 7 in the published blog post and
  11 in `paper/OUTLINE.md`.
- Amendment 3 drafted, **unsigned**.
- No rev-3 tag, no release manifest, no recorded rev-2 atlas provenance block.
- TOST wording correction (one-sided alpha 0.05 is a 90 percent two-sided
  interval, not 95) still unapplied.
- Independent validation of the required-sample-size calculation not done.
- arXiv and TMLR packages not started.
- **No LaTeX anywhere reachable.** Confirmed 2026-08-03: no `pdflatex`,
  `latexmk`, `xelatex` or `tectonic` on the login node, and no TeX Live module
  in the PACE module tree. Every §12 gate is blocked on this and nothing else.

---

## Part II: the road out

Six phases. Phases 0 and 1 run in parallel. Nothing after phase 2 can start
until the paper can be typeset.

### Phase 0: stop the bleeding (highest priority, independent of everything)

- [ ] **Correct the published blog post.**
      `paper/blog/2026-07-21-identical-scores-different-answers.md` asserts five
      numbers that Amendment 2 withdrew: "0 of the 17", "4 of the 12",
      "5 of the 17", the `2.0x` to `12.9x` shortfall range, and "the margin they
      assert". Seven linter hits at lines 130, 138, 150, 151, 152. This is the
      only place a withdrawn number is currently public.
- [ ] Add a dated correction notice to the post rather than silently editing it.
      The rule already applied to the artifact (visibly superseded, not quietly
      fixed) applies to prose the same way.
- [ ] Re-publish wherever the post is hosted, and confirm the live copy changed.
- [ ] **Retire or fence `paper/OUTLINE.md`.** Eleven hits, all planning material
      that never reaches the PDF. Either move it to `docs/` (which is already a
      review-only path) or add it to the review-only list with a stated reason.
      Do not edit its numbers: it is a dated record of what was planned.
- [ ] Confirm `check_paper.py` reports `STALE_CLAIM: OK` afterwards.

### Phase 1: close the open registrations and the fingerprint

- [ ] **Sign Amendment 3** (`docs/AUDIT_AMENDMENT3_DRAFT_2026-08-03.md`), or
      decide against it in writing. Amogh only.
- [ ] On signing: append Part 1 byte-identically under "Dated Amendments" in
      `docs/AUDIT_REGISTRATION_2026-07-15.md`, verify no line above it changed,
      and **regenerate `paper/sections/appendix_registrations.tex` in the same
      commit**. That gate failed silently for days after Amendment 2 for exactly
      this reason.
- [ ] **Green the source fingerprint.** Establish which of the 5 changed files
      are intended, run the in-image suite once for the 5 unrecorded test files,
      update the expected count in `CLAUDE.md` in the same commit, then
      `python3 scripts/freeze_prepace.py` and commit the refreshed freeze.
- [ ] Run `sbatch scripts/slurm/run_tests.sbatch` and record the
      `IN_IMAGE_PYTEST_SUMMARY:` line and log path. Current expectation is 297
      passed, 0 skipped. Any skip is a gate failure.
- [ ] **Apply the TOST correction.** One-sided alpha 0.05 corresponds to a 90
      percent two-sided confidence interval. This is a substantive statistical
      correction, not a wording preference, and it has been unassigned since
      2026-08-02.
- [ ] **Independently validate `n_req`** against a hand derivation or a second
      implementation, including nonzero true deltas. Record the check.

### Phase 2: get a machine that can typeset (the critical path)

Everything downstream is blocked here. Three options, in the order I would try
them:

- [ ] **Build a TeX Live Apptainer container on a compute node.** This is the
      cleanest fit for the environment already in use, needs no admin, and does
      not touch the pinned analysis image. Pull `texlive/texlive` or equivalent
      into `~/scratch/flipeval`, and note that scratch is 60-day purge so the
      recipe and the built `.sif` hash get recorded in `docs/`, not just the
      artifact. Submit builds with `sbatch -A $ACCOUNT -q embers`, all options
      before the script path.
- [ ] **Or compile on a local machine** with a TeX distribution and carry the
      PDF back.
- [ ] **Or Overleaf** for the visual pass only. Note this leaks the manuscript
      to a third party, so it is not appropriate for the anonymous package.
- [ ] Record the chosen toolchain and its version in the release manifest. The
      PDF is a released artifact and its build environment is part of provenance.

### Phase 3: first full typeset and the reckoning

Nothing in this phase has ever been executed. Budget for it generously.

- [ ] Compile `paper/main.tex` clean, both `\anontrue` and `\anonfalse`.
- [ ] **Typeset `tab:audit-locus` for the first time.** It has never been seen
      rendered.
- [ ] Typeset all 25 tabulars. Expect breakage: the appendix audit table has 11
      rows of numeric columns and has never been fitted to a page.
- [ ] **Check the TMLR geometry specifically.** `tmlr.sty` is single-column,
      6.5 by 9 inches. Everything reflows relative to any two-column draft. Wide
      tables are where this will hurt.
- [ ] Read every page. Fix overflowing paths, illegible tables, broken
      references, awkward page breaks.
- [ ] Spelling, grammar, citation and duplicate-reference checks against the
      compiled document, not the source.
- [ ] Verify every number in the abstract, main tables and conclusion against
      `paper/audit_denominators.tex`, reading the PDF.
- [ ] **Macro-ise the tier counts in `sec:audit:locus`.** It hand-types 3, 2, 1
      and the six-card denominator, against the standing rule. They belong in
      `paper/tools/gen_denominator_macros.py`. Do not add a second generator.
      Cheap, and do it before the PDF is frozen.

### Phase 4: finish the J2C argument

Do this after phase 3, when you can see the paper, and before packaging.

- [ ] **Lead with the reporting-standards result, not the K count.** After
      Amendment 2 the quantitative headline is 1 flagged claim out of 11, and the
      paper itself reports that the one does not survive sensitivity. A reviewer
      reads that as close to null. The durable contribution is that no source
      declares a margin, almost none releases per-item outputs, and whether a
      claim is auditable at all depends on where it was written. That argument
      survives the headline collapsing.
- [ ] Present the escalation result as the explicit validation case: near
      identical aggregate accuracy, materially different per-item behaviour.
- [ ] Show a conventional aggregate-delta analysis and the paired certificate
      reaching different conclusions on the same data.
- [ ] Demonstrate stable certification, sensitivity-dependent classification and
      insufficient evidence as three distinct outcomes.
- [ ] **One memorable figure** connecting aggregate delta, discordance, declared
      margin and certification outcome. The paper does not currently have a
      figure that does this and it is the single highest-leverage addition left.
- [ ] Keep this validation strictly separate from the audit denominators and the
      amendment logic.
- [ ] Human pass over every paragraph for cadence and judgement. Reduce the
      residual "registered" and "frozen" procedural density.

### Phase 5: artifact, then arXiv

- [ ] **Cut a rev-3 tag** and record the commit used for every final calculation.
- [ ] Record the rev-2 atlas path, revision, sha256, schema version and row
      count 792 in one provenance block.
- [ ] Record hashes for the rev-3 audit table, source manifest, configuration,
      generated tables and final PDF.
- [ ] **Publish Zenodo v1.1.0.** A new immutable version, never a replacement of
      v1.0.0. Change log, rev-2 to rev-3 mapping, exact commands, hashes.
- [ ] Cite the version DOI where exact reproducibility is claimed; the concept
      DOI only for discovery.
- [ ] Confirm the artifact reproduces from its own instructions in a clean
      environment.
- [ ] **Resolve the push blocker.** 21 commits are local. The history rewrite is
      blocked because signed Amendment 2 cites `bb45528`. Either Amogh signs a
      dated amendment recording the old-to-new hash mapping, or the rewrite is
      abandoned and the branch is pushed as is. arXiv can go out either way, but
      the artifact link cannot point at a repository that does not exist yet.
- [ ] Build the **named** arXiv package: author identity, version-specific
      artifact link, and a version note since a public draft already exists.
- [ ] Confirm the arXiv PDF, source archive and artifact version agree.
- [ ] Post to arXiv.

### Phase 6: TMLR

- [ ] Build the **anonymous** package with unmodified `tmlr.sty`.
- [ ] Strip names, affiliations, acknowledgements, grants, usernames, absolute
      paths and PDF metadata.
- [ ] **Do not link the anonymous submission to the named arXiv, GitHub or
      Zenodo release.** TMLR permits a concurrent arXiv preprint; it does not
      permit the submission to point at it.
- [ ] Anonymous supplementary ZIP with no Git history, remotes, author metadata
      or identity-bearing logs.
- [ ] Scan the PDF text and the ZIP contents for `Amogh`, `Georgia Tech`,
      `asingh3206`, `/storage/home/`, `/Users/`, repository URLs, DOI links and
      acknowledgements. Automate this as a gate, do not eyeball it.
- [ ] Confirm no artifact hash in the manuscript functions as an identity link.
- [ ] Freeze final hashes for the PDF, source package, supplementary package and
      artifact release.
- [ ] Submit.

---

## Standing constraints that shape all of the above

- **No second human, permanently.** Author re-verification and automated passes
  are never described as independent or inter-rater verification. Amendment 3's
  verification-status paragraph is the clause that holds this line and must
  survive editing intact.
- **No em dashes** in the paper or in chat.
- **Frozen files are amendment-only**, written by Amogh, stating whether results
  were inspected before the decision.
- **Every `sbatch` option precedes the script path**, and no job script gets a
  default grid.
- **A scheduler control is in force only when independently observed.**

## What I would do next, in order

1. The blog correction. It is the only public falsehood and it is independent of
   every blocker.
2. Sign or decline Amendment 3, since it is a single decision that unblocks the
   registration record.
3. Get TeX running. Everything from phase 3 onward is dead until it exists, and
   the first typeset will surface work that is not yet on any list.
