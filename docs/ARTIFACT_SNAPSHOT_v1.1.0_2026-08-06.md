# Clean artifact snapshot v1.1.0: prepared, verified, NOT published

**Status: built and fully verified locally. NOT uploaded.** The publish step is
blocked on credentials, not on readiness. See §7.

Built 2026-08-06 from the frozen manuscript tree
(`docs/MANUSCRIPT_FREEZE_2026-08-06.json`, collective sha256 `42a3d76e…e746ce`).

## 1. The archive

| | |
|---|---|
| location | `~/scratch/flipeval_export/flipeval-v1.1.0-artifact.tar.gz` |
| size | 18 MB |
| files | 325 |
| archive sha256 | `247eedf883efdda6a5b8684990505b56e20fe7c6d160646fe71bda80c7d266ad` |
| per-file manifest | `flipeval-v1.1.0-MANIFEST.sha256`, 330 lines |
| round-trip | extracted and re-hashed: **all files match** |

Built with `git archive HEAD` so it carries **no git history**, then reduced by
the exclusion list in §2. The tarball is deterministic (`--sort=name`, fixed
mtime, numeric owner 0:0), so rebuilding it from the same tree reproduces the
same digest.

**This is why the branch is not pushed.** The history still contains the private
source tarball in earlier commits, and a signed amendment cites commit
`bb45528`, so the history cannot be rewritten either. Exporting the tree without
history is the way past that, and it is what this archive is.

## 2. What was removed, and why

| removed | reason |
|---|---|
| `.git/` (by construction) | the private source tarball lives in earlier commits |
| `CLAUDE.md`, `AGENTS.md` | agent guardrails, internal process |
| `docs/SESSION_HANDOFF_*`, `docs/*HANDOFF*`, root `*_HANDOFF_*.md` | internal handoffs between working sessions |
| `.claude/` | worktree and agent metadata |
| `kaggle/`, `notebooks/` | scratch work, not part of the release |
| `paper/READING_COPY.md`, `paper/OUTLINE.md` | generated / planning artifacts |
| `__pycache__/`, `*.pyc` | build residue |

350 exported → **325 shipped**.

## 3. Leak scan, all clean

| check | result |
|---|---|
| full-text captures of audited sources | **none** (Option A intact) |
| files named `*capture*`, `*fulltext*`, `sources/*.html|pdf` | **none** |
| credentials, API keys, private keys, `hf_*` / `ghp_*` tokens | **none** |
| internal handoff or session documents | **none** |
| git metadata | only `.gitignore` |

### One finding: local absolute paths, in 45 files

`/storage/home/hcoda1/0/asingh3206/…` appears in 45 files. **Shipped code is
path-clean** — nothing under `scripts/`, `flipeval/`, `pilot_eval/`, `tests/` or
`configs/` hardcodes a local path, so there is no portability defect.

The 45 are:

| where | count | what they are |
|---|---|---|
| `results/receipts/*.json` | 40 | sealed per-build provenance recording where each quantized model was written |
| `results/calibration_receipts.json` | 1 | sealed calibration provenance |
| `container/flipeval.sif.sha256` | 1 | image digest record |
| `docs/*.md` | 3 | dated environment and onboarding notes |

**These were deliberately NOT scrubbed.** The receipts are sealed provenance
artifacts and part of the confirmatory record; rewriting them to tidy a path
would alter a sealed record to improve appearances, which is exactly what this
project's conventions forbid.

What they disclose is the cluster username `asingh3206` and a directory layout.
For a **named preprint** that is not a de-anonymisation risk, since the author is
named on the paper. **For a blind submission artifact it would be**, and that is
the author's decision, not mine. If scrubbing is wanted it should be a dated,
recorded transformation with the originals retained, not a silent rewrite.

## 4. Reproduction checks run FROM the export

Run against the extracted archive, not the working tree.

| check | result |
|---|---|
| `churn_ratio.py --check` | **OK**, 25 printed values |
| `check_paper.py` | **OK**, 0 dangling refs, 0 unresolved cites |
| `STALE_CLAIM` | **OK** |
| `gen_denominator_macros.py --check` | **OK**, all three layers |
| `gen_audit_tables.py --check` | **OK**, 17 rows byte for byte |
| `verify_registrations.py` | **OK**, 7,103 words |
| `measure_abstract.py` | 1879 / 1920, margin 41 |
| `PREPACE_FREEZE` **content** check | **90 of 90 files match, 0 differ, 0 missing** |
| in-image pytest | **342 passed, 6 failed** |

### The six failures are a real property of the archive, and are expected

All six are `tests/test_freeze_prepace.py`. Root cause confirmed from the
traceback, not guessed: `scripts/freeze_prepace.py::build_manifest` calls
`git rev-parse HEAD`, and a history-free export is not a git repository.

`freeze_prepace.py --verify` fails from the export for the same reason, with
`frozen source commit is not an ancestor of HEAD`.

**This does not mean the fingerprint is unverifiable from the archive.** The
*content* half verifies perfectly: all 90 fingerprinted files match their
recorded sha256. Only the git-ancestry half cannot run, and it is meaningless
outside a repository by design.

**Recommendation:** ship as-is and say so in the release notes. The alternative,
dropping `freeze_prepace.py` and its tests from the archive, would remove the
tool that documents the source fingerprint in order to make a test count look
clean, which is the wrong trade.

## 5. Network verification, unauthenticated

Performed with plain `curl`, no session and no token, which is what a logged-out
reader gets.

| target | result |
|---|---|
| `https://doi.org/10.5281/zenodo.21708923` (version DOI) | **200**, resolves |
| `https://doi.org/10.5281/zenodo.21708922` (concept DOI) | **200**, resolves |
| `https://github.com/amoghsingh130/flipeval` | **200** |
| `https://huggingface.co/datasets/AmoghSingh123/flipeval-artifacts` | **200** |

Both URLs asserted in the paper resolve for a logged-out reader.

### Zenodo v1.0 record

`title: amoghsingh130/flipeval: FlipEval v1.0.0`, `version: v1.0.0`,
`access: open`, 1 file in the record. It is live and open, and it still
describes what the paper cites.

### Hugging Face file count, reconciled

The API reports **210** entries. The release checklist records **209**. These
agree, and the checklist already explains why: the Hub adds `.gitattributes`.

```
210 API entries − 1 (.gitattributes added by the Hub) = 209 released files
209 = 208 payload + SHA256SUMS  (SHA256SUMS confirmed present)
payload by type: 88 jsonl, 64 json, 15 md, 10 sbatch, 9 yaml, 7 csv, 5 lock, 3 sha256
```

`private: false`, last modified 2026-07-30. **The 88 JSONL files are the per-item
outputs the paper's §Artifacts claims**, and this is the first time that count
has been confirmed against the live mirror rather than against the local tarballs.

## 6. What is still v1.0 and would become v1.1.0

The published Zenodo record is **v1.0.0**. This archive is the
**manuscript-matched** tree: it includes the frozen paper sources, the churn-ratio
generator and its 23 tests, the layout gate, the audit protection ledger, and the
two-panel audit table — none of which existed at v1.0.0.

Publishing it as v1.1.0 under the existing concept DOI `10.5281/zenodo.21708922`
would mint a new version DOI and leave v1.0.0 and its DOI untouched, which is the
correct Zenodo versioning behaviour and preserves every existing citation.

## 7. Why it is not published, precisely

**No Zenodo credentials exist on this machine.** No token file
(`~/.zenodo_token`, `~/.config/zenodo`), no Zenodo environment variable, and no
upload CLI on `PATH`. The deposition cannot be created from here.

Independently of that: minting a DOI is **permanent and not reversible**. A
Zenodo version DOI cannot be withdrawn once created, and the archive would become
part of the citable record immediately. That is a decision to take deliberately
with credentials in hand, not one to automate.

**Everything up to the upload is done and verified.** What remains for the author:

1. Create a new version under concept DOI `10.5281/zenodo.21708922`.
2. Upload `flipeval-v1.1.0-artifact.tar.gz`
   (sha256 `247eedf883efdda6a5b8684990505b56e20fe7c6d160646fe71bda80c7d266ad`)
   and `flipeval-v1.1.0-MANIFEST.sha256`.
3. Set version `v1.1.0`, note that it is the manuscript-matched tree, and record
   the six git-dependent test failures in the release notes per §4.
4. Decide the local-path question in §3 before publishing if a blind artifact is
   also wanted.
5. Update `\versiondoi` in `paper/main.tex` to the new version DOI. **That is a
   manuscript change and reopens the freeze**, so do it once, deliberately, and
   re-freeze.

Step 5 is the one with a trap: the paper currently cites the v1.0.0 version DOI,
and if a v1.1.0 is published without updating it, the paper points at an archive
that is not the one it describes.
