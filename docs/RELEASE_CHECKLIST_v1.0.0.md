# Artifact Release Checklist — v1.0.0

> ## ⚠️ CORRECTION, 2026-07-28 — the repository was ALREADY PUBLIC
>
> **Step 1 below ("make the repository public") describes an event that had
> already happened.** `gh repo view` returns `visibility: PUBLIC`, and the repo
> has been public since **2026-07-20**. Every document in this chain — this
> checklist, the decision record, the session reports — asserted it was private.
> None of them checked. See **incident 28**.
>
> **Consequence, stated plainly.** The three personal documents were readable at
> the public tip from 2026-07-20 until **2026-07-28**, because the deletion
> commit `e4cae49` sat unpushed along with 86 others. They are now off the tip
> (pushed `272136b..201424f`) and remain in history, which is the accepted
> option-(b) position. Pushing did not retract the eight days; it moved the
> documents from *findable at HEAD* to *recoverable by someone already digging*.
>
> **Branch rename, same day.** `codex/pre-pace-implementation` → `main`.
> `main` did not previously exist locally or remotely, so nothing was forced and
> nothing was lost; the old branch was deleted with `git branch -d` (which would
> have refused had anything been unmerged). GitHub's default branch is now
> `main`. The three cited freeze hashes `b74fd58`, `f06348f` and `715a7ce` all
> still resolve — a rename moves no commits.
>
> `docs/PREPACE_FREEZE.json` still records `"branch": "codex/pre-pace-implementation"`
> and is **deliberately not regenerated**: it is a dated record of the source
> state at freeze time, its `created_at` and `source_commit` are historical, and
> regenerating it to fix a cosmetic field would overwrite that record. It still
> verifies `passed: true` — the branch field is metadata, not part of the
> fingerprint.

**For Amogh. Every step below needs credentials I do not have.** Preparation,
scrubbing and verification are done; what remains is authentication and upload.

**Version string is `v1.0.0`,** used identically for the source tag, the archived
release and the dataset revision. Do not let these drift — the paper cites one
version.

The staged bundle is at:

```
<PROJECT>/asingh3206/release/flipeval-artifacts-v1.0.0/
```

209 files, 331 MB, `SHA256SUMS` at its root. It is scrubbed and verified; see
§"What was already checked" at the end.

It lives on the **project** filesystem, not scratch (60-day purge) and not the
repository (it is a 331 MB derived export). Re-verify any time with
`sha256sum -c SHA256SUMS` from the bundle root — it passed 208/208 after being
copied into place.

---

## Order of operations — EXECUTE IN THIS ORDER

**Step 2 must precede step 4.** That is the whole trap: Zenodo only sees GitHub
releases created *after* the toggle is switched on. Everything else is ordinary.

| # | Step | Notes |
|---|---|---|
| 1 | **Make the repository public** | Settings → General → Danger Zone → Change visibility. Confirm `LICENSE` is Apache-2.0 first. |
| 2 | **⚠️ ENABLE THE ZENODO–GITHUB TOGGLE FOR THIS REPO** | <https://zenodo.org> → sign in with GitHub → Settings → GitHub → switch **ON** for **`amoghsingh130/flipeval`** (GitHub handle). **This must happen before step 4.** |
| 3 | **Tag** | `git tag v1.0.0 && git push origin v1.0.0` |
| 4 | **Create a GitHub RELEASE from that tag** | `gh release create v1.0.0 --title "FlipEval v1.0.0" --notes "Companion code release for 'Certifying Compressed Language Models'."` **A tag alone mints nothing** — Zenodo triggers on the *release* event. |
| 5 | **Record BOTH DOIs** | Zenodo issues a **concept DOI** (resolves to latest) and a **v1.0.0 version DOI**. Write both down. **The paper cites the version DOI** — it describes a frozen state. |
| 6 | **`hf auth login --force`** | **NOT `huggingface-cli`** — `huggingface_hub` 1.x renamed the entry point to `hf`, and the old name is gone, not merely absent. `--force` is required: a plain `hf auth login` short-circuits on any stored token and never prompts. |
| 7 | **Upload the bundle** | `hf upload AmoghSingh123/flipeval-artifacts <bundle_path> . --repo-type=dataset` — **`AmoghSingh123` is the HuggingFace handle**, not the GitHub one |
| 8 | **Confirm the HF repo is public and not gated** | Settings → check visibility, and that no gating/access request is enabled. |

**If step 4 happened before step 2:** Zenodo never saw the release. **Delete the
GitHub Release and recreate it** — the tag can stay, and recreating the release
re-fires the webhook.

The bundle path is:

```
<PROJECT>/asingh3206/release/flipeval-artifacts-v1.0.0
```

## ✅ MINTED 2026-07-30 — the identifiers now exist

Steps 1–5 are complete. Zenodo minted on the release event, so the step-2 ordering
trap was avoided.

| Identifier | Value | Use |
|---|---|---|
| **Version DOI** | **`10.5281/zenodo.21708923`** | **Canonical. What the paper cites** — it resolves to the frozen v1.0.0 state. |
| Concept DOI | `10.5281/zenodo.21708922` | Resolves to whichever version is latest. Cite when you mean the artifact series, never for a specific claim. |

Zenodo record title: `amoghsingh130/flipeval: FlipEval v1.0.0`, version `v1.0.0`.

**Which is which was resolved from Zenodo's own record, not by inference.**
`https://zenodo.org/api/records/21708923` reports `doi` =
`10.5281/zenodo.21708923` and `conceptdoi` = `10.5281/zenodo.21708922`. The two
differ by one in the final digit, which makes them easy to transpose and
impossible to tell apart by eye — always re-read them from the API rather than
from a paste.

### Release state as executed

- **Tag `v1.0.0` → `987377a`**, not the `28c4c89` originally tagged. The tag was
  moved before the release was created, because at `28c4c89` the tagged tree's
  `docs/PREPACE_FREEZE.json` still pointed at pre-rewrite commit `92ece44`,
  which the 2026-07-29 identity rewrite made a non-ancestor of `main` — so the
  archived snapshot would have shipped a source-state freeze that **failed its
  own `--verify` gate**, the gate §3 relies on. It verifies `passed: true` at
  `987377a`. Zenodo archives the *tag's* tarball, not the branch tip, so this
  had to be fixed before step 4 and would have been unfixable after minting.
- Release published (not draft — Zenodo ignores drafts), not prerelease:
  <https://github.com/amoghsingh130/flipeval/releases/tag/v1.0.0>

### Bundle correction, 2026-07-30, before upload

The staged bundle's `README.md` cited the code repository as
`https://github.com/AmoghSingh123/flipeval` — the **HuggingFace** handle in a
**GitHub** URL, which 404s. Corrected to `amoghsingh130`. The same pass filled
the BibTeX `doi` field (was `TODO-ZENODO-DOI`) with the version DOI and added a
note distinguishing the two DOIs. `SHA256SUMS` was updated for `README.md` and
re-verified **208/208 OK**. The two handles have now crossed twice — see
incident 28.

### ✅ STEPS 6-8 DONE 2026-07-30 — dataset published

<https://huggingface.co/datasets/AmoghSingh123/flipeval-artifacts>, commit
`c197d65416c2458bd4161fe741fcc44252e57114`.

**209/209 files landed, path sets verified identical** against the local bundle —
0 missing, 0 extra. Per directory: `per_item_outputs` 97 (of which **88 cell
JSONLs**), `reproduction` 85, `h3` 12, `archives` 6, `atlas` 4, `audit` 2,
`certification` 1, root 2. The Hub adds `.gitattributes`, hence 210 remote.

Confirmed **from an unauthenticated client**, not the authoring session:
`private: False`, `gated: False`, `license: cc-by-4.0` registered in the repo
metadata *and* as the hub tag `license:cc-by-4.0`. The dataset viewer resolves
`configs: per_item_outputs -> per_item_outputs/**/*.jsonl` (splits `failed: []`,
100 rows load). `is-valid` lags the visibility flip by a few minutes and can
report `viewer: false` while rows demonstrably load — trust `/first-rows`, not
the flag.

**Uploaded private, then flipped public.** Private→public is a toggle;
public→private after indexing undoes nothing. Note the viewer cannot be checked
while private on a non-PRO account, so that verification necessarily follows the
flip.

**The token trap — check the scope BEFORE uploading, not by watching for a 403.**
The stored `Phoenix Cluster` token was fine-grained `['repo.content.read']`. A
330 MB upload would have failed partway. `HfApi().whoami()` reports
`auth.accessToken.role` and any fine-grained permission list; read it first. The
upload used a **separate write token, revoked afterwards** — `Phoenix Cluster` is
the *jobs'* credential for gated weights, and widening it would leave every SLURM
job running with account-wide write.

Also: the interactive `hf auth login` prompt needs a real TTY. Under a
non-interactive harness `getpass` aborts rather than echoing the token. Run it in
a normal terminal, or edit `~/.cache/huggingface/token` directly — never pass
`--token` on a command line, which records the secret in shell history.

### After the identifiers exist

Fill the **version DOI** as canonical into `paper/sections/artifacts.tex` and
`paper/sections/appendix_artifacts_detail.tex`, with the HuggingFace URL as a
clearly-marked secondary convenience link. Then arXiv — nothing reaches arXiv
with a placeholder where §11 promises a release.

---

## ✅ DECIDED 2026-07-27 — option (b): delete from HEAD, publish with history intact

**Amogh read `paceship-application.md`, `handoffv1.md` and
`compression-eval-proposal-v2.md` on 2026-07-27 and chose option (b).** The
three documents are deleted from HEAD; the history is published unrewritten.
The account below is kept as the record of what was decided against.

### Reasoning

**1. The commit history is load-bearing evidence for \S3.** Three hashes are
cited as proof that preregistration preceded analysis, and all three are
verified as of this decision:

| Commit | Date | What it froze |
|---|---|---|
| `b74fd58` | 2026-07-15 19:00 | The three registration documents (mini-grid, atlas mining, audit) |
| `f06348f` | 2026-07-15 19:18 | The 59-pair atlas manifest, **before any flip analysis** |
| `715a7ce` | 2026-07-15 22:35 | The reconciled 17-claim audit table, **before the verdict stage** |

These are what make *"the protocol was frozen before the analysis it governs"* a
checkable fact rather than an assertion. **This paper faults 17 sources for
precisely that distinction** — asserting a property whose evidence a third party
cannot inspect. Publishing the audit while destroying our own audit trail would
reproduce the failure the paper is about.

**2. A rewrite would invalidate the hashes it needs to preserve — all of them.**
`git filter-repo` rewrites every commit downstream of the first one it touches.
Verified 2026-07-27: **all three documents enter at `a8092df`, which is commit
\#1 of 178 — the root commit.** So the rewrite is not merely "early enough to
land before the registration commits" (they sit at \#9, \#12 and \#17). It would
rewrite **every commit in the repository**, invalidating every hash this project
has ever cited, in the paper and in every signed decision record. There is no
version of the rewrite that preserves the evidence.

**3. Accepted residual exposure, stated rather than minimised.** The three
documents remain reachable in history, carrying enrollment status, expected
graduation, employment background, and **a graduation-year inconsistency between
two of them (2028 vs 2029)**.

There are **no credentials** anywhere in history (606 blobs scanned, zero hits),
so nothing requires revocation. What remains is personal and site information of
low severity, knowingly accepted in exchange for an auditable freeze timeline.

---

## Amendment, 2026-07-27 — two further exposures, measured and accepted

**Added after the pre-flight. Neither was covered by the reasoning above, and
neither is removable by deleting files.** Both are recorded here so that
publishing is a decision rather than a default.

### (i) Cluster identifiers are in 48 tracked files, not ~10

The superseded option list below estimated "~10 tracked files". **That estimate
was wrong by roughly a factor of five.** Measured across the tree after the
deletion commit:

| Identifier | Tracked files |
|---|---:|
| `asingh3206` (username) | 48 |
| absolute `/storage/...` paths | 44 |
| `hcoda1` (home-path element) | 38 |
| `atl1-*` (compute node names) | 37 |
| `paceship-compressedlm` (charge account) | 6 |
| `login-phoenix` | 2 |

Concentrated in `results/receipts/*.json` (44 build receipts),
`scripts/slurm/*.sbatch`, and six operational documents under `docs/`.

### (ii) 158 of 180 commits carry the cluster hostname in the committer identity

```
72  asingh3206@login-phoenix-gnr-3.pace.gatech.edu
64  asingh3206@login-phoenix-gnr-2.pace.gatech.edu
22  amogh.singh130@gmail.com
17  asingh3206@login-phoenix-gnr-4.pace.gatech.edu
 5  asingh3206@login-phoenix-gnr-1.pace.gatech.edu
```

The original reasoning said the author's email is the committer on every commit.
**It is more specific than that:** 158 commits pair the username with a *named
login host*, and GitHub displays that address beside every commit in its UI.
Removing it means rewriting authorship on all 180 commits — the same rewrite
ruled out above, for the same reason.

### Why the bundle is scrubbed and the repository is not

This is the obvious question a reader will ask, and the answer is that they are
**different artifacts with different jobs**, not an inconsistency.

- **The published bundle is a dataset.** It is downloaded, mirrored, re-hosted
  and cited by people with no connection to this project or this cluster. Site
  identifiers in it are pure noise — they carry no scientific content, they
  cannot be verified by anyone outside the institution, and every one of them
  would propagate into every mirror. So the bundle is scrubbed to placeholders,
  with `reproduction/REDACTIONS.json` stating the rules (and deliberately *not*
  the mapping — see incident 27).
- **The repository is an operational record.** Its value is that it shows what
  was actually run: `sbatch` lines with the real account, receipts naming the
  real nodes, paths matching the real filesystem. Scrubbing those would make the
  reproduction package internally inconsistent with the incident log and the
  signed decision records that cite them, and would turn a checkable operational
  history into a sanitised narrative — which is the failure mode this paper is
  about.
- **The severity difference is real, not asserted.** A charge account, a home
  path and a login hostname are not secrets, are not credentials, and grant
  nothing to anyone who reads them. What they cost is a small amount of
  institutional attribution that the author's name on the paper already
  discloses.

**Conclusion: accepted, both of them.** The scrub boundary is drawn where it is
on purpose — the artifact that travels gets placeholders, the artifact that
documents gets the truth.

---

## The decision that was made against (kept for the record)

**Superseded 2026-07-27 by the decision above.**

The tagged GitHub release publishes the repository, and a public repo exposes its
**full history**, not just the tagged tree. Deleting a file now does not remove
it from the 174 commits behind it.

**Good news first: there are no credentials anywhere.** Every blob in history
(606 scanned) was checked for HF/API tokens, GitHub PATs, AWS keys and private
keys. **Zero hits.** Nothing has to be revoked.

What is in history, and in the current tree, is:

1. **Three root-level documents that are not scientific artifacts** and contain
   personal information:

   | File | Contains |
   |---|---|
   | `paceship-application.md` | Compute-grant application: full name, `@gatech.edu` address, enrolment status, expected graduation, personal GitHub handle |
   | `handoffv1.md` | Personal background, employment, a second (conflicting) graduation year |
   | `compression-eval-proposal-v2.md` | Name and `@gatech.edu` address |

2. **Cluster identifiers** across ~10 tracked files — charge account, username,
   absolute home/scratch paths, login and compute hostnames.

Three options:

- **(a) Publish a fresh public repo from a curated tree** (single commit, or a
  squashed history), keeping the private repo as the working one.
  *Cleanest, and it costs the public commit history — which for a preregistration
  project is a real loss, since the freeze timeline is part of the argument.*
- **(b) Make the existing repo public after deleting the three documents and
  scrubbing identifiers.** *Keeps the commit history, which corroborates the
  freeze dates. Accepts that the deleted content stays reachable in history.*
- **(c) Publish a curated public repo whose history is preserved from the freeze
  commits onward**, with the three documents removed via history rewrite.
  *Most work; keeps the part of the history that matters.*

**My recommendation is (b), with the three documents deleted.** The scrubbed
identifiers are low-severity — a charge account and a cluster hostname are not
secrets, and the paths reveal nothing exploitable. The commit history is
load-bearing evidence for §3: it is what shows `PREREGISTRATION.md` was frozen
before the analyses it governs. Option (a) discards that to remove information
that is, at worst, mildly embarrassing. But the three personal documents are
yours and the graduation-year discrepancy between two of them is the kind of
thing a reader notices — so my recommendation is contingent on you being
comfortable that they remain in history.

If you prefer (a) or (c), say so and I will prepare the curated tree.

---

## What was already checked

- **Secret scan:** clean. No credentials in the working tree or in any of 606
  historical blobs. Every site identifier in the staged bundle is replaced;
  a residual scan over all 209 files returns nothing.
- **Archive integrity:** both sealed tarballs verify against their recorded
  `.sha256`, and a full extract-and-rehash reconciles **96 of 96 files** against
  the per-file manifests, **88 of them cell JSONLs**.
- **Extraction integrity:** the extracted `per_item_outputs/` copy hashes
  **96/96** against the archive manifests, so the usable copy and the sealed copy
  are provably the same bytes.
- **Frozen claim table:** `audit/audit_claim_table.csv` hashes to
  `842b9756d668618374c710f97637311b70ac7278e8b74c06960e651fc5af7b15`, matching
  the value recorded in the signed `docs/AUDIT_VERDICTS_2026-07-20.md`.
- **Licensing boundary:** no raw upstream S1 per-item data is in the bundle. Only
  our derived per-cell statistics, with the re-derivation path documented.
- **Redaction record:** `reproduction/REDACTIONS.json` states the rules without
  publishing the reverse mapping.

---

# Pre-flight, run 2026-07-27 (Part 2.1)

## Bundle — all green

| Check | Result |
|---|---|
| `SHA256SUMS` at the release path | **208/208 OK, 0 failed** (209 files, the 209th being `SHA256SUMS` itself) |
| Both sealed archives vs their `.sha256` | **OK / OK** |
| Extracted copy vs archive per-file manifests | **96/96, 0 mismatches** |
| Dataset card | `README.md` **at bundle root**, YAML frontmatter is the first bytes, `license: cc-by-4.0` present |
| Residual identifier scan, all 209 files | **CLEAN — no hits** |

## Repository — what becomes public

290 tracked files, ~37 MB, **no untracked files at all**. `paperdraft1.pdf` is
gone and was never committed.

**`results/` cell data is correctly excluded.** `.gitignore` line 9 is
`results/*` with an explicit allowlist of ~40 exceptions. No loose `.jsonl` is
tracked anywhere; the only tracked JSONLs are ten small synthetic fixtures under
`packaging/tests/fixtures/`. The repo does carry the two **sealed run tarballs**
(`minigrid_run_20260722.tar.gz`, `escalation_run_20260726.tar.gz`, ~25 MB
combined), which is deliberate and required by the preservation convention —
compressed archives, not the 304 MB of extracted JSONLs, which go to
HuggingFace.

## ⚠️ Two exposures the recorded decision does not cover

The decision above accepts the residual exposure **of the three deleted
documents**. These two are separate, and neither is removable by deleting files.

### 1. Cluster identifiers are in 48 tracked files, not ~10

An earlier draft of this checklist estimated "~10 tracked files". **That estimate
was wrong.** Measured after the deletion commit:

| Identifier | Tracked files |
|---|---:|
| `asingh3206` (username) | 48 |
| absolute `/storage/...` paths | 44 |
| `hcoda1` (home path element) | 38 |
| `atl1-*` (compute node names) | 37 |
| `paceship-compressedlm` (charge account) | 6 |
| `login-phoenix` | 2 |

Concentrated in `results/receipts/*.json` (44 build receipts),
`scripts/slurm/*.sbatch`, and six operational docs. **The published bundle
scrubbed all of these; the repository does not.** Severity is the same as
already accepted — a charge account and cluster hostnames are not secrets and
nothing here is exploitable — but the *volume* is an order of magnitude above
what was previously recorded, so it is restated here for an explicit call rather
than inherited silently.

### 2. The committer identity carries the cluster hostname on 158 of 180 commits

```
72  asingh3206@login-phoenix-gnr-3.pace.gatech.edu
64  asingh3206@login-phoenix-gnr-2.pace.gatech.edu
22  amogh.singh130@gmail.com
17  asingh3206@login-phoenix-gnr-4.pace.gatech.edu
 5  asingh3206@login-phoenix-gnr-1.pace.gatech.edu
```

The decision above notes the author email is the committer on every commit.
**It is more specific than that:** 158 commits carry `username@login-node.pace.
gatech.edu`, which pairs the username with a named login host and is displayed
next to every commit in GitHub's UI. Removing it requires rewriting authorship
on all 180 commits — the same rewrite ruled out above, for the same reason.

**Neither of these blocks publication if accepted.** Both are recorded so the
decision is made rather than defaulted into.

## Cosmetic: five dangling references

`CODING_AGENT_HANDOFF_2026-07-10.md`, `KAGGLE_CHAT_HANDOFF_2026-07-10.md`,
`KAGGLE_RUN_COMPLETION_HANDOFF_2026-07-10.md`, `PILOT.md` and
`paper-proposal-v3.md` still reference the deleted paths; one is a markdown link
that will render as a 404. They are archival handoff documents. Not rewritten —
noted so it is a choice.

`paper-proposal-v3.md` was checked as a possible fourth personal document: it
carries only the authorship line "Amogh Singh, Georgia Tech", which is
publication metadata, not personal data.
