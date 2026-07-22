"""Regenerate the golden fixture files.

Not a test (deliberately not named `test_*.py`, so pytest does not collect it).
Run it only when a fixture needs to change:

    python packaging/tests/make_fixtures.py

Each fixture imitates the lm-eval 0.4.x `--log_samples` line format for a
generative task: `doc_id`, `task_name`, `doc`, `target`, `resps`,
`filtered_resps`, `exact_match`. The verdict each pair is built to produce is
asserted in `test_cli.py`, so a fixture that drifts fails the suite rather than
silently changing what the tests cover.
"""
from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

TASK = "gsm8k"


def sample(
    doc_id: int,
    correct: bool,
    prediction: str,
    target: str,
    filter_name: str | None = None,
    scored: bool = True,
) -> dict:
    row = {
        "doc_id": doc_id,
        "task_name": TASK,
        "doc": {"question": f"question {doc_id}", "answer": f"reasoning #### {target}"},
        "target": target,
        "resps": [[f"chain of thought for {doc_id} #### {prediction}"]],
        "filtered_resps": [prediction],
    }
    if filter_name is not None:
        row["filter"] = filter_name
    if scored:
        row["exact_match"] = 1.0 if correct else 0.0
    return row


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row) + "\n")


def build_pair(n: int, harmful: list[int], beneficial: list[int]) -> tuple[list[dict], list[dict]]:
    """Baseline is correct on 3 of every 4 items; candidate flips the given ids.

    `harmful` ids must be baseline-correct, `beneficial` ids baseline-wrong.
    """
    baseline, candidate = [], []
    for doc_id in range(n):
        target = str(100 + doc_id)
        base_correct = doc_id % 4 != 0
        base_pred = target if base_correct else "0"
        baseline.append(sample(doc_id, base_correct, base_pred, target))

        if doc_id in harmful:
            assert base_correct, f"harmful flip {doc_id} is not baseline-correct"
            cand_correct, cand_pred = False, "999"
        elif doc_id in beneficial:
            assert not base_correct, f"beneficial flip {doc_id} is not baseline-wrong"
            cand_correct, cand_pred = True, target
        elif not base_correct and doc_id % 8 == 4:
            # wrong -> different wrong: invisible to accuracy, visible to churn.
            cand_correct, cand_pred = False, "777"
        else:
            cand_correct, cand_pred = base_correct, base_pred
        candidate.append(sample(doc_id, cand_correct, cand_pred, target))
    return baseline, candidate


def correct_ids(n: int, count: int, start: int = 0) -> list[int]:
    ids = [i for i in range(start, n) if i % 4 != 0]
    return ids[:count]


def wrong_ids(n: int, count: int, start: int = 0) -> list[int]:
    ids = [i for i in range(start, n) if i % 4 == 0]
    return ids[:count]


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    # CERTIFIED-EQUIVALENT: n=400, balanced 4 up / 4 down. Net delta 0.
    base, cand = build_pair(400, correct_ids(400, 4), wrong_ids(400, 4))
    write(FIXTURES / "equivalent_baseline.jsonl", base)
    write(FIXTURES / "equivalent_candidate.jsonl", cand)

    # DEGRADED: n=400, 30 harmful vs 5 beneficial.
    base, cand = build_pair(400, correct_ids(400, 30), wrong_ids(400, 5))
    write(FIXTURES / "degraded_baseline.jsonl", base)
    write(FIXTURES / "degraded_candidate.jsonl", cand)

    # IMPROVED: mirror image, 5 harmful vs 30 beneficial.
    base, cand = build_pair(400, correct_ids(400, 5), wrong_ids(400, 30))
    write(FIXTURES / "improved_baseline.jsonl", base)
    write(FIXTURES / "improved_candidate.jsonl", cand)

    # UNDERPOWERED: n=60, 6 harmful vs 2 beneficial. A real-looking drop that
    # neither reaches significance nor fits inside a 2-point margin.
    base, cand = build_pair(60, correct_ids(60, 6), wrong_ids(60, 2))
    write(FIXTURES / "underpowered_baseline.jsonl", base)
    write(FIXTURES / "underpowered_candidate.jsonl", cand)

    # Item-set mismatch: overlapping but unequal doc_id ranges.
    base = [sample(i, i % 4 != 0, str(100 + i), str(100 + i)) for i in range(50)]
    cand = [sample(i, i % 4 != 0, str(100 + i), str(100 + i)) for i in range(25, 75)]
    write(FIXTURES / "mismatch_baseline.jsonl", base)
    write(FIXTURES / "mismatch_candidate.jsonl", cand)

    # Multi-filter: one row per (doc, filter), the shape lm-eval actually emits
    # for a task with filter_list. strict-match voids most rows the way the
    # stock gsm8k regex does; flexible-extract scores them. Same generations,
    # different numbers -- the CLI must refuse to pick without --filter.
    for name, path in (("baseline", "multifilter_baseline"), ("candidate", "multifilter_candidate")):
        rows = []
        for doc_id in range(120):
            target = str(100 + doc_id)
            flexible_correct = doc_id % 4 != 0
            if name == "candidate" and doc_id in (1, 5, 9, 13):
                flexible_correct = False
            # strict-match rejects the '$' the model writes, so it voids many
            # rows a flexible extractor scores correct.
            strict_correct = flexible_correct and doc_id % 3 == 0
            rows.append(
                sample(doc_id, strict_correct, target if strict_correct else "[invalid]",
                       target, filter_name="strict-match")
            )
            rows.append(
                sample(doc_id, flexible_correct, target if flexible_correct else "0",
                       target, filter_name="flexible-extract")
            )
        write(FIXTURES / f"{path}.jsonl", rows)

    # Unscored: no exact_match / acc anywhere, so correctness would fall back to
    # comparing the prediction string against the gold string.
    for path in ("unscored_baseline", "unscored_candidate"):
        rows = [
            sample(doc_id, True, str(100 + doc_id), str(100 + doc_id), scored=False)
            for doc_id in range(40)
        ]
        write(FIXTURES / f"{path}.jsonl", rows)

    print(f"wrote fixtures to {FIXTURES}")


if __name__ == "__main__":
    main()
