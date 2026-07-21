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
    # Hub revision of the benchmark dataset. Optional so existing single-model
    # configs are unaffected, but when set it is enforced at load time and the
    # loader's alternate-repo fallback is disabled -- a fallback repo carries a
    # different revision, so substituting it would silently break the pin.
    dataset_revision: str | None = None


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
    dataset_revision = raw.get("dataset_revision")
    return TaskConfig(
        name=str(raw["name"]),
        split=str(raw.get("split", "test")),
        limit=raw.get("limit"),
        subjects=[str(s) for s in subjects] if subjects else None,
        fewshot=int(raw.get("fewshot", 0)),
        max_new_tokens=int(raw.get("max_new_tokens", 256)),
        prompt_style=prompt_style,
        fewshot_style=fewshot_style,
        dataset_revision=str(dataset_revision) if dataset_revision else None,
    )


def model_tags(raw: dict[str, Any]) -> list[str]:
    """Tags declared by a multi-model config, in declaration order.

    Empty for a single-model config, which is how callers tell the two shapes
    apart without reaching into the raw mapping themselves.
    """
    return [str(entry["tag"]) for entry in raw.get("models", [])]


def read_raw(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(path: str | Path, model_tag: str | None = None) -> RunConfig:
    """Build a run config, selecting one model from a multi-model grid config.

    Two shapes are supported. A single-model config declares `baseline`/`methods`
    at the top level (every pilot and bridge config). A grid config declares a
    `models:` list, each entry carrying its own `tag`, `run_name`, `baseline` and
    `methods`, with `tasks` shared at the top level.

    Tasks are deliberately NOT per-model: the mini-grid's registered parity
    requirement is that every variant of a model sees the identical item set,
    and sharing one task list makes divergence unrepresentable rather than
    merely checked after the fact.

    Selection is required, never defaulted: a grid config with `model_tag=None`
    raises. Silently picking the first model would let a typo in a job script
    evaluate the wrong model into a correctly-named run directory.
    """
    path = Path(path)
    raw = read_raw(path)
    tags = model_tags(raw)

    if tags:
        if model_tag is None:
            raise ValueError(
                f"{path} is a multi-model grid config; pass model_tag "
                f"(available: {', '.join(tags)})"
            )
        if model_tag not in tags:
            raise ValueError(
                f"unknown model tag {model_tag!r} in {path} "
                f"(available: {', '.join(tags)})"
            )
        entry = next(m for m in raw["models"] if str(m["tag"]) == model_tag)
        run_name = str(entry.get("run_name", f"{path.stem}_{model_tag}"))
        baseline_raw = entry["baseline"]
        methods_raw = entry.get("methods", [])
    else:
        if model_tag is not None:
            raise ValueError(f"{path} is a single-model config; model_tag is not accepted")
        run_name = str(raw.get("run_name", path.stem))
        baseline_raw = raw["baseline"]
        methods_raw = raw.get("methods", [])

    return RunConfig(
        run_name=run_name,
        output_dir=Path(raw.get("output_dir", "results")),
        baseline=_method(baseline_raw),
        methods=[_method(m) for m in methods_raw],
        tasks=[_task(t) for t in raw.get("tasks", [])],
        batch_size=int(raw.get("batch_size", 1)),
        device_map=str(raw.get("device_map", "auto")),
    )
