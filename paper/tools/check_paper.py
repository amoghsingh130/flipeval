#!/usr/bin/env python3
"""Structural check of paper/main.tex. There is no LaTeX on this host, so this
stands in for a build: it expands \\input recursively, then checks references,
citations, environment balance and -- new on 2026-07-31 -- that the anonymous
build contains no identifying string outside a comment.

Two checker bugs bit a previous session and both looked like document defects:
a column-spec regex that truncated at the first '}' of '@{}ll@{}', and a
one-level \\input walk that missed sections/minigrid_escalation.tex nested
inside minigrid.tex. Both are fixed here: the walk is recursive, and the column
check counts unescaped '&' per row against the spec's column letters parsed
with brace awareness.

2026-08-01: the column check described above was NOT PRESENT in this file. It
existed in the scratchpad script this tool was assembled from and was dropped in
the move, leaving a docstring that promised a check nobody was running -- the
same failure mode as a stale expected test count. Implemented below, and
negative-controlled by deleting a column from a real row.
"""

import re
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "PREREGISTRATION.md").exists():
    ROOT = ROOT.parent
    if ROOT == ROOT.parent:
        sys.exit("could not locate repo root")
PAPER = ROOT / "paper"

# Strings that must never reach a rendered anonymous submission.
IDENTIFIERS = ["Amogh", "amoghsingh130", "AmoghSingh123", "Georgia Institute",
               "gatech", "21708923", "21708922", "3831", "Phoenix", "PACE"]


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        # a '%' preceded by a backslash is a literal percent sign
        cut = None
        for i, ch in enumerate(line):
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                cut = i
                break
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def skip_group(spec, i):
    """Advance past a balanced {...} starting at spec[i] == '{'."""
    depth = 0
    while i < len(spec):
        if spec[i] == "{":
            depth += 1
        elif spec[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def spec_columns(spec):
    """Count columns in a tabular column spec, brace-aware.

    '@{}llr@{}' is 3, not 0: the earlier bug regex stopped at the first '}'.
    'p{2cm}' is one column and its argument is skipped whole.
    """
    n, i = 0, 0
    while i < len(spec):
        ch = spec[i]
        if ch in "@!>?<":              # decoration: skip its brace argument
            i += 1
            if i < len(spec) and spec[i] == "{":
                i = skip_group(spec, i)
            continue
        if ch in "pmbP":               # sized column: one column, skip argument
            n += 1
            i += 1
            if i < len(spec) and spec[i] == "{":
                i = skip_group(spec, i)
            continue
        if ch in "lcrXY":
            n += 1
        i += 1                          # '|', whitespace and stray chars ignored
    return n


def row_columns(row):
    """Columns spanned by one tabular row: unescaped '&' at brace depth 0,
    plus the extra span of every \\multicolumn{k}."""
    depth, amps = 0, 0
    i = 0
    while i < len(row):
        ch = row[i]
        if ch == "\\":
            i += 2                      # escaped char, incl. \& and \{
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == "&" and depth == 0:
            amps += 1
        i += 1
    extra = sum(int(k) - 1
                for k in re.findall(r"\\multicolumn\{(\d+)\}", row))
    return amps + 1 + extra


RULE_ONLY = re.compile(r"^(\s|\\(top|mid|bottom)rule|\\cmidrule(\([lr]{1,2}\))?"
                       r"\{[^}]*\}|\\addlinespace(\[[^\]]*\])?|\\hline)*$")


def check_tabulars(chunks, problems, tally):
    """Every non-rule row of every tabular must span exactly the spec's columns.

    Runs per FILE, on comment-stripped text, so a line number is reportable and
    a commented-out table cannot raise a finding.
    """
    for text, path in chunks:
        for m in re.finditer(r"\\begin\{tabular\*?\}(?:\[[^\]]*\])?\s*", text):
            i = m.end()
            if i >= len(text) or text[i] != "{":
                continue
            end_spec = skip_group(text, i)
            spec = text[i + 1:end_spec - 1]
            close = text.find(r"\end{tabular}", end_spec)
            if close == -1:
                continue
            want = spec_columns(spec)
            tally[0] += 1
            body = text[end_spec:close]
            line0 = text[:m.start()].count("\n") + 1
            for row in body.split(r"\\"):
                if RULE_ONLY.match(row) or not row.strip():
                    continue
                tally[1] += 1
                got = row_columns(row)
                if got != want:
                    problems.append(
                        "%s: tabular near line %d declares %d columns but a row "
                        "spans %d: %r" % (path.name, line0, want, got,
                                          " ".join(row.split())[:60]))


def expand(path, seen):
    if path in seen:
        sys.exit("input cycle at %s" % path)
    seen.add(path)
    text = strip_comments(path.read_text(encoding="utf-8"))
    chunks, pos = [], 0
    for m in re.finditer(r"\\input\{([^}]*)\}", text):
        chunks.append((text[pos:m.start()], path))
        child = PAPER / (m.group(1) + ".tex")
        if not child.exists():
            sys.exit("missing \\input target: %s" % child)
        chunks.extend(expand(child, seen))
        pos = m.end()
    chunks.append((text[pos:], path))
    return chunks


def main():
    chunks = expand(PAPER / "main.tex", set())
    files = sorted({p for _, p in chunks})
    doc = "".join(c for c, _ in chunks)

    problems = []

    labels = re.findall(r"\\label\{([^}]*)\}", doc)
    refs = re.findall(r"\\(?:ref|autoref|pageref)\{([^}]*)\}", doc)
    dupes = {x for x in labels if labels.count(x) > 1}
    dangling = sorted(set(refs) - set(labels))
    if dupes:
        problems.append("duplicate labels: %s" % sorted(dupes))
    if dangling:
        problems.append("dangling refs: %s" % dangling)

    bib = (PAPER / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited = set()
    for group in re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", doc):
        cited.update(k.strip() for k in group.split(","))
    missing = sorted(cited - keys)
    if missing:
        problems.append("cite keys not in references.bib: %s" % missing)

    tally = [0, 0]
    check_tabulars(chunks, problems, tally)

    begins = re.findall(r"\\begin\{(\w+\*?)\}", doc)
    ends = re.findall(r"\\end\{(\w+\*?)\}", doc)
    for env in set(begins) | set(ends):
        if begins.count(env) != ends.count(env):
            problems.append("unbalanced environment %s: %d begin, %d end"
                            % (env, begins.count(env), ends.count(env)))

    # \ifanon / \fi balance in main.tex only (that is where the switch lives)
    main_src = strip_comments((PAPER / "main.tex").read_text(encoding="utf-8"))
    # \newif\ifanon DECLARES the conditional; it does not open one, so it must
    # not be counted against \fi.
    opens = main_src.count(r"\ifanon") - main_src.count(r"\newif\ifanon")
    if opens != main_src.count(r"\fi"):
        problems.append("\\ifanon/\\fi unbalanced in main.tex: %d vs %d"
                        % (opens, main_src.count(r"\fi")))

    # Anonymous-build leak check: every identifier must live inside main.tex's
    # \else branch, never in a section file's rendered text.
    for path in files:
        if path.name == "main.tex":
            continue
        body = strip_comments(path.read_text(encoding="utf-8"))
        for ident in IDENTIFIERS:
            if ident in body:
                problems.append("identifier %r renders in %s -- route it "
                                "through a main.tex macro"
                                % (ident, path.relative_to(ROOT)))

    print("PAPER_CHECK: %d files, %d labels, %d refs, %d cite keys, "
          "%d environments, %d tabulars (%d rows)"
          % (len(files), len(labels), len(refs), len(cited),
             len(set(begins)), tally[0], tally[1]))
    if problems:
        print("PAPER_CHECK: FAIL")
        for p in problems:
            print("  - %s" % p)
        return 1
    print("PAPER_CHECK: OK -- 0 dangling refs, 0 unresolved cites, "
          "environments balanced, tabular columns consistent, "
          "anonymous build clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
