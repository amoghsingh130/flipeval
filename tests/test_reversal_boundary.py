"""Boundary behaviour of the reversal point d*, and what may consume it.

final-checklist §3: "Test exact-boundary, `d* < 0`, `d* = 0`, `d* = 1`, `d* > 1`,
missing-value, and integer-ceiling cases."
final-checklist §4: "Treat unattainable reversal points outside `[0,1]` as stable
classifications rather than passing them to numerical routines."

d* = n * margin^2 / z^2 is the discordance at which required_n_for_tost equals the
claim's own n, so the classification changes across it. Discordance is a rate, so
only d* in [0, 1] names an attainable state of the world. Seven of the eleven
assessable claims have d* above 1: their n is large enough that no discordance the
atlas could impute would put them below the threshold, which is a *stronger*
statement than being above it at the median, and it has to be recorded as one
rather than printed as an impossible rate or handed to sqrt().

The two ends of the interval are unreachable from opposite directions and are
tested that way. d* <= 0 cannot be produced at all: it needs n <= 0 or margin <= 0,
and both are rejected at the door, so the guards are the test. d* > 1 is produced
routinely by real claims, so the consumers are the test.

Complements tests/test_audit_denominators.py, which pins the same stability from
the sealed CSV's text. These tests run the code.
"""
from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import pytest
from scipy import stats

import scripts.audit_verdicts as verdicts
from scripts.audit_stats import (
    ALPHA,
    POWER,
    _median,
    paired_flip_sd,
    required_n_for_tost,
    reversal_discordance,
)
from scripts.audit_verdicts import (
    CLAIM_PROFILES,
    REGISTERED_MARGIN_PP,
    _quantile,
    compute_rows,
)

CLAIM_TABLE = Path("docs/audit_claim_table.csv")
ATLAS_REV2 = Path("results/atlas_cells_summary_rev2.csv")

MARGIN = REGISTERED_MARGIN_PP / 100.0

# Rebuilt with the same operations audit_stats uses, so the identities below are
# exact rather than approximate.
Z_SUM = float(stats.norm.ppf(1 - ALPHA)) + float(stats.norm.ppf(POWER))

# The last n whose d* is still inside the unit interval at the registered margin,
# and the first whose d* leaves it. d* reaches 1 at n = z^2 / margin^2 = 15456.39,
# so the switch falls between these two items.
LAST_ATTAINABLE_N = 15456
FIRST_UNATTAINABLE_N = 15457

R01_N = 1838
R01_D_STAR = 0.118915


def _r01_row(monkeypatch, n):
    """Recompute R01's row with its reported n replaced, everything else intact.

    Substituting the profile rather than reimplementing the branch means these
    tests exercise the real guard in `compute_rows`, at n values no real claim
    happens to sit on.
    """
    base = next(p for p in CLAIM_PROFILES if p.claim_id == "R01")
    monkeypatch.setattr(verdicts, "CLAIM_PROFILES", [replace(base, n=n)])
    return compute_rows(CLAIM_TABLE, ATLAS_REV2)[0]


# ---------------------------------------------------------------------------
# d* < 0 and d* = 0: unreachable, and the guards are why
# ---------------------------------------------------------------------------

def test_d_star_cannot_be_zero_or_negative_because_its_inputs_are_rejected():
    """Both sub-unit endpoints are closed off at the inputs, not downstream.

    d* = n * margin^2 / z^2 is zero only at n = 0 and negative only at n < 0,
    since margin^2 and z^2 are positive. A margin of zero would divide the
    required-n formula by zero instead. Nothing later in the pipeline re-checks
    the sign, so these two guards carry the whole case.
    """
    with pytest.raises(ValueError, match="n must be positive"):
        reversal_discordance(0, MARGIN)
    with pytest.raises(ValueError, match="n must be positive"):
        reversal_discordance(-1838, MARGIN)
    with pytest.raises(ValueError, match="margin must be positive"):
        reversal_discordance(R01_N, 0.0)
    with pytest.raises(ValueError, match="margin must be positive"):
        reversal_discordance(R01_N, -MARGIN)


@pytest.mark.parametrize("n", [1, 250, 728, R01_N, 14042, 42701])
def test_d_star_is_strictly_positive_for_every_admissible_n(n):
    assert reversal_discordance(n, MARGIN) > 0.0


# ---------------------------------------------------------------------------
# The consumers: what may and may not be handed a d*
# ---------------------------------------------------------------------------

def test_paired_flip_sd_accepts_both_endpoints_and_rejects_everything_outside():
    """The numerical routine §4 says unattainable points must not reach.

    [0, 1] is closed on both ends: a d* of exactly 0 or exactly 1 is a rate and
    is accepted. Anything outside raises, which is the failure a blanking bug
    would produce at runtime instead of silently.
    """
    assert paired_flip_sd(0.0) == 0.0
    assert paired_flip_sd(1.0) == 1.0

    for outside in (-1e-12, -0.5, 1.0 + 1e-12, 1.854184, 2.762676):
        with pytest.raises(ValueError, match="discordance must be in"):
            paired_flip_sd(outside)


def test_the_degenerate_zero_discordance_case_stays_finite():
    """d* = 0 is unreachable, but sd = 0 is reachable from a zero-churn atlas
    cell, and both downstream formulas special-case it rather than dividing by
    zero or returning a requirement of zero items."""
    assert required_n_for_tost(0.0, MARGIN) == 1
    from scripts.audit_stats import minimum_detectable_delta

    assert minimum_detectable_delta(0.0, R01_N) == 0.0


def test_d_star_of_exactly_one_is_attainable_yet_the_verdict_guard_is_strict():
    """The `d* = 1` case, and a deliberate conservatism recorded rather than assumed.

    d* reaches exactly 1 when n * margin^2 == z^2. A discordance of 1.0 is a
    legal rate, so `paired_flip_sd` takes it, but the verdict path blanks on
    `d_star < 1.0` and therefore treats exactly 1 as unattainable too. That is
    the implemented convention: it would require every item to flip, and it
    errs toward reporting a stable classification rather than a reversal point
    no evaluation could realise.
    """
    exactly_one = reversal_discordance(1, Z_SUM)
    assert exactly_one == 1.0
    assert paired_flip_sd(exactly_one) == 1.0
    assert not (exactly_one < 1.0)


# ---------------------------------------------------------------------------
# The exact boundary in n, and d* > 1
# ---------------------------------------------------------------------------

def test_the_unit_interval_boundary_falls_between_two_adjacent_n():
    """Exact-boundary: 15,456 items still admit a reversal, 15,457 do not.

    Pinned to the item because the existing coverage brackets it loosely
    (14,042 below, 42,701 above), which cannot detect the boundary moving by a
    few hundred items.
    """
    assert reversal_discordance(LAST_ATTAINABLE_N, MARGIN) < 1.0
    assert reversal_discordance(FIRST_UNATTAINABLE_N, MARGIN) > 1.0
    assert Z_SUM ** 2 / MARGIN ** 2 == pytest.approx(15456.39, abs=0.01)


def test_the_blanking_switch_sits_exactly_on_that_boundary(monkeypatch):
    """Either side of the boundary the classification is the same; only the
    reported reversal point differs. That is what "stable classification rather
    than a numerical routine" has to mean in the output."""
    inside = _r01_row(monkeypatch, LAST_ATTAINABLE_N)
    outside = _r01_row(monkeypatch, FIRST_UNATTAINABLE_N)

    assert inside["reversal_discordance"] == pytest.approx(0.999975, abs=5e-7)
    assert outside["reversal_discordance"] == ""

    assert inside["robustness"] == outside["robustness"] == "robustly above threshold"
    assert inside["verdict"] == outside["verdict"] == "above planning threshold at 2pp"
    assert inside["underpowered_at_p75_discordance"] is False
    assert outside["underpowered_at_p75_discordance"] is False


def test_every_unattainable_reversal_point_is_blanked_and_classified_stable():
    """Over the real population, not a constructed one.

    Seven assessable claims have d* above 1. Each must leave the column empty
    and carry `robustly above threshold`, because a claim whose verdict cannot
    be flipped by any discordance is exactly the stable case. The set is
    asserted non-empty so this cannot pass by matching nothing.
    """
    rows = [r for r in compute_rows(CLAIM_TABLE, ATLAS_REV2) if r["eligible"]]
    unattainable = []
    for row in rows:
        if row["indeterminate"] or not row["n"]:
            continue
        d_star = reversal_discordance(int(row["n"]), MARGIN)
        if d_star <= 1.0:
            assert row["reversal_discordance"] == pytest.approx(round(d_star, 6))
            continue
        unattainable.append(row["claim_id"])
        assert row["reversal_discordance"] == "", row["claim_id"]
        assert row["robustness"] == "robustly above threshold", row["claim_id"]
        assert row["verdict"] == "above planning threshold at 2pp", row["claim_id"]
        # The count of reference cells below an unattainable point is still
        # reported, and is necessarily all of them.
        assert row["tier_cells_below_reversal"] == row["discordance_n_cells"], row["claim_id"]
        assert float(row["frac_tier_cells_below_reversal"]) == 1.0, row["claim_id"]

    assert unattainable == ["R03", "R06", "R08", "R09", "R15", "R16", "R17"]


def test_no_unattainable_reversal_point_ever_reaches_a_numerical_routine(monkeypatch):
    """The §4 requirement, enforced by watching the routine rather than the output.

    Every argument `paired_flip_sd` receives during a full run must be a real
    discordance in [0, 1]. If a future change routed d* into the sd path, the
    call would raise for seven claims; this fails first, and names the value.
    """
    seen: list[float] = []
    real = verdicts.paired_flip_sd

    def recording(discordance):
        seen.append(discordance)
        return real(discordance)

    monkeypatch.setattr(verdicts, "paired_flip_sd", recording)
    rows = compute_rows(CLAIM_TABLE, ATLAS_REV2)

    assert seen, "guard against this passing on an unexercised path"
    for value in seen:
        assert 0.0 <= value <= 1.0, f"paired_flip_sd received {value}, not a rate"

    unattainable = {
        reversal_discordance(int(r["n"]), MARGIN)
        for r in rows if r["n"] and not r["indeterminate"]
        and reversal_discordance(int(r["n"]), MARGIN) > 1.0
    }
    assert unattainable, "guard against an empty comparison set"
    assert not unattainable & set(seen)


# ---------------------------------------------------------------------------
# Integer ceiling
# ---------------------------------------------------------------------------

def test_the_integer_ceiling_places_the_classification_flip_at_d_star():
    """required_n is a ceiling, so `n < required_n` is a step function of d.
    Locating the realised step by bisection must land on d*, which is what makes
    d* the reported reversal point rather than an approximation of one."""
    lo, hi = R01_D_STAR * 0.99, R01_D_STAR * 1.01
    assert R01_N >= required_n_for_tost(paired_flip_sd(lo), MARGIN)
    assert R01_N < required_n_for_tost(paired_flip_sd(hi), MARGIN)

    for _ in range(200):
        mid = (lo + hi) / 2.0
        if R01_N >= required_n_for_tost(paired_flip_sd(mid), MARGIN):
            lo = mid
        else:
            hi = mid

    exact = reversal_discordance(R01_N, MARGIN)
    assert lo == pytest.approx(exact, rel=1e-12)
    # One item of requirement separates the two sides, never more.
    assert required_n_for_tost(paired_flip_sd(hi), MARGIN) == R01_N + 1
    assert required_n_for_tost(paired_flip_sd(lo), MARGIN) == R01_N


def test_the_ceiling_holds_the_requirement_constant_over_a_band_of_d():
    """"Rough by at most one cell of d", made a number.

    Because of the ceiling, every d in a band of relative width 1/n maps to the
    same requirement. That band is why the reported d* is documented as
    approximate, and why 0.118915 is quoted to six places and not more.
    """
    exact = reversal_discordance(R01_N, MARGIN)
    band_bottom = exact * (R01_N - 1) / R01_N

    assert (exact - band_bottom) / exact == pytest.approx(1.0 / R01_N, rel=1e-12)
    for d in (band_bottom * (1 + 1e-9), (band_bottom + exact) / 2.0, exact * (1 - 1e-12)):
        assert required_n_for_tost(paired_flip_sd(d), MARGIN) == R01_N
    assert required_n_for_tost(paired_flip_sd(band_bottom * (1 - 1e-9)), MARGIN) == R01_N - 1

    # And the published value rounds to the six places the registration quotes.
    assert round(exact, 6) == R01_D_STAR


def test_required_n_is_monotone_nondecreasing_across_the_whole_unit_interval():
    """The interval argument in §3 rests on monotonicity in d, so it is checked
    on both closed endpoints and across the range, not only near d*."""
    previous = required_n_for_tost(paired_flip_sd(0.0), MARGIN)
    assert previous == 1
    for step in range(1, 1001):
        current = required_n_for_tost(paired_flip_sd(step / 1000.0), MARGIN)
        assert current >= previous
        previous = current
    assert previous == required_n_for_tost(paired_flip_sd(1.0), MARGIN)
    assert previous == FIRST_UNATTAINABLE_N


# ---------------------------------------------------------------------------
# Missing values
# ---------------------------------------------------------------------------

def test_a_claim_with_no_reported_n_produces_no_reversal_point(monkeypatch):
    """Missing-value: n is the only input d* needs, so an absent n must blank
    the whole block rather than substituting a default or raising."""
    row = _r01_row(monkeypatch, None)

    for column in ("reversal_discordance", "tier_cells_below_reversal",
                   "frac_tier_cells_below_reversal", "underpowered_at_p25_discordance",
                   "underpowered_at_p75_discordance"):
        assert row[column] == "", column
    assert row["n"] == ""
    # The imputation itself still runs, so the atlas columns stay populated.
    assert row["imputed_discordance"] == 0.13
    assert row["discordance_p25"] != "" and row["discordance_p75"] != ""


def test_blocked_claims_never_produce_a_reversal_point_even_with_an_n():
    """R13 (n = 250) and R14 (n = 728) both report an n and are both blocked, so
    assessability gates the reversal point independently of the missing-value
    path above."""
    rows = {r["claim_id"]: r for r in compute_rows(CLAIM_TABLE, ATLAS_REV2)}

    for claim_id in ("R13", "R14"):
        row = rows[claim_id]
        assert row["n"] != "" and row["indeterminate"] is True
        assert row["reversal_discordance"] == ""
        assert row["robustness"] == "indeterminate"


def test_quantile_helpers_refuse_an_empty_distribution():
    """The other missing-value shape: a matched tier with no cells. The matcher
    cannot return one, so these guards are the only thing standing between an
    empty tier and a silent zero for Q1/median/Q3."""
    with pytest.raises(ValueError, match="quantile of empty sequence"):
        _quantile([], 0.25)
    with pytest.raises(ValueError, match="median of empty sequence"):
        _median([])
    assert _quantile([0.42], 0.75) == 0.42
    assert _median([0.42]) == 0.42


def test_a_single_cell_tier_gives_coincident_quartiles_and_one_requirement():
    """Degenerate but attainable: with one matching cell, Q1 = median = Q3, so
    the sensitivity interval collapses to a point and the classification cannot
    be interval-sensitive."""
    values = [0.0725]
    assert _quantile(values, 0.25) == _median(values) == _quantile(values, 0.75)
    need = required_n_for_tost(paired_flip_sd(values[0]), MARGIN)
    assert need == math.ceil((Z_SUM * math.sqrt(values[0]) / MARGIN) ** 2)
