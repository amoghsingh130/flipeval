"""The fingerprint must fail on an ADDED file, not only a changed or deleted one.

Verification used to iterate the recorded `files` map alone, so it detected
modification and deletion but was blind to a new file appearing in a
fingerprinted tree. A new grid-touching script under `scripts/` would have
passed the fingerprint silently, which is the direction that matters most given
the no-default-grid rule. These tests pin all three directions, and the
negative control pins that a complete manifest stays clean, so a checker that
flags everything fails just as loudly as one that flags nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.freeze_prepace import _payload_sha256, build_manifest, verify_manifest


ROOT = Path(__file__).resolve().parents[1]


def _write(manifest: dict, path: Path) -> Path:
    manifest = dict(manifest)
    manifest.pop("manifest_payload_sha256", None)
    manifest["manifest_payload_sha256"] = _payload_sha256(manifest)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def _unrecorded(errors: list[str]) -> list[str]:
    return [error for error in errors if error.startswith("unrecorded file in fingerprinted tree")]


def test_a_complete_manifest_reports_no_unrecorded_files(tmp_path):
    """Negative control. Without this, a checker that always fires would pass."""
    path = _write(build_manifest(ROOT), tmp_path / "freeze.json")
    assert _unrecorded(verify_manifest(ROOT, path)) == []


def test_a_file_present_on_disk_but_absent_from_the_manifest_is_an_error(tmp_path):
    manifest = build_manifest(ROOT)
    dropped = next(key for key in manifest["files"] if key.startswith("tests/"))
    del manifest["files"][dropped]
    path = _write(manifest, tmp_path / "freeze.json")

    errors = verify_manifest(ROOT, path)

    assert _unrecorded(errors) == [f"unrecorded file in fingerprinted tree: {dropped}"]


def test_an_unrecorded_script_is_caught_because_that_is_the_dangerous_case(tmp_path):
    """scripts/ is where a new grid-touching job script would land."""
    manifest = build_manifest(ROOT)
    dropped = next(key for key in manifest["files"] if key.startswith("scripts/"))
    del manifest["files"][dropped]
    path = _write(manifest, tmp_path / "freeze.json")

    assert _unrecorded(verify_manifest(ROOT, path)) == [
        f"unrecorded file in fingerprinted tree: {dropped}"
    ]


def test_a_changed_file_is_still_detected(tmp_path):
    manifest = build_manifest(ROOT)
    target = next(key for key in manifest["files"] if key.startswith("tests/"))
    manifest["files"][target] = "0" * 64
    path = _write(manifest, tmp_path / "freeze.json")

    assert f"frozen file changed: {target}" in verify_manifest(ROOT, path)


def test_a_deleted_file_is_still_detected(tmp_path):
    manifest = build_manifest(ROOT)
    manifest["files"]["tests/test_this_file_does_not_exist.py"] = "0" * 64
    path = _write(manifest, tmp_path / "freeze.json")

    errors = verify_manifest(ROOT, path)

    assert "missing frozen file: tests/test_this_file_does_not_exist.py" in errors
    assert _unrecorded(errors) == []


def test_addition_and_modification_are_reported_independently(tmp_path):
    """Each direction must be able to fire alone, or one masks the other."""
    manifest = build_manifest(ROOT)
    keys = [key for key in manifest["files"] if key.startswith("tests/")]
    changed, dropped = keys[0], keys[1]
    manifest["files"][changed] = "0" * 64
    del manifest["files"][dropped]
    path = _write(manifest, tmp_path / "freeze.json")

    errors = verify_manifest(ROOT, path)

    assert f"frozen file changed: {changed}" in errors
    assert f"unrecorded file in fingerprinted tree: {dropped}" in errors
