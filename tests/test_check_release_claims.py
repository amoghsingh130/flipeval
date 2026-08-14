"""Tests for the RELEASE_CLAIMS gate.

The gate exists to stop a specific set of defects reaching a published archive.
A gate that cannot fail is worse than no gate, so every check here is exercised
in BOTH directions: the real tree must pass, and each defect must be rejected.

This is not hypothetical. The first version of C2 silently PASSED when
\\versiondoi was pointed back at the v1.0.0 DOI, because its non-greedy regex
latched onto the \\ifanon arm's one-line definition instead of the identified
arm's. It was caught only by a by-hand negative test; these tests make that
permanent.

The fixture copies the real files rather than inventing fake ones, so the tests
fail if the gate stops matching the shapes the repository actually uses.
"""

from __future__ import annotations

import importlib.util
import shutil
import stat
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "paper" / "tools" / "check_release_claims.py"

_spec = importlib.util.spec_from_file_location("check_release_claims", GATE)
crc = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(crc)


# Everything the six checks read.
FILESET = (
    "paper/main.tex",
    "paper/sections/artifacts.tex",
    "paper/sections/appendix_artifacts_detail.tex",
    "paper/audit_denominators.tex",
    "results/audit_verdicts_rev3.csv",
)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A minimal copy of the real repository, mutable per test."""
    for rel in FILESET:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst)
        # copy2 preserves mode, and results/audit_verdicts_rev3.csv is sealed
        # read-only (0444) in the real tree. That seal protects the real
        # artifact; inheriting it here made the copy immutable, so the negative
        # test that rewrites the ledger died with PermissionError instead of
        # exercising C5 -- a gate test that cannot reach its assertion. The
        # copies are this fixture's mutable subject, as its docstring says, so
        # restore write permission on them.
        dst.chmod(dst.stat().st_mode | stat.S_IWUSR)
    return tmp_path


def results(root: Path, release_tree: Path | None = None) -> dict[str, bool]:
    return {cid: ok for cid, ok, _ in crc.run_checks(root, release_tree).rows}


def detail(root: Path, cid: str) -> str:
    return next(d for c, _, d in crc.run_checks(root).rows if c == cid)


# --------------------------------------------------------------------------
# Positive: the tree as it actually stands must pass every check.
# --------------------------------------------------------------------------

def test_real_repository_passes_every_check():
    r = crc.run_checks(REPO)
    failed = [f"{cid}: {d}" for cid, ok, d in r.rows if not ok]
    assert not failed, f"the repository fails its own release gate: {failed}"


def test_fixture_tree_passes(tree: Path):
    assert all(results(tree).values())


# --------------------------------------------------------------------------
# Negative: each defect must be rejected.
# --------------------------------------------------------------------------

def test_c2_rejects_current_doi_replaced_by_v10_doi(tree: Path):
    """The regression that the first implementation missed entirely."""
    p = tree / "paper/main.tex"
    p.write_text(p.read_text().replace(crc.V11_DOI, crc.V10_DOI))
    r = results(tree)
    assert r["C2"] is False, "pointing \\versiondoi at the v1.0.0 DOI must be rejected"
    assert r["C3"] is False, "and the v1.1.0 DOI is then absent"


def test_c2_rejects_an_unrelated_doi(tree: Path):
    """Neither-DOI must fail too: C2 is not merely 'v1.0.0 absent'."""
    p = tree / "paper/main.tex"
    p.write_text(p.read_text().replace(crc.V11_DOI, "10.5281/zenodo.99999999"))
    assert results(tree)["C2"] is False


def test_c1_rejects_restored_stale_canonical_v10_sentence(tree: Path):
    p = tree / "paper/sections/artifacts.tex"
    p.write_text(p.read_text() + f"\nThe archived release resolves to the {crc.FALSE_CLAIM}.\n")
    assert results(tree)["C1"] is False


def test_c1_scans_every_paper_source_not_just_artifacts(tree: Path):
    """The claim is rejected wherever it appears, not only in its usual home."""
    p = tree / "paper/sections/appendix_artifacts_detail.tex"
    p.write_text(p.read_text() + f"\n{crc.FALSE_CLAIM}\n")
    assert results(tree)["C1"] is False


def test_c5_rejects_absent_rev3_audit_artifact(tree: Path):
    (tree / "results/audit_verdicts_rev3.csv").unlink()
    assert results(tree)["C5"] is False, "a missing rev-3 artifact must fail closed, not skip"


def test_c5_rejects_rev3_artifact_that_does_not_match_the_ledger(tree: Path):
    (tree / "results/audit_verdicts_rev3.csv").write_text("claim_id\nR01\n")
    assert results(tree)["C5"] is False


def test_c4_rejects_identifying_pdfauthor_in_the_anonymous_arm(tree: Path):
    """Routing is not sufficient: the anonymous arm's VALUE must not name anyone.

    A macro defined as the real author inside \\ifanon leaks the identity into
    the blind build's PDF info dictionary, where no reader sees it on the page.
    """
    p = tree / "paper/main.tex"
    p.write_text(p.read_text().replace(
        "\\newcommand{\\pdfauthorstring}{Anonymous authors}",
        "\\newcommand{\\pdfauthorstring}{" + crc.AUTHOR_NAME + "}"))
    assert results(tree)["C4"] is False
    assert "anon_arm_names_author=True" in detail(tree, "C4")


def test_c4_rejects_unconditional_hardcoded_author(tree: Path):
    p = tree / "paper/main.tex"
    p.write_text(p.read_text().replace(
        "pdfauthor={\\pdfauthorstring}", "pdfauthor={" + crc.AUTHOR_NAME + "}"))
    assert results(tree)["C4"] is False


def test_c4_rejects_missing_pdfauthor(tree: Path):
    p = tree / "paper/main.tex"
    p.write_text("\n".join(l for l in p.read_text().splitlines() if "pdfauthor" not in l))
    assert results(tree)["C4"] is False


def test_c4_rejects_missing_pdftitle(tree: Path):
    p = tree / "paper/main.tex"
    p.write_text("\n".join(l for l in p.read_text().splitlines() if "pdftitle" not in l))
    assert results(tree)["C4"] is False


def test_c6_rejects_private_audit_capture_in_the_release_tree(tmp_path: Path):
    rt = tmp_path / "release"
    (rt / "audit").mkdir(parents=True)
    (rt / "audit" / "audit_sources_20260731.tar.gz").write_bytes(b"private")
    r = crc.run_checks(REPO, rt)
    c6 = {cid: (ok, d) for cid, ok, d in r.rows}["C6"]
    assert c6[0] is False and "private source captures" in c6[1]


@pytest.mark.parametrize("relpath", [
    "backups/flipeval-all-refs.bundle",
    ".git/config",
    "creds/.netrc",
])
def test_c6_rejects_backups_history_and_credentials(tmp_path: Path, relpath: str):
    rt = tmp_path / "release"
    p = rt / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")
    assert crc.run_checks(REPO, rt).failed()


def test_c6_passes_on_a_clean_tree(tmp_path: Path):
    rt = tmp_path / "release"
    (rt / "audit").mkdir(parents=True)
    (rt / "audit" / "audit_verdicts_rev3.csv").write_text("ok")
    c6 = {cid: ok for cid, ok, _ in crc.run_checks(REPO, rt).rows}["C6"]
    assert c6 is True


# --------------------------------------------------------------------------
# Fail-closed: a check that cannot find its subject must FAIL, never pass.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("missing", ["paper/main.tex", "paper/sections/artifacts.tex"])
def test_missing_inputs_fail_closed(tree: Path, missing: str):
    (tree / missing).unlink()
    assert crc.run_checks(tree).failed(), f"deleting {missing} must not yield a pass"


def test_release_tree_that_does_not_exist_fails_closed(tmp_path: Path):
    c6 = {cid: ok for cid, ok, _ in crc.run_checks(REPO, tmp_path / "nope").rows}["C6"]
    assert c6 is False
