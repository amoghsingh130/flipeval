from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class MethodConfig:
    name: str
    model_id: str
    dtype: str = "float16"
    seed: int | None = None
    revision: str | None = None
    trust_remote_code: bool = True
    quantization_backend: str | None = None


@dataclass(frozen=True)
class TaskConfig:
    name: str
    split: str = "test"
    limit: int | None = None
    subjects: list[str] | None = None
    fewshot: int = 0
    max_new_tokens: int = 256
    prompt_style: str = "raw"
    fewshot_style: str = "inline"


@dataclass(frozen=True)
class RunConfig:
    run_name: str
    output_dir: Path
    baseline: MethodConfig
    methods: list[MethodConfig]
    tasks: list[TaskConfig]
    batch_size: int = 1
    device_map: str = "auto"


def _method(raw: dict[str, Any]) -> MethodConfig:
    return MethodConfig(
        name=str(raw["name"]),
        model_id=str(raw["model_id"]),
        dtype=str(raw.get("dtype", "float16")),
        seed=raw.get("seed"),
        revision=raw.get("revision"),
        trust_remote_code=bool(raw.get("trust_remote_code", True)),
        quantization_backend=raw.get("quantization_backend"),
    )


def _task(raw: dict[str, Any]) -> TaskConfig:
    subjects = raw.get("subjects")
    prompt_style = str(raw.get("prompt_style", "raw"))
    if prompt_style not in {"raw", "chat"}:
        raise ValueError(f"prompt_style must be 'raw' or 'chat', got {prompt_style!r}")
    fewshot_style = str(raw.get("fewshot_style", "inline"))
    if fewshot_style != "inline":
        raise ValueError("only fewshot_style='inline' is currently supported")
    return TaskConfig(
        name=str(raw["name"]),
        split=str(raw.get("split", "test")),
        limit=raw.get("limit"),
        subjects=[str(s) for s in subjects] if subjects else None,
        fewshot=int(raw.get("fewshot", 0)),
        max_new_tokens=int(raw.get("max_new_tokens", 256)),
        prompt_style=prompt_style,
        fewshot_style=fewshot_style,
    )


def load_config(path: str | Path) -> RunConfig:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return RunConfig(
        run_name=str(raw.get("run_name", path.stem)),
        output_dir=Path(raw.get("output_dir", "results")),
        baseline=_method(raw["baseline"]),
        methods=[_method(m) for m in raw.get("methods", [])],
        tasks=[_task(t) for t in raw.get("tasks", [])],
        batch_size=int(raw.get("batch_size", 1)),
        device_map=str(raw.get("device_map", "auto")),
    )
