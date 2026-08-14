"""Tests for the two reviewer-requested figures: before/after, and required-$n$.

Same division of labour as tests/test_figure1.py, and for the same reason:
neither figure can be RENDERED on this project's machines (no LaTeX on the login
node or in the pinned image), so nobody will catch a wrong number by looking at
it. The tests are the only reader these figures get before a reviewer sees them.

SOURCE VALUES are read out of the canonical artifacts independently of the
generator, so a generator that silently reads the wrong key fails here.

THE COMMITTED FILE MUST BE THE GENERATED FILE. Both figures are emitted by a
script and committed; a hand edit to the .tex would survive every other check in
this repository. Each is regenerated in-process and compared against what is on
disk, which is what makes "GENERATED -- DO NOT EDIT BY HAND" enforceable rather
than advisory.

TWO WORDINGS ARE LOAD-BEARING and are asserted rather than trusted:

  * The 2,730 in Figure 2 is a PLANNING requirement computed at an assumed true
    difference of zero. It says the evaluation cannot support the equivalence
    claim. It is NOT evidence that the two methods differ, and a caption that
    let a reader think otherwise would invert the paper's own argument.
  * No committed artifact records a TOST verdict for that cell, so the figure
    must not print one. The interval it draws is the committed 95% paired
    bootstrap interval, which is not the 90% two-sided interval TOST at
    one-sided alpha = .05 requires and therefore decides nothing either way.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import make_figure2  # noqa: E402
import make_figure3  # noqa: E402

FIG2_TEX = ROOT / "paper/figures/fig2_before_after.tex"
FIG2_JSON = ROOT / "paper/figures/fig2_values.json"
FIG3_TEX = ROOT / "paper/figures/fig3_required_n.tex"
FIG3_JSON = ROOT / "paper/figures/fig3_values.json"


@pytest.fixture(scope="module")
def fig2():
    return make_figure2.collect_values()


@pytest.fixture(scope="module")
def v2(fig2):
    return {name: entry["value"] for name, entry in fig2["values"].items()}


@pytest.fixture(scope="module")
def fig3():
    return make_figure3.collect_values()


@pytest.fixture(scope="module")
def v3(fig3):
    return {name: entry["value"] for name, entry in fig3["values"].items()}


@pytest.fixture(scope="module")
def fig1_values():
    return {
        name: entry["value"]
        for name, entry in json.loads(
            (ROOT / "paper/figures/fig1_values.json").read_text()
        )["values"].items()
    }


# --------------------------------------------------------------------------
# Figure 2 -- source values.
# --------------------------------------------------------------------------


def test_fig2_shares_figure_ones_cell_values(v2, fig1_values):
    """Both figures describe the same cell; they must not drift apart."""
    for key in ("harmful", "beneficial", "churn", "n_items", "required_n", "acc_gptq", "acc_awq"):
        assert v2[key] == pytest.approx(fig1_values[key]), key


def test_fig2_churn_is_the_sum_of_the_two_flip_rates(v2):
    assert v2["churn"] == pytest.approx(v2["harmful"] + v2["beneficial"], abs=1e-9)


def test_fig2_net_is_the_difference_of_the_two_flip_rates(v2):
    assert v2["net_awq_minus_gptq"] == pytest.approx(v2["beneficial"] - v2["harmful"], abs=1e-9)


def test_fig2_evaluation_falls_short_of_the_requirement(v2):
    """The figure's whole point: 1,000 items run against 2,730 required."""
    assert v2["n_items"] < v2["required_n"]
    assert v2["n_items"] == 1000
    assert v2["required_n"] == 2730


def test_fig2_audit_counts_equal_the_generated_ledger(v2):
    """The three audit counts must be the ledger's, not hand-typed."""
    ledger = (ROOT / "paper/audit_denominators.tex").read_text(encoding="utf-8")
    assert f"\\newcommand{{\\AuditEligible}}{{{v2['audit_eligible']}}}" in ledger
    assert (
        f"\\newcommand{{\\AuditPerItemTaskMatched}}{{{v2['audit_per_item_task_matched']}}}"
        in ledger
    )


def test_fig2_per_item_release_count_matches_the_artifacts_section(v2):
    """paper/sections/artifacts.tex: 88 cell JSONL files are released."""
    assert v2["per_item_cells_released"] == 88


def test_fig2_confidence_interval_is_symmetric_under_negation(v2):
    low, high = v2["delta_ci_gptq_minus_awq"]
    neg_low, neg_high = v2["delta_ci_awq_minus_gptq"]
    assert neg_low == pytest.approx(-high, abs=1e-12)
    assert neg_high == pytest.approx(-low, abs=1e-12)


# --------------------------------------------------------------------------
# Figure 2 -- emission and the load-bearing wording.
# --------------------------------------------------------------------------


def test_fig2_committed_tex_is_the_generated_tex(fig2):
    assert FIG2_TEX.read_text(encoding="utf-8") == make_figure2.emit_tikz(fig2)


def test_fig2_committed_json_is_the_generated_json(fig2):
    assert json.loads(FIG2_JSON.read_text(encoding="utf-8")) == fig2


def test_fig2_emission_is_deterministic(fig2):
    assert make_figure2.emit_tikz(fig2) == make_figure2.emit_tikz(fig2)


def test_fig2_states_the_requirement_as_a_planning_count(fig2):
    text = make_figure2.emit_tikz(fig2) + make_figure2.caption(fig2)
    assert "planning" in text.lower()
    lowered = text.lower()
    assert "true difference of zero" in lowered or "assumed true difference" in lowered


def test_fig2_never_claims_the_two_methods_differ(fig2):
    """The forbidden reading of the 2,730, stated as a token test."""
    lowered = (make_figure2.emit_tikz(fig2) + make_figure2.caption(fig2)).lower()
    for forbidden in (
        "the methods differ",
        "methods are different",
        "significantly different",
        "proves a difference",
    ):
        assert forbidden not in lowered, forbidden


def test_fig2_prints_no_tost_verdict(fig2):
    """No committed artifact records one for this cell, so none may be shown."""
    lowered = (make_figure2.emit_tikz(fig2) + make_figure2.caption(fig2)).lower()
    for forbidden in ("tost says", "equivalence established", "certified equivalent"):
        assert forbidden not in lowered, forbidden


def test_fig2_carries_the_key_numbers(fig2):
    tex = make_figure2.emit_tikz(fig2)
    for token in ("0.58", "17.66", "2{,}730", "1{,}000"):
        assert token in tex, token


# --------------------------------------------------------------------------
# Figure 3 -- source values.
# --------------------------------------------------------------------------


def test_fig3_order_is_ascending_required_n(v3):
    rows = {
        row["benchmark_family"]: int(row["required_n_median"])
        for row in csv.DictReader(
            (ROOT / "results/certification_tables_rev2.csv").open(encoding="utf-8", newline="")
        )
        if float(row["margin_pp"]) == 2.0
    }
    ordered = v3["family_order"]
    counts = [rows[name] for name in ordered]
    assert counts == sorted(counts)


def test_fig3_makes_the_churn_not_difficulty_point_visible(v3):
    """GPQA is the harder benchmark and sits left of MMLU: fewer items, not more."""
    order = v3["family_order"]
    assert order.index("gpqa") < order.index("mmlu")


def test_fig3_margin_scaling_is_quadratic(v3):
    scaling = v3["margin_scaling"]
    assert scaling["1pp_over_2pp"]["median_of_ratios"] == pytest.approx(4.0, abs=0.01)
    # (2/3)^2 = 0.444...
    assert scaling["3pp_over_2pp"]["median_of_ratios"] == pytest.approx(4 / 9, abs=0.01)


def test_fig3_cross_checks_itself_against_the_papers_table(fig3):
    """The generator re-reads Table 1 out of the .tex and compares; assert it ran."""
    rows = make_figure3.read_csv()
    make_figure3.check_against_table(rows)  # raises if the table and CSV disagree


# --------------------------------------------------------------------------
# Figure 3 -- emission.
# --------------------------------------------------------------------------


def test_fig3_committed_tex_is_the_generated_tex(fig3):
    assert FIG3_TEX.read_text(encoding="utf-8") == make_figure3.emit_tikz(fig3)


def test_fig3_committed_json_is_the_generated_json(fig3):
    assert json.loads(FIG3_JSON.read_text(encoding="utf-8")) == fig3


def test_fig3_emission_is_deterministic(fig3):
    assert make_figure3.emit_tikz(fig3) == make_figure3.emit_tikz(fig3)


def test_fig3_states_the_planning_caveat(fig3):
    caption = make_figure3.caption(fig3).lower()
    assert "planning" in caption or "design" in caption


# --------------------------------------------------------------------------
# Both figures -- house style and preamble compatibility.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("path", [FIG2_TEX, FIG3_TEX])
def test_figures_need_no_package_beyond_the_pinned_preamble(path):
    """paper/main.tex loads tikz + arrows.meta and nothing else these could want.

    A figure that pulled in pgfplots would compile here and fail in the TMLR
    staging tree, where the preamble is converted rather than copied.
    """
    for forbidden in ("\\usepackage", "\\begin{axis}", "pgfplots", "\\usetikzlibrary"):
        for line in _body(path):
            assert forbidden not in line, f"{path.name}: {forbidden}"


def _body(path):
    """The emitted lines, without the generated header comments.

    The header comments deliberately NAME the things the body may not contain
    (the forbidden packages, the retired ratio), so a whole-file scan would
    fail on the very comments that document the rule.
    """
    return [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("%")
    ]


@pytest.mark.parametrize("path", [FIG2_TEX, FIG3_TEX])
def test_figures_use_no_em_dashes(path):
    """Author style rule; Figure 1 set the precedent and its test enforces it."""
    for line in _body(path):
        assert "—" not in line, line
        assert "---" not in line, line


@pytest.mark.parametrize("path", [FIG2_TEX, FIG3_TEX])
def test_figures_never_print_the_retired_atlas_ratio(path):
    """Defect D4: the retired 5.3x headline must not enter a new artifact.

    Matched as the RATIO spellings, not as the bare string "5.3": TikZ
    coordinates are full of numbers like (5.391,5.858), and a substring test
    over those is a false positive that would train the next reader to
    disable this check. A legitimate 5.3 also exists in the certification
    table's ifeval paired-advantage column, which is a different quantity;
    neither figure plots it.
    """
    for line in _body(path):
        for spelling in (r"5.3\times", "5.3 times", "5.3x", "$5.3$"):
            assert spelling not in line, f"{spelling}: {line}"


@pytest.mark.parametrize("path", [FIG2_TEX, FIG3_TEX])
def test_figures_declare_their_generator(path):
    head = path.read_text(encoding="utf-8")[:400]
    assert "GENERATED" in head
    assert "make_figure" in head
