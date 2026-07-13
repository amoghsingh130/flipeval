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
