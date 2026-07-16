"""Atlas flip analysis over the frozen public-data pair manifest.

Implements sections 4-6 of docs/ATLAS_MINING_REGISTRATION_2026-07-15.md against
docs/atlas_pair_manifest.json (frozen by commit f06348f). Exclusion decisions
are computed strictly before any metric, and every enumerated cell is written
regardless of outcome. Statistics come from flipeval.compare (registered suite:
net delta, flip rates, churn, exact two-sided McNemar, TOST at the 2 pp margin,
MDD at 80% power, required-n).
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from flipeval.core import compare

TOST_MARGIN = 0.02
PROMPT_PASS_THRESHOLD = 0.99
S2_METRIC_PRIORITY = ("acc_norm", "exact_match", "acc", "prompt_level_strict_acc")
HF_TREE = "https://huggingface.co/api/datasets/{repo}/tree/main?recursive=true"
HF_RESOLVE = "https://huggingface.co/datasets/{repo}/resolve/main/{path}"


class CellSkip(Exception):
    """A cell that cannot be analyzed; recorded in the exclusion table."""


# ---------------------------------------------------------------------------
# Section 4.1: join-key deduplication and joining
# ---------------------------------------------------------------------------

def dedupe_join_keys(rows: Sequence[Mapping[str, Any]], key_of) -> tuple[dict[str, Mapping[str, Any]], int]:
    """Drop every row whose join key occurs more than once; return (map, dropped)."""
    counts: dict[str, int] = {}
    for row in rows:
        key = key_of(row)
        if key is None:
            continue
        counts[str(key)] = counts.get(str(key), 0) + 1
    kept: dict[str, Mapping[str, Any]] = {}
    dropped = 0
    for row in rows:
        key = key_of(row)
        if key is None:
            dropped += 1
            continue
        key = str(key)
        if counts[key] > 1:
            dropped += 1
        else:
            kept[key] = row
    return kept, dropped


def join_cell(
    base_rows: Sequence[Mapping[str, Any]],
    quant_rows: Sequence[Mapping[str, Any]],
    *,
    key_of,
    identity_of,
    prompt_of,
) -> dict[str, Any]:
    """Apply the section 4 gates and return join statistics plus matched items.

    identity_of guards the join itself (byte-identical doc for S2; for S1 the
    example hash is both key and identity, so identity_of may return the key).
    prompt_of is the full-prompt hash used for the 99% pass gate.
    """
    base_map, base_dropped = dedupe_join_keys(base_rows, key_of)
    quant_map, quant_dropped = dedupe_join_keys(quant_rows, key_of)
    shared = sorted(set(base_map) & set(quant_map))
    joinable = [k for k in shared if identity_of(base_map[k]) == identity_of(quant_map[k])]
    passing = [k for k in joinable if prompt_of(base_map[k]) is not None
               and prompt_of(base_map[k]) == prompt_of(quant_map[k])]
    pass_rate = (len(passing) / len(joinable)) if joinable else 0.0
    excluded = not joinable or pass_rate < PROMPT_PASS_THRESHOLD
    return {
        "base_rows": len(base_rows),
        "quant_rows": len(quant_rows),
        "base_dropped_duplicate_keys": base_dropped,
        "quant_dropped_duplicate_keys": quant_dropped,
        "shared_keys": len(shared),
        "joinable": len(joinable),
        "prompt_identical": len(passing),
        "prompt_pass_rate": pass_rate,
        "excluded": excluded,
        "exclusion_reason": (
            None if not excluded
            else "no joinable items" if not joinable
            else f"prompt-hash pass rate {pass_rate:.4f} < {PROMPT_PASS_THRESHOLD}"
        ),
        "matched": [(k, base_map[k], quant_map[k]) for k in passing],
    }


# ---------------------------------------------------------------------------
# Section 5: correctness and prediction extraction
# ---------------------------------------------------------------------------

def s1_correctness_column(rows: Sequence[Mapping[str, Any]]) -> str:
    for column in ("acc_norm", "acc"):
        if any(row.get(column) is not None for row in rows):
            return column
    raise CellSkip("no acc_norm or acc column in S1 rows")


def binary_correct(value: Any, column: str) -> bool:
    number = float(value)
    if number not in (0.0, 1.0):
        raise CellSkip(f"{column} is not binary (saw {number}); cell has no 0/1 correctness")
    return bool(number)


def s1_prediction(row: Mapping[str, Any]) -> str | None:
    predictions = row.get("predictions")
    if predictions is None or (hasattr(predictions, "__len__") and len(predictions) == 0):
        return None
    values = list(predictions)
    if all(isinstance(v, (int, float)) for v in values):
        return str(max(range(len(values)), key=lambda i: float(values[i])))
    return str(values[0])


def s2_metric_column(rows: Sequence[Mapping[str, Any]]) -> str:
    for column in S2_METRIC_PRIORITY:
        if any(row.get(column) is not None for row in rows):
            return column
    raise CellSkip(f"no metric column among {S2_METRIC_PRIORITY} in S2 rows")


def s2_prediction(row: Mapping[str, Any]) -> str | None:
    resps = row.get("filtered_resps") or row.get("resps")
    if not resps:
        return None
    first = resps[0]
    while isinstance(first, (list, tuple)) and first:
        first = first[0]
    return str(first)


def build_records(
    matched: Sequence[tuple[str, Mapping[str, Any], Mapping[str, Any]]],
    *,
    correctness_column: str,
    prediction_of,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    base_records, quant_records = [], []
    prediction_available = True
    for key, base_row, quant_row in matched:
        base_pred = prediction_of(base_row)
        quant_pred = prediction_of(quant_row)
        if base_pred is None or quant_pred is None:
            prediction_available = False
        base_records.append({
            "item_id": key,
            "correct": binary_correct(base_row[correctness_column], correctness_column),
            "prediction": base_pred if base_pred is not None else "",
        })
        quant_records.append({
            "item_id": key,
            "correct": binary_correct(quant_row[correctness_column], correctness_column),
            "prediction": quant_pred if quant_pred is not None else "",
        })
    return base_records, quant_records, prediction_available


def analyze_cell(
    matched_join: Mapping[str, Any],
    *,
    correctness_column: str,
    prediction_of,
    bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    """Registered metric suite for one non-excluded cell."""
    base_records, quant_records, prediction_available = build_records(
        matched_join["matched"],
        correctness_column=correctness_column,
        prediction_of=prediction_of,
    )
    result = dataclasses.asdict(
        compare(base_records, quant_records, margin=TOST_MARGIN, bootstrap=bootstrap, seed=seed)
    )
    if not prediction_available:
        result["wrong_to_different_wrong_churn"] = None
        result["total_answer_churn"] = None
    result["prediction_available"] = prediction_available
    result["correctness_column"] = correctness_column
    return result


# ---------------------------------------------------------------------------
# Fetch layer (stdlib HTTPS; no new dependencies)
# ---------------------------------------------------------------------------

def _http_get(url: str, retries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "flipeval-atlas/0.1"})
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except Exception as exc:  # noqa: BLE001 - retried, then re-raised
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def list_repo_files(repo: str, cache_dir: Path) -> list[str]:
    cache = cache_dir / "trees" / f"{repo.replace('/', '__')}.json"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(_http_get(HF_TREE.format(repo=repo)))
    entries = json.loads(cache.read_text(encoding="utf-8"))
    return [entry["path"] for entry in entries if entry.get("type") == "file"]


def download(repo: str, path: str, cache_dir: Path) -> Path:
    target = cache_dir / "files" / repo.replace("/", "__") / path
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        quoted = urllib.parse.quote(path)
        target.write_bytes(_http_get(HF_RESOLVE.format(repo=repo, path=quoted)))
    return target


def normalize_token(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()


def timestamp_key(timestamp: str) -> str:
    """Canonical digits-only form; cardData uses underscores where dirs use -/:."""
    return re.sub(r"[^0-9]", "", timestamp)


def find_s1_task_file(files: Sequence[str], task_config: str, run_timestamps: Sequence[str]) -> str:
    """Latest run's parquet for a task config like 'harness_gsm8k_5' (section 3.2)."""
    want = normalize_token(task_config)
    for timestamp in sorted(run_timestamps, key=timestamp_key, reverse=True):
        for path in files:
            if not path.endswith(".parquet") or "/" not in path:
                continue
            if timestamp_key(path.split("/")[0]) != timestamp_key(timestamp):
                continue
            stem = Path(path).name
            if f"_{want}_" in f"_{normalize_token(stem)}_":
                return path
    raise CellSkip(f"no parquet found for task {task_config} in runs {list(run_timestamps)}")


def find_s2_task_file(files: Sequence[str], variant_dir: str, task: str, run_timestamps: Sequence[str]) -> str:
    for timestamp in sorted(run_timestamps, reverse=True):
        for path in files:
            parts = path.split("/")
            if parts[0] != variant_dir or not path.endswith(".jsonl"):
                continue
            name = Path(path).name
            if name in (f"samples_{task}_{timestamp}.jsonl",
                        f"samples_leaderboard_{task}_{timestamp}.jsonl"):
                return path
    raise CellSkip(f"no samples file for {variant_dir}/{task} in runs {list(run_timestamps)}")


def load_s1_rows(parquet_path: Path) -> list[dict[str, Any]]:
    import pandas as pd

    frame = pd.read_parquet(parquet_path)
    return frame.to_dict("records")


def load_s2_rows(jsonl_path: Path) -> list[dict[str, Any]]:
    rows = []
    with jsonl_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def harness_identity(files: Sequence[str], repo: str, prefix: str, cache_dir: Path) -> dict[str, Any] | None:
    """Best-effort section 4.3 provenance from the side's results JSON."""
    candidates = sorted(p for p in files if p.startswith(prefix) and "results" in Path(p).name and p.endswith(".json"))
    if not candidates:
        return None
    try:
        payload = json.loads(download(repo, candidates[-1], cache_dir).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - provenance is best-effort, never gates analysis
        return None
    config = payload.get("config") or payload.get("config_general") or {}
    return {
        "results_file": candidates[-1],
        "git_hash": payload.get("git_hash") or config.get("lighteval_sha") or config.get("git_hash"),
        "model_args": config.get("model_args") or config.get("model_config_path"),
        "dtype": config.get("model_dtype") or config.get("dtype"),
    }


# ---------------------------------------------------------------------------
# Per-source row accessors (section 4.1 join fields)
# ---------------------------------------------------------------------------

def s1_key(row: Mapping[str, Any]) -> Any:
    hashes = row.get("hashes") or {}
    return hashes.get("example") if isinstance(hashes, Mapping) else None


def s1_prompt(row: Mapping[str, Any]) -> Any:
    hashes = row.get("hashes") or {}
    return hashes.get("full_prompt") if isinstance(hashes, Mapping) else None


def s2_key(row: Mapping[str, Any]) -> Any:
    return row.get("doc_id")


def s2_identity(row: Mapping[str, Any]) -> Any:
    if row.get("doc_hash") is not None:
        return row["doc_hash"]
    return json.dumps(row.get("doc"), sort_keys=True)


def s2_prompt(row: Mapping[str, Any]) -> Any:
    return row.get("prompt_hash")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def repo_from_url(url: str) -> str:
    match = re.search(r"huggingface\.co/datasets/([^/\s(]+/[^/\s(]+)", url)
    if not match:
        raise CellSkip(f"cannot parse dataset repo from {url}")
    return match.group(1).rstrip(")")


def run_pair(pair: Mapping[str, Any], pair_index: int, *, cache_dir: Path, output_dir: Path,
             bootstrap: int, seed: int, only_task: str | None = None) -> list[dict[str, Any]]:
    source = pair["source"]
    rows_out: list[dict[str, Any]] = []
    if source == "S1":
        base_repo = repo_from_url(pair["base_details_url"])
        quant_repo = repo_from_url(pair["quantized_details_url"])
        base_files = list_repo_files(base_repo, cache_dir)
        quant_files = list_repo_files(quant_repo, cache_dir)
    else:
        base_repo = quant_repo = repo_from_url(pair["quantized_details_url"])
        base_files = quant_files = list_repo_files(base_repo, cache_dir)
        base_dir = pair["base_model"].split("/")[-1]
        quant_dir = pair["quantized_model"].split("/")[-1]

    for task in pair["tasks"]:
        if only_task and task != only_task:
            continue
        cell: dict[str, Any] = {
            "pair_index": pair_index,
            "source": source,
            "quantized_model": pair["quantized_model"],
            "base_model": pair["base_model"],
            "method": pair.get("method_guess"),
            "task": task,
            "contains_disclosed_probe_cell": bool(pair.get("contains_disclosed_probe_cell")),
        }
        try:
            if source == "S1":
                base_path = download(base_repo, find_s1_task_file(
                    base_files, task, pair["run_timestamps"]["base"]), cache_dir)
                quant_path = download(quant_repo, find_s1_task_file(
                    quant_files, task, pair["run_timestamps"]["quantized"]), cache_dir)
                base_rows, quant_rows = load_s1_rows(base_path), load_s1_rows(quant_path)
                joined = join_cell(base_rows, quant_rows, key_of=s1_key, identity_of=s1_key, prompt_of=s1_prompt)
                correctness = s1_correctness_column(quant_rows)
                prediction_of = s1_prediction
                cell["harness_identity"] = {
                    "base": harness_identity(base_files, base_repo, "", cache_dir),
                    "quantized": harness_identity(quant_files, quant_repo, "", cache_dir),
                }
            else:
                base_path = download(base_repo, find_s2_task_file(
                    base_files, base_dir, task, pair["run_timestamps"]["base"]), cache_dir)
                quant_path = download(quant_repo, find_s2_task_file(
                    quant_files, quant_dir, task, pair["run_timestamps"]["quantized"]), cache_dir)
                base_rows, quant_rows = load_s2_rows(base_path), load_s2_rows(quant_path)
                joined = join_cell(base_rows, quant_rows, key_of=s2_key, identity_of=s2_identity, prompt_of=s2_prompt)
                correctness = s2_metric_column(quant_rows)
                prediction_of = s2_prediction
                cell["harness_identity"] = {
                    "base": harness_identity(base_files, base_repo, base_dir, cache_dir),
                    "quantized": harness_identity(quant_files, quant_repo, quant_dir, cache_dir),
                }

            cell["join"] = {k: v for k, v in joined.items() if k != "matched"}
            if joined["excluded"]:
                cell["metrics"] = None
            else:
                cell["metrics"] = analyze_cell(
                    joined, correctness_column=correctness,
                    prediction_of=prediction_of, bootstrap=bootstrap, seed=seed,
                )
        except CellSkip as skip:
            cell["join"] = None
            cell["metrics"] = None
            cell["skip_reason"] = str(skip)

        rows_out.append(cell)
        cell_dir = output_dir / "cells"
        cell_dir.mkdir(parents=True, exist_ok=True)
        cell_path = cell_dir / f"pair{pair_index:03d}__{normalize_token(task)}.json"
        cell_path.write_text(json.dumps(cell, indent=2, default=str) + "\n", encoding="utf-8")
    return rows_out


SUMMARY_COLUMNS = [
    "pair_index", "source", "quantized_model", "base_model", "method", "task",
    "contains_disclosed_probe_cell", "excluded_or_skipped", "reason", "n",
    "correctness_column", "baseline_accuracy", "method_accuracy", "net_accuracy_delta",
    "harmful_flip_rate", "beneficial_flip_rate", "accuracy_state_churn",
    "total_answer_churn", "mcnemar_p", "tost_equivalent", "mdd_80_power",
    "required_n_for_observed_delta_80_power", "prompt_pass_rate",
]


def summarize(cells: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for cell in cells:
        metrics = cell.get("metrics") or {}
        join = cell.get("join") or {}
        rows.append({
            "pair_index": cell["pair_index"],
            "source": cell["source"],
            "quantized_model": cell["quantized_model"],
            "base_model": cell["base_model"],
            "method": cell["method"],
            "task": cell["task"],
            "contains_disclosed_probe_cell": cell["contains_disclosed_probe_cell"],
            "excluded_or_skipped": not metrics,
            "reason": cell.get("skip_reason") or join.get("exclusion_reason") or "",
            "n": metrics.get("n", ""),
            "correctness_column": metrics.get("correctness_column", ""),
            "baseline_accuracy": metrics.get("baseline_accuracy", ""),
            "method_accuracy": metrics.get("method_accuracy", ""),
            "net_accuracy_delta": metrics.get("net_accuracy_delta", ""),
            "harmful_flip_rate": metrics.get("harmful_flip_rate", ""),
            "beneficial_flip_rate": metrics.get("beneficial_flip_rate", ""),
            "accuracy_state_churn": metrics.get("accuracy_state_churn", ""),
            "total_answer_churn": metrics.get("total_answer_churn", ""),
            "mcnemar_p": metrics.get("mcnemar_p", ""),
            "tost_equivalent": metrics.get("tost_equivalent", ""),
            "mdd_80_power": metrics.get("mdd_80_power", ""),
            "required_n_for_observed_delta_80_power": metrics.get("required_n_for_observed_delta_80_power", ""),
            "prompt_pass_rate": join.get("prompt_pass_rate", ""),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="docs/atlas_pair_manifest.json")
    parser.add_argument("--output", default="results/atlas")
    parser.add_argument("--cache-dir", default="outputs/atlas_cache")
    parser.add_argument("--pairs", help="Comma-separated pair indices or ranges, e.g. 0,3,10-12")
    parser.add_argument("--source", choices=["S1", "S2"])
    parser.add_argument("--task")
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest.get("protocol") != "ATLAS_MINING_REGISTRATION_2026-07-15":
        raise SystemExit("manifest does not reference the frozen protocol; refusing to run")

    selected = set()
    if args.pairs:
        for chunk in args.pairs.split(","):
            if "-" in chunk:
                low, high = chunk.split("-")
                selected.update(range(int(low), int(high) + 1))
            else:
                selected.add(int(chunk))

    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir)
    all_cells: list[dict[str, Any]] = []
    for index, pair in enumerate(manifest["pairs"]):
        if selected and index not in selected:
            continue
        if args.source and pair["source"] != args.source:
            continue
        print(f"[pair {index}] {pair['quantized_model']} vs {pair['base_model']}", flush=True)
        all_cells.extend(run_pair(
            pair, index, cache_dir=cache_dir, output_dir=output_dir,
            bootstrap=args.bootstrap, seed=args.seed, only_task=args.task,
        ))

    summary = summarize(all_cells)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "atlas_cells_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(summary)
    excluded = [row for row in summary if row["excluded_or_skipped"]]
    with (output_dir / "atlas_exclusions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(excluded)
    print(f"{len(summary)} cells written ({len(excluded)} excluded/skipped) -> {output_dir}", flush=True)


if __name__ == "__main__":
    main()
