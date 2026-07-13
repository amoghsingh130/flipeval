"""Paired behavioral-change statistics for model evaluation records."""

from .core import (
    ComparisonResult,
    HierarchicalBootstrapResult,
    PerSeedBootstrapResult,
    RankStabilityResult,
    compare,
    paired_seed_bootstrap,
    rank_stability,
)

__all__ = [
    "ComparisonResult",
    "HierarchicalBootstrapResult",
    "PerSeedBootstrapResult",
    "RankStabilityResult",
    "compare",
    "paired_seed_bootstrap",
    "rank_stability",
]
__version__ = "0.2.0"
