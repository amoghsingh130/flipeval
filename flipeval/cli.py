from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .core import compare
from .io import from_lm_eval_harness, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="flipeval")
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("compare", help="Compare paired model-evaluation records.")
    command.add_argument("baseline")
    command.add_argument("method")
    command.add_argument("--margin", type=float, default=0.02)
    command.add_argument("--bootstrap", type=int, default=1000)
    command.add_argument("--seed", type=int, default=0)
    command.add_argument("--format", choices=("jsonl", "lm-eval"), default="jsonl")
    command.add_argument("--output", default="pair_summary.csv")
    args = parser.parse_args()
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


def _single_value(records, field):
    values = {str(record[field]) for record in records if field in record}
    return values.pop() if len(values) == 1 else None


if __name__ == "__main__":
    main()
