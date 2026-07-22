"""Reading lm-eval `--log_samples` files and pairing two of them.

This module is I/O, selection and validation only. It computes no statistic:
the numbers all come from `flipeval.core`, which is registered analysis code and
is imported, never modified. Sample conversion is likewise delegated to
`flipeval.io.from_lm_eval_harness` unchanged.

What is added here is the set of contracts the registered code deliberately does
not enforce, because they are wrong defaults for a general-purpose CLI even
though they are right for the registered pipeline's own callers:

* `require_identical_item_sets` -- pairing is refused across differing items.
* `resolve_filter` -- the scoring filter is never guessed on a multi-filter file.
* `require_scored_rows` -- the string-comparison correctness fallback is opt-in.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from flipeval.io import from_lm_eval_harness

Record = Mapping[str, Any]


class ItemSetMismatch(ValueError):
    """Raised when two runs were not scored on the same items.

    A comparison across differing item sets is not a paired comparison, and
    every statistic downstream of it assumes pairing.
    """


class FilterAmbiguity(ValueError):
    """Raised when a file carries several scoring filters and none was chosen.

    lm-eval logs one sample row per (doc, filter) pair, so a stock GSM8K run
    emits both `strict-match` and `flexible-extract` rows over the *same*
    generations. Those are different numbers, not different renderings of one
    number, so the tool refuses to pick.
    """


class UnscoredRows(ValueError):
    """Raised when correctness would fall back to comparing strings."""


def read_raw_samples(path: str | Path) -> list[dict[str, Any]]:
    """Read a log_samples file into a flat list of raw sample dicts.

    Mirrors the normalisation in `flipeval.io.from_lm_eval_harness` -- a bare
    JSONL list, a dict with a `samples` key, or a dict mapping task name to a
    list of samples (in which case `task_name` is injected, exactly as the
    registered reader does). Reading the raw rows is necessary because filter
    selection has to happen *before* conversion.
    """
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"no such log_samples file: {resolved}")
    text = resolved.read_text(encoding="utf-8")
    try:
        raw: Any = json.loads(text)
    except json.JSONDecodeError:
        raw = [json.loads(line) for line in text.splitlines() if line.strip()]

    samples = raw.get("samples", raw) if isinstance(raw, dict) else raw
    if isinstance(samples, dict):
        samples = [
            {"task_name": task_name, **sample}
            for task_name, task_samples in samples.items()
            for sample in task_samples
        ]
    if not isinstance(samples, list):
        raise ValueError(f"{resolved}: log must contain a list or a 'samples' mapping")
    if not samples:
        raise ValueError(f"{resolved} contained no samples")
    return samples


def available_filters(samples: Sequence[Mapping[str, Any]]) -> list[str]:
    """Distinct `filter` values present, in first-seen order."""
    seen: list[str] = []
    for sample in samples:
        name = sample.get("filter")
        if name is None:
            continue
        name = str(name)
        if name not in seen:
            seen.append(name)
    return seen


def resolve_filter(
    samples: Sequence[Mapping[str, Any]],
    requested: str | None,
    path: str | Path,
) -> list[Mapping[str, Any]]:
    """Select the rows for one scoring filter. Never guesses.

    lm-eval's stock `gsm8k` ships `filter_list: [strict-match,
    flexible-extract]` and scores the *same* generations under both. On this
    project's own Qwen2.5-1.5B run those two filters disagreed on 617 of 1,000
    rows and moved accuracy from 0.232 to 0.566. Picking one silently -- by
    index, or by a hardcoded preference for either -- would make the tool's
    headline number depend on an unstated choice, so a multi-filter file
    without `--filter` is an error.
    """
    names = available_filters(samples)

    if not names:
        # Single implicit filter, or a log that predates the field.
        if requested is not None:
            raise FilterAmbiguity(
                f"{path}: --filter {requested!r} was given but this file records "
                "no 'filter' field on any sample."
            )
        return list(samples)

    if len(names) == 1:
        only = names[0]
        if requested is not None and requested != only:
            raise FilterAmbiguity(
                f"{path}: --filter {requested!r} not present. "
                f"This file's only filter is {only!r}."
            )
        return [s for s in samples if str(s.get("filter")) == only]

    if requested is None:
        raise FilterAmbiguity(
            f"{path} carries {len(names)} scoring filters and no --filter was given: "
            f"{', '.join(repr(name) for name in names)}.\n"
            "  These score the SAME generations and are different numbers, not "
            "different views of one number.\n"
            "  On this project's Qwen2.5-1.5B GSM8K run, 'strict-match' voided 617 "
            "of 1,000 rows (336 of them answers a flexible extractor scores "
            "correct, because the model writes '#### $18'), moving accuracy from "
            "0.232 to 0.566.\n"
            "  Pass --filter <name> to state which surface you are comparing."
        )

    if requested not in names:
        raise FilterAmbiguity(
            f"{path}: --filter {requested!r} not present. "
            f"Available: {', '.join(repr(name) for name in names)}."
        )
    return [s for s in samples if str(s.get("filter")) == requested]


def _reaches_string_compare(sample: Mapping[str, Any]) -> bool:
    """True when `flipeval.io` would fall back to comparing strings.

    Mirrors the registered lookup order exactly: top-level `exact_match`, then
    top-level `acc`, then the same two inside `metrics`. If all are absent the
    registered converter compares the prediction against the gold string, which
    is a *different definition of correctness* from the one the harness scored
    with -- silently substituted. This detects that case so the caller can
    refuse rather than report numbers under a definition the user never chose.
    """
    correct = sample.get("exact_match", sample.get("acc"))
    if correct is None:
        metrics = sample.get("metrics", {})
        if isinstance(metrics, Mapping):
            correct = metrics.get("exact_match", metrics.get("acc"))
    return correct is None


def require_scored_rows(
    samples: Sequence[Mapping[str, Any]],
    path: str | Path,
    allow_string_compare: bool,
) -> None:
    """Refuse rows whose correctness would come from a string comparison."""
    if allow_string_compare:
        return
    offenders = [
        str(sample.get("doc_id", index))
        for index, sample in enumerate(samples)
        if _reaches_string_compare(sample)
    ]
    if not offenders:
        return
    shown = ", ".join(offenders[:5]) + (" ..." if len(offenders) > 5 else "")
    raise UnscoredRows(
        f"{path}: {len(offenders)} of {len(samples)} rows carry no harness metric "
        f"('exact_match' or 'acc', top-level or under 'metrics'); doc_id(s): {shown}.\n"
        "  Correctness for these rows would fall back to comparing the extracted "
        "prediction against the gold string, which is a different definition of "
        "correctness from the one the harness scored with.\n"
        "  Pass --allow-string-compare to accept that substitution deliberately."
    )


def load_log_samples(
    path: str | Path,
    filter_name: str | None = None,
    allow_string_compare: bool = False,
) -> list[dict[str, Any]]:
    """Load one lm-eval `--log_samples` file into FlipEval records."""
    resolved = Path(path)
    samples = read_raw_samples(resolved)
    selected = resolve_filter(samples, filter_name, resolved)
    if not selected:
        raise ValueError(f"{resolved}: no samples left after filter selection")
    require_scored_rows(selected, resolved, allow_string_compare)
    records = _convert(selected)
    _require_unique_item_ids(records, resolved, filter_name)
    return records


def _convert(samples: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Convert selected rows via the registered reader, unchanged.

    `flipeval.io.from_lm_eval_harness` takes a path, so the selected subset is
    written to a temporary JSONL and handed to it. This is deliberate: routing
    through the public registered entry point guarantees the conversion is
    byte-for-byte the one the registered pipeline performs, rather than a
    reimplementation of it that could drift.
    """
    with tempfile.TemporaryDirectory() as directory:
        staged = Path(directory) / "selected.jsonl"
        with staged.open("w", encoding="utf-8") as stream:
            for sample in samples:
                stream.write(json.dumps(sample) + "\n")
        return from_lm_eval_harness(staged)


def _require_unique_item_ids(
    records: Sequence[Record], path: Path, filter_name: str | None
) -> None:
    """Reject duplicate item ids inside a single file.

    `item_id` is `"{task_name}:{doc_id}"`. `doc_id` is unique only *within* a
    task, so a file concatenating two tasks without per-sample `task_name`
    (both then reading as `unknown`) would silently collide.
    """
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        item_id = str(record["item_id"])
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    if not duplicates:
        return
    sample = ", ".join(sorted(duplicates)[:5]) + (" ..." if len(duplicates) > 5 else "")
    hint = (
        ""
        if filter_name
        else " If this task ships multiple scoring filters, pass --filter."
    )
    raise ValueError(
        f"{path} has {len(duplicates)} duplicate item_id value(s): {sample}. "
        "item_id is 'task_name:doc_id'; if this file concatenates multiple tasks "
        f"without a per-sample task_name, doc_id alone is not unique.{hint}"
    )


def require_identical_item_sets(
    baseline: Sequence[Record],
    candidate: Sequence[Record],
    baseline_path: str | Path,
    candidate_path: str | Path,
) -> list[str]:
    """Fail unless both runs cover exactly the same items. Returns sorted ids.

    The registered `flipeval.core._align_pair` intersects the two id sets and
    proceeds on the overlap. That is correct for its own callers, which pair
    seeds known to share an item set. For a CLI pointed at two arbitrary files
    it is the wrong default: silently dropping non-shared items changes the
    population under test and would let a user compare a 1,000-item run against
    a 200-item run and receive a confident verdict about 200 items they did not
    ask about.
    """
    baseline_ids = {str(record["item_id"]) for record in baseline}
    candidate_ids = {str(record["item_id"]) for record in candidate}
    if baseline_ids == candidate_ids:
        return sorted(baseline_ids)

    only_baseline = sorted(baseline_ids - candidate_ids)
    only_candidate = sorted(candidate_ids - baseline_ids)
    lines = [
        "item sets differ between the two runs; this is not a paired comparison.",
        f"  {baseline_path}: {len(baseline_ids)} items",
        f"  {candidate_path}: {len(candidate_ids)} items",
        f"  shared: {len(baseline_ids & candidate_ids)}",
    ]
    if only_baseline:
        lines.append(
            f"  only in {baseline_path} ({len(only_baseline)}): "
            f"{', '.join(only_baseline[:5])}{' ...' if len(only_baseline) > 5 else ''}"
        )
    if only_candidate:
        lines.append(
            f"  only in {candidate_path} ({len(only_candidate)}): "
            f"{', '.join(only_candidate[:5])}{' ...' if len(only_candidate) > 5 else ''}"
        )
    raise ItemSetMismatch("\n".join(lines))


def align_by_item_id(
    baseline: Sequence[Record],
    candidate: Sequence[Record],
    item_ids: Sequence[str],
) -> tuple[list[Record], list[Record]]:
    """Return both record lists in a common item-id order.

    Joined on item identity, never on row order: lm-eval does not guarantee two
    runs emit samples in the same sequence, and a positional zip would silently
    mispair every item if it did not. The ordering matches the registered
    `_align_pair` (`sorted` over the id set).
    """
    baseline_map = {str(record["item_id"]): record for record in baseline}
    candidate_map = {str(record["item_id"]): record for record in candidate}
    return (
        [baseline_map[item_id] for item_id in item_ids],
        [candidate_map[item_id] for item_id in item_ids],
    )
