from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

# Imported both ways: as `scripts.verify_bridge` (tests, repo root on sys.path)
# and as a bare script (`python /workspace/scripts/verify_bridge.py`, the SLURM
# invocation, where sys.path[0] is scripts/ and the package name is empty).
try:
    from scripts.verify_common import (
        SHA256_HEX,
        check as _check,
        file_sha256 as _file_sha256,
        load_json_object as _load_json_object,
        load_jsonl as _load_jsonl,
    )
except ImportError:  # pragma: no cover - exercised by the SLURM script path
    from verify_common import (  # type: ignore[no-redef]
        SHA256_HEX,
        check as _check,
        file_sha256 as _file_sha256,
        load_json_object as _load_json_object,
        load_jsonl as _load_jsonl,
    )


PAIR_NAME = re.compile(r"^(gptq|awq)_s(\d+)$")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed validation for the pre-PACE bridge run.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", help="Defaults to RUN_DIR/bridge_validation_summary.json")
    args = parser.parse_args()

    output = Path(args.output) if args.output else Path(args.run_dir) / "bridge_validation_summary.json"
    summary = verify_bridge(Path(args.config), Path(args.run_dir), Path(args.project_root).resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {output}")
    if not summary["passed"]:
        raise SystemExit(1)


def verify_bridge(config_path: Path, run_dir: Path, project_root: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    acceptance = config.get("bridge_acceptance")
    if not isinstance(acceptance, dict):
        raise ValueError("bridge config must declare bridge_acceptance before execution")

    baseline = str(config["baseline"]["name"])
    baseline_model_id = str(config["baseline"]["model_id"])
    baseline_revision = config["baseline"].get("revision")
    methods = [baseline] + [str(method["name"]) for method in config.get("methods", [])]
    tasks = [str(task["name"]) for task in config.get("tasks", [])]
    expected_counts = {str(key): int(value) for key, value in acceptance["expected_item_counts"].items()}
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    manifest_path = run_dir / "manifest.json"
    manifest = _load_json_object(manifest_path, errors)
    if manifest is not None:
        manifest_methods = {str(entry.get("name")) for entry in manifest.get("methods", [])}
        manifest_tasks = {str(entry.get("name")) for entry in manifest.get("tasks", [])}
        _check(set(methods) == manifest_methods, "manifest method coverage", errors, checks)
        _check(set(tasks) == manifest_tasks, "manifest task coverage", errors, checks)
        _check(bool(manifest.get("runs")), "manifest has invocation history", errors, checks)

    records: dict[tuple[str, str], list[dict[str, Any]]] = {}
    file_checksums: dict[str, str] = {}
    for method in methods:
        for task in tasks:
            path = run_dir / f"{method}.{task}.jsonl"
            rows = _load_jsonl(path, errors)
            if rows is None:
                continue
            records[(method, task)] = rows
            file_checksums[path.name] = _file_sha256(path)
            expected = expected_counts[task]
            _check(len(rows) == expected, f"{path.name} has {expected} records", errors, checks)
            ids = [str(row.get("item_id")) for row in rows]
            _check(len(ids) == len(set(ids)), f"{path.name} item IDs are unique", errors, checks)
            _check(
                all(row.get("method") == method and row.get("task") == task for row in rows),
                f"{path.name} record labels match filename",
                errors,
                checks,
            )
            _check(
                all((row.get("metadata") or {}).get("prompt_style") == "chat" for row in rows),
                f"{path.name} uses chat prompts",
                errors,
                checks,
            )

    baseline_accuracies: dict[str, float] = {}
    for task in tasks:
        base_rows = records.get((baseline, task))
        if base_rows is None:
            continue
        accuracy = sum(bool(row.get("correct")) for row in base_rows) / len(base_rows)
        baseline_accuracies[task] = accuracy
        low, high = acceptance["baseline_accuracy_ranges"][task]
        _check(
            float(low) <= accuracy <= float(high),
            f"baseline {task} accuracy {accuracy:.6f} is within [{low}, {high}]",
            errors,
            checks,
        )
        baseline_map = {str(row["item_id"]): row for row in base_rows}
        for method in methods:
            candidate = records.get((method, task))
            if candidate is None:
                continue
            candidate_map = {str(row["item_id"]): row for row in candidate}
            _check(
                set(candidate_map) == set(baseline_map),
                f"{method}/{task} item set matches baseline",
                errors,
                checks,
            )
            if set(candidate_map) == set(baseline_map):
                fields_match = all(
                    candidate_map[item_id].get("gold") == baseline_map[item_id].get("gold")
                    and candidate_map[item_id].get("prompt_hash") == baseline_map[item_id].get("prompt_hash")
                    for item_id in baseline_map
                )
                _check(fields_match, f"{method}/{task} golds and prompts match baseline", errors, checks)

    calibration = acceptance["calibration"]
    expected_bits = int(calibration["bits"])
    _check(bool(baseline_revision), "baseline declares a pinned model revision", errors, checks)
    receipts: dict[tuple[str, int], dict[str, Any]] = {}
    method_configs = {str(method["name"]): method for method in config.get("methods", [])}
    for name, method in method_configs.items():
        match = PAIR_NAME.match(name)
        if not match:
            errors.append(f"compressed bridge method has unrecognized paired name: {name}")
            continue
        family, seed_text = match.groups()
        seed = int(seed_text)
        checkpoint = Path(str(method["model_id"]))
        if not checkpoint.is_absolute():
            checkpoint = project_root / checkpoint
        receipt_path = checkpoint / "calibration_manifest.json"
        receipt = _load_json_object(receipt_path, errors)
        if receipt is None:
            continue
        receipts[(family, seed)] = receipt
        valid = (
            int(receipt.get("seed", -1)) == seed
            and int(receipt.get("sample_count", -1)) == int(calibration["sample_count"])
            and int(receipt.get("sequence_length", -1)) == int(calibration["sequence_length"])
            and receipt.get("dataset", {}).get("repo_id") == calibration["dataset"]
            and receipt.get("dataset", {}).get("config") == calibration["dataset_config"]
            and receipt.get("dataset", {}).get("revision") == calibration["dataset_revision"]
            and len(receipt.get("selected_document_indices", [])) == int(calibration["sample_count"])
            and len(receipt.get("selected_token_hashes", [])) == int(calibration["sample_count"])
        )
        _check(valid, f"{name} calibration receipt matches frozen protocol", errors, checks)
        tokenizer_receipt = receipt.get("tokenizer") or {}
        provenance = (
            receipt.get("model_id") == baseline_model_id
            and receipt.get("model_revision") == baseline_revision
            and receipt.get("method") == family
            and receipt.get("bits") == expected_bits
            and tokenizer_receipt.get("model_id") == baseline_model_id
            and tokenizer_receipt.get("model_revision") == baseline_revision
            and bool(tokenizer_receipt.get("vocab_sha256"))
            and SHA256_HEX.fullmatch(str(receipt.get("artifact_sha256") or "")) is not None
        )
        _check(provenance, f"{name} calibration receipt provenance matches bridge config", errors, checks)

    for raw_seed in calibration["paired_seeds"]:
        seed = int(raw_seed)
        gptq = receipts.get(("gptq", seed))
        awq = receipts.get(("awq", seed))
        _check(gptq is not None and awq is not None, f"seed {seed} has GPTQ and AWQ receipts", errors, checks)
        if gptq is not None and awq is not None:
            paired = all(
                gptq.get(key) == awq.get(key)
                for key in ("artifact_sha256", "selected_document_indices", "selected_token_hashes", "tokenizer")
            )
            _check(paired, f"seed {seed} GPTQ/AWQ calibration artifacts are identical", errors, checks)

    return {
        "schema_version": 1,
        "passed": not errors,
        "decision_record_written": False,
        "config": str(config_path.resolve()),
        "run_dir": str(run_dir.resolve()),
        "expected_methods": methods,
        "expected_tasks": tasks,
        "baseline_accuracies": baseline_accuracies,
        "checks": checks,
        "errors": errors,
        "file_sha256": file_checksums,
        "interpretation": "Operational bridge validation only; not an H3 analysis.",
    }


if __name__ == "__main__":
    main()
