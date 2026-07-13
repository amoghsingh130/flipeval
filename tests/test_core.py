import math

import pytest

from flipeval import compare, rank_stability


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
