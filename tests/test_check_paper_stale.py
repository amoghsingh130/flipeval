"""Tests for the stale-claim and stale-pointer linter in paper/tools/check_paper.py.

The point of this file is the NEGATIVE CONTROLS. Five checkers on this project
have now been believed before they were controlled, and each bug first looked
like a document defect. A linter that silently matches nothing passes every run
and certifies nothing, so these tests assert three separate things:

  1. every rule fires on a string it is supposed to catch (no dead rules);
  2. clean text produces silence;
  3. the exemption machinery does not swallow a live hit.

Two traps get their own tests because both have already cost this project a
correct-looking wrong answer:

  * LINE-ORIENTED MATCHING. Several sources here are single-line blobs, and a
    line-based matcher returns nothing on them. `test_single_line_blob` plants a
    token deep inside one line.
  * PREFIX COLLISION. `results/atlas_cells_summary.csv` is a strict prefix of
    `results/atlas_cells_summary_rev2.csv`, so a substring match flags every
    correct rev-2 pointer as stale. `test_rev2_pointer_is_not_rev1` covers it.

And `test_canonical_results_block_is_clean` guards the opposite failure: the
target state must not trip the linter. The rev-3 canonical block requires a new
"10 of 16" statement, which a sloppy "N of 1x" pattern would flag.
"""

import importlib.util
import sys
from pathlib import Path

_TOOL = Path(__file__).resolve().parents[1] / "paper" / "tools" / "check_paper.py"
_spec = importlib.util.spec_from_file_location("check_paper_under_test", _TOOL)
cp = importlib.util.module_from_spec(_spec)
sys.modules["check_paper_under_test"] = cp
_spec.loader.exec_module(cp)


def hits(text, rel="paper/sections/fake.tex", ext=".tex", compiled=None):
    return cp.scan_text(text, rel, ext, compiled)


def live(text, **kw):
    """Hits that would fail the run: stale severity, not exempt."""
    return [h for h in hits(text, **kw)
            if h["severity"] == "stale" and not h["exempt"]]


def rules_hit(text, **kw):
    return {h["rule"] for h in hits(text, **kw)}


# --------------------------------------------------------------------------
# 1. No dead rules: every rule fires on a string it must catch.
# --------------------------------------------------------------------------

# One sample per rule key. Kept literal rather than generated from the patterns,
# so a broken pattern cannot also break its own test.
RULE_SAMPLES = {
    "count-4-of-12": "K = 4 of 12 determinate claims",
    "count-5-of-17": "and 5 of 17 cannot be evaluated",
    "count-0-of-17": "0 of the 17 audited sources release these",
    "four-claims": "four claims are underpowered for the margin",
    "shortfall-endpoint": r"shortfalls of $2.0\times$ were reported",
    "shortfall-pair": "the 2.0x-12.9x range",
    "own-margin": "evaluated against its own margin",
    "claim-specific-margin": "using a claim-specific margin",
    "margin-they-assert": "could not resolve the margin they assert",
    "stated-margin": "the Stated margin column",
    "label-audit-underpowered": r"see Table~\ref{tab:audit-underpowered}",
    "old-r-group": "the flagged rows R17, R07, R06, R15 are listed",
    "pointer-verdicts-rev2": "read from results/audit_verdicts_rev2.csv",
    "pointer-rev1-artifact": "read from results/atlas_cells_summary.csv",
    "pointer-rev1-certification-doc": "see docs/CERTIFICATION_TABLES_2026-07-20.md",
    "rev1-population": "over the 1,155 analysable cells",
    "rev1-certification-ratio": "a 4.4x compute penalty",
    "own-assertion": "underpowered for its own assertion",
    "own-margin-column": "the own_margin column",
    "underpowered": "the benchmark is underpowered here",
}


def test_every_rule_has_a_sample():
    """A rule with no sample is a rule nobody proved fires."""
    assert {k for k, _, _, _ in cp.STALE_RULES} == set(RULE_SAMPLES)


def test_every_rule_fires_on_its_sample():
    for key, sample in sorted(RULE_SAMPLES.items()):
        assert key in rules_hit(sample), "rule %r matched nothing in %r" % (
            key, sample)


def test_multiplication_sign_spellings_all_match():
    """Plain 'x', LaTeX \\times, '$...\\times$' and U+00D7 are all live in this
    tree. Matching only the first was the specific hazard called out."""
    for spelling in ["2.0x and 12.9x",
                     r"$2.0\times$ to $12.9\times$",
                     r"2.0\times to 12.9\times",
                     "2.0× to 12.9×"]:
        assert "shortfall-endpoint" in rules_hit(spelling), spelling


def test_math_mode_count_spellings_match():
    """The manuscript writes '$K = 4$ of 12', not '4 of 12'. A separator class
    of whitespace and hyphen alone walks straight past the closing '$'."""
    assert "count-4-of-12" in rules_hit("$K = 4$ of 12 determinate claims")
    assert "count-5-of-17" in rules_hit("$J = 5$ of the 17 audited claims")
    assert "count-0-of-17" in rules_hit(r"\textbf{0 of the 17 audited sources}")


def test_latex_braced_thousands_separator_matches():
    """The manuscript writes 1{,}155, not 1,155. Matching only the plain form
    finds none of the paper's own numbers."""
    assert "rev1-population" in rules_hit("the 1{,}155 cell population")
    assert "rev1-population" in rules_hit("the 1,155 cell population")


def test_old_r_group_is_order_independent():
    assert "old-r-group" in rules_hit("rows R06, R07, R15 and R17 were flagged")
    assert "old-r-group" in rules_hit("R17, R07, R06, R15")
    # a different set of four must not fire
    assert "old-r-group" not in rules_hit("R01, R03, R05, R08")


# --------------------------------------------------------------------------
# 2. NEGATIVE CONTROLS: clean text is silent, and correct text stays correct.
# --------------------------------------------------------------------------

CLEAN = r"""
\section{Results}
\label{sec:clean}
% SOURCE: results/audit_verdicts_rev3.csv, column verdict.
Across 16 eligible sources drawn from 17 frozen candidates, none reported an
a priori numerical equivalence margin. Among the remaining 11, ten stayed above
the approximate planning threshold throughout the atlas-IQR interval at a
uniform 2-percentage-point margin, and one changed classification within it.
The analysis population is the 1{,}707 cells that are neither excluded nor part
of a disclosed feasibility probe.
"""


def test_clean_file_is_silent():
    """The control that matters most: a checker that never says OK is as
    useless as one that never says FAIL."""
    assert hits(CLEAN) == []


# Verbatim from the canonical results block and the recommended headline of
# docs/PAPER_REV3_FINAL_CHECKLIST_2026-08-02.md. This is the TARGET STATE, and a
# linter that fights the target state gets switched off.
CANONICAL = """
- 17 frozen candidate sources.
- R10 is ineligible under the registered inclusion rule.
- 16 eligible sources.
- 11 numerically assessable sources.
- 5 non-assessable sources: 4 insufficiently reported and 1 outside the
  registered binary paired-outcome framework.
- At the uniform 2-percentage-point margin, 1 of 11 is below the approximate
  planning threshold at the median discordance imputation.
- No claim remains below the threshold throughout the atlas-IQR sensitivity
  interval.
- Ten of 11 remain above the threshold throughout that interval; R01 changes
  classification within it.
- R01: reported n = 1,838; median-imputation requirement n_req = 2,010;
  reversal point d* = 0.118915 under the implemented rounding convention.
- R01 is classified as adequate under 345 of 792 reference-cell imputations
  (43.6%); this fraction is descriptive, not a probability.
- No eligible source reports an a priori numerical equivalence margin.
- No eligible source releases task-matched per-item outputs; R08, R15, and R16
  release outputs for other tasks only.
- The margin taxonomy and the "10 of 16 contain no number" statement are
  reconciled in a cross-tab with explicit definitions.

Across 16 eligible sources, none reported an a priori numerical equivalence
margin or released task-matched per-item outputs. Five could not be assessed
under the registered binary paired-outcome framework. Among the remaining 11,
ten remained above the approximate planning threshold throughout the atlas-IQR
sensitivity interval, while one changed classification within it; no claim
remained below the threshold throughout that interval.
"""


def test_canonical_results_block_is_clean():
    assert hits(CANONICAL, rel="paper/sections/canon.tex") == []


def test_ten_of_sixteen_is_not_five_of_seventeen():
    """The specific false-positive trap: '10 of 16' is the NEW required
    wording and must never be read as the forbidden '5 of 17'."""
    for good in ["10 of 16 contain no number", "16 of 17 are eligible",
                 "1 of 11 is below the threshold", "0 of 16 released outputs",
                 "15 of 17 were reachable"]:
        assert hits(good) == [], good


def test_rev2_pointer_is_not_rev1():
    """Prefix collision. The rev-1 names are strict prefixes of the rev-2
    names; a substring match condemns every correct pointer in the tree."""
    for current in ["results/atlas_cells_summary_rev2.csv",
                    "results/audit_verdicts_rev3.csv",
                    "results/certification_tables_rev2.csv",
                    "results/identical_score_churn_rev2.csv",
                    "results/atlas_exclusions_rev2.csv",
                    "results/atlas_run_rev2_20260721.tar.gz"]:
        assert "pointer-rev1-artifact" not in rules_hit(current), current
    assert "pointer-rev1-artifact" in rules_hit("results/audit_verdicts.csv")


def test_decimals_that_are_not_the_shortfall_range():
    for benign in ["margin_pp = 2.0 rows", "Apache-2.0 licensed",
                   "at 1.0/2.0/3.0", "R04 & 2.09 pp", "mean 4,002.0;",
                   "a 3.3$\\times$ pool"]:
        assert "shortfall-endpoint" not in rules_hit(benign), benign
        assert "shortfall-pair" not in rules_hit(benign), benign


def test_underpowered_inside_an_identifier_is_not_a_prose_hit():
    """v2_underpowered_paired_2pp is a live rev-3 column name."""
    assert "underpowered" not in rules_hit("column v2_underpowered_paired_2pp")
    assert "underpowered" not in rules_hit("underpowered_at_p25_discordance,")


# --------------------------------------------------------------------------
# 3. The single-line blob trap.
# --------------------------------------------------------------------------

def test_single_line_blob():
    """No newlines at all, token 4 kB in. A line-oriented matcher, or a
    `grep -o` with a fixed character window, returns nothing here."""
    blob = ("filler text " * 350) + "and 4 of 12 claims " + ("more text " * 350)
    assert "\n" not in blob
    found = [h for h in hits(blob, rel="paper/blob.md", ext=".md")
             if h["rule"] == "count-4-of-12"]
    assert len(found) == 1
    assert found[0]["line"] == 1
    assert "4 of 12" in found[0]["text"]


def test_snippet_is_bounded_on_a_blob():
    blob = "x" * 5000 + " Stated margin " + "y" * 5000
    found = [h for h in hits(blob, rel="paper/blob.md", ext=".md")
             if h["rule"] == "stated-margin"]
    assert len(found) == 1
    assert len(found[0]["text"]) < 200


# --------------------------------------------------------------------------
# 4. Exemptions: they must not swallow a live hit.
# --------------------------------------------------------------------------

WITHDRAWN_COMMENT = """% THE 2.0x-12.9x SHORTFALL RANGE IS WITHDRAWN, NOT
% RECOMPUTED. Do not reintroduce this sentence with new numbers in it.
Prose that says nothing about it.
"""

BARE_COMMENT = """% The 2.0x-12.9x shortfall range, for reference.
Prose that says nothing about it.
"""


def test_withdrawal_comment_is_exempt_but_still_reported():
    got = [h for h in hits(WITHDRAWN_COMMENT) if h["rule"] == "shortfall-pair"]
    assert len(got) == 1
    assert got[0]["exempt"], "the withdrawal comment should be exempt"
    assert "WITHDRAWN" in got[0]["exempt"]
    assert live(WITHDRAWN_COMMENT) == []


def test_same_comment_without_the_marker_is_not_exempt():
    """The control on the exemption itself. If this passes only because the
    file is skipped, the marker is doing no work."""
    got = [h for h in live(BARE_COMMENT) if h["rule"] == "shortfall-pair"]
    assert len(got) == 1


def test_correction_note_is_exempt():
    text = ("% REV-2 CORRECTION 2026-07-26. This comment previously cited\n"
            "% results/identical_score_churn.csv and the 1,155-cell population.\n")
    assert live(text) == []


def test_supersession_mapping_is_exempt_but_a_bare_old_number_is_not():
    mapped = r"analysed cells rise from 1{,}254 to \textbf{1{,}807}."
    bare = r"computed over the 1{,}254 analysed cells."
    assert live(mapped, rel="paper/sections/m.tex") == []
    assert [h["rule"] for h in live(bare, rel="paper/sections/m.tex")] \
        == ["rev1-population"]


def test_quoted_retired_wording_is_exempt_but_asserting_it_is_not():
    quoted = ("The registration adds ``(and at the claim's own margin when it "
              "states one)'', which Amendment~2 retires.")
    asserted = "We evaluate each source against its own margin."
    assert live(quoted) == []
    assert [h["rule"] for h in live(asserted)] == ["own-margin"]


def test_allowlisted_file_is_exempt_and_says_why():
    text = "the Stated margin column and 4 of 12 claims"
    got = hits(text, rel="paper/sections/appendix_registrations.tex")
    assert got, "allowlisting must not suppress the report"
    assert all(h["exempt"] for h in got)
    assert all("machine-checked" in h["exempt"] for h in got)


def test_docs_are_downgraded_not_hidden():
    text = "K = 4 of 12 determinate claims were flagged"
    got = [h for h in hits(text, rel="docs/SOME_RECORD_2026-07-20.md", ext=".md")
           if h["rule"] == "count-4-of-12"]
    assert len(got) == 1
    assert got[0]["severity"] == "review"
    assert got[0]["note"] and "review-only" in got[0]["note"]


def test_underpowered_is_review_never_stale():
    """Background and related-work uses stay correct, so the linter flags for a
    human instead of asserting an error."""
    got = [h for h in hits("common benchmarks are underpowered")
           if h["rule"] == "underpowered"]
    assert len(got) == 1
    assert got[0]["severity"] == "review"
    assert live("common benchmarks are underpowered") == []


def test_quotation_exemption_does_not_span_a_paragraph():
    """A stray delimiter must not pull live prose into an exemption."""
    text = ('He said "something.\n\nWe evaluate against its own margin.')
    assert [h["rule"] for h in live(text)] == ["own-margin"]


# --------------------------------------------------------------------------
# 5. Context classification.
# --------------------------------------------------------------------------

def test_provenance_comment_is_its_own_context():
    """A SOURCE comment citing a superseded artifact for a number the prose
    below already corrected is the class that hides best."""
    text = ("% SOURCE: docs/CERTIFICATION_TABLES_2026-07-20.md \xa7Provenance\n"
            "% (\"analysable cells 1,155\").\n"
            "The population is the 1{,}707 analysable cells.\n")
    got = [h for h in live(text, rel="paper/sections/atlas.tex")]
    assert got
    assert {h["context"] for h in got} == {"provenance-comment"}


def test_prose_context_is_distinguished_from_comment():
    prose = "We report 0 of the 17 audited sources."
    commented = "% We report 0 of the 17 audited sources.\n"
    assert [h["context"] for h in live(prose)] == ["prose"]
    assert [h["context"] for h in live(commented)] == ["comment"]


def test_generated_and_planning_contexts():
    text = "4 of 12 claims"
    assert [h["context"] for h in hits(text, rel="paper/READING_COPY.md",
                                       ext=".md")] == ["generated-echo"]
    assert [h["context"] for h in hits(text, rel="paper/OUTLINE.md",
                                       ext=".md")] == ["planning-not-compiled"]
    assert [h["context"] for h in hits(text, rel="paper/blog/p.md",
                                       ext=".md")] == ["dated-post"]


# --------------------------------------------------------------------------
# 6. End to end over the real tree.
# --------------------------------------------------------------------------

def test_real_tree_scan_does_not_collapse():
    """Guards the way a whole-tree scan quietly becomes a no-op: an empty file
    list.

    This deliberately does NOT assert that every rule fires somewhere in the
    real tree. That assertion was here and was removed during integration,
    because it makes the suite depend on the defects surviving: it passes only
    while stale claims remain, and it fails at the moment the last instance of
    some rule is repaired. That inverts the point of the linter, and it would
    have meant the final prose fix could not land without also editing this
    test.

    Rule liveness is proved instead against fixed samples, by
    test_every_rule_has_a_sample and test_every_rule_fires_on_its_sample. Those
    catch a mistyped or dead pattern just as well and cannot rot as the tree is
    cleaned.
    """
    _, n_files = cp.check_stale_claims(cp.ROOT)
    assert n_files > 100, "scan scope collapsed to %d files" % n_files


def test_scan_scope_covers_every_required_tree():
    """Section 6 of the final checklist names LaTeX, Markdown, CSV, JSON,
    scripts, notebooks, tests, appendices, supplementary files and READMEs. A
    scope that silently narrows is a linter that silently stops looking, and
    the file count alone will not catch it while docs/ is still in scope.
    """
    scanned = {p.relative_to(cp.ROOT).as_posix()
               for p in cp.iter_source_files(cp.ROOT)}
    required = [
        "paper/main.tex", "paper/abstract.tex", "paper/sections/audit.tex",
        "paper/OUTLINE.md", "paper/READING_COPY.md", "paper/tools/README.md",
        "paper/references.bib",
        "scripts/audit_verdicts.py", "tests/test_audit_stats.py",
        "notebooks/kaggle_pilot.ipynb", "configs/main_grid_manifest.yaml",
        "flipeval/__init__.py", "pilot_eval/run.py",
        "docs/audit_claim_table.csv", "docs/atlas_pair_manifest.json",
        "README.md", "STATUS.md", "PREREGISTRATION.md",
        "packaging/README.md",
    ]
    missing = [p for p in required
               if p in _existing(required) and p not in scanned]
    assert not missing, "these are in the tree but never scanned: %s" % missing
    # blog posts and any other paper/ markdown must be in scope too
    assert any(p.startswith("paper/blog/") for p in scanned)


def _existing(paths):
    return {p for p in paths if (cp.ROOT / p).exists()}


def test_results_tree_is_out_of_scope():
    """Generated and sealed outputs are regenerated, not edited. Linting them
    would emit findings nobody is allowed to act on."""
    scanned = {p.relative_to(cp.ROOT).as_posix()
               for p in cp.iter_source_files(cp.ROOT)}
    assert not any(p.startswith("results/") for p in scanned)


def test_linter_and_its_tests_are_allowlisted():
    """Both state the forbidden tokens as literals. Without this the linter
    reports itself and can never reach OK."""
    allowed = {p for p, _, _ in cp.SCOPE_ALLOWLIST}
    assert "paper/tools/check_paper.py" in allowed
    assert "tests/test_check_paper_stale.py" in allowed
    assert "paper/tools/README.md" in allowed


def test_frozen_documents_are_allowlisted():
    allowed = {p for p, scope, _ in cp.SCOPE_ALLOWLIST if scope == "*"}
    for frozen in ["PREREGISTRATION.md",
                   "docs/AUDIT_REGISTRATION_2026-07-15.md",
                   "docs/MINIGRID_REGISTRATION_2026-07-15.md",
                   "docs/ATLAS_MINING_REGISTRATION_2026-07-15.md",
                   "docs/audit_claim_table.csv",
                   "docs/atlas_pair_manifest.json",
                   "paper/sections/appendix_registrations.tex"]:
        assert frozen in allowed, frozen


def test_every_allowlist_entry_carries_a_reason():
    for path, scope, reason in cp.SCOPE_ALLOWLIST:
        assert reason and len(reason) > 20, path
    for prefix, reason in cp.REVIEW_ONLY_PATHS:
        assert reason and len(reason) > 20, prefix


def test_report_lists_every_hit():
    """Nothing is dropped between scanning and printing."""
    lines = []
    hs = [
        {"path": "a.tex", "line": 1, "rule": "r", "text": "t", "exempt": None,
         "note": None, "severity": "stale", "context": "prose"},
        {"path": "b.tex", "line": 2, "rule": "r", "text": "t", "exempt": "why",
         "note": None, "severity": "stale", "context": "comment"},
        {"path": "c.tex", "line": 3, "rule": "r", "text": "t", "exempt": None,
         "note": None, "severity": "review", "context": "prose"},
    ]
    rc = cp.report_stale(hs, 3, out=lines.append)
    assert rc == 1
    body = "\n".join(lines)
    for name in ("a.tex", "b.tex", "c.tex"):
        assert name in body
