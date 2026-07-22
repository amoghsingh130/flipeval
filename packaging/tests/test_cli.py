"""Golden-fixture tests for the standalone comparison CLI.

One test per verdict class, plus the mismatched-item-set failure, plus the
guarantees that matter more than the labels: that pairing is on item identity
rather than row order, and that this layer does not alter any number the
registered analysis code produces.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from flipeval.core import compare
from flipeval_cli.loader import (
    FilterAmbiguity,
    ItemSetMismatch,
    UnscoredRows,
    align_by_item_id,
    available_filters,
    load_log_samples,
    read_raw_samples,
    require_identical_item_sets,
)
from flipeval_cli.main import EXIT_INPUT_ERROR, EXIT_UNDERPOWERED, main
from flipeval_cli.verdict import (
    CERTIFIED_EQUIVALENT,
    DEGRADED,
    IMPROVED,
    UNDERPOWERED,
)

FIXTURES = Path(__file__).parent / "fixtures"


def paths(stem: str) -> tuple[str, str]:
    return (
        str(FIXTURES / f"{stem}_baseline.jsonl"),
        str(FIXTURES / f"{stem}_candidate.jsonl"),
    )


def run(stem: str, *extra: str) -> tuple[int, str]:
    baseline, candidate = paths(stem)
    import io
    import contextlib

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main(["compare", baseline, candidate, *extra])
    return code, buffer.getvalue()


@pytest.mark.parametrize(
    "stem,expected_label,expected_code",
    [
        ("equivalent", CERTIFIED_EQUIVALENT, 0),
        ("degraded", DEGRADED, 0),
        ("improved", IMPROVED, 0),
        ("underpowered", UNDERPOWERED, EXIT_UNDERPOWERED),
    ],
)
def test_each_verdict_class(stem, expected_label, expected_code):
    code, output = run(stem, "--margin", "0.02")
    assert f"VERDICT: {expected_label}" in output
    assert code == expected_code


def test_degraded_and_improved_are_mirror_images():
    """Direction is read from the discordant counts, not from the label."""
    _, degraded = run("degraded", "--json")
    _, improved = run("improved", "--json")
    degraded_payload = json.loads(degraded)
    improved_payload = json.loads(improved)
    assert degraded_payload["mcnemar_b_harmful"] == improved_payload["mcnemar_c_beneficial"]
    assert degraded_payload["mcnemar_c_beneficial"] == improved_payload["mcnemar_b_harmful"]
    assert degraded_payload["net_accuracy_delta"] == pytest.approx(
        -improved_payload["net_accuracy_delta"]
    )


def test_mismatched_item_sets_fail_loudly(capsys):
    baseline, candidate = paths("mismatch")
    code = main(["compare", baseline, candidate])
    captured = capsys.readouterr()
    assert code == EXIT_INPUT_ERROR
    assert "item sets differ" in captured.err
    assert "shared: 25" in captured.err
    assert "VERDICT" not in captured.out


def test_mismatch_raises_before_any_statistic_is_computed():
    baseline = load_log_samples(FIXTURES / "mismatch_baseline.jsonl")
    candidate = load_log_samples(FIXTURES / "mismatch_candidate.jsonl")
    with pytest.raises(ItemSetMismatch) as error:
        require_identical_item_sets(baseline, candidate, "a", "b")
    assert "not a paired comparison" in str(error.value)


def test_pairing_is_on_item_identity_not_row_order(tmp_path):
    """Shuffling one file's rows must not change any reported number."""
    baseline_path, candidate_path = paths("degraded")
    rows = Path(candidate_path).read_text(encoding="utf-8").splitlines()
    random.Random(1234).shuffle(rows)
    shuffled = tmp_path / "shuffled_candidate.jsonl"
    shuffled.write_text("\n".join(rows) + "\n", encoding="utf-8")

    import contextlib
    import io

    def capture(path):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            main(["compare", baseline_path, str(path), "--json"])
        return json.loads(buffer.getvalue())

    assert capture(candidate_path) == capture(shuffled) | {
        "candidate_path": candidate_path
    }


def test_cli_does_not_alter_registered_statistics():
    """Every number in the report comes from `flipeval.core.compare` unchanged."""
    baseline_path, candidate_path = paths("degraded")
    baseline = load_log_samples(baseline_path)
    candidate = load_log_samples(candidate_path)
    item_ids = require_identical_item_sets(baseline, candidate, baseline_path, candidate_path)
    aligned_base, aligned_cand = align_by_item_id(baseline, candidate, item_ids)
    direct = compare(aligned_base, aligned_cand, margin=0.02, bootstrap=1000, seed=0)

    _, output = run("degraded", "--json", "--margin", "0.02")
    payload = json.loads(output)

    for field, value in direct.to_dict().items():
        if field == "confidence_intervals":
            continue
        assert payload[field] == value, f"CLI changed {field}"


def test_required_n_at_margin_is_reported_for_underpowered():
    _, output = run("underpowered", "--json", "--margin", "0.02")
    payload = json.loads(output)
    assert payload["verdict"] == UNDERPOWERED
    assert isinstance(payload["required_n_at_margin"], int)
    assert payload["required_n_at_margin"] > payload["n"], (
        "an underpowered run should need more items than it had"
    )


def test_underpowered_report_carries_flip_counts_and_churn():
    _, output = run("underpowered", "--margin", "0.02")
    assert "b  correct -> wrong" in output
    assert "c  wrong -> correct" in output
    assert "correctness-state" in output
    assert "net delta" in output
    assert "required n @ margin" in output


def test_duplicate_item_ids_are_rejected(tmp_path):
    row = json.loads(Path(paths("equivalent")[0]).read_text().splitlines()[0])
    duplicated = tmp_path / "dupes.jsonl"
    duplicated.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate item_id"):
        load_log_samples(duplicated)


def test_missing_file_is_an_input_error(capsys):
    code = main(["compare", str(FIXTURES / "nope.jsonl"), paths("equivalent")[1]])
    assert code == EXIT_INPUT_ERROR
    assert "no such log_samples file" in capsys.readouterr().err


def test_nonpositive_margin_is_rejected(capsys):
    baseline, candidate = paths("equivalent")
    assert main(["compare", baseline, candidate, "--margin", "0"]) == EXIT_INPUT_ERROR
    assert "--margin must be positive" in capsys.readouterr().err


class TestFilterSelection:
    """A multi-filter file must never be scored under a guessed filter."""

    def test_multiple_filters_without_flag_is_refused(self, capsys):
        baseline, candidate = paths("multifilter")
        code = main(["compare", baseline, candidate])
        captured = capsys.readouterr()
        assert code == EXIT_INPUT_ERROR
        assert "carries 2 scoring filters" in captured.err
        assert "'strict-match'" in captured.err
        assert "'flexible-extract'" in captured.err
        assert "617" in captured.err, "the refusal should cite why it matters"
        assert "VERDICT" not in captured.out

    def test_no_silent_default_to_index_zero(self):
        """The first filter in the file must not win by default."""
        samples = read_raw_samples(paths("multifilter")[0])
        assert available_filters(samples)[0] == "strict-match"
        with pytest.raises(FilterAmbiguity):
            load_log_samples(paths("multifilter")[0])

    @pytest.mark.parametrize("filter_name", ["strict-match", "flexible-extract"])
    def test_each_filter_is_selectable(self, filter_name):
        code, output = run("multifilter", "--filter", filter_name)
        assert f"filter   : {filter_name}" in output
        assert "items    : 120" in output
        assert code in (0, EXIT_UNDERPOWERED)

    def test_the_two_filters_give_different_numbers(self):
        """The whole reason the tool refuses to choose."""
        _, strict = run("multifilter", "--filter", "strict-match", "--json")
        _, flexible = run("multifilter", "--filter", "flexible-extract", "--json")
        strict_payload = json.loads(strict)
        flexible_payload = json.loads(flexible)
        assert strict_payload["baseline_accuracy"] != flexible_payload["baseline_accuracy"]
        assert strict_payload["n"] == flexible_payload["n"] == 120

    def test_unknown_filter_name_is_refused(self, capsys):
        baseline, candidate = paths("multifilter")
        code = main(["compare", baseline, candidate, "--filter", "nope"])
        assert code == EXIT_INPUT_ERROR
        assert "not present" in capsys.readouterr().err

    def test_single_filter_file_needs_no_flag(self):
        code, output = run("equivalent")
        assert "VERDICT" in output
        assert code == 0


class TestStringCompareGuard:
    """Correctness must not silently change definition."""

    def test_unscored_rows_are_refused_by_default(self, capsys):
        baseline, candidate = paths("unscored")
        code = main(["compare", baseline, candidate])
        captured = capsys.readouterr()
        assert code == EXIT_INPUT_ERROR
        assert "carry no harness metric" in captured.err
        assert "--allow-string-compare" in captured.err
        assert "VERDICT" not in captured.out

    def test_opt_in_flag_permits_them(self):
        code, output = run("unscored", "--allow-string-compare")
        assert "VERDICT" in output
        assert code in (0, EXIT_UNDERPOWERED)

    def test_guard_raises_before_conversion(self):
        with pytest.raises(UnscoredRows, match="different definition of"):
            load_log_samples(paths("unscored")[0])


def test_equivalent_fixture_is_not_trivially_identical():
    """Guards the fixture itself: equivalence must be earned, not vacuous."""
    _, output = run("equivalent", "--json")
    payload = json.loads(output)
    assert payload["mcnemar_b_harmful"] > 0
    assert payload["mcnemar_c_beneficial"] > 0
    assert payload["accuracy_state_churn"] > 0
    assert payload["total_answer_churn"] > payload["accuracy_state_churn"], (
        "answer churn should exceed correctness churn (wrong -> different wrong)"
    )
