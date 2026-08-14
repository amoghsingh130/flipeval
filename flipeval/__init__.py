"""Paired behavioral-change statistics for model evaluation records."""

from .certification import (
    RequiredN,
    required_n_for_benchmark,
    required_n_from_discordance,
)
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
from .report import FiveLineReport, five_line_report

# The two planning helpers are exported because they answer the question this
# package exists to answer -- how many items an equivalence claim needs -- and a
# reader arriving from the paper types `from flipeval import required_n_for_effect`.
# Both return plain scalars, so exporting them commits to no result-type shape.
#
# five_line_report and the certification lookup are exported for the same
# reason: they are what the paper asks a practitioner to do, so they are what a
# reader arriving from it types. `five_line_report` emits the paper's five-line
# standard for one pair; `required_n_for_benchmark` reads the published
# certification table so nobody has to retype a row out of a PDF.
#
# tost_equivalence is deliberately NOT exported: compare() already surfaces the
# same test through ComparisonResult.tost_equivalent / .tost_p_low / .tost_p_high,
# and a second top-level entry point taking deltas rather than records invites
# calling it with the record sequences that compare() takes. It stays importable
# from flipeval.core. The io helpers stay in flipeval.io for the same reason:
# the module name does the explaining.
__all__ = [
    "ComparisonResult",
    "FiveLineReport",
    "HierarchicalBootstrapResult",
    "PerSeedBootstrapResult",
    "RankStabilityResult",
    "RequiredN",
    "compare",
    "five_line_report",
    "minimum_detectable_difference",
    "paired_seed_bootstrap",
    "rank_stability",
    "required_n_for_benchmark",
    "required_n_for_effect",
    "required_n_from_discordance",
]
__version__ = "0.3.0"
