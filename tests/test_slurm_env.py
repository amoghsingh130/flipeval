"""Tests for scripts/slurm/env.sh and a representative released caller.

env.sh used to read `PROJECT_DIR="${PROJECT_DIR:-$HOME/ps-compressedlm-0/flipeval}"`.
Every job that sourced it therefore acted on THAT checkout when the variable was
unset, and on 2026-08-07 the in-image test gate certified the wrong tree and
exited 0 because of it (incident 29).

These tests run the real shell scripts as subprocesses. A shell guard that is
only read, never executed, is not a guard.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ENV_SH = REPO / "scripts" / "slurm" / "env.sh"
SLURM = REPO / "scripts" / "slurm"

MARKERS = ("pyproject.toml", "tests", "flipeval", "scripts/slurm/env.sh")


def run(script: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Execute a shell script with a controlled environment."""
    base = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/root")}
    base.update(env or {})
    return subprocess.run(["bash", str(script)], env=base, capture_output=True, text=True, timeout=120)


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """A minimal tree that satisfies env.sh's repository-root markers."""
    root = tmp_path / "repo"
    (root / "tests").mkdir(parents=True)
    (root / "flipeval").mkdir()
    (root / "scripts" / "slurm").mkdir(parents=True)
    (root / "container").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='fake'\n")
    (root / "tests" / "test_placeholder.py").write_text("def test_x(): pass\n")
    shutil.copy2(ENV_SH, root / "scripts" / "slurm" / "env.sh")
    # a stand-in "image" plus a matching recorded digest
    img = tmp_path / "flipeval.sif"
    img.write_bytes(b"not really a container, but hashable")
    (root / "container" / "flipeval.sif.sha256").write_text(
        f"{hashlib.sha256(img.read_bytes()).hexdigest()}  {img}\n")
    return root


def good_env(fake_repo: Path, tmp_path: Path, **over: str) -> dict[str, str]:
    e = {
        "PROJECT_DIR": str(fake_repo),
        "SCRATCH_DIR": str(tmp_path / "scratch"),
        "IMAGE": str(tmp_path / "flipeval.sif"),
        "HF_TOKEN_PATH": str(tmp_path / "no-such-token"),
    }
    e.update(over)
    return e


# --------------------------------------------------------------------------
# PROJECT_DIR must fail closed.
# --------------------------------------------------------------------------

def test_env_sh_aborts_when_project_dir_unset(fake_repo: Path, tmp_path: Path):
    e = good_env(fake_repo, tmp_path)
    del e["PROJECT_DIR"]
    r = run(fake_repo / "scripts/slurm/env.sh", e)
    assert r.returncode == 2
    assert "PROJECT_DIR is not set" in r.stderr


def test_env_sh_aborts_when_project_dir_empty(fake_repo: Path, tmp_path: Path):
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path, PROJECT_DIR=""))
    assert r.returncode == 2
    assert "PROJECT_DIR is not set" in r.stderr


def test_env_sh_aborts_when_project_dir_does_not_exist(fake_repo: Path, tmp_path: Path):
    r = run(fake_repo / "scripts/slurm/env.sh",
            good_env(fake_repo, tmp_path, PROJECT_DIR=str(tmp_path / "nope")))
    assert r.returncode == 2
    assert "does not exist" in r.stderr


def test_env_sh_aborts_on_an_unrelated_directory(fake_repo: Path, tmp_path: Path):
    unrelated = tmp_path / "elsewhere"
    unrelated.mkdir()
    r = run(fake_repo / "scripts/slurm/env.sh",
            good_env(fake_repo, tmp_path, PROJECT_DIR=str(unrelated)))
    assert r.returncode == 2
    assert "not a flipeval repository root" in r.stderr


def test_env_sh_aborts_on_a_subdirectory_rather_than_the_root(fake_repo: Path, tmp_path: Path):
    r = run(fake_repo / "scripts/slurm/env.sh",
            good_env(fake_repo, tmp_path, PROJECT_DIR=str(fake_repo / "scripts")))
    assert r.returncode == 2
    assert "not a flipeval repository root" in r.stderr


@pytest.mark.parametrize("marker", MARKERS)
def test_env_sh_aborts_when_any_root_marker_is_missing(fake_repo: Path, tmp_path: Path, marker: str):
    target = fake_repo / marker
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    r = run(ENV_SH, good_env(fake_repo, tmp_path))
    assert r.returncode == 2, f"a tree missing '{marker}' must be rejected"


def test_env_sh_accepts_a_valid_root(fake_repo: Path, tmp_path: Path):
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path))
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
    assert "project:" in r.stdout


def test_env_sh_resolves_the_path(fake_repo: Path, tmp_path: Path):
    """pwd -P, so two spellings of one tree cannot read as two trees."""
    messy = f"{fake_repo}/./scripts/../"
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path, PROJECT_DIR=messy))
    assert r.returncode == 0
    assert str(fake_repo.resolve()) in r.stdout
    assert "/./" not in r.stdout.split("project:")[1].split("\n")[0]


# --------------------------------------------------------------------------
# IMAGE selects the environment cell and is verified by digest.
# --------------------------------------------------------------------------

def test_env_sh_rejects_an_image_whose_digest_does_not_match(fake_repo: Path, tmp_path: Path):
    (tmp_path / "flipeval.sif").write_bytes(b"a DIFFERENT environment cell")
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path))
    assert r.returncode == 2
    assert "digest mismatch" in r.stderr


def test_env_sh_fails_closed_when_no_digest_is_recorded(fake_repo: Path, tmp_path: Path):
    (fake_repo / "container" / "flipeval.sif.sha256").unlink()
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path))
    assert r.returncode == 2
    assert "no recorded image digest" in r.stderr, "a missing record must fail, not skip"


def test_env_sh_fails_closed_on_an_empty_digest_record(fake_repo: Path, tmp_path: Path):
    (fake_repo / "container" / "flipeval.sif.sha256").write_text("\n")
    r = run(fake_repo / "scripts/slurm/env.sh", good_env(fake_repo, tmp_path))
    assert r.returncode == 2


# --------------------------------------------------------------------------
# A representative released caller, and a repo-wide regression guard.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("script", ["run_tests.sbatch", "verify_minigrid.sbatch", "run_minigrid.sbatch"])
def test_released_callers_abort_without_project_dir(script: str, tmp_path: Path):
    r = run(SLURM / script, {"SCRATCH_DIR": str(tmp_path)})
    assert r.returncode != 0, f"{script} ran without PROJECT_DIR"
    assert "PROJECT_DIR" in (r.stderr + r.stdout)


# `${VAR:-}` -- the EMPTY default -- is the idiomatic safe probe for an unset
# variable under `set -u`. It supplies no value and is not what the rule forbids.
# Only a default that SUPPLIES a value can silently select the wrong tree, so the
# pattern requires at least one character before the closing brace.
VALUE_DEFAULT = r"\$\{%s:-[^}]"


def test_no_released_script_still_defaults_project_dir():
    """The regression guard: the defect was one string, in many files."""
    offenders = []
    for p in sorted(list(SLURM.glob("*.sbatch")) + list(SLURM.glob("*.sh"))):
        for n, line in enumerate(p.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if re.search(VALUE_DEFAULT % "PROJECT_DIR", line):
                offenders.append(f"{p.name}:{n}")
    assert not offenders, f"PROJECT_DIR value-default reintroduced at: {offenders}"


def test_empty_default_probe_is_not_treated_as_a_defect():
    """Guards the guard: ${PROJECT_DIR:-} must not be flagged, ${PROJECT_DIR:-/x} must."""
    assert not re.search(VALUE_DEFAULT % "PROJECT_DIR", '[ -n "${PROJECT_DIR:-}" ]')
    assert re.search(VALUE_DEFAULT % "PROJECT_DIR", 'X="${PROJECT_DIR:-$HOME/flipeval}"')


def test_no_released_script_defaults_a_grid_or_results_selector():
    """Selectors named by the no-defaults rule must never carry `:-`."""
    banned = ("MINIGRID_CONFIG", "MINIGRID_RESULTS", "MINIGRID_MODELS", "MINIGRID_CELLS",
              "MINIGRID_OUTPUT", "AUDIT_CLAIM_TABLE", "AUDIT_ATLAS", "AUDIT_OUTPUT")
    offenders = []
    for p in sorted(list(SLURM.glob("*.sbatch")) + list(SLURM.glob("*.sh"))):
        for n, line in enumerate(p.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for var in banned:
                if re.search(VALUE_DEFAULT % var, line):
                    offenders.append(f"{p.name}:{n} {var}")
    assert not offenders, f"source/sink selector given a default at: {offenders}"
