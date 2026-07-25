"""The escalation config's all-or-nothing FP16 gate state.

Pairs with tests/test_minigrid_config.py::
test_fp16_ranges_are_either_derived_or_explicitly_pending -- the same guard,
bound to configs/pace_escalation_h3.yaml. The escalation gates are committed
all-or-nothing (docs/ESCALATION_FP16_GATE_DERIVATION_2026-07-24.md section 5):
either all four ranges (qwen25-7b x {mmlu, gsm8k}, llama31-8b x {mmlu, gsm8k})
are present and well-formed, or all four are absent with an explicit pending
status. A half-filled block -- e.g. Qwen's held pair committed while Llama's
reference is still deferred -- is the dangerous middle state this rejects, both
in the config's declared shape and in the validator that reads it.
"""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from pilot_eval.config import read_raw
from scripts.verify_minigrid import verify_minigrid


CONFIG = Path("configs/pace_escalation_h3.yaml")
MODELS = ("qwen25-7b", "llama31-8b")
TASKS = ("mmlu", "gsm8k")
# Plausibility bounds fixed in the escalation derivation doc section 6 branch 1,
# BEFORE any escalation reference ran -- wider than the mini-grid script's
# (0.25-0.75 / 0.10-0.90) because 7B/8B models legitimately score higher.
PLAUSIBLE = {"mmlu": (0.25, 0.85), "gsm8k": (0.10, 0.95)}


def _ranges_all_or_nothing_ok(acceptance) -> bool:
    """The rule as a pure predicate, so partial states can be tested directly.

    True iff the acceptance block is in one of the two permitted states:
      * baseline_accuracy_ranges absent AND an explicit pending status, or
      * all four ranges present, numeric, low < high in [0, 1], with the gate
        midpoint (the reference accuracy p) inside the pre-committed plausible
        band for its task.
    Any partial, malformed, or implausible state is False.
    """
    ranges = acceptance.get("baseline_accuracy_ranges")
    if ranges is None:
        status = str(acceptance.get("baseline_accuracy_ranges_status", ""))
        return status.startswith("pending")
    if set(ranges) != set(MODELS):
        return False
    for tag in MODELS:
        per_task = ranges[tag]
        if set(per_task) != set(TASKS):
            return False
        for task, bound in per_task.items():
            if not (isinstance(bound, (list, tuple)) and len(bound) == 2):
                return False
            low, high = bound
            if isinstance(low, bool) or isinstance(high, bool):
                return False
            if not all(isinstance(x, (int, float)) for x in (low, high)):
                return False
            if not (0.0 <= low < high <= 1.0):
                return False
            midpoint = (low + high) / 2
            lo_ok, hi_ok = PLAUSIBLE[task]
            if not (lo_ok <= midpoint <= hi_ok):
                return False
    return True


def _full_ranges() -> dict:
    """Four well-formed ranges. Qwen's are the real held pair
    (docs/ESCALATION_FP16_GATE_DERIVATION_2026-07-24.md); Llama's are
    placeholders here -- this fixture tests the SHAPE rule, not the values."""
    return {
        "qwen25-7b": {"mmlu": [0.600263, 0.700263], "gsm8k": [0.691, 0.807]},
        "llama31-8b": {"mmlu": [0.45, 0.55], "gsm8k": [0.60, 0.72]},
    }


# --------------------------------------------------------------------------
# The real config's declared state
# --------------------------------------------------------------------------

def test_escalation_fp16_ranges_are_either_derived_or_explicitly_pending():
    """Bound to configs/pace_escalation_h3.yaml; pairs with the mini-grid guard.

    The config takes exactly one of the two permitted branches. It held the
    pending branch until 2026-07-25; step 5 then landed all four ranges in one
    commit and it takes the derived branch. A half-filled commit takes neither
    (see the rejection tests below)."""
    acceptance = read_raw(CONFIG)["minigrid_acceptance"]
    assert _ranges_all_or_nothing_ok(acceptance)
    # concretely, it is now the filled state: four ranges, no pending status
    assert acceptance.get("baseline_accuracy_ranges_status") is None
    assert acceptance["baseline_accuracy_ranges"] == {
        "qwen25-7b": {"mmlu": [0.600263, 0.700263], "gsm8k": [0.691, 0.807]},
        "llama31-8b": {"mmlu": [0.492444, 0.592444], "gsm8k": [0.729, 0.841]},
    }


def test_escalation_fp16_ranges_match_the_derivation_arithmetic():
    """The committed gates must be exactly what section 3 produces from the
    recorded reference (p, n) -- not merely well-formed numbers.

    Recomputes half = ceil3(max(0.05, 2*SE + 0.03)) and gate = p +/- half from
    the reference accuracies and item counts, so a hand-edited bound, a
    transcription slip, or a silently changed tolerance fails here rather than
    passing as 'plausible'."""
    import math

    # (p, n) as recorded by the reference runs, derivation job 11478290.
    REFERENCE = {
        "qwen25-7b": {"mmlu": (0.6502634952285999, 14042), "gsm8k": (0.749, 1000)},
        "llama31-8b": {"mmlu": (0.5424440962825808, 14042), "gsm8k": (0.785, 1000)},
    }
    ranges = read_raw(CONFIG)["minigrid_acceptance"]["baseline_accuracy_ranges"]
    for tag, per_task in REFERENCE.items():
        for task, (p, n) in per_task.items():
            se = math.sqrt(p * (1 - p) / n)
            half = math.ceil(max(0.05, 2 * se + 0.03) * 1000 - 1e-9) / 1000
            expected = [round(max(0.0, p - half), 6), round(min(1.0, p + half), 6)]
            assert ranges[tag][task] == expected, f"{tag}/{task}"


# --------------------------------------------------------------------------
# The rule accepts exactly the two permitted states...
# --------------------------------------------------------------------------

def test_escalation_gate_accepts_the_two_permitted_states():
    assert _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": _full_ranges()})
    assert _ranges_all_or_nothing_ok(
        {"baseline_accuracy_ranges_status": "pending-reference-runs"}
    )


# --------------------------------------------------------------------------
# ...and rejects every partial / malformed / implausible one.
# --------------------------------------------------------------------------

def test_escalation_gate_rejects_a_half_filled_state():
    """The state this guard exists for. Two of four filled would sail through a
    naive 'is baseline_accuracy_ranges present and non-empty?' check -- it must
    fail here so Qwen's held pair cannot be committed while Llama's is deferred."""
    two_of_four = {"qwen25-7b": _full_ranges()["qwen25-7b"]}  # llama31-8b absent
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": two_of_four})

    three_of_four = _full_ranges()
    del three_of_four["llama31-8b"]["gsm8k"]  # one task missing on the second model
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": three_of_four})


def test_escalation_gate_rejects_absent_ranges_without_a_pending_status():
    """Absent ranges are only acceptable when the config SAYS it is pending."""
    assert not _ranges_all_or_nothing_ok({})
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges_status": "derived"})


def test_escalation_gate_rejects_malformed_or_implausible_bounds():
    bad_order = _full_ranges()
    bad_order["qwen25-7b"]["mmlu"] = [0.70, 0.60]  # low >= high
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": bad_order})

    non_numeric = _full_ranges()
    non_numeric["qwen25-7b"]["mmlu"] = ["lo", "hi"]
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": non_numeric})

    implausible = _full_ranges()
    implausible["qwen25-7b"]["mmlu"] = [0.90, 0.98]  # midpoint 0.94 > 0.85 ceiling
    assert not _ranges_all_or_nothing_ok({"baseline_accuracy_ranges": implausible})


# --------------------------------------------------------------------------
# Companion: the validator that reads this config fails closed on pending.
# --------------------------------------------------------------------------

def _receipt(tag, model_id, revision, family, seed) -> dict:
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


def _write_escalation_fixture(root: Path, ranges):
    """A complete, otherwise-valid escalation grid. With `ranges` present it
    passes verify_minigrid; with `ranges=None` (pending) it must fail closed --
    same fixture, so pending is provably the sole cause. Escalation tags, so the
    companion is bound to this grid, not the mini-grid's."""
    models_meta = [
        ("qwen25-7b", "fixture/qwen7b", "qwen7brev", "qwen25_7b_escalation_h3"),
        ("llama31-8b", "fixture/llama8b", "llama8brev", "llama31_8b_escalation_h3"),
    ]
    seeds = range(5)
    project = root / "project"
    results = project / "results"
    model_entries = []
    for tag, model_id, revision, run_name in models_meta:
        methods = []
        for family, backend in (("gptq", "gptqmodel_torch"), ("awq", "awq_gemm")):
            for seed in seeds:
                name = f"{family}_s{seed}"
                checkpoint = project / "outputs" / tag / name
                checkpoint.mkdir(parents=True)
                (checkpoint / "calibration_manifest.json").write_text(
                    json.dumps(_receipt(tag, model_id, revision, family, seed)),
                    encoding="utf-8",
                )
                methods.append(
                    {"name": name, "model_id": str(checkpoint), "seed": seed,
                     "quantization_backend": backend}
                )
        model_entries.append(
            {"tag": tag, "run_name": run_name,
             "baseline": {"name": "fp16", "model_id": model_id, "revision": revision},
             "methods": methods}
        )

    acceptance = {
        "expected_jsonl_files": 44,
        "expected_item_counts": {"mmlu": 2, "gsm8k": 2},
        "task_dataset_revisions": {"mmlu": "mmlu-rev", "gsm8k": "gsm8k-rev"},
        "calibration": {
            "dataset": "allenai/c4", "dataset_config": "en", "dataset_revision": "c4rev",
            "sample_count": 2, "sequence_length": 4, "bits": 4,
            "paired_seeds": list(seeds),
        },
    }
    if ranges is None:
        acceptance["baseline_accuracy_ranges_status"] = "pending-reference-runs"
    else:
        acceptance["baseline_accuracy_ranges"] = ranges

    config = {
        "schema_version": 1,
        "output_dir": str(results),
        "models": model_entries,
        "tasks": [
            {"name": "mmlu", "prompt_style": "chat", "dataset_revision": "mmlu-rev"},
            {"name": "gsm8k", "prompt_style": "chat", "dataset_revision": "gsm8k-rev"},
        ],
        "minigrid_acceptance": acceptance,
    }
    config_path = project / "escalation.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    for entry in model_entries:
        run_dir = results / entry["run_name"]
        run_dir.mkdir(parents=True)
        names = ["fp16"] + [m["name"] for m in entry["methods"]]
        (run_dir / "manifest.json").write_text(
            json.dumps({
                "methods": [{"name": n} for n in names],
                "tasks": [{"name": "mmlu"}, {"name": "gsm8k"}],
                "runs": [{"methods": names, "tasks": ["mmlu", "gsm8k"]}],
                "loaded": {
                    m["name"]: {"quantization_backend": m["quantization_backend"],
                                "kernel": "FixtureLinear"}
                    for m in entry["methods"]
                },
            }),
            encoding="utf-8",
        )
        for name in names:
            for task in ("mmlu", "gsm8k"):
                rows = [
                    {"item_id": f"{task}:{index}", "task": task, "method": name,
                     "gold": str(index), "prediction": str(index), "correct": index == 0,
                     "prompt_hash": f"prompt-{task}-{index}",
                     "metadata": {"prompt_style": "chat"}}
                    for index in range(2)
                ]
                (run_dir / f"{name}.{task}.jsonl").write_text(
                    "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
                )
    return project, config_path, results


def test_escalation_validator_fails_closed_on_the_pending_state(tmp_path):
    """A config that declares pending must not be able to produce a passing
    validation run. Proven by isolation: the same complete fixture passes with
    the four ranges present, and fails with them replaced by a pending status."""
    fixture_ranges = {tag: {"mmlu": [0.4, 0.6], "gsm8k": [0.4, 0.6]} for tag in MODELS}
    project, config, results = _write_escalation_fixture(tmp_path / "filled", fixture_ranges)
    filled = verify_minigrid(config, results, project)
    assert filled["passed"], filled["errors"]  # the fixture is otherwise complete

    project, config, results = _write_escalation_fixture(tmp_path / "pending", None)
    pending = verify_minigrid(config, results, project)
    assert not pending["passed"]
    assert any("baseline_accuracy_ranges" in error for error in pending["errors"])
