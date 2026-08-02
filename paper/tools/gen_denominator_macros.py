#!/usr/bin/env python3
"""Generate one LaTeX ledger of every repeated rev-3 audit count.

Why this exists: the same denominators appear in the abstract, the audit
section, three appendices, the conclusion and the artifact README. Every one of
them was hand-typed, which is how "4 of 12" outlived the verdicts that produced
it and how "5 of 17" outlived R10's exclusion. A count that is typed once, by a
generator, cannot go stale in one section and not another.

Sole input for the numbers is results/audit_verdicts_rev3.csv, the sealed
single-run rev-3 table (job 11591245). docs/audit_claim_table.csv is read only
to confirm the frozen candidate population is still the same 17 claim ids; no
count is taken from it.

DEFINITIONS, which the paper must use consistently (they come from
scripts/audit_verdicts.py, not from this file):

  eligible      = passes the frozen §3.1 inclusion rule. R10 alone fails it.
  assessable    = eligible AND NOT indeterminate. This is `determinate` in
                  audit_verdicts.py and is the denominator of the threshold
                  counts. 11 rows.
  margin category 1/2/3 is ORTHOGONAL to assessability, per the comment above
                  MARGIN_CATEGORY: category 3 is the amendment's evaluability
                  test ("without sufficient numerical information"), so
                  category 2 holds 12 rows = the 11 assessable ones plus R04,
                  which reports enough numbers but scores a generation metric.
                  That 12 is NOT the withdrawn rev-2 "12 determinate", which
                  was the 11 assessable rows plus R10. Two different sets of
                  the same size; this is why the cross-tab macros below are
                  named for the axis and never for "assessable".

VALIDATION, run by --check before anything here is trusted, in three layers:

  1. The input digest. The CSV's sha256 must equal the digest recorded in
     paper/sections/audit.tex and docs/PAPER_REV3_CARRY_CHECKLIST_2026-07-31.md.
  2. The registered invariants. Every count derived from the CSV is compared
     against the canonical block of docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md,
     transcribed into CANONICAL below. Those literals are used ONLY here, never
     to produce an emitted value, so a disagreement is a real failure rather
     than a tautology.
  3. The committed file. The regenerated ledger must match the committed
     paper/audit_denominators.tex byte for byte.

Usage:
    python3 paper/tools/gen_denominator_macros.py --check   # validate
    python3 paper/tools/gen_denominator_macros.py           # print
    python3 paper/tools/gen_denominator_macros.py --write   # rewrite the .tex
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
from pathlib import Path

# Resolved from this file, not from the working directory: the module is
# imported by tests/test_audit_denominators.py, which pytest may run from
# anywhere.
ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "PREREGISTRATION.md").exists():  # pragma: no cover - layout guard
    sys.exit("gen_denominator_macros.py is not two levels below the repo root")

CLAIMS = ROOT / "docs/audit_claim_table.csv"          # FROZEN, identity only
VERDICTS = ROOT / "results/audit_verdicts_rev3.csv"   # sealed 0444, single run
TARGET = ROOT / "paper/audit_denominators.tex"

# Recorded in paper/sections/audit.tex and the 2026-07-31 carry checklist as
# `c85d6f8a...b150082b`, job 11591245, single run under Amendment 2.
VERDICTS_SHA256 = "c85d6f8a5a25023389b27201a4165b79fbfdc6f274b89ca91e64182ab150082b"

MARGIN_PP = 2.0
Z = 1.6449 + 0.8416   # one-sided alpha=.05 + 80% power; see eq:tost-n

# Transcribed from the "Canonical rev-3 results" block of
# docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md. Never read by the derivation.
CANONICAL = {
    "FrozenCandidates": 17,
    "Ineligible": 1,
    "Eligible": 16,
    "Assessable": 11,
    "NotAssessable": 5,
    "NotAssessableInsufficient": 4,
    "NotAssessableOutsideFramework": 1,
    "BelowThresholdAtMedian": 1,
    "AboveThroughout": 10,
    "ChangesWithinIQR": 1,
    "BelowThroughout": 0,
    "PerItemTaskMatched": 0,
    "PerItemOtherTaskOnly": 3,
    "PerItemNone": 13,
    "ProspectiveNumericMargin": 0,
    "XtabQualTotal": 10,
    "XtabRetroTotal": 6,
    "XtabGrandTotal": 16,
}
CANONICAL_STR = {
    "IneligibleClaim": "R10",
    "OutsideFrameworkClaim": "R04",
    "SensitiveClaim": "R01",
    "SensitiveN": "1{,}838",
    "SensitiveNReq": "2{,}010",
    "SensitiveReversalD": "0.118915",
    "SensitiveCellsBelow": "345",
    "SensitiveCellsTotal": "792",
    "SensitiveCellsPct": "43.6",
}

# Per-claim fields the appendix table of final-checklist §5 consumes.
ASSESSABLE_FIELDS = ("n", "tier", "nreqQOne", "nreqMed", "nreqQThree", "dstar", "cls")
BLOCKED_FIELDS = ("n", "tier", "kind", "blocker")

CLASSIFICATION = {
    "robustly above threshold": "above throughout",
    "imputation-sensitive": "changes classification within IQR",
    "robustly below threshold": "below throughout",
}

NO_VALUE = "---"   # table notation for "no value", not prose punctuation


def num(x):
    """1838 -> '1{,}838'. LaTeX thousands separator used throughout the paper."""
    return "{:,}".format(int(x)).replace(",", "{,}")


def required_n(d, margin_pp=MARGIN_PP):
    """Registered planning size. Increasing in d, which is what lets Q1 and Q3
    bracket the whole IQR interval by monotonicity rather than by cell counts."""
    return math.ceil(((Z * math.sqrt(d)) / (margin_pp / 100.0)) ** 2)


def esc(s):
    """LaTeX-escape a verbatim CSV string. The blockers and R10's basis are
    quoted data, so they are escaped rather than rewritten."""
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("_", r"\_"),
                 ("%", r"\%"), ("#", r"\#"), ("$", r"\$"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}"), ("§", r"\S{}")):
        s = s.replace(a, b)
    return s


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load():
    """Read the sealed verdicts table, checking identity against the frozen one."""
    with open(VERDICTS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(CLAIMS, newline="", encoding="utf-8") as f:
        claim_ids = {r["claim_id"] for r in csv.DictReader(f)}
    ids = {r["claim_id"] for r in rows}
    if ids != claim_ids:
        sys.exit("claim id mismatch between the frozen table and the verdicts CSV")
    if len(rows) != len(ids):
        sys.exit("duplicate claim_id in %s" % VERDICTS)
    return rows


def is_eligible(row):
    return row["eligible"] == "True"


def is_indeterminate(row):
    return row["indeterminate"] == "True"


def is_assessable(row):
    """The threshold denominator. Eligible AND determinate, both required.

    Both halves are load-bearing and neither implies the other. R10 is
    ineligible yet determinate, and its row still carries a populated
    threshold verdict for transparency; R04 is eligible yet indeterminate.
    """
    return is_eligible(row) and not is_indeterminate(row)


def carries_threshold_verdict(row):
    """True when the row's verdict field states a threshold classification.

    Deliberately a property of the CSV text, not of assessability, so the
    invariant test can catch a row that is outside the denominator while
    still carrying a verdict.
    """
    v = row["verdict"]
    return (v.startswith("above planning threshold")
            or v.startswith("below planning threshold"))


def ledger(rows):
    """Every repeated count, derived from the CSV alone."""
    eligible = [r for r in rows if is_eligible(r)]
    assessable = [r for r in eligible if not is_indeterminate(r)]
    blocked = [r for r in eligible if is_indeterminate(r)]
    ineligible = [r for r in rows if not is_eligible(r)]

    counts = {
        "FrozenCandidates": len(rows),
        "Ineligible": len(ineligible),
        "Eligible": len(eligible),
        "Assessable": len(assessable),
        "NotAssessable": len(blocked),
        "NotAssessableInsufficient":
            sum(1 for r in blocked if r["indeterminate_kind"] == "insufficient reporting"),
        "NotAssessableOutsideFramework":
            sum(1 for r in blocked if r["indeterminate_kind"] == "metric-incompatible"),
        "BelowThresholdAtMedian":
            sum(1 for r in assessable
                if r["verdict"].startswith("below planning threshold")),
        "AboveThroughout":
            sum(1 for r in assessable if r["robustness"] == "robustly above threshold"),
        "ChangesWithinIQR":
            sum(1 for r in assessable if r["robustness"] == "imputation-sensitive"),
        "BelowThroughout":
            sum(1 for r in assessable if r["robustness"] == "robustly below threshold"),
        "PerItemTaskMatched":
            sum(1 for r in eligible if r["v3_per_item_outputs"] == "yes"),
        "PerItemOtherTaskOnly":
            sum(1 for r in eligible if r["v3_per_item_outputs"] == "partial"),
        "PerItemNone":
            sum(1 for r in eligible if r["v3_per_item_outputs"] == "no"),
        "ProspectiveNumericMargin":
            sum(1 for r in eligible if r["margin_category"] == "1"),
    }

    # The cross-tab that reconciles the margin taxonomy with "10 of 16 contain
    # no number at all". Rows are the registered margin category, columns the
    # descriptive evidence form. Both axes are over the 16 eligible sources.
    def xtab(cat, form):
        return sum(1 for r in eligible
                   if r["margin_category"] == cat and r["evidence_form"] == form)

    counts.update({
        "XtabProspectiveQual": xtab("1", "generic_adjective"),
        "XtabProspectiveRetro": xtab("1", "posthoc_delta"),
        "XtabSufficientQual": xtab("2", "generic_adjective"),
        "XtabSufficientRetro": xtab("2", "posthoc_delta"),
        "XtabInsufficientQual": xtab("3", "generic_adjective"),
        "XtabInsufficientRetro": xtab("3", "posthoc_delta"),
    })
    counts["XtabProspectiveTotal"] = counts["XtabProspectiveQual"] + counts["XtabProspectiveRetro"]
    counts["XtabSufficientTotal"] = counts["XtabSufficientQual"] + counts["XtabSufficientRetro"]
    counts["XtabInsufficientTotal"] = counts["XtabInsufficientQual"] + counts["XtabInsufficientRetro"]
    counts["XtabQualTotal"] = (counts["XtabProspectiveQual"] + counts["XtabSufficientQual"]
                               + counts["XtabInsufficientQual"])
    counts["XtabRetroTotal"] = (counts["XtabProspectiveRetro"] + counts["XtabSufficientRetro"]
                                + counts["XtabInsufficientRetro"])
    counts["XtabGrandTotal"] = counts["XtabQualTotal"] + counts["XtabRetroTotal"]

    strings = {
        "MarginPP": "%g" % MARGIN_PP,
        "IneligibleClaim": ", ".join(sorted(r["claim_id"] for r in ineligible)),
        "OutsideFrameworkClaim": ", ".join(sorted(
            r["claim_id"] for r in blocked if r["indeterminate_kind"] == "metric-incompatible")),
        "PerItemOtherTaskClaims": ", ".join(sorted(
            r["claim_id"] for r in eligible if r["v3_per_item_outputs"] == "partial")),
        "VerdictsSha": sha256_of(VERDICTS),
    }

    sensitive = [r for r in assessable if r["robustness"] == "imputation-sensitive"]
    if len(sensitive) == 1:
        s = sensitive[0]
        pct = 100.0 * float(s["frac_tier_cells_below_reversal"])
        strings.update({
            "SensitiveClaim": s["claim_id"],
            "SensitiveN": num(s["n"]),
            "SensitiveNReq": num(s["v2_required_n_paired_2pp"]),
            "SensitiveReversalD": s["reversal_discordance"],
            "SensitiveCellsBelow": s["tier_cells_below_reversal"],
            "SensitiveCellsTotal": s["discordance_n_cells"],
            "SensitiveCellsPct": "%.1f" % pct,
        })

    per_claim = {}
    for r in assessable:
        per_claim[r["claim_id"]] = {
            "n": num(r["n"]) if r["n"] else NO_VALUE,
            "tier": r["discordance_match_tier"],
            "nreqQOne": num(required_n(float(r["discordance_p25"]))),
            "nreqMed": num(r["v2_required_n_paired_2pp"]),
            "nreqQThree": num(required_n(float(r["discordance_p75"]))),
            # An empty reversal point means d* falls outside [0,1] and is
            # unattainable, which is a stable classification, not a gap.
            "dstar": r["reversal_discordance"] or NO_VALUE,
            "cls": CLASSIFICATION[r["robustness"]],
        }
    for r in blocked:
        per_claim[r["claim_id"]] = {
            "n": num(r["n"]) if r["n"] else NO_VALUE,
            "tier": r["discordance_match_tier"],
            "kind": r["indeterminate_kind"],
            "blocker": esc(r["indeterminate_reason"]),
        }
    for r in ineligible:
        per_claim[r["claim_id"]] = {
            "n": num(r["n"]) if r["n"] else NO_VALUE,
            "tier": r["discordance_match_tier"],
            "kind": "ineligible",
            "blocker": esc(r["eligibility_basis"]),
        }

    return counts, strings, per_claim


def render(counts, strings, per_claim):
    L = []
    a = L.append
    a("% audit_denominators.tex -- GENERATED, DO NOT EDIT BY HAND.")
    a("% Regenerate: python3 paper/tools/gen_denominator_macros.py --write")
    a("% Validate:   python3 paper/tools/gen_denominator_macros.py --check")
    a("%")
    a("% Source: results/audit_verdicts_rev3.csv (sealed 0444, single run, job 11591245)")
    a("%% sha256: %s" % strings["VerdictsSha"])
    a("% Identity cross-checked against docs/audit_claim_table.csv (FROZEN).")
    a("%% Margin: uniform %s pp, registered. Planning size increasing in d, so the" % strings["MarginPP"])
    a("% Q1 and Q3 columns bracket the whole atlas-IQR interval by monotonicity.")
    a("%")
    a("% Denominators. `Eligible` passes the frozen 3.1 inclusion rule;")
    a("% `Assessable` is eligible AND determinate and is the denominator of every")
    a("% threshold count.")
    a("")
    for k in ("FrozenCandidates", "Ineligible", "Eligible", "Assessable",
              "NotAssessable", "NotAssessableInsufficient",
              "NotAssessableOutsideFramework"):
        a(r"\newcommand{\Audit%s}{%d}" % (k, counts[k]))
    a("")
    a("% Threshold and sensitivity counts, all out of \\AuditAssessable.")
    for k in ("BelowThresholdAtMedian", "AboveThroughout", "ChangesWithinIQR",
              "BelowThroughout"):
        a(r"\newcommand{\Audit%s}{%d}" % (k, counts[k]))
    a("")
    a("% Per-item outputs, out of \\AuditEligible. `TaskMatched` is outputs for the")
    a("% tasks that support the audited claim; `OtherTaskOnly` is a release that")
    a("% does not cover them.")
    for k in ("PerItemTaskMatched", "PerItemOtherTaskOnly", "PerItemNone"):
        a(r"\newcommand{\Audit%s}{%d}" % (k, counts[k]))
    a(r"\newcommand{\AuditPerItemOtherTaskClaims}{%s}" % strings["PerItemOtherTaskClaims"])
    a("")
    a("% Margin cross-tab, over the 16 eligible sources, reconciling the margin")
    a("% taxonomy with the statement that ten of sixteen contain no number at all.")
    a("% Rows: registered margin category. 1 = a prospective numerical decision")
    a("% margin is declared; 2 = equivalence asserted with sufficient numerical")
    a("% information to evaluate it; 3 = asserted without sufficient numerical")
    a("% information. Columns: descriptive evidence form. Qual = qualitative")
    a("% language only, no number anywhere in the qualifying claim; Retro = a")
    a("% retrospective numerical description of an observed result.")
    a("% \\AuditXtabSufficientTotal is the 11 assessable sources plus R04, which")
    a("% reports enough numbers but scores a generation metric. It is NOT the")
    a("% withdrawn rev-2 count of twelve determinate claims, which was a")
    a("% different set of the same size.")
    for k in ("XtabProspectiveQual", "XtabProspectiveRetro", "XtabProspectiveTotal",
              "XtabSufficientQual", "XtabSufficientRetro", "XtabSufficientTotal",
              "XtabInsufficientQual", "XtabInsufficientRetro", "XtabInsufficientTotal",
              "XtabQualTotal", "XtabRetroTotal", "XtabGrandTotal"):
        a(r"\newcommand{\Audit%s}{%d}" % (k, counts[k]))
    a(r"\newcommand{\AuditProspectiveNumericMargin}{%d}" % counts["ProspectiveNumericMargin"])
    a("")
    a("% Named claims and the registered margin.")
    a(r"\newcommand{\AuditMarginPP}{%s}" % strings["MarginPP"])
    for k in ("IneligibleClaim", "OutsideFrameworkClaim"):
        a(r"\newcommand{\Audit%s}{%s}" % (k, strings[k]))
    a("")
    a("% The single imputation-sensitive claim. The percentage is a descriptive")
    a("% fraction of correlated reference cells: not a probability, not a")
    a("% confidence level, not a p-value.")
    for k in ("SensitiveClaim", "SensitiveN", "SensitiveNReq", "SensitiveReversalD",
              "SensitiveCellsBelow", "SensitiveCellsTotal", "SensitiveCellsPct"):
        a(r"\newcommand{\Audit%s}{%s}" % (k, strings[k]))
    a("")
    a("% Provenance of the numbers above.")
    a(r"\newcommand{\AuditVerdictsSha}{%s}" % strings["VerdictsSha"])
    a(r"\newcommand{\AuditVerdictsShaShort}{%s}"
      % (strings["VerdictsSha"][:8] + r"\ldots{}" + strings["VerdictsSha"][-8:]))
    a("")
    a("% Per-claim values, addressed as \\AuditVal{R01}{nreqMed}. Fields for an")
    a("%% assessable claim: %s." % ", ".join(ASSESSABLE_FIELDS))
    a("%% Fields for a non-assessable or ineligible claim: %s." % ", ".join(BLOCKED_FIELDS))
    a("% An undefined pair expands to nothing, so asking an ineligible claim for")
    a("% its classification silently yields empty; ask for `kind` instead.")
    a(r"\newcommand{\AuditVal}[2]{\csname AuditData#1#2\endcsname}")
    for cid in sorted(per_claim):
        for field in sorted(per_claim[cid]):
            a(r"\expandafter\def\csname AuditData%s%s\endcsname{%s}"
              % (cid, field, per_claim[cid][field]))
    a("")
    return "\n".join(L)


def check(rows, counts, strings, text):
    """Three layers, reported individually so a failure names its own layer."""
    problems = []

    got = sha256_of(VERDICTS)
    if got != VERDICTS_SHA256:
        problems.append("INPUT_DIGEST: %s expected %s, got %s"
                        % (VERDICTS.name, VERDICTS_SHA256, got))
    else:
        print("INPUT_DIGEST: OK -- %s matches the recorded sha256" % VERDICTS.name)

    bad = []
    for k, want in CANONICAL.items():
        if counts[k] != want:
            bad.append("  %s: canonical %s, derived %s" % (k, want, counts[k]))
    for k, want in CANONICAL_STR.items():
        if strings.get(k) != want:
            bad.append("  %s: canonical %r, derived %r" % (k, want, strings.get(k)))
    if bad:
        problems.append("CANONICAL_INVARIANTS: MISMATCH\n" + "\n".join(bad))
    else:
        print("CANONICAL_INVARIANTS: OK -- %d values reproduce the final checklist"
              % (len(CANONICAL) + len(CANONICAL_STR)))

    if not TARGET.exists():
        problems.append("COMMITTED_LEDGER: %s does not exist" % TARGET)
    else:
        committed = TARGET.read_text(encoding="utf-8")
        if committed != text:
            problems.append("COMMITTED_LEDGER: MISMATCH -- %s is not what the "
                            "generator produces; rerun with --write" % TARGET)
        else:
            print("COMMITTED_LEDGER: OK -- %d lines reproduce %s byte for byte"
                  % (len(text.splitlines()), TARGET.name))

    if problems:
        for p in problems:
            print(p)
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="validate the digest, the canonical invariants and "
                           "the committed ledger; emit nothing")
    mode.add_argument("--write", action="store_true",
                      help="rewrite paper/audit_denominators.tex")
    args = ap.parse_args(argv)

    rows = load()
    counts, strings, per_claim = ledger(rows)
    text = render(counts, strings, per_claim) + "\n"

    if args.check:
        return check(rows, counts, strings, text)
    if args.write:
        TARGET.write_text(text, encoding="utf-8")
        print("wrote %s (%d lines)" % (TARGET, len(text.splitlines())))
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
