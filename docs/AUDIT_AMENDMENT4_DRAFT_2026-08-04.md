# Audit Registration, Amendment 4 (SIGNED, APPENDED — DRAFTING RECORD ONLY)

> **✅ SIGNED by Amogh Singh, 2026-08-04**, on the verbatim instruction "i read
> the draft, fill in the two sections as approved and append". Appended to
> `docs/AUDIT_REGISTRATION_2026-07-15.md` under "Dated Amendments" (lines
> 346-411), verified to have changed **0 lines above the append point**.
>
> **THE OPERATIVE TEXT IS THE REGISTRATION, NOT THIS FILE.** This is now a
> drafting record, retained for the provenance of the wording. Amending
> Amendment 4 means a new dated amendment, never an edit here. Editing below
> would silently desynchronise this file from the frozen document and from the
> appendix that reproduces it.
>
> The appended text is reorganised into the frozen file's run-in heading style
> (*Occasion.*, *Finding.*, *Determination.*, …) to match Amendments 2 and 3.
> The substance is the same; where the two differ in wording, the registration
> governs.

Drafted by Claude Code, 2026-08-04, at the author's instruction to "deal with
the tarball", following the precedent of
`docs/AUDIT_AMENDMENT3_DRAFT_2026-08-03.md`.

**The rewrite this amendment authorises had NOT been applied at the time of
signature.** `main` was untouched and nothing had been pushed.

---

## Why this amendment is needed

`docs/audit_sources_20260731.tar.gz` holds the full-text captures of all 17
audited sources. It entered the repository at `cc357db` and was never deleted,
so every commit from there to HEAD carries it in its tree. `origin` is a public
GitHub repository. Pushing any commit in that range publishes the corpus.

That collides with the redistribution review of 2026-08-02, which found four of
the seventeen carry no grant permitting a third party to republish their text
(the Meta AI blog post, the NVIDIA TensorRT-LLM documentation page, and two vLLM
pages), and with the seven method papers sitting under arXiv's default licence,
which authorises arXiv to distribute them rather than authorising us to. It also
contradicts `README.md`, which states that the captures "are not redistributed
and are not part of any release."

Removing the blob rewrites 54 commits. **`bb45528` is one of them**, and
Amendment 2 cites it in its signature line at
`docs/AUDIT_REGISTRATION_2026-07-15.md:228`:

> *Signed.* Amogh Singh, 2026-07-31. Drafted by Claude Code at `19d485c`,
> revised at `bb45528` after the full-text source verification, and appended on
> the verbatim instruction "sign and append".

A signed provenance chain would otherwise point at a commit that no longer
exists. This amendment exists to remap that pointer on the record rather than
to let it silently break.

## What is being changed

Nothing in the audit protocol. No inclusion rule, eligibility rule, verdict
rule, indeterminacy rule, discordance imputation, denominator or count is
reopened or affected. Amendments 1, 2 and 3 remain in force in full, and every
published number stands unchanged.

What changes is one class of fact: the commit identifiers by which parts of this
registration's own provenance are cited.

## The remapping

`bb45528` is superseded by `ed92ae8`. In full:

```
bb455284a915f28ad8c7b94cabb59983c84a359b  ->  ed92ae84ab9482173c7988e9787d318b7d2426cd
```

The signature line of Amendment 2 is to be read as citing `ed92ae8` wherever it
cites `bb45528`. The original text of Amendment 2 is **not** edited: the
superseded identifier stays as written, because editing it would destroy the
record of what was signed.

The complete 54-row old-to-new mapping is recorded at
`docs/audit_source_tarball_hash_map_20260804.tsv`. `19d485c`, also cited in the
same signature line, is an ancestor of `cc357db` and **does not change**.
Likewise `987377a` (tag `v1.0.0`) is an ancestor of `cc357db`, so the release tag
and its Zenodo archive lie outside the rewrite entirely.

## What was verified before this draft was written

The rewrite was performed on a throwaway clone, never on the working repository:

- 251 commits before, 251 after. No commit was pruned; the mapping is 1:1.
- Author, email, date and subject are byte-identical for every commit.
- The only tree difference across the entire range is the removed tarball.
- `docs/audit_sources_20260731.tar.gz.sha256` and
  `docs/audit_sources_manifest.tsv` are **retained**, so the corpus stays
  identified and digest-checkable exactly as `README.md` describes.
- The blob is unreachable from the rewritten branch.
- The private sealed copy at
  `/storage/project/ps-compressedlm-0/asingh3206/private/audit_sources_20260731/`
  hashes `a912a1e7af0efd58459dcf57ade84be96cfea8337147a13d336dacfdb9240259`,
  byte-identical to the blob in git. Removing it from the repository loses
  nothing.

## Consequences to accept if this is signed

- 54 commit hashes change. Any reference to one of them in a document, a log or
  a notebook becomes stale unless read through the mapping file.
- `paper/sections/appendix_registrations.tex` and `paper/READING_COPY.md`
  reproduce the Amendment 2 signature line verbatim. Both are generated; they
  must be regenerated and the word-stream check re-run against the frozen source
  after this amendment is appended.
- The rewrite is irreversible once pushed. The pre-rewrite history is preserved
  locally at tag `pre-source-tarball-removal-20260802` and at a fresh tag to be
  cut immediately before the rewrite is applied.

## Determination

**The tarball is removed from the repository's history, and `bb45528` is
superseded by `ed92ae8` on the record rather than in the text.**

Three things follow, and the third is the one that matters.

First, `docs/audit_sources_20260731.tar.gz` is removed from every tree in the
range `cc357db..HEAD`. The corpus remains identified and digest-checkable:
`docs/audit_sources_20260731.tar.gz.sha256` and
`docs/audit_sources_manifest.tsv` are retained, and
`scripts/fetch_audit_sources.py` rebuilds the corpus from each publisher. This
is Option A carried through to the artifact it was always meant to reach, not a
new policy.

Second, the signature line of Amendment 2 is to be read as citing `ed92ae8`
wherever it cites `bb45528`, and the full 54-row mapping at
`docs/audit_source_tarball_hash_map_20260804.tsv` governs any other stale
identifier.

Third, **the original text of Amendment 2 is not edited.** The superseded
identifier stays exactly as signed. Correcting it in place would leave a record
that reads as though the chain never broke, and the fact that it broke is the
thing this amendment exists to preserve. A provenance chain that repairs itself
silently is worth less than one that carries its own repair.

*What this concedes.* The rewrite is irreversible once pushed, and 54 commit
hashes cited anywhere outside the mapping file become stale without warning. The
alternative considered was abandoning the rewrite and never pushing, which was
the resolution of record from 2026-08-02. It is rejected here because it makes
the repository permanently unpublishable, and the artifact link in a submitted
paper cannot point at a repository that does not exist. The cost of the rewrite
is borne once and is documented; the cost of not pushing recurs indefinitely.

*Quantities unchanged.* No inclusion rule, eligibility rule, verdict rule,
indeterminacy rule, discordance imputation, denominator or count is reopened.
The eligible population remains 16. Amendments 1, 2 and 3 remain in force in
full. Every published number stands.

## Decision context

**Results were inspected before this decision.** The rev-3 verdicts were
computed on 2026-07-31, the locus classification on 2026-08-02, and Amendment 3
was signed on 2026-08-03; all were known at signature. This amendment changes no
analysis, no count and no verdict, so there is no outcome for that knowledge to
have biased. It is recorded because the standing requirement applies to every
amendment to a frozen protocol, not only to those that could move a number.

---

*Signed.* Amogh Singh, 2026-08-04. Drafted by Claude Code at `df1615b` after the
rewrite was computed and verified on a throwaway clone; its *Determination* and
*Decision context* were completed on the verbatim instruction "i read the draft,
fill in the two sections as approved and append". The rewrite itself was not
applied at the time of signature.
