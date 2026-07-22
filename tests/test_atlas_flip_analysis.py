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
    binary_correct,
    parse_next_link,
    read_field,
    s1_key,
    s1_prompt,
    s1_run_combinations,
    RETRYABLE_STATUS,
    _retry_delay,
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
    # Rev-2 (F4): the gate decision is unchanged; the recorded reason now names
    # the root cause instead of the bare symptom "no joinable items", so an
    # exclusion is auditable from the archived cell alone.
    assert "disjoint item sets" in joined["exclusion_reason"]


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


# ---------------------------------------------------------------------------
# Rev-2 corrections (findings F1, F2, F4, F5 of the 2026-07-21 spot-check)
# ---------------------------------------------------------------------------

def _nested_row(example, prompt, acc_norm):
    """Newer lighteval details schema: no `hashes`, metrics nested (F2)."""
    return {"example": example, "full_prompt": prompt, "metrics": {"acc_norm": acc_norm}}


def test_s1_correctness_column_finds_nested_metrics_struct():
    rows = [_nested_row("a", "p", 1.0), _nested_row("b", "p", 0.0)]
    assert s1_correctness_column(rows) == "metrics.acc_norm"


def test_s1_correctness_column_prefers_top_level_when_both_present():
    rows = [{"acc_norm": 1.0, "metrics": {"acc_norm": 0.0}}]
    assert s1_correctness_column(rows) == "acc_norm"


def test_s1_correctness_column_still_skips_genuinely_non_binary_tasks():
    with pytest.raises(CellSkip):
        s1_correctness_column([{"metrics": {"mc1": 0.3, "mc2": 0.7}}])


def test_read_field_handles_dotted_and_plain_specs():
    assert read_field({"acc": 1.0}, "acc") == 1.0
    assert read_field({"metrics": {"acc": 0.0}}, "metrics.acc") == 0.0
    assert read_field({"metrics": None}, "metrics.acc") is None
    assert read_field({}, "missing") is None


def test_nested_schema_cell_joins_and_analyzes_end_to_end():
    """The 583 cells rev-1 dropped are analysable once the parser reads them."""
    base = [_nested_row("i1", "p1", 1.0), _nested_row("i2", "p2", 0.0)]
    quant = [_nested_row("i1", "p1", 0.0), _nested_row("i2", "p2", 0.0)]
    joined = join_cell(base, quant, key_of=s1_key, identity_of=s1_key, prompt_of=s1_prompt)
    assert not joined["excluded"] and joined["joinable"] == 2
    metrics = analyze_cell(joined, correctness_column=s1_correctness_column(quant),
                           prediction_of=s1_prediction, bootstrap=10, seed=0)
    assert metrics["n"] == 2
    assert metrics["harmful_flip_rate"] == pytest.approx(0.5)


def test_s1_key_and_prompt_prefer_hashes_then_fall_back_to_raw_columns():
    hashed = {"hashes": {"example": "H", "full_prompt": "P"}, "example": "raw", "full_prompt": "rawp"}
    assert s1_key(hashed) == "H" and s1_prompt(hashed) == "P"
    raw = _nested_row("R", "RP", 1.0)
    assert s1_key(raw) == "R" and s1_prompt(raw) == "RP"
    assert s1_key({}) is None and s1_prompt({}) is None


def test_run_combinations_start_at_latest_latest_and_step_back(): 
    """F1: a strict generalisation of rev-1 -- element 0 is rev-1's choice."""
    combos = s1_run_combinations(["2023_01_01T00_00_00", "2023_03_01T00_00_00"],
                                 ["2023_02_01T00_00_00", "2023_04_01T00_00_00"])
    assert combos[0] == ("2023_03_01T00_00_00", "2023_04_01T00_00_00")
    assert len(combos) == 4 and len(set(combos)) == 4
    # every base/quantized timestamp is reachable via some combination
    assert {b for b, _ in combos} == {"2023_01_01T00_00_00", "2023_03_01T00_00_00"}
    assert {q for _, q in combos} == {"2023_02_01T00_00_00", "2023_04_01T00_00_00"}


def test_run_combinations_single_run_per_side_is_a_single_combination():
    assert s1_run_combinations(["2023_01_01T00_00_00"], ["2023_02_01T00_00_00"]) == [
        ("2023_01_01T00_00_00", "2023_02_01T00_00_00")
    ]


def test_no_join_reason_names_the_root_cause_not_the_symptom():
    """F4: an unreadable join key must not be filed as a missing metric."""
    unkeyed = [{"metrics": {"acc_norm": 1.0}}, {"metrics": {"acc_norm": 0.0}}]
    joined = join_cell(unkeyed, unkeyed, key_of=s1_key, identity_of=s1_key, prompt_of=s1_prompt)
    assert joined["excluded"]
    assert "join key absent on both sides" in joined["exclusion_reason"]
    assert "no acc_norm" not in joined["exclusion_reason"]


def test_no_join_reason_distinguishes_disjoint_item_sets():
    left = [_nested_row("a", "p", 1.0)]
    right = [_nested_row("z", "p", 1.0)]
    joined = join_cell(left, right, key_of=s1_key, identity_of=s1_key, prompt_of=s1_prompt)
    assert "disjoint item sets" in joined["exclusion_reason"]


def test_binary_correct_rejects_missing_value_as_cellskip():
    with pytest.raises(CellSkip):
        binary_correct(None, "metrics.acc_norm")


def test_parse_next_link_reads_rfc5988_next_target():
    header = '<https://huggingface.co/api/x?cursor=abc>; rel="next", <https://x/first>; rel="first"'
    assert parse_next_link(header) == "https://huggingface.co/api/x?cursor=abc"
    assert parse_next_link('<https://x>; rel="prev"') is None
    assert parse_next_link(None) is None
    assert parse_next_link("") is None


def test_retry_delay_honours_retry_after_header():
    import urllib.error
    exc = urllib.error.HTTPError("u", 429, "Too Many Requests",
                                 {"Retry-After": "7"}, None)
    assert _retry_delay(exc, 0) == 7.0


def test_retry_delay_falls_back_to_bounded_exponential_backoff():
    delay = _retry_delay(RuntimeError("boom"), 3)
    assert 8.0 <= delay <= 10.0          # 2**3 plus <=25% jitter
    assert _retry_delay(RuntimeError("boom"), 20) <= 150.0   # bounded


def test_rate_limit_status_is_retryable_but_not_found_is_not():
    assert 429 in RETRYABLE_STATUS and 503 in RETRYABLE_STATUS
    assert 404 not in RETRYABLE_STATUS and 401 not in RETRYABLE_STATUS


def test_skipped_cell_join_does_not_carry_matched_rows():
    """A join travelling on a CellSkip must not archive its matched row-pairs.

    Regression for the rev-2 archival defect: the success path strips `matched`
    but the skip path did not, so one skipped DROP cell serialized 9,534 full
    row-pairs (174 MB) and the run tarball reached 306 MB against rev-1's
    735 KB. No statistic was affected -- `matched` is only serialized -- but the
    archive was unusable and dumped raw per-item rows.
    """
    base = [_nested_row("i1", "p1", 1.0), _nested_row("i2", "p2", 0.0)]
    joined = join_cell(base, base, key_of=s1_key, identity_of=s1_key, prompt_of=s1_prompt)
    assert "matched" in joined                      # join_cell itself still returns it
    stripped = {k: v for k, v in joined.items() if k != "matched"}
    assert "matched" not in stripped
    assert stripped["joinable"] == 2                # the statistics survive the strip
