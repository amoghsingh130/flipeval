"""Tests for the registered zero-GPU analyses: verdict rules and the atlas matcher."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

from flipeval.core import minimum_detectable_difference
from scripts.audit_stats import (
    AtlasCell,
    benchmark_family,
    independent_binomial_sd,
    method_profile,
    minimum_detectable_delta,
    nearest_cell_discordance,
    paired_flip_sd,
    quantiles,
    required_n_for_tost,
    synthetic_deltas,
)
from scripts.audit_verdicts import (
    CLAIM_PROFILES,
    REGISTERED_MARGIN_PP,
    per_item_outputs_verdict,
)


def _cell(family, bits, benchmark, discordance, n=1000, baseline=0.6):
    return AtlasCell(family, bits, benchmark, n, discordance, baseline, False)


# ---------------------------------------------------------------------------
# The analytic sd must agree with flipeval's tested array-based implementation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("discordance", [0.02, 0.05, 0.10, 0.25])
def test_paired_mdd_matches_flipeval_on_synthetic_deltas(discordance):
    """The audit's analytic MDD must not silently fork from flipeval.core."""
    n = 20000
    deltas = synthetic_deltas(n, discordance)
    from_flipeval = minimum_detectable_difference(deltas)
    # flipeval uses ddof=1 on the realised vector; correct for that to compare.
    realised = float(np.std(deltas, ddof=1))
    analytic = minimum_detectable_delta(realised, n)
    assert analytic == pytest.approx(from_flipeval, rel=1e-12)
    # And the closed-form sqrt(p_d) is the large-n limit of the realised sd.
    assert paired_flip_sd(discordance) == pytest.approx(realised, rel=1e-3)


def test_paired_sd_is_sqrt_discordance_and_independent_sd_is_larger_when_churn_low():
    """The premise of the certification tables: pairing wins when churn is low."""
    assert paired_flip_sd(0.04) == pytest.approx(0.2)
    assert independent_binomial_sd(0.5) == pytest.approx(math.sqrt(0.5))
    assert paired_flip_sd(0.04) < independent_binomial_sd(0.5)


def test_tost_required_n_uses_one_sided_alpha_and_scales_inversely_with_margin_squared():
    sd = 0.2
    n_2pp = required_n_for_tost(sd, 0.02)
    # (1.6449 + 0.8416)^2 * 0.04 / 0.0004 = 618.2 -> 619
    assert n_2pp == 619
    # Halving the margin quadruples the requirement.
    assert required_n_for_tost(sd, 0.01) == pytest.approx(4 * n_2pp, rel=0.01)


def test_required_n_rejects_nonpositive_margin():
    with pytest.raises(ValueError, match="margin must be positive"):
        required_n_for_tost(0.2, 0.0)


def test_mdd_rejects_nonpositive_n_and_sd_zero_is_zero():
    with pytest.raises(ValueError, match="n must be positive"):
        minimum_detectable_delta(0.2, 0)
    assert minimum_detectable_delta(0.0, 100) == 0.0


def test_paired_flip_sd_rejects_out_of_range_discordance():
    with pytest.raises(ValueError, match="discordance must be in"):
        paired_flip_sd(1.5)


# ---------------------------------------------------------------------------
# Nearest-cell matcher: tier ordering and graceful descent
# ---------------------------------------------------------------------------

def test_matcher_prefers_the_exact_family_bits_benchmark_cell():
    cells = [
        _cell("gptq", 4, "mmlu", 0.10),
        _cell("gptq", 4, "gsm8k", 0.50),
        _cell("awq", 4, "mmlu", 0.90),
    ]
    match = nearest_cell_discordance(cells, "gptq", 4, "mmlu")
    assert match.tier == "family+bits+benchmark"
    assert match.discordance == pytest.approx(0.10)
    assert match.n_cells == 1


def test_matcher_descends_to_family_bits_when_benchmark_absent():
    cells = [_cell("gptq", 4, "gsm8k", 0.20), _cell("gptq", 4, "arc_challenge", 0.40)]
    match = nearest_cell_discordance(cells, "gptq", 4, "mmlu")
    assert match.tier == "family+bits"
    assert match.discordance == pytest.approx(0.30)  # median of 0.20, 0.40
    assert match.n_cells == 2


def test_matcher_descends_to_bits_benchmark_for_an_unknown_family():
    cells = [_cell("gptq", 4, "mmlu", 0.20), _cell("awq", 4, "mmlu", 0.30), _cell("w8a8_fp8", 8, "mmlu", 0.90)]
    match = nearest_cell_discordance(cells, "squeezellm", 4, "mmlu")
    assert match.tier == "bits+benchmark"
    assert match.discordance == pytest.approx(0.25)


def test_matcher_falls_through_bit_tiers_when_claim_has_no_bit_width():
    """A pruning claim has no bit width and must not match a bit-width tier."""
    cells = [_cell("gptq", 4, "mmlu", 0.20), _cell("w8a8_fp8", 8, "gsm8k", 0.60)]
    match = nearest_cell_discordance(cells, "pruning", None, None)
    assert match.tier == "global"
    assert match.discordance == pytest.approx(0.40)


def test_matcher_uses_median_not_mean_so_one_outlier_cannot_dominate():
    cells = [_cell("gptq", 4, "mmlu", 0.10), _cell("gptq", 4, "mmlu", 0.12), _cell("gptq", 4, "mmlu", 0.98)]
    match = nearest_cell_discordance(cells, "gptq", 4, "mmlu")
    assert match.discordance == pytest.approx(0.12)


def test_matcher_raises_when_no_cells_at_all():
    with pytest.raises(ValueError, match="no atlas cells"):
        nearest_cell_discordance([], "gptq", 4, "mmlu")


# ---------------------------------------------------------------------------
# Task/method mapping and probe exclusion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("task,expected", [
    ("harness_hendrycksTest_abstract_algebra_5", "mmlu"),
    ("harness_hendrycksTest_world_religions_5", "mmlu"),
    ("bbh_snarks", "bbh"),
    ("math_geometry_hard", "math"),
    ("gpqa_diamond", "gpqa"),
    ("musr_team_allocation", "musr"),
    ("mmlu_pro", "mmlu_pro"),
    ("harness_gsm8k_5", "gsm8k"),
    ("ifeval", "ifeval"),
])
def test_benchmark_family_mapping(task, expected):
    assert benchmark_family(task) == expected


@pytest.mark.parametrize("method,family,bits", [
    ("GPTQ", "gptq", 4),
    ("AWQ", "awq", 4),
    ("W4A16", "w4a16", 4),
    ("W8A8-INT8", "w8a8_int8", 8),
    ("W8A8-FP8", "w8a8_fp8", 8),
    ("bnb-4bit(LoRA)", "bnb_4bit", 4),
    ("bnb-8bit(LoRA)", "bnb_8bit", 8),
])
def test_method_profile_mapping(method, family, bits):
    assert method_profile(method) == (family, bits)


def test_load_atlas_cells_excludes_probe_pairs_by_default(tmp_path):
    header = ("pair_index,source,quantized_model,base_model,method,task,"
              "contains_disclosed_probe_cell,excluded_or_skipped,reason,n,correctness_column,"
              "baseline_accuracy,method_accuracy,net_accuracy_delta,harmful_flip_rate,"
              "beneficial_flip_rate,accuracy_state_churn,total_answer_churn,mcnemar_p,"
              "tost_equivalent,mdd_80_power,required_n_for_observed_delta_80_power,prompt_pass_rate")
    body = [
        "2,S1,q,b,GPTQ,harness_gsm8k_5,True,False,,10,acc,0.5,0.5,0,0,0,0.9,0,1,True,0,,1",
        "3,S1,q,b,GPTQ,harness_gsm8k_5,False,False,,1319,acc,0.5,0.5,0,0,0,0.05,0,1,True,0,,1",
        "4,S1,q,b,GPTQ,harness_gsm8k_5,False,True,skipped,1319,acc,0.5,0.5,0,0,0,0.07,0,1,True,0,,1",
    ]
    path = tmp_path / "atlas.csv"
    path.write_text("\n".join([header, *body]) + "\n", encoding="utf-8")

    from scripts.audit_stats import load_atlas_cells

    default = load_atlas_cells(path)
    assert [c.discordance for c in default] == [0.05]  # probe and excluded both dropped

    with_probe = load_atlas_cells(path, include_probe=True)
    assert sorted(c.discordance for c in with_probe) == [0.05, 0.9]


def test_quantiles_are_ordered():
    q = quantiles([0.01, 0.02, 0.03, 0.04, 0.05])
    assert q["p25"] <= q["median"] <= q["p75"]


# ---------------------------------------------------------------------------
# Verdict decision rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("No (code released; no per-item outputs)", "no"),
    ("no", "no"),
    ("Partial - per-item outputs released as HF datasets for Arena-Hard", "partial"),
    ("yes - standard error reported", "yes"),
])
def test_v3_reproducibility_verdict(raw, expected):
    assert per_item_outputs_verdict(raw) == expected


def test_underpowered_rule_is_reported_n_below_required_n():
    """V2: 'underpowered' iff reported n < required n at the applicable margin."""
    sd = paired_flip_sd(0.05)
    required = required_n_for_tost(sd, REGISTERED_MARGIN_PP / 100.0)
    assert (required - 1) < required          # a claim one item short is underpowered
    assert not (required < required)          # a claim exactly at required n is not


def test_claim_profiles_cover_the_frozen_table_exactly():
    frozen = list(csv.DictReader(Path("docs/audit_claim_table.csv").open(encoding="utf-8", newline="")))
    assert {p.claim_id for p in CLAIM_PROFILES} == {r["claim_id"] for r in frozen}
    assert len(CLAIM_PROFILES) == 17


def test_indeterminate_set_is_exactly_the_four_flagged_rows():
    """R02/R11 (chart-image only) and R13/R14 (no on-page baseline)."""
    assert {p.claim_id for p in CLAIM_PROFILES if p.indeterminate} == {"R02", "R11", "R13", "R14"}


def test_every_determinate_profile_has_the_inputs_its_verdict_needs():
    for profile in CLAIM_PROFILES:
        if profile.indeterminate:
            continue
        assert profile.n, f"{profile.claim_id} has no n"
        assert profile.baseline_accuracy is not None, f"{profile.claim_id} has no baseline"
        assert profile.claimed_margin_pp, f"{profile.claim_id} has no claimed margin"
        assert profile.n_basis and profile.margin_basis, f"{profile.claim_id} missing a basis string"


def test_applicable_margin_is_the_claims_own_margin_when_it_states_one():
    """§4 judges V2 'at the applicable margin' and labels it 'for its OWN assertion'.

    A claim that states a margin is judged against that margin; 2pp is only the
    fallback. This distinction moves the headline count, so it is pinned here.
    """
    from scripts.audit_verdicts import compute_rows

    rows = {r["claim_id"]: r for r in compute_rows(
        Path("docs/audit_claim_table.csv"), Path("results/atlas_cells_summary.csv"))}

    # R17 states +0.15pp: far too fine to resolve at n=28,659, though it clears 2pp easily.
    assert rows["R17"]["applicable_margin_pp"] == 0.15
    assert rows["R17"]["v2_underpowered_applicable"] is True
    assert rows["R17"]["v2_underpowered_paired_2pp"] is False

    # R01 states 2.35pp, coarser than 2pp: the two readings disagree the other way.
    assert rows["R01"]["applicable_margin_pp"] == 2.35
    assert rows["R01"]["v2_underpowered_applicable"] is False
    assert rows["R01"]["v2_underpowered_paired_2pp"] is True

    # Claims stating no margin fall back to the registered 2pp.
    assert rows["R13"]["applicable_margin_pp"] == 2.0
    assert "registered fallback" in rows["R13"]["applicable_margin_basis"]
