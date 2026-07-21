"""The mini-grid config and the schema changes that carry it.

These tests pin the config's registered shape -- 22 variants, 44 files, the
pinned identities from configs/main_grid_manifest.yaml -- so a later edit that
quietly drops a seed, unpins a dataset, or lets a framework choose a kernel
fails here rather than in a 44-job fan-out.
"""
from pathlib import Path

import pytest
import yaml

from pilot_eval.config import QUANTIZATION_BACKENDS, load_config, model_tags, read_raw
from pilot_eval.tasks import load_gsm8k


CONFIG = Path("configs/pace_minigrid_h3.yaml")
MANIFEST = Path("configs/main_grid_manifest.yaml")


def _manifest_models():
    raw = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return {m["tag"]: m for m in raw["models"]}


def _manifest_tasks():
    raw = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return {t["name"]: t for t in raw["tasks"]}


# --------------------------------------------------------------------------
# Multi-model config schema
# --------------------------------------------------------------------------

def test_grid_config_requires_an_explicit_model_tag():
    """Never default. A typo'd tag must not evaluate the wrong weights into a
    correctly-named run directory."""
    with pytest.raises(ValueError, match="multi-model grid config"):
        load_config(CONFIG)


def test_grid_config_rejects_an_unknown_model_tag():
    with pytest.raises(ValueError, match="unknown model tag"):
        load_config(CONFIG, "qwen25-7b")


def test_single_model_config_rejects_a_model_tag(tmp_path):
    path = tmp_path / "single.yaml"
    path.write_text("baseline: {name: fp16, model_id: m}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="single-model config"):
        load_config(path, "anything")


def test_single_model_configs_still_load_unchanged():
    run = load_config(Path("configs/pace_bridge_chat.yaml"))
    assert run.run_name == "qwen25_1p5b_bridge_chat"
    assert len(run.methods) == 6


# --------------------------------------------------------------------------
# Mini-grid scope: 2 models x 11 variants x 2 tasks = 44
# --------------------------------------------------------------------------

def test_minigrid_declares_exactly_the_two_registered_small_model_cells():
    assert model_tags(read_raw(CONFIG)) == ["qwen25-1p5b", "llama32-3b"]


@pytest.mark.parametrize("tag", ["qwen25-1p5b", "llama32-3b"])
def test_each_model_has_eleven_variants_over_five_paired_seeds(tag):
    run = load_config(CONFIG, tag)
    assert run.baseline.name == "fp16"
    names = [m.name for m in run.methods]
    assert names == [f"gptq_s{s}" for s in range(5)] + [f"awq_s{s}" for s in range(5)]
    assert len({m.seed for m in run.methods}) == 5


def test_minigrid_expands_to_forty_four_jsonls():
    raw = read_raw(CONFIG)
    variants = sum(1 + len(m.get("methods", [])) for m in raw["models"])
    assert variants == 22
    assert variants * len(raw["tasks"]) == 44
    assert raw["minigrid_acceptance"]["expected_jsonl_files"] == 44


@pytest.mark.parametrize("tag", ["qwen25-1p5b", "llama32-3b"])
def test_every_quantized_variant_names_an_explicit_backend(tag):
    """No variant may rely on framework kernel auto-selection -- the campaign's
    known hazard class (missing optimum, absent Marlin runtime, SIGILL)."""
    run = load_config(CONFIG, tag)
    assert run.baseline.quantization_backend is None
    assert [m.quantization_backend for m in run.methods] == (
        ["gptqmodel_torch"] * 5 + ["awq_gemm"] * 5
    )
    assert all(m.quantization_backend in QUANTIZATION_BACKENDS for m in run.methods)


# --------------------------------------------------------------------------
# Pinned identities must match the frozen manifest
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tag", ["qwen25-1p5b", "llama32-3b"])
def test_baselines_pin_the_frozen_model_revisions(tag):
    run = load_config(CONFIG, tag)
    expected = _manifest_models()[tag]
    assert run.baseline.model_id == expected["model_id"]
    assert run.baseline.revision == expected["revision"]


def test_tasks_pin_the_frozen_dataset_revisions():
    run = load_config(CONFIG, "qwen25-1p5b")
    tasks = {t.name: t for t in run.tasks}
    manifest = _manifest_tasks()
    assert tasks["mmlu"].dataset_revision == manifest["mmlu"]["revision"]
    assert tasks["gsm8k"].dataset_revision == manifest["gsm8k"]["revision"]


def test_mmlu_is_the_full_test_split_across_all_57_subjects():
    """`limit` applies per subject in the loader, so 'full' means limit is None.
    14,042 is the sum of the 57 test splits at the pinned revision, verified
    in-image against that revision (job 11338439)."""
    task = {t.name: t for t in load_config(CONFIG, "qwen25-1p5b").tasks}["mmlu"]
    assert task.split == "test"
    assert task.limit is None
    assert task.subjects is not None
    assert len(task.subjects) == 57
    assert len(set(task.subjects)) == 57
    raw = read_raw(CONFIG)
    assert raw["minigrid_acceptance"]["expected_item_counts"]["mmlu"] == 14042


def test_gsm8k_is_indices_0_through_999():
    task = {t.name: t for t in load_config(CONFIG, "qwen25-1p5b").tasks}["gsm8k"]
    assert task.split == "test"
    assert task.limit == 1000
    assert read_raw(CONFIG)["minigrid_acceptance"]["expected_item_counts"]["gsm8k"] == 1000


def test_both_tasks_use_chat_prompts():
    """Chat template is ON for every method including FP16 baselines."""
    assert all(t.prompt_style == "chat" for t in load_config(CONFIG, "llama32-3b").tasks)


def test_gsm8k_prompt_is_byte_identical_to_the_validated_bridge(tmp_path, monkeypatch):
    """Amendment 2 (2026-07-21): the mini-grid is bound to the bridge's prompt,
    which is the fixed THREE-example block. `fewshot` is a boolean switch, so
    the config's value of 1 must still emit all three."""
    import json

    source = tmp_path / "gsm8k.jsonl"
    source.write_text(
        json.dumps({"question": "What is 2 + 3?", "answer": "Work. #### 5"}), encoding="utf-8"
    )
    monkeypatch.setenv("GSM8K_JSONL", str(source))

    bridge = {t["name"]: t for t in read_raw(Path("configs/pace_bridge_chat.yaml"))["tasks"]}
    minigrid = {t["name"]: t for t in read_raw(CONFIG)["tasks"]}
    assert minigrid["gsm8k"]["fewshot"] == bridge["gsm8k"]["fewshot"]
    assert minigrid["gsm8k"]["fewshot_style"] == bridge["gsm8k"]["fewshot_style"] == "inline"
    assert minigrid["gsm8k"]["max_new_tokens"] == bridge["gsm8k"]["max_new_tokens"]

    prompt = load_gsm8k(split="test", limit=1, fewshot=minigrid["gsm8k"]["fewshot"])[0].prompt
    assert prompt.count("Question:") == 4  # three exemplars plus the item itself


# --------------------------------------------------------------------------
# The FP16 gate ranges are derived, and their absence must fail closed
# --------------------------------------------------------------------------

def test_fp16_ranges_are_either_derived_or_explicitly_pending():
    """Guards against a hand-written range appearing without a reference run.

    Either the ranges are absent and the config says so (validator fails
    closed), or they cover both models and both tasks. A half-filled block is
    the dangerous middle state this rejects.
    """
    acceptance = read_raw(CONFIG)["minigrid_acceptance"]
    ranges = acceptance.get("baseline_accuracy_ranges")
    if ranges is None:
        assert acceptance.get("baseline_accuracy_ranges_status", "").startswith("pending")
        return
    assert set(ranges) == {"qwen25-1p5b", "llama32-3b"}
    for per_task in ranges.values():
        assert set(per_task) == {"mmlu", "gsm8k"}
        for low, high in per_task.values():
            assert 0.0 <= low < high <= 1.0


# --------------------------------------------------------------------------
# Dataset revision pinning is enforced, not merely declared
# --------------------------------------------------------------------------

def test_pinned_mmlu_load_does_not_fall_back_to_another_repository(monkeypatch):
    """A fallback repo carries a different revision, so substituting it would
    satisfy the load while breaking the pin."""
    import pilot_eval.tasks as tasks_module

    seen = []

    class _FakeDatasets:
        @staticmethod
        def load_dataset(name, config, split=None, revision=None):
            seen.append((name, config, split, revision))
            if name == "cais/mmlu":
                raise RuntimeError("hub unavailable")
            return [{"question": "q", "choices": ["a", "b", "c", "d"], "answer": 0}]

    monkeypatch.setitem(__import__("sys").modules, "datasets", _FakeDatasets)
    with pytest.raises(RuntimeError, match="hub unavailable"):
        tasks_module.load_mmlu(
            split="test", limit=1, subjects=["anatomy"], dataset_revision="pinned-rev"
        )
    assert seen == [("cais/mmlu", "anatomy", "test", "pinned-rev")]


def test_unpinned_mmlu_load_keeps_its_fallback(monkeypatch):
    import pilot_eval.tasks as tasks_module

    seen = []

    class _FakeDatasets:
        @staticmethod
        def load_dataset(name, config, split=None, revision=None):
            seen.append(name)
            if name == "cais/mmlu":
                raise RuntimeError("hub unavailable")
            return [{"question": "q", "choices": ["a", "b", "c", "d"], "answer": 0}]

    monkeypatch.setitem(__import__("sys").modules, "datasets", _FakeDatasets)
    items = tasks_module.load_mmlu(split="test", limit=1, subjects=["anatomy"])
    assert [name for name in seen] == ["cais/mmlu", "lukaemon/mmlu"]
    assert len(items) == 1


def test_local_gsm8k_file_cannot_claim_to_satisfy_a_pin(tmp_path, monkeypatch):
    """A run that believes it is pinned while reading an unverifiable local file
    is worse than one that stops."""
    import json

    source = tmp_path / "gsm8k.jsonl"
    source.write_text(
        json.dumps({"question": "What is 2 + 3?", "answer": "Work. #### 5"}), encoding="utf-8"
    )
    monkeypatch.setenv("GSM8K_JSONL", str(source))
    with pytest.raises(ValueError, match="carries no Hub revision"):
        load_gsm8k(split="test", limit=1, fewshot=1, dataset_revision="pinned-rev")
