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

    a(r"\begin{figure}[!t]")
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

    # Text-width budget, in cm, for the nodes that sit closest to a panel's
    # right edge. These are estimates from Computer Modern metrics at
    # \scriptsize (8pt in an 11pt document): a digit is 0.5em = 4pt, "%" is
    # 1em, a lowercase letter averages about 0.53em. They exist so that
    # fits_in_panel() below can fail the build instead of emitting a node that
    # silently runs into the margin.
    #
    # Wave 3 (2026-08-05) found three such overruns by reading the emitted TikZ,
    # because nothing here checked them: the panel D key ran about 1.1cm past
    # \textwidth (G1), the panel B colour key overlapped its own subtitle by
    # sitting 0.07cm below it (G2), and the panel A accuracy labels crossed the
    # panel border (G3). All three are fixed below and guarded here.
    W_ACC_LABEL = 0.95      # "74.28\%"
    W_PANELD_KEY = 1.70     # "\ \ $\bullet$ reversed"

    overruns: list[str] = []

    def fits_in_panel(what: str, x_left: float, width: float,
                      panel_x: float) -> None:
        """Record a node whose right edge lands outside its panel."""
        right = x_left + width
        limit = panel_x + pw
        if right > limit:
            overruns.append(
                f"{what}: right edge {right:.2f}cm exceeds panel edge "
                f"{limit:.2f}cm by {right - limit:.2f}cm")

    # ---------------- Panel A: aggregate view ----------------------------
    acc_g = v["acc_gptq"] * 100
    acc_a = v["acc_awq"] * 100
    gap_pp = v["gap_gptq_minus_awq"] * 100
    # Full 0 to 100 axis. A truncated axis would exaggerate the gap, which is
    # the opposite of this panel's point.
    # G3 (2026-08-05): was 4.35, which put the accuracy labels at x=5.38 with
    # about 0.95cm of text to draw and a panel border at 6.00. They crossed it.
    # The axis is the only thing here that can give, and shortening it does not
    # distort anything: it is a full 0-to-100 axis either way.
    axw = 3.50
    # Bars start clear of the row labels. F2 (2026-08-05, first render): the
    # bars began at 0.95 and "GPTQ" is about 0.80cm wide from 0.18, so the bar
    # was drawn over the Q and the label read "GPT".
    barx = 1.32
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({lx},{ty}) {{}};")
    a(rf"\node[ttl] at ({lx + 0.18},{ty + ph - 0.30}) "
      r"{A\quad The aggregate view};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({lx + 0.18},{ty + ph - 0.78}) "
      r"{Two 4-bit methods, one model, one item set.};")
    for idx, (name, acc) in enumerate((("GPTQ", acc_g), ("AWQ", acc_a))):
        yy = ty + 1.72 - idx * 0.62
        a(rf"\node[lbl] at ({lx + 0.18},{yy + 0.16}) {{{name}}};")
        a(rf"\draw[fill=frule!12, draw=frule!35] ({lx + barx},{yy}) "
          rf"rectangle ({lx + barx + axw},{yy + 0.32});")
        a(rf"\draw[fill=fneutral, draw=none] ({lx + barx},{yy}) "
          rf"rectangle ({lx + barx + axw * acc / 100.0},{yy + 0.32});")
        a(rf"\node[num, anchor=west] at ({lx + barx + axw + 0.08},{yy + 0.16}) "
          rf"{{{fmt(acc, 2)}\%}};")
        fits_in_panel(f"panel A {name} accuracy label",
                      lx + barx + axw + 0.08, W_ACC_LABEL, lx)
    a(rf"\draw[frule!55, line width=0.4pt] ({lx + barx},{ty + 0.72}) -- "
      rf"({lx + barx},{ty + 0.60}) -- ({lx + barx + axw},{ty + 0.60}) -- "
      rf"({lx + barx + axw},{ty + 0.72});")
    a(rf"\node[font=\scriptsize, anchor=north] "
      rf"at ({lx + barx + axw / 2},{ty + 0.58}) "
      rf"{{0 to 100\% accuracy, $n={fmt(v['n_items'], 0)}$ per seed}};")
    # F3 (2026-08-05, first render): this sat at ty + 1.06, which is inside the
    # AWQ bar row at ty + 1.10, so the two overprinted. It moves above the bars,
    # under the subtitle, where the panel is empty.
    a(rf"\node[font=\scriptsize\bfseries, anchor=west] "
      rf"at ({lx + 0.18},{ty + 2.38}) "
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
    # Raised from ty + 1.98 on 2026-08-05 to buy vertical room for the two
    # callouts that replaced the in-bar labels; the lowest line now clears the
    # panel floor by about 0.31cm.
    byy = ty + 2.25
    a(rf"\draw[fill=fharm, draw=none] ({rx + 0.4},{byy}) "
      rf"rectangle ({rx + 0.4 + bw * harm / 100.0},{byy + 0.42});")
    a(rf"\draw[fill=fben, draw=none] ({rx + 0.4 + bw * harm / 100.0},{byy}) "
      rf"rectangle ({rx + 0.4 + bw * (harm + ben) / 100.0},{byy + 0.42});")
    a(rf"\draw[fill=frule!8, draw=none] "
      rf"({rx + 0.4 + bw * (harm + ben) / 100.0},{byy}) "
      rf"rectangle ({rx + 0.4 + bw},{byy + 0.42});")
    a(rf"\draw[draw=frule!45] ({rx + 0.4},{byy}) rectangle ({rx + 0.4 + bw},{byy + 0.42});")
    a(rf"\node[font=\scriptsize, anchor=west] "
      rf"at ({rx + 0.4 + bw * (harm + ben) / 100.0 + 0.08},{byy + 0.21}) "
      rf"{{{fmt(100 - churn, 2)}\% unchanged}};")
    # The colour key sits directly under the bar it explains.
    # G2 (2026-08-05): this was at byy + 0.92, i.e. ABOVE the bar, which put it
    # at y=9.05 against the panel subtitle at y=9.12. Both are anchor=west, so
    # those are text centres 0.07cm apart and the two lines overlapped. The bug
    # was that the subtitle's y came from the panel top and the key's came from
    # the bar, so nothing kept them apart. Below the bar there is real room, and
    # a key next to the thing it labels is better anyway.
    # F5/F6 (2026-08-05, first render). The harmful rate used to be set INSIDE
    # its own segment in white, anchored east. That segment is 9.12% of 5.2cm =
    # 0.47cm and the label needs about 0.9cm, so "9.12" was drawn off the left
    # end of the bar over the panel background in white ink and vanished; only
    # the "%" landed on the dark fill. The beneficial rate sat above the bar,
    # detached, level with the subtitle. Both now read as callouts under the
    # bar, in the segment's own colour, which also makes the separate key
    # redundant: the numbers and the key are the same two lines.
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 0.28}) "
      rf"{{\textcolor{{fharm}}{{$\blacksquare$}} {fmt(harm, 2)}\% "
      r"correct $\to$ wrong};")
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 0.66}) "
      rf"{{\textcolor{{fben}}{{$\blacksquare$}} {fmt(ben, 2)}\% "
      r"wrong $\to$ correct};")
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 1.06}) "
      rf"{{net delta $= {fmt(ben, 2)} - {fmt(harm, 2)} = "
      rf"{fmt(ben - harm, 2)}$ pp}};")
    a(rf"\node[lbl, anchor=west, font=\scriptsize\bfseries] "
      rf"at ({rx + 0.4},{byy - 1.44}) "
      rf"{{churn $= {fmt(ben, 2)} + {fmt(harm, 2)} = "
      rf"{fmt(churn, 2)}$\%}};")
    a(rf"\node[lbl, anchor=west] at ({rx + 0.4},{byy - 1.80}) "
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
    cw = 2.98
    # F7 (2026-08-05, first render): the bars began at 1.55 and "items
    # required" is about 1.35cm wide from 0.18, so the bar overprinted its own
    # label and it read "items req".
    cbarx = 2.28
    for idx, (name, val, col) in enumerate((
            ("items run", act, "fneutral"),
            ("items required", req, "fharm"))):
        yy = by + 2.05 - idx * 0.62
        a(rf"\node[lbl] at ({lx + 0.18},{yy + 0.16}) {{{name}}};")
        a(rf"\draw[fill={col}, draw=none] ({lx + cbarx},{yy}) "
          rf"rectangle ({lx + cbarx + cw * val / req},{yy + 0.32});")
        a(rf"\node[num] at ({lx + cbarx + cw * val / req + 0.08},{yy + 0.16}) "
          rf"{{{fmt(val, 0)}}};")
    # F8 (2026-08-05, first render): a five-line prose block used to sit here
    # and ran off the bottom of the panel, over the atlas strip below it. The
    # caption already carries that sentence in full, so the panel keeps only
    # the qualification that must not be read off the bars alone.
    a(rf"\node[lbl, text width={pw - 0.45}cm, anchor=north west] "
      rf"at ({lx + 0.18},{by + 1.22}) "
      rf"{{Observed disagreement {fmt(v['discordance'] * 100, 2)}\%. A planning "
      rf"requirement, not evidence the methods differ.}};")

    # ---------------- Panel D: calibration-seed instability --------------
    deltas = [d * 100 for d in v["seed_deltas_gptq_minus_awq"]]
    flips_n = v["n_cells_winner_flip"]
    cells_n = v["n_cells_total"]
    a(rf"\node[panel, minimum width={pw}cm, minimum height={ph}cm, "
      rf"anchor=south west] at ({rx},{by}) {{}};")
    a(rf"\node[ttl] at ({rx + 0.18},{by + ph - 0.30}) "
      r"{D\quad The calibration draw alone};")
    a(rf"\node[lbl, font=\scriptsize\itshape, text width={pw - 0.5}cm] "
      rf"at ({rx + 0.18},{by + ph - 0.78}) "
      r"{GPTQ minus AWQ, per calibration seed.};")
    # F9 (2026-08-05, first render). The bars sat at by + 1.62 and a three-line
    # sentence was placed at by + 0.80, which put it through the seed labels at
    # by + 0.90 and through the all-cells strip at by + 0.30. Three sets of text
    # overprinted. The bars move up, the sentence is dropped because the caption
    # states it in full, and the strip gets the space back.
    zero_y = by + 1.95
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
        a(rf"\node[font=\scriptsize, anchor=north] at ({cx},{zero_y - 0.95}) "
          rf"{{s{label}}};")
    # All eight cells, so this one cannot read as the whole evidence base.
    #
    # G1 (2026-08-05). The key used to be emitted at sx + 1.02 + 8*0.55 - 0.18,
    # one dot-pitch past the last dot, with nothing checking the result. At a
    # 0.55cm pitch that is x=12.16, and the key needs about 1.7cm, so it ran to
    # about 13.8cm against a 12.6cm panel and a 12.65cm \textwidth: an overfull
    # box with the key sitting in the right margin. The pitch is now derived
    # from the space the key actually needs, and fits_in_panel() checks it.
    sx = rx + 0.30
    dot_x0 = sx + 1.28           # first dot, clear of the "all cells:" label
    key_gap = 0.20               # dot centre to key left edge
    n_dots = len(v["all_cells"])
    # Solve for the pitch that leaves the key inside the panel, then round down
    # to a tidy value. 0.36 keeps the circled marker clear of its neighbours
    # (radius 0.16 against a 0.36 pitch) while leaving the key about 0.3cm.
    dot_pitch = 0.34
    a(rf"\node[font=\scriptsize, anchor=west] at ({sx},{by + 0.40}) "
      r"{all cells:};")
    for idx, cell in enumerate(v["all_cells"]):
        cx = dot_x0 + idx * dot_pitch
        mark = r"$\bullet$" if cell["winner_flip"] else r"$\circ$"
        col = "fharm" if cell["winner_flip"] else "frule!55"
        this = cell["model"] == CELL_MODEL and cell["task"] == CELL_TASK
        a(rf"\node[font=\scriptsize, text={col}] at ({cx},{by + 0.40}) {{{mark}}};")
        if this:
            a(rf"\draw[frule!60, line width=0.4pt] ({cx},{by + 0.40}) circle (0.16);")
    key_x = dot_x0 + (n_dots - 1) * dot_pitch + key_gap
    a(rf"\node[font=\scriptsize, anchor=west] at ({key_x},{by + 0.40}) "
      r"{\ \ $\bullet$ reversed};")
    fits_in_panel("panel D reversed key", key_x, W_PANELD_KEY, rx)

    # ---------------- Atlas context strip --------------------------------
    a(rf"\draw[frule!25, line width=0.4pt] ({lx},{by - 0.30}) -- ({rx + pw},{by - 0.30});")
    # inner sep=0 is load-bearing, not cosmetic. This node is the only one whose
    # text width spans the full picture, and TikZ adds its default inner sep
    # (0.3333em, about 0.12cm at this size) OUTSIDE that width on both sides. The
    # node therefore ran from -0.12cm to 12.72cm inside a 12.6cm picture, making
    # the tikzpicture 6.2pt wider than \textwidth: ink in the right margin on
    # page 3, the flagship figure's own page. Found by compiling, not by the
    # guard below, which measured the declared widths and not the padding TeX
    # adds to them. Any future full-width node needs the same treatment.
    a(rf"\node[anchor=north west, inner sep=0, text width={2 * pw + 0.6}cm, "
      rf"font=\scriptsize] "
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

    # Fail the build rather than emit a node that runs into the margin. The
    # widths are estimates, so this guard catches the gross case (Wave 3's G1
    # was 1.1cm past \textwidth) and is not a substitute for looking at a
    # rendered page.
    #
    # THREE THINGS IT CANNOT SEE, each learned by compiling (2026-08-05):
    #   1. vertical overflow and label/bar collisions -- ten defects were found
    #      by rendering at 250 dpi after this guard passed clean;
    #   2. the inner sep TeX adds outside a declared text width, which put the
    #      atlas strip 6.2pt into the margin while every checked width fitted;
    #   3. anything about the page the figure lands on.
    # The premise it was written under -- "nobody on this project can compile
    # the figure" -- stopped being true on 2026-08-05, when TeX Live was
    # installed at ~/scratch/texlive (docs/PAPER_BUILD_ENVIRONMENT.md). Render
    # the figure after changing its geometry; do not trust this guard alone.
    if overruns:
        raise SystemExit(
            "figure geometry: node(s) outside their panel:\n  "
            + "\n  ".join(overruns))

    return "\n".join(out) + "\n"


def caption(data: dict) -> str:
    v = {name: entry["value"] for name, entry in data["values"].items()}
    ratio = v["cell_churn_ratio"]
    median_ratio = v["median_churn_ratio"]
    return (
        r"\caption{\textbf{Near-equal aggregate accuracy does not certify "
        r"interchangeable behavior.} One registered cell: Qwen2.5-7B on GSM8K, "
        r"4-bit GPTQ against 4-bit AWQ, paired on byte-identical calibration "
        r"samples across five seeds. (A)~and~(B)~The aggregate gap of "
        + fmt(abs(v["gap_gptq_minus_awq"]) * 100, 2) + r"~pp is the small "
        r"difference between two large opposing quantities summing to " +
        fmt(v["churn"] * 100, 2) +
        r"\%. (C)~The item count needed to certify equivalence at a declared "
        r"$\pm" + fmt(data["margin_pp"], 0) + r"$~pp margin is a planning "
        r"requirement computed at an assumed true difference of zero: it says "
        r"the evaluation cannot support the claim, not that the methods "
        r"differ. (D)~The sign changes with the calibration draw alone, and "
        r"across the eight registered cells the winner reverses in " +
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
