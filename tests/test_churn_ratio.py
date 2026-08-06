"""The churn-to-net-delta ratio, and the zero-denominator policy underneath it.

This number had no generator until 2026-08-05 and rotted twice while it was
only a LaTeX comment: D8 (a median hand-copied as 0.138 for 0.13745229) and D4
(three figures in one sentence under two rounding conventions). These tests are
the second half of the fix. `scripts/churn_ratio.py` computes every value the
paper prints for this quantity; the tests below pin those values, pin the
population against the audit path so the two cannot fork, and pin the *policy*
decisions that the values depend on.

The policy tests matter more than the value tests. A wrong value is visible; a
silently changed convention -- pre-rounding an input, or dropping the zero-delta
cells without saying so -- reproduces a plausible number and hides the defect.
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from scripts.audit_stats import load_atlas_cells
from scripts.churn_ratio import (
    ATLAS_CSV,
    CONTROLLED_JSON,
    PAPER_VALUES,
    Cell,
    ZeroPolicy,
    check,
    load_atlas_population,
    load_controlled_cells,
    median_of_per_cell_ratios,
    per_cell_ratios,
    ratio_of_medians,
    report,
)

ATLAS_CELLS = 1707
S1_CELLS = 1398
S2_CELLS = 309
ZERO_DELTA_CELLS = 145
ZERO_DELTA_WITH_CHURN = 128


@pytest.fixture(scope="module")
def atlas():
    return load_atlas_population(ATLAS_CSV)


@pytest.fixture(scope="module")
def controlled():
    return load_controlled_cells(CONTROLLED_JSON)


@pytest.fixture(scope="module")
def summary():
    return report()


# --------------------------------------------------------------------------
# The registered population. Not a free choice, so it is pinned hardest.
# --------------------------------------------------------------------------

def test_the_population_is_the_registered_1707_cells(atlas):
    assert len(atlas) == ATLAS_CELLS
    assert len([c for c in atlas if c.stratum == "S1"]) == S1_CELLS
    assert len([c for c in atlas if c.stratum == "S2"]) == S2_CELLS
    assert S1_CELLS + S2_CELLS == ATLAS_CELLS


def test_the_population_matches_the_audit_path_cell_for_cell():
    """The two loaders apply the same registered filters and must never fork.

    `scripts/audit_stats.load_atlas_cells` feeds the certification tables and
    the audit verdicts. If one path starts admitting probe cells or excluded
    rows and the other does not, two families of published numbers quietly stop
    describing the same population, and nothing else in the suite would notice.
    """
    assert len(load_atlas_population(ATLAS_CSV)) == len(load_atlas_cells(ATLAS_CSV))


def test_probe_and_excluded_cells_are_never_admitted():
    """1,807 is pipeline accounting; admitting it would inflate every median."""
    with_probes = load_atlas_cells(ATLAS_CSV, include_probe=True)
    assert len(with_probes) > ATLAS_CELLS
    assert len(load_atlas_population(ATLAS_CSV)) == ATLAS_CELLS


# --------------------------------------------------------------------------
# Aggregation 1: ratio of medians. Nothing is dropped, nothing is pre-rounded.
# --------------------------------------------------------------------------

def test_the_pooled_ratio_of_medians_is_five_point_four(summary):
    assert summary["atlas"]["ratio_of_medians"] == pytest.approx(5.4000, abs=5e-5)


def test_the_stratum_ratios_are_the_unrounded_ones(summary):
    """5.22 and 5.19, not the retired 5.27 and 5.33.

    The retired pair came from dividing medians pre-rounded to the 3 dp the
    table happened to print. Both readings support the section's claim that the
    strata sit at the same multiple, but only one convention may be in force,
    and the unrounded pair is also the closer of the two.
    """
    assert summary["atlas_S1"]["ratio_of_medians"] == pytest.approx(5.2232, abs=5e-5)
    assert summary["atlas_S2"]["ratio_of_medians"] == pytest.approx(5.1936, abs=5e-5)


def test_pre_rounding_the_inputs_changes_the_answer(atlas):
    """The exact defect D4 was, demonstrated rather than asserted.

    Rounding the medians to 3 dp first moves S2 from 5.19 to 5.33, which is a
    larger move than the difference between the two strata. That is why the
    convention is fixed in code and printed in the caption.
    """
    s1 = [c for c in atlas if c.stratum == "S1"]
    s2 = [c for c in atlas if c.stratum == "S2"]
    import statistics

    def rounded(cells):
        churn = round(statistics.median([c.churn for c in cells]), 3)
        delta = round(statistics.median([c.abs_net_delta for c in cells]), 3)
        return churn / delta

    assert rounded(s1) == pytest.approx(5.2692, abs=5e-5)
    assert rounded(s2) == pytest.approx(5.3333, abs=5e-5)
    assert abs(rounded(s2) - ratio_of_medians(s2)) > abs(
        ratio_of_medians(s1) - ratio_of_medians(s2)
    )


def test_the_six_printed_decimals_reproduce_the_printed_ratios(summary):
    """tab:atlas-strata prints 6 dp so a reader can divide the cells.

    This is the promise the caption makes. If a future edit trims the table back
    to 3 dp, the caption becomes false and this test says so.
    """
    for stratum, expected in (("atlas_S1", 5.22), ("atlas_S2", 5.19)):
        block = summary[stratum]
        printed = round(block["median_churn"], 6) / round(block["median_abs_net_delta"], 6)
        assert round(printed, 2) == expected


# --------------------------------------------------------------------------
# Aggregation 2, and the zero-denominator policy.
# --------------------------------------------------------------------------

def test_the_zero_delta_cells_are_counted_not_forgotten(summary):
    counts = summary["atlas"]["counts"]
    assert counts["total"] == ATLAS_CELLS
    assert counts["zero_delta"] == ZERO_DELTA_CELLS
    assert counts["zero_delta_with_churn"] == ZERO_DELTA_WITH_CHURN
    assert counts["zero_delta_zero_churn"] == ZERO_DELTA_CELLS - ZERO_DELTA_WITH_CHURN
    assert counts["finite"] + counts["zero_delta"] == ATLAS_CELLS


def test_the_reported_per_cell_median_excludes_exactly_those_cells(summary):
    counts = summary["atlas"]["counts"]
    assert counts["included"] == ATLAS_CELLS - ZERO_DELTA_CELLS == 1562
    assert summary["atlas"]["per_cell_median_exclude"] == pytest.approx(3.8452, abs=5e-5)


def test_readmitting_the_zero_delta_cells_raises_the_ratio(summary):
    """Two medians over two cell sets, and which way the second moves.

    The median among finite cellwise ratios is 3.85; assigning +infinity to the
    128 zero-delta/nonzero-churn cells raises the all-cell median to 4.20. These
    are not a bound and an estimate, they are different statistics over
    different cell sets, and the paper says so in those terms.

    The direction is what is pinned. A cell with churn against an exactly zero
    net delta is the most complete cancellation the atlas contains, so it sorts
    above every finite cell under any convention that keeps it. A future change
    that made the reported figure the *larger* of the two would need explaining,
    and this test is where it surfaces.
    """
    assert summary["atlas"]["per_cell_median_extended"] == pytest.approx(4.2000, abs=5e-5)
    assert summary["atlas"]["per_cell_median_extended"] > summary["atlas"]["per_cell_median_exclude"]


def test_the_extended_policy_drops_only_genuine_zero_over_zero(atlas):
    ratios, counts = per_cell_ratios(atlas, ZeroPolicy.EXTENDED)
    assert len(ratios) == counts["finite"] + counts["zero_delta_with_churn"] == 1690
    assert math.isinf(max(ratios))
    assert sum(1 for r in ratios if math.isinf(r)) == ZERO_DELTA_WITH_CHURN
    # 0/0 is undefined under every convention and is never silently called zero.
    assert counts["zero_delta_zero_churn"] == 17


def test_the_zero_delta_definition_is_the_one_the_paper_already_uses(atlas):
    """Exact equality at 1e-12, matching sec:atlas:identical's 145 cells.

    Two definitions of "zero" in one paper would let the subsection that reports
    145 identical-accuracy cells and the ratio that drops 145 cells disagree
    while both looked right. On this data the strict and tolerant readings pick
    the same cells, and that is a fact worth pinning rather than assuming: no
    atlas cell has a net delta that is non-zero but smaller than 1e-12.
    """
    strict = {c.label for c in atlas if c.abs_net_delta == 0.0}
    tolerant = {c.label for c in atlas if c.abs_net_delta < 1e-12}
    assert strict == tolerant
    assert len(strict) == ZERO_DELTA_CELLS


def test_the_policy_is_the_same_in_both_strata(summary):
    """One rule, applied identically, with the counts reported per stratum.

    The strata differ in how many cells the rule removes (95 of 1,398 against 50
    of 309, so proportionally more of S2), which is a fact about the data and
    exactly why the counts are published rather than the policy varied.
    """
    s1, s2 = summary["atlas_S1"]["counts"], summary["atlas_S2"]["counts"]
    assert s1["zero_delta"] == 95 and s2["zero_delta"] == 50
    assert s1["zero_delta"] + s2["zero_delta"] == ZERO_DELTA_CELLS
    for counts in (s1, s2):
        assert counts["included"] == counts["finite"]
    assert s2["zero_delta"] / s2["total"] > s1["zero_delta"] / s1["total"]


def test_a_ratio_of_medians_never_consults_the_zero_policy():
    """Aggregation 1 has no per-cell denominator, so a zero delta is ordinary.

    Two of these five cells have a zero net delta and the pooled ratio is still
    defined, because only the *median* denominator has to be non-zero. The
    per-cell aggregation over the same cells drops those two.
    """
    cells = [
        Cell("a", "T", churn=0.20, abs_net_delta=0.00),
        Cell("b", "T", churn=0.10, abs_net_delta=0.00),
        Cell("c", "T", churn=0.30, abs_net_delta=0.05),
        Cell("d", "T", churn=0.40, abs_net_delta=0.10),
        Cell("e", "T", churn=0.50, abs_net_delta=0.20),
    ]
    assert ratio_of_medians(cells) == pytest.approx(0.30 / 0.05)
    _, counts = per_cell_ratios(cells, ZeroPolicy.EXCLUDE)
    assert counts["included"] == 3 and counts["zero_delta"] == 2


def test_a_zero_median_denominator_raises_rather_than_returning_infinity():
    """A population that cancels at the median has no ratio, and must say so.

    Returning inf would print as a headline. This is the one place the module is
    allowed to fail loudly instead of producing a number.
    """
    cells = [Cell(str(i), "T", churn=0.2, abs_net_delta=0.0) for i in range(3)]
    with pytest.raises(ZeroDivisionError):
        ratio_of_medians(cells)
    with pytest.raises(ValueError):
        ratio_of_medians([])
    with pytest.raises(ValueError):
        median_of_per_cell_ratios(cells, ZeroPolicy.EXCLUDE)


# --------------------------------------------------------------------------
# The cross-regime comparison, which is only honest if it is like-for-like.
# --------------------------------------------------------------------------

def test_the_controlled_cells_have_no_zero_denominator(summary, controlled):
    """Why the comparison is like-for-like on policy as well as on aggregation.

    All eight controlled cells have a non-zero net delta, so the per-cell
    aggregation drops none of them and the zero policy is vacuous on that side.
    The atlas side drops 145 of 1,707. Stating that difference is what makes the
    two medians comparable rather than merely adjacent.
    """
    assert len(controlled) == 8
    assert summary["controlled"]["counts"]["zero_delta"] == 0
    assert summary["controlled"]["counts"]["included"] == 8


def test_the_direction_holds_under_both_aggregations(summary):
    """The claim does not depend on picking the flattering aggregation.

    Ratio of medians:        atlas 5.40 against controlled 12.14  (2.2x)
    Median of per-cell ratios: atlas 3.85 against controlled 12.71  (3.3x)

    Result 1 quotes the like-for-like pair and gives the other alongside. If a
    future edit ever left only the pairing with the larger contrast, this test
    still requires both to point the same way.
    """
    atlas, controlled = summary["atlas"], summary["controlled"]
    assert controlled["ratio_of_medians"] > atlas["ratio_of_medians"]
    assert controlled["per_cell_median_exclude"] > atlas["per_cell_median_exclude"]
    assert controlled["ratio_of_medians"] == pytest.approx(12.1415, abs=5e-5)
    assert controlled["per_cell_median_exclude"] == pytest.approx(12.7080, abs=5e-5)


def test_the_controlled_range_is_the_one_result_one_quotes(summary):
    assert summary["controlled"]["per_cell_min"] == pytest.approx(3.0372, abs=5e-5)
    assert summary["controlled"]["per_cell_max"] == pytest.approx(30.4483, abs=5e-5)


def test_two_regimes_are_never_eight_cells_against_eight_cells(atlas, controlled):
    """A guard on the framing, not the arithmetic.

    The section says two measured points, one at 1,707 cells and one at 8, and
    explicitly declines to read a curve through them. The asymmetry is the
    reason for that caution, so it is pinned.
    """
    assert len(atlas) == ATLAS_CELLS
    assert len(controlled) == 8


# --------------------------------------------------------------------------
# The README's separate quantity, and the whole-manuscript check.
# --------------------------------------------------------------------------

def test_answer_churn_is_a_different_ratio_from_accuracy_state_churn(summary):
    """The README named this quantity and printed the other one's value.

    Total answer churn against the same denominator is 13.50, not 5.40. Keeping
    both in one report is what makes the naming error visible instead of
    plausible.
    """
    assert summary["atlas"]["answer_churn_ratio_of_medians"] == pytest.approx(13.5000, abs=5e-5)
    assert summary["atlas"]["answer_churn_ratio_of_medians"] > 2 * summary["atlas"]["ratio_of_medians"]


def test_every_value_the_manuscript_prints_reproduces_from_the_artifacts(summary):
    """The gate. A failure here means the paper and the artifacts have diverged."""
    assert check(summary) == []
    assert len(PAPER_VALUES) >= 25


def test_the_check_actually_fails_when_a_value_drifts(summary):
    """A gate that cannot fail is worse than no gate."""
    drifted = {**summary, "atlas": {**summary["atlas"], "ratio_of_medians": 5.3}}
    failures = check(drifted)
    assert len(failures) == 1
    assert "5.4" in failures[0] and "5.3" in failures[0]


def test_the_artifacts_the_ratio_reads_are_committed():
    """results/* is gitignored by default; these two are allowlisted in.

    If either stops being tracked, the number loses its provenance and this
    whole module is computing from a file that no reviewer can obtain.
    """
    assert Path(ATLAS_CSV).is_file()
    assert Path(CONTROLLED_JSON).is_file()
