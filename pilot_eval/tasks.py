from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class EvalItem:
    task: str
    item_id: str
    prompt: str
    gold: str
    choices: list[str] | None = None
    metadata: dict[str, str] | None = None


MMLU_TEMPLATE = """Question: {question}
A. {a}
B. {b}
C. {c}
D. {d}
Answer:"""

GSM8K_FEWSHOT = """Question: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Answer: Natalia sold 48 / 2 = 24 clips in May. Altogether she sold 48 + 24 = 72 clips. #### 72

Question: Weng earns $12 an hour for babysitting. Yesterday, she babysat for 50 minutes. How much did she earn?
Answer: Weng earns 12 / 60 = $0.20 per minute. She worked 50 minutes, so she earned 50 * 0.20 = $10. #### 10

Question: Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need?
Answer: Betty has 100 / 2 = $50. Her grandparents give 15 * 2 = $30. She now has 50 + 15 + 30 = $95, so she needs 100 - 95 = $5 more. #### 5

"""


def load_task(name: str, split: str, limit: int | None, subjects: list[str] | None, fewshot: int) -> list[EvalItem]:
    if name == "mmlu":
        return load_mmlu(split=split, limit=limit, subjects=subjects)
    if name == "gsm8k":
        return load_gsm8k(split=split, limit=limit, fewshot=fewshot)
    raise ValueError(f"unknown task: {name}")


def load_mmlu(split: str, limit: int | None, subjects: list[str] | None) -> list[EvalItem]:
    subjects = subjects or ["abstract_algebra"]
    items: list[EvalItem] = []
    for subject in subjects:
        ds = _load_mmlu_subject(subject, split)
        for idx, row in enumerate(_take(ds, limit)):
            choices = list(row["choices"])
            answer = row["answer"]
            if isinstance(answer, int):
                gold = "ABCD"[answer]
            else:
                gold = str(answer).strip().upper()[0]
            prompt = MMLU_TEMPLATE.format(
                question=str(row["question"]).strip(),
                a=choices[0],
                b=choices[1],
                c=choices[2],
                d=choices[3],
            )
            items.append(
                EvalItem(
                    task="mmlu",
                    item_id=f"{subject}:{split}:{idx}",
                    prompt=prompt,
                    gold=gold,
                    choices=["A", "B", "C", "D"],
                    metadata={"subject": subject},
                )
            )
    return items


def _load_mmlu_subject(subject: str, split: str):
    from datasets import load_dataset

    last_error: Exception | None = None
    for dataset_name, config in [("cais/mmlu", subject), ("lukaemon/mmlu", subject)]:
        try:
            return load_dataset(dataset_name, config, split=split)
        except Exception as exc:  # pragma: no cover - depends on external dataset availability.
            last_error = exc
    raise RuntimeError(f"could not load MMLU subject {subject!r}") from last_error


def load_gsm8k(split: str, limit: int | None, fewshot: int) -> list[EvalItem]:
    jsonl_path = os.environ.get("GSM8K_JSONL")
    if jsonl_path:
        ds = _load_gsm8k_jsonl(Path(jsonl_path))
    else:
        from datasets import load_dataset

        ds = load_dataset("openai/gsm8k", "main", split=split)
    prefix = GSM8K_FEWSHOT if fewshot else ""
    items: list[EvalItem] = []
    for idx, row in enumerate(_take(ds, limit)):
        prompt = f"{prefix}Question: {str(row['question']).strip()}\nAnswer:"
        items.append(
            EvalItem(
                task="gsm8k",
                item_id=f"gsm8k:{split}:{idx}",
                prompt=prompt,
                gold=extract_gsm8k_answer(str(row["answer"])),
                choices=None,
                metadata={},
            )
        )
    return items


def _load_gsm8k_jsonl(path: Path) -> list[dict[str, str]]:
    """Load an official GSM8K JSONL when Hub-backed datasets are unavailable."""
    if not path.is_file():
        raise FileNotFoundError(f"GSM8K_JSONL does not point to a file: {path}")

    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in GSM8K_JSONL at {path}:{line_number}") from exc
            if not isinstance(row, dict) or not isinstance(row.get("question"), str) or not isinstance(row.get("answer"), str):
                raise ValueError(f"GSM8K_JSONL row at {path}:{line_number} must contain string question and answer fields")
            rows.append({"question": row["question"], "answer": row["answer"]})
    if not rows:
        raise ValueError(f"GSM8K_JSONL contains no usable rows: {path}")
    return rows


def _take(ds: Iterable, limit: int | None):
    for idx, row in enumerate(ds):
        if limit is not None and idx >= limit:
            break
        yield row


def extract_gsm8k_answer(text: str) -> str:
    marker = re.search(r"####\s*([-+]?\d[\d,]*(?:\.\d+)?)", text)
    if marker:
        return _clean_number(marker.group(1))
    numbers = re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
    return _clean_number(numbers[-1]) if numbers else ""


def _clean_number(value: str) -> str:
    value = value.replace(",", "").strip()
    if value.endswith(".0"):
        value = value[:-2]
    return value
