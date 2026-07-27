"""Fail-closed validation for the H3 mini-grid.

The bridge validator's counterpart at grid scale, per
`docs/PACE_EXECUTION_PLAN_2026-07-15.md` Stage 6. It enforces, over the complete
expected set and nothing less:

  * the acceptance block is structurally complete -- every key in
    REQUIRED_ACCEPTANCE_KEYS is present, checked up front and reported all at
    once, so a config cannot be validated against a contract it only partly
    supplies;
  * the config is the grid the operator asked for -- model tags and cell count
    are declared independently at invocation and must match the config, and
    each run dir must hold exactly the cells the config declares;
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


# The surface this pipeline actually implements. Kept in sync with
# configs/main_grid_manifest.yaml `implementation_status` by
# tests/test_verify_minigrid.py, which reads that file rather than trusting
# these literals.
IMPLEMENTED_TASKS = {"mmlu", "gsm8k"}
IMPLEMENTED_METHOD_FAMILIES = {"gptq", "awq"}

# The acceptance contract every grid config must satisfy, declared once and
# checked up front (incident 25, 2026-07-26).
#
# The defect this replaces: four of these were read with `.get()` and the fifth,
# `calibration`, with a subscript. `configs/pace_escalation_h3.yaml` omitted the
# subscripted one, so the escalation validator died with a bare
# `KeyError: 'calibration'` at the first read, after the complete 44-cell grid
# had been produced, archived and sealed. The reuse decision that preceded it
# ("the validator is model-agnostic, so no fork") had checked the validator's
# ITERATION surface -- which models it walks -- and never its CONTRACT surface --
# which keys it demands. Diff the contract, not the code path.
#
# So: one constant, validated together, reporting EVERY missing key rather than
# whichever one a subscript reaches first.
REQUIRED_ACCEPTANCE_KEYS = (
    "expected_jsonl_files",
    "expected_item_counts",
    "task_dataset_revisions",
    "calibration",
)

# `baseline_accuracy_ranges` is the fifth key and is deliberately NOT in the
# tuple above. It has a REGISTERED absent-state: a config may omit it while
# declaring `baseline_accuracy_ranges_status: pending-...`, which is how the
# escalation config legitimately sat between its eval fan-out and its four-gate
# commit. Raising on its absence would delete that state. Its absence is still
# fail-closed, as a named check that produces a validation error rather than a
# passing run -- see `test_escalation_validator_fails_closed_on_the_pending_state`
# and `test_minigrid_validator_fails_closed_without_derived_fp16_ranges`.
#
# The distinction is registered design, not the accidental split this incident
# was about: every key here fails closed, and none can go missing quietly.
GATED_ACCEPTANCE_KEY = "baseline_accuracy_ranges"


class MissingAcceptanceKeys(ValueError):
    """Raised when a grid config's acceptance block is structurally incomplete."""


def acceptance_value(acceptance: dict[str, Any], key: str) -> Any:
    """The single accessor for every acceptance key, required or gated.

    Uniform by construction: `verify_acceptance_contract` has already proved the
    required keys present, so no caller needs to know which class a key is in,
    and no future key can quietly acquire a different access idiom.
    """
    return acceptance.get(key)


def verify_acceptance_contract(acceptance: dict[str, Any], config_path: Path) -> None:
    """Fail before any per-file work if the acceptance block is incomplete.

    Reports every missing key at once. A validator that dies on the first one
    tells the operator to add a key, run again, and discover the next.
    """
    missing = [key for key in REQUIRED_ACCEPTANCE_KEYS if acceptance.get(key) is None]
    if missing:
        raise MissingAcceptanceKeys(
            f"{config_path}: minigrid_acceptance is missing "
            f"{len(missing)} required key(s): {', '.join(missing)}. "
            f"Every grid config must declare all of {list(REQUIRED_ACCEPTANCE_KEYS)} "
            f"(plus {GATED_ACCEPTANCE_KEY}, or an explicit "
            f"{GATED_ACCEPTANCE_KEY}_status: pending-... in its place)."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed validation for the H3 mini-grid.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--results-root", required=True, help="Directory holding each model's run dir.")
    parser.add_argument("--project-root", default=".")
    # REQUIRED, no default (incident 26, 2026-07-26). This used to default to
    # RESULTS_ROOT/minigrid_validation_summary.json -- a filename naming ONE grid,
    # under a results root BOTH grids share. The escalation validator therefore
    # overwrote the mini-grid's completed validation summary while being correct
    # in every other respect: config, results root, model tags and cell count all
    # declared and all verified. None of those controls says where output lands.
    #
    # This is the standing rule -- no job script is ever given a default grid,
    # reader or writer -- applied to the one place it had not been. The validator
    # was hardened as the pair's reader; it also writes.
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the validation summary. Required: a default here names one "
        "grid while both grids share a results root, which silently overwrites "
        "the other grid's completed summary (incident 26).",
    )
    # The grid the OPERATOR believes they are validating, declared independently
    # of the config so the two can be made to disagree. Required, because the
    # dangerous invocation is not a missing config -- it is a *valid* config for
    # the wrong grid, which validates a complete set and exits 0 while saying
    # nothing about the grid the operator meant. Two independent declarations
    # that must agree is the only thing that catches that.
    parser.add_argument(
        "--expect-model-tags",
        required=True,
        nargs="+",
        help="Model tags this run is expected to cover; must match the config's models exactly.",
    )
    parser.add_argument(
        "--expect-cells",
        required=True,
        type=int,
        help="Number of JSONL cells this grid must expand to; must match the config.",
    )
    args = parser.parse_args()

    results_root = Path(args.results_root)
    output = Path(args.output)
    summary = verify_minigrid(
        Path(args.config),
        results_root,
        Path(args.project_root).resolve(),
        expect_model_tags=args.expect_model_tags,
        expect_cells=args.expect_cells,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {output}")
    if not summary["passed"]:
        raise SystemExit(1)


def verify_minigrid(
    config_path: Path,
    results_root: Path,
    project_root: Path,
    *,
    expect_model_tags: list[str] | None = None,
    expect_cells: int | None = None,
) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    acceptance = config.get("minigrid_acceptance")
    if not isinstance(acceptance, dict):
        raise ValueError("mini-grid config must declare minigrid_acceptance before execution")

    models = config.get("models") or []
    if not models:
        raise ValueError("mini-grid config must declare a models list")

    tasks = [str(task["name"]) for task in config.get("tasks", [])]
    task_by_name = {str(task["name"]): task for task in config.get("tasks", [])}
    # Structural completeness first: every required key, reported together, before
    # any per-file work (incident 25).
    verify_acceptance_contract(acceptance, config_path)

    expected_counts = {
        str(k): int(v)
        for k, v in acceptance_value(acceptance, "expected_item_counts").items()
    }
    calibration = acceptance_value(acceptance, "calibration")
    paired_seeds = [int(seed) for seed in calibration["paired_seeds"]]

    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    # ---- grid identity: the config must be the grid the operator asked for --
    # A validator pointed at the wrong config does not fail -- it validates a
    # complete, self-consistent grid and exits 0, certifying nothing about the
    # grid it was meant to check. Both grids in this campaign live under the
    # same results root, so the results root cannot disambiguate them; only an
    # independent declaration of intent can. These run FIRST so a mismatched
    # pairing errors before any per-file work.
    declared_tags = [str(model["tag"]) for model in models]
    declared_runs = {str(model["tag"]): str(model["run_name"]) for model in models}
    expected_files = sum(
        (1 + len(model.get("methods", []))) * len(tasks) for model in models
    )

    if expect_model_tags is not None:
        check(
            sorted(declared_tags) == sorted(str(t) for t in expect_model_tags),
            f"config covers the expected model tags {sorted(expect_model_tags)} "
            f"(config declares {sorted(declared_tags)})",
            errors,
            checks,
        )
    if expect_cells is not None:
        check(
            expected_files == int(expect_cells),
            f"config expands to the expected {expect_cells} cells "
            f"(config expands to {expected_files})",
            errors,
            checks,
        )

    # ---- the results root holds exactly this grid's cells, nothing else -----
    # Equality, not containment: a missing cell and a foreign cell are both
    # pairing failures. A run dir carrying another grid's JSONLs means the
    # config and the results do not describe the same run.
    for model in models:
        tag = str(model["tag"])
        run_dir = results_root / declared_runs[tag]
        # NB: verify_common.check() returns None, so its result must never be
        # branched on -- `if not check(...)` is always true and would skip the
        # check below unconditionally. Evaluate the condition separately.
        run_dir_exists = run_dir.is_dir()
        check(run_dir_exists, f"{tag}: run dir {declared_runs[tag]!r} exists", errors, checks)
        if not run_dir_exists:
            continue
        declared_cells = {
            f"{name}.{task}.jsonl"
            for name in [str(model["baseline"]["name"])]
            + [str(m["name"]) for m in model.get("methods", [])]
            for task in tasks
        }
        observed_cells = {p.name for p in run_dir.glob("*.jsonl")}
        missing = sorted(declared_cells - observed_cells)
        foreign = sorted(observed_cells - declared_cells)
        check(
            observed_cells == declared_cells,
            f"{tag}: run dir holds exactly the {len(declared_cells)} cells the "
            f"config declares (missing={missing or 'none'}, "
            f"unaccounted={foreign or 'none'})",
            errors,
            checks,
        )

    # ---- scope guard against the open implementation items -----------------
    # configs/main_grid_manifest.yaml records rtn_builder, wanda_builder,
    # arc_challenge_loader and hellaswag_loader as not-implemented, and the
    # WikiText-2 calibration path as blocked (decided by the 2026-07-16
    # amendment, deliberately not yet implemented). The mini-grid registration
    # scopes this grid to {GPTQ, AWQ} x 4-bit x C4 x {MMLU, GSM8K}.
    #
    # These checks make each of those gaps fail closed BY NAME. Without them a
    # config edit could route the grid into an unimplemented builder or loader
    # and the failure would surface as a KeyError or an empty file rather than
    # as a scope violation.
    for task_name in tasks:
        check(
            task_name in IMPLEMENTED_TASKS,
            f"task {task_name!r} is an implemented loader "
            f"(implemented: {', '.join(sorted(IMPLEMENTED_TASKS))}; "
            "arc_challenge and hellaswag are not-implemented per "
            "configs/main_grid_manifest.yaml)",
            errors,
            checks,
        )
        check(
            task_name in expected_counts,
            f"task {task_name!r} declares an expected item count",
            errors,
            checks,
        )
    check(
        str(calibration["dataset"]) == "allenai/c4",
        "calibration set is C4 (the mini-grid is C4-only; the WikiText-2 "
        "builder path is decided but not implemented and fails closed)",
        errors,
        checks,
    )
    check(
        int(calibration["bits"]) == 4,
        "calibration declares 4-bit (3-bit dose-response is deferred with the "
        "rest of the main grid)",
        errors,
        checks,
    )
    check(
        sorted(int(s) for s in paired_seeds) == [0, 1, 2, 3, 4],
        "paired seeds are exactly the registered {0,1,2,3,4}",
        errors,
        checks,
    )
    file_checksums: dict[str, str] = {}
    baseline_accuracies: dict[str, dict[str, float]] = {}
    per_model_artifacts: dict[str, set[str]] = {}

    # The gate ranges are derived from the trusted reference runs and committed
    # before any quantized result exists. Their absence is a hard stop, not a
    # skipped check: a mini-grid validated without FP16 gates has no baseline
    # evidence that the eval path was intact.
    ranges = acceptance_value(acceptance, GATED_ACCEPTANCE_KEY)
    check(
        isinstance(ranges, dict) and bool(ranges),
        "config declares FP16 baseline_accuracy_ranges "
        "(see docs/MINIGRID_FP16_GATE_DERIVATION_2026-07-21.md)",
        errors,
        checks,
    )
    ranges = ranges if isinstance(ranges, dict) else {}

    for model in models:
        tag = str(model["tag"])
        run_name = str(model["run_name"])
        run_dir = results_root / run_name
        baseline_name = str(model["baseline"]["name"])
        baseline_model_id = str(model["baseline"]["model_id"])
        baseline_revision = model["baseline"].get("revision")
        method_configs = {str(m["name"]): m for m in model.get("methods", [])}
        methods = [baseline_name] + list(method_configs)

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
                if task not in expected_counts:
                    continue
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
            if family not in IMPLEMENTED_METHOD_FAMILIES or not seed_text.isdigit():
                check(
                    False,
                    f"{tag}: method {name!r} is an implemented, seed-paired family "
                    f"(implemented: {', '.join(sorted(IMPLEMENTED_METHOD_FAMILIES))}; "
                    "rtn and wanda are not-implemented per "
                    "configs/main_grid_manifest.yaml)",
                    errors,
                    checks,
                )
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
    for task_name, revision in acceptance_value(acceptance, "task_dataset_revisions").items():
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
    # No `is not None` guard: the contract check above has already proved this
    # key present, so the check is unconditional. The old guard made a declared
    # cell count optional in practice while the docstring called it required.
    declared_total = acceptance_value(acceptance, "expected_jsonl_files")
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
        "declared_model_tags": declared_tags,
        "expect_model_tags": list(expect_model_tags) if expect_model_tags is not None else None,
        "expect_cells": int(expect_cells) if expect_cells is not None else None,
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
