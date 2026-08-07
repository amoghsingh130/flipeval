# Audit Registration, Amendment 5 (DRAFT — AWAITING SIGNATURE)

> **⏳ NOT SIGNED.** This draft is complete and ready to read. Nothing has been
> appended to `docs/AUDIT_REGISTRATION_2026-07-15.md`.
>
> To sign, give the verbatim instruction, as with Amendments 2, 3 and 4. The
> *Signed.* line below will then be completed with that instruction quoted, and
> the **Determination** and **Decision context** appended to the frozen
> registration under "Dated Amendments" — changing zero lines above the append
> point, verified after the append.
>
> **One thing only you can settle** is marked `[CONFIRM]` in *Decision context*.

Drafted by Claude Code, 2026-08-06, on the instruction "sign the addendum",
following the precedent of `docs/AUDIT_AMENDMENT4_DRAFT_2026-08-04.md`.

**The rewrite this amendment reports HAS been applied**, in a disposable clone
at `rewrite-clone/flipeval-v11`. Nothing has been pushed. This is the reverse of
Amendment 4's position, which was signed before application.

---

## Why this amendment is needed

Amendment 4 (signed 2026-08-04) authorises removing
`docs/audit_sources_20260731.tar.gz` from history, and its *Determination*
provides that "the full 54-row mapping at
`docs/audit_source_tarball_hash_map_20260804.tsv` governs any other stale
identifier."

That mapping was computed at `83d2b6c`. **Five commits postdate it**, each
carrying the tarball in its tree and therefore each rewritten. They fall outside
the governance Amendment 4 established, and the map cannot be extended by
editing it without contradicting the signed word "54-row".

**Three of the five are Amendment 4's own commits.** The commit that signed and
appended Amendment 4, `02ea10b`, becomes `5339a48`. An amendment written to
remap a signature's provenance pointer moved its own.

## What was verified before this draft was written

The rewrite was applied on 2026-08-06 to a disposable clone containing only
`main`, using **`git filter-branch --index-filter`** — the same tool the signed
map was computed with. A different tool was considered and rejected: commit
hashes are a function of the tool's exact output, and a substitution that
shifted any of the 54 signed pairs would have falsified a signed document
rather than implemented it.

- **All 54 signed rows reproduced exactly**, `bb45528 -> ed92ae8` included.
- 256 commits before and after; none pruned; author, email, author date,
  committer, committer date and subject byte-identical for every commit.
- The tarball is the only path differing in any tree, in every commit.
- The blob is absent from the object database and unreachable from every ref.
- **`987377a`, tag `v1.0.0`, is unchanged and remains an ancestor** of the
  sanitized tip, so publication is a fast-forward and requires no force push.
  The Zenodo archive of v1.0.0 lies outside the rewrite, as Amendment 4 stated.

Two further findings, both recorded because neither was anticipated:

- **Eleven refs reached the blob**, not only `main`: nine local branches
  (`flagship-narrative`, `wave2-body`, `wave2-frontback`, `wave4-partial-20260805`,
  `worker-a` through `worker-e`) and the tag `pre-source-tarball-removal-20260802`.
  The publication clone was made `--single-branch main`, so none followed it.
- **The source-state freeze fails its own gate after the rewrite.**
  `docs/PREPACE_FREEZE.json` recorded `source_commit` `8aafe22`, which the
  rewrite replaces with `4a8a83f`, so `--verify` reported "frozen source commit
  is not an ancestor of HEAD" — the identical failure the 2026-07-29 identity
  rewrite produced, and the reason tag `v1.0.0` had to be moved to `987377a`
  before Zenodo minted. It was refreshed. All 86 recorded file hashes are
  unchanged; only provenance pointers move.

## Determination

**The five commits Amendment 4's map could not reach are governed by
`docs/audit_source_tarball_hash_map_20260806_addendum.tsv`, and Amendment 4's
own signature commit is superseded on the record rather than in its text.**

First, the addendum file records the five old-to-new pairs and is read together
with the 54-row map as the complete mapping for the range `cc357db..HEAD`.
**The signed 54-row file is not edited**, and its "54-row" description remains
literally true of it.

Second, the signature line of Amendment 4 is to be read as citing `5339a48`
wherever it cites `02ea10b`, and its drafting commit `df1615b` as `7d053c1`.

Third, **the text of Amendment 4 is not edited**, for the reason Amendment 4
itself gave about Amendment 2: a provenance chain that repairs itself silently
is worth less than one that carries its own repair. The superseded identifiers
stay exactly as signed.

Fourth, the tag `pre-source-tarball-removal-20260802` is **deleted from the
publication clone rather than remapped**. It marks the state that still
contained the tarball; a remapped version of it would point at a tree without
the tarball and so would assert something false. The state it marked is
preserved outside the repository in the sealed pre-rewrite backup of
2026-08-06, which is not published.

*What this concedes.* The remapping recursed once, and this amendment is the
record of that recursion rather than a guarantee against it. **It does not
recur again.** Amendment 4 was drafted and committed while the tarball was still
in every tree, so its own commits were inside the range its map governed. This
amendment is the first appended *after* the rewrite was applied, so its commits
never contain the tarball and are never rewritten. The condition that produced
the defect is gone, not merely handled.

*Quantities unchanged.* No inclusion rule, eligibility rule, verdict rule,
indeterminacy rule, discordance imputation, denominator or count is reopened.
The eligible population remains 16. Amendments 1, 2, 3 and 4 remain in force in
full, and every published number stands.

*Scope.* This amendment records commit identifiers and one deleted tag. It
changes no analysis and no audited property.

## Decision context

**Results were inspected before this decision.** The rev-3 verdicts were
computed on 2026-07-31, the locus classification on 2026-08-02, Amendment 3 was
signed on 2026-08-03 and Amendment 4 on 2026-08-04; all were known here. This
amendment changes no analysis, no count and no verdict, so there is no outcome
for that knowledge to have biased. It is recorded because the standing
requirement applies to every amendment to a frozen protocol, not only to those
that could move a number.

`[CONFIRM]` — the sentence above is carried forward from Amendment 4 because the
same facts hold. Confirm it reads true for you, or replace it. It is the one
statement in this document that is yours to make and not mine to infer.

*Signed.* — **awaiting signature; do not treat this document as in force.**
