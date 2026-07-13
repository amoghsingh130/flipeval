import json
import subprocess
import sys

from flipeval.io import from_lm_eval_harness


def test_harness_loglikelihood_and_generation_conversion():
    mmlu = from_lm_eval_harness("tests/fixtures/lm_eval_mmlu_baseline.json")
    gsm8k = from_lm_eval_harness("tests/fixtures/lm_eval_gsm8k.jsonl")
    assert [record["prediction"] for record in mmlu] == ["B", "A", "D"]
    assert [record["correct"] for record in gsm8k] == [True, False, True]


def test_cli_compares_harness_logs_end_to_end(tmp_path):
    output = tmp_path / "summary.csv"
    result = subprocess.run(
        [sys.executable, "-m", "flipeval", "compare", "tests/fixtures/lm_eval_mmlu_baseline.json", "tests/fixtures/lm_eval_mmlu_method.json", "--format", "lm-eval", "--bootstrap", "10", "--output", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert output.exists()
    assert '"mcnemar_b_harmful": 1' in result.stdout


def test_cli_runs_paired_seed_bootstrap_end_to_end(tmp_path):
    paths = {}
    values = {
        "gptq0": [True, True, False, False],
        "gptq1": [True, True, True, False],
        "awq0": [True, False, False, False],
        "awq1": [True, True, False, False],
    }
    for name, correct in values.items():
        path = tmp_path / f"{name}.jsonl"
        path.write_text(
            "".join(
                json.dumps({"item_id": str(index), "prediction": str(value), "correct": value}) + "\n"
                for index, value in enumerate(correct)
            ),
            encoding="utf-8",
        )
        paths[name] = path
    output = tmp_path / "hierarchical.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "flipeval",
            "paired-seeds",
            "--first",
            f"0={paths['gptq0']}",
            "--first",
            f"1={paths['gptq1']}",
            "--second",
            f"0={paths['awq0']}",
            "--second",
            f"1={paths['awq1']}",
            "--expected-seeds",
            "2",
            "--bootstrap",
            "20",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(output.read_text())
    assert summary["seed_labels"] == ["0", "1"]
    assert summary["full_sample_winner"] == "gptq"
    assert summary["bootstrap_replicates"] == 20
    assert "joint_exact_tie_rate" in summary
    assert "Wrote" in result.stdout
