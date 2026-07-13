from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .core import compare, paired_seed_bootstrap
from .io import from_lm_eval_harness, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="flipeval")
    subparsers = parser.add_subparsers(dest="command", required=True)
    compare_command = subparsers.add_parser("compare", help="Compare paired model-evaluation records.")
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
    args = parser.parse_args()

    if args.command == "paired-seeds":
        _run_paired_seeds(args)
        return

    loader = from_lm_eval_harness if args.format == "lm-eval" else read_jsonl
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


def _run_paired_seeds(args) -> None:
    loader = from_lm_eval_harness if args.format == "lm-eval" else read_jsonl
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


def _parse_seed_paths(values, flag):
    result = {}
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


def _single_value(records, field):
    values = {str(record[field]) for record in records if field in record}
    return values.pop() if len(values) == 1 else None


if __name__ == "__main__":
    main()
