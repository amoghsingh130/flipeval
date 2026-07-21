"""Primitives shared by the fail-closed run validators.

Extracted from `verify_bridge.py` when the mini-grid validator was written, so
the two validators cannot drift apart in how they record a check, parse a file,
or hash one. Behaviour is byte-for-byte what the bridge validator already did;
`scripts/verify_bridge.py` is the reference for that claim and its tests pin it.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def check(condition: bool, description: str, errors: list[str], checks: list[dict[str, Any]]) -> None:
    """Record one check. A failure appends to `errors`, which fails the run."""
    checks.append({"check": description, "passed": bool(condition)})
    if not condition:
        errors.append(description)


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON file {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"expected JSON object: {path}")
        return None
    return value


def load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]] | None:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return None
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("record is not an object")
                rows.append(value)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid JSONL file {path}: {exc}")
        return None
    return rows


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
