import hashlib
import json
from pathlib import Path

import yaml

from scripts.verify_bridge import verify_bridge


def _write_fixture(tmp_path: Path):
    project = tmp_path / "project"
    run_dir = project / "results" / "bridge"
    run_dir.mkdir(parents=True)
    methods = []
    for family in ("gptq", "awq"):
        for seed in range(3):
            name = f"{family}_s{seed}"
            checkpoint = project / "outputs" / name
            checkpoint.mkdir(parents=True)
            receipt = {
                "artifact_sha256": hashlib.sha256(f"artifact-{seed}".encode()).hexdigest(),
                "model_id": "fixture/model",
                "model_revision": "model123",
                "method": family,
                "bits": 4,
                "seed": seed,
                "sample_count": 2,
                "sequence_length": 4,
                "dataset": {"repo_id": "fixture/c4", "config": "en", "revision": "data123"},
                "tokenizer": {
                    "model_id": "fixture/model",
                    "model_revision": "model123",
                    "class": "FixtureTokenizer",
                    "vocab_sha256": hashlib.sha256(b"fixture-vocab").hexdigest(),
                },
                "selected_document_indices": [seed * 2, seed * 2 + 1],
                "selected_token_hashes": [f"{seed}-a", f"{seed}-b"],
            }
            (checkpoint / "calibration_manifest.json").write_text(json.dumps(receipt), encoding="utf-8")
            methods.append({"name": name, "model_id": str(checkpoint), "seed": seed})
    config = {
        "run_name": "bridge",
        "output_dir": str(project / "results"),
        "baseline": {"name": "fp16", "model_id": "fixture/model", "revision": "model123"},
        "methods": methods,
        "tasks": [{"name": "mmlu"}, {"name": "gsm8k"}],
        "bridge_acceptance": {
            "expected_item_counts": {"mmlu": 2, "gsm8k": 2},
            "baseline_accuracy_ranges": {"mmlu": [0.5, 0.5], "gsm8k": [0.5, 0.5]},
            "calibration": {
                "dataset": "fixture/c4",
                "dataset_config": "en",
                "dataset_revision": "data123",
                "sample_count": 2,
                "sequence_length": 4,
                "bits": 4,
                "paired_seeds": [0, 1, 2],
            },
        },
    }
    config_path = project / "bridge.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    method_names = ["fp16"] + [method["name"] for method in methods]
    manifest = {
        "methods": [{"name": name} for name in method_names],
        "tasks": [{"name": "mmlu"}, {"name": "gsm8k"}],
        "runs": [{"methods": method_names, "tasks": ["mmlu", "gsm8k"]}],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    for method in method_names:
        for task in ("mmlu", "gsm8k"):
            rows = [
                {
                    "item_id": f"{task}:{index}",
                    "task": task,
                    "method": method,
                    "gold": str(index),
                    "prediction": str(index),
                    "correct": index == 0,
                    "prompt_hash": f"prompt-{task}-{index}",
                    "metadata": {"prompt_style": "chat"},
                }
                for index in range(2)
            ]
            (run_dir / f"{method}.{task}.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
    return project, config_path, run_dir


def test_bridge_validator_accepts_complete_paired_run(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    summary = verify_bridge(config, run_dir, project)
    assert summary["passed"]
    assert summary["errors"] == []
    assert summary["baseline_accuracies"] == {"mmlu": 0.5, "gsm8k": 0.5}
    assert len(summary["file_sha256"]) == 14


def test_bridge_validator_rejects_unpaired_calibration_receipt(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    path = project / "outputs" / "awq_s1" / "calibration_manifest.json"
    receipt = json.loads(path.read_text())
    receipt["artifact_sha256"] = hashlib.sha256(b"different").hexdigest()
    path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "seed 1 GPTQ/AWQ calibration artifacts are identical" in summary["errors"]


def test_bridge_validator_rejects_checkpoint_from_wrong_model_revision(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    for name in ("gptq_s0", "awq_s0"):
        path = project / "outputs" / name / "calibration_manifest.json"
        receipt = json.loads(path.read_text())
        receipt["model_revision"] = "other456"
        path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "gptq_s0 calibration receipt provenance matches bridge config" in summary["errors"]
    assert "awq_s0 calibration receipt provenance matches bridge config" in summary["errors"]


def test_bridge_validator_rejects_wrong_bit_width(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    for name in ("gptq_s2", "awq_s2"):
        path = project / "outputs" / name / "calibration_manifest.json"
        receipt = json.loads(path.read_text())
        receipt["bits"] = 3
        path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "gptq_s2 calibration receipt provenance matches bridge config" in summary["errors"]


def test_bridge_validator_rejects_malformed_artifact_hash(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    for name in ("gptq_s1", "awq_s1"):
        path = project / "outputs" / name / "calibration_manifest.json"
        receipt = json.loads(path.read_text())
        receipt["artifact_sha256"] = "not-a-real-hash"
        path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "gptq_s1 calibration receipt provenance matches bridge config" in summary["errors"]


def test_bridge_validator_rejects_tokenizer_drift_across_pair(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    path = project / "outputs" / "awq_s0" / "calibration_manifest.json"
    receipt = json.loads(path.read_text())
    receipt["tokenizer"]["vocab_sha256"] = hashlib.sha256(b"other-vocab").hexdigest()
    path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "seed 0 GPTQ/AWQ calibration artifacts are identical" in summary["errors"]


def test_bridge_validator_rejects_prompt_or_gold_drift(tmp_path):
    project, config, run_dir = _write_fixture(tmp_path)
    path = run_dir / "awq_s2.mmlu.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["gold"] = "changed"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    summary = verify_bridge(config, run_dir, project)
    assert not summary["passed"]
    assert "awq_s2/mmlu golds and prompts match baseline" in summary["errors"]
