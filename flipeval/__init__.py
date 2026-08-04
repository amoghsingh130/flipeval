"""Paired behavioral-change statistics for model evaluation records."""

from .core import (
    ComparisonResult,
    HierarchicalBootstrapResult,
    PerSeedBootstrapResult,
    RankStabilityResult,
    compare,
    minimum_detectable_difference,
    paired_seed_bootstrap,
    rank_stability,
    required_n_for_effect,
)

# The two planning helpers are exported because they answer the question this
# package exists to answer -- how many items an equivalence claim needs -- and a
# reader arriving from the paper types `from flipeval import required_n_for_effect`.
# Both return plain scalars, so exporting them commits to no result-type shape.
#
# tost_equivalence is deliberately NOT exported: compare() already surfaces the
# same test through ComparisonResult.tost_equivalent / .tost_p_low / .tost_p_high,
# and a second top-level entry point taking deltas rather than records invites
# calling it with the record sequences that compare() takes. It stays importable
# from flipeval.core. The io helpers stay in flipeval.io for the same reason:
# the module name does the explaining.
__all__ = [
    "ComparisonResult",
    "HierarchicalBootstrapResult",
    "PerSeedBootstrapResult",
    "RankStabilityResult",
    "compare",
    "minimum_detectable_difference",
    "paired_seed_bootstrap",
    "rank_stability",
    "required_n_for_effect",
]
__version__ = "0.2.0"
