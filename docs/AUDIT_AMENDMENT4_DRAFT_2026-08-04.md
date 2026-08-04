# Amendment 4 to `docs/AUDIT_REGISTRATION_2026-07-15.md` — DRAFT, UNSIGNED

**Status: DRAFT. Not appended to the frozen registration. Not signed.**

Drafted by Claude Code, 2026-08-04, at the author's instruction to "deal with
the tarball". It is reproduced here for review; only Amogh may append it to the
frozen file, and only Amogh may sign it. Nothing in the rewrite it describes has
been applied. `main` is untouched and nothing has been pushed.

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

## Decision context

**To be completed by the author before signing.** State whether results were
inspected before this decision, per the standing requirement on every amendment
to a frozen protocol.

## Determination

**To be written by the author.**

---

*Signed.* **UNSIGNED — awaiting Amogh Singh.**
