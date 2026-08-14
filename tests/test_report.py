"""Tests for the five-line reporting standard emitted by ``flipeval report``.

The five lines are the paper's deliverable, so these tests are about what the
block SAYS, not only about what it computes.

THE FIFTH LINE IS THE ONE THAT MATTERS MOST. The paper's audit found that no
audited source releases task-matched per-item outputs, and line 5 asks the field
to. The tool cannot verify a release, so it must never imply one: with no
location given it has to say the line is unmet, and it must not fall back to
"the files you passed me" as though that were a publication. Passing that line
silently would be this tool's own version of the defect the paper documents, so
it gets the most explicit test in the file.

THE SECOND LINE MUST NOT LAUNDER A NON-RESULT. "We failed to detect a
difference" is not "the models are equivalent" -- that conflation is the error
\\S\\ref{sec:certification} exists to prevent -- so the emitted line carries the
distinction in words as well as in its verdict field.

FRAGILITY. Tests here assert the block's structure, its wording, and arithmetic
that is exactly determined (the shortfall against a published requirement).
Where an outcome depends on a test statistic, they assert that the rendered text
AGREES WITH the computed field rather than hard-coding a verdict, so a change in
the statistics shows up in test_core.py where it belongs, not as a spurious
failure here.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from flipeval import five_line_report
from flipeval.report import FiveLineReport

ROOT = Path(__file__).resolve().parents[1]


def _records(correct, predictions=None):
    predictions = predictions or [str(int(value)) for value in correct]
    return [
        {"item_id": str(index), "prediction": predictions[index], "correct": value}
        for index, value in enumerate(correct)
    ]


def _pair(n=200, harmful=8, beneficial=6):
    """A paired set of ``n`` items with a controlled number of flips each way."""
    base = [True] * (n // 2) + [False] * (n - n // 2)
    method = list(base)
    for index in range(harmful):
        method[index] = False
    for index in range(n // 2, n // 2 + beneficial):
        method[index] = True
    return _records(base), _records(method)


def _report(**kwargs):
    baseline, method = _pair()
    return five_line_report(baseline, method, bootstrap=50, seed=0, **kwargs)


def test_the_block_has_exactly_five_numbered_lines():
    report = _report()
    assert isinstance(report, FiveLineReport)
    assert len(report.lines) == 5
    text = report.to_text()
    for number in range(1, 6):
        assert f"{number}. " in text


def test_line_five_is_unmet_when_no_location_is_given():
    report = _report()
    line5 = report.lines[4]
    assert "NOT DECLARED" in line5
    assert report.per_item_outputs is None
    # It must not present the inputs it was handed as though they were released.
    assert "released at" not in line5


def test_line_five_records_the_location_when_one_is_given():
    report = _report(per_item_outputs="https://example.invalid/per-item")
    line5 = report.lines[4]
    assert "released at https://example.invalid/per-item" in line5
    assert "NOT DECLARED" not in line5


def test_line_two_refuses_to_read_a_non_detection_as_equivalence():
    line2 = _report().lines[1]
    assert "failure to detect a difference is not" in line2
    assert "equivalence" in line2


def test_line_two_agrees_with_the_computed_tost_verdict():
    report = _report()
    expected = "EQUIVALENT" if report.result.tost_equivalent else "NOT EQUIVALENT"
    assert expected in report.lines[1]
    # "NOT EQUIVALENT" contains "EQUIVALENT", so check the negative case exactly.
    if not report.result.tost_equivalent:
        assert "NOT EQUIVALENT" in report.lines[1]


def test_line_one_states_the_margin_in_points():
    assert "+/-2.00 pp" in _report(margin=0.02).lines[0]
    assert "+/-1.00 pp" in _report(margin=0.01).lines[0]


def test_line_three_reports_churn_beside_the_net_delta():
    baseline, method = _pair(n=200, harmful=8, beneficial=6)
    report = five_line_report(baseline, method, bootstrap=50, seed=0)
    line3 = report.lines[2]
    # net = (6 - 8)/200 = -1.00 pp; churn = 14/200 = 7.00 pp.
    assert "-1.00 pp" in line3
    assert "7.00 pp" in line3
    assert "4.00 pp correct->wrong" in line3
    assert "3.00 pp wrong->correct" in line3


def test_line_four_cites_the_published_requirement_and_the_shortfall():
    report = _report(benchmark="mmlu", margin=0.02)
    # MMLU at 2 pp, median churn: 2,164 items required, 200 evaluated.
    assert report.required_n == 2164
    assert report.meets_required_n is False
    line4 = report.lines[3]
    assert "200 items evaluated against 2164 required" in line4
    assert "SHORT by 1964 items" in line4
    assert "mmlu" in line4
    # The planning caveat travels with the count, always.
    assert "assumed true difference of zero" in line4


def test_line_four_falls_back_to_this_pairs_own_churn_and_says_so():
    report = _report()
    assert report.benchmark is None
    assert "this pair's own observed churn" in report.required_n_source
    assert "pass --benchmark" in report.required_n_source


def test_line_four_reports_a_surplus_when_the_requirement_is_met():
    baseline, method = _pair(n=4000, harmful=10, beneficial=10)
    report = five_line_report(baseline, method, bootstrap=50, seed=0, benchmark="mmlu")
    assert report.meets_required_n is True
    assert "MEETS the requirement" in report.lines[3]
    assert "surplus" in report.lines[3]


def test_percentile_selects_a_different_published_requirement():
    typical = _report(benchmark="mmlu", percentile="median").required_n
    pessimistic = _report(benchmark="mmlu", percentile="p75").required_n
    assert pessimistic > typical


def test_margin_in_the_wrong_unit_is_caught():
    # 2.0 here would be a 200-point margin. compare() takes a proportion.
    with pytest.raises(ValueError, match="PROPORTION"):
        _report(margin=2.0)
    with pytest.raises(ValueError, match="margin must be positive"):
        _report(margin=0.0)


def test_bad_percentile_is_rejected_before_any_computation():
    with pytest.raises(ValueError, match="percentile must be one of"):
        _report(percentile="p50")


def test_to_dict_carries_the_numbers_behind_the_block():
    payload = _report(benchmark="mmlu").to_dict()
    assert payload["margin_pp"] == pytest.approx(2.0)
    assert payload["required_n"] == 2164
    assert payload["n_evaluated"] == 200
    assert payload["meets_required_n"] is False
    assert len(payload["lines"]) == 5
    assert "accuracy_state_churn" in payload["comparison"]
    json.dumps(payload)  # must be serialisable as emitted by `--json`


def test_labels_appear_in_the_header():
    report = _report(baseline_label="fp16.jsonl", method_label="gptq.jsonl")
    header = report.to_text(header=True)
    assert "fp16.jsonl" in header
    assert "gptq.jsonl" in header
    assert "paired on item_id" in header
    assert "fp16.jsonl" not in report.to_text(header=False)


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")


def test_cli_report_end_to_end(tmp_path):
    baseline, method = _pair()
    base_path = tmp_path / "fp16.jsonl"
    method_path = tmp_path / "gptq.jsonl"
    _write_jsonl(base_path, baseline)
    _write_jsonl(method_path, method)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "flipeval",
            "report",
            str(base_path),
            str(method_path),
            "--margin",
            "0.02",
            "--benchmark",
            "mmlu",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "1. " in completed.stdout and "5. " in completed.stdout
    # to_text() wraps at 88 columns, so any asserted phrase must be matched
    # against whitespace-normalised output or it breaks when the wrap moves.
    flat = " ".join(completed.stdout.split())
    assert "2164" in flat
    assert "NOT DECLARED" in flat


def test_cli_report_json_is_machine_readable(tmp_path):
    baseline, method = _pair()
    base_path = tmp_path / "fp16.jsonl"
    method_path = tmp_path / "gptq.jsonl"
    _write_jsonl(base_path, baseline)
    _write_jsonl(method_path, method)

    completed = subprocess.run(
        [sys.executable, "-m", "flipeval", "report", str(base_path), str(method_path), "--json"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["n_evaluated"] == 200
    assert len(payload["lines"]) == 5


def test_cli_required_n_lists_and_looks_up():
    listing = subprocess.run(
        [sys.executable, "-m", "flipeval", "required-n", "--list"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert listing.returncode == 0, listing.stderr
    assert "mmlu" in listing.stdout

    lookup = subprocess.run(
        [sys.executable, "-m", "flipeval", "required-n", "--benchmark", "mmlu", "--margin", "2.0"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert lookup.returncode == 0, lookup.stderr
    assert "2164" in lookup.stdout
