"""Compatibility CLI for analyzing a pilot run directory with flipeval."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from flipeval.core import _compare_arrays, _rank_stability_arrays

PAIR_SUMMARY_COLUMNS = [
    "task", "method", "n", "baseline_accuracy", "compressed_accuracy",
    "net_accuracy_delta", "harmful_flip_rate", "beneficial_flip_rate",
    "accuracy_state_churn", "wrong_to_different_wrong_churn", "total_answer_churn",
    "net_accuracy_delta_ci_low", "harmful_flip_rate_ci_low", "beneficial_flip_rate_ci_low",
    "accuracy_state_churn_ci_low", "wrong_to_different_wrong_churn_ci_low",
    "total_answer_churn_ci_low", "net_accuracy_delta_ci_high", "harmful_flip_rate_ci_high",
    "beneficial_flip_rate_ci_high", "accuracy_state_churn_ci_high",
    "wrong_to_different_wrong_churn_ci_high", "total_answer_churn_ci_high",
    "mcnemar_b_harmful", "mcnemar_c_beneficial", "mcnemar_p", "tost_equivalent",
    "tost_p_low", "tost_p_high", "mdd_80_power", "required_n_for_observed_delta_80_power",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze compressed-LLM pilot JSONL logs.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--baseline", default="fp16")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--equivalence-margin", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    pair_df, rank_df = analyze_run_directory(
        Path(args.run_dir), args.baseline, args.bootstrap, args.alpha, args.equivalence_margin, args.seed
    )
    pair_path = Path(args.run_dir) / "pair_summary.csv"
    rank_path = Path(args.run_dir) / "rank_instability.csv"
    pair_df.to_csv(pair_path, index=False)
    rank_df.to_csv(rank_path, index=False)
    print(f"Wrote {pair_path}")
    print(pair_df.to_string(index=False))
    if not rank_df.empty:
        print(f"\nWrote {rank_path}")
        print(rank_df.to_string(index=False))


def analyze_run_directory(run_dir: Path, baseline_name="fp16", bootstrap=2000, alpha=0.05, margin=0.02, seed=0):
    df = read_jsonl_dir(run_dir)
    if df.empty:
        raise ValueError(f"no JSONL records found in {run_dir}")
    rng = np.random.default_rng(seed)
    pair_rows: list[dict[str, Any]] = []
    for (task, method), group in df[df["method"] != baseline_name].groupby(["task", "method"]):
        baseline = df[(df["task"] == task) & (df["method"] == baseline_name)]
        base_records, method_records = _paired_records(baseline, group)
        result = _compare_arrays(base_records, method_records, margin, bootstrap, rng, alpha)
        values = result.to_dict(flatten_cis=True)
        values["compressed_accuracy"] = values.pop("method_accuracy")
        pair_rows.append({"task": task, "method": method, **values})
    pair_df = pd.DataFrame(pair_rows).sort_values(["task", "method"])
    pair_df = pair_df[PAIR_SUMMARY_COLUMNS]

    rank_rows = []
    for task, task_df in df.groupby("task"):
        baseline = task_df[task_df["method"] == baseline_name]
        compressed = task_df[task_df["method"] != baseline_name].copy()
        compressed["method_group"] = compressed["method"].map(method_group)
        methods = sorted(compressed["method_group"].unique())
        if len(methods) < 2:
            continue
        base_map = {str(row.item_id): bool(row.correct) for row in baseline.itertuples()}
        method_maps = {
            method: {str(row.item_id): bool(row.correct) for row in compressed[compressed["method_group"] == method].itertuples()}
            for method in methods
        }
        common_ids = sorted(set(base_map).intersection(*(set(values) for values in method_maps.values())))
        scores = {
            method: np.array([float(values[item_id]) - float(base_map[item_id]) for item_id in common_ids])
            for method, values in method_maps.items()
        }
        result = _rank_stability_arrays(scores, len(common_ids), bootstrap, rng)
        rank_rows.append({
            "task": task,
            "comparison": "bootstrap_items",
            "methods": ",".join(methods),
            "n_common_items": result.n_common_items,
            "full_sample_winner": result.full_sample_winner,
            "rank_flip_rate": result.rank_flip_rate,
            **{f"delta_{name}": value for name, value in result.deltas.items()},
        })
    return pair_df, pd.DataFrame(rank_rows)


def _paired_records(baseline: pd.DataFrame, method: pd.DataFrame):
    paired = baseline[["item_id", "correct", "prediction"]].merge(
        method[["item_id", "correct", "prediction"]], on="item_id", suffixes=("_base", "_method")
    )
    base = [{"item_id": row.item_id, "correct": row.correct_base, "prediction": row.prediction_base} for row in paired.itertuples()]
    compressed = [{"item_id": row.item_id, "correct": row.correct_method, "prediction": row.prediction_method} for row in paired.itertuples()]
    return base, compressed


def read_jsonl_dir(run_dir: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(run_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as stream:
            rows.extend(json.loads(line) for line in stream if line.strip())
    return pd.DataFrame(rows)


def method_group(method: str) -> str:
    return re.sub(r"([_-]s(?:eed)?\d+)$", "", method)


if __name__ == "__main__":
    main()
