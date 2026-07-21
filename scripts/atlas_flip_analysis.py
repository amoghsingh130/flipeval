"""Atlas flip analysis over the frozen public-data pair manifest.

Implements sections 4-6 of docs/ATLAS_MINING_REGISTRATION_2026-07-15.md against
docs/atlas_pair_manifest.json (frozen by commit f06348f). Exclusion decisions
are computed strictly before any metric, and every enumerated cell is written
regardless of outcome. Statistics come from flipeval.compare (registered suite:
net delta, flip rates, churn, exact two-sided McNemar, TOST at the 2 pp margin,
MDD at 80% power, required-n).
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from flipeval.core import compare

TOST_MARGIN = 0.02
PROMPT_PASS_THRESHOLD = 0.99
S2_METRIC_PRIORITY = ("acc_norm", "exact_match", "acc", "prompt_level_strict_acc")
HF_TREE = "https://huggingface.co/api/datasets/{repo}/tree/main?recursive=true"
HF_RESOLVE = "https://huggingface.co/datasets/{repo}/resolve/main/{path}"


class CellSkip(Exception):
    """A cell that cannot be analyzed; recorded in the exclusion table."""


# ---------------------------------------------------------------------------
# Section 4.1: join-key deduplication and joining
# ---------------------------------------------------------------------------

def dedupe_join_keys(rows: Sequence[Mapping[str, Any]], key_of) -> tuple[dict[str, Mapping[str, Any]], int]:
    """Drop every row whose join key occurs more than once; return (map, dropped)."""
    counts: dict[str, int] = {}
    for row in rows:
        key = key_of(row)
        if key is None:
            continue
        counts[str(key)] = counts.get(str(key), 0) + 1
    kept: dict[str, Mapping[str, Any]] = {}
    dropped = 0
    for row in rows:
        key = key_of(row)
        if key is None:
            dropped += 1
            continue
        key = str(key)
        if counts[key] > 1:
            dropped += 1
        else:
            kept[key] = row
    return kept, dropped


def _no_join_reason(
    base_map: Mapping[str, Any],
    quant_map: Mapping[str, Any],
    base_rows: Sequence[Mapping[str, Any]],
    quant_rows: Sequence[Mapping[str, Any]],
) -> str:
    """Root-cause text for an empty join (F4).

    Rev-1 recorded the bare symptom "no joinable items" and, worse, discarded
    the join entirely when a later CellSkip fired, so an unreadable join key was
    filed under whatever error surfaced next. That lossiness is what hid F2 for
    six days. Distinguish the causes so an exclusion is auditable from the
    archived cell alone.
    """
    base_null = not base_map and base_rows
    quant_null = not quant_map and quant_rows
    if base_null and quant_null:
        return ("join key absent on both sides: no `hashes.example` and no `example` "
                f"column in {len(base_rows)} base / {len(quant_rows)} quantized rows")
    if base_null:
        return f"join key absent on the base side ({len(base_rows)} rows, 0 usable keys)"
    if quant_null:
        return f"join key absent on the quantized side ({len(quant_rows)} rows, 0 usable keys)"
    if not base_rows or not quant_rows:
        return f"empty side: {len(base_rows)} base rows, {len(quant_rows)} quantized rows"
    return (f"no shared join keys between {len(base_map)} base and "
            f"{len(quant_map)} quantized keyed rows (disjoint item sets)")


def join_cell(
    base_rows: Sequence[Mapping[str, Any]],
    quant_rows: Sequence[Mapping[str, Any]],
    *,
    key_of,
    identity_of,
    prompt_of,
) -> dict[str, Any]:
    """Apply the section 4 gates and return join statistics plus matched items.

    identity_of guards the join itself (byte-identical doc for S2; for S1 the
    example hash is both key and identity, so identity_of may return the key).
    prompt_of is the full-prompt hash used for the 99% pass gate.
    """
    base_map, base_dropped = dedupe_join_keys(base_rows, key_of)
    quant_map, quant_dropped = dedupe_join_keys(quant_rows, key_of)
    shared = sorted(set(base_map) & set(quant_map))
    joinable = [k for k in shared if identity_of(base_map[k]) == identity_of(quant_map[k])]
    passing = [k for k in joinable if prompt_of(base_map[k]) is not None
               and prompt_of(base_map[k]) == prompt_of(quant_map[k])]
    pass_rate = (len(passing) / len(joinable)) if joinable else 0.0
    excluded = not joinable or pass_rate < PROMPT_PASS_THRESHOLD
    return {
        "base_rows": len(base_rows),
        "quant_rows": len(quant_rows),
        "base_dropped_duplicate_keys": base_dropped,
        "quant_dropped_duplicate_keys": quant_dropped,
        "shared_keys": len(shared),
        "joinable": len(joinable),
        "prompt_identical": len(passing),
        "prompt_pass_rate": pass_rate,
        "excluded": excluded,
        "exclusion_reason": (
            None if not excluded
            else _no_join_reason(base_map, quant_map, base_rows, quant_rows) if not joinable
            else f"prompt-hash pass rate {pass_rate:.4f} < {PROMPT_PASS_THRESHOLD}"
        ),
        "matched": [(k, base_map[k], quant_map[k]) for k in passing],
    }


# ---------------------------------------------------------------------------
# Section 5: correctness and prediction extraction
# ---------------------------------------------------------------------------

def read_field(row: Mapping[str, Any], column: str) -> Any:
    """Read a possibly dotted column spec, e.g. 'acc_norm' or 'metrics.acc_norm'.

    Rev-2 / finding F2: the newer lighteval details schema nests the scalar
    metrics inside a `metrics` struct instead of exposing them at top level.
    Registration section 5 selects the correctness column by *presence in the
    data* ("acc_norm where present, else acc"), not by its position in the file
    layout, so a nested acc_norm is the registered column and the cell is a
    registered-population cell.
    """
    head, _, tail = column.partition(".")
    value = row.get(head)
    if not tail:
        return value
    if isinstance(value, Mapping):
        return value.get(tail)
    return None


def s1_correctness_column(rows: Sequence[Mapping[str, Any]]) -> str:
    for column in ("acc_norm", "acc", "metrics.acc_norm", "metrics.acc"):
        if any(read_field(row, column) is not None for row in rows):
            return column
    raise CellSkip(
        "no acc_norm or acc column in S1 rows (checked top level and the "
        "`metrics` struct); task has no binary correctness metric"
    )


def binary_correct(value: Any, column: str) -> bool:
    if value is None:
        raise CellSkip(f"{column} is missing on a matched row; cell has no 0/1 correctness")
    number = float(value)
    if number not in (0.0, 1.0):
        raise CellSkip(f"{column} is not binary (saw {number}); cell has no 0/1 correctness")
    return bool(number)


def s1_prediction(row: Mapping[str, Any]) -> str | None:
    predictions = row.get("predictions")
    if predictions is None or (hasattr(predictions, "__len__") and len(predictions) == 0):
        return None
    values = list(predictions)
    if all(isinstance(v, (int, float)) for v in values):
        return str(max(range(len(values)), key=lambda i: float(values[i])))
    return str(values[0])


def s2_metric_column(rows: Sequence[Mapping[str, Any]]) -> str:
    for column in S2_METRIC_PRIORITY:
        if any(row.get(column) is not None for row in rows):
            return column
    raise CellSkip(f"no metric column among {S2_METRIC_PRIORITY} in S2 rows")


def s2_prediction(row: Mapping[str, Any]) -> str | None:
    resps = row.get("filtered_resps") or row.get("resps")
    if not resps:
        return None
    first = resps[0]
    while isinstance(first, (list, tuple)) and first:
        first = first[0]
    return str(first)


def build_records(
    matched: Sequence[tuple[str, Mapping[str, Any], Mapping[str, Any]]],
    *,
    correctness_column: str,
    prediction_of,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    base_records, quant_records = [], []
    prediction_available = True
    for key, base_row, quant_row in matched:
        base_pred = prediction_of(base_row)
        quant_pred = prediction_of(quant_row)
        if base_pred is None or quant_pred is None:
            prediction_available = False
        base_records.append({
            "item_id": key,
            "correct": binary_correct(read_field(base_row, correctness_column), correctness_column),
            "prediction": base_pred if base_pred is not None else "",
        })
        quant_records.append({
            "item_id": key,
            "correct": binary_correct(read_field(quant_row, correctness_column), correctness_column),
            "prediction": quant_pred if quant_pred is not None else "",
        })
    return base_records, quant_records, prediction_available


def analyze_cell(
    matched_join: Mapping[str, Any],
    *,
    correctness_column: str,
    prediction_of,
    bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    """Registered metric suite for one non-excluded cell."""
    base_records, quant_records, prediction_available = build_records(
        matched_join["matched"],
        correctness_column=correctness_column,
        prediction_of=prediction_of,
    )
    result = dataclasses.asdict(
        compare(base_records, quant_records, margin=TOST_MARGIN, bootstrap=bootstrap, seed=seed)
    )
    if not prediction_available:
        result["wrong_to_different_wrong_churn"] = None
        result["total_answer_churn"] = None
    result["prediction_available"] = prediction_available
    result["correctness_column"] = correctness_column
    return result


# ---------------------------------------------------------------------------
# Fetch layer (stdlib HTTPS; no new dependencies)
# ---------------------------------------------------------------------------

HTTP_RETRIES = 8
MIN_REQUEST_INTERVAL = 0.12  # seconds between Hub requests (politeness throttle)
RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})
_LAST_REQUEST_AT = [0.0]


def _throttle() -> None:
    """Keep a floor on the interval between Hub requests.

    The F1 fallback issues several downloads per cell where rev-1 issued one,
    which multiplied the request rate enough to trip the Hub's 429 limiter on
    the first rev-2 attempt (job 11339935, failed at pair 18).
    """
    elapsed = time.monotonic() - _LAST_REQUEST_AT[0]
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _LAST_REQUEST_AT[0] = time.monotonic()


def _retry_delay(exc: Exception, attempt: int) -> float:
    """Exponential backoff with jitter, honouring Retry-After when present."""
    if isinstance(exc, urllib.error.HTTPError):
        retry_after = exc.headers.get("Retry-After") if exc.headers else None
        if retry_after:
            try:
                return min(120.0, float(retry_after))
            except ValueError:
                pass
    return min(120.0, (2.0 ** attempt)) * (1.0 + random.random() * 0.25)


def _http_get_with_headers(url: str, retries: int = HTTP_RETRIES) -> tuple[bytes, Mapping[str, str]]:
    """Fetch with backoff. Retries rate-limit and transient server errors only.

    An authenticated request gets a substantially higher Hub rate limit, so the
    token env.sh already forwards for gated repos is used here when present. It
    is never logged.
    """
    headers = {"User-Agent": "flipeval-atlas/0.1"}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            _throttle()
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read(), dict(response.headers)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in RETRYABLE_STATUS:
                raise RuntimeError(f"failed to fetch {url}: {exc}") from exc
            time.sleep(_retry_delay(exc, attempt))
        except Exception as exc:  # noqa: BLE001 - transient transport; retried
            last = exc
            time.sleep(_retry_delay(exc, attempt))
    raise RuntimeError(f"failed to fetch {url} after {retries} attempts: {last}")


def _http_get(url: str, retries: int = 3) -> bytes:
    return _http_get_with_headers(url, retries)[0]


def parse_next_link(link_header: str | None) -> str | None:
    """Next-page URL from an RFC 5988 Link header, or None.

    Rev-2 / finding F5: the HF tree endpoint paginates. Rev-1 issued a single
    `?recursive=true` request and ignored `Link: rel="next"`, so any details
    repo with more entries than one page would silently truncate into spurious
    "no parquet found for task" skips.
    """
    if not link_header:
        return None
    for part in link_header.split(","):
        segments = part.split(";")
        if len(segments) < 2:
            continue
        target = segments[0].strip()
        if not (target.startswith("<") and target.endswith(">")):
            continue
        for attribute in segments[1:]:
            key, _, value = attribute.strip().partition("=")
            if key.strip().lower() == "rel" and value.strip().strip('"') == "next":
                return target[1:-1]
    return None


def fetch_repo_tree(repo: str) -> list[dict[str, Any]]:
    """All tree entries, following pagination to exhaustion (F5)."""
    entries: list[dict[str, Any]] = []
    url: str | None = HF_TREE.format(repo=repo)
    seen: set[str] = set()
    while url and url not in seen:
        seen.add(url)
        body, headers = _http_get_with_headers(url)
        page = json.loads(body.decode("utf-8"))
        if not isinstance(page, list):
            raise RuntimeError(f"unexpected tree payload for {repo}: {type(page)}")
        entries.extend(page)
        url = parse_next_link(headers.get("Link") or headers.get("link"))
    return entries


def list_repo_files(repo: str, cache_dir: Path) -> list[str]:
    cache = cache_dir / "trees" / f"{repo.replace('/', '__')}.json"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(fetch_repo_tree(repo)), encoding="utf-8")
    entries = json.loads(cache.read_text(encoding="utf-8"))
    return [entry["path"] for entry in entries if entry.get("type") == "file"]


def download(repo: str, path: str, cache_dir: Path) -> Path:
    target = cache_dir / "files" / repo.replace("/", "__") / path
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        quoted = urllib.parse.quote(path)
        target.write_bytes(_http_get(HF_RESOLVE.format(repo=repo, path=quoted)))
    return target


def normalize_token(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()


def timestamp_key(timestamp: str) -> str:
    """Canonical digits-only form; cardData uses underscores where dirs use -/:."""
    return re.sub(r"[^0-9]", "", timestamp)


def find_s1_task_file(files: Sequence[str], task_config: str, run_timestamps: Sequence[str]) -> str:
    """Latest run's parquet for a task config like 'harness_gsm8k_5' (section 3.2)."""
    want = normalize_token(task_config)
    for timestamp in sorted(run_timestamps, key=timestamp_key, reverse=True):
        for path in files:
            if not path.endswith(".parquet") or "/" not in path:
                continue
            if timestamp_key(path.split("/")[0]) != timestamp_key(timestamp):
                continue
            stem = Path(path).name
            if f"_{want}_" in f"_{normalize_token(stem)}_":
                return path
    raise CellSkip(f"no parquet found for task {task_config} in runs {list(run_timestamps)}")


def s1_run_combinations(
    base_timestamps: Sequence[str], quant_timestamps: Sequence[str]
) -> list[tuple[str, str]]:
    """(base, quantized) run pairs in reverse-chronological order (section 3.2).

    Registration lines 41-42: "use the latest run timestamp per task for each
    side unless prompt-hash agreement (rule 4.2) fails, in which case try
    earlier run combinations in reverse-chronological order and record the
    choice." Rev-1 implemented only the first half.

    Ordering: the latest-latest combination is always first; thereafter
    combinations are ranked by how far back they step in total, with the
    quantized side held as new as possible on ties. That makes the traversal a
    strict generalisation of rev-1 -- the first element is exactly what rev-1
    would have picked -- so the fallback can only add cells, never change the
    choice for a cell that already succeeded.
    """
    base_sorted = sorted(base_timestamps, key=timestamp_key, reverse=True)
    quant_sorted = sorted(quant_timestamps, key=timestamp_key, reverse=True)
    combos = [
        (b_rank + q_rank, q_rank, base, quant)
        for b_rank, base in enumerate(base_sorted)
        for q_rank, quant in enumerate(quant_sorted)
    ]
    combos.sort(key=lambda item: (item[0], item[1]))
    return [(base, quant) for _, _, base, quant in combos]


def find_s2_task_file(files: Sequence[str], variant_dir: str, task: str, run_timestamps: Sequence[str]) -> str:
    for timestamp in sorted(run_timestamps, reverse=True):
        for path in files:
            parts = path.split("/")
            if parts[0] != variant_dir or not path.endswith(".jsonl"):
                continue
            name = Path(path).name
            if name in (f"samples_{task}_{timestamp}.jsonl",
                        f"samples_leaderboard_{task}_{timestamp}.jsonl"):
                return path
    raise CellSkip(f"no samples file for {variant_dir}/{task} in runs {list(run_timestamps)}")


def load_s1_rows(parquet_path: Path) -> list[dict[str, Any]]:
    import pandas as pd

    frame = pd.read_parquet(parquet_path)
    return frame.to_dict("records")


def load_s2_rows(jsonl_path: Path) -> list[dict[str, Any]]:
    rows = []
    with jsonl_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def harness_identity(files: Sequence[str], repo: str, prefix: str, cache_dir: Path) -> dict[str, Any] | None:
    """Best-effort section 4.3 provenance from the side's results JSON."""
    candidates = sorted(p for p in files if p.startswith(prefix) and "results" in Path(p).name and p.endswith(".json"))
    if not candidates:
        return None
    try:
        payload = json.loads(download(repo, candidates[-1], cache_dir).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - provenance is best-effort, never gates analysis
        return None
    config = payload.get("config") or payload.get("config_general") or {}
    return {
        "results_file": candidates[-1],
        "git_hash": payload.get("git_hash") or config.get("lighteval_sha") or config.get("git_hash"),
        "model_args": config.get("model_args") or config.get("model_config_path"),
        "dtype": config.get("model_dtype") or config.get("dtype"),
    }


# ---------------------------------------------------------------------------
# Per-source row accessors (section 4.1 join fields)
# ---------------------------------------------------------------------------

def s1_key(row: Mapping[str, Any]) -> Any:
    """Section 4.1 join key: `hashes.example`, else the raw `example` column.

    Rev-2 / finding F2: the newer lighteval details schema drops the `hashes`
    struct and stores the raw `example` and `full_prompt` strings instead. The
    registered clause names `hashes.example` because that is what the older
    schema exposes; its operative content is *item identity*, and the raw
    example string identifies the item at least as precisely as its hash. Rev-1
    read only `hashes`, so every join key came back null and the cell was
    excluded as "no joinable items" -- a parser limitation recorded as though it
    were a property of the data. Recorded as an interpretive choice in the
    rev-2 correction memo.
    """
    hashes = row.get("hashes")
    if isinstance(hashes, Mapping) and hashes.get("example") is not None:
        return hashes["example"]
    return row.get("example")


def s1_prompt(row: Mapping[str, Any]) -> Any:
    """Section 4.2 prompt identity: `hashes.full_prompt`, else raw `full_prompt`.

    Same interpretive basis as `s1_key`: the clause controls prompt identity
    across the pair, and comparing the raw prompt strings tests exactly that.
    """
    hashes = row.get("hashes")
    if isinstance(hashes, Mapping) and hashes.get("full_prompt") is not None:
        return hashes["full_prompt"]
    return row.get("full_prompt")


def s2_key(row: Mapping[str, Any]) -> Any:
    return row.get("doc_id")


def s2_identity(row: Mapping[str, Any]) -> Any:
    if row.get("doc_hash") is not None:
        return row["doc_hash"]
    return json.dumps(row.get("doc"), sort_keys=True)


def s2_prompt(row: Mapping[str, Any]) -> Any:
    return row.get("prompt_hash")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def repo_from_url(url: str) -> str:
    match = re.search(r"huggingface\.co/datasets/([^/\s(]+/[^/\s(]+)", url)
    if not match:
        raise CellSkip(f"cannot parse dataset repo from {url}")
    return match.group(1).rstrip(")")


def resolve_s1_cell(
    task: str,
    run_timestamps: Mapping[str, Sequence[str]],
    *,
    base_files: Sequence[str],
    quant_files: Sequence[str],
    base_repo: str,
    quant_repo: str,
    cache_dir: Path,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    """Section 3.2 run selection with the registered earlier-run fallback (F1).

    Tries (base, quantized) run combinations in reverse-chronological order and
    returns the first that clears the section 4.2 gate and yields a correctness
    column. Every attempt is recorded, and the accepted combination is reported
    in `run_choice` as the clause requires ("record the choice").

    If no combination clears the gate, the *first* (latest-latest) attempt is
    returned as the outcome, so a genuinely unusable cell is excluded with the
    same reason rev-1 would have given, now accompanied by the full attempt log.
    """
    combos = s1_run_combinations(run_timestamps["base"], run_timestamps["quantized"])
    attempts: list[dict[str, Any]] = []
    first: tuple[dict[str, Any] | None, str | None, CellSkip | None] | None = None

    for base_ts, quant_ts in combos:
        outcome: str
        joined = correctness = None
        skip: CellSkip | None = None
        try:
            base_path = download(base_repo, find_s1_task_file(base_files, task, [base_ts]), cache_dir)
            quant_path = download(quant_repo, find_s1_task_file(quant_files, task, [quant_ts]), cache_dir)
            base_rows, quant_rows = load_s1_rows(base_path), load_s1_rows(quant_path)
            joined = join_cell(base_rows, quant_rows, key_of=s1_key,
                               identity_of=s1_key, prompt_of=s1_prompt)
            correctness = s1_correctness_column(quant_rows)
            outcome = "accepted" if not joined["excluded"] else str(joined["exclusion_reason"])
        except CellSkip as exc:
            skip = exc
            outcome = str(exc)

        attempts.append({"base": base_ts, "quantized": quant_ts, "outcome": outcome})
        if first is None:
            first = (joined, correctness, skip)
        if joined is not None and correctness is not None and not joined["excluded"]:
            return joined, correctness, {
                "base": base_ts,
                "quantized": quant_ts,
                "fallback_used": len(attempts) > 1,
                "attempts": attempts,
            }

    if first is None:
        raise CellSkip(f"no run combinations enumerated for task {task}")

    joined, correctness, skip = first
    run_choice = {
        "base": combos[0][0],
        "quantized": combos[0][1],
        "fallback_used": False,
        "fallback_exhausted": len(attempts) > 1,
        "attempts": attempts,
    }
    if skip is not None:
        skip.join = joined          # type: ignore[attr-defined]
        skip.run_choice = run_choice  # type: ignore[attr-defined]
        raise skip
    if correctness is None:
        exhausted = CellSkip(f"no correctness column in any of {len(attempts)} run combinations")
        exhausted.join = joined          # type: ignore[attr-defined]
        exhausted.run_choice = run_choice  # type: ignore[attr-defined]
        raise exhausted
    return joined, correctness, run_choice


def run_pair(pair: Mapping[str, Any], pair_index: int, *, cache_dir: Path, output_dir: Path,
             bootstrap: int, seed: int, only_task: str | None = None) -> list[dict[str, Any]]:
    source = pair["source"]
    rows_out: list[dict[str, Any]] = []
    if source == "S1":
        base_repo = repo_from_url(pair["base_details_url"])
        quant_repo = repo_from_url(pair["quantized_details_url"])
        base_files = list_repo_files(base_repo, cache_dir)
        quant_files = list_repo_files(quant_repo, cache_dir)
    else:
        base_repo = quant_repo = repo_from_url(pair["quantized_details_url"])
        base_files = quant_files = list_repo_files(base_repo, cache_dir)
        base_dir = pair["base_model"].split("/")[-1]
        quant_dir = pair["quantized_model"].split("/")[-1]

    for task in pair["tasks"]:
        if only_task and task != only_task:
            continue
        cell: dict[str, Any] = {
            "pair_index": pair_index,
            "source": source,
            "quantized_model": pair["quantized_model"],
            "base_model": pair["base_model"],
            "method": pair.get("method_guess"),
            "task": task,
            "contains_disclosed_probe_cell": bool(pair.get("contains_disclosed_probe_cell")),
        }
        try:
            if source == "S1":
                joined, correctness, run_choice = resolve_s1_cell(
                    task, pair["run_timestamps"], base_files=base_files, quant_files=quant_files,
                    base_repo=base_repo, quant_repo=quant_repo, cache_dir=cache_dir,
                )
                cell["run_choice"] = run_choice
                prediction_of = s1_prediction
                cell["harness_identity"] = {
                    "base": harness_identity(base_files, base_repo, "", cache_dir),
                    "quantized": harness_identity(quant_files, quant_repo, "", cache_dir),
                }
            else:
                base_path = download(base_repo, find_s2_task_file(
                    base_files, base_dir, task, pair["run_timestamps"]["base"]), cache_dir)
                quant_path = download(quant_repo, find_s2_task_file(
                    quant_files, quant_dir, task, pair["run_timestamps"]["quantized"]), cache_dir)
                base_rows, quant_rows = load_s2_rows(base_path), load_s2_rows(quant_path)
                joined = join_cell(base_rows, quant_rows, key_of=s2_key, identity_of=s2_identity, prompt_of=s2_prompt)
                correctness = s2_metric_column(quant_rows)
                prediction_of = s2_prediction
                cell["harness_identity"] = {
                    "base": harness_identity(base_files, base_repo, base_dir, cache_dir),
                    "quantized": harness_identity(quant_files, quant_repo, quant_dir, cache_dir),
                }

            cell["join"] = {k: v for k, v in joined.items() if k != "matched"}
            if joined["excluded"]:
                cell["metrics"] = None
            else:
                cell["metrics"] = analyze_cell(
                    joined, correctness_column=correctness,
                    prediction_of=prediction_of, bootstrap=bootstrap, seed=seed,
                )
        except CellSkip as skip:
            # F4: preserve whatever join was computed before the skip fired.
            # Rev-1 discarded it unconditionally, so an unreadable join key was
            # filed under whichever error surfaced next -- the lossiness that
            # hid F2. `run_choice` is attached above and survives here.
            cell.setdefault("join", getattr(skip, "join", None))
            cell["metrics"] = None
            cell["skip_reason"] = str(skip)
            cell.setdefault("run_choice", getattr(skip, "run_choice", None))

        rows_out.append(cell)
        cell_dir = output_dir / "cells"
        cell_dir.mkdir(parents=True, exist_ok=True)
        cell_path = cell_dir / f"pair{pair_index:03d}__{normalize_token(task)}.json"
        cell_path.write_text(json.dumps(cell, indent=2, default=str) + "\n", encoding="utf-8")
    return rows_out


SUMMARY_COLUMNS = [
    "pair_index", "source", "quantized_model", "base_model", "method", "task",
    "contains_disclosed_probe_cell", "excluded_or_skipped", "reason", "n",
    "correctness_column", "baseline_accuracy", "method_accuracy", "net_accuracy_delta",
    "harmful_flip_rate", "beneficial_flip_rate", "accuracy_state_churn",
    "total_answer_churn", "mcnemar_p", "tost_equivalent", "mdd_80_power",
    "required_n_for_observed_delta_80_power", "prompt_pass_rate",
    # Rev-2 (F1): the section 3.2 "record the choice" fields.
    "run_base_timestamp", "run_quantized_timestamp", "run_fallback_used",
]


def summarize(cells: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for cell in cells:
        metrics = cell.get("metrics") or {}
        join = cell.get("join") or {}
        run_choice = cell.get("run_choice") or {}
        rows.append({
            "run_base_timestamp": run_choice.get("base", ""),
            "run_quantized_timestamp": run_choice.get("quantized", ""),
            "run_fallback_used": run_choice.get("fallback_used", ""),
            "pair_index": cell["pair_index"],
            "source": cell["source"],
            "quantized_model": cell["quantized_model"],
            "base_model": cell["base_model"],
            "method": cell["method"],
            "task": cell["task"],
            "contains_disclosed_probe_cell": cell["contains_disclosed_probe_cell"],
            "excluded_or_skipped": not metrics,
            "reason": cell.get("skip_reason") or join.get("exclusion_reason") or "",
            "n": metrics.get("n", ""),
            "correctness_column": metrics.get("correctness_column", ""),
            "baseline_accuracy": metrics.get("baseline_accuracy", ""),
            "method_accuracy": metrics.get("method_accuracy", ""),
            "net_accuracy_delta": metrics.get("net_accuracy_delta", ""),
            "harmful_flip_rate": metrics.get("harmful_flip_rate", ""),
            "beneficial_flip_rate": metrics.get("beneficial_flip_rate", ""),
            "accuracy_state_churn": metrics.get("accuracy_state_churn", ""),
            "total_answer_churn": metrics.get("total_answer_churn", ""),
            "mcnemar_p": metrics.get("mcnemar_p", ""),
            "tost_equivalent": metrics.get("tost_equivalent", ""),
            "mdd_80_power": metrics.get("mdd_80_power", ""),
            "required_n_for_observed_delta_80_power": metrics.get("required_n_for_observed_delta_80_power", ""),
            "prompt_pass_rate": join.get("prompt_pass_rate", ""),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="docs/atlas_pair_manifest.json")
    parser.add_argument("--output", default="results/atlas")
    parser.add_argument("--cache-dir", default="outputs/atlas_cache")
    parser.add_argument("--pairs", help="Comma-separated pair indices or ranges, e.g. 0,3,10-12")
    parser.add_argument("--source", choices=["S1", "S2"])
    parser.add_argument("--task")
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest.get("protocol") != "ATLAS_MINING_REGISTRATION_2026-07-15":
        raise SystemExit("manifest does not reference the frozen protocol; refusing to run")

    selected = set()
    if args.pairs:
        for chunk in args.pairs.split(","):
            if "-" in chunk:
                low, high = chunk.split("-")
                selected.update(range(int(low), int(high) + 1))
            else:
                selected.add(int(chunk))

    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir)
    all_cells: list[dict[str, Any]] = []
    for index, pair in enumerate(manifest["pairs"]):
        if selected and index not in selected:
            continue
        if args.source and pair["source"] != args.source:
            continue
        print(f"[pair {index}] {pair['quantized_model']} vs {pair['base_model']}", flush=True)
        all_cells.extend(run_pair(
            pair, index, cache_dir=cache_dir, output_dir=output_dir,
            bootstrap=args.bootstrap, seed=args.seed, only_task=args.task,
        ))

    summary = summarize(all_cells)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "atlas_cells_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(summary)
    excluded = [row for row in summary if row["excluded_or_skipped"]]
    with (output_dir / "atlas_exclusions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(excluded)
    print(f"{len(summary)} cells written ({len(excluded)} excluded/skipped) -> {output_dir}", flush=True)


if __name__ == "__main__":
    main()
