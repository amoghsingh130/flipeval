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


# Claimed margin convention: the LARGEST absolute delta the source asserts is
# negligible, since that is the effect an equivalence claim must be able to
# resolve. This is the reading most favourable to the source -- see the
# interpretive-choices section of docs/AUDIT_VERDICTS_2026-07-20.md.
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
            "claimed_margin_pp": profile.claimed_margin_pp if profile.claimed_margin_pp is not None else "",
            "margin_basis": profile.margin_basis,
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

        # The claim's own margin, where it states one.
        if profile.claimed_margin_pp and profile.n:
            need_own = required_n_for_tost(sd_paired, profile.claimed_margin_pp / 100.0)
            row["v2_required_n_paired_own_margin"] = need_own
            row["v2_underpowered_own_margin"] = profile.n < need_own
        else:
            row["v2_required_n_paired_own_margin"] = ""
            row["v2_underpowered_own_margin"] = ""

        # §4 evaluates V2 "at the applicable margin" and names the label
        # "underpowered for its OWN assertion", so a claim that states a margin is
        # judged against that margin; 2 pp is the fallback for claims that state
        # none. The registered-margin-only reading is carried alongside because
        # the parenthetical phrasing admits it -- see the interpretive-choices
        # section of docs/AUDIT_VERDICTS_2026-07-20.md.
        if profile.claimed_margin_pp:
            row["applicable_margin_pp"] = profile.claimed_margin_pp
            row["applicable_margin_basis"] = "claim's own stated margin"
        else:
            row["applicable_margin_pp"] = REGISTERED_MARGIN_PP
            row["applicable_margin_basis"] = f"registered fallback ({REGISTERED_MARGIN_PP:g}pp); claim states no margin"
        if profile.n:
            applicable_need = required_n_for_tost(sd_paired, float(row["applicable_margin_pp"]) / 100.0)
            row["v2_required_n_applicable"] = applicable_need
            row["v2_underpowered_applicable"] = profile.n < applicable_need
        else:
            row["v2_required_n_applicable"] = ""
            row["v2_underpowered_applicable"] = ""

        # Margin sensitivity: does the 2pp verdict survive the 1pp/3pp sweep?
        sweep = [row[f"v2_underpowered_paired_{m:g}pp"] for m in MARGINS_PP]
        row["margin_sensitive"] = (len({v for v in sweep if v != ""}) > 1) if profile.n else ""

        # Headline verdict, at the applicable margin.
        if profile.indeterminate:
            row["verdict"] = f"indeterminate - {profile.indeterminate_kind}"
        elif row["v2_underpowered_applicable"]:
            row["verdict"] = "underpowered for its own assertion"
        else:
            row["verdict"] = "adequately powered at its applicable margin"
        # Secondary reading: everything judged at the registered 2pp margin.
        if profile.indeterminate:
            row["verdict_at_registered_2pp"] = f"indeterminate - {profile.indeterminate_kind}"
        elif row[f"v2_underpowered_paired_{REGISTERED_MARGIN_PP:g}pp"]:
            row["verdict_at_registered_2pp"] = "underpowered for its own assertion"
        else:
            row["verdict_at_registered_2pp"] = "adequately powered at 2pp"
        rows.append(row)
    return rows


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

    determinate = [r for r in rows if not r["indeterminate"]]
    underpowered = [r for r in determinate if r["verdict"] == "underpowered for its own assertion"]
    indeterminate = [r for r in rows if r["indeterminate"]]
    # Margin sensitivity qualifies a verdict, so it is reported over the claims
    # that HAVE a headline verdict. Indeterminate rows keep the column (their
    # supplementary V2 can still flip across the sweep) but are not counted here.
    sensitive = [r for r in determinate if r["margin_sensitive"] is True]

    print(f"AUDIT_INPUT_SHA256 claim_table={sha256_of(claim_table)}")
    print(f"AUDIT_INPUT_SHA256 atlas={sha256_of(atlas)}")
    print(f"AUDIT_ALPHA={ALPHA} POWER={POWER} registered_margin_pp={REGISTERED_MARGIN_PP}")
    at_2pp = [r for r in determinate if r["verdict_at_registered_2pp"] == "underpowered for its own assertion"]
    insufficient = [r for r in indeterminate if r["indeterminate_kind"] == "insufficient reporting"]
    incompatible = [r for r in indeterminate if r["indeterminate_kind"] == "metric-incompatible"]
    print(f"AUDIT_HEADLINE K={len(underpowered)} of {len(determinate)} determinate claims "
          f"underpowered for their own assertion; J={len(indeterminate)} indeterminate from "
          f"insufficient or incompatible reporting ({len(insufficient)} insufficient, "
          f"{len(incompatible)} metric-incompatible); {len(rows)} claims audited")
    print(f"AUDIT_HEADLINE_AT_REGISTERED_2PP {len(at_2pp)} of {len(determinate)} determinate "
          f"underpowered (+ {len(indeterminate)} indeterminate) -- secondary reading, uniform 2pp yardstick")
    print(f"AUDIT_MARGIN_SENSITIVE {len(sensitive)} of {len(determinate)} determinate claims")
    print(f"AUDIT_V3_REPRODUCIBLE "
          f"{sum(1 for r in rows if r['v3_per_item_outputs'] == 'yes')} yes / "
          f"{sum(1 for r in rows if r['v3_per_item_outputs'] == 'partial')} partial / "
          f"{sum(1 for r in rows if r['v3_per_item_outputs'] == 'no')} no")
    print(f"AUDIT_OUTPUT {output}")


if __name__ == "__main__":
    main()
