import tarfile
from pathlib import Path

import pandas as pd

from pilot_eval.analyze import analyze_run_directory


def test_archived_pilot_csvs_reproduced_to_six_decimals(tmp_path):
    archive = Path("results/pilot_outputs_20260711T000427Z.tar.gz")
    with tarfile.open(archive) as bundle:
        for member in bundle.getmembers():
            target = (tmp_path / member.name).resolve()
            if tmp_path.resolve() not in target.parents and target != tmp_path.resolve():
                raise ValueError(f"unsafe archive path: {member.name}")
        bundle.extractall(tmp_path)
    run_dir = tmp_path / "results/kaggle_qwen25_1p5b_public_quantized"
    expected_pairs = pd.read_csv("tests/fixtures/pilot/pair_summary.csv")
    expected_ranks = pd.read_csv("tests/fixtures/pilot/rank_instability.csv")
    actual_pairs, actual_ranks = analyze_run_directory(run_dir, bootstrap=1000, seed=0)
    pd.testing.assert_frame_equal(actual_pairs, expected_pairs, check_exact=False, atol=1e-6, rtol=0)
    pd.testing.assert_frame_equal(actual_ranks, expected_ranks, check_exact=False, atol=1e-6, rtol=0)
