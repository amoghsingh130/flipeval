import pytest

from scripts.atlas_flip_analysis import (
    PROMPT_PASS_THRESHOLD,
    CellSkip,
    analyze_cell,
    dedupe_join_keys,
    find_s1_task_file,
    find_s2_task_file,
    join_cell,
    s1_correctness_column,
    s1_prediction,
    s2_metric_column,
    s2_prediction,
)


def _s1_row(example, prompt, acc_norm, predictions=None):
    return {
        "hashes": {"example": example, "full_prompt": prompt},
        "acc_norm": acc_norm,
        "predictions": predictions,
    }


def _key(row):
    return row["hashes"]["example"]


def _prompt(row):
    return row["hashes"]["full_prompt"]


def test_dedupe_drops_every_occurrence_of_duplicated_keys():
    rows = [_s1_row("a", "p", 1), _s1_row("a", "p", 0), _s1_row("b", "p", 1)]
    kept, dropped = dedupe_join_keys(rows, _key)
    assert set(kept) == {"b"}
    assert dropped == 2


def test_join_gate_excludes_below_99_percent_prompt_identity():
    base = [_s1_row(str(i), f"p{i}", 1) for i in range(200)]
    quant = [_s1_row(str(i), f"p{i}" if i else "different", 1) for i in range(200)]
    joined = join_cell(base, quant, key_of=_key, identity_of=_key, prompt_of=_prompt)
    assert joined["joinable"] == 200
    assert joined["prompt_identical"] == 199
    assert joined["prompt_pass_rate"] == pytest.approx(0.995)
    assert not joined["excluded"]

    quant_bad = [_s1_row(str(i), f"p{i}" if i >= 3 else "x", 1) for i in range(200)]
    joined_bad = join_cell(base, quant_bad, key_of=_key, identity_of=_key, prompt_of=_prompt)
    assert joined_bad["prompt_pass_rate"] < PROMPT_PASS_THRESHOLD
    assert joined_bad["excluded"]
    assert "pass rate" in joined_bad["exclusion_reason"]


def test_join_gate_excludes_empty_intersection():
    joined = join_cell([_s1_row("a", "p", 1)], [_s1_row("b", "p", 1)],
                       key_of=_key, identity_of=_key, prompt_of=_prompt)
    assert joined["excluded"]
    assert joined["exclusion_reason"] == "no joinable items"


def test_s1_correctness_prefers_acc_norm_then_acc():
    assert s1_correctness_column([{"acc_norm": 1, "acc": 0}]) == "acc_norm"
    assert s1_correctness_column([{"acc_norm": None, "acc": 0}]) == "acc"
    with pytest.raises(CellSkip):
        s1_correctness_column([{"em": 0.5}])


def test_s1_prediction_is_loglikelihood_argmax_or_first_string():
    assert s1_prediction({"predictions": [-4.0, -1.5, -9.0]}) == "1"
    assert s1_prediction({"predictions": ["generated text", "other"]}) == "generated text"
    assert s1_prediction({"predictions": None}) is None


def test_s2_metric_priority_and_prediction():
    assert s2_metric_column([{"exact_match": 1, "acc": 0}]) == "exact_match"
    assert s2_metric_column([{"acc_norm": 0}]) == "acc_norm"
    with pytest.raises(CellSkip):
        s2_metric_column([{"other": 1}])
    assert s2_prediction({"filtered_resps": [["answer"]]}) == "answer"
    assert s2_prediction({"resps": [["fallback"]]}) == "fallback"
    assert s2_prediction({}) is None


def test_analyze_cell_runs_registered_suite_and_flags_missing_predictions():
    base = [_s1_row(str(i), f"p{i}", 1 if i < 60 else 0, [-1.0, -2.0]) for i in range(100)]
    quant = [_s1_row(str(i), f"p{i}", 1 if (10 <= i < 65) else 0, [-2.0, -1.0]) for i in range(100)]
    joined = join_cell(base, quant, key_of=_key, identity_of=_key, prompt_of=_prompt)
    metrics = analyze_cell(joined, correctness_column="acc_norm",
                           prediction_of=s1_prediction, bootstrap=50, seed=0)
    assert metrics["n"] == 100
    assert metrics["baseline_accuracy"] == pytest.approx(0.60)
    assert metrics["method_accuracy"] == pytest.approx(0.55)
    assert metrics["harmful_flip_rate"] == pytest.approx(0.10)
    assert metrics["beneficial_flip_rate"] == pytest.approx(0.05)
    assert metrics["prediction_available"] is True
    assert metrics["mcnemar_p"] is not None

    quant_no_pred = [dict(row, predictions=None) for row in quant]
    joined2 = join_cell(base, quant_no_pred, key_of=_key, identity_of=_key, prompt_of=_prompt)
    metrics2 = analyze_cell(joined2, correctness_column="acc_norm",
                            prediction_of=s1_prediction, bootstrap=50, seed=0)
    assert metrics2["prediction_available"] is False
    assert metrics2["total_answer_churn"] is None
    assert metrics2["wrong_to_different_wrong_churn"] is None


def test_analyze_cell_fails_closed_on_non_binary_correctness():
    base = [_s1_row("a", "p", 0.37)]
    joined = join_cell(base, base, key_of=_key, identity_of=_key, prompt_of=_prompt)
    with pytest.raises(CellSkip, match="not binary"):
        analyze_cell(joined, correctness_column="acc_norm",
                     prediction_of=s1_prediction, bootstrap=10, seed=0)


def test_find_s1_task_file_picks_latest_run_and_exact_task():
    # Directory names use the -/: timestamp form; manifest cardData uses underscores.
    files = [
        "2023-11-05T00:29:27.161865/details_harness|gsm8k|5_2023-11-05T00-29-27.161865.parquet",
        "2023-11-07T07:11:46.594603/details_harness|gsm8k|5_2023-11-07T07-11-46.594603.parquet",
        "2023-11-07T07:11:46.594603/details_harness|drop|3_2023-11-07T07-11-46.594603.parquet",
    ]
    stamps = ["2023_11_05T00_29_27.161865", "2023_11_07T07_11_46.594603"]
    assert find_s1_task_file(files, "harness_gsm8k_5", stamps).startswith("2023-11-07")
    assert "drop" in find_s1_task_file(files, "harness_drop_3", stamps)
    with pytest.raises(CellSkip):
        find_s1_task_file(files, "harness_arc_challenge_25", stamps)


def test_find_s2_task_file_requires_exact_variant_dir_and_task_boundary():
    files = [
        "Meta-Llama-3.1-8B-Instruct/samples_leaderboard_bbh_navigate_2024-09-26T08-31-39.355596.jsonl",
        "Meta-Llama-3.1-8B-Instruct-W4A16/samples_bbh_navigate_2024-09-27T00-03-53.710013.jsonl",
        "Meta-Llama-3.1-8B-Instruct-W4A16/samples_bbh_logical_deduction_five_objects_2024-09-27T00-03-53.710013.jsonl",
    ]
    base = find_s2_task_file(files, "Meta-Llama-3.1-8B-Instruct", "bbh_navigate",
                             ["2024-09-26T08-31-39.355596"])
    assert base.startswith("Meta-Llama-3.1-8B-Instruct/")
    quant = find_s2_task_file(files, "Meta-Llama-3.1-8B-Instruct-W4A16", "bbh_navigate",
                              ["2024-09-27T00-03-53.710013"])
    assert quant.startswith("Meta-Llama-3.1-8B-Instruct-W4A16/")
    with pytest.raises(CellSkip):
        find_s2_task_file(files, "Meta-Llama-3.1-8B-Instruct-W4A16", "bbh_logical_deduction",
                          ["2024-09-27T00-03-53.710013"])
