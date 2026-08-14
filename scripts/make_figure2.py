#!/usr/bin/env python3
r"""Generate Figure 2, the before/after reporting comparison, as TikZ.

WHAT THIS FIGURE IS. One evaluation -- the registered Qwen2.5-7B / GSM8K cell
that Figure 1 already dissects -- shown twice: as an aggregate report of the kind
the audit finds in the field (two accuracies and a net delta), and as the same
run reported under the five-line standard of this paper. The point is that the
two columns describe the SAME numbers: nothing in column B needs a new
experiment, only a different report.

Why TikZ and not matplotlib: same reason as scripts/make_figure1.py. There is no
matplotlib in the pinned image and no LaTeX on the compute nodes, so the figure
ships as source and is rasterised to vector by whatever machine runs pdflatex.
Nothing in this file renders anything.

STDLIB ONLY, and Python 3.9 compatible, so it runs on the Phoenix login node.
Unlike scripts/make_figure1.py it does NOT import scripts/audit_stats.py: the one
value that needs scipy (the TOST planning requirement, 2,730 at a 2 pp margin) is
read out of paper/figures/fig1_values.json, which is the committed provenance
record that make_figure1.py emitted from audit_stats.required_n_for_tost. It is
read, never recomputed and never typed.

PANEL SCOPE, LOAD-BEARING -- the same wording rule that governs Figure 1 panel C
and \S\ref{sec:intro}. The 2,730 is a PLANNING requirement computed at an assumed
TRUE difference of zero. It says this evaluation cannot support an equivalence
claim at a +/-2 pp margin. It is NOT evidence that GPTQ and AWQ differ, and no
line of this figure or its caption may be edited into implying that it is.

NO TOST VERDICT IS ASSERTED. No committed artifact records a TOST outcome for
this cell. What the artifacts do record is a joint percentile-bootstrap 95%
confidence interval for the paired accuracy delta
(results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json), and that is what row 2
draws, labelled as exactly that. It is NOT the 90% two-sided interval that TOST
at one-sided alpha=.05 requires (\S\ref{sec:cert:method}), so its relationship to
the +/-2 pp bounds decides nothing about the TOST, and the row says so.

CONSEQUENCE OF LIVING HERE: scripts/ is a fingerprinted tree, so changing this
file requires the in-image pytest gate and a freeze refresh (CLAUDE.md). It is
placed here to match scripts/make_figure1.py, the figure generator this one is
modelled on. It is stdlib-only, so paper/tools/ would also satisfy its
dependencies and would avoid the freeze burden; that is the author's call.

Run:

    python3 scripts/make_figure2.py \
      --out-tex paper/figures/fig2_before_after.tex \
      --out-json paper/figures/fig2_values.json

Both arguments are REQUIRED and have no defaults, following the project rule that
no script is given a default for the thing it reads or writes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Committed artifacts. Named once, each with the role it plays.
# ---------------------------------------------------------------------------
FIG1_JSON = "paper/figures/fig1_values.json"
PAIRED_SEEDS = "results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json"
AUDIT_CSV = "results/audit_verdicts_rev3.csv"
DENOMINATORS = "paper/audit_denominators.tex"
MINIGRID_MANIFEST = "results/minigrid_run_20260722.manifest.json"
ESCALATION_MANIFEST = "results/escalation_run_20260726.manifest.json"

CELL = "qwen25-7b/gsm8k"


def _load_json(rel: str):
    return json.loads((ROOT / rel).read_text())


def _macros(rel: str) -> dict:
    """Parse \\newcommand{\\Name}{value} out of a generated macro ledger."""
    text = (ROOT / rel).read_text()
    out = {}
    for name, value in re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", text):
        out[name] = value
    return out


def _jsonl_cells(rel: str) -> int:
    """Count per-item cell JSONLs recorded in an archive manifest.

    The manifests are per-file records with a `path`; a run directory also holds
    a manifest and a lock file, so the JSONL filter is what isolates the cells.
    """
    manifest = _load_json(rel)
    names = [entry["path"] for entry in manifest["files"]]
    cells = sum(1 for n in names if n.endswith(".jsonl"))
    if cells == 0:
        raise SystemExit(f"{rel}: no .jsonl entries in the manifest")
    return cells


def collect_values() -> dict:
    """Read every figure value from a committed artifact, with provenance."""
    fig1 = _load_json(FIG1_JSON)["values"]
    seeds = _load_json(PAIRED_SEEDS)
    macros = _macros(DENOMINATORS)

    v = {}

    def put(name, value, source, key):
        v[name] = {"value": value, "source": source, "key": key}

    # --- the cell, as Figure 1 already reports it ------------------------
    # Every one of these is copied from the committed Figure 1 provenance
    # record, so the two figures cannot drift apart. fig1_values.json names the
    # primary artifact for each in its own "source" field; that field is carried
    # through here so the chain stays visible.
    # "alpha" is the registered ONE-SIDED TOST level from
    # scripts/audit_stats.py::ALPHA. It is not the bootstrap alpha below, and
    # the two must not be conflated: TOST at one-sided alpha corresponds to
    # containment of the (1 - 2*alpha) two-sided interval.
    for name in ("acc_gptq", "acc_awq", "net_awq_minus_gptq", "harmful",
                 "beneficial", "churn", "n_items", "required_n", "discordance",
                 "alpha"):
        entry = fig1[name]
        put(name, entry["value"], f"{FIG1_JSON} -> {entry['source']}",
            entry["key"])
    put("margin_pp", _load_json(FIG1_JSON)["margin_pp"], FIG1_JSON, "margin_pp")

    # --- the paired delta interval, read from the primary artifact --------
    # SIGN CONVENTION. paired_seeds stores GPTQ minus AWQ; every item-level
    # quantity above (harmful/beneficial/churn/net) is AWQ minus GPTQ, the
    # method-minus-baseline convention of flipeval/core.py that make_figure1.py
    # documents. The interval is therefore negated and its endpoints swapped, an
    # exact transformation of a percentile interval under x -> -x. Both forms are
    # recorded below so the negation is checkable.
    raw_ci = list(seeds["joint_confidence_intervals"]["accuracy_delta"])
    put("delta_ci_gptq_minus_awq", raw_ci, PAIRED_SEEDS,
        "joint_confidence_intervals.accuracy_delta")
    put("delta_ci_awq_minus_gptq", [-raw_ci[1], -raw_ci[0]], PAIRED_SEEDS,
        "negation of joint_confidence_intervals.accuracy_delta")
    put("ci_alpha", seeds["alpha"], PAIRED_SEEDS, "alpha")
    put("bootstrap_replicates", seeds["bootstrap_replicates"], PAIRED_SEEDS,
        "bootstrap_replicates")
    put("full_sample_delta_gptq_minus_awq", seeds["full_sample_accuracy_delta"],
        PAIRED_SEEDS, "full_sample_accuracy_delta")

    # CROSS-CHECK, not decoration: the aggregate delta in the primary artifact
    # must be the negation of the item-level net delta Figure 1 reports. If this
    # ever fails, one of the two figures is reporting the wrong direction.
    if abs(seeds["full_sample_accuracy_delta"]
           + fig1["net_awq_minus_gptq"]["value"]) > 1e-9:
        raise SystemExit(
            "sign check failed: paired_seeds full_sample_accuracy_delta "
            f"{seeds['full_sample_accuracy_delta']} is not the negation of "
            f"fig1 net_awq_minus_gptq {fig1['net_awq_minus_gptq']['value']}")

    # --- what the audit found in the field -------------------------------
    # Read from the sealed verdict CSV, then reconciled against the generated
    # macro ledger. Neither count is typed.
    rows = list(csv.DictReader((ROOT / AUDIT_CSV).open()))
    eligible = [r for r in rows if r["eligible"] == "True"]
    n_eligible = len(eligible)
    n_margin = sum(1 for r in eligible if r["margin_category"] == "1")
    n_per_item = sum(1 for r in eligible if r["v3_per_item_outputs"] == "yes")
    put("audit_eligible", n_eligible, AUDIT_CSV, "count of eligible == True")
    put("audit_prospective_margin", n_margin, AUDIT_CSV,
        "count of eligible rows with margin_category == 1")
    put("audit_per_item_task_matched", n_per_item, AUDIT_CSV,
        "count of eligible rows with v3_per_item_outputs == yes")
    expected = {
        "AuditEligible": n_eligible,
        "AuditProspectiveNumericMargin": n_margin,
        "AuditPerItemTaskMatched": n_per_item,
    }
    for macro, computed in expected.items():
        if int(macros[macro]) != computed:
            raise SystemExit(
                f"audit cross-check failed: {DENOMINATORS} \\{macro} = "
                f"{macros[macro]} but {AUDIT_CSV} gives {computed}")
    # The registered uniform audit margin must be the margin this figure draws.
    if float(macros["AuditMarginPP"]) != float(v["margin_pp"]["value"]):
        raise SystemExit(
            f"margin cross-check failed: \\AuditMarginPP = "
            f"{macros['AuditMarginPP']} but fig1_values.json margin_pp = "
            f"{v['margin_pp']['value']}")

    # --- what this paper releases in place of it -------------------------
    n_minigrid = _jsonl_cells(MINIGRID_MANIFEST)
    n_escalation = _jsonl_cells(ESCALATION_MANIFEST)
    put("per_item_cells_released", n_minigrid + n_escalation,
        f"{MINIGRID_MANIFEST} + {ESCALATION_MANIFEST}",
        "count of .jsonl entries in the two archived run manifests")

    return {
        "figure": "fig2_before_after",
        "cell": CELL,
        "margin_pp": v["margin_pp"]["value"],
        "generator": "scripts/make_figure2.py",
        "values": v,
    }


# ---------------------------------------------------------------------------
# TikZ emission.
#
# Plain TikZ plus arrows.meta, exactly the preamble paper/main.tex already loads.
# No pgfplots, no new package: an extra package is an extra way for the author's
# pinned build to fail.
#
# Colour repeats Figure 1's palette so the two figures read as one system, and
# for the same greyscale reason: relative luminance 0.2126R + 0.7152G + 0.0722B
# gives fharm (140,45,20) -> 0.28 and fben (125,178,219) -> 0.65, a separation of
# 0.37. Colour is never load-bearing here either -- every marked element carries
# its own words, and the "missing" column is marked by an em dash and the word
# "none", not by being grey.
# ---------------------------------------------------------------------------

PREAMBLE = r"""% GENERATED by scripts/make_figure2.py. DO NOT EDIT BY HAND.
% Regenerate:
%   python3 scripts/make_figure2.py \
%     --out-tex paper/figures/fig2_before_after.tex \
%     --out-json paper/figures/fig2_values.json
%
% Requires \usepackage{tikz} and \usetikzlibrary{arrows.meta} in the preamble,
% both already loaded by paper/main.tex. No other package is needed.
%
% Provenance for every number here is paper/figures/fig2_values.json.
% SOURCE: paper/figures/fig1_values.json (accuracies, flip rates, churn, n,
%   and the 2,730 planning requirement, itself emitted from
%   scripts/audit_stats.py::required_n_for_tost by scripts/make_figure1.py)
% SOURCE: results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json
%   (joint_confidence_intervals.accuracy_delta, alpha, bootstrap_replicates)
% SOURCE: results/audit_verdicts_rev3.csv (eligible sources; margin_category;
%   v3_per_item_outputs), cross-checked against paper/audit_denominators.tex
% SOURCE: results/minigrid_run_20260722.manifest.json and
%   results/escalation_run_20260726.manifest.json (per-item cell JSONL count)
%
% TWO WORDINGS ARE LOAD-BEARING AND MUST NOT BE SOFTENED:
%   row 4 -- the required n is a PLANNING requirement at an assumed true
%     difference of zero. It says the evaluation cannot support the claim. It is
%     NOT evidence that the two methods differ.
%   row 2 -- no committed artifact records a TOST verdict for this cell. The
%     interval drawn is the committed 95% paired bootstrap interval, which is not
%     the 90% two-sided interval TOST at one-sided alpha=.05 requires, so it
%     decides nothing about the TOST either way.
\definecolor{fharm}{RGB}{140,45,20}
\definecolor{fben}{RGB}{125,178,219}
\definecolor{fneutral}{RGB}{110,110,110}
\definecolor{frule}{RGB}{60,60,60}
"""

# Text metrics for Computer Modern at \scriptsize (8pt in an 11pt document).
# These are estimates and exist only so that row heights are derived from the
# text rather than guessed: a cell that gains a clause grows its row. The
# rendered page is still the authority -- see the note at the foot of this file.
CHAR_CM = 0.1345          # mean advance of a roman character at \scriptsize
BOLD_CM = 0.150           # the same for bold, which the column titles are set in
LINE_CM = 0.335           # \baselineskip at \scriptsize

# Vertical space row 2 buys for the drawn interval, on top of its text. Row 2
# reserves it and the row's own prose is placed below it, so the two must be
# the same number: they were both spelled 1.30 in two places, and raising one
# without the other would have printed the interval over the prose.
INTERVAL_H = 1.46

# The two column titles. Stated once: their height is measured from these and
# the measurement is only worth anything if it measures what is emitted.
TITLE_A = r"A\quad As reported today"
TITLE_B = r"B\quad The same evaluation, reported to the standard"


def label_tex(entry: dict) -> str:
    """The row label exactly as it is set: bold item number, \\quad, label.

    One function so the height measurement and the emitted node cannot drift
    apart. They did: the measurement used the bare label.
    """
    return rf"\textbf{{{entry['n']}}}\quad {entry['label']}"


def plain(text: str) -> str:
    """Strip enough LaTeX to estimate a printed length."""
    text = re.sub(r"\\[a-zA-Z]+\s*", " ", text)
    text = text.replace("$", "").replace("{", "").replace("}", "")
    text = text.replace("~", " ").replace("\\", "")
    return re.sub(r"\s+", " ", text).strip()


def nlines(text: str, width_cm: float, char_cm: float = CHAR_CM) -> int:
    """Estimated wrapped line count for `text` set in a `width_cm` measure.

    Greedy word wrapping, not a character-count division. The original model
    was `ceil(total_chars / chars_per_line)`, which assumes every line can be
    filled to its last column. TeX breaks at spaces, so a word that does not
    fit moves down whole and leaves the line before it short -- the estimate is
    therefore low exactly when a measure is narrow relative to its words.

    On 2026-08-14 that under-counted the row-1 label and both column titles by
    one line each. The row heights below are laid out from this count, so the
    separating rules were drawn through the text that had wrapped past them:
    the first proof struck a line through "today", "standard" and "gin".

    `char_cm` is a parameter because the column titles are set bold, which is
    wider than the roman advance CHAR_CM describes.
    """
    per_line = max(1.0, width_cm / char_cm)
    # \quad is 1em -- about two character widths here -- and plain() would
    # otherwise flatten it to a single space. Give it its own trailing space so
    # it stays attached to the item number it follows, which is where it is.
    words = plain(text.replace(r"\quad", "·· ")).split()
    if not words:
        return 1
    lines, used = 1, 0.0
    for word in words:
        need = len(word) if used == 0 else len(word) + 1
        if used > 0 and used + need > per_line:
            lines += 1
            used = float(len(word))
        else:
            used += need
    return lines


def fmt(value: float, places: int) -> str:
    """Fixed-point, with LaTeX thousands separators for integers."""
    if places == 0:
        return f"{int(round(value)):,}".replace(",", "{,}")
    return f"{value:.{places}f}"


def signed(value: float, places: int) -> str:
    """A signed number with a real minus sign, for maths mode."""
    return ("-" if value < 0 else "+") + fmt(abs(value), places)


def emit_tikz(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    out = [PREAMBLE]
    a = out.append

    margin = v["margin_pp"]
    net_pp = v["net_awq_minus_gptq"] * 100
    ci_lo, ci_hi = (x * 100 for x in v["delta_ci_awq_minus_gptq"])
    churn_pct = v["churn"] * 100
    harm_pct = v["harmful"] * 100
    ben_pct = v["beneficial"] * 100
    acc_g = v["acc_gptq"] * 100
    acc_a = v["acc_awq"] * 100
    n_run = v["n_items"]
    n_req = v["required_n"]
    # Two different levels, deliberately kept apart. conf_pct is the committed
    # bootstrap interval's own two-sided level (1 - bootstrap alpha). tost_pct is
    # the two-sided level TOST at one-sided alpha corresponds to, 1 - 2*alpha.
    conf_pct = int(round((1 - v["ci_alpha"]) * 100))
    tost_pct = int(round((1 - 2 * v["alpha"]) * 100))

    # ---------------- geometry -------------------------------------------
    # 12.6cm is the width Figure 1 uses and is just inside \textwidth for
    # article 11pt. Nothing here is scaled, so the figure cannot be silently
    # shrunk to fit.
    W = 12.6
    lab_x, lab_w = 0.04, 2.52         # the five lines of the standard
    a_box, a_x, a_w = 2.72, 2.86, 3.06   # column A, "as reported today"
    b_box, b_x, b_w = 6.16, 6.30, 6.24   # column B, the same run to the standard

    rows = []

    def row(number, label, col_a, col_b, extra=0.0):
        rows.append({"n": number, "label": label, "a": col_a, "b": col_b,
                     "extra": extra})

    row(1, "declare a margin",
        r"\textemdash\ none declared",
        rf"$\pm{fmt(margin, 0)}$ pp, declared in advance")

    # Row 2 carries the drawn interval, so it buys height for the axis on top
    # of whatever its text needs.
    row(2, "run the paired equivalence test at that margin",
        r"\textemdash\ no equivalence test is reported",
        rf"$\Delta = {signed(net_pp, 2)}$ pp (AWQ $-$ GPTQ), "
        rf"{conf_pct}\% paired bootstrap CI "
        rf"$[{signed(ci_lo, 2)}, {signed(ci_hi, 2)}]$ pp. "
        r"No TOST verdict is recorded for this cell, and this is not the "
        rf"{tost_pct}\% interval TOST would read.",
        extra=INTERVAL_H)

    row(3, "report churn beside net delta",
        rf"net delta ${signed(net_pp, 2)}$ pp \\ "
        rf"(GPTQ {fmt(acc_g, 2)}\%, AWQ {fmt(acc_a, 2)}\%)",
        rf"net delta ${signed(net_pp, 2)}$ pp \emph{{and}} churn "
        rf"{fmt(churn_pct, 2)}\%: {fmt(harm_pct, 2)}\% correct $\to$ wrong, "
        rf"{fmt(ben_pct, 2)}\% wrong $\to$ correct. The net is what is left "
        r"of the two.")

    row(4, "cite the sample size met against the size required",
        rf"$n = {fmt(n_run, 0)}$; no requirement cited",
        rf"${fmt(n_run, 0)}$ items evaluated against ${fmt(n_req, 0)}$ "
        rf"required at $\pm{fmt(margin, 0)}$ pp. That is a planning "
        r"requirement at an assumed true difference of zero: it says this "
        r"evaluation cannot support the claim, and it is \emph{not} evidence "
        r"that the two methods differ.")

    row(5, "release per-item outputs",
        r"\textemdash\ not released",
        rf"released: {fmt(v['per_item_cells_released'], 0)} per-item cell "
        r"JSONL files, one per cell of the controlled experiment")

    # Row heights follow from the text, taking whichever column wraps further.
    # Measure label_tex(), not entry["label"]: the emitted node carries a bold
    # item number and a \quad in front of the label, and measuring the bare
    # label ignored roughly three characters of it. Row 1 -- "declare a
    # margin", the shortest label and so the one with the least slack -- then
    # wrapped to two lines inside a box budgeted for one, and the rule below it
    # was drawn through the word "margin".
    for entry in rows:
        lines = max(nlines(label_tex(entry), lab_w),
                    entry["a"].count(r"\\") + 1 + nlines(
                        entry["a"].replace(r"\\", " "), a_w) - 1,
                    nlines(entry["b"], b_w))
        entry["h"] = lines * LINE_CM + 0.26 + entry["extra"]

    header = (r"Qwen2.5-7B on GSM8K, 4-bit GPTQ against 4-bit AWQ, "
              rf"${fmt(n_run, 0)}$ paired items, five calibration seeds. "
              r"One evaluation, reported twice. Column~A is the whole of the "
              r"report; column~B is the same run, same items, same numbers, "
              r"under the five-line standard.")
    footer = (r"\textbf{Nothing in column~B is a new experiment.} Every "
              r"quantity there was already produced by the run column~A "
              r"summarises; what changes is what is reported. Column~A is "
              r"complete as drawn: there is no further evidence behind it. "
              rf"Across the {fmt(v['audit_eligible'], 0)} eligible sources of "
              rf"our audit, {fmt(v['audit_prospective_margin'], 0)} declare a "
              rf"prospective numerical margin and "
              rf"{fmt(v['audit_per_item_task_matched'], 0)} release "
              r"task-matched per-item outputs.")

    h_header = nlines(header, W) * LINE_CM
    h_footer = nlines(footer, W) * LINE_CM
    # The column titles were budgeted a flat 0.42cm -- one line plus padding --
    # while both of them wrap to two at these measures, so the rule beneath
    # them was drawn across their second line. Measure them like every other
    # block instead of assuming. BOLD_CM, not CHAR_CM: these are set bold.
    h_titles = max(nlines(TITLE_A, a_w, BOLD_CM),
                   nlines(TITLE_B, b_w, BOLD_CM)) * LINE_CM + 0.085
    total = h_header + 0.22 + h_titles + 0.14 + sum(r["h"] for r in rows) \
        + 0.16 + h_footer
    top = total

    # [!tp], not [!t]. In the arXiv arm (plain article, \textheight 541pt) this
    # float measures 520pt -- 96% of the page -- so a top float leaves no room
    # for the text that must accompany it, LaTeX can never complete the page,
    # and it defers. Floats are placed in order, so a stuck Figure 2 took
    # Figure 3 with it: both landed in the appendix, 95 pages after the text
    # that cites them, and neither triggered a warning. "p" lets a float this
    # size take a page of its own near its reference. "t" is still tried first,
    # which is what the TMLR arm (wider measure, shorter float) uses.
    a(r"\begin{figure}[!tp]")
    a(r"\centering")
    a(r"\begin{tikzpicture}[")
    a(r"  x=1cm, y=1cm, line width=0.5pt,")
    a(r"  font=\scriptsize,")
    a(r"  ttl/.style={font=\scriptsize\bfseries, anchor=north west},")
    a(r"  lbl/.style={font=\scriptsize, anchor=north west},")
    a(r"  gone/.style={font=\scriptsize, text=fneutral, anchor=north west},")
    a(r"]")

    overruns = []

    def check(what, x_left, width, limit=W):
        if x_left + width > limit + 1e-9:
            overruns.append(
                f"{what}: right edge {x_left + width:.2f}cm exceeds "
                f"{limit:.2f}cm by {x_left + width - limit:.2f}cm")

    # ---------------- header ---------------------------------------------
    # inner sep=0 on every full-width node. TikZ adds its default inner sep
    # OUTSIDE a declared text width, which is what put Figure 1's atlas strip
    # 6.2pt into the right margin while every checked width fitted.
    a(rf"\node[anchor=north west, inner sep=0, text width={W}cm, "
      rf"font=\scriptsize] at (0,{top:.2f}) {{{header}}};")
    check("header", 0.0, W)
    y = top - h_header - 0.22

    # ---------------- column titles --------------------------------------
    a(rf"\node[ttl, text width={a_w}cm, inner sep=0] at ({a_x},{y:.2f}) "
      rf"{{{TITLE_A}}};")
    a(rf"\node[ttl, text width={b_w}cm, inner sep=0] at ({b_x},{y:.2f}) "
      rf"{{{TITLE_B}}};")
    check("column A title", a_x, a_w)
    check("column B title", b_x, b_w)
    y -= h_titles
    a(rf"\draw[frule!45, line width=0.5pt] (0,{y:.2f}) -- ({W},{y:.2f});")
    y -= 0.14

    # A single light frame around the emptier column, so the comparison is
    # visible before a word is read. It is a frame, not a fill: a fill would
    # make the column harder to read in print, and the "missing" state is
    # already carried by the words in it.
    a_frame_top = y + 0.10

    # ---------------- the five rows --------------------------------------
    for entry in rows:
        a(rf"\node[lbl, text width={lab_w}cm, inner sep=0] "
          rf"at ({lab_x},{y - 0.04:.2f}) "
          rf"{{{label_tex(entry)}}};")
        a(rf"\node[gone, text width={a_w}cm, inner sep=0] "
          rf"at ({a_x},{y - 0.04:.2f}) {{{entry['a']}}};")
        check(f"row {entry['n']} label", lab_x, lab_w, a_box)
        check(f"row {entry['n']} column A", a_x, a_w, b_box)

        if entry["n"] == 2:
            # The drawn interval sits above this row's text.
            _emit_interval(a, check, b_x, b_w, y - 0.04, margin, net_pp,
                           ci_lo, ci_hi)
            a(rf"\node[lbl, text width={b_w}cm, inner sep=0] "
              rf"at ({b_x},{y - 0.04 - INTERVAL_H:.2f}) {{{entry['b']}}};")
        else:
            a(rf"\node[lbl, text width={b_w}cm, inner sep=0] "
              rf"at ({b_x},{y - 0.04:.2f}) {{{entry['b']}}};")
        check(f"row {entry['n']} column B", b_x, b_w)

        y -= entry["h"]
        if entry is not rows[-1]:
            a(rf"\draw[frule!18, line width=0.3pt] (0,{y + 0.05:.2f}) -- "
              rf"({W},{y + 0.05:.2f});")

    a(rf"\draw[frule!25, rounded corners=1pt, line width=0.4pt] "
      rf"({a_box},{a_frame_top:.2f}) rectangle ({b_box - 0.10},{y + 0.02:.2f});")

    # ---------------- footer ---------------------------------------------
    a(rf"\draw[frule!45, line width=0.5pt] (0,{y - 0.02:.2f}) -- "
      rf"({W},{y - 0.02:.2f});")
    a(rf"\node[anchor=north west, inner sep=0, text width={W}cm, "
      rf"font=\scriptsize] at (0,{y - 0.16:.2f}) {{{footer}}};")
    check("footer", 0.0, W)

    a(r"\end{tikzpicture}")
    a(caption(data))
    a(r"\label{fig:standard}")
    a(r"\end{figure}")

    # Fail the build rather than emit a node that runs into the margin. This
    # guard sees declared widths only. It cannot see vertical collisions, and it
    # cannot see the page the figure lands on. TeX Live is installed at
    # ~/scratch/texlive (docs/PAPER_BUILD_ENVIRONMENT.md): render the figure
    # after changing its geometry and run paper/tools/check_layout.py. Ten
    # defects in Figure 1 were found by rendering after a clean guard pass.
    if overruns:
        raise SystemExit("figure geometry: node(s) outside their column:\n  "
                         + "\n  ".join(overruns))

    return "\n".join(out) + "\n"


def _emit_interval(a, check, x0, width, y_top, margin, net_pp, ci_lo, ci_hi):
    """Draw the declared margin, the observed delta and its bootstrap interval.

    The axis is symmetric about zero and wide enough to hold both the margin and
    the whole interval, so neither is clipped and the margin is never redrawn at
    a scale that flatters it.
    """
    span = max(margin, abs(ci_lo), abs(ci_hi)) * 1.20
    ax_l, ax_r = x0 + 0.10, x0 + 5.30
    mid = (ax_l + ax_r) / 2.0
    unit = (ax_r - ax_l) / (2 * span)

    def px(pp):
        return mid + pp * unit

    # 0.78, not 0.62. The group is positioned from its band, but the topmost
    # ink is the "declared equivalence region" caption two steps above it
    # (band_h + 0.12 + the cap height). At 0.62 that caption reached to within
    # ~1.3pt of the row rule above, which prints as touching it. This offset is
    # what holds the caption clear, so it moves with band_h and the 0.12, not
    # independently of them.
    band_y = y_top - 0.78
    band_h = 0.30

    # The declared equivalence region.
    a(rf"\draw[fill=frule!8, draw=none] ({px(-margin):.3f},{band_y:.3f}) "
      rf"rectangle ({px(margin):.3f},{band_y + band_h:.3f});")
    for edge in (-margin, margin):
        a(rf"\draw[frule!70, line width=0.5pt, dash pattern=on 1.4pt off 1.0pt] "
          rf"({px(edge):.3f},{band_y - 0.10:.3f}) -- "
          rf"({px(edge):.3f},{band_y + band_h + 0.10:.3f});")
    a(rf"\node[font=\scriptsize, anchor=south] at ({mid:.3f},"
      rf"{band_y + band_h + 0.12:.3f}) "
      rf"{{declared equivalence region, $\pm{fmt(margin, 0)}$ pp}};")

    # The zero line and the axis.
    a(rf"\draw[frule!40, line width=0.4pt] ({ax_l:.3f},{band_y - 0.02:.3f}) -- "
      rf"({ax_r:.3f},{band_y - 0.02:.3f});")
    for tick in (-margin, 0.0, margin):
        a(rf"\node[font=\scriptsize, anchor=north] at ({px(tick):.3f},"
          rf"{band_y - 0.06:.3f}) {{${signed(tick, 0) if tick else '0'}$}};")

    # The observed delta and its interval.
    y_pt = band_y + band_h / 2.0
    a(rf"\draw[frule!85, line width=0.9pt] ({px(ci_lo):.3f},{y_pt:.3f}) -- "
      rf"({px(ci_hi):.3f},{y_pt:.3f});")
    for end in (ci_lo, ci_hi):
        a(rf"\draw[frule!85, line width=0.9pt] ({px(end):.3f},"
          rf"{y_pt - 0.09:.3f}) -- ({px(end):.3f},{y_pt + 0.09:.3f});")
    a(rf"\draw[fill=fharm, draw=fharm] ({px(net_pp):.3f},{y_pt:.3f}) "
      r"circle (0.075);")
    a(rf"\node[font=\scriptsize, anchor=west] at ({ax_r + 0.10:.3f},"
      rf"{y_pt:.3f}) {{pp}};")
    check("row 2 interval axis", ax_r + 0.10, 0.40)


def caption(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    margin = v["margin_pp"]
    net_pp = abs(v["net_awq_minus_gptq"]) * 100
    return (
        r"\caption{\textbf{The same evaluation, before and after the "
        r"reporting standard.} Both columns describe one registered cell: "
        r"Qwen2.5-7B on GSM8K, 4-bit GPTQ against 4-bit AWQ, "
        r"$" + fmt(v["n_items"], 0) + r"$ paired items. \textbf{A}~is the "
        r"aggregate report (two accuracies and a net delta of "
        r"$" + fmt(net_pp, 2) + r"$~pp), and it is complete: there is no "
        r"further evidence behind it. \textbf{B}~is the same run reported "
        r"under the five lines of \S\ref{sec:conclusion}, and it needs no "
        r"additional experiment. Row~2 draws the declared "
        r"$\pm" + fmt(margin, 0) + r"$~pp margin together with the observed "
        r"paired delta and the committed "
        + str(int(round((1 - v["ci_alpha"]) * 100))) +
        r"\% percentile-bootstrap interval for it; \emph{no TOST verdict "
        r"exists for this cell}, and that interval is not the "
        + str(int(round((1 - 2 * v["alpha"]) * 100))) + r"\% two-sided "
        r"interval TOST at one-sided $\alpha=" + f"{v['alpha']:.2f}"[1:] +
        r"$ requires "
        r"(\S\ref{sec:cert:method}), so it settles the equivalence question "
        r"in neither direction. Row~4's "
        r"$" + fmt(v["required_n"], 0) + r"$ is a \emph{planning} requirement "
        r"computed at an assumed true difference of zero: it says this "
        r"evaluation cannot support an equivalence claim at "
        r"$\pm" + fmt(margin, 0) + r"$~pp, and it is not evidence that the "
        r"two methods differ. Figure~\ref{fig:cancellation} decomposes the "
        r"same cell; every value here is read from the artifacts recorded in "
        r"\texttt{paper/figures/fig2\_values.json}.}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-tex", required=True,
                        help="destination for the TikZ figure (required)")
    parser.add_argument("--out-json", required=True,
                        help="destination for the provenance record (required)")
    args = parser.parse_args()

    data = collect_values()
    Path(args.out_tex).write_text(emit_tikz(data))
    Path(args.out_json).write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"FIGURE2: wrote {args.out_tex} and {args.out_json}")
    values = data["values"]
    print(f"FIGURE2: cell={data['cell']} "
          f"n={values['n_items']['value']} "
          f"required_n={values['required_n']['value']} "
          f"churn={values['churn']['value']} "
          f"per_item_cells={values['per_item_cells_released']['value']}")


if __name__ == "__main__":
    main()
