import math

import numpy as np
import pytest

from flipeval import compare, paired_seed_bootstrap, rank_stability
from flipeval.core import draw_two_level_indices


def _records(correct, predictions=None, method=None):
    predictions = predictions or [str(int(value)) for value in correct]
    return [
        {"item_id": str(i), "prediction": predictions[i], "correct": value, **({"method": method} if method else {})}
        for i, value in enumerate(correct)
    ]


def test_hand_computed_pair_b3_c5():
    base = [True] * 10 + [False] * 10
    method = [False] * 3 + [True] * 7 + [True] * 5 + [False] * 5
    result = compare(_records(base), _records(method), bootstrap=100, seed=4)
    assert result.mcnemar_b_harmful == 3
    assert result.mcnemar_c_beneficial == 5
    assert result.harmful_flip_rate == pytest.approx(3 / 20)
    assert result.beneficial_flip_rate == pytest.approx(5 / 20)
    assert result.accuracy_state_churn == pytest.approx(8 / 20)
    assert result.net_accuracy_delta == pytest.approx(2 / 20)


@pytest.mark.parametrize(
    "base,method,p",
    [([True] * 5, [True] * 5, 1.0), ([True, False] * 5, [False, True] * 5, 1.0), ([True], [False], 1.0)],
)
def test_degenerate_flip_cases(base, method, p):
    result = compare(_records(base), _records(method), bootstrap=10)
    assert result.mcnemar_p == pytest.approx(p)


def test_tost_equivalent_and_not_equivalent():
    base = [True, False] * 50
    method = [False, True] * 50
    assert compare(_records(base), _records(method), margin=0.5, bootstrap=10).tost_equivalent
    assert not compare(_records(base), _records(method), margin=0.01, bootstrap=10).tost_equivalent


def test_bootstrap_is_deterministic():
    base = _records([True, False] * 10)
    method = _records([False, False, True, True] * 5)
    assert compare(base, method, bootstrap=100, seed=17).confidence_intervals == compare(
        base, method, bootstrap=100, seed=17
    ).confidence_intervals


def test_rank_stability_is_deterministic():
    baseline = _records([False] * 20)
    first = _records([True] * 11 + [False] * 9, method="a")
    second = _records([True] * 10 + [False] * 10, method="b")
    one = rank_stability([first, second], baseline, bootstrap=100, seed=9)
    two = rank_stability([first, second], baseline, bootstrap=100, seed=9)
    assert one == two
    assert one.full_sample_winner == "a"


def test_paired_seed_bootstrap_is_deterministic_and_reports_variance_components():
    first = {
        0: _records([True, True, True, False], method="gptq"),
        1: _records([True, True, False, False], method="gptq"),
    }
    second = {
        0: _records([True, True, False, False], method="awq"),
        1: _records([True, False, False, False], method="awq"),
    }
    one = paired_seed_bootstrap(
        first,
        second,
        bootstrap=200,
        seed=11,
        expected_seed_count=2,
    )
    two = paired_seed_bootstrap(
        first,
        second,
        bootstrap=200,
        seed=11,
        expected_seed_count=2,
    )
    assert one == two
    assert one.seed_labels == ("0", "1")
    assert one.n_items_per_seed == {"0": 4, "1": 4}
    assert one.full_sample_accuracies == {"gptq": 0.625, "awq": 0.375}
    assert one.full_sample_accuracy_delta == pytest.approx(0.25)
    assert one.full_sample_winner == "gptq"
    assert one.seed_level_accuracy_sd["gptq"] == pytest.approx(math.sqrt(0.03125))
    assert one.seed_level_accuracy_sd["awq"] == pytest.approx(math.sqrt(0.03125))
    assert one.item_level_se_by_seed["0"]["gptq"] == pytest.approx(0.25)
    assert one.per_seed["0"].confidence_intervals["accuracy_delta"]


def test_paired_seed_bootstrap_reports_exact_ties_without_calling_them_flips():
    records = {
        0: _records([True, False, True, False]),
        1: _records([False, True, False, True]),
    }
    result = paired_seed_bootstrap(records, records, bootstrap=50, seed=3)
    assert result.full_sample_winner is None
    assert result.joint_rank_flip_rate is None
    assert result.joint_exact_tie_rate == 1.0
    assert all(seed_result.rank_flip_rate is None for seed_result in result.per_seed.values())
    assert all(seed_result.exact_tie_rate == 1.0 for seed_result in result.per_seed.values())


def test_paired_seed_bootstrap_fails_closed_on_seed_or_item_mismatch():
    records = {0: _records([True, False]), 1: _records([False, True])}
    with pytest.raises(ValueError, match="seed labels do not match"):
        paired_seed_bootstrap(records, {0: records[0]})

    mismatched = {0: deepcopy_records(records[0]), 1: deepcopy_records(records[1])}
    mismatched[1][1]["item_id"] = "different"
    with pytest.raises(ValueError, match="item_id sets differ"):
        paired_seed_bootstrap(records, mismatched)

    cross_seed_mismatch = {0: deepcopy_records(records[0]), 1: deepcopy_records(records[1])}
    for record in cross_seed_mismatch[1]:
        record["item_id"] = f"x-{record['item_id']}"
    with pytest.raises(ValueError, match="differs from the other seeds"):
        paired_seed_bootstrap(cross_seed_mismatch, cross_seed_mismatch)


def test_two_level_draw_resamples_repeated_seed_occurrences_independently():
    class StubRng:
        def __init__(self):
            self.values = [
                np.array([1, 1]),
                np.array([0, 1, 1]),
                np.array([2, 2, 1]),
            ]

        def integers(self, *args):
            return self.values.pop(0)

    draws = list(draw_two_level_indices(2, 3, 1, StubRng()))
    seed_positions, item_draws = draws[0]
    assert seed_positions.tolist() == [1, 1]
    assert item_draws[0].tolist() == [0, 1, 1]
    assert item_draws[1].tolist() == [2, 2, 1]


def deepcopy_records(records):
    return [dict(record) for record in records]
