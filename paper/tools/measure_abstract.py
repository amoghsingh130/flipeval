#!/usr/bin/env python3
"""Measure abstract.tex against the arXiv abstract-field limit.

The limit is 1,920 characters, confirmed from https://info.arxiv.org/help/prep.html.
arXiv receives PLAIN TEXT, so what counts is the rendered abstract with LaTeX
markup resolved -- not the file's byte count, which includes comments and macros
and would read ~2x too large.

MEASURE, never eyeball. The margin has been under 40 characters more than once.

GENERATED AUDIT MACROS ARE EXPANDED FIRST, and that step is load-bearing.
`rendered_text` deletes bare control sequences, so an unexpanded
`\\AuditEligible{}` would contribute ZERO characters here while arXiv receives
the two characters "16". With the abstract carrying a dozen such macros the
measurement would read tens of characters short of the truth, against a margin
that has been under 40 -- a gate that cannot fail in the direction that matters.
So the macros are resolved from paper/audit_denominators.tex before any
stripping, and an audit macro this file cannot resolve is a hard error rather
than a silent deletion.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ARXIV_LIMIT = 1920

MACRO_FILE = Path(__file__).resolve().parents[1] / "audit_denominators.tex"

_NEWCOMMAND = re.compile(r"\\newcommand\{\\(Audit[A-Za-z]+)\}\{(.*)\}\s*$", re.M)
_CSNAME = re.compile(r"\\expandafter\\def\\csname\s+(Audit[A-Za-z0-9]+)\\endcsname\{(.*)\}\s*$", re.M)


def audit_macros() -> dict[str, str]:
    """Every \\Audit* value the generated ledger defines, as plain text."""
    if not MACRO_FILE.exists():
        raise SystemExit(f"missing generated macro file: {MACRO_FILE}")
    src = MACRO_FILE.read_text(encoding="utf-8")
    table = {name: value for name, value in _NEWCOMMAND.findall(src)}
    table.update({name: value for name, value in _CSNAME.findall(src)})
    return table


def expand_audit_macros(body: str) -> str:
    """Resolve \\AuditVal{Rnn}{field} and \\AuditFoo{} to the text arXiv sees."""
    table = audit_macros()

    def one_val(m: re.Match) -> str:
        key = f"AuditData{m.group(1)}{m.group(2)}"
        if key not in table:
            raise SystemExit(f"abstract asks for undefined audit value: {key}")
        return table[key]

    body = re.sub(r"\\AuditVal\{([A-Za-z0-9]+)\}\{([A-Za-z]+)\}", one_val, body)

    def one_macro(m: re.Match) -> str:
        name = m.group(1)
        if name in ("Val",):  # already handled above
            return m.group(0)
        key = f"Audit{name}"
        if key not in table:
            raise SystemExit(f"abstract uses undefined audit macro: \\{key}")
        return table[key]

    return re.sub(r"\\Audit([A-Za-z]+)(?:\{\})?", one_macro, body)


def rendered_text(tex: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if not m:
        raise SystemExit("no abstract environment found")
    body = m.group(1)
    body = re.sub(r"(?m)^\s*%.*$", "", body)          # whole-line comments
    body = re.sub(r"(?<!\\)%.*$", "", body, flags=re.M)  # trailing comments
    # BEFORE any control-sequence stripping -- see the module docstring.
    body = expand_audit_macros(body)
    body = re.sub(r"\\S\\ref\{[^}]*\}", "", body)     # cross-references vanish
    body = re.sub(r"\\ref\{[^}]*\}", "", body)
    body = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", body)  # \textbf{x} -> x
    body = re.sub(r"\\[a-zA-Z]+", "", body)           # bare control sequences
    body = body.replace("{,}", ",").replace("---", "\u2014").replace("--", "\u2013")
    body = body.replace("~", " ").replace("$", "").replace("\\", "")
    # Grouping braces are markup and render as nothing, so they must not count
    # against a character limit. They survived every rule above: line 81 removes
    # `\sloppy` and `\par` but leaves the `{` and `}` that scoped them, which
    # added 3 phantom characters when the abstract's last paragraph was wrapped
    # in a \sloppy group on 2026-08-05. Run after the `{,}` digit-separator
    # substitution above, which is the one place a brace is meaningful.
    body = body.replace("{", "").replace("}", "")
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
