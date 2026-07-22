"""Reading lm-eval `--log_samples` files and pairing two of them.

This module is I/O and validation only. It does not compute any statistic: the
numbers all come from `flipeval.core`, which is registered analysis code and is
imported, never modified.

The parsing itself is delegated to `flipeval.io.from_lm_eval_harness`, which
already understands the lm-eval 0.4.x sample layout (`doc_id`, `filtered_resps`,
`resps`, `exact_match`/`acc`, and the multiple-choice loglikelihood form). What
is added here is the *pairing contract* the registered code deliberately does
not enforce -- see `require_identical_item_sets`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from flipeval.io import from_lm_eval_harness

Record = Mapping[str, Any]


class ItemSetMismatch(ValueError):
    """Raised when two runs were not scored on the same items.

    A comparison across differing item sets is not a paired comparison, and
    every statistic downstream of it assumes pairing. This is a hard error
    rather than a warning for that reason.
    """


def load_log_samples(path: str | Path) -> list[dict[str, Any]]:
    """Load one lm-eval `--log_samples` file into FlipEval records."""
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"no such log_samples file: {resolved}")
    records = from_lm_eval_harness(resolved)
    if not records:
        raise ValueError(f"{resolved} contained no samples")
    _require_unique_item_ids(records, resolved)
    return records


def _require_unique_item_ids(records: Sequence[Record], path: Path) -> None:
    """Reject duplicate item ids inside a single file.

    `item_id` is `"{task_name}:{doc_id}"`. `doc_id` is only unique *within* a
    task, so a file that concatenates two tasks without per-sample `task_name`
    (both then reading as `unknown`) would silently collide. The registered
    `_record_map` would also reject this, but it would do so after both files
    were read, with a message that does not say which file was at fault.
    """
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        item_id = str(record["item_id"])
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    if duplicates:
        sample = ", ".join(sorted(duplicates)[:5])
        raise ValueError(
            f"{path} has {len(duplicates)} duplicate item_id value(s): {sample}"
            f"{' ...' if len(duplicates) > 5 else ''}. "
            "item_id is 'task_name:doc_id'; if this file concatenates multiple "
            "tasks without a per-sample task_name, doc_id alone is not unique."
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
    seeds known to share an item set. For a general-purpose CLI pointed at two
    arbitrary files it is the wrong default: silently dropping the non-shared
    items changes the population under test and would let a user compare a
    1,000-item run against a 200-item run and receive a confident verdict about
    200 items they did not ask about.

    So the check happens *here*, before `compare` is called, and the registered
    behaviour is left exactly as it is.
    """
    baseline_ids = {str(record["item_id"]) for record in baseline}
    candidate_ids = {str(record["item_id"]) for record in candidate}
    if baseline_ids == candidate_ids:
        return sorted(baseline_ids)

    only_baseline = sorted(baseline_ids - candidate_ids)
    only_candidate = sorted(candidate_ids - baseline_ids)
    shared = len(baseline_ids & candidate_ids)
    lines = [
        "item sets differ between the two runs; this is not a paired comparison.",
        f"  {baseline_path}: {len(baseline_ids)} items",
        f"  {candidate_path}: {len(candidate_ids)} items",
        f"  shared: {shared}",
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

    Joined on item identity, never on row order: lm-eval does not guarantee
    that two runs emit samples in the same sequence, and a positional zip would
    silently mispair every item if it did not. The ordering matches the
    registered `_align_pair` (`sorted` over the id set), so the arrays this
    produces are the same arrays `compare` builds internally.
    """
    baseline_map = {str(record["item_id"]): record for record in baseline}
    candidate_map = {str(record["item_id"]): record for record in candidate}
    return (
        [baseline_map[item_id] for item_id in item_ids],
        [candidate_map[item_id] for item_id in item_ids],
    )
