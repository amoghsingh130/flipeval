"""Command line interface.

Four subcommands, each a thin wrapper over the library:

    flipeval report       the paper's five-line reporting standard, in one command
    flipeval required-n   look up the certification requirement for a benchmark
    flipeval compare      full paired comparison, as a one-row CSV plus JSON
    flipeval paired-seeds the registered seed-by-item bootstrap

`report` is the one to reach for first: it is the paper's proposal made
runnable. `compare` and `paired-seeds` are unchanged from earlier versions --
their arguments, their stdout and the files they write are the same, because the
research pipeline consumes them.

MARGIN UNITS. `--margin` is a proportion (0.02 = two accuracy points) everywhere
it compares against accuracies, and percentage points only in `required-n`,
where it indexes a table published in points. Both directions are range-checked
and say which unit they wanted, rather than silently accepting a number that is
100x wrong.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from . import __version__
from .certification import (
    PERCENTILES,
    available_benchmarks,
    format_required_n,
    required_n_for_benchmark,
)
from .core import Record, compare, paired_seed_bootstrap
from .io import from_lm_eval_harness, read_jsonl
from .report import five_line_report

EXIT_INPUT_ERROR = 2

MAIN_EPILOG = """\
examples:
  # The paper's five-line reporting standard, from two per-item files.
  flipeval report fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --benchmark mmlu

  # The same, straight off two lm-evaluation-harness --output_path directories.
  flipeval report runs/fp16 runs/gptq --format lm-eval --margin 0.02 \\
      --benchmark mmlu --per-item-outputs https://example.org/per-item

  # How many items does an MMLU equivalence claim at 2 points need?
  flipeval required-n --benchmark mmlu --margin 2.0

  # Full paired comparison, written as a one-row CSV.
  flipeval compare fp16.mmlu.jsonl gptq.mmlu.jsonl --margin 0.02 --output pair.csv
"""

REPORT_EPILOG = """\
The five lines are the standard proposed in the paper: declare a margin; run the
paired equivalence test at that margin; report churn beside net delta; cite the
sample size met against the count the benchmark family requires; release
per-item outputs. Lines 1-4 are computed here. Line 5 is a release action, so it
reports the location given with --per-item-outputs and otherwise says the line
is not met.

examples:
  flipeval report fp16.jsonl gptq.jsonl --margin 0.02 --benchmark mmlu
  flipeval report runs/fp16 runs/gptq --format lm-eval --margin 0.02 --json
"""

REQUIRED_N_EPILOG = """\
--margin is in PERCENTAGE POINTS here (2.0 = a two-point margin), because that
is how the published table is indexed. The table is not interpolated.

examples:
  flipeval required-n --benchmark mmlu --margin 2.0
  flipeval required-n --benchmark gsm8k --margin 1.0 --percentile p75
  flipeval required-n --list
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flipeval",
        description=(
            "Paired, per-item statistics for deciding whether a compressed model is "
            "equivalent to its baseline."
        ),
        epilog=MAIN_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"flipeval {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_command = subparsers.add_parser(
        "report",
        help="Emit the paper's five-line reporting standard for one pair.",
        epilog=REPORT_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    report_command.add_argument("baseline", help="Per-item records for the reference run.")
    report_command.add_argument("method", help="Per-item records for the run under test.")
    report_command.add_argument(
        "--margin",
        type=float,
        default=0.02,
        help="Equivalence margin as a proportion: 0.02 is two accuracy points (default: 0.02).",
    )
    report_command.add_argument(
        "--benchmark",
        default=None,
        help=(
            "Benchmark family whose published requirement line 4 cites, e.g. mmlu. "
            "Without it, line 4 falls back to this pair's own observed churn."
        ),
    )
    report_command.add_argument(
        "--percentile",
        choices=PERCENTILES,
        default="median",
        help="Which churn percentile of the benchmark family to require (default: median).",
    )
    report_command.add_argument(
        "--per-item-outputs",
        default=None,
        help="Where the per-item files are published. Line 5 is unmet without it.",
    )
    report_command.add_argument("--alpha", type=float, default=0.05)
    report_command.add_argument("--bootstrap", type=int, default=1000)
    report_command.add_argument("--seed", type=int, default=0)
    report_command.add_argument(
        "--format",
        choices=("jsonl", "lm-eval"),
        default="jsonl",
        help="Input format. 'lm-eval' accepts a --log_samples file or an output directory.",
    )
    report_command.add_argument(
        "--table",
        default=None,
        help="Certification table to read (default: the copy shipped with flipeval).",
    )
    report_command.add_argument(
        "--json", action="store_true", help="Emit the report and its numbers as JSON."
    )
    report_command.add_argument(
        "--output", default=None, help="Also write the block (or the JSON) to this file."
    )

    required_n_command = subparsers.add_parser(
        "required-n",
        help="Look up the items an equivalence claim needs, by benchmark family.",
        epilog=REQUIRED_N_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    required_n_command.add_argument("--benchmark", default=None, help="Benchmark family, e.g. mmlu.")
    required_n_command.add_argument(
        "--margin",
        type=float,
        default=2.0,
        help="Margin in PERCENTAGE POINTS (default: 2.0).",
    )
    required_n_command.add_argument(
        "--percentile",
        choices=PERCENTILES,
        default="median",
        help="Churn percentile to report as the selected requirement (default: median).",
    )
    required_n_command.add_argument(
        "--table",
        default=None,
        help="Certification table to read (default: the copy shipped with flipeval).",
    )
    required_n_command.add_argument(
        "--list", action="store_true", help="List the benchmark families in the table and exit."
    )
    required_n_command.add_argument("--json", action="store_true", help="Emit the row as JSON.")

    compare_command = subparsers.add_parser(
        "compare",
        help="Compare paired model-evaluation records; writes a one-row CSV.",
    )
    compare_command.add_argument("baseline")
    compare_command.add_argument("method")
    compare_command.add_argument("--margin", type=float, default=0.02)
    compare_command.add_argument("--bootstrap", type=int, default=1000)
    compare_command.add_argument("--seed", type=int, default=0)
    compare_command.add_argument("--format", choices=("jsonl", "lm-eval"), default="jsonl")
    compare_command.add_argument("--output", default="pair_summary.csv")

    seeds_command = subparsers.add_parser(
        "paired-seeds", help="Run the registered paired seed-by-item bootstrap."
    )
    seeds_command.add_argument(
        "--first", action="append", required=True, metavar="SEED=JSONL", help="First-method records."
    )
    seeds_command.add_argument(
        "--second", action="append", required=True, metavar="SEED=JSONL", help="Second-method records."
    )
    seeds_command.add_argument("--first-name", default="gptq")
    seeds_command.add_argument("--second-name", default="awq")
    seeds_command.add_argument("--bootstrap", type=int, default=2000)
    seeds_command.add_argument("--seed", type=int, default=0)
    seeds_command.add_argument("--alpha", type=float, default=0.05)
    seeds_command.add_argument("--expected-seeds", type=int, default=5)
    seeds_command.add_argument("--format", choices=("jsonl", "lm-eval"), default="jsonl")
    seeds_command.add_argument("--output", default="hierarchical_summary.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code; 2 for bad input."""
    args = build_parser().parse_args(argv)
    handlers: dict[str, Callable[[argparse.Namespace], int]] = {
        "report": _run_report,
        "required-n": _run_required_n,
        "compare": _run_compare,
        "paired-seeds": _run_paired_seeds,
    }
    try:
        return handlers[args.command](args)
    except (ValueError, TypeError, FileNotFoundError, IsADirectoryError) as error:
        # Input defects are reported as a message, not a traceback: every one of
        # these carries a message written to be read by the person who typed the
        # command, and a stack trace buries it.
        print(f"error: {error}", file=sys.stderr)
        return EXIT_INPUT_ERROR


def _run_report(args: argparse.Namespace) -> int:
    loader = _loader(args.format)
    report = five_line_report(
        loader(args.baseline),
        loader(args.method),
        margin=args.margin,
        alpha=args.alpha,
        bootstrap=args.bootstrap,
        seed=args.seed,
        benchmark=args.benchmark,
        percentile=args.percentile,
        per_item_outputs=args.per_item_outputs,
        table=args.table,
        baseline_label=str(args.baseline),
        method_label=str(args.method),
    )
    rendered = json.dumps(report.to_dict(), indent=2) if args.json else report.to_text()
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {output}", file=sys.stderr)
    return 0


def _run_required_n(args: argparse.Namespace) -> int:
    if args.list:
        for name in available_benchmarks(args.table):
            print(name)
        return 0
    if args.benchmark is None:
        raise ValueError(
            "required-n needs --benchmark (or --list to see the families the table covers)"
        )
    row = required_n_for_benchmark(args.benchmark, args.margin, table=args.table)
    if args.json:
        payload = row.to_dict()
        payload["percentile"] = args.percentile
        payload["selected_required_n"] = row.required_n(args.percentile)
        print(json.dumps(payload, indent=2))
    else:
        print(format_required_n(row, args.percentile))
    return 0


def _run_compare(args: argparse.Namespace) -> int:
    loader = _loader(args.format)
    baseline, method = loader(args.baseline), loader(args.method)
    result = compare(baseline, method, margin=args.margin, bootstrap=args.bootstrap, seed=args.seed)
    values = result.to_dict(flatten_cis=True)
    values["compressed_accuracy"] = values.pop("method_accuracy")
    task = _single_value(baseline, "task") or Path(args.baseline).stem.split(".")[-1]
    method_name = _single_value(method, "method") or Path(args.method).stem.split(".")[0]
    row = {"task": task, "method": method_name, **values}
    output = Path(args.output)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    print(json.dumps(result.to_dict(), indent=2))
    print(f"Wrote {output}")
    return 0


def _run_paired_seeds(args: argparse.Namespace) -> int:
    loader = _loader(args.format)
    first_paths = _parse_seed_paths(args.first, "--first")
    second_paths = _parse_seed_paths(args.second, "--second")
    result = paired_seed_bootstrap(
        {label: loader(path) for label, path in first_paths.items()},
        {label: loader(path) for label, path in second_paths.items()},
        method_names=(args.first_name, args.second_name),
        bootstrap=args.bootstrap,
        seed=args.seed,
        alpha=args.alpha,
        expected_seed_count=args.expected_seeds,
    )
    output = Path(args.output)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(result.to_dict(), stream, indent=2)
        stream.write("\n")
    print(json.dumps(result.to_dict(), indent=2))
    print(f"Wrote {output}")
    return 0


def _loader(format_name: str) -> Callable[[str], list[dict[str, Any]]]:
    return from_lm_eval_harness if format_name == "lm-eval" else read_jsonl


def _parse_seed_paths(values: Sequence[str], flag: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"{flag} values must use SEED=PATH syntax: {value!r}")
        label, path = value.split("=", 1)
        if not label or not path:
            raise SystemExit(f"{flag} values must use SEED=PATH syntax: {value!r}")
        if label in result:
            raise SystemExit(f"duplicate {flag} seed label: {label!r}")
        result[label] = path
    return result


def _single_value(records: Sequence[Record], field: str) -> str | None:
    values = {str(record[field]) for record in records if field in record}
    return values.pop() if len(values) == 1 else None


if __name__ == "__main__":
    sys.exit(main())
