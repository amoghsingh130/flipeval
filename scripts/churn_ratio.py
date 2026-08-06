"""The churn-to-net-delta ratio: one generator for every aggregation the paper quotes.

Why this file exists
--------------------
Until 2026-08-05 the paper's most repeated headline number had **no generator**.
It existed only as arithmetic inside a LaTeX comment, and it rotted twice:

- **D8** -- the S1 median accuracy-state churn was hand-copied as 0.138 when the
  artifact says 0.13745229, so the printed stratum ratio was 5.31.
- **D4** -- three figures in one sentence were computed under two different
  rounding conventions (pooled from unrounded medians, strata from medians
  pre-rounded to the 3 dp the table happened to print).

`paper/tools/gen_denominator_macros.py` exists because hand-typed audit counts
rot. This module is the same argument applied to the atlas ratio: every value the
paper prints for this quantity is computed here, from committed artifacts, and
pinned by `tests/test_churn_ratio.py`.

What is registered and what is not
----------------------------------
ATLAS_MINING_REGISTRATION_2026-07-15 §5 registers the **per-cell metrics** and §6
registers the **population** (probe cells appear in the atlas but not in headline
aggregates). Neither registration says one word about **aggregation**. So the
population filter below is registered and must not be varied, while the choice
between the two aggregations is a descriptive one that the paper makes openly.
See `docs/HEADLINE_CHURN_RATIO_DEFINITION.md`.

The two aggregations, which are different quantities
----------------------------------------------------
1. **Ratio of medians** -- median(churn) / median(|net delta|) over the cells.
   Describes the typical churn against the typical net delta. Every cell in the
   population contributes to both medians, so nothing is ever dropped.
2. **Median of per-cell ratios** -- median over cells of churn_i / |net delta_i|.
   Describes the typical cell. Undefined wherever |net delta_i| = 0.

They are not interchangeable and neither is "the" ratio. Over the atlas they
differ substantially (5.40 against 3.85); over the eight controlled cells they
nearly agree (12.14 against 12.71).

The zero-denominator problem, which is the point of the `ZeroPolicy` below
-------------------------------------------------------------------------
145 of the 1,707 atlas cells have an exactly zero net accuracy delta, and **128
of them have non-zero churn**: behaviour changed and the aggregate did not move
at all. Those cells are the subject of the paper's own `sec:atlas:identical`, so
an aggregation that discards them silently is discarding the strongest instance
of the effect the paper is about.

Aggregation 1 is unaffected -- a zero delta is an ordinary value inside a median.
Aggregation 2 has to say what it does, and the honest observation is that the
choice is **conservative in the direction that matters**:

- `EXCLUDE` drops all 145. This is what the paper reports (median 3.85).
- `EXTENDED` keeps the 128 as +inf, because churn > 0 against a zero delta is the
  limit of the ratio, and drops only the 17 genuine 0/0 cells. The median then
  **rises**, since every readmitted cell sorts above every finite one.

So the reported 3.85 is a lower bound on the per-cell ratio under any convention
that does not throw the zero-delta cells away, and cannot be the product of a
favourable choice. `--zero-policy` computes both; the paper states both.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence

ATLAS_CSV = Path("results/atlas_cells_summary_rev2.csv")
CONTROLLED_JSON = Path("results/minigrid_supporting/minigrid_supporting.json")

# Exact equality, no rounding tolerance. This is not a new definition: it is the
# one docs/IDENTICAL_SCORE_CHURN_2026-07-21.md and results/identical_score_churn_rev2.csv
# already use for the 145 zero-delta cells that sec:atlas:identical reports, and
# reusing it is what keeps the count in this module identical to the count the
# paper prints two subsections earlier. A rounding-based threshold would admit
# more cells and is deliberately not used.
ZERO_DELTA_TOL = 1e-12


class ZeroPolicy(str, Enum):
    """What to do with a cell whose net accuracy delta is exactly zero.

    Only ever consulted by the per-cell aggregation; a ratio of medians has no
    per-cell denominator to be zero.
    """

    EXCLUDE = "exclude"
    EXTENDED = "extended"


@dataclass(frozen=True)
class Cell:
    """One evaluation cell, reduced to what this ratio needs."""

    label: str
    stratum: str
    churn: float
    abs_net_delta: float
    answer_churn: float | None = None


def load_atlas_population(path: str | Path = ATLAS_CSV) -> list[Cell]:
    """The registered 1,707-cell analysis population.

    The two filters are registered (ATLAS_MINING_REGISTRATION §1 and §6) and are
    the same ones `scripts/audit_stats.load_atlas_cells` applies;
    `tests/test_churn_ratio.py` asserts the two agree cell for cell so they
    cannot fork. The 1,807 figure is pipeline accounting and is never an
    analysis denominator.
    """
    cells: list[Cell] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["excluded_or_skipped"].strip().lower() != "false":
                continue
            if row["contains_disclosed_probe_cell"].strip().lower() == "true":
                continue
            try:
                churn = float(row["accuracy_state_churn"])
                delta = float(row["net_accuracy_delta"])
            except (TypeError, ValueError):
                continue
            try:
                answer_churn = float(row["total_answer_churn"])
            except (TypeError, ValueError):
                answer_churn = None
            cells.append(Cell(
                label=f"{row['pair_index']}/{row['task']}",
                stratum=row["source"].strip(),
                churn=churn,
                abs_net_delta=abs(delta),
                answer_churn=answer_churn,
            ))
    return cells


def load_controlled_cells(path: str | Path = CONTROLLED_JSON) -> list[Cell]:
    """The eight confirmatory cells, GPTQ against AWQ, from the cell means.

    These are the same quantities computed by the same
    `flipeval.core.compute_pair_metrics` that produced the atlas, which is what
    makes a like-for-like comparison legitimate at all. The contrast differs:
    method against method at one bit width, where the atlas is quantized against
    FP16.

    Reading `cell_mean` rather than any per-seed value is deliberate. This
    touches no accuracy figure beyond the flip statistics the paper already
    prints in panel (c) of `tab:h3-supporting`.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    cells: list[Cell] = []
    for label, entry in payload["slot4_flip_statistics"].items():
        mean = entry["cell_mean"]
        cells.append(Cell(
            label=label,
            stratum="controlled",
            churn=float(mean["accuracy_state_churn"]),
            abs_net_delta=abs(float(mean["net_accuracy_delta"])),
            answer_churn=float(mean["total_answer_churn"]),
        ))
    return cells


def ratio_of_medians(cells: Sequence[Cell], *, numerator: str = "churn") -> float:
    """median(numerator) / median(|net delta|), both unrounded.

    Never rounds an input. Every rounding defect this number has had came from
    dividing pre-rounded medians, so the rounding happens once, at the point of
    printing, and never here.
    """
    if not cells:
        raise ValueError("ratio of medians over an empty population")
    values = [getattr(cell, numerator) for cell in cells]
    if any(value is None for value in values):
        raise ValueError(f"{numerator} is missing for at least one cell")
    denominator = statistics.median([cell.abs_net_delta for cell in cells])
    if denominator == 0:
        raise ZeroDivisionError("median |net delta| is zero; the ratio is undefined")
    return statistics.median(values) / denominator


def per_cell_ratios(
    cells: Iterable[Cell],
    policy: ZeroPolicy = ZeroPolicy.EXCLUDE,
) -> tuple[list[float], dict[str, int]]:
    """Per-cell churn / |net delta|, and an account of every cell not in it.

    The counts are returned rather than logged because the paper has to state
    them: a median over 1,562 of 1,707 cells is only honest if the 145 are
    named, and which of them carry churn is the whole question.
    """
    ratios: list[float] = []
    counts = {"total": 0, "finite": 0, "zero_delta": 0, "zero_delta_with_churn": 0,
              "zero_delta_zero_churn": 0, "included": 0}
    for cell in cells:
        counts["total"] += 1
        if cell.abs_net_delta >= ZERO_DELTA_TOL:
            counts["finite"] += 1
            ratios.append(cell.churn / cell.abs_net_delta)
            continue
        counts["zero_delta"] += 1
        if cell.churn > 0:
            counts["zero_delta_with_churn"] += 1
            if policy is ZeroPolicy.EXTENDED:
                ratios.append(math.inf)
        else:
            counts["zero_delta_zero_churn"] += 1
    counts["included"] = len(ratios)
    return ratios, counts


def median_of_per_cell_ratios(
    cells: Sequence[Cell],
    policy: ZeroPolicy = ZeroPolicy.EXCLUDE,
) -> float:
    ratios, _ = per_cell_ratios(cells, policy)
    if not ratios:
        raise ValueError("no cell has a defined per-cell ratio")
    return statistics.median(ratios)


def summarize(cells: Sequence[Cell], name: str) -> dict:
    """Both aggregations, both zero policies, and the counts behind them."""
    excluded, counts = per_cell_ratios(cells, ZeroPolicy.EXCLUDE)
    extended, _ = per_cell_ratios(cells, ZeroPolicy.EXTENDED)
    summary = {
        "population": name,
        "cells": len(cells),
        "median_churn": statistics.median([cell.churn for cell in cells]),
        "median_abs_net_delta": statistics.median([cell.abs_net_delta for cell in cells]),
        "ratio_of_medians": ratio_of_medians(cells),
        "per_cell_median_exclude": statistics.median(excluded) if excluded else None,
        "per_cell_median_extended": statistics.median(extended) if extended else None,
        "per_cell_mean_exclude": (sum(excluded) / len(excluded)) if excluded else None,
        "per_cell_min": min(excluded) if excluded else None,
        "per_cell_max": max(excluded) if excluded else None,
        "counts": counts,
    }
    if all(cell.answer_churn is not None for cell in cells):
        summary["answer_churn_ratio_of_medians"] = ratio_of_medians(cells, numerator="answer_churn")
    return summary


def report(atlas_path: str | Path = ATLAS_CSV, controlled_path: str | Path = CONTROLLED_JSON) -> dict:
    atlas = load_atlas_population(atlas_path)
    controlled = load_controlled_cells(controlled_path)
    strata = sorted({cell.stratum for cell in atlas})
    out = {
        "atlas": summarize(atlas, "atlas"),
        "controlled": summarize(controlled, "controlled"),
    }
    for stratum in strata:
        subset = [cell for cell in atlas if cell.stratum == stratum]
        out[f"atlas_{stratum}"] = summarize(subset, f"atlas {stratum}")
    return out


# Values the manuscript prints, to 4 dp, with the section that prints each.
# A failure here means the paper and the artifacts have diverged. Fix the paper.
PAPER_VALUES = {
    # sec:atlas:netgross, prose and tab:atlas-strata
    "atlas.cells": 1707,
    "atlas.ratio_of_medians": 5.4000,
    "atlas_S1.cells": 1398,
    "atlas_S1.ratio_of_medians": 5.2232,
    "atlas_S2.cells": 309,
    "atlas_S2.ratio_of_medians": 5.1936,
    "atlas.median_churn": 0.1200,
    "atlas.median_abs_net_delta": 0.0222,
    "atlas_S1.median_churn": 0.1375,
    "atlas_S1.median_abs_net_delta": 0.0263,
    "atlas_S2.median_churn": 0.0480,
    "atlas_S2.median_abs_net_delta": 0.0092,
    "atlas.per_cell_median_exclude": 3.8452,
    "atlas.counts.included": 1562,
    "atlas.counts.zero_delta": 145,
    "atlas.counts.zero_delta_with_churn": 128,
    # res:churnratio, sec:minigrid:churnratio
    "controlled.cells": 8,
    "controlled.per_cell_median_exclude": 12.7080,
    "controlled.ratio_of_medians": 12.1415,
    "controlled.counts.zero_delta": 0,
    "controlled.per_cell_min": 3.0372,
    "controlled.per_cell_max": 30.4483,
    # sec:atlas:identical and the zero-denominator disclosure
    "atlas.per_cell_median_extended": 4.2000,
    "atlas.counts.zero_delta_zero_churn": 17,
    # README.md, which names this quantity separately
    "atlas.answer_churn_ratio_of_medians": 13.5000,
}


def _dig(data: dict, dotted: str):
    node = data
    for part in dotted.split("."):
        node = node[part]
    return node


def check(data: dict, tolerance: float = 5e-5) -> list[str]:
    """Every mismatch, not just the first: a partial report invites a partial fix."""
    failures = []
    for key, expected in PAPER_VALUES.items():
        actual = _dig(data, key)
        if isinstance(expected, int):
            if actual != expected:
                failures.append(f"{key}: paper says {expected}, artifacts give {actual}")
        elif abs(actual - expected) > tolerance:
            failures.append(f"{key}: paper says {expected}, artifacts give {actual:.6f}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--atlas", default=str(ATLAS_CSV))
    parser.add_argument("--controlled", default=str(CONTROLLED_JSON))
    parser.add_argument("--json", action="store_true", help="emit the full report as JSON")
    parser.add_argument("--check", action="store_true",
                        help="verify the values the manuscript prints, and exit non-zero on any drift")
    args = parser.parse_args()

    data = report(args.atlas, args.controlled)

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        for key in ("atlas", "atlas_S1", "atlas_S2", "controlled"):
            block = data[key]
            counts = block["counts"]
            print(f"{block['population']}: {block['cells']} cells")
            print(f"  median churn                 {block['median_churn']:.8f}")
            print(f"  median |net delta|           {block['median_abs_net_delta']:.8f}")
            print(f"  ratio of medians             {block['ratio_of_medians']:.4f}")
            print(f"  median of per-cell ratios    {block['per_cell_median_exclude']:.4f}"
                  f"   (over {counts['included']} cells)")
            print(f"  ... same, zero delta kept    {block['per_cell_median_extended']:.4f}"
                  f"   (over {counts['finite'] + counts['zero_delta_with_churn']} cells)")
            print(f"  zero net delta               {counts['zero_delta']}"
                  f"   ({counts['zero_delta_with_churn']} with churn,"
                  f" {counts['zero_delta_zero_churn']} without)")
            print()

    if args.check:
        failures = check(data)
        if failures:
            print("CHURN_RATIO: FAILED")
            for line in failures:
                print(f"  {line}")
            return 1
        print(f"CHURN_RATIO: OK -- {len(PAPER_VALUES)} printed values reproduce from the artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
