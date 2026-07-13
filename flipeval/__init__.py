"""Paired behavioral-change statistics for model evaluation records."""

from .core import ComparisonResult, RankStabilityResult, compare, rank_stability

__all__ = ["ComparisonResult", "RankStabilityResult", "compare", "rank_stability"]
__version__ = "0.1.0"
