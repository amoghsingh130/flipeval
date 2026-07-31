#!/usr/bin/env python3
"""Prove that paper/sections/appendix_registrations.tex reproduces the four
frozen registration documents word-for-word.

Both sides are reduced to a stream of words -- LaTeX markup stripped on one
side, markdown markup stripped on the other -- and the streams are diffed. A
non-empty diff means the appendix says something the frozen source does not, or
drops something it does. Exits non-zero on any mismatch.
"""

import difflib
import re
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "PREREGISTRATION.md").exists():
    ROOT = ROOT.parent
    if ROOT == ROOT.parent:
        sys.exit("could not locate repo root")

SOURCES = [
    ("PREREGISTRATION.md", "app:reg:main"),
    ("docs/MINIGRID_REGISTRATION_2026-07-15.md", "app:reg:minigrid"),
    ("docs/ATLAS_MINING_REGISTRATION_2026-07-15.md", "app:reg:atlas"),
    ("docs/AUDIT_REGISTRATION_2026-07-15.md", "app:reg:audit"),
]

UNICODE_BACK = {
    r"$\times$": "×", "---": "—", "--": "–", r"\S{}": "§",
    r"$\Rightarrow$": "⇒", "$-$": "−", r"$\alpha$": "α",
    r"$\leq$": "≤", r"$\geq$": "≥",
    "``": '"', "''": '"',
}


def md_words(text):
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Exactly one leading marker is stripped per line. Stripping a list
        # marker after a heading marker would eat the "1." of headings like
        # "## 1. Scope", which is heading TEXT, not a list marker.
        if re.match(r"^#{1,6}\s+", line):
            line = re.sub(r"^#{1,6}\s+", "", line)
        elif re.match(r"^[-*+]\s+", line):
            line = re.sub(r"^[-*+]\s+", "", line)
        else:
            line = re.sub(r"^\d+\.\s+", "", line)
        line = line.replace("**", "").replace("`", "")
        line = re.sub(r"(?<!\*)\*(?!\*)", "", line)
        out.extend(line.split())
    return out


def tex_words(text):
    # drop comment-only lines, marked non-source lines, and the non-source block
    kept = []
    skipping = False
    for line in text.split("\n"):
        if "% NON-SOURCE-BLOCK-BEGIN" in line:
            skipping = True
            continue
        if "% NON-SOURCE-BLOCK-END" in line:
            skipping = False
            continue
        if skipping or "% NON-SOURCE" in line:
            continue
        if line.lstrip().startswith("%"):
            continue
        kept.append(line)
    body = "\n".join(kept)

    # \authorname is the de-anonymisation macro (see main.tex). The word
    # stream is checked against the NON-anonymous expansion, which is what
    # makes "verbatim" true of the arXiv build.
    body = body.replace(r"\authorname{}", "Amogh Singh")
    body = body.replace(r"\mbox{}\\", " ")
    body = body.replace(r"\allowbreak{}", "")
    # structural commands carry no words of their own
    body = re.sub(r"\\(begin|end)\{[a-z]*\}", " ", body)
    body = re.sub(r"\\label\{[^}]*\}", " ", body)
    body = re.sub(r"\\item\b", " ", body)

    # Escaped literals are parked on sentinels so that stripping the markup
    # braces below cannot eat them. Longest patterns first.
    parked = {}
    for i, (tex, char) in enumerate([
            (r"\textbackslash{}", "\\"), (r"\textasciicircum{}", "^"),
            (r"\textasciitilde{}", "~"), (r"\{", "{"), (r"\}", "}"),
            (r"\_", "_"), (r"\%", "%"), (r"\#", "#"), (r"\&", "&"),
            (r"\$", "$")]):
        token = "\x00%d\x01" % i
        parked[token] = char
        body = body.replace(tex, token)
    for tex, char in sorted(UNICODE_BACK.items(), key=lambda kv: -len(kv[0])):
        token = "\x00u%d\x01" % len(parked)
        parked[token] = char
        body = body.replace(tex, token)

    # Wrappers whose ARGUMENT is source text: drop the wrapper, keep the words.
    # Braces go to the EMPTY string, not a space -- markdown's ** and ` are
    # likewise removed without separating the text they abut from following
    # punctuation.
    body = re.sub(r"\\(subsection|subsubsection|paragraph|textbf|emph|texttt)\{",
                  "", body)
    body = body.replace("}", "").replace("{", "")

    for token, char in parked.items():
        body = body.replace(token, char)
    return body.split()


def main():
    tex = (ROOT / "paper/sections/appendix_registrations.tex").read_text(encoding="utf-8")
    words = tex_words(tex)

    expected = []
    for rel, _ in SOURCES:
        expected.extend(md_words((ROOT / rel).read_text(encoding="utf-8")))

    if words == expected:
        print("REGISTRATIONS_VERBATIM: OK -- %d words match across %d documents"
              % (len(words), len(SOURCES)))
        return 0

    print("REGISTRATIONS_VERBATIM: MISMATCH")
    print("  appendix words: %d, source words: %d" % (len(words), len(expected)))
    diff = list(difflib.unified_diff(expected, words, "frozen-sources",
                                     "appendix", lineterm="", n=3))
    for line in diff[:120]:
        print("  " + line)
    if len(diff) > 120:
        print("  ... %d more diff lines" % (len(diff) - 120))
    return 1


if __name__ == "__main__":
    sys.exit(main())
