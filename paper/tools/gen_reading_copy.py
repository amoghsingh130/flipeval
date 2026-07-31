#!/usr/bin/env python3
"""Regenerate paper/READING_COPY.md.

There is no LaTeX on this host, so the reading copy is the review surface: the
sections concatenated verbatim in main.tex \\input order, nested \\input expanded
in place, with no content edits. LaTeX markup is left as-is deliberately --
substituting rendered text would be an edit.
"""

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "PREREGISTRATION.md").exists():
    ROOT = ROOT.parent
    if ROOT == ROOT.parent:
        sys.exit("could not locate repo root")
PAPER = ROOT / "paper"

FRONT = {"paper/abstract.tex": "—"}


def order(path, nested=False):
    """main.tex \\input order, nested \\input expanded in place."""
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"^[^%\n]*\\input\{([^}]*)\}", text, re.M):
        child = PAPER / (m.group(1) + ".tex")
        if not child.exists():
            sys.exit("missing \\input target: %s" % child)
        yield child, nested
        yield from order(child, nested=True)


def title_of(path):
    # Comments are cut first: a trailing "% NON-SOURCE" on a \section line
    # otherwise defeats the end-anchor and the file is misread as having no
    # \section, which demotes it to a nested subsection in the index.
    text = "\n".join(re.sub(r"(?<!\\)%.*$", "", line)
                     for line in path.read_text(encoding="utf-8").split("\n"))
    for m in re.finditer(r"^[^\n]*\\(section|subsection)\*?\{(.+?)\}\s*$",
                         text, re.M):
        title = m.group(2)
        title = re.sub(r"\\[a-zA-Z]+\s*", "", title)
        title = title.replace("{", "").replace("}", "").replace("\\\\", " ")
        title = title.replace("---", "\u2014").replace("--", "\u2013")
        return title.strip(), m.group(1)
    return None, None


def main():
    sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse",
                                   "--short", "HEAD"]).decode().strip()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    files = list(order(PAPER / "main.tex"))

    out = [
        "# FlipEval — Paper Reading Copy",
        "",
        "**Generated %s from `paper/main.tex` at commit `%s`.**" % (stamp, sha),
        "",
        "No PDF: the Phoenix login node has no `pdflatex`, `xelatex`, "
        "`lualatex`, `latexmk`, `tectonic` or `pandoc`, and the pinned "
        "Apptainer image is an ML runtime with no TeX distribution. Per the "
        "fallback, the sections are concatenated **verbatim, in `main.tex` "
        "input order** (nested `\\input` expanded in place), with no content "
        "edits. LaTeX markup is left as-is deliberately: substituting rendered "
        "text would be an edit.",
        "",
        "A reader's index is at the end.",
        "",
    ]

    rows, number = [], 0
    for path, nested in files:
        rel = str(path.relative_to(ROOT))
        out += ["", "---", "", "## FILE: `%s`" % rel, "", "```latex",
                path.read_text(encoding="utf-8").rstrip(), "```"]

        title, kind = title_of(path)
        if rel in FRONT:
            rows.append(("—", "Abstract", rel))
        elif nested or kind == "subsection":
            rows.append(("↳", "(subsection) %s" % (title or rel), rel))
        elif "appendix" in path.name:
            rows.append(("App.", title or rel, rel))
        else:
            number += 1
            rows.append((str(number), title or rel, rel))

    out += [
        "---",
        "",
        "## Reader's index",
        "",
        "Sections in reading order (numbered as the compiled paper numbers "
        "them; front matter and appendix marked).",
        "",
        "| # | Section | File |",
        "|---|---|---|",
    ]
    # Rows are contiguous: the previous generator separated them with blank
    # lines, which ends the markdown table after its header and leaves every
    # row as literal text.
    out += ["| %s | %s | `%s` |" % r for r in rows]
    out.append("")

    dest = PAPER / "READING_COPY.md"
    dest.write_text("\n".join(out), encoding="utf-8")
    print("READING_COPY regenerated at %s: %d files, %d index rows"
          % (sha, len(files), len(rows)))


if __name__ == "__main__":
    main()
