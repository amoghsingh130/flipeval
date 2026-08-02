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

2026-08-02: added the STALE-CLAIM AND STALE-POINTER LINTER (section 6 of
docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md). It runs over the whole source
tree, not just the \\input graph, because a withdrawn count can sit in a script
docstring, a notebook, a README or a test as easily as in a section file. See
STALE_RULES below for the tokens and SCOPE_ALLOWLIST for the exemptions, each of
which carries a written reason.
"""

import re
import sys
from pathlib import Path


def _find_root(start):
    root = Path(start).resolve()
    while not (root / "PREREGISTRATION.md").exists():
        if root == root.parent:
            return None
        root = root.parent
    return root


# Prefer the file's own location over the cwd: the linter is imported by
# tests/, which may run from anywhere, and a tool that only works from one
# directory is a tool that gets skipped.
ROOT = _find_root(Path(__file__).parent) or _find_root(Path.cwd())
if ROOT is None:
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


# --------------------------------------------------------------------------
# Stale-claim and stale-pointer linter
# --------------------------------------------------------------------------
#
# Two severities, and the distinction is deliberate:
#
#   "stale"   the token is a superseded rev-2 count, a retired construction, or
#             a pointer at a superseded artifact. Asserted wrong. Fails the run.
#   "review"  the token is sometimes correct -- "underpowered" is still the
#             right word in background and related-work discussion -- so the
#             linter surfaces it for a human and does NOT assert it is wrong.
#
# Nothing is silently dropped. Hits exempted by an allowlist or by the
# withdrawal-comment construct are still printed, under their own heading, with
# the reason that exempted them, so an over-broad exemption is visible.
#
# Matching is done over the WHOLE FILE TEXT with character offsets, never line
# by line. Several sources in this project (archived HTML/Markdown captures, the
# .ipynb notebooks, generated tables) are single-line blobs; a line-oriented
# matcher returns nothing on them and the nothing looks like a pass.


def _rx(pattern):
    return re.compile(pattern, re.IGNORECASE)


# The multiplication sign has four live spellings in this tree: 'x' (plain-text
# comments), U+00D7 (the blog post), '\times' (LaTeX math) and '$...\times$'.
# A plain "2.0x" match alone finds one of the four. Confirmed against the
# withdrawal commit 1137964, which left '2.0x-12.9x' in comments while the
# prose it edited carried '$2.0\times$' and '$12.9\times$'.
_MULT = r"(?:[\s$\\,!{}]{0,6})(?:x\b|×|\\times)"
_SHORTFALL_ENDPOINT = r"(?<![0-9.])(?:2\.0|12\.9)(?![0-9])" + _MULT
# ...and the bare pair, for prose that names the range without a sign at all
# ("the 2.0-12.9 range", "`2.0`-`12.9`"). Spans newlines on purpose: the
# withdrawn sentence in appendix_prereg_detail.tex wraps between the endpoints.
_SHORTFALL_PAIR = r"(?<![0-9.])2\.0(?![0-9])[\s\S]{0,40}?(?<![0-9.])12\.9(?![0-9])"

def _num(head, tail):
    """A thousands-separated integer in both spellings this tree uses: '1,155'
    in plain text and comments, '1{,}155' in LaTeX. Matching only the first
    finds none of the manuscript's own numbers."""
    return r"%s(?:,|\{,\})%s" % (head, tail)


# Rev-1 atlas/certification headline values, superseded by the 2026-07-21 rev-2
# correction: analysed 1,254 -> 1,807, probe-excluded analysable 1,155 -> 1,707,
# mmlu required n 2,123 -> 2,164, naive 7,355. 2,055 enumerated is NOT here: it
# is unchanged across the revision (verified against
# results/atlas_cells_summary_rev2.csv, 2,055 rows).
_REV1_POPULATION = (r"(?<![0-9])(?:" + "|".join(
    [_num("1", "155"), _num("1", "254"), _num("2", "123"), _num("7", "355")])
    + r")(?![0-9])")
# The naive-over-paired compute ratios of the rev-1 certification narrative.
_REV1_RATIO = r"(?<![0-9.])(?:3\.5|4\.4)(?![0-9])" + _MULT

# An old value written as "X to Y", "X $\to$ Y", "X -> Y" is a supersession
# MAPPING, which is how the correction appendix discloses the change. The old
# number belongs there. Narrow on purpose: the arrow must follow the number.
_SUPERSESSION_MAP = re.compile(
    r"\s*(?:\$?\\to\$?|→|-+>|to)\s*\\?(?:textbf\{|mathbf\{)?[0-9]")

_RCODE_RUN = re.compile(r"R\d{2}(?:[^A-Za-z0-9\n]{1,10}(?:and\s+)?R\d{2}){2,5}")
_OLD_GROUP = {"R06", "R07", "R15", "R17"}


def find_old_r_group(text):
    """The retired 'four underpowered claims' grouping, in any order.

    A literal 'R17, R07, R06, R15' misses 'R06, R07, R15 and R17'. Match any
    short run of R-codes and test the SET, so ordering and conjunctions do not
    matter, and a longer list that merely happens to contain them does not fire
    (the run is capped at six codes).
    """
    for m in _RCODE_RUN.finditer(text):
        if _OLD_GROUP <= set(re.findall(r"R\d{2}", m.group(0))):
            yield m.start(), m.end()


# key, severity, matcher, why it is on the list
STALE_RULES = [
    ("count-4-of-12", "stale",
     _rx(r"(?<![0-9])4[\s$-]+of[\s$-]+(?:the[\s$-]+)?12(?![0-9])"),
     "rev-2 headline K; rev-3 is 1 of 11 below the planning threshold"),
    ("count-5-of-17", "stale",
     _rx(r"(?<![0-9])5[\s$-]+of[\s$-]+(?:the[\s$-]+)?17(?![0-9])"),
     "rev-2 denominator; the eligible denominator is 16, not 17"),
    ("count-0-of-17", "stale",
     _rx(r"(?<![0-9])0[\s$-]+of[\s$-]+(?:the[\s$-]+)?17(?![0-9])"),
     "per-item-output tally is over the 16 ELIGIBLE sources in rev-3"),
    ("four-claims", "stale", _rx(r"\bfour\s+claims\b"),
     "the four flagged claims are all above threshold at 2 pp in rev-3"),
    ("shortfall-endpoint", "stale", _rx(_SHORTFALL_ENDPOINT),
     "the 2.0x-12.9x shortfall range is WITHDRAWN, not recomputed"),
    ("shortfall-pair", "stale", _rx(_SHORTFALL_PAIR),
     "the 2.0x-12.9x shortfall range is WITHDRAWN, not recomputed"),
    ("own-margin", "stale", _rx(r"own\s+margin"),
     "Amendment 2 forbids calling a derived quantity the source's own margin"),
    ("claim-specific-margin", "stale", _rx(r"claim[\s-]+specific\s+margin"),
     "same retired construction as own-margin"),
    ("margin-they-assert", "stale",
     _rx(r"margin\s+(?:they|it|the\s+source|its\s+source)\s+asserts?"),
     "no audited source asserts a margin; this is the abstract's old wording"),
    ("stated-margin", "stale", _rx(r"stated\s+margin"),
     "table header for a quantity no source stated"),
    ("label-audit-underpowered", "stale", _rx(r"audit[\s-]+underpowered"),
     "the LaTeX label tab:audit-underpowered was itself a stale claim"),
    ("old-r-group", "stale", find_old_r_group,
     "the retired R17/R07/R06/R15 'underpowered' grouping"),
    ("pointer-verdicts-rev2", "stale", _rx(r"audit_verdicts_rev2"),
     "superseded by results/audit_verdicts_rev3.csv"),
    # The rev-1 names are PREFIXES of the rev-2 names, so the '\.csv' is
    # load-bearing: without it every correct '_rev2.csv' pointer is flagged.
    ("pointer-rev1-artifact", "stale",
     re.compile(r"results/(?:atlas_cells_summary|atlas_exclusions"
                r"|identical_score_churn|certification_tables"
                r"|audit_verdicts)\.csv"
                r"|results/atlas_run_20260715\.tar\.gz"),
     "rev-1 atlas-era artifact; rev-2/rev-3 files carry a _rev suffix"),
    ("pointer-rev1-certification-doc", "stale",
     re.compile(r"docs/CERTIFICATION_TABLES_2026-07-20\.md"),
     "rev-1 certification narrative; its headline population and ratios are "
     "superseded. Current artifact: results/certification_tables_rev2.csv"),
    ("rev1-population", "stale", re.compile(_REV1_POPULATION),
     "rev-1 atlas population/required-n; rev-2 is 1,807 analysed and "
     "1,707 probe-excluded analysable"),
    ("rev1-certification-ratio", "review", _rx(_REV1_RATIO),
     "3.5x/4.4x are the rev-1 naive-over-paired compute ratios; a bare decimal "
     "with a multiplication sign is ambiguous, so HUMAN REVIEW"),
    ("own-assertion", "review", _rx(r"own\s+assertions?\b"),
     "the retired 'underpowered for its own assertion' verdict wording; "
     "legitimate only when quoted and marked as pre-Amendment-2 history"),
    ("own-margin-column", "review", re.compile(r"own_margin"),
     "legacy output column, removed in rev-3; absence assertions are fine"),
    ("underpowered", "review",
     re.compile(r"(?<![_\w])underpowered(?![_\w])", re.IGNORECASE),
     "correct in background and related-work discussion; wrong as a verdict "
     "about an audited claim. HUMAN REVIEW, not an assertion of error"),
]

# Every entry is narrow and carries its reason. An exemption suppresses the
# FAILURE, never the report: exempt hits are still listed.
SCOPE_ALLOWLIST = [
    ("paper/sections/appendix_registrations.tex", "*",
     "reproduces the FROZEN registrations verbatim and is machine-checked "
     "against them by verify_registrations.py; editing it falsifies the "
     "reproduction and breaks that gate"),
    ("PREREGISTRATION.md", "*", "frozen 2026-07-11; amendment-only"),
    ("docs/MINIGRID_REGISTRATION_2026-07-15.md", "*", "frozen; amendment-only"),
    ("docs/ATLAS_MINING_REGISTRATION_2026-07-15.md", "*",
     "frozen; amendment-only"),
    ("docs/AUDIT_REGISTRATION_2026-07-15.md", "*", "frozen; amendment-only"),
    ("docs/audit_claim_table.csv", "*",
     "frozen data; the audited claims are recorded as they were extracted"),
    ("docs/atlas_pair_manifest.json", "*",
     "frozen data; the pair manifest is fixed for the whole campaign"),
    ("paper/tools/check_paper.py", "*",
     "this linter states every forbidden token as a pattern literal"),
    ("tests/test_check_paper_stale.py", "*",
     "the linter's own tests state the forbidden tokens as fixtures"),
    ("paper/tools/README.md", "*",
     "documents the linter, so it quotes the forbidden tokens and the "
     "false-positive traps verbatim in order to explain them"),
]

# Downgraded to "review", never suppressed: these paths are reported in full but
# do not fail the run, for the reason recorded against each.
REVIEW_ONLY_PATHS = [
    ("docs/",
     "dated, append-only record archive. Superseded verdict records, incident "
     "write-ups and prior checklists are retained ON PURPOSE and must keep "
     "their original numbers"),
    ("paper/READING_COPY.md",
     "generated by paper/tools/gen_reading_copy.py from the .tex sources. Fix "
     "the source and regenerate; a hit here duplicates a source hit"),
]

SCAN_EXTS = {".tex", ".md", ".py", ".ipynb", ".json", ".csv", ".yaml", ".yml",
             ".sbatch", ".sh", ".bib", ".txt", ".cfg", ".toml", ".def"}
SCAN_DIRS = ["paper", "scripts", "tests", "notebooks", "flipeval", "pilot_eval",
             "configs", "docs", "container", "packaging", "kaggle"]
# results/ holds generated and sealed artifacts (audit_verdicts_rev3.csv is a
# released, paper-cited output). They are outputs to regenerate, never text to
# edit, so linting them would produce findings no one may act on.
SKIP_DIR_NAMES = {".git", "__pycache__", ".claude", "results", "node_modules",
                  ".pytest_cache", ".ipynb_checkpoints"}

# A '%' comment run is treated as LaTeX even inside .md, because READING_COPY.md
# is a generated concatenation of the .tex sources and inlines their comments.
COMMENT_PREFIXES = {
    ".tex": ("%",), ".md": ("%",), ".bib": ("%",),
    ".py": ("#",), ".sh": ("#",), ".sbatch": ("#",),
    ".yaml": ("#",), ".yml": ("#",), ".toml": ("#",), ".cfg": ("#",),
}

# The withdrawal commit (1137964) deliberately left a comment at every former
# shortfall-range site saying the range is withdrawn, "because the natural
# repair is to reach for new numbers". Those comments legitimately contain the
# withdrawn numbers. Exempt them BY CONSTRUCT -- a comment run that states the
# withdrawal -- rather than by skipping the file, so a stale claim added to the
# same file later is still caught.
WITHDRAWAL_MARKER = _rx(
    r"withdrawn|withdraw\b|not\s+recomputed|superseded|supersedes"
    r"|do\s+not\s+restore|do\s+not\s+reintroduce|stale\s+claim|retired\b"
    # ...and the correction-note idiom this tree uses for the rev-1 survivors.
    # A comment that says "this previously cited the REV-1 file" is doing the
    # right thing; the rev-1 name is the subject of the note, not a live
    # pointer. Without these, the 2026-07-26 and 2026-07-30 correction notes in
    # atlas.tex and appendix_audit_table.tex read as defects.
    r"|rev-\d\s+correction|corrected\s+20\d\d|rev-1\s+survivor"
    r"|previously\s+cited|previously\s+read"
    r"|this\s+(?:comment|sentence|paragraph|table)\s+(?:read|cited)")

# A provenance comment is the one place where a stale pointer is most dangerous
# and least visible: it can cite the rev-1 file as the source for a number the
# prose below it already corrected, and nothing renders, so nothing shows. That
# defect was found and fixed once in atlas.tex on 2026-07-26 and missed in the
# same file at line 102. Hits inside one are reported as their own class.
PROVENANCE_MARKER = re.compile(
    r"SOURCES?:|SOURCES?\s+for\b|POPULATION NOTE|Population:|Provenance",
    re.IGNORECASE)

# The same construct in RENDERED PROSE, for the paragraph that discloses the
# withdrawal to the reader. Deliberately stricter than the comment form: only a
# sentence that says the quantity is withdrawn or superseded exempts it, and
# only within its own sentence, not its paragraph. "do not restore" and "stale
# claim" are comment idioms and are not accepted here.
PROSE_WITHDRAWAL_MARKER = _rx(
    r"withdrawn|withdraw\b|not\s+recomputed|superseded|supersedes")
# A LaTeX row break and a markdown table pipe end a "statement" as firmly as a
# full stop: without them the window walks into the NEXT table row and borrows
# its "withdrawn" marker, exempting a cell that says no such thing.
_SENT_BREAK = re.compile(r"\.\s|\n\n|\\\\|\n\|")

# The paper deliberately QUOTES the retired wording in order to explain what
# Amendment 2 withdraws ("adds ``(and at the claim's own margin when it states
# one)''"). Quoting a retired phrase is not using it, so a wording hit wholly
# inside a quotation is exempt. This applies to the WORDING rules only: putting
# a superseded count or a dead file path inside quotation marks does not make it
# current, and those rules are covered by the withdrawal construct instead.
QUOTABLE_RULES = {"own-margin", "claim-specific-margin", "stated-margin",
                  "margin-they-assert", "own-assertion",
                  "label-audit-underpowered"}
# (opener, closer, max span). Markdown backticks are deliberately ABSENT: with a
# symmetric one-character delimiter, `K = 4` ... `J = 5` pairs the CLOSER of one
# span with the OPENER of the next and reads the prose between them as quoted.
# The straight-quote pair keeps a tight cap for the same reason; the asymmetric
# LaTeX pair does not need one.
_QUOTE_PAIRS = [("``", "''", 400), ("“", "”", 400), ('"', '"', 120)]


def in_quotation(text, start, end):
    """The enclosing quotation, or None. Bounded so a stray delimiter far away
    in the file cannot swallow live prose into an exemption."""
    for op, cl, limit in _QUOTE_PAIRS:
        o = text.rfind(op, max(0, start - limit), start)
        if o == -1:
            continue
        c = text.find(cl, end, min(len(text), end + limit))
        if c == -1:
            continue
        if text.find(cl, o + len(op), start) != -1:
            continue          # that opener was already closed before the hit
        span = text[o:c + len(cl)]
        if "\n\n" in span:
            continue          # a quotation does not cross a paragraph break
        return span
    return None


def prose_statement(text, start, end, window=250):
    """The sentence containing the hit, capped at `window` characters each way.

    Character-based on purpose. A sentence in these sources routinely wraps
    across lines, and the archived captures are single-line blobs, so anything
    line-oriented either misses the marker or swallows a whole file.
    """
    lo, hi = max(0, start - window), min(len(text), end + window)
    left = None
    for left in _SENT_BREAK.finditer(text[lo:start]):
        pass
    s = lo + (left.end() if left else 0)
    right = _SENT_BREAK.search(text[end:hi])
    e = end + (right.end() if right else hi - end)
    return text[s:e]


def comment_block(text, offset, prefixes):
    """The contiguous run of comment lines containing `offset`, or None.

    Blank lines end a run; a bare '%' does not, since that is how these files
    paragraph their comment headers.
    """
    if not prefixes:
        return None
    lines = text.split("\n")
    idx = text.count("\n", 0, offset)

    def is_comment(i):
        return 0 <= i < len(lines) and lines[i].lstrip().startswith(prefixes)

    if not is_comment(idx):
        return None
    lo = hi = idx
    while is_comment(lo - 1):
        lo -= 1
    while is_comment(hi + 1):
        hi += 1
    return "\n".join(lines[lo:hi + 1])


def snippet(text, start, end, width=44):
    """Whitespace-collapsed character window. Character-based, not line-based,
    so it still says something useful inside a single-line blob."""
    lo, hi = max(0, start - width), min(len(text), end + width)
    body = " ".join(text[lo:hi].split())
    return ("..." if lo else "") + body + ("..." if hi < len(text) else "")


def rule_spans(matcher, text):
    if callable(matcher) and not hasattr(matcher, "finditer"):
        for span in matcher(text):
            yield span
    else:
        for m in matcher.finditer(text):
            yield m.start(), m.end()


def allowlist_reason(rel, key):
    for path, scope, reason in SCOPE_ALLOWLIST:
        if rel == path and scope in ("*", key):
            return reason
    return None


CODE_EXTS = {".py", ".sh", ".sbatch", ".yaml", ".yml", ".ipynb", ".toml",
             ".cfg", ".def"}


def hit_context(rel, ext, block, compiled):
    """Which CLASS of thing this hit is. A bare token match cannot tell a
    manuscript defect from a historical note from a generated echo, so every
    hit carries this and the report groups by it."""
    if rel == "paper/READING_COPY.md":
        return "generated-echo"
    if rel == "paper/OUTLINE.md":
        return "planning-not-compiled"
    if rel.startswith("paper/blog/"):
        return "dated-post"
    if block is not None:
        return ("provenance-comment" if PROVENANCE_MARKER.search(block)
                else "comment")
    if rel.startswith("docs/"):
        return "dated-record"
    if ext in CODE_EXTS:
        return "code"
    if rel.startswith("paper/") and compiled is not None \
            and rel not in compiled:
        return "not-compiled"
    return "prose"


def scan_text(text, rel, ext, compiled=None):
    """Every hit in one file, each already labelled with its final severity, its
    context class, and any exemption that applies. Returns a list of dicts."""
    prefixes = COMMENT_PREFIXES.get(ext)
    hits = []
    for key, severity, matcher, why in STALE_RULES:
        for start, end in rule_spans(matcher, text):
            block = comment_block(text, start, prefixes)
            exempt = allowlist_reason(rel, key)
            if exempt is None and key == "rev1-population" \
                    and _SUPERSESSION_MAP.match(text, end):
                exempt = ("stated as an explicit old-to-new mapping (%s)"
                          % " ".join(text[start:end + 24].split()))
            if exempt is None:
                if block is not None:
                    marker = WITHDRAWAL_MARKER.search(block)
                    if marker:
                        exempt = ("comment states the withdrawal/supersession "
                                  "(%r)" % marker.group(0))
                else:
                    marker = PROSE_WITHDRAWAL_MARKER.search(
                        prose_statement(text, start, end))
                    if marker:
                        exempt = ("sentence states the withdrawal/supersession "
                                  "(%r)" % marker.group(0))
            if exempt is None and key in QUOTABLE_RULES:
                quote = in_quotation(text, start, end)
                if quote is not None:
                    exempt = ("quoted verbatim, not asserted (%s)"
                              % " ".join(quote.split())[:70])
            sev, note = severity, None
            if exempt is None and severity == "stale":
                for prefix, reason in REVIEW_ONLY_PATHS:
                    if rel.startswith(prefix):
                        sev, note = "review", "downgraded: review-only %s" % prefix
                        break
            hits.append({
                "path": rel, "rule": key, "why": why, "severity": sev,
                "context": hit_context(rel, ext, block, compiled),
                "line": text.count("\n", 0, start) + 1,
                "text": snippet(text, start, end), "exempt": exempt,
                "note": note,
            })
    hits.sort(key=lambda h: (h["line"], h["rule"]))
    return hits


def iter_source_files(root):
    seen = []
    roots = [root / d for d in SCAN_DIRS]
    roots += [p for p in sorted(root.glob("*")) if p.is_file()]
    for base in roots:
        if base.is_file():
            if base.suffix in SCAN_EXTS:
                seen.append(base)
            continue
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_EXTS:
                continue
            if SKIP_DIR_NAMES & set(path.relative_to(root).parts):
                continue
            seen.append(path)
    return sorted(set(seen))


def compiled_files(root):
    """Paths actually reachable from main.tex, so the report can separate a
    defect that reaches the PDF from stale planning material that never does.
    Returns None if the \\input graph cannot be walked."""
    try:
        chunks = expand(root / "paper" / "main.tex", set())
    except SystemExit:
        return None
    return {p.relative_to(root).as_posix() for _, p in chunks}


def check_stale_claims(root, compiled=None):
    """Returns (hits, n_files). Callers decide what fails."""
    if compiled is None:
        compiled = compiled_files(root)
    hits, n = [], 0
    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        n += 1
        hits.extend(scan_text(text, path.relative_to(root).as_posix(),
                              path.suffix, compiled))
    return hits, n


# Most consequential first: a defect that reaches the PDF, then one that
# misdirects a future editor, then material that never renders.
CONTEXT_ORDER = ["prose", "provenance-comment", "comment", "code",
                 "not-compiled", "planning-not-compiled", "dated-post",
                 "generated-echo", "dated-record"]
CONTEXT_HELP = {
    "prose": "RENDERS IN THE PDF. A manuscript defect if the token is stale.",
    "provenance-comment": "a SOURCE/provenance comment. Does not render, but "
                          "it can cite a superseded artifact as the source for "
                          "a number the prose below it already corrected.",
    "comment": "a non-provenance comment.",
    "code": "a script, test, notebook or config.",
    "not-compiled": "under paper/ but not reachable from main.tex.",
    "planning-not-compiled": "planning material, never reaches the PDF.",
    "dated-post": "a dated blog post. Correct or annotate is a human call; "
                  "rewriting a dated artifact is not automatic.",
    "generated-echo": "regenerated from the sections. Fix the source.",
    "dated-record": "the docs/ record archive, retained on purpose.",
}


def report_stale(hits, n_files, out=print):
    live = [h for h in hits if not h["exempt"] and h["severity"] == "stale"]
    review = [h for h in hits if not h["exempt"] and h["severity"] == "review"]
    exempt = [h for h in hits if h["exempt"]]
    out("STALE_CLAIM: %d files scanned, %d rules, %d hits "
        "(%d stale, %d review, %d exempt)"
        % (n_files, len(STALE_RULES), len(hits), len(live), len(review),
           len(exempt)))

    def dump(title, group):
        if not group:
            return
        out("STALE_CLAIM: %s (%d)" % (title, len(group)))
        for ctx in sorted({h["context"] for h in group},
                          key=lambda c: (CONTEXT_ORDER.index(c)
                                         if c in CONTEXT_ORDER else 99, c)):
            rows = [h for h in group if h["context"] == ctx]
            out("  -- context: %s (%d) -- %s"
                % (ctx, len(rows), CONTEXT_HELP.get(ctx, "")))
            for h in sorted(rows, key=lambda x: (x["path"], x["line"])):
                out("    %s:%d [%s] %s" % (h["path"], h["line"], h["rule"],
                                           h["text"]))
                if h["exempt"]:
                    out("        exempt: %s" % h["exempt"])
                if h["note"]:
                    out("        note: %s" % h["note"])

    dump("STALE -- superseded, asserted wrong", live)
    dump("REVIEW -- may be correct, a human must decide", review)
    dump("EXEMPT -- allowlisted or withdrawal-marked", exempt)
    out("STALE_CLAIM: allowlist (path, rules, reason)")
    for path, scope, reason in SCOPE_ALLOWLIST:
        out("  %s [%s] %s" % (path, scope, reason))
    out("STALE_CLAIM: review-only paths (reported, never failing)")
    for prefix, reason in REVIEW_ONLY_PATHS:
        out("  %s %s" % (prefix, reason))
    if live:
        out("STALE_CLAIM: FAIL -- %d stale claim/pointer hits" % len(live))
    else:
        out("STALE_CLAIM: OK -- no stale claims or pointers outside the "
            "documented exemptions")
    return 1 if live else 0


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


def run(argv):
    """Both checks run by default. A checker behind an opt-in flag is a checker
    nobody runs, which is the failure mode this file already has a docstring
    about."""
    want_structure = "--stale-only" not in argv
    want_stale = "--structure-only" not in argv
    rc = 0
    if want_structure:
        rc |= main()
    if want_stale:
        hits, n_files = check_stale_claims(ROOT)
        rc |= report_stale(hits, n_files) << 1
    return rc


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
