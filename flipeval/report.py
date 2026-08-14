"""The paper's five-line reporting standard, emitted from two per-item files.

The paper proposes five lines a compression claim should carry: declare a
margin; run the paired test at that margin; report churn beside net delta; cite
the sample size it met against the count its benchmark family requires; and
release per-item outputs. This module turns those five lines into something a
practitioner runs in one command:

    flipeval report fp16.jsonl gptq.jsonl --margin 0.02 --benchmark mmlu

The wording of the five headings is taken from the paper (end of
``paper/sections/introduction.tex``, recapped in ``sections/conclusion.tex``) and
is deliberately not paraphrased: the block is meant to be recognisable as *that*
standard when it is pasted into a model card.

WHAT THE TOOL CAN AND CANNOT ATTEST. Lines 1-4 are computed from the two files
it was given. Line 5 is a release action, so the tool reports the location it was
told and otherwise says the line is unmet. It never prints a location it did not
receive, and it never treats "no location" as satisfied -- that fifth line is the
one the audit in the paper found nobody meets, so silently passing it would be
the tool's own version of the defect.
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Any, Sequence

from .certification import (
    RequiredN,
    _check_percentile,
    required_n_for_benchmark,
    required_n_from_discordance,
)
from .core import ComparisonResult, Record, compare

#: Column width the emitted block is wrapped to.
WRAP = 88


@dataclass(frozen=True)
class FiveLineReport:
    """A computed five-line block, plus the numbers behind it."""

    margin: float
    alpha: float
    result: ComparisonResult
    benchmark: str | None
    percentile: str
    required_n: int | None
    required_n_source: str
    per_item_outputs: str | None
    baseline_label: str
    method_label: str
    lines: tuple[str, ...]

    @property
    def meets_required_n(self) -> bool | None:
        """True/False against the cited requirement; None when none was found."""
        if self.required_n is None:
            return None
        return self.result.n >= self.required_n

    def to_text(self, *, header: bool = True) -> str:
        """The copy-pasteable block."""
        out: list[str] = []
        if header:
            out += [
                "FlipEval five-line report",
                f"  baseline : {self.baseline_label}",
                f"  candidate: {self.method_label}",
                f"  items    : {self.result.n} (paired on item_id)",
                "",
            ]
        for index, line in enumerate(self.lines, start=1):
            out.append(
                textwrap.fill(
                    f"{index}. {line}",
                    width=WRAP,
                    subsequent_indent="   ",
                )
            )
        return "\n".join(out)

    def to_dict(self) -> dict[str, Any]:
        return {
            "margin": self.margin,
            "margin_pp": self.margin * 100.0,
            "alpha": self.alpha,
            "benchmark": self.benchmark,
            "percentile": self.percentile,
            "n_evaluated": self.result.n,
            "required_n": self.required_n,
            "required_n_source": self.required_n_source,
            "meets_required_n": self.meets_required_n,
            "per_item_outputs": self.per_item_outputs,
            "baseline": self.baseline_label,
            "candidate": self.method_label,
            "lines": list(self.lines),
            "comparison": self.result.to_dict(),
        }


def five_line_report(
    baseline_records: Sequence[Record],
    method_records: Sequence[Record],
    *,
    margin: float = 0.02,
    alpha: float = 0.05,
    bootstrap: int = 1000,
    seed: int = 0,
    benchmark: str | None = None,
    percentile: str = "median",
    per_item_outputs: str | None = None,
    table: str | None = None,
    baseline_label: str = "baseline",
    method_label: str = "candidate",
) -> FiveLineReport:
    """Compute the five-line block for one paired comparison.

    ``margin`` is a proportion (0.02 = a two-point margin), matching
    :func:`flipeval.compare`. ``benchmark`` selects the row of the published
    certification table that line 4 cites; without it, line 4 falls back to the
    requirement implied by *this pair's own* observed churn and says so.
    """
    if margin <= 0:
        raise ValueError(f"margin must be positive; got {margin!r}")
    if margin > 0.5:
        raise ValueError(
            f"margin is a PROPORTION here; got {margin!r}. A two-point margin is "
            "margin=0.02, not 2.0 (the certification table is indexed in points, "
            "flipeval.compare and this function are not)."
        )
    _check_percentile(percentile)
    result = compare(
        baseline_records,
        method_records,
        margin=margin,
        bootstrap=bootstrap,
        seed=seed,
        alpha=alpha,
    )
    required, source = _requirement(result, margin, benchmark, percentile, table)
    lines = _lines(
        result,
        margin=margin,
        alpha=alpha,
        required_n=required,
        required_n_source=source,
        benchmark=benchmark,
        percentile=percentile,
        per_item_outputs=per_item_outputs,
    )
    return FiveLineReport(
        margin=margin,
        alpha=alpha,
        result=result,
        benchmark=benchmark,
        percentile=percentile,
        required_n=required,
        required_n_source=source,
        per_item_outputs=per_item_outputs,
        baseline_label=baseline_label,
        method_label=method_label,
        lines=lines,
    )


def _requirement(
    result: ComparisonResult,
    margin: float,
    benchmark: str | None,
    percentile: str,
    table: str | None,
) -> tuple[int | None, str]:
    """The count line 4 cites, and a phrase naming where it came from."""
    margin_pp = margin * 100.0
    if benchmark is not None:
        row: RequiredN = required_n_for_benchmark(benchmark, margin_pp, table=table)
        label = {"p25": "25th percentile", "median": "median", "p75": "75th percentile"}[
            percentile
        ]
        return (
            row.required_n(percentile),
            f"{row.benchmark_family} at +/-{row.margin_pp:g} pp, {label} of the churn "
            f"observed across {row.n_atlas_cells} atlas cells "
            "(results/certification_tables_rev2.csv)",
        )
    return (
        required_n_from_discordance(result.accuracy_state_churn, margin_pp),
        "this pair's own observed churn, not a benchmark family "
        "(pass --benchmark to cite the published table)",
    )


def _pp(value: float) -> str:
    return f"{value * 100:.2f} pp"


def _lines(
    result: ComparisonResult,
    *,
    margin: float,
    alpha: float,
    required_n: int | None,
    required_n_source: str,
    benchmark: str | None,
    percentile: str,
    per_item_outputs: str | None,
) -> tuple[str, ...]:
    # 1 -- declare a margin.
    line1 = (
        f"Margin declared: equivalence is claimed within +/-{margin * 100:.2f} pp of "
        f"accuracy, tested at alpha = {alpha:g}."
    )

    # 2 -- run the paired equivalence test at that margin.
    verdict = "EQUIVALENT" if result.tost_equivalent else "NOT EQUIVALENT"
    line2 = (
        f"Paired equivalence test at that margin: TOST says {verdict} "
        f"(p_low = {result.tost_p_low:.4g}, p_high = {result.tost_p_high:.4g}; "
        f"equivalence requires both < {alpha:g}). Exact McNemar p = {result.mcnemar_p:.4g} "
        f"on {result.mcnemar_b_harmful} harmful and {result.mcnemar_c_beneficial} "
        "beneficial discordant pairs; failure to detect a difference is not "
        "equivalence and is not reported as one."
    )

    # 3 -- churn beside net delta.
    line3 = (
        f"Churn beside net delta: net accuracy delta {result.net_accuracy_delta * 100:+.2f} pp, "
        f"accuracy-state churn {_pp(result.accuracy_state_churn)} "
        f"({_pp(result.harmful_flip_rate)} correct->wrong, "
        f"{_pp(result.beneficial_flip_rate)} wrong->correct), "
        f"answer churn {_pp(result.total_answer_churn)}."
    )

    # 4 -- sample size met against what the benchmark family requires.
    if required_n is None:
        line4 = (
            f"Sample size: {result.n} items evaluated; no required count could be "
            "computed for this pair."
        )
    else:
        shortfall = required_n - result.n
        state = (
            f"MEETS the requirement (surplus {-shortfall} items)"
            if shortfall <= 0
            else f"SHORT by {shortfall} items"
        )
        line4 = (
            f"Sample size: {result.n} items evaluated against {required_n} required by "
            f"{required_n_source}; {state}. The requirement is a planning count at an "
            "assumed true difference of zero, so it is a lower bound."
        )

    # 5 -- release per-item outputs.
    if per_item_outputs:
        line5 = (
            f"Per-item outputs: released at {per_item_outputs}, one row per evaluation "
            "item with the correctness state and predicted answer this report was "
            "computed from."
        )
    else:
        line5 = (
            "Per-item outputs: NOT DECLARED. This line is the one the tool cannot "
            "verify for you; publish the two per-item files and pass "
            "--per-item-outputs <location> to record where they are."
        )
    return (line1, line2, line3, line4, line5)
