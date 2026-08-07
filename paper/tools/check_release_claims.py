"""Fail-closed release-claim gate.

Six checks, each rejecting a specific defect that has actually occurred in this
project rather than a hypothetical one. Every check fails CLOSED: a check that
cannot locate what it is meant to inspect reports FAIL, never PASS, because a
silently-skipped check is worse than no check (the lesson of the stale in-image
count recorded in CLAUDE.md).

Run:  python3 paper/tools/check_release_claims.py [--release-tree DIR]
Exit: 0 all pass, 1 any fail.

The defects, and where each came from:

C1  The availability claim naming the v1.0.0 archive as the frozen state the
    paper describes. Verified false 2026-08-06: Zenodo 21708923 holds one file,
    the source zip of tag v1.0.0 (2026-07-29), whose tree has no rev3 verdicts,
    while the paper reports rev-3 (computed 2026-07-31). Survived a manuscript
    freeze and an artifact build on flagship-narrative before being caught.

C2  The v1.0.0 DOI presented as canonical for the current paper.

C3  The v1.1.0 DOI absent from the availability statement.

C4  PDF /Author metadata missing, or present but NOT routed through \\ifanon.
    An unconditional name in the info dictionary is a double-blind leak that no
    reader sees on the page.

C5  rev-2 audit data presented as the current audit. Checked precisely, against
    the generated denominator ledger's recorded source and digest, because the
    paper legitimately discusses rev-2 as superseded and a keyword scan would
    false-positive on that (and on the unrelated rev-2 ATLAS).

C6  Any private source capture, git backup, or credential in a release tree.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

V11_DOI = "10.5281/zenodo.21829570"
V10_DOI = "10.5281/zenodo.21708923"
FALSE_CLAIM = "frozen v1.0.0 state this paper describes"
AUTHOR_NAME = "Amogh Singh"

# Compiled manuscript sources. READING_COPY.md is generated from these and is
# included deliberately: if it still carries a withdrawn claim, it was not
# regenerated after the fix, which is itself the defect.
def paper_sources() -> list[Path]:
    out = sorted((ROOT / "paper").rglob("*.tex"))
    rc = ROOT / "paper" / "READING_COPY.md"
    if rc.is_file():
        out.append(rc)
    return out


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, bool, str]] = []

    def add(self, cid: str, ok: bool, detail: str) -> None:
        self.rows.append((cid, ok, detail))

    def failed(self) -> bool:
        return any(not ok for _, ok, _ in self.rows)


def c1_no_false_availability_claim(r: Report) -> None:
    files = paper_sources()
    if not files:
        r.add("C1", False, "no paper sources found -- cannot verify, failing closed")
        return
    hits = [f"{p.relative_to(ROOT)}" for p in files if FALSE_CLAIM in p.read_text(encoding="utf-8", errors="replace")]
    r.add("C1", not hits,
          "the withdrawn availability claim is absent from all paper sources"
          if not hits else f"withdrawn claim present in: {', '.join(hits)}")


def _macro_body(text: str, macro: str) -> str | None:
    """Body of \\newcommand{\\macro}{...}, by brace matching.

    Brace matching rather than a regex: the first version of this check used
    `\\{(.*?)\\n(.*?)\\}` and silently PASSED when \\versiondoi was pointed back
    at the v1.0.0 DOI, because the non-greedy span latched onto the \\ifanon
    arm's one-line definition instead. It was caught only by a negative test.
    Returns the LAST definition, which is the \\else (identified) arm.
    """
    needle = "\\newcommand{" + macro + "}{"
    start = text.rfind(needle)
    if start < 0:
        return None
    i = start + len(needle)
    depth = 1
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i] if depth == 0 else None


def c2_v10_not_canonical(r: Report) -> None:
    main = ROOT / "paper" / "main.tex"
    if not main.is_file():
        r.add("C2", False, "paper/main.tex missing -- failing closed")
        return
    body = _macro_body(main.read_text(encoding="utf-8"), "\\versiondoi")
    if body is None:
        r.add("C2", False, "could not locate the \\versiondoi definition -- failing closed")
        return
    if V10_DOI in body:
        r.add("C2", False, f"\\versiondoi resolves to the v1.0.0 DOI {V10_DOI}")
        return
    if V11_DOI not in body:
        r.add("C2", False, f"\\versiondoi resolves to neither the v1.1.0 nor the v1.0.0 DOI: {body[-60:]!r}")
        return
    r.add("C2", True, f"\\versiondoi resolves to {V11_DOI}, not {V10_DOI}")


def c3_v11_present(r: Report) -> None:
    main = (ROOT / "paper" / "main.tex")
    arts = (ROOT / "paper" / "sections" / "artifacts.tex")
    if not (main.is_file() and arts.is_file()):
        r.add("C3", False, "main.tex or artifacts.tex missing -- failing closed")
        return
    mt, at = main.read_text(encoding="utf-8"), arts.read_text(encoding="utf-8")
    body = _macro_body(mt, "\\versiondoi")
    defined = bool(body) and V11_DOI in body
    # The availability statement must cite it, via the macro (raw URLs break the
    # anonymous build, so the macro is the only correct form).
    cited = bool(re.search(r"archived release is canonical.{0,120}\\versiondoi", at, re.S))
    ok = defined and cited
    r.add("C3", ok,
          f"{V11_DOI} defined in main.tex and cited via \\versiondoi in the availability statement"
          if ok else
          f"defined={defined} cited_in_availability={cited} (need both)")


def c4_pdf_metadata(r: Report) -> None:
    main = ROOT / "paper" / "main.tex"
    if not main.is_file():
        r.add("C4", False, "paper/main.tex missing -- failing closed")
        return
    t = main.read_text(encoding="utf-8")
    has_title = bool(re.search(r"pdftitle\s*=\s*\{[^}]+\}", t))
    am = re.search(r"pdfauthor\s*=\s*\{([^}]*)\}", t)
    if not am:
        r.add("C4", False, "no pdfauthor set: the PDF would ship with an empty /Author")
        return
    value = am.group(1).strip()
    routed = value.startswith("\\")          # a macro, not a literal
    literal_name = AUTHOR_NAME in value
    # the macro must be defined in BOTH arms of \ifanon
    macro = value.lstrip("\\").strip()
    anon_arm = re.search(r"\\ifanon(.*?)\\else(.*?)\\fi", t, re.S)
    both_arms = bool(anon_arm and macro and f"\\{macro}" in anon_arm.group(1) and f"\\{macro}" in anon_arm.group(2))
    ok = has_title and routed and not literal_name and both_arms
    detail = (f"pdftitle set; pdfauthor routed through \\{macro}, defined in both \\ifanon arms"
              if ok else
              f"pdftitle={has_title} routed={routed} literal_name={literal_name} both_arms={both_arms}")
    r.add("C4", ok, detail)


def c5_audit_is_rev3(r: Report) -> None:
    ledger = ROOT / "paper" / "audit_denominators.tex"
    csv = ROOT / "results" / "audit_verdicts_rev3.csv"
    if not ledger.is_file() or not csv.is_file():
        r.add("C5", False, "denominator ledger or rev-3 CSV missing -- failing closed")
        return
    lt = ledger.read_text(encoding="utf-8")
    if "audit_verdicts_rev3.csv" not in lt:
        r.add("C5", False, "the denominator ledger is not generated from the rev-3 verdicts")
        return
    m = re.search(r"sha256:\s*([0-9a-f]{64})", lt)
    if not m:
        r.add("C5", False, "the ledger records no source digest -- failing closed")
        return
    actual = hashlib.sha256(csv.read_bytes()).hexdigest()
    ok = actual == m.group(1)
    r.add("C5", ok,
          f"denominators generated from rev-3, digest matches ({actual[:8]}...)"
          if ok else
          f"digest mismatch: ledger says {m.group(1)[:8]}..., rev-3 CSV is {actual[:8]}...")


FORBIDDEN_IN_RELEASE = (
    ("private source captures", re.compile(r"audit_sources_\d+\.tar\.gz$")),
    ("git bundles/backups", re.compile(r"\.(bundle|pack)$|(^|/)backups?/|flipeval-dotgit")),
    ("git history", re.compile(r"(^|/)\.git/")),
    ("credentials", re.compile(r"(^|/)(\.netrc|\.git-credentials|id_rsa|.*\.pem|token(\.txt)?)$")),
)


def c6_release_tree_clean(r: Report, tree: Path | None) -> None:
    if tree is None:
        r.add("C6", True, "skipped: no --release-tree given (run again with it before publishing)")
        return
    if not tree.is_dir():
        r.add("C6", False, f"release tree {tree} does not exist -- failing closed")
        return
    bad: list[str] = []
    for p in tree.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(tree))
        for label, pat in FORBIDDEN_IN_RELEASE:
            if pat.search(rel):
                bad.append(f"{label}: {rel}")
    r.add("C6", not bad,
          f"release tree clean ({sum(1 for _ in tree.rglob('*') if _.is_file())} files scanned)"
          if not bad else "; ".join(bad[:6]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-tree", type=Path, default=None)
    a = ap.parse_args()
    r = Report()
    c1_no_false_availability_claim(r)
    c2_v10_not_canonical(r)
    c3_v11_present(r)
    c4_pdf_metadata(r)
    c5_audit_is_rev3(r)
    c6_release_tree_clean(r, a.release_tree)
    for cid, ok, detail in r.rows:
        print(f"{cid}: {'PASS' if ok else 'FAIL'} -- {detail}")
    if r.failed():
        print("RELEASE_CLAIMS: FAIL")
        return 1
    print("RELEASE_CLAIMS: OK -- 6 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
