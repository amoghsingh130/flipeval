from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


# Quantized load routes, each named for the loader and kernel that actually run.
# The value is what the run manifest records, so it must never be an alias for
# something else. See docs/PACE_ENVIRONMENT_NOTE.md, cell-3 backend probe.
QUANTIZATION_BACKENDS = ("gptqmodel_torch", "awq_gemm")

# Values that were valid before the cell-3 probe. These fail loudly and are
# never remapped: silently rewriting a backend would let a manifest claim a
# route that did not run, which is worse than a crash.
RETIRED_QUANTIZATION_BACKENDS = {
    "gptq_torch": (
        "quantization_backend 'gptq_torch' loaded via transformers.GPTQConfig, "
        "which cannot work in the cell-3 image: transformers raises "
        "'Loading a GPTQ quantized model requires optimum' and optimum is not in "
        "the frozen environment (backend probe 11285139, 2026-07-19). "
        "Use 'gptqmodel_torch', which loads via GPTQModel.load(BACKEND.TORCH) and "
        "runs the same TorchLinear kernel. This is deliberately NOT remapped for "
        "you: the recorded backend must name the route that actually executed."
    ),
}


def validate_quantization_backend(value: Any) -> str | None:
    """Return a known backend name, or raise with a pointer to the replacement."""
    if value is None:
        return None
    name = str(value)
    if name in RETIRED_QUANTIZATION_BACKENDS:
        raise ValueError(RETIRED_QUANTIZATION_BACKENDS[name])
    if name not in QUANTIZATION_BACKENDS:
        raise ValueError(
            f"unknown quantization backend: {name!r} "
            f"(known: {', '.join(QUANTIZATION_BACKENDS)})"
        )
    return name


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
        quantization_backend=validate_quantization_backend(raw.get("quantization_backend")),
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
