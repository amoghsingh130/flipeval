"""Shared statistics and atlas lookup for the registered zero-GPU analyses.

Used by `scripts/audit_verdicts.py` (AUDIT_REGISTRATION_2026-07-15 §4-5) and
`scripts/certification_tables.py` (ATLAS_MINING_REGISTRATION_2026-07-15 §5).

Statistical model
-----------------
Both analyses rest on the **paired-flip model**. For a paired evaluation of a
baseline and a compressed model on the same n items, the per-item accuracy
difference is d_i in {-1, 0, +1}: -1 when the compression turns a correct answer
wrong (harmful flip), +1 for the reverse (beneficial flip), 0 when both agree.
Writing p_d for the discordance rate (harmful + beneficial flip rate, which the
atlas records as `accuracy_state_churn`), under the null of no true difference
the flips split evenly and

    Var(d) = p_d          =>  sd_paired = sqrt(p_d)

The naive alternative treats the two evaluations as independent binomials at
baseline accuracy p, giving Var(p_hat_1 - p_hat_2) * n = 2p(1-p), i.e.

    sd_independent = sqrt(2 p (1 - p))

Because real compressed models agree with their baselines on the large majority
of items, p_d is typically far below 2p(1-p) and the paired design needs far
fewer items for the same resolution. Quantifying that gap is the point of the
certification tables, so both columns are always reported side by side.

Reuse and cross-checking
------------------------
`flipeval.core.minimum_detectable_difference` and `required_n_for_effect` are the
project's tested implementations, but they take a per-item delta *array*. The
audit has no per-item data -- only (n, baseline accuracy, imputed discordance) --
so the sd is derived analytically above and fed to the same z-formulas here.
`tests/test_audit_stats.py` pins these against the flipeval functions on
synthetic delta vectors: any divergence is a test failure, not a silent fork.
"""
from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path

from scipy import stats

ALPHA = 0.05
POWER = 0.80

# Two-sided detection (V1/MDD) vs one-sided-per-bound TOST (V2/required-n).
# TOST rejects both one-sided nulls at alpha each; its sample size therefore uses
# z_{1-alpha}, not z_{1-alpha/2}. See the methods block in the output docs.
Z_TWO_SIDED = float(stats.norm.ppf(1 - ALPHA / 2))
Z_ONE_SIDED = float(stats.norm.ppf(1 - ALPHA))
Z_POWER = float(stats.norm.ppf(POWER))


def paired_flip_sd(discordance: float) -> float:
    """Per-item sd of the paired accuracy delta at discordance rate `discordance`."""
    if not 0.0 <= discordance <= 1.0:
        raise ValueError(f"discordance must be in [0, 1], got {discordance}")
    return math.sqrt(discordance)


def independent_binomial_sd(baseline_accuracy: float) -> float:
    """Per-item sd of the delta if the two runs were independent binomials."""
    p = baseline_accuracy
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"baseline accuracy must be in [0, 1], got {p}")
    return math.sqrt(2.0 * p * (1.0 - p))


def minimum_detectable_delta(sd: float, n: int, alpha: float = ALPHA, power: float = POWER) -> float:
    """Smallest true delta detectable at `power`, two-sided `alpha`, given n items."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if sd == 0.0:
        return 0.0
    z = float(stats.norm.ppf(1 - alpha / 2)) + float(stats.norm.ppf(power))
    return z * sd / math.sqrt(n)


def required_n_for_tost(sd: float, margin: float, alpha: float = ALPHA, power: float = POWER) -> int | None:
    """Items needed to conclude equivalence within +/-`margin` via TOST.

    Standard TOST sample size with assumed true difference zero:
        n = ceil( ((z_{1-alpha} + z_{1-beta}) * sd / margin)^2 )
    """
    if margin <= 0:
        raise ValueError(f"margin must be positive, got {margin}")
    if sd == 0.0:
        return 1
    z = float(stats.norm.ppf(1 - alpha)) + float(stats.norm.ppf(power))
    return int(math.ceil((z * sd / margin) ** 2))


def synthetic_deltas(n: int, discordance: float):
    """A per-item delta vector realising `discordance` with zero net delta.

    Lets the analytic sd be cross-checked against flipeval's array-based
    functions, which is how `tests/test_audit_stats.py` pins the two together.
    """
    import numpy as np

    flips_each_way = int(round(n * discordance / 2.0))
    deltas = np.zeros(n, dtype=float)
    deltas[:flips_each_way] = 1.0
    deltas[flips_each_way : 2 * flips_each_way] = -1.0
    return deltas


# ---------------------------------------------------------------------------
# Atlas cell loading and the nearest-cell matcher
# ---------------------------------------------------------------------------

# Atlas task name -> benchmark family. The atlas logs MMLU as 57 per-subject
# hendrycksTest cells and BBH/MATH/MuSR/GPQA as per-subtask cells; the audit
# matches at family granularity, so these collapse.
_TASK_FAMILY_PREFIXES = (
    ("harness_hendrycksTest_", "mmlu"),
    ("bbh_", "bbh"),
    ("gpqa_", "gpqa"),
    ("math_", "math"),
    ("musr_", "musr"),
)
_TASK_FAMILY_EXACT = {
    "mmlu_pro": "mmlu_pro",
    "ifeval": "ifeval",
    "harness_arc_challenge_25": "arc_challenge",
    "harness_hellaswag_10": "hellaswag",
    "harness_winogrande_5": "winogrande",
    "harness_gsm8k_5": "gsm8k",
    "harness_drop_3": "drop",
    "harness_truthfulqa_mc_0": "truthfulqa",
}

# Atlas `method` -> (family, bit width). Bit width is the weight precision.
_METHOD_PROFILE = {
    "GPTQ": ("gptq", 4),
    "AWQ": ("awq", 4),
    "W4A16": ("w4a16", 4),
    "W8A8-INT8": ("w8a8_int8", 8),
    "W8A8-FP8": ("w8a8_fp8", 8),
    "bnb-4bit(LoRA)": ("bnb_4bit", 4),
    "bnb-8bit(LoRA)": ("bnb_8bit", 8),
}


def benchmark_family(task: str) -> str:
    """Map an atlas task name to its benchmark family."""
    if task in _TASK_FAMILY_EXACT:
        return _TASK_FAMILY_EXACT[task]
    for prefix, family in _TASK_FAMILY_PREFIXES:
        if task.startswith(prefix):
            return family
    return task


def method_profile(method: str) -> tuple[str, int | None]:
    """Map an atlas method label to (method family, bit width)."""
    return _METHOD_PROFILE.get(method, (method.lower(), None))


@dataclass(frozen=True)
class AtlasCell:
    method_family: str
    bits: int | None
    benchmark: str
    n: int
    discordance: float
    baseline_accuracy: float
    is_probe: bool


def load_atlas_cells(path: str | Path, include_probe: bool = False) -> list[AtlasCell]:
    """Load analysable atlas cells.

    Drops rows the atlas already excluded, and -- per
    ATLAS_MINING_REGISTRATION §6 -- drops every cell belonging to a disclosed
    probe pair unless `include_probe`. Probe pairs are tiny hand-built
    sanity pairs (n as low as 10) and would distort an empirical
    discordance distribution badly.
    """
    cells: list[AtlasCell] = []
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["excluded_or_skipped"].strip().lower() != "false":
                continue
            is_probe = row["contains_disclosed_probe_cell"].strip().lower() == "true"
            if is_probe and not include_probe:
                continue
            try:
                n = int(row["n"])
                discordance = float(row["accuracy_state_churn"])
                baseline = float(row["baseline_accuracy"])
            except (TypeError, ValueError):
                continue
            family, bits = method_profile(row["method"])
            cells.append(AtlasCell(
                method_family=family,
                bits=bits,
                benchmark=benchmark_family(row["task"]),
                n=n,
                discordance=discordance,
                baseline_accuracy=baseline,
                is_probe=is_probe,
            ))
    return cells


# Match tiers, most specific first. Each is (label, key function over an
# AtlasCell, key function over the requested target). A tier matches when the
# two keys are equal; `None` in a target field makes that field a wildcard, so a
# claim with no bit width (e.g. a pruning method) simply falls through the
# bit-width tiers instead of matching them spuriously.
MATCH_TIERS = ("family+bits+benchmark", "family+bits", "bits+benchmark", "bits", "benchmark", "global")


def _tier_matches(tier: str, cell: AtlasCell, family: str | None, bits: int | None, benchmark: str | None) -> bool:
    if tier == "family+bits+benchmark":
        return cell.method_family == family and cell.bits == bits and cell.benchmark == benchmark
    if tier == "family+bits":
        return cell.method_family == family and cell.bits == bits
    if tier == "bits+benchmark":
        return cell.bits == bits and cell.benchmark == benchmark
    if tier == "bits":
        return cell.bits == bits
    if tier == "benchmark":
        return cell.benchmark == benchmark
    if tier == "global":
        return True
    raise ValueError(f"unknown match tier: {tier}")


@dataclass(frozen=True)
class DiscordanceMatch:
    discordance: float
    tier: str
    n_cells: int


def nearest_cell_discordance(
    cells: list[AtlasCell],
    family: str | None,
    bits: int | None,
    benchmark: str | None,
) -> DiscordanceMatch:
    """Impute a discordance rate from the nearest atlas cells.

    Tiers are tried most-specific first and the first non-empty tier wins:

      1. family + bits + benchmark   exact cell
      2. family + bits               same method at same precision, any benchmark
      3. bits + benchmark            same precision on the same benchmark
      4. bits                        same precision anywhere
      5. benchmark                   same benchmark at any precision
      6. global                      all analysable cells

    A tier whose target field is None can never match (`cell.bits == None` is
    false for every real cell), so an unmappable claim descends automatically
    rather than being forced into a wrong cell. The **median** over matching
    cells is used, not the mean: per-cell discordance is right-skewed and a few
    high-churn generative cells would otherwise dominate.
    """
    for tier in MATCH_TIERS:
        matching = [c for c in cells if _tier_matches(tier, c, family, bits, benchmark)]
        if matching:
            values = sorted(c.discordance for c in matching)
            return DiscordanceMatch(_median(values), tier, len(matching))
    raise ValueError("no atlas cells available for imputation")


def _median(sorted_values: list[float]) -> float:
    if not sorted_values:
        raise ValueError("median of empty sequence")
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def quantiles(values: list[float]) -> dict[str, float]:
    """25th / 50th / 75th percentiles, linear interpolation (numpy default)."""
    import numpy as np

    array = np.asarray(values, dtype=float)
    return {
        "p25": float(np.quantile(array, 0.25)),
        "median": float(np.quantile(array, 0.50)),
        "p75": float(np.quantile(array, 0.75)),
    }


def sha256_of(path: str | Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_leading_int(text: str) -> int | None:
    """First standalone integer in `text`, or None. Used for stated-n parsing."""
    match = re.search(r"\b(\d{2,7})\b", text.replace(",", ""))
    return int(match.group(1)) if match else None
