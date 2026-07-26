"""The eval runner must fail closed on a missing grid declaration.

Regression tests for incident 24 (2026-07-25). `run_minigrid.sbatch` carried
defaults for MINIGRID_CONFIG and MINIGRID_MODELS. A resubmit of ten escalation
cells omitted both, fell through to the mini-grid defaults, and opened ten cells
of the sealed, archived, paper-cited mini-grid in write mode. Only the 0444 seal
on those JSONLs turned a truncation into a PermissionError.

`verify_minigrid.sbatch` had been hardened to ${VAR:?} weeks earlier, so the
reader failed closed while the writer failed open. These tests pin the writer's
half: an undeclared grid must abort BEFORE the container starts, because by the
time pilot_eval.run opens an output path the damage is already done.

The tests drive the real script with a stubbed `srun` on PATH. The stub writes a
sentinel, so "did execution reach the container?" is a file-existence check
rather than an assertion about output text.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "slurm" / "run_minigrid.sbatch"

GRID_VARS = ("MINIGRID_CONFIG", "MINIGRID_MODELS")


@pytest.fixture()
def harness(tmp_path):
    """A sandbox in which the script can run without a cluster.

    Returns (run, sentinel): `run` invokes the script with a given environment
    overlay, `sentinel` is the path the stubbed `srun` touches if execution ever
    reaches the container invocation.
    """
    project = tmp_path / "project"
    (project / "scripts" / "slurm").mkdir(parents=True)

    # Stub env.sh: the real one resolves cluster paths and module state.
    (project / "scripts" / "slurm" / "env.sh").write_text(
        "export PROJECT_DIR='%s'\n"
        "export SCRATCH_DIR='%s'\n"
        "export IMAGE='%s/flipeval.sif'\n" % (project, tmp_path / "scratch", tmp_path / "scratch"),
        encoding="utf-8",
    )

    sentinel = tmp_path / "srun_was_reached"
    bindir = tmp_path / "bin"
    bindir.mkdir()
    stub = bindir / "srun"
    stub.write_text("#!/bin/bash\ntouch '%s'\nexit 0\n" % sentinel, encoding="utf-8")
    stub.chmod(0o755)

    workdir = tmp_path / "workdir"
    workdir.mkdir()

    def run(**overlay):
        env = {
            "PATH": "%s:%s" % (bindir, os.environ.get("PATH", "/usr/bin:/bin")),
            "HOME": str(tmp_path),
            "PROJECT_DIR": str(project),
            "SLURM_ARRAY_TASK_ID": "13",
        }
        for key, value in overlay.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=workdir,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    return run, sentinel


def _declared(**overrides):
    env = {
        "MINIGRID_CONFIG": "/workspace/configs/pace_escalation_h3.yaml",
        "MINIGRID_MODELS": "qwen25-7b llama31-8b",
    }
    env.update(overrides)
    return env


# ---- the positive control -------------------------------------------------
# Without this, a guard that always aborts would pass every test below.


def test_a_fully_declared_grid_reaches_the_container(harness):
    run, sentinel = harness
    result = run(**_declared())
    assert result.returncode == 0, result.stderr
    assert sentinel.exists(), "a correctly declared grid must still run"
    assert "config=/workspace/configs/pace_escalation_h3.yaml" in result.stdout
    assert "models=qwen25-7b llama31-8b" in result.stdout


# ---- the incident-24 guards ------------------------------------------------


@pytest.mark.parametrize("missing", GRID_VARS)
def test_an_undeclared_grid_aborts_before_the_container_starts(harness, missing):
    """The exact shape of the 11485972 submission: a grid var simply absent."""
    run, sentinel = harness
    result = run(**_declared(**{missing: None}))
    assert result.returncode != 0, "an unset %s must abort, not fall through" % missing
    assert not sentinel.exists(), (
        "%s was unset and execution still reached the container; "
        "by then pilot_eval.run decides an output path from the config" % missing
    )
    assert missing in result.stderr


@pytest.mark.parametrize("missing", GRID_VARS)
def test_an_empty_grid_declaration_is_also_refused(harness, missing):
    """`--export=ALL` with an exported-but-empty var must not read as declared."""
    run, sentinel = harness
    result = run(**_declared(**{missing: ""}))
    assert result.returncode != 0
    assert not sentinel.exists()


@pytest.mark.parametrize("models", ["qwen25-7b", "a b c", "qwen25-7b llama31-8b extra"])
def test_a_model_list_of_the_wrong_length_is_refused(harness, models):
    """The idx->cell map assumes 2 models x 22 variants.

    A shorter list would index past the array and hand pilot_eval.run an empty
    --model-tag; a longer one would silently drop cells.
    """
    run, sentinel = harness
    result = run(**_declared(MINIGRID_MODELS=models))
    assert result.returncode != 0
    assert not sentinel.exists()
    assert "exactly 2 model tags" in result.stderr


def test_a_missing_array_index_is_refused(harness):
    """The script has no single-cell mode; an unset index must not become cell 0."""
    run, sentinel = harness
    result = run(SLURM_ARRAY_TASK_ID=None, **_declared())
    assert result.returncode != 0
    assert not sentinel.exists()


# ---- the defaults must not come back ---------------------------------------


@pytest.mark.parametrize("var", GRID_VARS)
def test_the_runner_declares_no_default_grid(var):
    """Static guard on the standing rule: no job script is ever given a default grid.

    A behavioural test cannot catch a default reintroduced alongside a guard, so
    pin the source text too.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"${%s:?' % var in source, "%s must be required via ${VAR:?}" % var
    assert "${%s:-" % var not in source, "%s must not have a fallback default" % var


def test_the_validator_and_the_runner_agree_on_required_grid_vars():
    """The reader was hardened first; the writer must not drift behind it again."""
    validator = (REPO_ROOT / "scripts" / "slurm" / "verify_minigrid.sbatch").read_text(
        encoding="utf-8"
    )
    runner = SCRIPT.read_text(encoding="utf-8")
    for var in GRID_VARS:
        assert '"${%s:?' % var in validator
        assert '"${%s:?' % var in runner
