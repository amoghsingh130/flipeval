"""Compute the registered per-claim audit verdicts (AUDIT_REGISTRATION §4-5).

Reads the frozen `docs/audit_claim_table.csv` (never written), imputes a
discordance rate per claim from the atlas, and emits `results/audit_verdicts.csv`.

The frozen claim table stores n, baseline accuracy and deltas as human-written
prose ("imputed (PIQA validation set, standard n=1838)"), which no regex can
parse safely across 17 heterogeneous rows. Rather than guess at read time, each
claim's numeric profile is transcribed once into CLAIM_PROFILES below, with the
basis string recorded alongside every value so a reviewer can check it against
the frozen row. `tests/test_audit_stats.py` asserts the profile set matches the
frozen claim ids exactly and that the flagged-degenerate set is exactly the four
rows the reconciliation memo flags.

Nothing here re-imputes beyond §3.2, which already prescribes "reported n as
stated, else the benchmark's standard size, recorded as imputed". Where the
frozen row says "imputed via standard task sizes" without writing the number,
STANDARD_SIZES supplies it and `n_basis` names every task summed.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path

from scripts.audit_stats import (
    ALPHA,
    POWER,
    independent_binomial_sd,
    load_atlas_cells,
    minimum_detectable_delta,
    nearest_cell_discordance,
    paired_flip_sd,
    required_n_for_tost,
    reversal_discordance,
    sha256_of,
)

# Standard evaluation-set sizes used for §3.2 imputation.
STANDARD_SIZES = {
    "mmlu": 14042, "mmlu_cot": 14042, "arc_challenge": 1172, "arc_easy": 2376,
    "gsm8k": 1319, "hellaswag": 10042, "winogrande": 1267, "truthfulqa": 817,
    "piqa": 1838, "lambada": 5153, "storycloze": 1871, "boolq": 3270,
    "rte": 277, "openbookqa": 500, "arena_hard": 500, "aime25": 30,
    "gpqa_diamond": 198, "math500": 500,
}

OPENLLM_V1 = ("mmlu", "mmlu_cot", "arc_challenge", "gsm8k", "hellaswag", "winogrande", "truthfulqa")
OPENLLM_V1_6TASK = ("mmlu", "arc_challenge", "gsm8k", "hellaswag", "winogrande", "truthfulqa")


def _sum(tasks) -> int:
    return sum(STANDARD_SIZES[t] for t in tasks)


@dataclass(frozen=True)
class ClaimProfile:
    claim_id: str
    method_family: str | None
    bits: int | None
    benchmark: str | None
    n: int | None
    n_basis: str
    baseline_accuracy: float | None
    claimed_margin_pp: float | None
    margin_basis: str
    indeterminate: bool = False          # a registered input absent, or the metric incompatible
    indeterminate_reason: str = ""
    # Why the claim is indeterminate, as it appears in the verdict string. Two
    # kinds: the source reports too little ("insufficient reporting"), or it
    # reports enough but about a metric the registered flip model cannot score
    # ("metric-incompatible").
    indeterminate_kind: str = "insufficient reporting"
    notes: str = ""
    # Registered components that remain computable for an indeterminate claim.
    # Reported in the CSV as supplementary transparency, never verdict-bearing.
    determinate_components: tuple = field(default=())


# --------------------------------------------------------------------------
# AUDIT_REGISTRATION Amendment 2 (2026-07-31, signed).
#
# The quantity previously called `claimed_margin_pp` is the largest absolute
# delta the SOURCE REPORTED. Amendment 2 establishes that this is not a margin:
# "A reported delta is an outcome of the evaluation; a margin is a threshold
# against which an outcome is judged." It is therefore emitted under a name that
# says what it is, and every quantity derived from it is non-verdict-bearing.
# --------------------------------------------------------------------------

# Excluded from the eligible population by Amendment 2's eligibility correction,
# applying the inclusion rule already registered in §3.1. Evidence:
# docs/AUDIT_SOURCE_VERIFICATION_2026-07-31.md §4.
INELIGIBLE = {
    "R10": "quoted claim appears in neither prose nor a table caption (§3.1): the "
           "recorded exact_quote appears nowhere in the source; 98.6% is a table cell",
}

# Amendment 2 category (1 formal / 2 informal / 3 unquantified), with the text
# supporting it. Determined against the frozen exact_quote and, where the quote
# alone was inconclusive, the archived source. NO source declares a prospective
# tolerance, so category 1 is empty -- see the verification doc §6-7.
#
# Category is orthogonal to determinacy: category 3 is the amendment's
# EVALUABILITY test ("without sufficient numerical information"), while R04 is
# category 2 (its source reports a result and calls it negligible) and separately
# indeterminate for metric-incompatibility.
MARGIN_CATEGORY = {
    "R01": (2, "negligible accuracy degradation relative to the uncompressed baseline"),
    "R02": (3, "without any performance degradation"),
    "R03": (2, "negligible loss in accuracy"),
    "R04": (2, "providing 4x model size reduction with negligible performance loss"),
    "R05": (2, "enables lossless compression to ultra-low precisions of up to 3-bit"),
    "R06": (2, "able to match the zero-shot accuracies of their dense counterparts"),
    "R07": (2, "inducing 50% sparsity results in practically no accuracy decrease"),
    "R08": (2, "achieves 93.0% recovery for the Arena-Hard evaluation, 98.9% for OpenLLM v1"),
    "R09": (2, "achieves an average score of 73.44 on the OpenLLM benchmark"),
    "R10": (2, "(ineligible; recorded for transparency only)"),
    "R11": (3, "achieves competitive accuracy to the BF16 model"),
    "R12": (2, "maintaining model accuracy"),
    "R13": (3, "minimal impact on accuracy"),
    "R14": (3, "is nearly lossless here, with sub-point differences across the aggregate scores"),
    "R15": (2, "100.3% for OpenLLM v1 (using Meta's prompting when available)"),
    "R16": (2, "99.4% for OpenLLM v1 (using Meta's prompting when available)"),
    "R17": (2, "achieves an average score of 68.69 ... whereas the unquantized model achieves 68.54"),
}

# Descriptive sub-classification of the evidence the source offers, from the
# 2026-07-31 full-text review. Not a registered quantity and never
# verdict-bearing; reported because "no source states a threshold, and ten state
# no number at all" is the audit's substantive reporting finding.
EVIDENCE_FORM = {
    **{c: "generic_adjective" for c in
       ("R01", "R02", "R03", "R04", "R05", "R06", "R07", "R11", "R12", "R13")},
    **{c: "posthoc_delta" for c in
       ("R08", "R09", "R10", "R14", "R15", "R16", "R17")},
}

CLAIM_PROFILES = [
    ClaimProfile("R01", "gptq", 4, "piqa", 1838,
                 "frozen row states 'imputed (PIQA validation set, standard n=1838)'",
                 0.8107, 2.35,
                 "max |delta| over the 5 OPT-175B tasks the claim covers (ARC-e -2.35pp)",
                 notes="n is PIQA's; the largest delta is ARC-Easy's. Using PIQA's own "
                       "-0.07pp delta instead would raise the MDD/margin ratio ~34x."),
    ClaimProfile("R02", "w8a8_int8", 8, None, None,
                 "frozen row: 'not stated in extractable text (Figure 1 is a chart image)'",
                 None, None, "no numeric delta on the page (figure-only)",
                 indeterminate=True,
                 indeterminate_reason="no reported or imputable n, no baseline, no numeric delta",
                 notes="Headline comparison exists only as a chart image."),
    ClaimProfile("R03", "w8a8_int8", 8, None, _sum(("winogrande", "hellaswag", "piqa", "lambada")),
                 "frozen row itemises WinoGrande 1267 + HellaSwag 10042 + PIQA 1838 + LAMBADA 5153",
                 0.669, 0.8,
                 "body text 'only 0.8% degradation at O3' (BLOOM-176B), the largest stated",
                 notes="Multi-task pooled n; benchmark left unmatched (mixed suite)."),
    ClaimProfile("R04", "awq", 4, "gsm8k", 1319,
                 "GSM8K standard test size; the frozen row's own n (COCO 5000) belongs to a CIDEr claim",
                 0.1387, 0.30,
                 "GSM8K -0.30pp, the accuracy benchmark the source reports",
                 indeterminate=True,
                 indeterminate_reason="qualifying quote asserts negligible loss on COCO CIDEr, a "
                                      "generation metric with no per-item correct/incorrect state; "
                                      "V1/V2 are flip-model quantities that do not apply to it",
                 indeterminate_kind="metric-incompatible",
                 determinate_components=("V1_paired", "V1_independent", "V2"),
                 notes="The GSM8K columns are computable and retained for transparency, but GSM8K "
                       "is a different benchmark from the one the qualifying sentence is about, and "
                       "the source used non-trigger language for it. Scoring the CIDEr assertion "
                       "via GSM8K would audit a sentence the source did not write, so R04 is "
                       "indeterminate and its GSM8K numbers are supplementary only."),
    ClaimProfile("R05", "squeezellm", 4, "mmlu", 14042,
                 "frozen row states 'imputed (MMLU test set, standard n=14042)'",
                 0.391, 3.1,
                 "3-bit -3.1pp: the abstract asserts losslessness 'up to 3-bit'",
                 notes="Source-internal contradiction: abstract claims lossless to 3-bit, own "
                       "Table 2 shows -3.1pp at 3-bit. Atlas has no 3-bit cells; matched at 4-bit."),
    ClaimProfile("R06", "pruning", None, None,
                 _sum(("boolq", "rte", "hellaswag", "winogrande", "arc_easy", "arc_challenge", "openbookqa")),
                 "frozen row itemises the 7 zero-shot splits",
                 0.6697, 0.30, "LLaMA-65B -0.30pp, the larger of the two stated deltas",
                 notes="50% unstructured pruning: no bit width, and the atlas contains no pruning "
                       "cells, so imputation descends to the global tier by construction."),
    ClaimProfile("R07", "pruning", None, None,
                 _sum(("lambada", "piqa", "arc_easy", "arc_challenge", "storycloze")),
                 "frozen row itemises the 5 zero-shot splits",
                 0.7029, 0.23, "+0.23pp 5-task average (sparse above dense)",
                 notes="Paper itself notes 'these numbers are more noisy' -- an informal "
                       "acknowledgment of measurement uncertainty, no interval."),
    ClaimProfile("R08", "w4a16", 4, "mmlu", _sum(OPENLLM_V1),
                 "OpenLLM v1 7-task pooled standard sizes ('imputed via each task's standard size')",
                 0.743, 1.4,
                 "Arena-Hard +1.4pp absolute, the largest delta the quoted sentence covers",
                 notes="Self-contradiction: prose says 93.0% Arena-Hard recovery, the card's own "
                       "table shows 25.8->27.2 = 105.4%. Per-item outputs exist for Arena-Hard/"
                       "OpenLLM v2/HumanEval but NOT for the OpenLLM v1 tasks in this claim."),
    ClaimProfile("R09", "w8a8_fp8", 8, "mmlu", _sum(OPENLLM_V1),
                 "OpenLLM v1 7-task pooled standard sizes ('not stated; imputed via standard task sizes')",
                 0.7379, 0.84, "GSM8K-CoT -0.84pp, the largest per-task delta on the card",
                 notes="Headline average delta is -0.35pp (99.52% recovery)."),
    ClaimProfile("R10", "w4a16", 4, "mmlu", _sum(OPENLLM_V1_6TASK),
                 "OpenLLM v1 6-task pooled standard sizes ('not stated; imputed via standard task sizes')",
                 0.7316, 1.05, "MMLU -1.05pp, the largest per-task delta on the card",
                 notes="Headline average delta is -0.47pp (98.6% recovery)."),
    ClaimProfile("R11", "spinquant", 4, None, None,
                 "frozen row: 'not stated / not extractable' (blog presents bar charts only)",
                 None, None, "no numeric delta in the blog (chart-image only)",
                 indeterminate=True,
                 indeterminate_reason="no reported or imputable n, no baseline, no numeric delta",
                 notes="Qualifying prose is in the blog; numbers live only in a companion model "
                       "card that carries no qualifying prose. Per-source purity enforced."),
    ClaimProfile("R12", "w8a8_fp8", 8, "mmlu", 14042,
                 "frozen row states 'imputed (MMLU test set, standard n=14042)'",
                 0.704, 0.87,
                 "LLaMA-v2-70B FP8 MMLU loss 0.87%, the largest numeric loss on the page",
                 notes="Page's primary evidence is a qualitative Very Low/Low/Medium/High rating "
                       "table; numeric losses appear only as scattered examples."),
    ClaimProfile("R13", "w8a8_fp8", 8, "gsm8k", 250,
                 "explicitly stated on the page: lm_eval --limit 250",
                 None, None,
                 "no delta computable: the page shows no baseline run at all",
                 indeterminate=True,
                 indeterminate_reason="no on-page baseline accuracy and no computable delta",
                 determinate_components=("V2",),
                 notes="n IS stated (250), so the TOST required-n comparison is computable and is "
                       "reported as a supplementary result; V1's MDD/margin ratio is not."),
    ClaimProfile("R14", "w8a8_fp8", 8, None, _sum(("aime25", "gpqa_diamond", "math500")),
                 "frozen row imputes AIME25=30 + GPQA:Diamond=198 + MATH500=500 (LiveCodeBench-v6 size not stated)",
                 None, 0.7, "prose states differences of 'at most 0.7 points'",
                 indeterminate=True,
                 indeterminate_reason="no baseline accuracy stated (Figure 8 chart only)",
                 determinate_components=("V1_paired", "V2"),
                 notes="Most methodologically careful vendor source found (explicit 5-10 "
                       "repetitions per benchmark), but no variance reported for the comparison."),
    ClaimProfile("R15", "w8a8_int8", 8, "mmlu", _sum(OPENLLM_V1),
                 "OpenLLM v1 7-task pooled standard sizes ('not stated; imputed via standard task sizes')",
                 0.741, 0.2, "+0.2pp OpenLLM v1 average (100.3% recovery)",
                 notes="Per-item outputs released for Arena-Hard/OpenLLM v2/HumanEval, not OpenLLM v1."),
    ClaimProfile("R16", "w4a16", 4, "mmlu", _sum(OPENLLM_V1),
                 "OpenLLM v1 7-task pooled standard sizes ('not stated; imputed via standard task sizes')",
                 0.845, 0.52, "-0.52pp OpenLLM v1 average (99.4% recovery)",
                 notes="Per-item outputs referenced for other suites, not OpenLLM v1."),
    ClaimProfile("R17", "w8a16", 8, "mmlu", _sum(OPENLLM_V1_6TASK),
                 "OpenLLM v1 6-task pooled standard sizes ('not stated; imputed via standard task sizes')",
                 0.6854, 0.15, "+0.15pp (68.69 vs 68.54, 99.8% recovery)",
                 notes="Atlas has no W8A16 cells; imputation descends to the 8-bit tiers."),
]

MARGINS_PP = (1.0, 2.0, 3.0)
REGISTERED_MARGIN_PP = 2.0


def per_item_outputs_verdict(raw: str) -> str:
    """V3: binary reproducibility from the frozen `per_item_outputs_released` column."""
    text = raw.strip().lower()
    if text.startswith("partial"):
        return "partial"
    if text.startswith("yes"):
        return "yes"
    return "no"


def compute_rows(claim_table: Path, atlas: Path) -> list[dict]:
    frozen = {r["claim_id"]: r for r in csv.DictReader(claim_table.open(encoding="utf-8", newline=""))}
    cells = load_atlas_cells(atlas)
    rows = []

    for profile in CLAIM_PROFILES:
        source_row = frozen[profile.claim_id]
        match = nearest_cell_discordance(cells, profile.method_family, profile.bits, profile.benchmark)
        row: dict = {
            "claim_id": profile.claim_id,
            "source_name": source_row["source_name"][:80],
            "frame": source_row["frame"],
            "method_family": profile.method_family or "",
            "bits": profile.bits if profile.bits is not None else "",
            "benchmark": profile.benchmark or "(mixed/unmatched)",
            "n": profile.n if profile.n is not None else "",
            "n_basis": profile.n_basis,
            "baseline_accuracy": profile.baseline_accuracy if profile.baseline_accuracy is not None else "",
            "eligible": profile.claim_id not in INELIGIBLE,
            "eligibility_basis": INELIGIBLE.get(profile.claim_id, "meets §3.1 inclusion"),
            "margin_category": MARGIN_CATEGORY[profile.claim_id][0],
            "margin_category_basis": MARGIN_CATEGORY[profile.claim_id][1],
            "evidence_form": EVIDENCE_FORM[profile.claim_id],
            # NOT a margin. The largest absolute delta the source REPORTED.
            # Amendment 2: never to be described as the claim's own, stated,
            # declared or asserted margin.
            "source_reported_delta_pp": profile.claimed_margin_pp if profile.claimed_margin_pp is not None else "",
            "reported_delta_basis": profile.margin_basis,
            "imputed_discordance": round(match.discordance, 6),
            "discordance_match_tier": match.tier,
            "discordance_n_cells": match.n_cells,
            "indeterminate": profile.indeterminate,
            "indeterminate_kind": profile.indeterminate_kind if profile.indeterminate else "",
            "indeterminate_reason": profile.indeterminate_reason,
            "determinate_components": " ".join(profile.determinate_components),
            "v3_per_item_outputs": per_item_outputs_verdict(source_row["per_item_outputs_released"]),
            "notes": profile.notes,
        }

        sd_paired = paired_flip_sd(match.discordance)
        sd_indep = (independent_binomial_sd(profile.baseline_accuracy)
                    if profile.baseline_accuracy is not None else None)

        # V1 -- minimum detectable delta, paired and independent-binomial.
        if profile.n:
            mdd_paired = minimum_detectable_delta(sd_paired, profile.n) * 100.0
            row["v1_mdd_pp_paired"] = round(mdd_paired, 4)
            row["v1_mdd_pp_independent"] = (
                round(minimum_detectable_delta(sd_indep, profile.n) * 100.0, 4)
                if sd_indep is not None else "")
            if profile.claimed_margin_pp:
                row["v1_mdd_over_margin_paired"] = round(mdd_paired / profile.claimed_margin_pp, 3)
                row["v1_mdd_over_margin_independent"] = (
                    round(minimum_detectable_delta(sd_indep, profile.n) * 100.0 / profile.claimed_margin_pp, 3)
                    if sd_indep is not None else "")
            else:
                row["v1_mdd_over_margin_paired"] = ""
                row["v1_mdd_over_margin_independent"] = ""
        else:
            row["v1_mdd_pp_paired"] = ""
            row["v1_mdd_pp_independent"] = ""
            row["v1_mdd_over_margin_paired"] = ""
            row["v1_mdd_over_margin_independent"] = ""

        # V2 -- required n for TOST, at the registered margin and the sweep.
        for margin_pp in MARGINS_PP:
            margin = margin_pp / 100.0
            need_paired = required_n_for_tost(sd_paired, margin)
            row[f"v2_required_n_paired_{margin_pp:g}pp"] = need_paired
            row[f"v2_required_n_independent_{margin_pp:g}pp"] = (
                required_n_for_tost(sd_indep, margin) if sd_indep is not None else "")
            if profile.n:
                row[f"v2_underpowered_paired_{margin_pp:g}pp"] = profile.n < need_paired
                row[f"v2_underpowered_independent_{margin_pp:g}pp"] = (
                    profile.n < required_n_for_tost(sd_indep, margin) if sd_indep is not None else "")
            else:
                row[f"v2_underpowered_paired_{margin_pp:g}pp"] = ""
                row[f"v2_underpowered_independent_{margin_pp:g}pp"] = ""

        # SUPERSEDED READING, retained as a non-verdict-bearing sensitivity
        # analysis per Amendment 2. This is what the audit reported through
        # v1.0.0: each claim judged against the largest delta its own source
        # reported. Amendment 2 withdraws it as a verdict because a reported
        # delta is an outcome, not a declared threshold. Kept, not deleted, so
        # the paper and the citable artifact can disagree without either being
        # silently rewritten.
        if profile.claimed_margin_pp and profile.n:
            need_rep = required_n_for_tost(sd_paired, profile.claimed_margin_pp / 100.0)
            row["sens_required_n_at_reported_delta"] = need_rep
            row["sens_underpowered_at_reported_delta"] = profile.n < need_rep
        else:
            row["sens_required_n_at_reported_delta"] = ""
            row["sens_underpowered_at_reported_delta"] = ""

        # Margin sensitivity: does the 2pp verdict survive the 1pp/3pp sweep?
        sweep = [row[f"v2_underpowered_paired_{m:g}pp"] for m in MARGINS_PP]
        row["margin_sensitive"] = (len({v for v in sweep if v != ""}) > 1) if profile.n else ""

        # PRIMARY VERDICT -- Amendment 2: at the registered 2 pp margin, for
        # every claim. §4 names 2 pp first; the own-margin clause is
        # parenthetical and rested on a quantity no source declared.
        underpowered_2pp = row[f"v2_underpowered_paired_{REGISTERED_MARGIN_PP:g}pp"]
        if profile.indeterminate:
            row["verdict"] = f"indeterminate - {profile.indeterminate_kind}"
        elif underpowered_2pp:
            row["verdict"] = f"below planning threshold at {REGISTERED_MARGIN_PP:g}pp"
        else:
            row["verdict"] = f"above planning threshold at {REGISTERED_MARGIN_PP:g}pp"

        # Discordance-imputation sensitivity. The verdict above rests on a POINT
        # imputation (the median of the matched tier). Amendment 2 requires the
        # surviving power result to be reported as a sensitivity-dependent
        # planning flag, never without its reversal point, so the reversal point
        # and the supporting distribution are emitted for every claim.
        vals = match.values
        row["discordance_p25"] = round(_quantile(vals, 0.25), 6) if vals else ""
        row["discordance_p75"] = round(_quantile(vals, 0.75), 6) if vals else ""
        if profile.n and not profile.indeterminate:
            d_star = reversal_discordance(profile.n, REGISTERED_MARGIN_PP / 100.0)
            below = sum(1 for v in vals if v < d_star)
            # d* > 1 means no attainable discordance could put this claim below
            # the threshold: n is large enough that the verdict cannot flip. The
            # column is left blank rather than printing an impossible rate, and
            # `robustness` carries the finding.
            row["reversal_discordance"] = round(d_star, 6) if d_star < 1.0 else ""
            row["tier_cells_below_reversal"] = below
            row["frac_tier_cells_below_reversal"] = round(below / len(vals), 4) if vals else ""
            at_p25 = profile.n < required_n_for_tost(paired_flip_sd(_quantile(vals, 0.25)),
                                                     REGISTERED_MARGIN_PP / 100.0)
            at_p75 = profile.n < required_n_for_tost(paired_flip_sd(_quantile(vals, 0.75)),
                                                     REGISTERED_MARGIN_PP / 100.0)
            row["underpowered_at_p25_discordance"] = at_p25
            row["underpowered_at_p75_discordance"] = at_p75
            if at_p25 and at_p75 and underpowered_2pp:
                row["robustness"] = "robustly below threshold"
            elif not at_p25 and not at_p75 and not underpowered_2pp:
                row["robustness"] = "robustly above threshold"
            else:
                row["robustness"] = "imputation-sensitive"
        else:
            row["reversal_discordance"] = ""
            row["tier_cells_below_reversal"] = ""
            row["frac_tier_cells_below_reversal"] = ""
            row["underpowered_at_p25_discordance"] = ""
            row["underpowered_at_p75_discordance"] = ""
            row["robustness"] = "indeterminate" if profile.indeterminate else ""
        rows.append(row)
    return rows


def _quantile(sorted_values, p: float) -> float:
    """Linear-interpolation quantile over an already-sorted sequence.

    Matches numpy's default so the reported quartiles agree with the atlas
    summary statistics, without importing numpy into the verdict path.
    """
    if not sorted_values:
        raise ValueError("quantile of empty sequence")
    if len(sorted_values) == 1:
        return sorted_values[0]
    i = p * (len(sorted_values) - 1)
    lo = int(i)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (i - lo)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-table", default="docs/audit_claim_table.csv")
    parser.add_argument("--atlas", default="results/atlas_cells_summary.csv")
    parser.add_argument("--output", default="results/audit_verdicts.csv")
    args = parser.parse_args()

    claim_table, atlas = Path(args.claim_table), Path(args.atlas)
    rows = compute_rows(claim_table, atlas)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Amendment 2: every count is over the ELIGIBLE population. Ineligible rows
    # stay in the CSV, flagged, so the exclusion is auditable rather than a gap.
    eligible = [r for r in rows if r["eligible"]]
    determinate = [r for r in eligible if not r["indeterminate"]]
    indeterminate = [r for r in eligible if r["indeterminate"]]
    below = [r for r in determinate if r["verdict"].startswith("below planning threshold")]
    sensitive = [r for r in determinate if r["margin_sensitive"] is True]
    insufficient = [r for r in indeterminate if r["indeterminate_kind"] == "insufficient reporting"]
    incompatible = [r for r in indeterminate if r["indeterminate_kind"] == "metric-incompatible"]
    cat = {c: sum(1 for r in eligible if r["margin_category"] == c) for c in (1, 2, 3)}
    generic = sum(1 for r in eligible if r["evidence_form"] == "generic_adjective")

    print(f"AUDIT_INPUT_SHA256 claim_table={sha256_of(claim_table)}")
    print(f"AUDIT_INPUT_SHA256 atlas={sha256_of(atlas)}")
    print(f"AUDIT_ALPHA={ALPHA} POWER={POWER} registered_margin_pp={REGISTERED_MARGIN_PP}")
    print(f"AUDIT_POPULATION {len(rows)} frozen candidates; {len(rows) - len(eligible)} ineligible "
          f"({', '.join(sorted(INELIGIBLE))}); {len(eligible)} eligible")
    print(f"AUDIT_MARGIN_CATEGORY formal={cat[1]} informal={cat[2]} unquantified={cat[3]} "
          f"of {len(eligible)} eligible; {generic} state no number at all")
    print(f"AUDIT_HEADLINE K={len(below)} of {len(determinate)} assessable claims below the "
          f"planning threshold at {REGISTERED_MARGIN_PP:g}pp; J={len(indeterminate)} not assessable "
          f"({len(insufficient)} insufficient reporting, {len(incompatible)} metric-incompatible)")
    for r in below:
        print(f"AUDIT_FLAG {r['claim_id']} n={r['n']} required={r[f'v2_required_n_paired_{REGISTERED_MARGIN_PP:g}pp']} "
              f"imputed_d={r['imputed_discordance']} reversal_d={r['reversal_discordance']} "
              f"tier_cells_below_reversal={r['tier_cells_below_reversal']}/{r['discordance_n_cells']} "
              f"({r['frac_tier_cells_below_reversal']}) robustness={r['robustness']}")
    rob = {k: sum(1 for r in determinate if r["robustness"] == k)
           for k in ("robustly below threshold", "robustly above threshold", "imputation-sensitive")}
    print(f"AUDIT_ROBUSTNESS {rob}")
    print(f"AUDIT_MARGIN_SENSITIVE {len(sensitive)} of {len(determinate)} assessable claims")
    print(f"AUDIT_V3_REPRODUCIBLE "
          f"{sum(1 for r in eligible if r['v3_per_item_outputs'] == 'yes')} yes / "
          f"{sum(1 for r in eligible if r['v3_per_item_outputs'] == 'partial')} partial / "
          f"{sum(1 for r in eligible if r['v3_per_item_outputs'] == 'no')} no (of {len(eligible)} eligible)")
    print(f"AUDIT_OUTPUT {output}")


if __name__ == "__main__":
    main()
