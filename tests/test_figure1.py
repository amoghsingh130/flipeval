"""Tests for the flagship Figure 1 generator.

Two jobs, kept separate on purpose.

SOURCE VALUES: every number the figure shows must equal what the canonical
artifact stores. These tests read the artifacts independently of the generator,
so a generator that silently reads the wrong key fails here rather than shipping
a wrong figure. This matters more than usual because the figure CANNOT BE
RENDERED on this project's machines (no LaTeX on the login node or in the pinned
image, probe job 11675341), so nobody will catch a wrong number by looking at it.

DERIVED VALUES: the identities that make the figure's argument (net is the
difference of the two flip rates, churn is their sum, the planning requirement
comes from the project's own implementation) are asserted rather than assumed.

The sign convention is the highest-risk item and gets its own test. flipeval's
compute_pair_metrics defines net_accuracy_delta as method minus baseline and
harmful as base & ~method, so the direction of every item-level quantity depends
on which method occupies the baseline role. Getting it backwards would invert
the figure's central claim while leaving every magnitude correct.
"""
from __future__ import annotations

import csv
import json
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_stats  # noqa: E402
import make_figure1  # noqa: E402

CELL = "qwen25-7b/gsm8k"


@pytest.fixture(scope="module")
def data():
    return make_figure1.collect_values()


@pytest.fixture(scope="module")
def values(data):
    return {name: entry["value"] for name, entry in data["values"].items()}


@pytest.fixture(scope="module")
def supporting():
    return json.loads(
        (ROOT / "results/minigrid_supporting/minigrid_supporting.json").read_text()
    )


@pytest.fixture(scope="module")
def seeds():
    return json.loads(
        (ROOT / "results/h3_eight_cell/paired_seeds_qwen25-7b_gsm8k.json").read_text()
    )


@pytest.fixture(scope="module")
def h3():
    return json.loads(
        (ROOT / "results/h3_eight_cell/h3_eight_cell_summary.json").read_text()
    )


# --------------------------------------------------------------------------
# Source values, read independently of the generator.
# --------------------------------------------------------------------------


def test_panel_a_accuracies_match_artifact(values, seeds):
    assert values["acc_gptq"] == seeds["full_sample_accuracies"]["gptq"]
    assert values["acc_awq"] == seeds["full_sample_accuracies"]["awq"]
    assert values["gap_gptq_minus_awq"] == seeds["full_sample_accuracy_delta"]


def test_panel_a_gap_is_the_difference_of_the_two_accuracies(values):
    assert values["gap_gptq_minus_awq"] == pytest.approx(
        values["acc_gptq"] - values["acc_awq"], abs=1e-12
    )


def test_panel_b_flip_rates_match_artifact(values, supporting):
    cell_mean = supporting["slot4_flip_statistics"][CELL]["cell_mean"]
    assert values["harmful"] == cell_mean["harmful_flip_rate"]
    assert values["beneficial"] == cell_mean["beneficial_flip_rate"]
    assert values["churn"] == cell_mean["accuracy_state_churn"]
    assert values["answer_churn"] == cell_mean["total_answer_churn"]


def test_panel_d_seed_deltas_match_artifact(values, seeds):
    stored = [seeds["per_seed"][s]["accuracy_delta"] for s in seeds["seed_labels"]]
    assert values["seed_deltas_gptq_minus_awq"] == stored
    assert len(stored) == 5


def test_grid_level_counts_match_artifact(values, h3):
    assert values["n_cells_winner_flip"] == h3["n_cells_winner_flip"]
    assert values["n_cells_total"] == len(h3["cells"]) == 8
    assert values["h3_verdict"] == h3["verdict"]


def test_atlas_context_matches_committed_summary(values):
    stats = {}
    with (ROOT / "results/identical_score_churn_rev2.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row.get("statistic"):
                stats[row["statistic"]] = row["value"]
            if row.get("statistic") == "churn_median_nonzero_only":
                break
    assert values["atlas_cells"] == int(stats["analysable_cells"])
    assert values["atlas_zero_delta"] == int(stats["zero_delta_cells"])
    assert values["atlas_zero_delta_nonzero_churn"] == int(
        stats["zero_delta_nonzero_churn_cells"]
    )
    # The zero-delta subset is a subset, and the caption says so.
    assert values["atlas_zero_delta_nonzero_churn"] <= values["atlas_zero_delta"]
    assert values["atlas_zero_delta"] <= values["atlas_cells"]


def test_margin_matches_the_generated_denominator_ledger():
    """The figure's margin must be the one the audit registered.

    paper/audit_denominators.tex is generated from the sealed rev-3 verdict CSV,
    so it is the single place the registered margin is recorded for the paper.
    A figure quoting a different margin than the audit would be incoherent.
    """
    ledger = (ROOT / "paper/audit_denominators.tex").read_text()
    assert r"\newcommand{\AuditMarginPP}{2}" in ledger
    assert make_figure1.MARGIN_PP == 2.0


# --------------------------------------------------------------------------
# Derived values.
# --------------------------------------------------------------------------


def test_net_delta_is_beneficial_minus_harmful(values):
    assert values["net_awq_minus_gptq"] == pytest.approx(
        values["beneficial"] - values["harmful"], abs=1e-12
    )


def test_churn_is_beneficial_plus_harmful(values):
    assert values["churn"] == pytest.approx(
        values["beneficial"] + values["harmful"], abs=1e-12
    )


def test_churn_dwarfs_the_aggregate_gap(values):
    """The figure's whole claim, as an assertion rather than a picture."""
    assert values["churn"] > 20 * abs(values["gap_gptq_minus_awq"])


def test_answer_churn_is_at_least_correctness_churn(values):
    """An answer can change without changing correctness, never the reverse."""
    assert values["answer_churn"] >= values["churn"]


def test_planning_requirement_comes_from_project_code(values):
    """Panel C must be the project's own computation, not a copied number."""
    sd = audit_stats.paired_flip_sd(values["discordance"])
    assert values["paired_sd"] == sd
    assert values["required_n"] == audit_stats.required_n_for_tost(sd, 0.02)
    # Pinned, so a change in the statistics is a visible test failure rather
    # than a silently different figure.
    assert values["required_n"] == 2730
    assert values["n_items"] == 1000


def test_paired_sd_agrees_with_the_committed_record(values):
    """The generator's sd must equal the one sealed in the supporting JSON."""
    assert values["paired_sd"] == pytest.approx(values["step5_paired_sd"], abs=1e-12)


def test_evaluation_falls_short_of_the_requirement(values):
    """Panel C's conclusion, asserted rather than eyeballed."""
    assert values["n_items"] < values["required_n"]


def test_reversal_discordance_is_below_the_observed_rate(values):
    """Why the shortfall exists: the cell disagrees with itself far too much.

    n=1,000 would suffice only at a discordance below reversal_discordance.
    """
    assert values["reversal_discordance"] < values["discordance"]
    assert values["reversal_discordance"] == pytest.approx(0.0646981, abs=1e-6)


def test_alpha_and_power_are_the_registered_values(values):
    assert values["alpha"] == 0.05
    assert values["power"] == 0.80


def test_seed_deltas_change_sign(values):
    """Panel D exists to show this. If it stops being true, the panel is wrong."""
    deltas = values["seed_deltas_gptq_minus_awq"]
    assert any(d > 0 for d in deltas)
    assert any(d < 0 for d in deltas)


def test_flagship_cell_is_the_most_extreme_of_the_eight(values):
    """The caption claims this. It must stay true or the caption misleads.

    The scope sentence calls the cell the most extreme of the eight; if a later
    artifact revision changed that, the caption would overstate its own honesty.
    """
    total, is_max = values["cell_ratio_rank_of"]
    assert total == 8
    assert is_max is True
    assert values["cell_churn_ratio"] > values["median_churn_ratio"]


def test_atlas_ratio_is_about_five_not_five_point_three(values):
    """Defect D4 guard.

    docs/FLAGSHIP_NARRATIVE_PLAN.md records that the manuscript's 5.3x headline
    divides ROUNDED medians, while the unrounded pooled ratio is 5.40 and the
    two strata give 5.22 and 5.19. The figure therefore says "about five times"
    and must never print 5.3. This test pins the unrounded value so the
    discrepancy stays visible rather than being quietly absorbed.
    """
    assert values["atlas_pooled_ratio"] == pytest.approx(5.40, abs=0.01)
    assert values["atlas_median_churn"] == pytest.approx(0.120, abs=1e-6)
    assert values["atlas_median_abs_net"] == pytest.approx(0.022222, abs=1e-6)


# --------------------------------------------------------------------------
# Emission.
# --------------------------------------------------------------------------


def test_emitted_tikz_is_deterministic(data):
    assert make_figure1.emit_tikz(data) == make_figure1.emit_tikz(data)


def test_emitted_tikz_carries_the_key_numbers(data):
    tex = make_figure1.emit_tikz(data)
    for token in ("74.28", "73.70", "0.58", "9.12", "8.54", "17.66", "28.66",
                  "2{,}730", "1{,}000", "5 of 8", "1{,}707", "145", "128"):
        assert token in tex, token


def test_emitted_tikz_never_prints_the_disputed_ratio(data):
    """Defect D4: the 5.3x headline must not enter a new artifact.

    A bare "5.3" substring is the wrong test: TikZ coordinates legitimately
    contain it (a panel edge sits at x=5.3). What must not appear is 5.3 used
    as a RATIO, so the check targets the ways that would be written.
    """
    tex = make_figure1.emit_tikz(data)
    for spelling in (r"5.3\times", r"$5.3\times$", "5.3 times", r"5.3$\times$",
                     "5.3x", r"5{.}3"):
        assert spelling not in tex, spelling
    # And the honest formulation must be the one present.
    assert "about five times" in tex


def test_caption_states_scope_and_the_major_qualification(data):
    cap = make_figure1.caption(data)
    assert "illustrative example" in cap
    assert "most extreme of the eight" in cap
    assert "planning requirement" in cap
    assert "not that the methods differ" in cap
    assert "observational" in cap


def test_no_em_dashes_anywhere_in_the_output(data):
    """Author style rule, and the project linter enforces it elsewhere."""
    tex = make_figure1.emit_tikz(data)
    assert "—" not in tex
    assert "---" not in tex


def test_generator_requires_both_output_paths(tmp_path):
    """No defaults, following the project's fail-closed rule for scripts."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/make_figure1.py"),
         "--out-tex", str(tmp_path / "f.tex")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "out-json" in (result.stderr + result.stdout)


def test_generator_writes_both_files_and_they_round_trip(tmp_path):
    tex_path = tmp_path / "fig1.tex"
    json_path = tmp_path / "fig1.json"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/make_figure1.py"),
         "--out-tex", str(tex_path), "--out-json", str(json_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert tex_path.exists() and json_path.exists()
    record = json.loads(json_path.read_text())
    # Every recorded value carries its provenance, which is the point of the
    # JSON: the figure is checkable without reading TikZ.
    for name, entry in record["values"].items():
        assert "source" in entry and entry["source"], name
        assert "key" in entry and entry["key"], name


def test_committed_figure_matches_a_fresh_generation(tmp_path):
    """The committed .tex must be what the generator currently produces.

    Without this, the figure and the artifacts drift apart silently, which is
    exactly the failure the project's stale-claim linter exists to prevent for
    prose.
    """
    committed = ROOT / "paper/figures/fig1_cancellation.tex"
    # Deliberately not a skip. CLAUDE.md makes any in-image skip a gate
    # failure, and "the figure is missing" is precisely the condition this
    # test exists to catch.
    assert committed.exists(), "paper/figures/fig1_cancellation.tex is not committed"
    assert committed.read_text() == make_figure1.emit_tikz(make_figure1.collect_values())
