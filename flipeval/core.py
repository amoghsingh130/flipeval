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
