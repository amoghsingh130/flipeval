"""Golden regression on the atlas revision: rev-1 gives R01 n_req 1,936, rev-2 gives 2,010.

final-checklist §4: "Add a golden test showing that rev-1 produces the expected
1,936 value and rev-2 the expected 2,010 value for R01."

The defect being pinned is the `--atlas` default. Until 682185d it was
`results/atlas_cells_summary.csv`, the REV-1 file, superseded by rev-2 on
2026-07-21. Run against rev-1 the recomputation imputes R01 from 484 GPTQ 4-bit
cells at median 0.125201 instead of rev-2's 792 at 0.130000, requires 1,936
items instead of 2,010, and exits 0 with a complete, self-consistent, silently
wrong result set.

Nothing downstream would surface that. R01 is below the planning threshold under
BOTH revisions, so the verdict string, K, and the robustness classification are
byte-identical across the two; only the required-n number moves. A test written
against the verdict is a test that cannot fail, which is why the checklist asks
for one against the number. `test_the_r01_verdict_is_identical_under_both_revisions`
below pins that fact so the reason for this file cannot be lost.

The revision is selected in exactly one place: the atlas path handed to
`compute_rows`, which `main()` takes from the required `--atlas` argument. There
is no revision flag, no environment variable and no module-level constant. Both
atlas files remain in `results/`, so the comparison stays runnable rather than
being asserted from a changelog.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from scripts.audit_stats import (
    load_atlas_cells,
    nearest_cell_discordance,
    paired_flip_sd,
    required_n_for_tost,
)
from scripts.audit_verdicts import REGISTERED_MARGIN_PP, compute_rows

CLAIM_TABLE = Path("docs/audit_claim_table.csv")

# The superseded revision. Kept, not deleted, so a reversion is detectable by
# running it rather than by reading a commit message.
ATLAS_REV1 = Path("results/atlas_cells_summary.csv")
ATLAS_REV2 = Path("results/atlas_cells_summary_rev2.csv")

# The sealed, paper-cited rev-3 verdict set, generated from rev-2 (job 11591245).
SEALED_REV3 = Path("results/audit_verdicts_rev3.csv")

R01_REPORTED_N = 1838
R01_REQUIRED_N_REV1 = 1936
R01_REQUIRED_N_REV2 = 2010

REQUIRED_N_COLUMN = f"v2_required_n_paired_{REGISTERED_MARGIN_PP:g}pp"


def _r01(atlas: Path) -> dict:
    return {r["claim_id"]: r for r in compute_rows(CLAIM_TABLE, atlas)}["R01"]


# ---------------------------------------------------------------------------
# The golden numbers
# ---------------------------------------------------------------------------

def test_r01_required_n_is_1936_under_rev1_and_2010_under_rev2():
    """The same code, the same frozen claim table, one changed argument.

    Both calls go through `compute_rows` unmodified; the only difference is the
    atlas path. If a rev-1 default ever returns, or the two files are swapped,
    the value moves by 74 items and this fails.
    """
    rev1, rev2 = _r01(ATLAS_REV1), _r01(ATLAS_REV2)

    assert rev1[REQUIRED_N_COLUMN] == R01_REQUIRED_N_REV1
    assert rev2[REQUIRED_N_COLUMN] == R01_REQUIRED_N_REV2
    assert rev1[REQUIRED_N_COLUMN] != rev2[REQUIRED_N_COLUMN]

    # Reported n is an input from the frozen table and must not move with the atlas.
    assert rev1["n"] == rev2["n"] == R01_REPORTED_N


def test_the_required_n_gap_is_entirely_the_imputed_discordance():
    """Reproduce both numbers from their inputs, so a coincidental match fails.

    n_req = ceil((z * sqrt(d) / margin)^2) with d the median of the matched
    tier. Recomputing it from the tier median alone must land on the same two
    integers, which pins that the atlas revision reaches the requirement only
    through the imputation and not through some other changed column.
    """
    margin = REGISTERED_MARGIN_PP / 100.0
    for atlas, expected in ((ATLAS_REV1, R01_REQUIRED_N_REV1), (ATLAS_REV2, R01_REQUIRED_N_REV2)):
        match = nearest_cell_discordance(load_atlas_cells(atlas), "gptq", 4, "piqa")
        assert required_n_for_tost(paired_flip_sd(match.discordance), margin) == expected


def test_the_rev1_and_rev2_imputations_share_a_tier_and_differ_in_support():
    """Same match tier, different cell population: 484 cells at 0.125201 against
    792 at 0.130000. Pinned because a silent edit to either atlas file would
    move the golden numbers without touching a line of code."""
    rev1, rev2 = _r01(ATLAS_REV1), _r01(ATLAS_REV2)

    assert rev1["discordance_match_tier"] == rev2["discordance_match_tier"] == "family+bits"
    assert (rev1["discordance_n_cells"], rev1["imputed_discordance"]) == (484, 0.125201)
    assert (rev2["discordance_n_cells"], rev2["imputed_discordance"]) == (792, 0.13)


def test_the_r01_verdict_is_identical_under_both_revisions():
    """Why the golden test has to be on the number.

    R01 is below the planning threshold at 2 pp under rev-1 and rev-2 alike, so
    every categorical output agrees and a reversion produces no visible symptom.
    This test fails if that ever stops being true, at which point the comment at
    the top of this file needs rewriting rather than the assertion relaxing.
    """
    rev1, rev2 = _r01(ATLAS_REV1), _r01(ATLAS_REV2)

    assert rev1["verdict"] == rev2["verdict"] == "below planning threshold at 2pp"
    assert rev1[f"v2_underpowered_paired_{REGISTERED_MARGIN_PP:g}pp"] is True
    assert rev2[f"v2_underpowered_paired_{REGISTERED_MARGIN_PP:g}pp"] is True
    assert rev1["robustness"] == rev2["robustness"] == "imputation-sensitive"


# ---------------------------------------------------------------------------
# The whole artifact, and the mechanism that selects the revision
# ---------------------------------------------------------------------------

def test_rev2_recomputation_reproduces_the_sealed_rev3_artifact_byte_for_byte():
    """The broadest form of the same regression.

    R01's required n is one cell of a table the paper cites and Zenodo carries.
    Rebuilding it from the frozen claim table and the rev-2 atlas must give back
    the sealed file exactly, so any input swap, column rename or rounding change
    fails here even when it leaves R01 alone.
    """
    rows = compute_rows(CLAIM_TABLE, ATLAS_REV2)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    rebuilt = buffer.getvalue().replace("\r\n", "\n")

    assert rebuilt == SEALED_REV3.read_text(encoding="utf-8")
    assert f"{R01_REQUIRED_N_REV2}" in rebuilt, "guard against this passing on an empty rebuild"


def test_the_atlas_revision_has_no_source_other_than_the_argument():
    """final-checklist §4: require `--atlas` and `--output`, no silent defaults.

    This is the mechanism the golden numbers above depend on. `compute_rows`
    takes the atlas as a positional path and neither entry point may supply one,
    so choosing rev-1 has to be an explicit act by an operator.
    """
    import scripts.audit_verdicts as verdicts
    import scripts.certification_tables as tables

    for module in (verdicts, tables):
        source = Path(module.__file__).read_text(encoding="utf-8")
        for option in ('"--atlas"', '"--output"'):
            assert f"parser.add_argument({option}, required=True" in source, (
                f"{module.__name__} must require {option}")
        assert 'add_argument("--atlas", default' not in source
        assert 'add_argument("--output", default' not in source

    # And no module-level constant reintroduces the rev-1 path by another route.
    for module in (verdicts, tables):
        for name, value in vars(module).items():
            if isinstance(value, str) and value.endswith("atlas_cells_summary.csv"):
                raise AssertionError(f"{module.__name__}.{name} names the rev-1 atlas")
