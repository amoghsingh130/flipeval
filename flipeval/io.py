from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Filename patterns lm-evaluation-harness v0.4.x writes under --output_path
#: when --log_samples is given: one file per task, named
#: samples_<task>_<ISO timestamp>.jsonl, inside a per-model subdirectory.
_SAMPLE_GLOBS = ("samples_*.jsonl", "samples_*.json")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSONL file of FlipEval records.

    Parse errors name the file and the line, because the common failure here is
    one malformed row in a long file and a bare JSONDecodeError does not say
    which one.
    """
    resolved = Path(path)
    if resolved.is_dir():
        raise IsADirectoryError(
            f"{resolved} is a directory. read_jsonl takes a single .jsonl file; "
            "for a lm-evaluation-harness output directory use from_lm_eval_harness()."
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"no such records file: {resolved}")
    records: list[dict[str, Any]] = []
    with resolved.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            records.append(_load_line(line, resolved, number))
    if not records:
        raise ValueError(f"{resolved} contains no records")
    return records


def from_lm_eval_harness(path: str | Path) -> list[dict[str, Any]]:
    """Convert lm-evaluation-harness v0.4.x sample logs to FlipEval records.

    ``path`` may be either a single ``--log_samples`` file (a full result JSON
    with a ``samples`` mapping, or a sample JSON/JSONL), or the ``--output_path``
    directory the harness wrote. A directory is searched recursively for
    ``samples_<task>_<timestamp>.jsonl`` files and all of them are concatenated,
    which is what a practitioner actually has after running the harness: one
    file per task, one level below the path they passed.
    """
    resolved = Path(path)
    if resolved.is_dir():
        return _from_directory(resolved)
    if not resolved.is_file():
        raise FileNotFoundError(f"no such lm-evaluation-harness log: {resolved}")
    raw = _read_json_or_jsonl(resolved)
    samples = raw.get("samples", raw) if isinstance(raw, dict) else raw
    if isinstance(samples, dict):
        samples = [
            {"task_name": task_name, **sample}
            for task_name, task_samples in samples.items()
            for sample in task_samples
        ]
    if not isinstance(samples, list):
        raise ValueError(
            f"{resolved}: harness log must contain a list of samples or a 'samples' "
            f"mapping; found a {type(samples).__name__}. Point this at a file written "
            "by lm_eval --log_samples, not at a results summary."
        )
    if not samples:
        raise ValueError(f"{resolved} contains no samples")
    return [_convert_sample(sample, index) for index, sample in enumerate(samples)]


def _from_directory(directory: Path) -> list[dict[str, Any]]:
    """Load every per-task sample log under an lm-eval output directory."""
    files = sorted(
        {path for pattern in _SAMPLE_GLOBS for path in directory.rglob(pattern)}
    )
    if not files:
        raise FileNotFoundError(
            f"no lm-evaluation-harness sample logs under {directory}. Expected one or "
            "more samples_<task>_<timestamp>.jsonl files, which lm_eval writes only "
            "when --log_samples is passed alongside --output_path. Point this at the "
            "--output_path directory, or at a single sample file."
        )
    by_task: dict[str, list[Path]] = {}
    for file in files:
        by_task.setdefault(_task_of(file), []).append(file)
    repeated = {task: paths for task, paths in by_task.items() if len(paths) > 1}
    if repeated:
        detail = "; ".join(
            f"{task}: {', '.join(path.name for path in paths)}"
            for task, paths in sorted(repeated.items())
        )
        raise ValueError(
            f"{directory} holds more than one sample log for the same task ({detail}). "
            "That is two runs of one task, and concatenating them would pair items "
            "against the wrong run. Keep one run per directory, or pass the single "
            "file you mean."
        )
    records: list[dict[str, Any]] = []
    seen: dict[str, Path] = {}
    for file in files:
        for record in from_lm_eval_harness(file):
            item_id = str(record["item_id"])
            if item_id in seen:
                raise ValueError(
                    f"duplicate item_id {item_id!r} across {seen[item_id].name} and "
                    f"{file.name} in {directory}. item_id is 'task_name:doc_id', so "
                    "this means two files cover the same task."
                )
            seen[item_id] = file
            records.append(record)
    return records


def _task_of(path: Path) -> str:
    """Task name embedded in a samples_<task>_<timestamp>.jsonl filename."""
    stem = path.stem
    if stem.startswith("samples_"):
        stem = stem[len("samples_") :]
    head, _, _tail = stem.rpartition("_")
    return head or stem


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


def _load_line(line: str, path: Path, number: int) -> dict[str, Any]:
    try:
        return json.loads(line)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path}: line {number} is not valid JSON: {error.msg}") from error


def _read_json_or_jsonl(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [
            _load_line(line, path, number)
            for number, line in enumerate(text.splitlines(), start=1)
            if line.strip()
        ]
