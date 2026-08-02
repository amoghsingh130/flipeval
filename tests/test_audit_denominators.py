"""The rev-3 denominator ledger: arithmetic identities and structural invariants.

Every count here is DERIVED from results/audit_verdicts_rev3.csv by
paper/tools/gen_denominator_macros.py and then compared against the canonical
block of docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md. Asserting 17 - 1 == 16
would be a gate that cannot fail; asserting that the CSV yields 17 candidates,
1 ineligible and 16 eligible, and that those three agree with the registration,
is a gate that fails the moment any of the three moves.

The structural invariant these tests exist to hold is R14. Its reported
n = 728 sits just under the 742 the median imputation requires, so a verdict
rule that looked only at n against n_req would flag it and change K from 1 to 2.
It must stay out of K because it is not assessable at all: its source states no
baseline accuracy, only a chart.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from paper.tools.gen_denominator_macros import (
    CANONICAL,
    CANONICAL_STR,
    VERDICTS,
    VERDICTS_SHA256,
    carries_threshold_verdict,
    is_assessable,
    is_eligible,
    is_indeterminate,
    ledger,
    load,
    render,
    required_n,
    sha256_of,
)

ROOT = Path(__file__).resolve().parents[1]
LEDGER_TEX = ROOT / "paper/audit_denominators.tex"


@pytest.fixture(scope="module")
def rows():
    return load()


@pytest.fixture(scope="module")
def counts(rows):
    return ledger(rows)[0]


@pytest.fixture(scope="module")
def strings(rows):
    return ledger(rows)[1]


@pytest.fixture(scope="module")
def per_claim(rows):
    return ledger(rows)[2]


# ---------------------------------------------------------------------------
# Schema and provenance of the sealed input
# ---------------------------------------------------------------------------

def test_verdicts_csv_matches_its_recorded_digest():
    """The ledger is only as good as the table it reads. This is the same
    digest paper/sections/audit.tex cites for job 11591245."""
    assert sha256_of(VERDICTS) == VERDICTS_SHA256


def test_verdicts_csv_carries_every_column_the_ledger_reads():
    with open(VERDICTS, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    required = {
        "claim_id", "n", "eligible", "eligibility_basis", "indeterminate",
        "indeterminate_kind", "indeterminate_reason", "margin_category",
        "evidence_form", "discordance_match_tier", "discordance_n_cells",
        "discordance_p25", "discordance_p75", "imputed_discordance",
        "reversal_discordance", "tier_cells_below_reversal",
        "frac_tier_cells_below_reversal", "v2_required_n_paired_2pp",
        "v3_per_item_outputs", "verdict", "robustness",
    }
    missing = required - set(header)
    assert not missing, "verdicts CSV is missing %s" % sorted(missing)


def test_every_row_has_a_parseable_boolean_and_a_known_vocabulary(rows):
    for r in rows:
        assert r["eligible"] in {"True", "False"}, r["claim_id"]
        assert r["indeterminate"] in {"True", "False"}, r["claim_id"]
        assert r["v3_per_item_outputs"] in {"yes", "partial", "no"}, r["claim_id"]
        assert r["margin_category"] in {"1", "2", "3"}, r["claim_id"]
        assert r["evidence_form"] in {"generic_adjective", "posthoc_delta"}, r["claim_id"]
        assert r["robustness"] in {
            "robustly above threshold", "robustly below threshold",
            "imputation-sensitive", "indeterminate"}, r["claim_id"]


def test_claim_ids_are_unique_and_match_the_frozen_table(rows):
    ids = [r["claim_id"] for r in rows]
    assert len(ids) == len(set(ids))
    with open(ROOT / "docs/audit_claim_table.csv", newline="", encoding="utf-8") as f:
        frozen = {r["claim_id"] for r in csv.DictReader(f)}
    assert set(ids) == frozen


# ---------------------------------------------------------------------------
# Arithmetic identities, every term derived from the CSV
# ---------------------------------------------------------------------------

def test_seventeen_minus_one_is_sixteen(rows, counts):
    """17 frozen candidates - 1 ineligible = 16 eligible."""
    candidates = len(rows)
    ineligible = sum(1 for r in rows if not is_eligible(r))
    eligible = sum(1 for r in rows if is_eligible(r))
    assert candidates - ineligible == eligible
    assert (candidates, ineligible, eligible) == (
        CANONICAL["FrozenCandidates"], CANONICAL["Ineligible"], CANONICAL["Eligible"])
    assert (counts["FrozenCandidates"], counts["Ineligible"], counts["Eligible"]) == (
        candidates, ineligible, eligible)
    # And the single ineligible row is R10, by name, not by count.
    assert [r["claim_id"] for r in rows if not is_eligible(r)] == [
        CANONICAL_STR["IneligibleClaim"]]


def test_eleven_plus_five_is_sixteen(rows, counts):
    """11 assessable + 5 not assessable = 16 eligible."""
    eligible = [r for r in rows if is_eligible(r)]
    assessable = [r for r in eligible if is_assessable(r)]
    blocked = [r for r in eligible if is_indeterminate(r)]
    assert len(assessable) + len(blocked) == len(eligible)
    assert (len(assessable), len(blocked), len(eligible)) == (
        CANONICAL["Assessable"], CANONICAL["NotAssessable"], CANONICAL["Eligible"])
    assert counts["Assessable"] == len(assessable)
    assert counts["NotAssessable"] == len(blocked)


def test_four_plus_one_is_five(rows, counts):
    """4 insufficiently reported + 1 outside the binary paired-outcome
    framework = 5 not assessable. The 1 is R04, by name."""
    blocked = [r for r in rows if is_eligible(r) and is_indeterminate(r)]
    insufficient = [r for r in blocked
                    if r["indeterminate_kind"] == "insufficient reporting"]
    outside = [r for r in blocked if r["indeterminate_kind"] == "metric-incompatible"]
    assert len(insufficient) + len(outside) == len(blocked)
    assert (len(insufficient), len(outside), len(blocked)) == (
        CANONICAL["NotAssessableInsufficient"],
        CANONICAL["NotAssessableOutsideFramework"],
        CANONICAL["NotAssessable"])
    assert [r["claim_id"] for r in outside] == [CANONICAL_STR["OutsideFrameworkClaim"]]
    # Every blocked row states exactly one primary blocker, non-empty.
    for r in blocked:
        assert r["indeterminate_reason"].strip(), r["claim_id"]


def test_zero_plus_three_plus_thirteen_is_sixteen(rows, counts):
    """0 task-matched + 3 other-task-only + 13 none = 16 eligible per-item
    output releases. The 0 is the finding; the 3 must be disclosed with it."""
    eligible = [r for r in rows if is_eligible(r)]
    matched = [r for r in eligible if r["v3_per_item_outputs"] == "yes"]
    other = [r for r in eligible if r["v3_per_item_outputs"] == "partial"]
    none = [r for r in eligible if r["v3_per_item_outputs"] == "no"]
    assert len(matched) + len(other) + len(none) == len(eligible)
    assert (len(matched), len(other), len(none), len(eligible)) == (
        CANONICAL["PerItemTaskMatched"], CANONICAL["PerItemOtherTaskOnly"],
        CANONICAL["PerItemNone"], CANONICAL["Eligible"])
    assert sorted(r["claim_id"] for r in other) == ["R08", "R15", "R16"]


def test_ten_plus_one_plus_zero_is_eleven(rows, counts):
    """10 above throughout + 1 changes classification within + 0 below
    throughout = 11 assessable, over the atlas-IQR sensitivity interval."""
    assessable = [r for r in rows if is_assessable(r)]
    above = [r for r in assessable if r["robustness"] == "robustly above threshold"]
    sensitive = [r for r in assessable if r["robustness"] == "imputation-sensitive"]
    below = [r for r in assessable if r["robustness"] == "robustly below threshold"]
    assert len(above) + len(sensitive) + len(below) == len(assessable)
    assert (len(above), len(sensitive), len(below), len(assessable)) == (
        CANONICAL["AboveThroughout"], CANONICAL["ChangesWithinIQR"],
        CANONICAL["BelowThroughout"], CANONICAL["Assessable"])
    assert [r["claim_id"] for r in sensitive] == [CANONICAL_STR["SensitiveClaim"]]


def test_margin_crosstab_sums_to_sixteen_both_ways(rows, counts):
    """The reconciliation the canonical block requires: the margin taxonomy and
    'ten of sixteen contain no number at all' are two axes, not one marginal.

    Row totals and column totals must both reach 16, and the prospective row
    must be empty. That empty row is the finding, so it is asserted as zero
    rather than allowed to be absent.
    """
    eligible = [r for r in rows if is_eligible(r)]
    cell = {}
    for cat in ("1", "2", "3"):
        for form in ("generic_adjective", "posthoc_delta"):
            cell[(cat, form)] = sum(
                1 for r in eligible
                if r["margin_category"] == cat and r["evidence_form"] == form)
    assert sum(cell.values()) == len(eligible) == CANONICAL["XtabGrandTotal"]
    row_totals = {cat: cell[(cat, "generic_adjective")] + cell[(cat, "posthoc_delta")]
                  for cat in ("1", "2", "3")}
    col_totals = {form: sum(cell[(cat, form)] for cat in ("1", "2", "3"))
                  for form in ("generic_adjective", "posthoc_delta")}
    assert sum(row_totals.values()) == len(eligible)
    assert sum(col_totals.values()) == len(eligible)
    assert row_totals["1"] == CANONICAL["ProspectiveNumericMargin"] == 0
    assert col_totals["generic_adjective"] == CANONICAL["XtabQualTotal"]
    assert col_totals["posthoc_delta"] == CANONICAL["XtabRetroTotal"]
    assert counts["XtabSufficientTotal"] == row_totals["2"]
    assert counts["XtabInsufficientTotal"] == row_totals["3"]


def test_margin_category_two_is_not_the_withdrawn_twelve_determinate(rows):
    """Two different sets of size 12, which is exactly how a stale count hides.

    Margin category 2 is the 11 assessable claims plus R04. The withdrawn rev-2
    'twelve determinate' was the 11 assessable claims plus R10. Anything that
    treats the cross-tab row total as a determinacy count is wrong.
    """
    eligible = [r for r in rows if is_eligible(r)]
    cat_two = {r["claim_id"] for r in eligible if r["margin_category"] == "2"}
    assessable = {r["claim_id"] for r in rows if is_assessable(r)}
    assert cat_two == assessable | {"R04"}
    assert "R10" not in cat_two
    assert len(cat_two) == 12 and len(assessable) == 11


# ---------------------------------------------------------------------------
# Structural invariant: a non-assessable row can never carry, or contribute,
# a threshold verdict
# ---------------------------------------------------------------------------

def test_indeterminate_rows_never_carry_a_threshold_verdict(rows):
    """The invariant, over the CSV text itself. An indeterminate row's verdict
    must name its blocker, and its robustness must be 'indeterminate'."""
    for r in rows:
        if is_indeterminate(r):
            assert not carries_threshold_verdict(r), r["claim_id"]
            assert r["verdict"].startswith("indeterminate - "), r["claim_id"]
            assert r["verdict"].endswith(r["indeterminate_kind"]), r["claim_id"]
            assert r["robustness"] == "indeterminate", r["claim_id"]


def test_power_flags_are_populated_on_non_assessable_rows_and_must_be_filtered(rows):
    """The leak this invariant actually has to close, pinned so it cannot drift.

    `verdict` and `robustness` are correctly blanked for indeterminate rows, but
    the raw power-diagnostic columns are NOT: `margin_sensitive` is True for
    R04 and R14, and `v2_underpowered_paired_2pp` is True for R13 and R14,
    because both are computed from n before assessability is consulted. Counted
    unfiltered, either column reports three flagged claims instead of one.

    So the invariant cannot be 'the flag columns are empty'. It is that every
    reported count filters on assessability first. This test states both halves
    so that a future run which blanks the columns, or one which starts counting
    them raw, both fail loudly instead of silently agreeing.
    """
    flagged_raw = {c: sorted(r["claim_id"] for r in rows if r[c] == "True")
                   for c in ("margin_sensitive", "v2_underpowered_paired_2pp")}
    assert flagged_raw["margin_sensitive"] == ["R01", "R04", "R14"]
    assert flagged_raw["v2_underpowered_paired_2pp"] == ["R01", "R13", "R14"]

    for col in ("margin_sensitive", "v2_underpowered_paired_2pp"):
        filtered = sorted(r["claim_id"] for r in rows
                          if is_assessable(r) and r[col] == "True")
        assert filtered == [CANONICAL_STR["SensitiveClaim"]], col
        assert len(filtered) == CANONICAL["BelowThresholdAtMedian"], col
        assert len(flagged_raw[col]) == 3, col   # the count a missing filter gives


def test_no_non_assessable_row_contributes_to_any_threshold_count(rows, counts):
    """Membership, not text. Recomputing every threshold count over the
    assessable rows alone must reproduce the ledger exactly, and recomputing
    over all 17 must not: otherwise the filter is decorative.
    """
    assessable = [r for r in rows if is_assessable(r)]
    assert counts["BelowThresholdAtMedian"] == sum(
        1 for r in assessable if r["verdict"].startswith("below planning threshold"))
    assert counts["AboveThroughout"] == sum(
        1 for r in assessable if r["robustness"] == "robustly above threshold")
    # R10 is ineligible yet its row still carries 'above planning threshold at
    # 2pp' for transparency, so the unfiltered count is genuinely different.
    unfiltered_above = sum(
        1 for r in rows if r["robustness"] == "robustly above threshold")
    assert unfiltered_above == counts["AboveThroughout"] + 1
    assert carries_threshold_verdict(next(r for r in rows if r["claim_id"] == "R10"))
    assert not is_assessable(next(r for r in rows if r["claim_id"] == "R10"))


def test_r14_stays_out_of_k_despite_a_visible_n_below_the_requirement(rows, per_claim):
    """The R14 trap, made executable.

    n = 728 against the 742 the median imputation requires. On n alone R14 is
    short, and the CSV even records v2_underpowered_paired_2pp = True. It is
    still not in K, because assessability is decided before the comparison is
    consulted: R14's source states no baseline accuracy, only a chart.
    """
    r14 = next(r for r in rows if r["claim_id"] == "R14")

    # The trap is real: the naive comparison does fire.
    assert int(r14["n"]) == 728
    assert int(r14["v2_required_n_paired_2pp"]) == 742
    assert int(r14["n"]) < int(r14["v2_required_n_paired_2pp"])
    assert r14["v2_underpowered_paired_2pp"] == "True"
    assert r14["margin_sensitive"] == "True"

    # And it is disarmed by assessability, not by the numbers.
    assert is_eligible(r14)
    assert is_indeterminate(r14)
    assert not is_assessable(r14)
    assert not carries_threshold_verdict(r14)
    assert r14["robustness"] == "indeterminate"

    # K counts assessable rows only, so R14 cannot move it.
    k = [r["claim_id"] for r in rows
         if is_assessable(r) and r["verdict"].startswith("below planning threshold")]
    assert k == [CANONICAL_STR["SensitiveClaim"]]
    assert "R14" not in k

    # The ledger must be able to explain the exclusion, since a visible n
    # invites the question. The blocker text is required, not optional.
    assert per_claim["R14"]["blocker"] == "no baseline accuracy stated (Figure 8 chart only)"
    assert per_claim["R14"]["kind"] == "insufficient reporting"
    assert "cls" not in per_claim["R14"]


def test_every_non_assessable_claim_reaches_the_ledger_with_a_blocker(per_claim, rows):
    """final-checklist §5 lists the five non-assessable claims separately with
    exact blockers, so no non-assessable claim may reach the paper blank."""
    blocked = [r["claim_id"] for r in rows if is_eligible(r) and is_indeterminate(r)]
    assert len(blocked) == CANONICAL["NotAssessable"]
    for cid in blocked + [CANONICAL_STR["IneligibleClaim"]]:
        assert per_claim[cid]["blocker"].strip(), cid
        assert per_claim[cid]["kind"].strip(), cid
        assert "cls" not in per_claim[cid], cid


# ---------------------------------------------------------------------------
# R01, the one sensitive claim, and the per-claim table feed
# ---------------------------------------------------------------------------

def test_r01_values_are_derived_and_match_the_registration(strings, per_claim):
    for key, want in CANONICAL_STR.items():
        assert strings[key] == want, key
    assert per_claim["R01"]["n"] == CANONICAL_STR["SensitiveN"]
    assert per_claim["R01"]["nreqMed"] == CANONICAL_STR["SensitiveNReq"]
    assert per_claim["R01"]["dstar"] == CANONICAL_STR["SensitiveReversalD"]
    assert per_claim["R01"]["cls"] == "changes classification within IQR"


def test_r01_is_short_at_the_median_and_the_fraction_is_descriptive(rows):
    r01 = next(r for r in rows if r["claim_id"] == "R01")
    assert int(r01["n"]) < int(r01["v2_required_n_paired_2pp"])
    below = int(r01["tier_cells_below_reversal"])
    total = int(r01["discordance_n_cells"])
    assert below == 345 and total == 792
    # 43.6% is below/total, a count of reference cells. If it were ever a
    # probability it would have to come from somewhere other than this ratio.
    assert round(100.0 * below / total, 1) == 43.6
    assert abs(float(r01["frac_tier_cells_below_reversal"]) - below / total) < 5e-5


def test_required_n_is_monotone_so_q1_and_q3_bracket_the_interval(rows):
    """The interval claim rests on monotonicity, not on the scatter of cells.
    Q1 <= median <= Q3 in d must give n_req(Q1) <= n_req(median) <= n_req(Q3)."""
    for r in rows:
        if not is_assessable(r):
            continue
        q1, q3 = float(r["discordance_p25"]), float(r["discordance_p75"])
        assert q1 <= q3, r["claim_id"]
        assert required_n(q1) <= required_n(q3), r["claim_id"]
        med = int(r["v2_required_n_paired_2pp"])
        assert required_n(q1) <= med <= required_n(q3), r["claim_id"]


def test_per_claim_feed_covers_every_column_the_appendix_table_needs(per_claim, rows):
    """final-checklist §5: reported n, imputation stratum, n_req at Q1/median/Q3,
    attainable d*, and classification, for all 11 assessable claims."""
    assessable = [r["claim_id"] for r in rows if is_assessable(r)]
    assert len(assessable) == CANONICAL["Assessable"]
    for cid in assessable:
        entry = per_claim[cid]
        for field in ("n", "tier", "nreqQOne", "nreqMed", "nreqQThree", "dstar", "cls"):
            assert field in entry and entry[field].strip(), (cid, field)
        assert entry["tier"] in {"family+bits", "bits", "bits+benchmark",
                                 "family+bits+benchmark"}, cid
        # An unattainable reversal point renders as the no-value cell, never
        # as a number outside [0, 1] handed to a reader as if it were one.
        if entry["dstar"] != "---":
            assert 0.0 <= float(entry["dstar"]) <= 1.0, cid


def test_all_seventeen_claims_reach_the_ledger(per_claim, rows):
    assert set(per_claim) == {r["claim_id"] for r in rows}
    assert len(per_claim) == CANONICAL["FrozenCandidates"]


# ---------------------------------------------------------------------------
# The committed ledger file
# ---------------------------------------------------------------------------

def test_committed_ledger_is_what_the_generator_produces(rows):
    """Same gate as --check layer 3, run by the suite so a hand edit to the
    .tex cannot survive a test run."""
    counts, strings, per_claim = ledger(rows)
    assert LEDGER_TEX.exists(), "run gen_denominator_macros.py --write"
    assert LEDGER_TEX.read_text(encoding="utf-8") == render(counts, strings, per_claim) + "\n"


def test_committed_ledger_defines_every_canonical_macro():
    text = LEDGER_TEX.read_text(encoding="utf-8")
    for key in list(CANONICAL) + list(CANONICAL_STR):
        assert (r"\newcommand{\Audit%s}" % key) in text, key


def test_committed_ledger_contains_no_em_dash_and_no_raw_section_sign():
    """House style: no em dashes in paper sources. The '---' cells are LaTeX
    'no value' notation and are intentional, so only the real U+2014 is
    forbidden. A raw U+00A7 would break a non-unicode TeX run."""
    text = LEDGER_TEX.read_text(encoding="utf-8")
    assert "—" not in text
    assert "§" not in text
