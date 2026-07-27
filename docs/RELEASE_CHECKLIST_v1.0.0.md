# Artifact Release Checklist — v1.0.0

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

## Order of operations — the DOI must exist before the paper cites it

### 1. GitHub release of `flipeval`, Apache-2.0, tag `v1.0.0`

**⚠️ Decide this first — see "Open decision" below.** The repository is currently
private and its history contains material that should not go public as-is.

```bash
# after the repo-history decision is made and any exclusions are applied
git tag -a v1.0.0 -m "FlipEval v1.0.0 — paper release"
git push origin v1.0.0
gh release create v1.0.0 --title "FlipEval v1.0.0" \
  --notes "Companion code release for 'Certifying Compressed Language Models'. Artifacts: <DOI>"
```

Confirm `LICENSE` is Apache-2.0 at the tagged commit before tagging.

### 2. Zenodo DOI, auto-minted from the GitHub release

**This is the least-effort path and the one to use.** Zenodo watches the repo and
mints a DOI automatically when a release is published — no manual upload.

1. Sign in to <https://zenodo.org> with GitHub.
2. Settings → GitHub → flip the toggle **ON** for `AmoghSingh123/flipeval`.
3. **The toggle must be on _before_ step 1's release is published.** Zenodo only
   sees releases created after the switch. If the release already exists, delete
   and re-publish it, or fall back to a manual Zenodo upload.
4. Zenodo issues two DOIs: a **concept DOI** (all versions) and a
   **version DOI** (v1.0.0 specifically). **Cite the version DOI in the paper.**
5. Edit the Zenodo record: license CC-BY-4.0 for data, author ORCID, and the
   title used in the dataset card.

### 3. HuggingFace dataset repo

One repo, public, **not gated**.

```bash
huggingface-cli login
huggingface-cli repo create flipeval-artifacts --type dataset      # under AmoghSingh123
cd <PROJECT>/asingh3206/release/flipeval-artifacts-v1.0.0
git init && git lfs install
git lfs track "*.tar.gz" "*.jsonl"
git remote add origin https://huggingface.co/datasets/AmoghSingh123/flipeval-artifacts
git add -A && git commit -m "FlipEval artifacts v1.0.0"
git push -u origin main
git tag v1.0.0 && git push origin v1.0.0
```

`git lfs track` matters — `per_item_outputs/` is 304 MB and individual JSONLs
exceed HF's non-LFS limit.

Then, in the repo README (already written, at the bundle root), replace
`TODO-ZENODO-DOI` with the version DOI from step 2.

**Post-upload check:** the dataset viewer renders `per_item_outputs/`, and

```bash
sha256sum -c SHA256SUMS
```

passes on a fresh clone.

### 4. Fill the identifiers into the paper

Two files, both currently carrying `\TODO`:

- `paper/sections/artifacts.tex` — the release paragraph
- `paper/sections/appendix_artifacts_detail.tex` — §"Metadata and identifiers"

**§11 cites the DOI as canonical. The HuggingFace URL appears as a secondary
convenience link, clearly marked as such.**

### 5. arXiv

Only after 1–4. Nothing reaches arXiv with a placeholder where §11 promises a
release.

---

## ⛔ Open decision — the repository's history

**This needs your call, and it blocks step 1 only.**

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
