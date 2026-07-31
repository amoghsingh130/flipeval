#!/usr/bin/env python3
"""Measure abstract.tex against the arXiv abstract-field limit.

The limit is 1,920 characters, confirmed from https://info.arxiv.org/help/prep.html.
arXiv receives PLAIN TEXT, so what counts is the rendered abstract with LaTeX
markup resolved -- not the file's byte count, which includes comments and macros
and would read ~2x too large.

MEASURE, never eyeball. The margin has been under 40 characters more than once.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ARXIV_LIMIT = 1920


def rendered_text(tex: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if not m:
        raise SystemExit("no abstract environment found")
    body = m.group(1)
    body = re.sub(r"(?m)^\s*%.*$", "", body)          # whole-line comments
    body = re.sub(r"(?<!\\)%.*$", "", body, flags=re.M)  # trailing comments
    body = re.sub(r"\\S\\ref\{[^}]*\}", "", body)     # cross-references vanish
    body = re.sub(r"\\ref\{[^}]*\}", "", body)
    body = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", body)  # \textbf{x} -> x
    body = re.sub(r"\\[a-zA-Z]+", "", body)           # bare control sequences
    body = body.replace("{,}", ",").replace("---", "\u2014").replace("--", "\u2013")
    body = body.replace("~", " ").replace("$", "").replace("\\", "")
    return re.sub(r"\s+", " ", body).strip()


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "abstract.tex")
    text = rendered_text(path.read_text(encoding="utf-8"))
    n = len(text)
    margin = ARXIV_LIMIT - n
    print(f"ABSTRACT_CHARS {n} / {ARXIV_LIMIT}  margin={margin}  words={len(text.split())}")
    if margin < 0:
        print(f"OVER LIMIT by {-margin} characters", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
