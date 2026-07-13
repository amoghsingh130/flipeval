from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand and validate the frozen main-grid job matrix.")
    parser.add_argument("--config", default="configs/main_grid_manifest.yaml")
    parser.add_argument("--output", default="docs/EXPECTED_MAIN_GRID.json")
    args = parser.parse_args()
    matrix = expand_grid(Path(args.config))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(matrix, stream, indent=2)
        stream.write("\n")
    print(json.dumps(matrix["counts"], indent=2))
    print(f"Wrote {output}")


def expand_grid(path: Path) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    models = config["models"]
    tasks = [task["name"] for task in config["tasks"]]
    seeds = [int(seed) for seed in config["calibration"]["seeds"]]
    variants: list[dict[str, Any]] = []

    for model in models:
        variants.append(_variant(model, "fp16", None, None, None, tasks))
        for bit in config["methods"]["rtn"]["bits"]:
            variants.append(_variant(model, "rtn", int(bit), None, None, tasks))
        variants.extend(_calibrated_variants(model, "c4", config, seeds, tasks))

    wikitext_models = set(config["calibration_datasets"]["wikitext2"]["models"])
    for model in models:
        if model["tag"] in wikitext_models:
            variants.extend(_calibrated_variants(model, "wikitext2", config, seeds, tasks))

    identifiers = [variant["variant_id"] for variant in variants]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("expanded main-grid variant IDs are not unique")
    actual = {
        "baseline_checkpoints": sum(variant["method"] == "fp16" for variant in variants),
        "compressed_checkpoints_c4": sum(
            variant["method"] != "fp16" and variant["calibration_dataset"] in (None, "c4")
            for variant in variants
        ),
        "compressed_checkpoints_wikitext2": sum(
            variant["calibration_dataset"] == "wikitext2" for variant in variants
        ),
        "total_model_variants": len(variants),
        "evaluation_jsonl_files": sum(len(variant["expected_outputs"]) for variant in variants),
    }
    expected = {key: int(value) for key, value in config["expected_counts"].items()}
    if actual != expected:
        raise ValueError(f"expanded grid counts differ from frozen counts: actual={actual}, expected={expected}")
    return {
        "schema_version": 1,
        "source_config": str(path),
        "counts": actual,
        "variants": variants,
    }


def _calibrated_variants(model, dataset, config, seeds, tasks):
    variants = []
    for method in ("gptq", "awq"):
        for bit in config["methods"][method]["bits"]:
            for seed in seeds:
                variants.append(_variant(model, method, int(bit), seed, dataset, tasks))
    for seed in seeds:
        variants.append(_variant(model, "wanda", None, seed, dataset, tasks, sparsity="2:4"))
    return variants


def _variant(model, method, bit, seed, calibration_dataset, tasks, sparsity=None):
    parts = [model["tag"], method]
    if bit is not None:
        parts.append(f"{bit}bit")
    if sparsity is not None:
        parts.append("2to4")
    if calibration_dataset is not None:
        parts.append(calibration_dataset)
    if seed is not None:
        parts.append(f"s{seed}")
    variant_id = "-".join(parts)
    return {
        "variant_id": variant_id,
        "model_tag": model["tag"],
        "model_id": model["model_id"],
        "model_revision": model["revision"],
        "method": method,
        "bits": bit,
        "sparsity": sparsity,
        "calibration_dataset": calibration_dataset,
        "seed": seed,
        "expected_outputs": [f"{variant_id}.{task}.jsonl" for task in tasks],
    }


if __name__ == "__main__":
    main()
