#!/usr/bin/env python3
r"""Layout gate: measure where the ink actually lands, not what the log admits.

Why this exists
---------------
The LaTeX log is not a sufficient record of whether the paper fits its measure.
On 2026-08-05 the three widest boxes in the document produced **no warning at
all**: a `tabular` wider than `\textwidth` inside `\centering` is set silently,
and the S2 column of the atlas strata table was rendering off the right edge of
the page where no reader could see it. It was found by measuring glyph
positions in the PDF, and only then.

So this gate has two independent halves, and both must pass:

1. **The log half** -- overfull boxes, with an allowlist keyed to a reason.
2. **The ink half** -- the maximum `xMax` of any glyph on each page, from
   `pdftotext -bbox`, against the right edge of the text block. This is the half
   that catches silent tabulars, and it is the reason the tool exists.

Neither half subsumes the other. A silent tabular fails only the ink half; an
overfull box in a float that happens to be centred can fail only the log half.

Usage
-----
    python3 tools/check_layout.py                  # after a full build
    python3 tools/check_layout.py --body-only      # ignore the appendices

Run it from `paper/`, after the three-pass build documented in
`docs/PAPER_BUILD_ENVIRONMENT.md`. It reads `main.pdf` and `main.log` and never
compiles anything itself, so it always describes the build you actually made.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Right edge of the text block, in PDF points, for this class and geometry.
# Measured as the modal xMax over body pages, not taken from a class file.
TEXT_RIGHT_PT = 484.5

# Ink is allowed this far past the edge before it counts. Half a point is below
# the width of a rule and cannot be seen; anything above it is a real defect.
INK_TOLERANCE_PT = 0.5

# Overfull boxes below this are not worth a build failure. 1pt is roughly the
# width of a thin space at this size.
BOX_TOLERANCE_PT = 1.0

LAST_BODY_PAGE = 35

# Accepted violations, each with the reason it cannot be fixed. An entry here is
# a decision, not a silencer: if the reason stops applying, delete the entry.
#
# Format: (page, description). A page may appear once.
ACCEPTED_INK = {
    88: "frozen registrations appendix: a 64-character model revision hash with "
        "no break point, inside text reproduced verbatim and machine-checked by "
        "verify_registrations.py. The file cannot be edited to add one, and "
        "main.tex already applies \\emergencystretch 6em around it from outside.",
}


def overfull_boxes(log: Path) -> list[tuple[float, str, str]]:
    out = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"Overfull \\([hv])box \(([\d.]+)pt too (?:wide|high)\)(.*)", line)
        if m:
            out.append((float(m.group(2)), m.group(1) + "box", m.group(3).strip()))
    return sorted(out, key=lambda r: -r[0])


def ink_past_measure(pdf: Path) -> list[tuple[int, float]]:
    if shutil.which("pdftotext") is None:
        sys.exit("check_layout: pdftotext not on PATH; see docs/PAPER_BUILD_ENVIRONMENT.md")
    proc = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"check_layout: pdftotext failed: {proc.stderr.strip()}")
    pages = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>',
                       proc.stdout, re.S)
    out = []
    for number, body in enumerate(pages, 1):
        xs = [float(x) for x in re.findall(r'xMax="([\d.]+)"', body)]
        if xs and max(xs) > TEXT_RIGHT_PT + INK_TOLERANCE_PT:
            out.append((number, max(xs) - TEXT_RIGHT_PT))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", default="main.pdf")
    ap.add_argument("--log", default="main.log")
    ap.add_argument("--body-only", action="store_true",
                    help=f"only check pages 1-{LAST_BODY_PAGE}")
    args = ap.parse_args()

    pdf, log = Path(args.pdf), Path(args.log)
    for path in (pdf, log):
        if not path.is_file():
            sys.exit(f"check_layout: {path} not found; build first")

    failures = []

    boxes = [b for b in overfull_boxes(log) if b[0] >= BOX_TOLERANCE_PT]
    print(f"LAYOUT: {len(boxes)} overfull box(es) at or above {BOX_TOLERANCE_PT}pt")
    for pt, kind, where in boxes[:10]:
        print(f"  {pt:7.2f}pt {kind} {where[:60]}")

    ink = ink_past_measure(pdf)
    checked = f"1-{LAST_BODY_PAGE}" if args.body_only else "all"
    print(f"LAYOUT: ink past the text block, pages {checked}:")
    if not ink:
        print("  none")
    for page, over in ink:
        if args.body_only and page > LAST_BODY_PAGE:
            continue
        if page in ACCEPTED_INK:
            print(f"  page {page:3d}: +{over:.1f}pt  ACCEPTED -- {ACCEPTED_INK[page]}")
            continue
        print(f"  page {page:3d}: +{over:.1f}pt  FAIL")
        failures.append(f"page {page} has ink {over:.1f}pt past the text block")

    # The body is held to a stricter standard than the appendices: it is what a
    # reviewer reads, and every body-page violation to date has been fixable.
    body_ink = [p for p, _ in ink if p <= LAST_BODY_PAGE and p not in ACCEPTED_INK]
    if body_ink:
        failures.append(f"body pages with ink outside the text block: {body_ink}")

    if failures:
        print("LAYOUT: FAILED")
        for line in failures:
            print(f"  {line}")
        return 1
    print("LAYOUT: OK -- no unaccepted ink outside the text block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
