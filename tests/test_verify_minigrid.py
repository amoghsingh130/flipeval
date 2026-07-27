import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts.verify_minigrid import (
    GATED_ACCEPTANCE_KEY,
    REQUIRED_ACCEPTANCE_KEYS,
    MissingAcceptanceKeys,
    verify_minigrid,
)


MODELS = [
    ("qwen25-1p5b", "fixture/qwen", "qwenrev", "qwen_run"),
    ("llama32-3b", "fixture/llama", "llamarev", "llama_run"),
]
SEEDS = range(5)
MMLU_REVISION = "mmlu-rev"
GSM8K_REVISION = "gsm8k-rev"


def _receipt(tag: str, model_id: str, revision: str, family: str, seed: int) -> dict:
    # Artifact identity is per (model, seed): calibration eligibility depends on
    # the tokenizer, so two models never share one.
    return {
        "artifact_sha256": hashlib.sha256(f"{tag}-{seed}".encode()).hexdigest(),
        "model_id": model_id,
        "model_revision": revision,
        "method": family,
        "bits": 4,
        "seed": seed,
        "sample_count": 2,
        "sequence_length": 4,
        "dataset": {"repo_id": "allenai/c4", "config": "en", "revision": "c4rev"},
        "tokenizer": {
            "model_id": model_id,
            "model_revision": revision,
            "class": "FixtureTokenizer",
            "vocab_sha256": hashlib.sha256(f"{tag}-vocab".encode()).hexdigest(),
        },
        "selected_document_indices": [seed * 2, seed * 2 + 1],
        "selected_token_hashes": [f"{tag}-{seed}-a", f"{tag}-{seed}-b"],
    }


def _write_fixture(tmp_path: Path):
    project = tmp_path / "project"
    results = project / "results"
    model_entries = []

    for tag, model_id, revision, run_name in MODELS:
        methods = []
        for family, backend in (("gptq", "gptqmodel_torch"), ("awq", "awq_gemm")):
            for seed in SEEDS:
                name = f"{family}_s{seed}"
                checkpoint = project / "outputs" / tag / name
                checkpoint.mkdir(parents=True)
                (checkpoint / "calibration_manifest.json").write_text(
                    json.dumps(_receipt(tag, model_id, revision, family, seed)), encoding="utf-8"
                )
                methods.append(
                    {
                        "name": name,
                        "model_id": str(checkpoint),
                        "seed": seed,
                        "quantization_backend": backend,
                    }
                )
        model_entries.append(
            {
                "tag": tag,
                "run_name": run_name,
                "baseline": {"name": "fp16", "model_id": model_id, "revision": revision},
                "methods": methods,
            }
        )

    config = {
        "schema_version": 1,
        "output_dir": str(results),
        "models": model_entries,
        "tasks": [
            {"name": "mmlu", "prompt_style": "chat", "dataset_revision": MMLU_REVISION},
            {"name": "gsm8k", "prompt_style": "chat", "dataset_revision": GSM8K_REVISION},
        ],
        "minigrid_acceptance": {
            "expected_jsonl_files": 44,
            "expected_item_counts": {"mmlu": 2, "gsm8k": 2},
            "task_dataset_revisions": {"mmlu": MMLU_REVISION, "gsm8k": GSM8K_REVISION},
            "baseline_accuracy_ranges": {
                "qwen25-1p5b": {"mmlu": [0.4, 0.6], "gsm8k": [0.4, 0.6]},
                "llama32-3b": {"mmlu": [0.4, 0.6], "gsm8k": [0.4, 0.6]},
            },
            "calibration": {
                "dataset": "allenai/c4",
                "dataset_config": "en",
                "dataset_revision": "c4rev",
                "sample_count": 2,
                "sequence_length": 4,
                "bits": 4,
                "paired_seeds": list(SEEDS),
            },
        },
    }
    config_path = project / "minigrid.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    for entry in model_entries:
        run_dir = results / entry["run_name"]
        run_dir.mkdir(parents=True)
        names = ["fp16"] + [m["name"] for m in entry["methods"]]
        (run_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "methods": [{"name": n} for n in names],
                    "tasks": [{"name": "mmlu"}, {"name": "gsm8k"}],
                    "runs": [{"methods": names, "tasks": ["mmlu", "gsm8k"]}],
                    "loaded": {
                        m["name"]: {
                            "quantization_backend": m["quantization_backend"],
                            "kernel": "FixtureLinear",
                        }
                        for m in entry["methods"]
                    },
                }
            ),
            encoding="utf-8",
        )
        for name in names:
            for task in ("mmlu", "gsm8k"):
                rows = [
                    {
                        "item_id": f"{task}:{index}",
                        "task": task,
                        "method": name,
                        "gold": str(index),
                        "prediction": str(index),
                        "correct": index == 0,
                        "prompt_hash": f"prompt-{task}-{index}",
                        "metadata": {"prompt_style": "chat"},
                    }
                    for index in range(2)
                ]
                (run_dir / f"{name}.{task}.jsonl").write_text(
                    "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
                )
    return project, config_path, results


def test_minigrid_validator_accepts_the_complete_expected_set(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    summary = verify_minigrid(config, results, project)
    assert summary["passed"], summary["errors"]
    assert summary["errors"] == []
    assert summary["expected_jsonl_files"] == 44
    assert summary["observed_jsonl_files"] == 44
    assert len(summary["file_sha256"]) == 44
    assert summary["baseline_accuracies"] == {
        "qwen25-1p5b": {"mmlu": 0.5, "gsm8k": 0.5},
        "llama32-3b": {"mmlu": 0.5, "gsm8k": 0.5},
    }


def test_minigrid_validator_rejects_a_missing_cell(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    (results / "llama_run" / "awq_s4.gsm8k.jsonl").unlink()
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert summary["observed_jsonl_files"] == 43
    assert "all 44 expected JSONLs are present" in summary["errors"]


def test_minigrid_validator_rejects_wrong_item_count(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    path = results / "qwen_run" / "gptq_s3.mmlu.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    path.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "qwen25-1p5b/gptq_s3.mmlu.jsonl has 2 records" in summary["errors"]


def test_minigrid_validator_rejects_prompt_drift_within_a_model(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    path = results / "llama_run" / "awq_s2.gsm8k.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["prompt_hash"] = "drifted"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "llama32-3b: awq_s2/gsm8k golds and prompts match baseline" in summary["errors"]


def test_minigrid_validator_rejects_unpaired_seed(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    path = project / "outputs" / "qwen25-1p5b" / "awq_s4" / "calibration_manifest.json"
    receipt = json.loads(path.read_text())
    receipt["artifact_sha256"] = hashlib.sha256(b"unpaired").hexdigest()
    path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "qwen25-1p5b: seed 4 GPTQ/AWQ calibration artifacts are identical" in summary["errors"]


def test_minigrid_validator_requires_all_five_seeds_paired(tmp_path):
    """A four-seed grid must not pass; the registered analysis needs five."""
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    for entry in raw["models"]:
        entry["methods"] = [m for m in entry["methods"] if not m["name"].endswith("_s4")]
    raw["minigrid_acceptance"]["expected_jsonl_files"] = 44
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "qwen25-1p5b: seed 4 has GPTQ and AWQ receipts" in summary["errors"]
    assert "config expands to the declared 44 JSONLs" in summary["errors"]


def test_minigrid_validator_rejects_a_shared_artifact_across_models(tmp_path):
    """Two models cannot legitimately share a C4 artifact: eligibility is
    tokenizer-dependent. Each model's receipts stay internally consistent here,
    so only the cross-model check can catch it."""
    project, config, results = _write_fixture(tmp_path)
    for family in ("gptq", "awq"):
        path = project / "outputs" / "llama32-3b" / f"{family}_s0" / "calibration_manifest.json"
        receipt = json.loads(path.read_text())
        borrowed = json.loads(
            (project / "outputs" / "qwen25-1p5b" / f"{family}_s0" / "calibration_manifest.json").read_text()
        )
        receipt["artifact_sha256"] = borrowed["artifact_sha256"]
        path.write_text(json.dumps(receipt), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "qwen25-1p5b and llama32-3b share no calibration artifact" in summary["errors"]


def test_minigrid_validator_fails_closed_without_derived_fp16_ranges(tmp_path):
    """The gate ranges are derived from the reference runs. Missing ranges must
    stop the grid, not silently skip the only baseline evidence there is."""
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    del raw["minigrid_acceptance"]["baseline_accuracy_ranges"]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("baseline_accuracy_ranges" in error for error in summary["errors"])


def test_minigrid_validator_rejects_fp16_outside_its_gate(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["minigrid_acceptance"]["baseline_accuracy_ranges"]["llama32-3b"]["mmlu"] = [0.9, 1.0]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("baseline mmlu accuracy 0.500000" in error for error in summary["errors"])


def test_minigrid_validator_rejects_a_recorded_backend_that_differs_from_config(tmp_path):
    """A manifest naming a route that did not run is the failure this catches."""
    project, config, results = _write_fixture(tmp_path)
    path = results / "qwen_run" / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["loaded"]["gptq_s1"]["quantization_backend"] = "awq_gemm"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert (
        "qwen25-1p5b/gptq_s1 recorded backend matches the declared 'gptqmodel_torch'"
        in summary["errors"]
    )


def test_minigrid_validator_rejects_unpinned_dataset_revision(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["tasks"][0].pop("dataset_revision")
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert f"task mmlu pins dataset revision {MMLU_REVISION}" in summary["errors"]


def test_minigrid_validator_rejects_raw_prompts(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    path = results / "qwen_run" / "fp16.mmlu.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        row["metadata"]["prompt_style"] = "raw"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert "qwen25-1p5b/fp16.mmlu.jsonl uses chat prompts" in summary["errors"]


def test_minigrid_validator_requires_an_acceptance_block(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    del raw["minigrid_acceptance"]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="minigrid_acceptance"):
        verify_minigrid(config, results, project)


# --------------------------------------------------------------------------
# Open implementation items must fail closed BY NAME.
#
# configs/main_grid_manifest.yaml records rtn_builder, wanda_builder,
# arc_challenge_loader and hellaswag_loader as not-implemented, and the
# WikiText-2 calibration path as blocked. The mini-grid must not be routable
# into any of them by a config edit. Ruling 6 of 2026-07-21.
# --------------------------------------------------------------------------

def _manifest_implementation_status():
    raw = yaml.safe_load(Path("configs/main_grid_manifest.yaml").read_text(encoding="utf-8"))
    return raw["implementation_status"]


def test_the_open_items_are_still_the_ones_these_tests_cover():
    """If an item is implemented or a new gap appears, this fails and forces the
    guard list below to be revisited rather than silently going stale."""
    status = _manifest_implementation_status()
    open_items = {k for k, v in status.items() if v.startswith(("not-implemented", "blocked"))}
    assert open_items == {
        "rtn_builder",
        "wanda_builder",
        "arc_challenge_loader",
        "hellaswag_loader",
        "real_wikitext2_artifact_preflight",
    }


def test_validator_scope_matches_the_implemented_surface():
    from scripts.verify_minigrid import IMPLEMENTED_METHOD_FAMILIES, IMPLEMENTED_TASKS

    status = _manifest_implementation_status()
    assert status["rtn_builder"].startswith("not-implemented")
    assert status["wanda_builder"].startswith("not-implemented")
    assert "rtn" not in IMPLEMENTED_METHOD_FAMILIES
    assert "wanda" not in IMPLEMENTED_METHOD_FAMILIES
    assert status["arc_challenge_loader"].startswith("not-implemented")
    assert status["hellaswag_loader"].startswith("not-implemented")
    assert "arc_challenge" not in IMPLEMENTED_TASKS
    assert "hellaswag" not in IMPLEMENTED_TASKS
    assert IMPLEMENTED_METHOD_FAMILIES == {"gptq", "awq"}
    assert IMPLEMENTED_TASKS == {"mmlu", "gsm8k"}


@pytest.mark.parametrize("family", ["rtn", "wanda"])
def test_minigrid_validator_rejects_an_unimplemented_method_family(tmp_path, family):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    entry = raw["models"][0]["methods"][0]
    entry["name"] = f"{family}_s0"
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any(f"{family}_s0" in e and "implemented" in e for e in summary["errors"])


@pytest.mark.parametrize("task", ["arc_challenge", "hellaswag"])
def test_minigrid_validator_rejects_an_unimplemented_task(tmp_path, task):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["tasks"].append({"name": task, "prompt_style": "chat"})
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any(task in e and "implemented loader" in e for e in summary["errors"])


def test_minigrid_validator_rejects_a_wikitext2_calibration_set(tmp_path):
    """The WikiText-2 document rule is decided but deliberately not implemented;
    the builder fails closed and so must the validator."""
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["minigrid_acceptance"]["calibration"]["dataset"] = "Salesforce/wikitext"
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("C4" in e for e in summary["errors"])


def test_minigrid_validator_rejects_three_bit(tmp_path):
    """3-bit dose-response is deferred with the rest of the main grid."""
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["minigrid_acceptance"]["calibration"]["bits"] = 3
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("4-bit" in e for e in summary["errors"])


def test_minigrid_validator_rejects_a_reduced_seed_set(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    raw["minigrid_acceptance"]["calibration"]["paired_seeds"] = [0, 1, 2]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("registered {0,1,2,3,4}" in e for e in summary["errors"])


# ---- grid identity: the config must be the grid the operator asked for ------
# Regression tests for the hazard found 2026-07-25: verify_minigrid.sbatch
# hardcoded the mini-grid config, so running it after the escalation eval would
# have validated the complete mini-grid and exited 0 -- a green validator
# certifying nothing about the grid it claimed to check. A wrong config is not a
# crash; it is a *valid* run of the wrong thing, which only an independent
# declaration of intent can catch.


def test_minigrid_validator_accepts_a_matching_grid_declaration(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    summary = verify_minigrid(
        config,
        results,
        project,
        expect_model_tags=["qwen25-1p5b", "llama32-3b"],
        expect_cells=44,
    )
    assert summary["passed"], summary["errors"]
    assert summary["declared_model_tags"] == ["qwen25-1p5b", "llama32-3b"]
    assert summary["expect_cells"] == 44


def test_minigrid_validator_rejects_a_config_for_a_different_grid(tmp_path):
    """The escalation-vs-mini-grid mixup, which is otherwise a silent PASS."""
    project, config, results = _write_fixture(tmp_path)
    summary = verify_minigrid(
        config,
        results,
        project,
        expect_model_tags=["qwen25-7b", "llama31-8b"],
        expect_cells=44,
    )
    assert not summary["passed"]
    assert any("expected model tags" in e for e in summary["errors"])


def test_minigrid_validator_rejects_a_cell_count_mismatch(tmp_path):
    project, config, results = _write_fixture(tmp_path)
    summary = verify_minigrid(
        config,
        results,
        project,
        expect_model_tags=["qwen25-1p5b", "llama32-3b"],
        expect_cells=88,
    )
    assert not summary["passed"]
    assert any("expected 88 cells" in e for e in summary["errors"])


def test_minigrid_validator_rejects_a_run_dir_holding_a_foreign_cell(tmp_path):
    """A JSONL the config does not declare means config and results disagree."""
    project, config, results = _write_fixture(tmp_path)
    (results / "qwen_run" / "rtn_s0.mmlu.jsonl").write_text("{}\n", encoding="utf-8")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("unaccounted=['rtn_s0.mmlu.jsonl']" in e for e in summary["errors"])


def test_minigrid_validator_rejects_a_missing_run_dir(tmp_path):
    import shutil

    project, config, results = _write_fixture(tmp_path)
    shutil.rmtree(results / "llama_run")
    summary = verify_minigrid(config, results, project)
    assert not summary["passed"]
    assert any("run dir 'llama_run' exists" in e for e in summary["errors"])


def test_minigrid_validator_cli_requires_the_grid_declaration():
    """The CLI must not let the operator omit the intent declaration."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/verify_minigrid.py", "--config", "x", "--results-root", "y"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert result.returncode != 0
    assert "--expect-model-tags" in result.stderr
    assert "--expect-cells" in result.stderr


# --------------------------------------------------------------------------
# The acceptance CONTRACT (incident 25, 2026-07-26).
#
# The escalation config omitted `calibration`, the one acceptance key the
# validator read with a subscript rather than `.get()`. The complete 44-cell
# grid was produced, archived and sealed before anything noticed, and the
# validator then died with a bare KeyError before a single check ran.
#
# The preceding reuse decision -- "the validator is model-agnostic, so no fork"
# -- was true and irrelevant: it checked which MODELS the validator walks, not
# which KEYS it demands. These tests check the contract, not the code path.
# --------------------------------------------------------------------------

def _grid_configs():
    """Every config that declares an acceptance block, found by inspection.

    Deliberately not a hardcoded pair: a third grid config is covered the day it
    is committed, which is exactly what a pairwise comparison between two named
    files stops doing the moment a third exists.
    """
    root = Path(__file__).resolve().parents[1] / "configs"
    found = {}
    for path in sorted(root.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("minigrid_acceptance"), dict):
            found[path.name] = raw["minigrid_acceptance"]
    return found


def test_every_grid_config_declares_the_required_acceptance_keys():
    """The incident-25 regression, stated over all grid configs at once."""
    configs = _grid_configs()
    assert configs, "no grid config declares minigrid_acceptance; the sweep found nothing"
    for name, acceptance in configs.items():
        missing = [k for k in REQUIRED_ACCEPTANCE_KEYS if acceptance.get(k) is None]
        assert not missing, f"{name} is missing required acceptance key(s): {missing}"
        # The gated key must be present OR explicitly declared pending -- never
        # simply absent, which is the state that reads as "nobody decided".
        gated = acceptance.get(GATED_ACCEPTANCE_KEY)
        status = str(acceptance.get(f"{GATED_ACCEPTANCE_KEY}_status", ""))
        assert gated is not None or status.startswith("pending"), (
            f"{name}: {GATED_ACCEPTANCE_KEY} is absent with no pending status"
        )


def test_grid_configs_declare_the_same_acceptance_contract():
    """Secondary, pairwise: the grid configs must not drift apart key-wise.

    Weaker than the required-set check above and kept behind it, because it goes
    vacuous with a single config and says nothing about whether the shared key
    set is the RIGHT one. It catches the narrower thing the required set cannot:
    a key one config declares and another silently drops.
    """
    configs = _grid_configs()
    # No pytest.skip: an in-image skip is a gate FAILURE in this project (it
    # means a pinned dependency did not import), so this degrades to a vacuous
    # pass rather than becoming a false alarm if a config is ever removed.
    key_sets = {name: set(acceptance) for name, acceptance in configs.items()}
    reference_name, reference = next(iter(key_sets.items()))
    for name, keys in key_sets.items():
        assert keys == reference, (
            f"{name} and {reference_name} declare different acceptance keys: "
            f"only in {name}={sorted(keys - reference)}, "
            f"only in {reference_name}={sorted(reference - keys)}"
        )


def test_validator_rejects_a_config_without_calibration(tmp_path):
    """Incident 25 exactly: the key whose absence killed job 11509869."""
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    del raw["minigrid_acceptance"]["calibration"]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(MissingAcceptanceKeys, match="calibration"):
        verify_minigrid(config, results, project)


def test_missing_acceptance_keys_are_reported_together(tmp_path):
    """Every missing key at once, not whichever a subscript reaches first.

    A validator that dies on the first missing key teaches the operator to add
    one, rerun, and discover the next -- which is how a contract gap becomes a
    sequence of failed jobs instead of one message.
    """
    project, config, results = _write_fixture(tmp_path)
    raw = yaml.safe_load(config.read_text())
    del raw["minigrid_acceptance"]["calibration"]
    del raw["minigrid_acceptance"]["task_dataset_revisions"]
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(MissingAcceptanceKeys) as excinfo:
        verify_minigrid(config, results, project)
    message = str(excinfo.value)
    assert "calibration" in message
    assert "task_dataset_revisions" in message
    assert "2 required key(s)" in message


# --------------------------------------------------------------------------
# The OUTPUT path is a grid declaration too (incident 26, 2026-07-26).
#
# `--output` defaulted to RESULTS_ROOT/minigrid_validation_summary.json -- one
# grid's name, under a results root both grids share -- so the escalation
# validator overwrote the mini-grid's completed summary while declaring its
# config, results root, model tags and cell count correctly. None of those
# controls governs where output lands. The standing rule ("no job script is ever
# given a default grid, reader or writer") had been applied to this pair's
# reader; it also writes.
# --------------------------------------------------------------------------

def test_validator_cli_requires_an_explicit_output_path():
    """Omitting --output must abort, not silently pick one grid's filename."""
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable, "scripts/verify_minigrid.py",
            "--config", "x", "--results-root", "y",
            "--expect-model-tags", "a", "--expect-cells", "1",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert result.returncode != 0
    assert "--output" in result.stderr


def test_the_validator_sbatch_declares_no_default_output_path():
    """Static guard, in the shape used for the runner's grid vars.

    A behavioural test cannot catch a default reintroduced next to a guard, so
    the source text is pinned too.
    """
    sbatch = (
        Path(__file__).resolve().parents[1] / "scripts" / "slurm" / "verify_minigrid.sbatch"
    ).read_text(encoding="utf-8")
    assert '"${MINIGRID_OUTPUT:?' in sbatch, "MINIGRID_OUTPUT must be required via ${VAR:?}"
    assert "${MINIGRID_OUTPUT:-" not in sbatch, "MINIGRID_OUTPUT must have no fallback"
    assert "--output" in sbatch, "the sbatch must pass MINIGRID_OUTPUT through"
    # The old default must not reappear anywhere in the writer path.
    source = (
        Path(__file__).resolve().parents[1] / "scripts" / "verify_minigrid.py"
    ).read_text(encoding="utf-8")
    assert 'results_root / "minigrid_validation_summary.json"' not in source
