#!/usr/bin/env python3
"""Generate the synthetic lm-evaluation-harness fixture used by examples/README.md.

The fixture exists so the end-to-end recipe is runnable with no GPU, no model
download and no harness install. It writes two directories laid out the way
`lm_eval --output_path DIR --log_samples` lays them out:

    DIR/<model>/samples_<task>_<timestamp>.jsonl

with the v0.4.x sample schema (`doc_id`, `doc`, `target`, `filter`, `resps`,
`filtered_resps`, `exact_match`). Only the fields FlipEval reads are populated;
the harness writes more, and nothing here depends on the rest.

WHAT IT IS AND IS NOT. The numbers are drawn from a fixed seed to illustrate the
phenomenon the toolkit measures -- a small net delta sitting on much larger
per-item churn -- and they are a *simulation*, not a measurement of any model.
No paper number is derived from this file, and none should be.

Regenerate with:  python3 examples/make_fixture.py
Output is deterministic: re-running it produces byte-identical files.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

TASK = "mmlu"
TIMESTAMP = "2026-08-13T00-00-00.000000"
CHOICES = ["A", "B", "C", "D"]
N_ITEMS = 400

# Per-item transition probabilities from the baseline's correctness state. The
# two flip directions are close to equal, which is exactly the cancellation the
# paper is about: the net delta is the small residue of two large opposing
# quantities.
P_BASELINE_CORRECT = 0.62
P_CORRECT_TO_WRONG = 0.11
P_WRONG_TO_CORRECT = 0.13
P_WRONG_TO_OTHER_WRONG = 0.35


def build(seed: int = 20260813) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    baseline: list[dict] = []
    compressed: list[dict] = []
    for doc_id in range(N_ITEMS):
        gold = CHOICES[rng.randrange(len(CHOICES))]
        wrong = [choice for choice in CHOICES if choice != gold]
        base_correct = rng.random() < P_BASELINE_CORRECT
        base_answer = gold if base_correct else rng.choice(wrong)

        if base_correct:
            if rng.random() < P_CORRECT_TO_WRONG:
                comp_correct, comp_answer = False, rng.choice(wrong)
            else:
                comp_correct, comp_answer = True, gold
        else:
            if rng.random() < P_WRONG_TO_CORRECT:
                comp_correct, comp_answer = True, gold
            elif rng.random() < P_WRONG_TO_OTHER_WRONG:
                others = [choice for choice in wrong if choice != base_answer]
                comp_correct, comp_answer = False, rng.choice(others)
            else:
                comp_correct, comp_answer = False, base_answer

        baseline.append(_sample(doc_id, gold, base_answer, base_correct))
        compressed.append(_sample(doc_id, gold, comp_answer, comp_correct))
    return baseline, compressed


def _sample(doc_id: int, gold: str, answer: str, correct: bool) -> dict:
    """One lm-eval v0.4.x --log_samples row, with the fields FlipEval reads."""
    return {
        "doc_id": doc_id,
        "task_name": TASK,
        "doc": {"question": f"synthetic item {doc_id}", "choices": CHOICES},
        "target": gold,
        "filter": "strict-match",
        "output_type": "generate_until",
        "resps": [[f"The answer is {answer}."]],
        "filtered_resps": [answer],
        "exact_match": 1.0 if correct else 0.0,
    }


def write(root: Path) -> None:
    baseline, compressed = build()
    for model, rows in (("fp16-baseline", baseline), ("gptq-4bit", compressed)):
        directory = root / model / "synthetic__model"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"samples_{TASK}_{TIMESTAMP}.jsonl"
        with path.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
        print(f"wrote {path} ({len(rows)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "runs",
        help="Directory to write the two synthetic run trees into.",
    )
    write(parser.parse_args().out)


if __name__ == "__main__":
    main()
