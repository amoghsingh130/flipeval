#!/usr/bin/env python3
"""Generate the three appendix audit tables from the frozen claim table and the
rev-3 verdicts CSV.

Why this exists: the tables in sections/appendix_audit_table.tex were
hand-transcribed and went stale twice. The rev-1 imputation-tier distribution
survived in prose until 2026-07-30 (the seventh rev-1 survivor), and the tables
themselves were still rev-2 after Amendment 2 retired the vocabulary they used.
Generating a table from the CSV is itself a stale-value detector.

Identity comes from docs/audit_claim_table.csv, which is FROZEN and read-only,
NOT from the verdicts CSV, which truncates source_name at 80 characters with
several rows ending mid-word.

VALIDATION, run by --check before anything else is trusted: regenerate the
identity table, which is already correct in the tree, and diff it against what
is committed. A generator that cannot reproduce a table we already believe has
no business emitting one we do not.

Usage:
    python3 tools/gen_audit_tables.py --check    # validate against the tree
    python3 tools/gen_audit_tables.py            # print all three tables
"""

import argparse
import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "PREREGISTRATION.md").exists():
    ROOT = ROOT.parent
    if ROOT == ROOT.parent:
        sys.exit("could not locate repo root")

CLAIMS = ROOT / "docs/audit_claim_table.csv"          # FROZEN
VERDICTS = ROOT / "results/audit_verdicts_rev3.csv"   # single run, 0444
TARGET = ROOT / "paper/sections/appendix_audit_table.tex"

MARGIN_PP = 2.0
Z = 1.6449 + 0.8416   # one-sided alpha=.05 + 80% power; see eq:tost-n


def num(x):
    """1838 -> '1{,}838'. LaTeX thousands separator used throughout the paper."""
    return "{:,}".format(int(x)).replace(",", "{,}")


def required_n(d, margin_pp=MARGIN_PP):
    return math.ceil(((Z * math.sqrt(d)) / (margin_pp / 100.0)) ** 2)


def esc(s):
    for a, b in (("&", r"\&"), ("_", r"\_"), ("%", r"\%"), ("#", r"\#")):
        s = s.replace(a, b)
    # Straight quotes in the frozen table become LaTeX directional quotes, which
    # is what the committed identity table carries. The --check run caught this
    # omission: four source names are titles in quotation marks.
    out, opening = [], True
    for ch in s:
        if ch == '"':
            out.append("``" if opening else "''")
            opening = not opening
        else:
            out.append(ch)
    if not opening:
        sys.exit("unbalanced quotation marks in %r" % s)
    return "".join(out)


def load():
    claims = {r["claim_id"]: r for r in csv.DictReader(open(CLAIMS))}
    verdicts = {r["claim_id"]: r for r in csv.DictReader(open(VERDICTS))}
    if set(claims) != set(verdicts):
        sys.exit("claim id mismatch between frozen table and verdicts")
    return claims, verdicts


def table_identity(claims):
    rows = []
    for cid in sorted(claims):
        c = claims[cid]
        rows.append("%s & %s & %s \\\\" % (cid, c["frame"], esc(c["source_name"])))
    return rows


def table_characterisation(claims, verdicts):
    """Identity-free per-claim characterisation at the REGISTERED margin.

    The retired version carried a claimed-margin column (\\bar{m}) and a verdict
    column reading 'underpowered'. Both are gone: no source states a margin, and
    Amendment 2 replaces the verdict with a threshold classification reported
    together with its sensitivity. R10 keeps its row and is marked ineligible.
    """
    rows = []
    for cid in sorted(verdicts):
        v = verdicts[cid]
        bits = v["bits"] or "---"
        bench = v["benchmark"] or "(mixed/unmatched)"
        n = num(v["n"]) if v["n"] else "---"
        pd = "%.3f" % float(v["imputed_discordance"])
        tier = v["discordance_match_tier"]
        v3 = v["v3_per_item_outputs"]
        if v["eligible"] != "True":
            cls = r"\emph{ineligible}"
        elif v["indeterminate"] == "True":
            kind = "metric" if "metric" in v["indeterminate_kind"] else "reporting"
            cls = "not assessable (%s)" % kind
        else:
            cls = {"robustly above threshold": "above throughout",
                   "imputation-sensitive": r"\textbf{sensitive}",
                   "robustly below threshold": "below throughout"}[v["robustness"]]
        rows.append("%s & %s & %s & %s & %s & %s & %s & %s & %s \\\\"
                    % (cid, esc(v["method_family"]), bits, esc(bench), n, pd,
                       tier, v3, cls))
    return rows


def table_power(verdicts):
    """MDD and required n at the registered margin, with the IQR bracket.

    Replaces the retired columns m* and n@m*, which divided by result-derived
    margins, with n_req at Q1 and Q3 of the same atlas cells that supplied the
    median. Those two bracket the whole interval because n_req is increasing
    in the discordance rate.
    """
    rows = []
    for cid in sorted(verdicts):
        v = verdicts[cid]
        mdd_p = "%.2f" % float(v["v1_mdd_pp_paired"]) if v["v1_mdd_pp_paired"] else "---"
        mdd_i = "%.2f" % float(v["v1_mdd_pp_independent"]) if v["v1_mdd_pp_independent"] else "---"
        q1 = num(required_n(float(v["discordance_p25"])))
        med = num(v["v2_required_n_paired_2pp"])
        q3 = num(required_n(float(v["discordance_p75"])))
        rev = ("%.4f" % float(v["reversal_discordance"])
               if v["reversal_discordance"] else "---")
        n = num(v["n"]) if v["n"] else "---"
        rows.append("%s & %s & %s & %s & %s & %s & %s & %s \\\\"
                    % (cid, n, mdd_p, mdd_i, q1, med, q3, rev))
    return rows


def committed_rows(label):
    """Pull the body rows of the tabular carrying \\label{label} from TARGET."""
    src = TARGET.read_text(encoding="utf-8")
    i = src.find(r"\label{%s}" % label)
    if i == -1:
        sys.exit("no \\label{%s} in %s" % (label, TARGET))
    body = src[src.index(r"\midrule", i) + len(r"\midrule"):
               src.index(r"\bottomrule", i)]
    return [ln.strip() for ln in body.strip().split("\n") if ln.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate the generator against the trusted identity "
                         "table instead of emitting anything")
    args = ap.parse_args()
    claims, verdicts = load()

    if args.check:
        want = committed_rows("tab:audit-identity")
        got = table_identity(claims)
        if want != got:
            print("IDENTITY_REGEN: MISMATCH")
            for w, g in zip(want, got):
                if w != g:
                    print("  committed: %s" % w)
                    print("  generated: %s" % g)
            if len(want) != len(got):
                print("  row counts: committed %d, generated %d"
                      % (len(want), len(got)))
            return 1
        print("IDENTITY_REGEN: OK -- %d rows reproduce the committed table "
              "byte for byte" % len(got))
        return 0

    for label, rows in (("tab:audit-identity", table_identity(claims)),
                        ("tab:audit-characterisation",
                         table_characterisation(claims, verdicts)),
                        ("tab:audit-power", table_power(verdicts))):
        print("%% %s" % label)
        for r in rows:
            print(r)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
