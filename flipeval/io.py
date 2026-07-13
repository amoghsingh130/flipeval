from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def from_lm_eval_harness(path: str | Path) -> list[dict[str, Any]]:
    """Convert lm-evaluation-harness v0.4.x sample logs to FlipEval records."""
    raw = _read_json_or_jsonl(Path(path))
    samples = raw.get("samples", raw) if isinstance(raw, dict) else raw
    if isinstance(samples, dict):
        samples = [
            {"task_name": task_name, **sample}
            for task_name, task_samples in samples.items()
            for sample in task_samples
        ]
    if not isinstance(samples, list):
        raise ValueError("harness log must contain a list or a 'samples' mapping")
    return [_convert_sample(sample, index) for index, sample in enumerate(samples)]


def _convert_sample(sample: dict[str, Any], index: int) -> dict[str, Any]:
    doc = sample.get("doc", {})
    item_id = sample.get("doc_id", sample.get("id", index))
    task = str(sample.get("task_name", sample.get("task", "unknown")))
    filtered = sample.get("filtered_resps", sample.get("filtered_response"))
    prediction: Any
    if _looks_like_choice_loglikelihood(sample):
        responses = sample.get("resps", sample.get("responses"))
        values = [_loglikelihood_value(value) for value in responses]
        prediction_index = max(range(len(values)), key=values.__getitem__)
        choices = doc.get("choices") or sample.get("choices")
        prediction = choices[prediction_index] if choices else prediction_index
        gold = sample.get("target", doc.get("answer", doc.get("gold")))
        if isinstance(gold, int) and choices:
            gold = choices[gold]
    else:
        prediction = _first_scalar(filtered)
        if prediction is None:
            prediction = _first_scalar(sample.get("resps", sample.get("responses", "")))
        gold = sample.get("target", doc.get("answer", doc.get("gold", doc.get("target", ""))))
    correct = sample.get("exact_match", sample.get("acc"))
    if correct is None:
        metrics = sample.get("metrics", {})
        correct = metrics.get("exact_match", metrics.get("acc"))
    if correct is None:
        correct = str(prediction).strip() == str(gold).strip()
    return {
        "item_id": f"{task}:{item_id}",
        "task": task,
        "prediction": str(prediction),
        "gold": str(gold),
        "correct": bool(correct),
        "metadata": {"source": "lm-evaluation-harness", "doc_id": item_id},
    }


def _looks_like_choice_loglikelihood(sample: dict[str, Any]) -> bool:
    output_type = str(sample.get("output_type", ""))
    responses = sample.get("resps", sample.get("responses"))
    return output_type in {"loglikelihood", "multiple_choice"} or (
        isinstance(responses, list) and len(responses) > 1 and all(isinstance(value, (list, tuple)) for value in responses)
    )


def _loglikelihood_value(value: Any) -> float:
    while isinstance(value, (list, tuple)) and value:
        value = value[0]
    return float(value)


def _first_scalar(value: Any) -> Any:
    while isinstance(value, (list, tuple)):
        if not value:
            return None
        value = value[0]
    return value


def _read_json_or_jsonl(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
