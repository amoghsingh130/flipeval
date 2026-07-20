"""Build the practitioner certification tables (ATLAS_MINING_REGISTRATION §5).

For each benchmark family and equivalence margin, report the number of items an
evaluation needs in order to certify equivalence via TOST at 95% confidence,
evaluated at the empirical 25th/50th/75th percentiles of the discordance rates
the atlas actually observed for that family. The independent-binomial column is
carried alongside as the naive comparison a practitioner would otherwise reach
for -- the gap between the two columns is the argument for paired evaluation.

Probe cells are excluded per ATLAS_MINING_REGISTRATION §6.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from scripts.audit_stats import (
    ALPHA,
    POWER,
    independent_binomial_sd,
    load_atlas_cells,
    paired_flip_sd,
    quantiles,
    required_n_for_tost,
    sha256_of,
)

MARGINS_PP = (1.0, 2.0, 3.0)
MIN_CELLS_PER_FAMILY = 4  # below this a quartile is not meaningfully estimated


def build_rows(atlas: Path) -> list[dict]:
    cells = load_atlas_cells(atlas)
    by_family: dict[str, list] = defaultdict(list)
    for cell in cells:
        by_family[cell.benchmark].append(cell)
    by_family["ALL (pooled)"] = list(cells)

    rows = []
    for family in sorted(by_family, key=lambda k: (k == "ALL (pooled)", k)):
        family_cells = by_family[family]
        if len(family_cells) < MIN_CELLS_PER_FAMILY:
            continue
        discordances = [c.discordance for c in family_cells]
        baselines = [c.baseline_accuracy for c in family_cells]
        disc_q = quantiles(discordances)
        # The naive column is evaluated at the family's median baseline accuracy,
        # since the independent-binomial variance depends on accuracy, not churn.
        median_baseline = quantiles(baselines)["median"]
        sd_indep = independent_binomial_sd(median_baseline)

        for margin_pp in MARGINS_PP:
            margin = margin_pp / 100.0
            row = {
                "benchmark_family": family,
                "n_atlas_cells": len(family_cells),
                "margin_pp": margin_pp,
                "median_baseline_accuracy": round(median_baseline, 4),
                "required_n_independent_binomial": required_n_for_tost(sd_indep, margin),
            }
            for label in ("p25", "median", "p75"):
                discordance = disc_q[label]
                row[f"discordance_{label}"] = round(discordance, 6)
                row[f"required_n_{label}"] = required_n_for_tost(paired_flip_sd(discordance), margin)
            row["paired_advantage_at_median"] = (
                round(row["required_n_independent_binomial"] / row["required_n_median"], 2)
                if row["required_n_median"] else "")
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", default="results/atlas_cells_summary.csv")
    parser.add_argument("--output", default="results/certification_tables.csv")
    args = parser.parse_args()

    atlas = Path(args.atlas)
    rows = build_rows(atlas)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    families = sorted({r["benchmark_family"] for r in rows})
    print(f"CERT_INPUT_SHA256 atlas={sha256_of(atlas)}")
    print(f"CERT_ALPHA={ALPHA} POWER={POWER}")
    print(f"CERT_FAMILIES {len(families)}: {', '.join(families)}")
    print(f"CERT_ROWS {len(rows)}")
    for row in rows:
        if row["benchmark_family"] == "ALL (pooled)":
            print(f"CERT_POOLED margin={row['margin_pp']:g}pp "
                  f"disc_median={row['discordance_median']:.4f} "
                  f"n_median={row['required_n_median']} "
                  f"n_p25={row['required_n_p25']} n_p75={row['required_n_p75']} "
                  f"n_independent={row['required_n_independent_binomial']} "
                  f"advantage={row['paired_advantage_at_median']}x")
    print(f"CERT_OUTPUT {output}")


if __name__ == "__main__":
    main()
