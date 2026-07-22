"""Turning a registered `ComparisonResult` into a verdict.

No statistic is computed here. Every number is read off `flipeval.core`'s
`ComparisonResult`, or obtained by calling a registered function
(`required_n_for_effect`) with a different argument. The only thing this module
adds is the decision rule that maps those numbers onto a verdict label, and the
prose that reports them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from flipeval.core import ComparisonResult, required_n_for_effect

CERTIFIED_EQUIVALENT = "CERTIFIED-EQUIVALENT"
DEGRADED = "DEGRADED"
IMPROVED = "IMPROVED"
UNDERPOWERED = "UNDERPOWERED"


@dataclass(frozen=True)
class Verdict:
    label: str
    headline: str
    notes: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        """0 for a decided verdict, 1 for UNDERPOWERED.

        UNDERPOWERED is not an error -- the run was valid, it just cannot
        support a claim -- but it is the case a CI job wants to catch, so it
        gets a distinct non-zero code. Parse errors exit 2.
        """
        return 1 if self.label == UNDERPOWERED else 0


def deltas_from_records(baseline: Sequence[Any], candidate: Sequence[Any]) -> np.ndarray:
    """Per-item signed correctness change, in the order given.

    Same construction as `flipeval.core._compare_arrays`: candidate minus
    baseline over the boolean `correct` field. Recomputed here only so that
    `required_n_for_effect` can be evaluated at the user's margin; the
    `ComparisonResult` reports required-n at the *observed* delta, which is a
    different question.
    """
    base = np.array([bool(record["correct"]) for record in baseline])
    cand = np.array([bool(record["correct"]) for record in candidate])
    return cand.astype(float) - base.astype(float)


def decide(result: ComparisonResult, margin: float, alpha: float = 0.05) -> Verdict:
    """Map a registered comparison onto a verdict.

    Precedence is TOST first, then McNemar. The two can both fire: a difference
    can be statistically real and still small enough to sit inside the margin.
    When that happens the equivalence claim is the one the user asked for --
    they supplied the margin as their tolerance -- so the verdict is
    CERTIFIED-EQUIVALENT, and the significant-but-negligible difference is
    reported as a note rather than hidden.
    """
    notes: list[str] = []
    significant = result.mcnemar_p < alpha
    direction_worse = result.mcnemar_b_harmful > result.mcnemar_c_beneficial

    if result.tost_equivalent:
        headline = (
            f"equivalent within +/-{margin:.4g} "
            f"(TOST p_low={result.tost_p_low:.4g}, p_high={result.tost_p_high:.4g}, "
            f"both < {alpha})"
        )
        if significant:
            notes.append(
                f"McNemar is also significant (p={result.mcnemar_p:.4g}): the difference "
                f"is real but smaller than your margin of {margin:.4g}. "
                "Equivalence is claimed at the margin you supplied, not at zero."
            )
        return Verdict(CERTIFIED_EQUIVALENT, headline, notes)

    if significant:
        label = DEGRADED if direction_worse else IMPROVED
        headline = (
            f"McNemar p={result.mcnemar_p:.4g} < {alpha}; "
            f"net accuracy delta {result.net_accuracy_delta:+.4f}"
        )
        notes.append(
            "Not equivalent at your margin and not consistent with no change: "
            f"TOST p_low={result.tost_p_low:.4g}, p_high={result.tost_p_high:.4g} "
            f"(equivalence needs both < {alpha})."
        )
        return Verdict(label, headline, notes)

    headline = (
        f"neither equivalence nor difference is established at margin "
        f"+/-{margin:.4g} (TOST p_low={result.tost_p_low:.4g}, "
        f"p_high={result.tost_p_high:.4g}; McNemar p={result.mcnemar_p:.4g})"
    )
    notes.append(
        "A non-significant McNemar result is not evidence of equivalence. "
        "This run cannot support either claim."
    )
    return Verdict(UNDERPOWERED, headline, notes)


def render(
    result: ComparisonResult,
    verdict: Verdict,
    margin: float,
    required_n_at_margin: int | None,
    baseline_path: str,
    candidate_path: str,
) -> str:
    """Human-readable report. Always prints the inputs beside the verdict."""
    lines = [
        f"baseline : {baseline_path}",
        f"candidate: {candidate_path}",
        f"items    : {result.n} (paired on item identity)",
        "",
        f"VERDICT: {verdict.label}",
        f"  {verdict.headline}",
    ]
    for note in verdict.notes:
        lines.append(f"  note: {note}")

    lines += [
        "",
        "Accuracy",
        f"  baseline           {result.baseline_accuracy:.4f}",
        f"  candidate          {result.method_accuracy:.4f}",
        f"  net delta          {result.net_accuracy_delta:+.4f}",
        "",
        "Flips (McNemar discordant pairs)",
        f"  b  correct -> wrong  {result.mcnemar_b_harmful}"
        f"   ({result.harmful_flip_rate:.4f})",
        f"  c  wrong -> correct  {result.mcnemar_c_beneficial}"
        f"   ({result.beneficial_flip_rate:.4f})",
        f"  McNemar p            {result.mcnemar_p:.4g}",
        "",
        "Churn",
        f"  correctness-state    {result.accuracy_state_churn:.4f}",
        f"  answer string        {result.total_answer_churn:.4f}",
        f"  wrong -> other wrong {result.wrong_to_different_wrong_churn:.4f}",
        "",
        "Equivalence and power",
        f"  TOST margin          +/-{margin:.4g}",
        f"  TOST p_low           {result.tost_p_low:.4g}",
        f"  TOST p_high          {result.tost_p_high:.4g}",
        f"  min detectable diff  {result.mdd_80_power:.4f}  (80% power, this n)",
    ]
    if required_n_at_margin is None:
        lines.append(
            "  required n @ margin  n/a (zero per-item variance in this pair)"
        )
    else:
        lines.append(
            f"  required n @ margin  {required_n_at_margin}"
            f"  (to detect {margin:.4g} at 80% power)"
        )
    if result.required_n_for_observed_delta_80_power is None:
        lines.append("  required n @ observed  n/a")
    else:
        lines.append(
            f"  required n @ observed  {result.required_n_for_observed_delta_80_power}"
            f"  (to detect {abs(result.net_accuracy_delta):.4g})"
        )
    return "\n".join(lines)


def required_n_at_margin(deltas: np.ndarray, margin: float) -> int | None:
    """Registered power calculation, evaluated at the user's margin."""
    return required_n_for_effect(deltas, margin)
