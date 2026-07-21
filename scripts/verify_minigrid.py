"""Fail-closed validation for the H3 mini-grid.

The bridge validator's counterpart at grid scale, per
`docs/PACE_EXECUTION_PLAN_2026-07-15.md` Stage 6. It enforces, over the complete
expected set and nothing less:

  * 44 expected JSONLs -- 2 models x 11 variants x 2 tasks -- all present;
  * exact item counts: MMLU 14,042, GSM8K 1,000;
  * identical item / gold / prompt-hash sets across every variant WITHIN a model;
  * chat prompt metadata on every record;
  * the pinned benchmark dataset revisions, as declared and as recorded;
  * FP16 operational gates, per model and per task;
  * calibration receipt pairing for 5 seeds x 2 models x {GPTQ, AWQ};
  * the recorded quantization backend and kernel for every quantized variant.

INSPECTION DISCIPLINE. This validator is the only thing that may look at
mini-grid output before the grid is complete, and it reports job health, not
findings. The one class of accuracy it computes is the FP16 baseline rate, which
is a registered operational gate. Quantized accuracies are never computed here,
never emitted, and never gated -- see
`docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md` section 3.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.verify_common import (
        SHA256_HEX,
        check,
        file_sha256,
        load_json_object,
        load_jsonl,
    )
except ImportError:  # pragma: no cover - exercised by the SLURM script path
    from verify_common import (  # type: ignore[no-redef]
        SHA256_HEX,
        check,
        file_sha256,
        load_json_object,
        load_jsonl,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed validation for the H3 mini-grid.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--results-root", required=True, help="Directory holding each model's run dir.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", help="Defaults to RESULTS_ROOT/minigrid_validation_summary.json")
    args = parser.parse_args()

    results_root = Path(args.results_root)
    output = Path(args.output) if args.output else results_root / "minigrid_validation_summary.json"
    summary = verify_minigrid(Path(args.config), results_root, Path(args.project_root).resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {output}")
    if not summary["passed"]:
        raise SystemExit(1)


def verify_minigrid(config_path: Path, results_root: Path, project_root: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    acceptance = config.get("minigrid_acceptance")
    if not isinstance(acceptance, dict):
        raise ValueError("mini-grid config must declare minigrid_acceptance before execution")

    models = config.get("models") or []
    if not models:
        raise ValueError("mini-grid config must declare a models list")

    tasks = [str(task["name"]) for task in config.get("tasks", [])]
    task_by_name = {str(task["name"]): task for task in config.get("tasks", [])}
    expected_counts = {str(k): int(v) for k, v in acceptance["expected_item_counts"].items()}
    calibration = acceptance["calibration"]
    paired_seeds = [int(seed) for seed in calibration["paired_seeds"]]

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    file_checksums: dict[str, str] = {}
    baseline_accuracies: dict[str, dict[str, float]] = {}
    per_model_artifacts: dict[str, set[str]] = {}

    # The gate ranges are derived from the trusted reference runs and committed
    # before any quantized result exists. Their absence is a hard stop, not a
    # skipped check: a mini-grid validated without FP16 gates has no baseline
    # evidence that the eval path was intact.
    ranges = acceptance.get("baseline_accuracy_ranges")
    check(
        isinstance(ranges, dict) and bool(ranges),
        "config declares FP16 baseline_accuracy_ranges "
        "(see docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md)",
        errors,
        checks,
    )
    ranges = ranges if isinstance(ranges, dict) else {}

    expected_files = 0
    for model in models:
        tag = str(model["tag"])
        run_name = str(model["run_name"])
        run_dir = results_root / run_name
        baseline_name = str(model["baseline"]["name"])
        baseline_model_id = str(model["baseline"]["model_id"])
        baseline_revision = model["baseline"].get("revision")
        method_configs = {str(m["name"]): m for m in model.get("methods", [])}
        methods = [baseline_name] + list(method_configs)
        expected_files += len(methods) * len(tasks)

        check(bool(baseline_revision), f"{tag}: baseline declares a pinned model revision", errors, checks)

        manifest = load_json_object(run_dir / "manifest.json", errors)
        loaded: dict[str, Any] = {}
        if manifest is not None:
            loaded = manifest.get("loaded") or {}
            check(
                {str(e.get("name")) for e in manifest.get("methods", [])} == set(methods),
                f"{tag}: manifest method coverage",
                errors,
                checks,
            )
            check(
                {str(e.get("name")) for e in manifest.get("tasks", [])} == set(tasks),
                f"{tag}: manifest task coverage",
                errors,
                checks,
            )
            check(bool(manifest.get("runs")), f"{tag}: manifest has invocation history", errors, checks)

        # ---- per-file structure -------------------------------------------
        records: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for method in methods:
            for task in tasks:
                path = run_dir / f"{method}.{task}.jsonl"
                rows = load_jsonl(path, errors)
                if rows is None:
                    continue
                records[(method, task)] = rows
                file_checksums[f"{run_name}/{path.name}"] = file_sha256(path)
                check(
                    len(rows) == expected_counts[task],
                    f"{tag}/{path.name} has {expected_counts[task]} records",
                    errors,
                    checks,
                )
                ids = [str(row.get("item_id")) for row in rows]
                check(len(ids) == len(set(ids)), f"{tag}/{path.name} item IDs are unique", errors, checks)
                check(
                    all(row.get("method") == method and row.get("task") == task for row in rows),
                    f"{tag}/{path.name} record labels match filename",
                    errors,
                    checks,
                )
                check(
                    all((row.get("metadata") or {}).get("prompt_style") == "chat" for row in rows),
                    f"{tag}/{path.name} uses chat prompts",
                    errors,
                    checks,
                )

        # ---- backend and kernel, as actually recorded ----------------------
        for name, method in method_configs.items():
            declared = method.get("quantization_backend")
            info = loaded.get(name) or {}
            check(
                bool(declared),
                f"{tag}/{name} declares an explicit quantization_backend",
                errors,
                checks,
            )
            check(
                info.get("quantization_backend") == declared,
                f"{tag}/{name} recorded backend matches the declared {declared!r}",
                errors,
                checks,
            )
            check(
                bool(info.get("kernel")),
                f"{tag}/{name} records the kernel it actually loaded",
                errors,
                checks,
            )

        # ---- item / gold / prompt parity, within this model ----------------
        for task in tasks:
            base_rows = records.get((baseline_name, task))
            if base_rows is None:
                continue
            accuracy = sum(bool(row.get("correct")) for row in base_rows) / len(base_rows)
            baseline_accuracies.setdefault(tag, {})[task] = accuracy
            bounds = (ranges.get(tag) or {}).get(task)
            if bounds is None:
                check(False, f"{tag}: FP16 {task} gate range is declared", errors, checks)
            else:
                low, high = float(bounds[0]), float(bounds[1])
                check(
                    low <= accuracy <= high,
                    f"{tag}: baseline {task} accuracy {accuracy:.6f} is within [{low}, {high}]",
                    errors,
                    checks,
                )

            baseline_map = {str(row["item_id"]): row for row in base_rows}
            for method in methods:
                candidate = records.get((method, task))
                if candidate is None:
                    continue
                candidate_map = {str(row["item_id"]): row for row in candidate}
                same_items = set(candidate_map) == set(baseline_map)
                check(same_items, f"{tag}: {method}/{task} item set matches baseline", errors, checks)
                if same_items:
                    check(
                        all(
                            candidate_map[i].get("gold") == baseline_map[i].get("gold")
                            and candidate_map[i].get("prompt_hash") == baseline_map[i].get("prompt_hash")
                            for i in baseline_map
                        ),
                        f"{tag}: {method}/{task} golds and prompts match baseline",
                        errors,
                        checks,
                    )

        # ---- calibration receipts and seed pairing -------------------------
        receipts: dict[tuple[str, int], dict[str, Any]] = {}
        for name, method in method_configs.items():
            family, _, seed_text = name.partition("_s")
            if family not in {"gptq", "awq"} or not seed_text.isdigit():
                errors.append(f"{tag}: compressed method has unrecognized paired name: {name}")
                continue
            seed = int(seed_text)
            checkpoint = Path(str(method["model_id"]))
            if not checkpoint.is_absolute():
                checkpoint = project_root / checkpoint
            receipt = load_json_object(checkpoint / "calibration_manifest.json", errors)
            if receipt is None:
                continue
            receipts[(family, seed)] = receipt
            per_model_artifacts.setdefault(tag, set()).add(str(receipt.get("artifact_sha256")))

            protocol = (
                int(receipt.get("seed", -1)) == seed
                and int(receipt.get("sample_count", -1)) == int(calibration["sample_count"])
                and int(receipt.get("sequence_length", -1)) == int(calibration["sequence_length"])
                and receipt.get("dataset", {}).get("repo_id") == calibration["dataset"]
                and receipt.get("dataset", {}).get("config") == calibration["dataset_config"]
                and receipt.get("dataset", {}).get("revision") == calibration["dataset_revision"]
                and len(receipt.get("selected_document_indices", [])) == int(calibration["sample_count"])
                and len(receipt.get("selected_token_hashes", [])) == int(calibration["sample_count"])
            )
            check(protocol, f"{tag}/{name} calibration receipt matches frozen protocol", errors, checks)

            tokenizer_receipt = receipt.get("tokenizer") or {}
            provenance = (
                receipt.get("model_id") == baseline_model_id
                and receipt.get("model_revision") == baseline_revision
                and receipt.get("method") == family
                and receipt.get("bits") == int(calibration["bits"])
                and tokenizer_receipt.get("model_id") == baseline_model_id
                and tokenizer_receipt.get("model_revision") == baseline_revision
                and bool(tokenizer_receipt.get("vocab_sha256"))
                and SHA256_HEX.fullmatch(str(receipt.get("artifact_sha256") or "")) is not None
            )
            check(provenance, f"{tag}/{name} calibration receipt provenance matches config", errors, checks)

        for seed in paired_seeds:
            gptq = receipts.get(("gptq", seed))
            awq = receipts.get(("awq", seed))
            check(
                gptq is not None and awq is not None,
                f"{tag}: seed {seed} has GPTQ and AWQ receipts",
                errors,
                checks,
            )
            if gptq is not None and awq is not None:
                check(
                    all(
                        gptq.get(key) == awq.get(key)
                        for key in (
                            "artifact_sha256",
                            "selected_document_indices",
                            "selected_token_hashes",
                            "tokenizer",
                        )
                    ),
                    f"{tag}: seed {seed} GPTQ/AWQ calibration artifacts are identical",
                    errors,
                    checks,
                )

    # ---- declared benchmark revisions match the frozen manifest -------------
    for task_name, revision in (acceptance.get("task_dataset_revisions") or {}).items():
        declared = (task_by_name.get(str(task_name)) or {}).get("dataset_revision")
        check(
            declared == revision,
            f"task {task_name} pins dataset revision {revision}",
            errors,
            checks,
        )

    # ---- cross-model independence -----------------------------------------
    # Calibration eligibility is a function of the tokenizer, so two models can
    # never legitimately share a C4 artifact. An overlap means a build read the
    # wrong model's artifact -- which the per-model checks above cannot see,
    # because each is internally consistent.
    tags = list(per_model_artifacts)
    for i, left in enumerate(tags):
        for right in tags[i + 1 :]:
            check(
                not (per_model_artifacts[left] & per_model_artifacts[right]),
                f"{left} and {right} share no calibration artifact",
                errors,
                checks,
            )

    check(
        len(file_checksums) == expected_files,
        f"all {expected_files} expected JSONLs are present",
        errors,
        checks,
    )
    declared_total = acceptance.get("expected_jsonl_files")
    if declared_total is not None:
        check(
            expected_files == int(declared_total),
            f"config expands to the declared {declared_total} JSONLs",
            errors,
            checks,
        )

    return {
        "schema_version": 1,
        "passed": not errors,
        "decision_record_written": False,
        "config": str(config_path.resolve()),
        "results_root": str(results_root.resolve()),
        "expected_jsonl_files": expected_files,
        "observed_jsonl_files": len(file_checksums),
        "expected_tasks": tasks,
        "baseline_accuracies": baseline_accuracies,
        "checks": checks,
        "errors": errors,
        "file_sha256": file_checksums,
        "interpretation": (
            "Operational mini-grid validation only. FP16 baseline rates are "
            "registered gates; no quantized accuracy is computed or gated here, "
            "and this is not an H3 analysis."
        ),
    }


if __name__ == "__main__":
    main()
