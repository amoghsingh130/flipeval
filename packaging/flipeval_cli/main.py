"""Argument parsing and process wiring for the standalone comparison CLI."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from flipeval.core import compare

from .loader import (
    FilterAmbiguity,
    ItemSetMismatch,
    UnscoredRows,
    align_by_item_id,
    load_log_samples,
    require_identical_item_sets,
)
from .verdict import decide, deltas_from_records, render, required_n_at_margin

EXIT_UNDERPOWERED = 1
EXIT_INPUT_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flipeval-compare",
        description=(
            "Compare two lm-eval --log_samples runs on the same items and print a "
            "verdict: CERTIFIED-EQUIVALENT, DEGRADED, IMPROVED, or UNDERPOWERED."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    cmp_parser = subparsers.add_parser(
        "compare", help="Compare two --log_samples files."
    )
    cmp_parser.add_argument("baseline", help="lm-eval --log_samples file for the reference run.")
    cmp_parser.add_argument("candidate", help="lm-eval --log_samples file for the run under test.")
    cmp_parser.add_argument(
        "--margin",
        type=float,
        default=0.02,
        help="Equivalence margin in accuracy points, e.g. 0.02 for 2 points (default: 0.02).",
    )
    cmp_parser.add_argument(
        "--alpha", type=float, default=0.05, help="Significance level (default: 0.05)."
    )
    cmp_parser.add_argument(
        "--bootstrap",
        type=int,
        default=1000,
        help="Bootstrap replicates for churn confidence intervals (default: 1000).",
    )
    cmp_parser.add_argument(
        "--seed", type=int, default=0, help="Bootstrap RNG seed (default: 0)."
    )
    cmp_parser.add_argument(
        "--filter",
        dest="filter_name",
        default=None,
        help=(
            "Which lm-eval scoring filter to compare (e.g. strict-match, "
            "flexible-extract). Required when a file records more than one; the "
            "tool never picks for you, because they are different numbers over "
            "the same generations."
        ),
    )
    cmp_parser.add_argument(
        "--allow-string-compare",
        action="store_true",
        help=(
            "Accept rows carrying no harness metric, whose correctness is then "
            "decided by comparing the extracted prediction against the gold "
            "string. Off by default: that is a different definition of "
            "correctness from the one the harness scored with."
        ),
    )
    cmp_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON instead of a report."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.margin <= 0:
        print("error: --margin must be positive", file=sys.stderr)
        return EXIT_INPUT_ERROR

    try:
        baseline = load_log_samples(
            args.baseline, args.filter_name, args.allow_string_compare
        )
        candidate = load_log_samples(
            args.candidate, args.filter_name, args.allow_string_compare
        )
        item_ids = require_identical_item_sets(
            baseline, candidate, args.baseline, args.candidate
        )
    except (
        FilterAmbiguity,
        UnscoredRows,
        ItemSetMismatch,
        FileNotFoundError,
        ValueError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    baseline_aligned, candidate_aligned = align_by_item_id(baseline, candidate, item_ids)

    result = compare(
        baseline_aligned,
        candidate_aligned,
        margin=args.margin,
        bootstrap=args.bootstrap,
        seed=args.seed,
        alpha=args.alpha,
    )
    verdict = decide(result, args.margin, args.alpha)
    deltas = deltas_from_records(baseline_aligned, candidate_aligned)
    needed = required_n_at_margin(deltas, args.margin)

    if args.json:
        payload = {
            "verdict": verdict.label,
            "headline": verdict.headline,
            "notes": verdict.notes,
            "margin": args.margin,
            "alpha": args.alpha,
            "filter": args.filter_name,
            "allow_string_compare": args.allow_string_compare,
            "baseline_path": args.baseline,
            "candidate_path": args.candidate,
            "required_n_at_margin": needed,
            **result.to_dict(),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            render(
                result,
                verdict,
                args.margin,
                needed,
                args.baseline,
                args.candidate,
                args.filter_name,
            )
        )
    return verdict.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
