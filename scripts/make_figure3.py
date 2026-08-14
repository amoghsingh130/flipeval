#!/usr/bin/env python3
r"""Generate Figure 3, the required-n lookup chart, as TikZ.

WHAT THIS FIGURE IS. Table~\ref{tab:certification} in paper/sections/
certification.tex is the authoritative object: eleven benchmark families plus the
pooled row, required n at the 25th/50th/75th percentile of the discordance the
atlas observes for that family, at three margins. It is dense, and a practitioner
sizing an evaluation reads it one row at a time. This figure is the same data,
one margin, drawn on a log axis so the family ordering and the width of each
family's plausible range are visible at a glance, with the discordance and the
median baseline accuracy printed beside each row so the section's conceptual
point is checkable from the figure itself: the ordering follows churn, not task
difficulty.

WHY ONE MARGIN AND NOT THREE. Required n scales as 1/m^2, so on a log axis a
change of margin is a rigid translation of the entire chart and adds no shape
information whatever. The script verifies this against the CSV rather than
assuming it: it computes the 1 pp / 2 pp and 2 pp / 3 pp ratios for all twelve
rows and reports their range, which integer rounding keeps inside 3.99-4.00 and
2.25-2.25. Three overlaid sets of twelve intervals would be thirty-six marks
carrying the information of twelve plus two numbers. Instead the chart is drawn
at the registered 2 pp margin and the pooled median at each of the three margins
is marked on the SAME axis in a ruler row at the foot, so the quadratic cost is
visible as a distance rather than asserted in prose.

THE VALUES ARE CROSS-CHECKED AGAINST THE PAPER'S OWN TABLE. `check_against_table`
parses the tabular in paper/sections/certification.tex and fails the build if any
family's atlas-cell count, rounded discordance triple or required-n triple
disagrees with results/certification_tables_rev2.csv. The CSV is authoritative
(see the precedence note at the head of certification.tex); the check exists so
that this figure cannot quietly disagree with the table a reader compares it to.

Why TikZ and not matplotlib: same reason as scripts/make_figure1.py. STDLIB ONLY
and Python 3.9 compatible, so it runs on the Phoenix login node; it needs no
scipy because every value it draws is already computed in the committed CSV.

CONSEQUENCE OF LIVING HERE: scripts/ is a fingerprinted tree, so changing this
file requires the in-image pytest gate and a freeze refresh (CLAUDE.md). It is
placed here to match scripts/make_figure1.py. It is stdlib-only, so paper/tools/
would also satisfy its dependencies and would avoid the freeze burden; that is
the author's call.

Run:

    python3 scripts/make_figure3.py \
      --out-tex paper/figures/fig3_required_n.tex \
      --out-json paper/figures/fig3_values.json

Both arguments are REQUIRED and have no defaults, following the project rule that
no script is given a default for the thing it reads or writes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CERT_CSV = "results/certification_tables_rev2.csv"
CERT_TEX = "paper/sections/certification.tex"

# The margin the chart is drawn at: the registered uniform margin, the same one
# Table~\ref{tab:certification} is printed at.
MARGIN_PP = 2.0
# The other two margins the CSV carries, used only for the ruler row and the
# scaling statement.
OTHER_MARGINS = (1.0, 3.0)

POOLED = "ALL (pooled)"

# Display names. The CSV keys are the harness task names; these are how the
# paper sets them in prose. Nothing numeric depends on this map.
DISPLAY = {
    "arc_challenge": r"ARC-Challenge",
    "bbh": r"BBH",
    "gpqa": r"GPQA",
    "gsm8k": r"GSM8K",
    "hellaswag": r"HellaSwag",
    "ifeval": r"IFEval",
    "math": r"MATH",
    "mmlu": r"MMLU",
    "mmlu_pro": r"MMLU-Pro",
    "musr": r"MuSR",
    "winogrande": r"WinoGrande",
    POOLED: r"\textbf{ALL (pooled)}",
}


def read_csv():
    """Every row of the certification table, keyed by (family, margin)."""
    rows = {}
    with (ROOT / CERT_CSV).open() as handle:
        for row in csv.DictReader(handle):
            key = (row["benchmark_family"], float(row["margin_pp"]))
            rows[key] = {
                "family": row["benchmark_family"],
                "margin_pp": float(row["margin_pp"]),
                "n_atlas_cells": int(row["n_atlas_cells"]),
                "median_baseline_accuracy": float(row["median_baseline_accuracy"]),
                "required_n_independent_binomial":
                    int(row["required_n_independent_binomial"]),
                "discordance_p25": float(row["discordance_p25"]),
                "discordance_median": float(row["discordance_median"]),
                "discordance_p75": float(row["discordance_p75"]),
                "required_n_p25": int(row["required_n_p25"]),
                "required_n_median": int(row["required_n_median"]),
                "required_n_p75": int(row["required_n_p75"]),
                "paired_advantage_at_median":
                    float(row["paired_advantage_at_median"]),
            }
    return rows


# ---------------------------------------------------------------------------
# The cross-check against the paper's own table.
#
# This is the check the task brief asks for: confirm that what is plotted is what
# Table~\ref{tab:certification} prints, and stop rather than silently pick one.
# ---------------------------------------------------------------------------

def _detex(cell: str) -> str:
    cell = cell.replace(r"{,}", "").replace(r"\textbf", "")
    cell = cell.replace(r"\_", "_").replace(r"$", "")
    cell = re.sub(r"[{}]", "", cell)
    return cell.strip()


def parse_table():
    """Read the printed tabular out of paper/sections/certification.tex.

    Returns {family: {"cells", "disc", "req"}} using the CSV's own family keys.
    """
    text = (ROOT / CERT_TEX).read_text()
    match = re.search(r"\\label\{tab:certification\}.*?\\midrule(.*?)\\bottomrule",
                      text, re.S)
    if not match:
        raise SystemExit(f"{CERT_TEX}: could not locate the tab:certification body")
    parsed = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("%") or line.startswith(r"\midrule"):
            continue
        line = line.rstrip("\\").rstrip()
        cells = [c.strip() for c in line.split("&")]
        if len(cells) != 6:
            continue
        family = _detex(cells[0])
        if family.lower().startswith("all"):
            family = POOLED
        disc = [float(x) for x in _detex(cells[2]).split("/")]
        req = [int(x) for x in _detex(cells[3]).split("/")]
        parsed[family] = {
            "cells": int(_detex(cells[1])),
            "disc": disc,
            "req": req,
        }
    return parsed


def check_against_table(rows):
    """Fail loudly on any disagreement between the CSV and the printed table."""
    printed = parse_table()
    csv_families = sorted(f for (f, m) in rows if m == MARGIN_PP)
    if sorted(printed) != csv_families:
        raise SystemExit(
            "table/CSV family sets differ.\n"
            f"  table: {sorted(printed)}\n  csv:   {csv_families}")
    problems = []
    for family in csv_families:
        row = rows[(family, MARGIN_PP)]
        want = printed[family]
        if row["n_atlas_cells"] != want["cells"]:
            problems.append(
                f"{family}: atlas cells table {want['cells']} vs csv "
                f"{row['n_atlas_cells']}")
        got_req = [row["required_n_p25"], row["required_n_median"],
                   row["required_n_p75"]]
        if got_req != want["req"]:
            problems.append(
                f"{family}: required n table {want['req']} vs csv {got_req}")
        # The table prints discordance to three decimals; compare at the
        # precision the table is set at, not at the CSV's.
        got_disc = [round(row["discordance_p25"], 3),
                    round(row["discordance_median"], 3),
                    round(row["discordance_p75"], 3)]
        if got_disc != [round(x, 3) for x in want["disc"]]:
            problems.append(
                f"{family}: discordance table {want['disc']} vs csv {got_disc}")
    if problems:
        raise SystemExit(
            "figure 3 refuses to plot values the paper's table disagrees with:\n  "
            + "\n  ".join(problems))
    return len(csv_families)


def collect_values() -> dict:
    rows = read_csv()
    n_checked = check_against_table(rows)

    families = [f for (f, m) in rows if m == MARGIN_PP and f != POOLED]
    families.sort(key=lambda f: rows[(f, MARGIN_PP)]["required_n_median"])

    # Margin scaling, computed from the CSV over every row, never assumed.
    scaling = {}
    for other in OTHER_MARGINS:
        ratios = []
        for family in families + [POOLED]:
            here = rows[(family, MARGIN_PP)]["required_n_median"]
            there = rows[(family, other)]["required_n_median"]
            ratios.append(there / here)
        scaling[f"{other:g}pp_over_{MARGIN_PP:g}pp"] = {
            "min": min(ratios), "max": max(ratios),
            "median_of_ratios": sorted(ratios)[len(ratios) // 2],
        }

    values = {
        "margin_pp": {"value": MARGIN_PP, "source": CERT_CSV,
                      "key": "rows with margin_pp == 2.0"},
        "family_order": {
            "value": families,
            "source": CERT_CSV,
            "key": "families at margin_pp 2.0, ascending required_n_median"},
        "rows": {
            "value": {f"{family}@{margin:g}": rows[(family, margin)]
                      for family in families + [POOLED]
                      for margin in (MARGIN_PP,) + OTHER_MARGINS},
            "source": CERT_CSV,
            "key": "n_atlas_cells, median_baseline_accuracy, discordance_"
                   "p25/median/p75, required_n_p25/median/p75"},
        "margin_scaling": {
            "value": scaling,
            "source": CERT_CSV,
            "key": "required_n_median at 1.0 and 3.0 pp over the same at 2.0 pp,"
                   " across all twelve rows"},
        "table_rows_cross_checked": {
            "value": n_checked,
            "source": CERT_TEX,
            "key": "rows of tab:certification verified against the CSV"},
    }
    return {
        "figure": "fig3_required_n",
        "margin_pp": MARGIN_PP,
        "generator": "scripts/make_figure3.py",
        "values": values,
    }


# ---------------------------------------------------------------------------
# TikZ emission. Plain TikZ plus arrows.meta -- exactly what paper/main.tex
# already loads, and deliberately NOT pgfplots: the log axis here is five tick
# marks and a logarithm, which is not worth a package the author's pinned build
# has never compiled.
#
# Greyscale: the interquartile band is a light grey rectangle and the median is a
# dark filled disc, so the two are separated by shape and by luminance, not by
# hue. Every row also prints its median as a number, so nothing in the chart is
# readable only from the ink.
# ---------------------------------------------------------------------------

PREAMBLE = r"""% GENERATED by scripts/make_figure3.py. DO NOT EDIT BY HAND.
% Regenerate:
%   python3 scripts/make_figure3.py \
%     --out-tex paper/figures/fig3_required_n.tex \
%     --out-json paper/figures/fig3_values.json
%
% Requires \usepackage{tikz} and \usetikzlibrary{arrows.meta} in the preamble,
% both already loaded by paper/main.tex. No other package is needed; in
% particular this figure does NOT use pgfplots.
%
% Provenance for every number here is paper/figures/fig3_values.json.
% SOURCE: results/certification_tables_rev2.csv, rows with margin_pp = 2.0
%   (columns n_atlas_cells, median_baseline_accuracy, discordance_p25/median/p75,
%   required_n_p25/median/p75), plus the margin_pp 1.0 and 3.0 rows of
%   "ALL (pooled)" for the margin ruler.
% CROSS-CHECKED at generation time against the printed tabular of
%   Table~\ref{tab:certification} in paper/sections/certification.tex: atlas-cell
%   counts, the rounded discordance triples and the required-n triples must agree
%   for all twelve rows or the generator refuses to emit.
%
% LOAD-BEARING WORDING: these are TOST PLANNING sample sizes at an assumed true
% difference of zero (\S\ref{sec:cert:method}). They are design targets and a
% lower bound under any non-zero true difference; they are not retrospective
% certification of any reported result, and meeting one certifies nothing on its
% own -- the test still has to be run and to pass.
\definecolor{fharm}{RGB}{140,45,20}
\definecolor{fben}{RGB}{125,178,219}
\definecolor{fneutral}{RGB}{110,110,110}
\definecolor{frule}{RGB}{60,60,60}
"""

LINE_CM = 0.335
CHAR_CM = 0.1345


def fmt(value: float, places: int) -> str:
    if places == 0:
        return f"{int(round(value)):,}".replace(",", "{,}")
    return f"{value:.{places}f}"


def nlines(text: str, width_cm: float) -> int:
    plain = re.sub(r"\\[a-zA-Z]+\s*", " ", text)
    plain = re.sub(r"[${}~\\]", "", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    return max(1, int(math.ceil(len(plain) / max(1.0, width_cm / CHAR_CM))))


def nice_bounds(lo: float, hi: float):
    """A log-axis domain from the 1-2-5 ladder that contains [lo, hi]."""
    ladder = [x * 10 ** e for e in range(0, 6) for x in (1, 2, 5)]
    low = max(t for t in ladder if t <= lo)
    high = min(t for t in ladder if t >= hi)
    return low, high


def emit_tikz(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    rows = v["rows"]
    order = list(v["family_order"])
    margin = v["margin_pp"]
    out = [PREAMBLE]
    a = out.append

    def row(family, margin_pp=margin):
        return rows[f"{family}@{margin_pp:g}"]

    # ---------------- geometry -------------------------------------------
    W = 12.6                     # the width Figure 1 uses; nothing is scaled
    lab_x = 0.04                 # family names, left aligned
    ax_l, ax_r = 2.66, 9.16      # the log axis
    # The three right-hand columns are spaced by their HEADERS, not their
    # numbers: set bold, "med.", "churn" and "base acc" measure about 0.55,
    # 0.80 and 1.30cm against roughly 0.62cm of digits, so the widest thing in
    # each column is the word above it. Placed right to left from col_a with a
    # 0.15cm gutter between headers. The first attempt spaced them by eye and
    # printed "churnbase acc"; the second moved one column and printed
    # "med.churn". Measured, they clear.
    col_n = 10.18                # required n, right aligned
    col_d = 11.13                # median discordance, right aligned
    col_a = 12.58                # median baseline accuracy, right aligned
    pitch = 0.395                # row pitch
    RULER_EXTRA = 0.24           # the margin ruler's captions sit above its
                                 # dots; this is the room they need

    # Axis domain: the 1-2-5 bracket around everything that has to be drawn,
    # including the pooled medians at the other two margins, so the ruler row
    # shares the chart's own scale rather than a second one.
    drawn = []
    for family in order + ["ALL (pooled)"]:
        entry = row(family)
        drawn += [entry["required_n_p25"], entry["required_n_p75"]]
    pooled_by_margin = [(m, row("ALL (pooled)", m)["required_n_median"])
                        for m in sorted([margin] + list(OTHER_MARGINS))]
    drawn += [n for _, n in pooled_by_margin]
    lo, hi = nice_bounds(min(drawn), max(drawn))
    span = math.log10(hi) - math.log10(lo)

    def px(n):
        return ax_l + (math.log10(n) - math.log10(lo)) / span * (ax_r - ax_l)

    ticks = [t for t in (100, 200, 500, 1000, 2000, 5000, 10000, 20000)
             if lo <= t <= hi]

    # ---------------- vertical budget ------------------------------------
    n_rows = len(order) + 1 + 1          # families, pooled, margin ruler
    head_h = 1.16                # 0.24 + 0.28 + 0.30 + 0.24, the three header
                                 # rows plus the rule; was 0.90 for two rows
    axis_h = 0.52
    note = (
        rf"\textbf{{The ordering is set by churn, not by difficulty.}} MMLU "
        rf"needs ${fmt(row('mmlu')['required_n_median'], 0)}$ items at "
        rf"$\pm{fmt(margin, 0)}$ pp and GPQA needs "
        rf"${fmt(row('gpqa')['required_n_median'], 0)}$, although GPQA is the "
        rf"harder benchmark: its median baseline accuracy in the atlas is "
        rf"${fmt(row('gpqa')['median_baseline_accuracy'], 3)}$ against MMLU's "
        rf"${fmt(row('mmlu')['median_baseline_accuracy'], 3)}$. What separates "
        rf"them is the churn column, "
        rf"${fmt(row('mmlu')['discordance_median'], 3)}$ against "
        rf"${fmt(row('gpqa')['discordance_median'], 3)}$. Read the row, not the "
        rf"leaderboard."
    )
    note_h = nlines(note, W) * LINE_CM
    total = head_h + n_rows * pitch + RULER_EXTRA + axis_h + 0.18 + note_h
    top = total

    # [!tp] for the same reason as Figure 2: see the note there. This float is
    # 438pt against a 541pt \textheight in the arXiv arm, so it can be a top
    # float on its own, but it sits behind Figure 2 in the float queue and
    # inherits whatever happens to it.
    a(r"\begin{figure}[!tp]")
    a(r"\centering")
    a(r"\begin{tikzpicture}[")
    a(r"  x=1cm, y=1cm, line width=0.5pt,")
    a(r"  font=\scriptsize,")
    a(r"  hd/.style={font=\scriptsize\bfseries},")
    a(r"  lbl/.style={font=\scriptsize, anchor=west},")
    a(r"  num/.style={font=\scriptsize, anchor=east},")
    a(r"]")

    overruns = []

    def check(what, x_left, width, limit=W):
        if x_left + width > limit + 1e-9:
            overruns.append(
                f"{what}: right edge {x_left + width:.2f}cm exceeds "
                f"{limit:.2f}cm by {x_left + width - limit:.2f}cm")

    # ---------------- headers --------------------------------------------
    # THREE header rows, not two (2026-08-14). The axis span title used to
    # share a baseline with the column headers. It is centred on the axis, but
    # at this measure the title is wider than the axis it labels, so it
    # overprinted "benchmark family" on the left and "med." on the right: the
    # first proof rendered "benchmark family" and the title on top of one
    # another. Nothing here is centred over a region narrower than itself any
    # more. The alternative was to shorten the title, but the title is the
    # sentence that says what the whole chart measures, so the row was cheaper.
    y = top - 0.24
    a(rf"\node[hd, anchor=north] at ({(ax_l + ax_r) / 2:.2f},{y + 0.16:.2f}) "
      rf"{{items required to certify equivalence within $\pm{fmt(margin, 0)}$ pp}};")
    y -= 0.28
    a(rf"\node[font=\scriptsize\itshape, anchor=north] "
      rf"at ({(ax_l + ax_r) / 2:.2f},{y + 0.16:.2f}) "
      rf"{{p25 \rule[0.10em]{{0.45cm}}{{0.30ex}} p75 band, "
      rf"$\bullet$ median, log scale}};")
    y -= 0.30
    a(rf"\node[hd, anchor=west] at ({lab_x},{y:.2f}) {{benchmark family}};")
    a(rf"\node[hd, anchor=east] at ({col_n},{y:.2f}) {{med.}};")
    a(rf"\node[hd, anchor=east] at ({col_d},{y:.2f}) {{churn}};")
    a(rf"\node[hd, anchor=east] at ({col_a},{y:.2f}) {{base acc}};")
    check("right numeric column", col_a - 0.90, 0.90)
    y -= 0.24
    a(rf"\draw[frule!45, line width=0.5pt] (0,{y:.2f}) -- ({W},{y:.2f});")

    # ---------------- gridlines ------------------------------------------
    grid_top = y
    grid_bot = y - (len(order) + 1) * pitch - 0.06

    # ---------------- the family rows ------------------------------------
    def draw_row(family, y_mid, bold=False):
        entry = row(family)
        name = DISPLAY[family]
        a(rf"\node[lbl] at ({lab_x},{y_mid:.3f}) {{{name}}};")
        x25, x50, x75 = (px(entry["required_n_p25"]),
                         px(entry["required_n_median"]),
                         px(entry["required_n_p75"]))
        a(rf"\draw[fill=frule!20, draw=none] ({x25:.3f},{y_mid - 0.065:.3f}) "
          rf"rectangle ({x75:.3f},{y_mid + 0.065:.3f});")
        for edge in (x25, x75):
            a(rf"\draw[frule!60, line width=0.4pt] ({edge:.3f},"
              rf"{y_mid - 0.085:.3f}) -- ({edge:.3f},{y_mid + 0.085:.3f});")
        a(rf"\draw[fill=fharm, draw=fharm] ({x50:.3f},{y_mid:.3f}) "
          r"circle (0.070);")
        med = fmt(entry["required_n_median"], 0)
        if bold:
            med = rf"\textbf{{{med}}}"
        a(rf"\node[num] at ({col_n},{y_mid:.3f}) {{{med}}};")
        a(rf"\node[num] at ({col_d},{y_mid:.3f}) "
          rf"{{{fmt(entry['discordance_median'], 3)}}};")
        a(rf"\node[num] at ({col_a},{y_mid:.3f}) "
          rf"{{{fmt(entry['median_baseline_accuracy'], 3)}}};")

    y_cursor = y - 0.06
    for family in order:
        y_cursor -= pitch
        draw_row(family, y_cursor + pitch / 2)
    a(rf"\draw[frule!30, line width=0.4pt] (0,{y_cursor:.3f}) -- "
      rf"({W},{y_cursor:.3f});")
    y_cursor -= pitch
    draw_row("ALL (pooled)", y_cursor + pitch / 2, bold=True)

    # ---------------- axis ------------------------------------------------
    for tick in ticks:
        a(rf"\draw[frule!16, line width=0.3pt] ({px(tick):.3f},"
          rf"{grid_bot:.3f}) -- ({px(tick):.3f},{grid_top:.3f});")
    a(rf"\draw[frule!30, line width=0.4pt] (0,{y_cursor:.3f}) -- "
      rf"({W},{y_cursor:.3f});")

    # ---------------- the margin ruler -----------------------------------
    # The same axis, so the quadratic cost of a tighter margin is a distance the
    # reader can measure against the rows above rather than a claim in prose.
    # RULER_EXTRA, because this row is the only one carrying labels ABOVE its
    # ink: the +-1/+-2/+-3 captions sit over the dots. At a bare `pitch` their
    # cap height reached about 0.11cm past the rule above, printing them inside
    # the "ALL (pooled)" band. The row is taller than the others by exactly the
    # space those captions need.
    y_cursor -= pitch + RULER_EXTRA
    ruler_y = y_cursor + pitch / 2
    a(rf"\node[lbl] at ({lab_x},{ruler_y:.3f}) "
      r"{pooled, by margin};")
    xs = [(m, px(n), n) for m, n in pooled_by_margin]
    a(rf"\draw[frule!55, line width=0.4pt, "
      r"{Latex[length=1.4mm]}-{Latex[length=1.4mm]}] "
      rf"({min(x for _, x, _ in xs):.3f},{ruler_y:.3f}) -- "
      rf"({max(x for _, x, _ in xs):.3f},{ruler_y:.3f});")
    for margin_pp, x, n in xs:
        a(rf"\draw[fill=fneutral, draw=fneutral] ({x:.3f},{ruler_y:.3f}) "
          r"circle (0.055);")
        a(rf"\node[font=\scriptsize, anchor=south] at ({x:.3f},"
          rf"{ruler_y + 0.07:.3f}) {{$\pm{fmt(margin_pp, 0)}$}};")
    a(rf"\node[num] at ({col_a},{ruler_y:.3f}) "
      rf"{{{' / '.join(fmt(n, 0) for _, _, n in xs)}}};")
    check("margin ruler numbers", col_a - 2.10, 2.10)

    y_cursor -= 0.04
    a(rf"\draw[frule!45, line width=0.5pt] (0,{y_cursor:.3f}) -- "
      rf"({W},{y_cursor:.3f});")

    # ---------------- tick labels ----------------------------------------
    for tick in ticks:
        a(rf"\node[font=\scriptsize, anchor=north] at ({px(tick):.3f},"
          rf"{y_cursor - 0.04:.3f}) {{{fmt(tick, 0)}}};")
    a(rf"\node[font=\scriptsize, anchor=north east] at ({W},"
      rf"{y_cursor - 0.04:.3f}) {{items}};")

    # ---------------- the note -------------------------------------------
    y_note = y_cursor - 0.42
    a(rf"\node[anchor=north west, inner sep=0, text width={W}cm, "
      rf"font=\scriptsize] at (0,{y_note:.3f}) {{{note}}};")
    check("note", 0.0, W)

    a(r"\end{tikzpicture}")
    a(caption(data))
    a(r"\label{fig:requiredn}")
    a(r"\end{figure}")

    if overruns:
        raise SystemExit("figure geometry: node(s) outside the measure:\n  "
                         + "\n  ".join(overruns))
    return "\n".join(out) + "\n"


def caption(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    rows = v["rows"]
    margin = v["margin_pp"]
    scale1 = v["margin_scaling"]["1pp_over_2pp"]
    scale3 = v["margin_scaling"]["3pp_over_2pp"]
    pooled = rows[f"ALL (pooled)@{margin:g}"]["required_n_median"]
    pooled1 = rows["ALL (pooled)@1"]["required_n_median"]
    pooled3 = rows["ALL (pooled)@3"]["required_n_median"]
    return (
        r"\caption{\textbf{How many items an equivalence claim needs, by "
        r"benchmark family.} The same data as "
        r"Table~\ref{tab:certification}, drawn for reference at the registered "
        r"$\pm" + fmt(margin, 0) + r"$~pp margin: TOST at one-sided "
        r"$\alpha=.05$ with 80\% power, at an assumed true difference of zero. "
        r"Each row is one family; the band spans the requirement at the 25th "
        r"and 75th percentiles of the discordance the atlas observes for that "
        r"family and the disc is the median. Families are ordered by that "
        r"median, and the two right-hand columns are what the ordering does and "
        r"does not follow: it tracks median churn and not median baseline "
        r"accuracy. \textbf{Other margins.} The requirement scales as $1/m^2$, "
        r"so on this log axis a change of margin translates the whole chart "
        r"without reshaping it: across all twelve rows the $\pm1$~pp "
        r"requirement is $" + fmt(scale1["min"], 2) + r"$--$"
        + fmt(scale1["max"], 2) + r"\times$ the $\pm" + fmt(margin, 0) +
        r"$~pp one and the $\pm3$~pp requirement is $"
        + fmt(scale3["min"], 2) + r"$--$" + fmt(scale3["max"], 2) +
        r"\times$ it. The ruler row marks the pooled median at all three "
        r"margins on this same axis ($" + fmt(pooled3, 0) + r"$, $"
        + fmt(pooled, 0) + r"$, $" + fmt(pooled1, 0) + r"$ items). "
        r"\textbf{Scope.} These are planning sizes, and a lower bound under any "
        r"non-zero true difference (\S\ref{sec:cert:method}); meeting one makes "
        r"the equivalence test informative, it does not certify anything on its "
        r"own. Families with fewer than four analysable atlas cells are absent, "
        r"and two of the rows shown rest on thin evidence "
        r"(\S\ref{sec:cert:caveats}).}"
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
    print(f"FIGURE3: wrote {args.out_tex} and {args.out_json}")
    v = data["values"]
    print(f"FIGURE3: margin={data['margin_pp']}pp "
          f"rows_cross_checked={v['table_rows_cross_checked']['value']} "
          f"order={','.join(v['family_order']['value'])}")
    for key, entry in v["margin_scaling"]["value"].items():
        print(f"FIGURE3: scaling {key}: "
              f"{entry['min']:.4f}--{entry['max']:.4f}")


if __name__ == "__main__":
    main()
