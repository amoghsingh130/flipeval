"""Tests for the required-$n$ lookup over the published certification table.

Three jobs, kept separate on purpose.

THE TWO COPIES MUST NOT FORK. ``flipeval/data/certification_tables_rev2.csv``
ships inside the package so the lookup works from an installed distribution,
where ``results/`` is absent. It is a second copy of a released artifact, and a
second copy is only safe while something checks it is the same copy -- so the
first test compares the two byte for byte. Both modules' docstrings promise this
test exists; if it is ever deleted, delete that promise with it.

THE TABLE MUST REMAIN THE PAPER'S TABLE. Every ``required_n`` column is
recomputed from its own ``discordance`` column through
``required_n_from_discordance``, which is the paper's Equation (2). This is what
keeps the lookup and the released CSV from drifting apart: if either the formula
or the artifact changes, all 108 cells stop agreeing at once. The recomputation
uses the library's implementation, and the values it must reproduce were read
independently out of the CSV, so agreement is not circular.

THE UNIT TRAP GETS ITS OWN TESTS. The table is indexed in percentage points
(``margin_pp=2.0``) and ``flipeval.compare`` takes the same quantity as a
proportion (``margin=0.02``). Passing one to the other is the mistake this API
is most likely to invite, it is silent in both directions -- 0.02 pp is a
plausible-looking margin, and 2.0 as a proportion is a 200-point one -- and it
is off by a factor of 10,000 in the resulting sample size. Both entry points
range-check and both are asserted here.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from flipeval import RequiredN, required_n_for_benchmark, required_n_from_discordance
from flipeval.certification import (
    PACKAGED_TABLE,
    available_benchmarks,
    available_margins_pp,
    format_required_n,
    load_certification_table,
)

ROOT = Path(__file__).resolve().parents[1]
RELEASED_TABLE = ROOT / "results" / "certification_tables_rev2.csv"

# Values quoted in paper/sections/certification.tex, Table~\ref{tab:certification}
# at the registered 2 pp margin. The table is the paper's, so a change here is a
# change to a published number and must be argued, not accepted.
PAPER_AT_2PP = {
    "mmlu": 2164,
    "gpqa": 749,
    "musr": 519,
    "gsm8k": 1184,
    "math": 2186,
    "arc_challenge": 1218,
    "ALL (pooled)": 1855,
}


def test_packaged_copy_is_byte_identical_to_the_released_artifact():
    if not RELEASED_TABLE.is_file():
        pytest.skip(f"released artifact not present in this checkout: {RELEASED_TABLE}")
    assert PACKAGED_TABLE.read_bytes() == RELEASED_TABLE.read_bytes()


def test_every_required_n_column_reproduces_from_its_own_discordance():
    rows = list(csv.DictReader(PACKAGED_TABLE.open(encoding="utf-8", newline="")))
    assert rows, "packaged certification table is empty"
    checked = 0
    for row in rows:
        margin_pp = float(row["margin_pp"])
        for percentile in ("p25", "median", "p75"):
            expected = int(row[f"required_n_{percentile}"])
            recomputed = required_n_from_discordance(
                float(row[f"discordance_{percentile}"]), margin_pp
            )
            assert recomputed == expected, (
                f"{row['benchmark_family']} at {margin_pp} pp, {percentile}: "
                f"table says {expected}, formula gives {recomputed}"
            )
            checked += 1
    assert checked == len(rows) * 3


def test_paper_table_values_are_what_the_lookup_returns():
    for family, expected in PAPER_AT_2PP.items():
        row = required_n_for_benchmark(family, 2.0)
        assert row.required_n("median") == expected, family


def test_lookup_returns_the_ordered_quartiles():
    row = required_n_for_benchmark("mmlu", 2.0)
    assert isinstance(row, RequiredN)
    assert row.required_n("p25") <= row.required_n("median") <= row.required_n("p75")
    assert row.discordance("p25") <= row.discordance("median") <= row.discordance("p75")


def test_requirement_is_quadratic_in_the_margin():
    # The paper: "a claim of parity within 1 pp is four times as expensive to
    # certify as parity within 2 pp." Halving the margin quadruples the count,
    # up to the ceiling.
    tight = required_n_for_benchmark("mmlu", 1.0).required_n("median")
    registered = required_n_for_benchmark("mmlu", 2.0).required_n("median")
    assert tight == pytest.approx(4 * registered, rel=0.01)


def test_churn_not_difficulty_sets_the_requirement():
    # The section's main conceptual point: GPQA is the harder benchmark by
    # baseline accuracy and needs FEWER items, because it churns less.
    mmlu = required_n_for_benchmark("mmlu", 2.0)
    gpqa = required_n_for_benchmark("gpqa", 2.0)
    assert gpqa.median_baseline_accuracy < mmlu.median_baseline_accuracy
    assert gpqa.discordance("median") < mmlu.discordance("median")
    assert gpqa.required_n("median") < mmlu.required_n("median")


def test_pooled_row_is_reachable_by_its_aliases():
    canonical = required_n_for_benchmark("ALL (pooled)", 2.0)
    for alias in ("all", "pooled", "  Pooled  ", "overall"):
        assert required_n_for_benchmark(alias, 2.0).required_n("median") == canonical.required_n(
            "median"
        )


def test_family_names_are_matched_case_and_separator_insensitively():
    canonical = required_n_for_benchmark("arc_challenge", 2.0).required_n("median")
    for spelling in ("ARC_Challenge", "arc-challenge", " arc_challenge "):
        assert required_n_for_benchmark(spelling, 2.0).required_n("median") == canonical


def test_unknown_family_names_what_is_available():
    with pytest.raises(ValueError, match="unknown benchmark family"):
        required_n_for_benchmark("humaneval", 2.0)
    with pytest.raises(ValueError) as excinfo:
        required_n_for_benchmark("humaneval", 2.0)
    assert "mmlu" in str(excinfo.value)


def test_subtasks_are_not_silently_mapped_to_their_family():
    # mmlu_pro is its own family, not a variant of mmlu, and a caller who types
    # a subject name must not receive the parent's row.
    with pytest.raises(ValueError, match="unknown benchmark family"):
        required_n_for_benchmark("mmlu_abstract_algebra", 2.0)


def test_off_table_margin_is_refused_rather_than_interpolated():
    with pytest.raises(ValueError, match="computed at margins"):
        required_n_for_benchmark("mmlu", 2.5)


def test_margin_in_the_wrong_unit_is_caught():
    # 0.02 is the proportion form; passing it here would silently ask for a
    # 0.02-point margin and return a requirement 10,000x too large.
    with pytest.raises(ValueError, match="PERCENTAGE POINTS"):
        required_n_for_benchmark("mmlu", 0.02)
    with pytest.raises(ValueError):
        required_n_for_benchmark("mmlu", 0.0)
    with pytest.raises(ValueError):
        required_n_for_benchmark("mmlu", -2.0)
    with pytest.raises(TypeError):
        required_n_for_benchmark("mmlu", "2.0")


def test_required_n_from_discordance_matches_the_papers_worked_example():
    # paper/sections/certification.tex worked example: MMLU at typical
    # discordance needs 2,164 items at 2 pp, 8,656 at 1 pp, 962 at 3 pp.
    discordance = required_n_for_benchmark("mmlu", 2.0).discordance("median")
    assert required_n_from_discordance(discordance, 2.0) == 2164
    assert required_n_from_discordance(discordance, 1.0) == 8656
    assert required_n_from_discordance(discordance, 3.0) == 962


def test_required_n_from_discordance_validates_its_inputs():
    with pytest.raises(ValueError, match=r"rate in \[0, 1\]"):
        required_n_from_discordance(1.5, 2.0)
    with pytest.raises(ValueError, match=r"rate in \[0, 1\]"):
        required_n_from_discordance(-0.01, 2.0)
    with pytest.raises(ValueError, match="margin_pp must be positive"):
        required_n_from_discordance(0.1, 0.0)
    with pytest.raises(ValueError, match="alpha"):
        required_n_from_discordance(0.1, 2.0, alpha=1.0)
    with pytest.raises(ValueError, match="power"):
        required_n_from_discordance(0.1, 2.0, power=0.0)


def test_zero_discordance_does_not_divide_by_zero():
    # Two models that never disagree have no paired variance. The planning
    # count collapses to one item rather than raising or returning zero.
    assert required_n_from_discordance(0.0, 2.0) == 1


def test_percentile_names_are_checked():
    row = required_n_for_benchmark("mmlu", 2.0)
    with pytest.raises(ValueError, match="percentile must be one of"):
        row.required_n("p50")
    with pytest.raises(ValueError, match="percentile must be one of"):
        row.discordance("mean")


def test_table_covers_eleven_families_plus_the_pooled_row_at_three_margins():
    # paper/sections/certification.tex: "Eleven benchmark families plus the
    # pooled row", at margins 1, 2 and 3 pp.
    families = available_benchmarks()
    assert len(families) == 12
    assert any(name.lower().startswith("all") for name in families)
    assert available_margins_pp() == [1.0, 2.0, 3.0]


def test_loading_a_non_table_says_so():
    with pytest.raises(FileNotFoundError, match="certification table not found"):
        load_certification_table("/nonexistent/certification.csv")


def test_loading_a_csv_with_the_wrong_schema_names_the_missing_columns(tmp_path):
    wrong = tmp_path / "not_a_table.csv"
    wrong.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing column"):
        load_certification_table(wrong)


def test_format_required_n_states_the_planning_caveat():
    text = format_required_n(required_n_for_benchmark("mmlu", 2.0))
    assert "2164" in text
    # The count is a planning size, and the block must not read as a verdict.
    assert "true difference zero" in text
    assert "the test still has to be run and to pass" in text


def test_independent_binomial_column_is_larger_than_the_paired_requirement():
    # The paired advantage is the point of the naive column: ignoring pairing
    # always costs items, never saves them.
    for row in load_certification_table():
        assert row.required_n_independent_binomial > row.required_n_median
        assert row.paired_advantage_at_median > 1.0
