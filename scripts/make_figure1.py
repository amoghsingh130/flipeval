#!/usr/bin/env python3
"""Generate the flagship Figure 1 as TikZ, from committed artifacts only.

Why TikZ and not matplotlib. There is no LaTeX on the Phoenix login node and
none inside the pinned image, and the image has no matplotlib either (probe job
11675341). A TikZ figure is emitted as source here and rasterised to vector by
whatever machine eventually runs pdflatex, so the figure is buildable now and
publication-quality later. Nothing in this file renders anything.

Why it lives in scripts/ and not paper/tools/. paper/tools/ is deliberately
stdlib-only so it runs where the image is not available. This script must
compute the Panel C planning requirement through the project's own
implementation (scripts/audit_stats.py), which imports scipy, so it cannot meet
that contract. It is an analysis-pipeline tool and belongs with audit_stats.

CONSEQUENCE: scripts/ is a fingerprinted tree. Changing this file requires the
in-image pytest gate and a freeze refresh. See CLAUDE.md.

Every number in the output is read from a committed artifact or computed from
one by project code. Nothing is typed. The emitted JSON records, for each value,
the file and key path it came from, so the figure's provenance is checkable
without reading the TikZ.

Run (needs scipy, so a compute node):

    apptainer exec --bind "$PROJECT_DIR:/workspace" "$IMAGE" \
      python /workspace/scripts/make_figure1.py \
        --out-tex /workspace/paper/figures/fig1_cancellation.tex \
        --out-json /workspace/paper/figures/fig1_values.json

Both arguments are REQUIRED and have no defaults, following the project rule
that no script is given a default for the thing it reads or writes.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_stats  # noqa: E402  (path set above)

# The registered cell this figure illustrates. Named once.
CELL = "qwen25-7b/gsm8k"
CELL_MODEL = "qwen25-7b"
CELL_TASK = "gsm8k"
# The registered uniform audit margin, in percentage points. Cross-checked
# against \AuditMarginPP in paper/audit_denominators.tex by the test suite.
MARGIN_PP = 2.0

H3_SUMMARY = "results/h3_eight_cell/h3_eight_cell_summary.json"
PAIRED_SEEDS = f"results/h3_eight_cell/paired_seeds_{CELL_MODEL}_{CELL_TASK}.json"
SUPPORTING = "results/minigrid_supporting/minigrid_supporting.json"
IDENTICAL = "results/identical_score_churn_rev2.csv"
ATLAS = "results/atlas_cells_summary_rev2.csv"


def _load_json(rel: str):
    return json.loads((ROOT / rel).read_text())


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes")


def collect_values() -> dict:
    """Read every figure value from a canonical artifact, with provenance.

    Returns a dict whose "values" maps a name to {"value", "source", "key"}.
    """
    h3 = _load_json(H3_SUMMARY)
    seeds = _load_json(PAIRED_SEEDS)
    supporting = _load_json(SUPPORTING)
    flips = supporting["slot4_flip_statistics"][CELL]
    cell_mean = flips["cell_mean"]
    step5 = supporting["step5_resolution_POST_HOC"]["cells"][CELL]

    v: dict[str, dict] = {}

    def put(name, value, source, key):
        v[name] = {"value": value, "source": source, "key": key}

    # --- Panel A: the aggregate view -------------------------------------
    # Sign: paired_seeds stores GPTQ minus AWQ. flipeval/core.py defines
    # net_accuracy_delta as method minus baseline, and slot4's net is the
    # negation of this one, which is what fixes GPTQ as the baseline role and
    # AWQ as the method role for every item-level quantity below.
    put("acc_gptq", seeds["full_sample_accuracies"]["gptq"],
        PAIRED_SEEDS, "full_sample_accuracies.gptq")
    put("acc_awq", seeds["full_sample_accuracies"]["awq"],
        PAIRED_SEEDS, "full_sample_accuracies.awq")
    put("gap_gptq_minus_awq", seeds["full_sample_accuracy_delta"],
        PAIRED_SEEDS, "full_sample_accuracy_delta")
    put("n_items", flips["n"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.n")

    # --- Panel B: the paired-item decomposition --------------------------
    put("harmful", cell_mean["harmful_flip_rate"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.harmful_flip_rate")
    put("beneficial", cell_mean["beneficial_flip_rate"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.beneficial_flip_rate")
    put("churn", cell_mean["accuracy_state_churn"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.accuracy_state_churn")
    put("answer_churn", cell_mean["total_answer_churn"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.total_answer_churn")
    put("net_awq_minus_gptq", cell_mean["net_accuracy_delta"], SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.net_accuracy_delta")

    # --- Panel C: certification resolution -------------------------------
    # Computed through the project implementation, never by hand.
    p_d = cell_mean["accuracy_state_churn"]
    sd = audit_stats.paired_flip_sd(p_d)
    required_n = audit_stats.required_n_for_tost(sd, MARGIN_PP / 100.0)
    reversal_d = audit_stats.reversal_discordance(flips["n"], MARGIN_PP / 100.0)
    put("discordance", p_d, SUPPORTING,
        f"slot4_flip_statistics.{CELL}.cell_mean.accuracy_state_churn")
    put("paired_sd", sd, "scripts/audit_stats.py",
        "paired_flip_sd(discordance)")
    put("required_n", required_n, "scripts/audit_stats.py",
        f"required_n_for_tost(paired_flip_sd(d), {MARGIN_PP / 100.0})")
    put("reversal_discordance", reversal_d, "scripts/audit_stats.py",
        f"reversal_discordance(n, {MARGIN_PP / 100.0})")
    put("alpha", audit_stats.ALPHA, "scripts/audit_stats.py", "ALPHA")
    put("power", audit_stats.POWER, "scripts/audit_stats.py", "POWER")
    # Independent cross-check that the sd matches the committed record.
    put("step5_paired_sd", step5["paired_sd"], SUPPORTING,
        f"step5_resolution_POST_HOC.cells.{CELL}.paired_sd")

    # --- Panel D: calibration-seed instability ---------------------------
    seed_labels = list(seeds["seed_labels"])
    seed_deltas = [seeds["per_seed"][s]["accuracy_delta"] for s in seed_labels]
    put("seed_labels", seed_labels, PAIRED_SEEDS, "seed_labels")
    put("seed_deltas_gptq_minus_awq", seed_deltas, PAIRED_SEEDS,
        "per_seed.<seed>.accuracy_delta")
    put("n_cells_winner_flip", h3["n_cells_winner_flip"], H3_SUMMARY,
        "n_cells_winner_flip")
    put("n_cells_total", len(h3["cells"]), H3_SUMMARY, "len(cells)")
    put("h3_verdict", h3["verdict"], H3_SUMMARY, "verdict")
    all_cells = [
        {
            "model": c["model"],
            "task": c["task"],
            "gap": c["gap"],
            "winner_flip": bool(c["winner_flip"]),
        }
        for c in h3["cells"]
    ]
    put("all_cells", all_cells, H3_SUMMARY, "cells[].{model,task,gap,winner_flip}")

    # Where this cell sits among the eight, so the caption cannot imply it is
    # typical. Ratio is churn over absolute net delta, per cell.
    ratios = []
    for name, entry in supporting["slot4_flip_statistics"].items():
        cm = entry["cell_mean"]
        net = abs(cm["net_accuracy_delta"])
        if net > 0:
            ratios.append((name, cm["accuracy_state_churn"] / net))
    ratios.sort(key=lambda pair: pair[1])
    this_ratio = dict(ratios)[CELL]
    put("cell_churn_ratio", this_ratio, SUPPORTING,
        f"slot4 cell_mean churn / abs(net) for {CELL}")
    put("median_churn_ratio", statistics.median([r for _, r in ratios]),
        SUPPORTING, "median over slot4 cell_mean churn / abs(net)")
    put("cell_ratio_rank_of", [len(ratios), ratios[-1][0] == CELL],
        SUPPORTING, "rank of this cell among the eight ratios; True = maximum")

    # --- Atlas context ---------------------------------------------------
    ident = {}
    with (ROOT / IDENTICAL).open() as handle:
        for row in csv.DictReader(handle):
            if row.get("statistic"):
                ident[row["statistic"]] = row["value"]
            if row.get("statistic") == "churn_median_nonzero_only":
                break
    put("atlas_cells", int(ident["analysable_cells"]), IDENTICAL,
        "analysable_cells")
    put("atlas_zero_delta", int(ident["zero_delta_cells"]), IDENTICAL,
        "zero_delta_cells")
    put("atlas_zero_delta_nonzero_churn", int(ident["zero_delta_nonzero_churn_cells"]),
        IDENTICAL, "zero_delta_nonzero_churn_cells")

    # Atlas churn-to-net ratio. Reported as the ratio of pooled medians and as
    # the two stratum ratios, all computed from unrounded values. The
    # manuscript's 5.3x headline divides the ROUNDED medians printed in
    # tab:atlas-strata and is escalated as defect D4 in
    # docs/FLAGSHIP_NARRATIVE_PLAN.md. This figure states "about five times",
    # which every derivation supports, and never prints 5.3.
    rows = []
    with (ROOT / ATLAS).open() as handle:
        for row in csv.DictReader(handle):
            if _truthy(row["excluded_or_skipped"]):
                continue
            if _truthy(row["contains_disclosed_probe_cell"]):
                continue
            rows.append(row)
    churn = [float(r["accuracy_state_churn"]) for r in rows]
    net = [abs(float(r["net_accuracy_delta"])) for r in rows]
    put("atlas_median_churn", statistics.median(churn), ATLAS,
        "median accuracy_state_churn over the analysis population")
    put("atlas_median_abs_net", statistics.median(net), ATLAS,
        "median abs net_accuracy_delta over the analysis population")
    put("atlas_pooled_ratio", statistics.median(churn) / statistics.median(net),
        ATLAS, "ratio of the two pooled medians, unrounded")

    return {
        "figure": "fig1_cancellation",
        "cell": CELL,
        "margin_pp": MARGIN_PP,
        "generator": "scripts/make_figure1.py",
        "values": v,
    }


# --------------------------------------------------------------------------
# TikZ emission.
#
# Plain TikZ only, plus arrows.meta, which ships with every pgf since 3.0. No
# pgfplots: an extra package that cannot be compile-tested here is an extra way
# for the build to fail on a machine we cannot reach.
#
# Colour: two hues chosen for a large GRAYSCALE luminance separation, since the
# figure must survive a black-and-white print. Relative luminance is
# 0.2126R + 0.7152G + 0.0722B on the sRGB values below:
#   fharm  (140, 45, 20)  -> 0.28
#   fben   (125,178,219)  -> 0.65
# a separation of 0.37, well past the 0.2 that is legible in print. Colour is
# additionally never load-bearing: every coloured element carries a text label,
# so the figure reads correctly in pure monochrome.
# --------------------------------------------------------------------------

PREAMBLE = r"""% GENERATED by scripts/make_figure1.py. DO NOT EDIT BY HAND.
% Regenerate in the pinned image; the generator needs scipy for the planning
% requirement, which is computed by scripts/audit_stats.py and never typed.
%
% Requires \usepackage{tikz} and \usetikzlibrary{arrows.meta} in the preamble.
%
% Provenance for every number here is paper/figures/fig1_values.json.
% NOT RENDERED OR VISUALLY INSPECTED: there is no LaTeX on the machine that
% generated this (probe job 11675341), so the first person to compile it must
% check it for clipping, overlap and label legibility.
\definecolor{fharm}{RGB}{140,45,20}
\definecolor{fben}{RGB}{125,178,219}
\definecolor{fneutral}{RGB}{110,110,110}
\definecolor{frule}{RGB}{60,60,60}
"""


def fmt(value: float, places: int) -> str:
    """Fixed-point, with LaTeX thousands separators for integers."""
    if places == 0:
        text = f"{int(round(value)):,}"
        return text.replace(",", "{,}")
    return f"{value:.{places}f}"


def emit_tikz(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    out: list[str] = [PREAMBLE]
    a = out.append

    a(r"\begin{figure}[t]")
    a(r"\centering")
    a(r"\begin{tikzpicture}[")
    a(r"  x=1cm, y=1cm, line width=0.5pt,")
    a(r"  font=\scriptsize,")
    a(r"  panel/.style={draw=frule!35, rounded corners=1pt, line width=0.4pt},")
    a(r"  ttl/.style={font=\scriptsize\bfseries, anchor=west},")
    a(r"  lbl/.style={font=\scriptsize, anchor=west},")
    a(r"  num/.style={font=\scriptsize, anchor=west},")
    a(r"]")

    # Panel geometry. Two columns of 6.0cm with a 0.6cm gutter is 12.6cm, which
    # is just inside \textwidth at article 11pt (12.65cm). Nothing is scaled.
    lx, rx, pw = 0.0, 6.6, 6.0
    ty, by = 6.15, 1.55
    ph = 3.75

    # ---------------- Panel A: aggregate view ----------------------------
    acc_g = v["acc_gptq"] * 100
    acc_a = v["acc_awq"] * 100
    gap_pp = v["gap_gptq_minus_awq"] * 100
    # Full 0 to 100 axis. A truncated axis would exaggerate the gap, which is
    # the opposite of this panel's point.
    axw = 4.35
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({lx},{ty}) {{}};")
    a(rf"\node[ttl] at ({lx + 0.18},{ty + ph - 0.30}) "
      r"{A\quad The aggregate view};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({lx + 0.18},{ty + ph - 0.78}) "
      r"{Two 4-bit methods, same model, same items.};")
    for idx, (name, acc) in enumerate((("GPTQ", acc_g), ("AWQ", acc_a))):
        yy = ty + 1.72 - idx * 0.62
        a(rf"\node[lbl] at ({lx + 0.18},{yy + 0.16}) {{{name}}};")
        a(rf"\draw[fill=frule!12, draw=frule!35] ({lx + 0.95},{yy}) "
          rf"rectangle ({lx + 0.95 + axw},{yy + 0.32});")
        a(rf"\draw[fill=fneutral, draw=none] ({lx + 0.95},{yy}) "
          rf"rectangle ({lx + 0.95 + axw * acc / 100.0},{yy + 0.32});")
        a(rf"\node[num, anchor=west] at ({lx + 0.95 + axw + 0.08},{yy + 0.16}) "
          rf"{{{fmt(acc, 2)}\%}};")
    a(rf"\draw[frule!55, line width=0.4pt] ({lx + 0.95},{ty + 0.72}) -- "
      rf"({lx + 0.95},{ty + 0.60}) -- ({lx + 0.95 + axw},{ty + 0.60}) -- "
      rf"({lx + 0.95 + axw},{ty + 0.72});")
    a(rf"\node[font=\scriptsize, anchor=north] "
      rf"at ({lx + 0.95 + axw / 2},{ty + 0.58}) "
      rf"{{0 to 100\% accuracy, $n={fmt(v['n_items'], 0)}$ per seed}};")
    a(rf"\node[font=\scriptsize\bfseries, anchor=west] "
      rf"at ({lx + 0.18},{ty + 1.06}) "
      rf"{{Gap: {fmt(abs(gap_pp), 2)} pp}};")

    # ---------------- Panel B: paired decomposition ----------------------
    harm = v["harmful"] * 100
    ben = v["beneficial"] * 100
    churn = v["churn"] * 100
    answer = v["answer_churn"] * 100
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({rx},{ty}) {{}};")
    a(rf"\node[ttl] at ({rx + 0.18},{ty + ph - 0.30}) "
      r"{B\quad The same items, paired};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({rx + 0.18},{ty + ph - 0.78}) "
      r"{Every item, going from GPTQ to AWQ.};")
    # A 100-item bar split into break / heal / unchanged.
    bw = 5.2
    byy = ty + 1.98
    a(rf"\draw[fill=fharm, draw=none] ({rx + 0.4},{byy}) "
      rf"rectangle ({rx + 0.4 + bw * harm / 100.0},{byy + 0.42});")
    a(rf"\draw[fill=fben, draw=none] ({rx + 0.4 + bw * harm / 100.0},{byy}) "
      rf"rectangle ({rx + 0.4 + bw * (harm + ben) / 100.0},{byy + 0.42});")
    a(rf"\draw[fill=frule!8, draw=none] "
      rf"({rx + 0.4 + bw * (harm + ben) / 100.0},{byy}) "
      rf"rectangle ({rx + 0.4 + bw},{byy + 0.42});")
    a(rf"\draw[draw=frule!45] ({rx + 0.4},{byy}) rectangle ({rx + 0.4 + bw},{byy + 0.42});")
    a(rf"\node[font=\scriptsize, anchor=east, text=white] "
      rf"at ({rx + 0.4 + bw * harm / 100.0 - 0.06},{byy + 0.21}) "
      rf"{{{fmt(harm, 2)}\%}};")
    a(rf"\node[font=\scriptsize, anchor=west] "
      rf"at ({rx + 0.4 + bw * (harm + ben) / 100.0 + 0.08},{byy + 0.21}) "
      rf"{{{fmt(100 - churn, 2)}\% unchanged}};")
    a(rf"\node[font=\scriptsize, anchor=south] "
      rf"at ({rx + 0.4 + bw * (harm + ben / 2) / 100.0},{byy + 0.46}) "
      rf"{{{fmt(ben, 2)}\%}};")
    a(rf"\node[lbl] at ({rx + 0.4},{byy + 0.92}) "
      r"{\textcolor{fharm}{$\blacksquare$} correct $\to$ wrong \quad "
      r"\textcolor{fben}{$\blacksquare$} wrong $\to$ correct};")
    # The two derived quantities, stated as arithmetic.
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 0.55}) "
      rf"{{net delta $= {fmt(ben, 2)} - {fmt(harm, 2)} = "
      rf"{fmt(ben - harm, 2)}$ pp}};")
    a(rf"\node[lbl, anchor=west, font=\scriptsize\bfseries] "
      rf"at ({rx + 0.4},{byy - 1.00}) "
      rf"{{churn $= {fmt(ben, 2)} + {fmt(harm, 2)} = "
      rf"{fmt(churn, 2)}$\%}};")
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 1.42}) "
      rf"{{{fmt(answer, 2)}\% of answers change in all}};")

    # ---------------- Panel C: certification resolution ------------------
    req = v["required_n"]
    act = v["n_items"]
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({lx},{by}) {{}};")
    a(rf"\node[ttl] at ({lx + 0.18},{by + ph - 0.30}) "
      r"{C\quad Could this evaluation certify?};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({lx + 0.18},{by + ph - 0.78}) "
      rf"{{Planning requirement at a declared $\pm{fmt(MARGIN_PP, 0)}$ pp margin.}};")
    cw = 3.9
    for idx, (name, val, col) in enumerate((
            ("items run", act, "fneutral"),
            ("items required", req, "fharm"))):
        yy = by + 1.72 - idx * 0.62
        a(rf"\node[lbl] at ({lx + 0.18},{yy + 0.16}) {{{name}}};")
        a(rf"\draw[fill={col}, draw=none] ({lx + 1.55},{yy}) "
          rf"rectangle ({lx + 1.55 + cw * val / req},{yy + 0.32});")
        a(rf"\node[num] at ({lx + 1.55 + cw * val / req + 0.08},{yy + 0.16}) "
          rf"{{{fmt(val, 0)}}};")
    a(rf"\node[lbl, text width={pw - 0.45}cm, anchor=north west] "
      rf"at ({lx + 0.18},{by + 1.02}) "
      rf"{{At the observed disagreement rate of {fmt(v['discordance'] * 100, 2)}\%, "
      rf"certifying at $\pm{fmt(MARGIN_PP, 0)}$ pp needs {fmt(req, 0)} items. "
      rf"This is a planning requirement at an assumed true difference of zero, "
      rf"so the evaluation cannot support an equivalence claim at that margin. "
      rf"It is not evidence that the methods differ.}};")

    # ---------------- Panel D: calibration-seed instability --------------
    deltas = [d * 100 for d in v["seed_deltas_gptq_minus_awq"]]
    flips_n = v["n_cells_winner_flip"]
    cells_n = v["n_cells_total"]
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({rx},{by}) {{}};")
    a(rf"\node[ttl] at ({rx + 0.18},{by + ph - 0.30}) "
      r"{D\quad Change only the calibration draw};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({rx + 0.18},{by + ph - 0.78}) "
      r"{GPTQ minus AWQ, one bar per calibration seed.};")
    zero_y = by + 1.62
    span = max(abs(d) for d in deltas)
    unit = 0.52 / span
    a(rf"\draw[frule!70, line width=0.5pt] ({rx + 0.35},{zero_y}) -- "
      rf"({rx + 5.1},{zero_y});")
    a(rf"\node[font=\scriptsize, anchor=east] at ({rx + 0.33},{zero_y}) {{0}};")
    for idx, (label, delta) in enumerate(zip(v["seed_labels"], deltas)):
        cx = rx + 0.85 + idx * 0.72
        col = "fben" if delta > 0 else "fharm"
        a(rf"\draw[fill={col}, draw=none] ({cx - 0.20},{zero_y}) "
          rf"rectangle ({cx + 0.20},{zero_y + delta * unit});")
        anchor = "south" if delta > 0 else "north"
        a(rf"\node[font=\scriptsize, anchor={anchor}] "
          rf"at ({cx},{zero_y + delta * unit + (0.04 if delta > 0 else -0.04)}) "
          rf"{{{fmt(delta, 1)}}};")
        a(rf"\node[font=\scriptsize, anchor=north] at ({cx},{zero_y - 0.72}) "
          rf"{{s{label}}};")
    a(rf"\node[lbl, text width={pw - 0.45}cm, anchor=north west] "
      rf"at ({rx + 0.18},{by + 0.80}) "
      rf"{{The sign changes: on one calibration draw AWQ wins, on the others "
      rf"GPTQ does. Across the {cells_n} registered cells the winner reverses "
      rf"in \textbf{{{flips_n} of {cells_n}}}.}};")
    # All eight cells, so this one cannot read as the whole evidence base.
    sx = rx + 0.32
    a(rf"\node[font=\scriptsize, anchor=west] at ({sx},{by + 0.30}) "
      r"{all cells:};")
    for idx, cell in enumerate(v["all_cells"]):
        cx = sx + 1.02 + idx * 0.55
        mark = r"$\bullet$" if cell["winner_flip"] else r"$\circ$"
        col = "fharm" if cell["winner_flip"] else "frule!55"
        this = cell["model"] == CELL_MODEL and cell["task"] == CELL_TASK
        a(rf"\node[font=\scriptsize, text={col}] at ({cx},{by + 0.30}) {{{mark}}};")
        if this:
            a(rf"\draw[frule!60, line width=0.4pt] ({cx},{by + 0.30}) circle (0.16);")
    a(rf"\node[font=\scriptsize, anchor=west] at ({sx + 1.02 + 8 * 0.55 - 0.18},{by + 0.30}) "
      r"{\ \ $\bullet$ reversed};")

    # ---------------- Atlas context strip --------------------------------
    a(rf"\draw[frule!25, line width=0.4pt] ({lx},{by - 0.30}) -- ({rx + pw},{by - 0.30});")
    a(rf"\node[anchor=north west, text width={2 * pw + 0.6}cm, font=\scriptsize] "
      rf"at ({lx},{by - 0.42}) "
      rf"{{\textbf{{This is not one cell's problem.}} Across "
      rf"{fmt(v['atlas_cells'], 0)} paired model-by-task cells mined from public "
      rf"per-item evaluation dumps, median per-item churn is about five times "
      rf"the median net accuracy delta. "
      rf"{fmt(v['atlas_zero_delta'], 0)} of those cells post an aggregate "
      rf"accuracy identical to their baseline, and "
      rf"{fmt(v['atlas_zero_delta_nonzero_churn'], 0)} of the "
      rf"{fmt(v['atlas_zero_delta'], 0)} still change which items they get "
      rf"right. Ratios are undefined for a zero net delta, so those cells are "
      rf"counted here and excluded from the ratio.}};")

    a(r"\end{tikzpicture}")
    a(caption(data))
    a(r"\label{fig:cancellation}")
    a(r"\end{figure}")
    return "\n".join(out) + "\n"


def caption(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    ratio = v["cell_churn_ratio"]
    median_ratio = v["median_churn_ratio"]
    return (
        r"\caption{\textbf{Near-equal aggregate accuracy does not certify "
        r"interchangeable behavior.} One registered cell: Qwen2.5-7B on GSM8K, "
        r"4-bit GPTQ against 4-bit AWQ, paired on byte-identical calibration "
        r"samples across five seeds. (A)~The two methods differ by "
        + fmt(abs(v["gap_gptq_minus_awq"]) * 100, 2) + r"~pp of aggregate "
        r"accuracy. (B)~The same items disagree far more than that: "
        + fmt(v["harmful"] * 100, 2) + r"\% of items go from correct to wrong "
        r"and " + fmt(v["beneficial"] * 100, 2) + r"\% from wrong to correct, "
        r"so the aggregate gap is the small difference between two large "
        r"opposing quantities whose sum is " + fmt(v["churn"] * 100, 2) +
        r"\%. (C)~At the observed disagreement rate, certifying equivalence at "
        r"a declared $\pm" + fmt(data["margin_pp"], 0) + r"$~pp margin would "
        r"need " + fmt(v["required_n"], 0) + r" items against the " +
        fmt(v["n_items"], 0) + r" run. That is a planning requirement computed "
        r"at an assumed true difference of zero: it says the evaluation cannot "
        r"support the claim, not that the methods differ. (D)~The sign of the "
        r"difference changes with the calibration draw alone, and across the "
        r"eight registered cells the winner reverses in " +
        str(v["n_cells_winner_flip"]) + r" of " + str(v["n_cells_total"]) +
        r". \textbf{Scope.} This cell is an illustrative example chosen because "
        r"it is legible, and it is the most extreme of the eight: its "
        r"churn-to-net-delta ratio is $" + fmt(ratio, 1) + r"\times$ against a "
        r"median of $" + fmt(median_ratio, 1) + r"\times$ across the eight. "
        r"All eight are shown in~(D) for that reason. The atlas figures in the "
        r"panel above are observational and describe the public evaluation "
        r"record rather than a census of compression.}"
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
    Path(args.out_json).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"FIGURE1: wrote {args.out_tex} and {args.out_json}")
    print(f"FIGURE1: cell={data['cell']} required_n="
          f"{data['values']['required_n']['value']} "
          f"n={data['values']['n_items']['value']}")


if __name__ == "__main__":
    main()
