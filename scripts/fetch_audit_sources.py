#!/usr/bin/env python3
"""Re-fetch the 17 audited sources and check them against the recorded hashes.

WHY THIS EXISTS. The full-text captures of the audited sources are NOT
redistributed: four of them (Meta AI, NVIDIA, and two vLLM pages) grant no
redistribution right, and arXiv's default licence permits arXiv to distribute
rather than third parties. What ships instead is the URL, the pinned version,
the sha256 and this script, so a reader can rebuild the corpus themselves and
verify it is the same corpus the audit read.

WHAT "THE SAME" MEANS HERE, AND WHERE IT DOES NOT HOLD. A hash pins bytes, and
only some of these sources serve stable bytes:

  * arXiv (R01-R07) are fetched as ar5iv full-text HTML at a pinned version.
    This is the retrieval that reproduces the recorded hash. The PDF, the
    extracted text and the /abs page all hash differently; do not substitute
    them.
  * Hugging Face model cards (R08-R10, R15-R17) are fetched as the RAW
    README.md at a PINNED COMMIT, so they are reproducible indefinitely.
  * R12 is raw GitHub Markdown from `main`, which moves. Drift here means the
    upstream doc changed, not that the audit was wrong.
  * R11 (Meta AI blog) serves per-response dynamic content: two fetches seconds
    apart differed by 9 bytes when this was checked on 2026-07-31. Its recorded
    hash was NEVER a valid fingerprint and it is reported as EXPECTED-DRIFT, not
    as a failure. This is a limitation of the source, disclosed rather than
    papered over.
  * R13 is subtler, and the manifest's own status column says so. A hash for it
    IS recorded, so a re-fetch can be checked against the archived capture. What
    is missing is a baseline from BEFORE that capture, so the capture itself was
    never independently corroborated. Verifying against it proves you have the
    same bytes the audit read; it does not prove those bytes were the page as it
    stood when the claim was extracted.

Every source therefore verifies against the archive, which is what `--offline`
checks. A LIVE run is weaker: R11 will drift by construction, R12 may drift
whenever upstream edits the doc, and R13 verifies only in the limited sense
above. Distinguishing those cases is the whole job of this script; one that
printed "17/17 OK" against live fetches would be lying.

NO DEFAULTS, BY PROJECT RULE. Every path argument is required. The same hazard
that motivated required `--atlas`/`--output` on the analysis entry points and
required grid variables on the job scripts applies here: a defaulted run
completes, exits 0, and certifies the wrong corpus.

Standard library only, and 3.9-compatible: this has to run on the Phoenix login
node, which has python 3.9.21 and no third-party packages.
"""

import argparse
import csv
import hashlib
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = "flipeval-audit-source-fetcher/1.0 (research reproducibility check)"
TIMEOUT = 60

# Sources whose bytes are not stable, with the reason. Drift on these is
# reported as expected and does not fail the run.
UNSTABLE = {
    "R11": "server renders per-response content; recorded hash was never a "
           "valid fingerprint (two fetches 2026-07-31 differed by 9 bytes)",
    "R12": "tracks GitHub `main`, which moves; drift means the upstream doc "
           "changed",
}


def arxiv_id(url):
    m = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+)", url)
    return m.group(1) if m else None


def hf_repo(url):
    m = re.search(r"huggingface\.co/([^/]+/[^/?#]+)", url)
    return m.group(1) if m else None


def hf_commit(pinned):
    m = re.search(r"HF commit ([0-9a-f]{6,})", pinned)
    return m.group(1) if m else None


def github_raw(url):
    m = re.search(r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", url)
    if not m:
        return None
    owner, repo, ref, path = m.groups()
    return "https://raw.githubusercontent.com/%s/%s/%s/%s" % (owner, repo, ref, path)


def resolve(claim, url, retrieval, pinned):
    """Map a source's recorded retrieval method to the URL that reproduces it.

    Returns (fetch_url, note). Raises if the method and the URL disagree, which
    would mean the manifest and the frozen claim table have drifted apart.
    """
    if "ar5iv" in retrieval:
        aid = arxiv_id(url)
        if not aid:
            raise ValueError("%s: ar5iv retrieval but URL is not an arXiv abs "
                             "page: %s" % (claim, url))
        return "https://ar5iv.labs.arxiv.org/html/%s" % aid, "ar5iv full text"
    if "HF raw README" in retrieval:
        repo = hf_repo(url)
        if not repo:
            raise ValueError("%s: HF retrieval but URL is not a HF repo: %s"
                             % (claim, url))
        rev = hf_commit(pinned)
        if not rev:
            raise ValueError("%s: HF retrieval with no pinned commit in %r"
                             % (claim, pinned))
        return ("https://huggingface.co/%s/raw/%s/README.md" % (repo, rev),
                "pinned commit %s" % rev)
    if "raw.githubusercontent" in retrieval:
        raw = github_raw(url)
        if not raw:
            raise ValueError("%s: GitHub raw retrieval but URL is not a blob "
                             "URL: %s" % (claim, url))
        return raw, "GitHub raw, ref moves"
    if "curl live HTML" in retrieval:
        return url, "live page"
    raise ValueError("%s: unrecognised retrieval method %r" % (claim, retrieval))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True,
                    help="docs/audit_sources_manifest.tsv (REQUIRED, no default)")
    ap.add_argument("--claims", required=True,
                    help="docs/audit_claim_table.csv, frozen (REQUIRED, no default)")
    ap.add_argument("--out", required=True,
                    help="directory to write fetched sources to (REQUIRED)")
    ap.add_argument("--claim", action="append", default=None,
                    help="fetch only these claim ids; repeatable")
    ap.add_argument("--offline", action="store_true",
                    help="verify files already in --out; fetch nothing")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.manifest), delimiter="\t"))
    claims = {r["claim_id"]: r for r in csv.DictReader(open(args.claims))}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    wanted = set(args.claim) if args.claim else {r["claim"] for r in rows}
    verified = drifted = expected = unverifiable = failed = 0

    for row in rows:
        cid = row["claim"]
        if cid not in wanted:
            continue
        claim = claims.get(cid)
        if claim is None:
            print("%-4s FAIL          not in the frozen claim table" % cid)
            failed += 1
            continue

        try:
            url, note = resolve(cid, claim["source_url"], row["retrieval"],
                                row["pinned_version"])
        except ValueError as exc:
            print("%-4s FAIL          %s" % (cid, exc))
            failed += 1
            continue

        dest = out / row["file"]
        if args.offline:
            if not dest.exists():
                print("%-4s FAIL          %s absent (offline mode)" % (cid, dest.name))
                failed += 1
                continue
            body = dest.read_bytes()
        else:
            try:
                body = fetch(url)
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
                print("%-4s FAIL          %s (%s)" % (cid, exc, url))
                failed += 1
                continue
            dest.write_bytes(body)

        got = hashlib.sha256(body).hexdigest()
        want = row["sha256"].strip()

        if not want:
            print("%-4s NO-BASELINE   %s  (no hash was ever recorded; %s)"
                  % (cid, got[:16], note))
            unverifiable += 1
        elif got == want:
            print("%-4s VERIFIED      %s  (%s)" % (cid, got[:16], note))
            verified += 1
        elif cid in UNSTABLE:
            print("%-4s EXPECTED-DRIFT %s vs %s  (%s)"
                  % (cid, got[:16], want[:16], UNSTABLE[cid]))
            expected += 1
        else:
            print("%-4s DRIFT         %s vs recorded %s  (%s)"
                  % (cid, got[:16], want[:16], note))
            drifted += 1

    print("\nFETCH_AUDIT_SOURCES: %d verified, %d drifted, %d expected-drift, "
          "%d unverifiable, %d failed"
          % (verified, drifted, expected, unverifiable, failed))
    # A fetch failure is an error. Unexplained drift is an error, because it
    # means the corpus a reader rebuilds is not the corpus the audit read.
    # Expected drift and the missing baseline are disclosed limitations, not
    # failures, and are listed above rather than hidden in the exit code.
    return 1 if (failed or drifted) else 0


if __name__ == "__main__":
    sys.exit(main())
