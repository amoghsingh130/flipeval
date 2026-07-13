from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import stats

Record = Mapping[str, Any]


@dataclass(frozen=True)
class ComparisonResult:
    n: int
    baseline_accuracy: float
    method_accuracy: float
    net_accuracy_delta: float
    harmful_flip_rate: float
    beneficial_flip_rate: float
    accuracy_state_churn: float
    wrong_to_different_wrong_churn: float
    total_answer_churn: float
    confidence_intervals: dict[str, tuple[float, float]]
    mcnemar_b_harmful: int
    mcnemar_c_beneficial: int
    mcnemar_p: float
    tost_equivalent: bool
    tost_p_low: float
    tost_p_high: float
    mdd_80_power: float
    required_n_for_observed_delta_80_power: int | None

    def to_dict(self, *, flatten_cis: bool = False) -> dict[str, Any]:
        result = asdict(self)
        if flatten_cis:
            cis = result.pop("confidence_intervals")
            for name, (low, _high) in cis.items():
                result[f"{name}_ci_low"] = low
            for name, (_low, high) in cis.items():
                result[f"{name}_ci_high"] = high
        return result


@dataclass(frozen=True)
class RankStabilityResult:
    methods: tuple[str, ...]
    n_common_items: int
    full_sample_winner: str
    rank_flip_rate: float
    deltas: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PerSeedBootstrapResult:
    seed_label: str
    n_items: int
    accuracies: dict[str, float]
    accuracy_delta: float
    confidence_intervals: dict[str, tuple[float, float]]
    full_sample_winner: str | None
    rank_flip_rate: float | None
    exact_tie_rate: float
    item_level_se: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HierarchicalBootstrapResult:
    methods: tuple[str, str]
    seed_labels: tuple[str, ...]
    n_items_per_seed: dict[str, int]
    bootstrap_replicates: int
    rng_seed: int
    alpha: float
    full_sample_accuracies: dict[str, float]
    full_sample_accuracy_delta: float
    full_sample_winner: str | None
    joint_confidence_intervals: dict[str, tuple[float, float]]
    joint_rank_flip_rate: float | None
    joint_exact_tie_rate: float
    seed_level_accuracy_sd: dict[str, float]
    item_level_se_by_seed: dict[str, dict[str, float]]
    per_seed: dict[str, PerSeedBootstrapResult]
    tie_policy: str = "ties-are-reported-separately-and-never-count-as-flips"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compare(
    baseline_records: Sequence[Record],
    method_records: Sequence[Record],
    margin: float = 0.02,
    bootstrap: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
) -> ComparisonResult:
    base, method = _align_pair(baseline_records, method_records)
    return _compare_arrays(base, method, margin, bootstrap, np.random.default_rng(seed), alpha)


def rank_stability(
    list_of_method_records: Sequence[Sequence[Record]],
    baseline_records: Sequence[Record] | None = None,
    bootstrap: int = 1000,
    seed: int = 0,
    method_names: Sequence[str] | None = None,
) -> RankStabilityResult:
    if len(list_of_method_records) < 2:
        raise ValueError("rank_stability requires at least two methods")
    names = list(method_names) if method_names is not None else [_record_method(r, i) for i, r in enumerate(list_of_method_records)]
    if len(names) != len(list_of_method_records) or len(set(names)) != len(names):
        raise ValueError("method names must be unique and match the record lists")

    method_maps = [_record_map(records) for records in list_of_method_records]
    common_ids = set.intersection(*(set(records) for records in method_maps))
    if baseline_records is not None:
        baseline_map = _record_map(baseline_records)
        common_ids &= set(baseline_map)
    else:
        baseline_map = None
    ids = sorted(common_ids)
    if not ids:
        raise ValueError("record sets have no common item_id values")

    scores: dict[str, np.ndarray] = {}
    for name, records in zip(names, method_maps):
        values = np.array([float(bool(records[item_id]["correct"])) for item_id in ids])
        if baseline_map is not None:
            values -= np.array([float(bool(baseline_map[item_id]["correct"])) for item_id in ids])
        scores[name] = values
    return _rank_stability_arrays(scores, len(ids), bootstrap, np.random.default_rng(seed))


def paired_seed_bootstrap(
    first_records_by_seed: Mapping[Any, Sequence[Record]],
    second_records_by_seed: Mapping[Any, Sequence[Record]],
    *,
    method_names: tuple[str, str] = ("gptq", "awq"),
    bootstrap: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
    expected_seed_count: int | None = None,
) -> HierarchicalBootstrapResult:
    """Paired seed-by-item bootstrap registered for the H3 analysis.

    Seed labels are sampled with replacement. For every sampled occurrence of a
    seed, common item positions are sampled with replacement and applied to both
    methods. Flip and tie rates use all bootstrap replicates as their denominator.
    """
    if len(method_names) != 2 or method_names[0] == method_names[1]:
        raise ValueError("method_names must contain two distinct names")
    if bootstrap <= 0:
        raise ValueError("bootstrap must be positive")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")

    first = _normalize_seed_mapping(first_records_by_seed, "first")
    second = _normalize_seed_mapping(second_records_by_seed, "second")
    if set(first) != set(second):
        missing_first = sorted(set(second) - set(first))
        missing_second = sorted(set(first) - set(second))
        raise ValueError(
            "paired seed labels do not match: "
            f"missing from first={missing_first}, missing from second={missing_second}"
        )
    seed_labels = tuple(sorted(first))
    if not seed_labels:
        raise ValueError("paired_seed_bootstrap requires at least one seed")
    if expected_seed_count is not None and len(seed_labels) != expected_seed_count:
        raise ValueError(f"expected {expected_seed_count} paired seeds, found {len(seed_labels)}")

    arrays: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    canonical_ids: tuple[str, ...] | None = None
    for label in seed_labels:
        first_map = _record_map(first[label])
        second_map = _record_map(second[label])
        first_ids = set(first_map)
        second_ids = set(second_map)
        if first_ids != second_ids:
            raise ValueError(f"item_id sets differ between methods for seed {label!r}")
        ids = tuple(sorted(first_ids))
        if not ids:
            raise ValueError(f"seed {label!r} contains no items")
        if canonical_ids is None:
            canonical_ids = ids
        elif ids != canonical_ids:
            raise ValueError(f"item_id set for seed {label!r} differs from the other seeds")
        arrays[label] = (
            np.array([float(bool(first_map[item_id]["correct"])) for item_id in ids]),
            np.array([float(bool(second_map[item_id]["correct"])) for item_id in ids]),
        )

    assert canonical_ids is not None
    n_items = len(canonical_ids)
    method_a, method_b = method_names
    first_seed_means = np.array([arrays[label][0].mean() for label in seed_labels], dtype=float)
    second_seed_means = np.array([arrays[label][1].mean() for label in seed_labels], dtype=float)
    full_accuracies = {
        method_a: float(first_seed_means.mean()),
        method_b: float(second_seed_means.mean()),
    }
    full_winner = _winner(full_accuracies, method_names)

    child_sequences = np.random.SeedSequence(seed).spawn(len(seed_labels) + 1)
    per_seed: dict[str, PerSeedBootstrapResult] = {}
    for label, child in zip(seed_labels, child_sequences[:-1]):
        per_seed[label] = _per_seed_bootstrap(
            label,
            arrays[label][0],
            arrays[label][1],
            method_names,
            bootstrap,
            np.random.default_rng(child),
            alpha,
        )

    joint_rng = np.random.default_rng(child_sequences[-1])
    accuracy_samples = {method_a: [], method_b: []}
    delta_samples: list[float] = []
    flips = 0
    ties = 0
    for seed_positions, item_draws in draw_two_level_indices(
        len(seed_labels), n_items, bootstrap, joint_rng
    ):
        first_values: list[np.ndarray] = []
        second_values: list[np.ndarray] = []
        for seed_position, item_indices in zip(seed_positions, item_draws):
            label = seed_labels[int(seed_position)]
            first_values.append(arrays[label][0][item_indices])
            second_values.append(arrays[label][1][item_indices])
        first_accuracy = float(np.concatenate(first_values).mean())
        second_accuracy = float(np.concatenate(second_values).mean())
        sampled = {method_a: first_accuracy, method_b: second_accuracy}
        sampled_winner = _winner(sampled, method_names)
        accuracy_samples[method_a].append(first_accuracy)
        accuracy_samples[method_b].append(second_accuracy)
        delta_samples.append(first_accuracy - second_accuracy)
        if sampled_winner is None:
            ties += 1
        elif full_winner is not None and sampled_winner != full_winner:
            flips += 1

    joint_cis = {
        method_a: _quantile_interval(accuracy_samples[method_a], alpha),
        method_b: _quantile_interval(accuracy_samples[method_b], alpha),
        "accuracy_delta": _quantile_interval(delta_samples, alpha),
    }
    seed_sd = {
        method_a: _sample_sd(first_seed_means),
        method_b: _sample_sd(second_seed_means),
    }
    return HierarchicalBootstrapResult(
        methods=method_names,
        seed_labels=seed_labels,
        n_items_per_seed={label: n_items for label in seed_labels},
        bootstrap_replicates=bootstrap,
        rng_seed=seed,
        alpha=alpha,
        full_sample_accuracies=full_accuracies,
        full_sample_accuracy_delta=full_accuracies[method_a] - full_accuracies[method_b],
        full_sample_winner=full_winner,
        joint_confidence_intervals=joint_cis,
        joint_rank_flip_rate=None if full_winner is None else flips / bootstrap,
        joint_exact_tie_rate=ties / bootstrap,
        seed_level_accuracy_sd=seed_sd,
        item_level_se_by_seed={
            label: per_seed[label].item_level_se for label in seed_labels
        },
        per_seed=per_seed,
    )


def draw_two_level_indices(
    seed_count: int,
    n_items: int,
    bootstrap: int,
    rng: np.random.Generator,
):
    """Yield paired seed positions and an independent item draw per seed occurrence."""
    for _ in range(bootstrap):
        seed_positions = rng.integers(0, seed_count, seed_count)
        item_draws = tuple(rng.integers(0, n_items, n_items) for _ in seed_positions)
        yield seed_positions, item_draws


def _per_seed_bootstrap(
    label: str,
    first: np.ndarray,
    second: np.ndarray,
    method_names: tuple[str, str],
    bootstrap: int,
    rng: np.random.Generator,
    alpha: float,
) -> PerSeedBootstrapResult:
    method_a, method_b = method_names
    accuracies = {method_a: float(first.mean()), method_b: float(second.mean())}
    full_winner = _winner(accuracies, method_names)
    first_samples: list[float] = []
    second_samples: list[float] = []
    delta_samples: list[float] = []
    flips = 0
    ties = 0
    for _ in range(bootstrap):
        indices = rng.integers(0, len(first), len(first))
        first_accuracy = float(first[indices].mean())
        second_accuracy = float(second[indices].mean())
        sampled_winner = _winner(
            {method_a: first_accuracy, method_b: second_accuracy}, method_names
        )
        first_samples.append(first_accuracy)
        second_samples.append(second_accuracy)
        delta_samples.append(first_accuracy - second_accuracy)
        if sampled_winner is None:
            ties += 1
        elif full_winner is not None and sampled_winner != full_winner:
            flips += 1
    return PerSeedBootstrapResult(
        seed_label=label,
        n_items=len(first),
        accuracies=accuracies,
        accuracy_delta=accuracies[method_a] - accuracies[method_b],
        confidence_intervals={
            method_a: _quantile_interval(first_samples, alpha),
            method_b: _quantile_interval(second_samples, alpha),
            "accuracy_delta": _quantile_interval(delta_samples, alpha),
        },
        full_sample_winner=full_winner,
        rank_flip_rate=None if full_winner is None else flips / bootstrap,
        exact_tie_rate=ties / bootstrap,
        item_level_se={method_a: _item_se(first), method_b: _item_se(second)},
    )


def _normalize_seed_mapping(
    records_by_seed: Mapping[Any, Sequence[Record]], name: str
) -> dict[str, Sequence[Record]]:
    result: dict[str, Sequence[Record]] = {}
    for raw_label, records in records_by_seed.items():
        label = str(raw_label)
        if label in result:
            raise ValueError(f"{name} seed labels collide after string normalization: {label!r}")
        result[label] = records
    return result


def _winner(values: Mapping[str, float], method_names: tuple[str, str]) -> str | None:
    first, second = method_names
    if values[first] == values[second]:
        return None
    return first if values[first] > values[second] else second


def _quantile_interval(values: Sequence[float], alpha: float) -> tuple[float, float]:
    return (
        float(np.quantile(values, alpha / 2)),
        float(np.quantile(values, 1 - alpha / 2)),
    )


def _sample_sd(values: np.ndarray) -> float:
    return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0


def _item_se(values: np.ndarray) -> float:
    return float(np.std(values, ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0


def _rank_stability_arrays(
    scores: dict[str, np.ndarray],
    n_items: int,
    bootstrap: int,
    rng: np.random.Generator,
) -> RankStabilityResult:
    means = {name: float(values.mean()) for name, values in scores.items()}
    winner = max(means.items(), key=lambda item: item[1])[0]
    flips = 0
    for _ in range(bootstrap):
        idx = rng.integers(0, n_items, n_items)
        sampled = {name: float(values[idx].mean()) for name, values in scores.items()}
        flips += max(sampled.items(), key=lambda item: item[1])[0] != winner
    return RankStabilityResult(tuple(sorted(scores)), n_items, winner, flips / bootstrap, means)


def _compare_arrays(
    baseline_records: Sequence[Record],
    method_records: Sequence[Record],
    margin: float,
    bootstrap: int,
    rng: np.random.Generator,
    alpha: float,
) -> ComparisonResult:
    base = np.array([bool(record["correct"]) for record in baseline_records])
    method = np.array([bool(record["correct"]) for record in method_records])
    pred_base = np.array([str(record["prediction"]) for record in baseline_records])
    pred_method = np.array([str(record["prediction"]) for record in method_records])
    metrics = compute_pair_metrics(base, method, pred_base, pred_method)
    cis = bootstrap_pair_metrics(base, method, pred_base, pred_method, bootstrap, rng, alpha)
    b = int(np.sum(base & ~method))
    c = int(np.sum(~base & method))
    mcnemar_p = float(stats.binomtest(min(b, c), n=b + c, p=0.5).pvalue) if b + c else 1.0
    deltas = method.astype(float) - base.astype(float)
    tost = tost_equivalence(deltas, margin, alpha)
    return ComparisonResult(
        n=len(base),
        baseline_accuracy=float(base.mean()),
        method_accuracy=float(method.mean()),
        **metrics,
        confidence_intervals=cis,
        mcnemar_b_harmful=b,
        mcnemar_c_beneficial=c,
        mcnemar_p=mcnemar_p,
        tost_equivalent=tost["equivalent"],
        tost_p_low=tost["p_low"],
        tost_p_high=tost["p_high"],
        mdd_80_power=minimum_detectable_difference(deltas, alpha, 0.80),
        required_n_for_observed_delta_80_power=required_n_for_effect(
            deltas, abs(metrics["net_accuracy_delta"]), alpha, 0.80
        ),
    )


def compute_pair_metrics(base: np.ndarray, method: np.ndarray, pred_base: np.ndarray, pred_method: np.ndarray) -> dict[str, float]:
    harmful = base & ~method
    beneficial = ~base & method
    return {
        "net_accuracy_delta": float(method.mean() - base.mean()),
        "harmful_flip_rate": float(harmful.mean()),
        "beneficial_flip_rate": float(beneficial.mean()),
        "accuracy_state_churn": float((harmful | beneficial).mean()),
        "wrong_to_different_wrong_churn": float(((~base) & (~method) & (pred_base != pred_method)).mean()),
        "total_answer_churn": float((pred_base != pred_method).mean()),
    }


def bootstrap_pair_metrics(base, method, pred_base, pred_method, bootstrap, rng, alpha):
    if bootstrap <= 0:
        return {}
    samples: dict[str, list[float]] = {}
    for _ in range(bootstrap):
        idx = rng.integers(0, len(base), len(base))
        for key, value in compute_pair_metrics(base[idx], method[idx], pred_base[idx], pred_method[idx]).items():
            samples.setdefault(key, []).append(value)
    return {key: (float(np.quantile(values, alpha / 2)), float(np.quantile(values, 1 - alpha / 2))) for key, values in samples.items()}


def minimum_detectable_difference(deltas: np.ndarray, alpha: float = 0.05, power: float = 0.80) -> float:
    sd = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
    if sd == 0:
        return 0.0
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return float(z * sd / math.sqrt(len(deltas)))


def required_n_for_effect(deltas: np.ndarray, effect: float, alpha: float = 0.05, power: float = 0.80) -> int | None:
    sd = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
    if effect <= 0 or sd == 0:
        return None
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(math.ceil((z * sd / effect) ** 2))


def tost_equivalence(deltas: np.ndarray, margin: float = 0.02, alpha: float = 0.05) -> dict[str, Any]:
    if margin <= 0:
        raise ValueError("equivalence margin must be positive")
    mean = float(np.mean(deltas))
    sd = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
    if len(deltas) <= 1 or sd == 0:
        equivalent = abs(mean) < margin
        p = 0.0 if equivalent else 1.0
        return {"equivalent": bool(equivalent), "p_low": p, "p_high": p}
    se = sd / math.sqrt(len(deltas))
    p_low = 1 - stats.t.cdf((mean + margin) / se, df=len(deltas) - 1)
    p_high = stats.t.cdf((mean - margin) / se, df=len(deltas) - 1)
    return {"equivalent": bool(p_low < alpha and p_high < alpha), "p_low": float(p_low), "p_high": float(p_high)}


def _align_pair(baseline_records: Sequence[Record], method_records: Sequence[Record]):
    base = _record_map(baseline_records)
    method = _record_map(method_records)
    ids = sorted(set(base) & set(method))
    if not ids:
        raise ValueError("record sets have no common item_id values")
    return [base[item_id] for item_id in ids], [method[item_id] for item_id in ids]


def _record_map(records: Sequence[Record]) -> dict[str, Record]:
    result: dict[str, Record] = {}
    for record in records:
        for field in ("item_id", "prediction", "correct"):
            if field not in record:
                raise ValueError(f"record is missing required field {field!r}")
        item_id = str(record["item_id"])
        if item_id in result:
            raise ValueError(f"duplicate item_id: {item_id}")
        result[item_id] = record
    return result


def _record_method(records: Sequence[Record], index: int) -> str:
    values = {str(record["method"]) for record in records if "method" in record}
    return values.pop() if len(values) == 1 else f"method_{index + 1}"
