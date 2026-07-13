from pathlib import Path

from scripts.expected_grid import expand_grid


def test_frozen_main_grid_expands_to_expected_unique_jobs():
    matrix = expand_grid(Path("configs/main_grid_manifest.yaml"))
    assert matrix["counts"] == {
        "baseline_checkpoints": 4,
        "compressed_checkpoints_c4": 108,
        "compressed_checkpoints_wikitext2": 25,
        "total_model_variants": 137,
        "evaluation_jsonl_files": 548,
    }
    identifiers = [variant["variant_id"] for variant in matrix["variants"]]
    assert len(identifiers) == len(set(identifiers)) == 137
    assert any(identifier == "qwen25-1p5b-gptq-4bit-c4-s0" for identifier in identifiers)
    assert any(identifier == "qwen25-1p5b-wanda-2to4-wikitext2-s4" for identifier in identifiers)
