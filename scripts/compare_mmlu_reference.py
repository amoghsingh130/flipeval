#!/usr/bin/env python3
"""Compare pilot MMLU predictions with lm-evaluation-harness logged samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable


LABELS = "ABCD"


def _json_records(path: Path) -> Iterable[dict[str, Any]]:
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        yield from payload
    elif isinstance(payload, dict) and isinstance(payload.get("samples"), dict):
        for samples in payload["samples"].values():
            yield from samples
    else:
        raise ValueError(f"unsupported reference JSON structure: {path}")


def _reference_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files = sorted(path.glob("**/samples*.jsonl"))
    if not files:
        files = sorted(path.glob("**/*.json"))
    if not files:
        raise FileNotFoundError(f"no harness sample files found under {path}")
    return files


def _subject(task_name: str) -> str:
    for prefix in ("mmlu_", "mmlu-"):
        if task_name.startswith(prefix):
            return task_name[len(prefix) :]
    return task_name


def _score(response: Any) -> float:
    if isinstance(response, (list, tuple)):
        if not response:
            raise ValueError("empty likelihood response")
        return _score(response[0])
    if isinstance(response, dict):
        for key in ("loglikelihood", "score"):
            if key in response:
                return float(response[key])
    return float(response)


def _reference_row(sample: dict[str, Any]) -> tuple[str, str, str, bool]:
    subject = _subject(str(sample["task_name"]))
    item_id = f"{subject}:test:{int(sample['doc_id'])}"
    responses = sample.get("resps") or sample.get("filtered_resps")
    if not isinstance(responses, list) or len(responses) != 4:
        raise ValueError(f"expected four likelihood responses for {item_id}")
    prediction = LABELS[max(range(4), key=lambda idx: _score(responses[idx]))]
    answer = sample.get("doc", {}).get("answer")
    gold = LABELS[int(answer)] if isinstance(answer, int) else str(answer).strip().upper()[0]
    return item_id, prediction, gold, prediction == gold


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pilot_jsonl", type=Path)
    parser.add_argument("harness_samples", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/mmlu_reference_diff.csv"))
    args = parser.parse_args()

    pilot = {row["item_id"]: row for row in _json_records(args.pilot_jsonl)}
    reference: dict[str, tuple[str, str, bool]] = {}
    for path in _reference_files(args.harness_samples):
        for sample in _json_records(path):
            item_id, prediction, gold, correct = _reference_row(sample)
            reference[item_id] = (prediction, gold, correct)

    missing_pilot = sorted(reference.keys() - pilot.keys())
    missing_reference = sorted(pilot.keys() - reference.keys())
    if missing_pilot or missing_reference:
        raise SystemExit(
            f"item sets differ: missing from pilot={len(missing_pilot)}, "
            f"missing from reference={len(missing_reference)}"
        )

    rows = []
    for item_id in sorted(pilot):
        pilot_row = pilot[item_id]
        ref_prediction, ref_gold, ref_correct = reference[item_id]
        if pilot_row["gold"] != ref_gold:
            raise SystemExit(f"gold mismatch for {item_id}: {pilot_row['gold']} != {ref_gold}")
        rows.append(
            {
                "item_id": item_id,
                "gold": ref_gold,
                "pilot_prediction": pilot_row["prediction"],
                "reference_prediction": ref_prediction,
                "pilot_correct": bool(pilot_row["correct"]),
                "reference_correct": ref_correct,
                "prediction_agrees": pilot_row["prediction"] == ref_prediction,
                "pilot_b_disagreement": pilot_row["prediction"] == "B" and ref_prediction != "B",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    count = len(rows)
    pilot_accuracy = sum(row["pilot_correct"] for row in rows) / count
    reference_accuracy = sum(row["reference_correct"] for row in rows) / count
    agreement = sum(row["prediction_agrees"] for row in rows) / count
    b_disagreements = sum(row["pilot_b_disagreement"] for row in rows)
    print(f"items={count}")
    print(f"pilot_accuracy={pilot_accuracy:.4f}")
    print(f"reference_accuracy={reference_accuracy:.4f}")
    print(f"prediction_agreement={agreement:.4f}")
    print(f"pilot_B_reference_non_B={b_disagreements}")
    print(f"diff_csv={args.output}")


if __name__ == "__main__":
    main()
