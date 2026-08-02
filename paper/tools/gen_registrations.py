#!/usr/bin/env python3
"""Generate paper/sections/appendix_registrations.tex from the four frozen
registration documents.

READ-ONLY against the frozen sources. The conversion is faithful word-for-word:
markdown structure becomes LaTeX structure, inline markup becomes LaTeX inline
markup, and no word of the source text is added, dropped or reordered. That
property is machine-checked by verify_registrations.py, which strips both sides
back to a word stream and diffs them.

Why not \\begin{verbatim}: PREREGISTRATION.md is unwrapped prose with lines up
to 967 characters. Verbatim would run off the page and be clipped in print,
which defeats the point of reproducing the rule text for reviewers.
"""

import re
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "PREREGISTRATION.md").exists():
    ROOT = ROOT.parent
    if ROOT == ROOT.parent:
        sys.exit("could not locate repo root")

AUTHOR = "Amogh Singh"

SOURCES = [
    ("PREREGISTRATION.md", "app:reg:main", "Main-grid preregistration"),
    ("docs/MINIGRID_REGISTRATION_2026-07-15.md", "app:reg:minigrid",
     "Mini-grid registration"),
    ("docs/ATLAS_MINING_REGISTRATION_2026-07-15.md", "app:reg:atlas",
     "Atlas mining registration"),
    ("docs/AUDIT_REGISTRATION_2026-07-15.md", "app:reg:audit",
     "Published-claim audit registration"),
]

# Every non-ASCII codepoint that occurs in the four sources, mapped to a LaTeX
# form that renders the same glyph without inputenc/unicode-math assumptions.
UNICODE = {
    "×": r"$\times$",
    "—": "---",
    "–": "--",
    "§": r"\S{}",
    "⇒": r"$\Rightarrow$",
    "−": "$-$",
    "α": r"$\alpha$",
    "≤": r"$\leq$",
    "≥": r"$\geq$",
    "‘": "`",
    "’": "'",
    "“": "``",
    "”": "''",
    # Entered the corpus with Amendment 2 (signed 2026-07-31), which is the
    # first frozen text to use an ellipsis character. The generator fails closed
    # on an unmapped codepoint rather than dropping or mangling it, which is
    # what surfaced this: the appendix could not be regenerated until the map
    # covered it.
    "…": r"\dots{}",
}

SPECIALS = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "^": r"\textasciicircum{}",
    "_": r"\_",
    "%": r"\%",
    "~": r"\textasciitilde{}",
}


def escape(text, verb=False):
    out = []
    for ch in text:
        if ch in SPECIALS:
            out.append(SPECIALS[ch])
        elif ch in UNICODE:
            out.append(UNICODE[ch])
        elif ord(ch) > 127:
            sys.exit("unmapped non-ASCII codepoint %r (U+%04X)" % (ch, ord(ch)))
        else:
            out.append(ch)
        if verb and ch in "/-":
            # let long \texttt paths and flags break across lines
            out.append(r"\allowbreak{}")
    return "".join(out)


def inline(text):
    """Convert markdown inline markup.

    Code spans are parked on sentinels rather than converted in place, because
    bold spans in these documents cross code spans -- e.g. the mini-grid
    registration's "**1 few-shot example ... `configs/pace_bridge_chat.yaml`**".
    Converting code first would leave those ** markers unmatched and print them
    literally. Parking keeps the code-span text out of the emphasis regexes
    while still letting emphasis span them.
    """
    spans = []

    def park(m):
        spans.append(m.group(1))
        return "\x10%d\x11" % (len(spans) - 1)

    text = re.sub(r"`([^`]*)`", park, text)

    # Straight double quotes would both render as closing quotes in LaTeX.
    # Verified safe: no code span in the four sources contains a quote, so
    # pairing cannot straddle one.
    text = re.sub(r'"([^"]*)"', lambda m: "``" + m.group(1) + "''", text)

    text = re.sub(r"\*\*(.+?)\*\*", lambda m: "\x00" + m.group(1) + "\x01", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
                  lambda m: "\x02" + m.group(1) + "\x03", text)
    text = escape(text)
    text = text.replace("\x00", r"\textbf{").replace("\x01", "}")
    text = text.replace("\x02", r"\emph{").replace("\x03", "}")

    def unpark(m):
        return r"\texttt{%s}" % escape(spans[int(m.group(1))], verb=True)

    return re.sub("\x10(\\d+)\x11", unpark, text)


HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
ORDERED = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")


def convert(path, label, short_title):
    lines = path.read_text(encoding="utf-8").split("\n")
    out = []
    stack = []          # open list environments, innermost last
    para = []           # accumulating paragraph / list-item text
    pending_item = None  # environment the accumulated text belongs to

    def flush():
        nonlocal para, pending_item
        if not para:
            return
        text = inline(" ".join(para).strip())
        if pending_item:
            out.append(r"\item " + text)
        else:
            out.append(text)
            out.append("")
        para = []
        pending_item = None

    def close_lists(to_depth=0):
        while len(stack) > to_depth:
            flush()
            out.append(r"\end{%s}" % stack.pop())

    first_heading = True
    for raw in lines:
        line = raw.rstrip()

        if not line.strip():
            flush()
            continue

        m = HEADING.match(line)
        if m:
            close_lists()
            flush()
            level, title = len(m.group(1)), inline(m.group(2).strip())
            if level == 1:
                if not first_heading:
                    sys.exit("unexpected second level-1 heading in %s" % path)
                first_heading = False
                out.append(r"\subsection{%s}" % title)
                out.append(r"\label{%s}  %% NON-SOURCE" % label)
                out.append(r"\emph{Reproduced from \texttt{%s}; see "
                           r"\S\ref{app:reg:note}.}  %% NON-SOURCE"
                           % escape(str(path.relative_to(ROOT)), verb=True))
                out.append("")
            elif level == 2:
                out.append(r"\subsubsection{%s}" % title)
            else:
                out.append(r"\paragraph{%s}" % title)
                out.append(r"\mbox{}\\")
            continue

        m = BULLET.match(line)
        if m:
            indent = len(m.group(1))
            depth = indent // 2 + 1
            if depth > len(stack):
                flush()
                while len(stack) < depth:
                    out.append(r"\begin{itemize}")
                    stack.append("itemize")
            else:
                close_lists(depth)
                flush()
            para = [m.group(2)]
            pending_item = stack[-1]
            continue

        m = ORDERED.match(line)
        if m:
            indent = len(m.group(1))
            depth = indent // 3 + 1
            if depth > len(stack):
                flush()
                while len(stack) < depth:
                    out.append(r"\begin{enumerate}")
                    stack.append("enumerate")
            else:
                close_lists(depth)
                flush()
            para = [m.group(3)]
            pending_item = stack[-1]
            continue

        # continuation line: belongs to the open item or paragraph
        if stack and not para and not pending_item:
            # indented continuation after a blank line inside a list
            close_lists()
        para.append(line.strip())

    close_lists()
    flush()
    return out


def main():
    body = [
        "% =====================================================================",
        "% Appendix: the frozen preregistration documents, reproduced.",
        "%",
        "% GENERATED -- do not hand-edit. Regenerate with the session script",
        "% gen_registrations.py and re-check with verify_registrations.py, which",
        "% diffs the word stream of this file against the four frozen sources.",
        "%",
        "% Sources are FROZEN and are read READ-ONLY:",
        "%   PREREGISTRATION.md",
        "%   docs/MINIGRID_REGISTRATION_2026-07-15.md",
        "%   docs/ATLAS_MINING_REGISTRATION_2026-07-15.md",
        "%   docs/AUDIT_REGISTRATION_2026-07-15.md",
        "%",
        "% Faithfulness: markdown structure becomes LaTeX structure and inline",
        "% markup becomes LaTeX inline markup. No word is added, dropped or",
        "% reordered; the verifier proves that. Verbatim environments were",
        "% rejected because PREREGISTRATION.md has unwrapped lines up to 967",
        "% characters, which would be clipped at the page edge.",
        "%",
        "% This appendix is IDENTICAL in the arXiv and TMLR builds: reproducing",
        "% the text rather than linking it is what keeps the frozen rules",
        "% readable under double-blind review.",
        "% =====================================================================",
        "",
        r"\section{Preregistration documents}  % NON-SOURCE",
        r"\label{app:registrations}  % NON-SOURCE",
        "",
        r"\label{app:reg:note}  % NON-SOURCE",
        r"% NON-SOURCE-BLOCK-BEGIN",
        r"This appendix reproduces the four frozen protocol documents that",
        r"\S\ref{sec:prereg} describes, so that the rule text can be read without",
        r"leaving the paper. Each is reproduced in full, including its dated",
        r"amendments. Formatting is typeset rather than plain-text, but no wording",
        r"has been changed: the conversion is generated and machine-checked",
        r"word-for-word against the frozen files. The authoritative copies are the",
        r"files themselves in the archived source package",
        r"(\S\ref{sec:artifacts}).",
        r"% NON-SOURCE-BLOCK-END",
        "",
    ]
    for rel, label, short in SOURCES:
        body.extend(convert(ROOT / rel, label, short))
        body.append("")

    # The frozen documents name their decision owner. That is source text, so
    # it cannot be dropped -- but it de-anonymises the double-blind build, so it
    # is routed through the same macro as every other identifier. The arXiv
    # build prints the name and stays literally verbatim; the TMLR build prints
    # a visible withheld marker.
    text = "\n".join(body).rstrip() + "\n"
    before = text.count(AUTHOR)
    text = text.replace(AUTHOR, r"\authorname{}")
    if before == 0:
        sys.exit("expected the decision owner's name in the sources; found none")

    dest = ROOT / "paper/sections/appendix_registrations.tex"
    dest.write_text(text, encoding="utf-8")
    print("wrote %s (%d lines, %d author-name site(s) routed through "
          "\\authorname)" % (dest, len(body), before))


if __name__ == "__main__":
    main()
