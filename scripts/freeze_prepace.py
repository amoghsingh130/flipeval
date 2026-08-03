from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INCLUDED_PATHS = (
    "PREREGISTRATION.md",
    "STATUS.md",
    "README.md",
    "pyproject.toml",
    "Dockerfile",
    "flipeval.def",
    "container/requirements.lock",
    "docs/PACE_RUNBOOK.md",
    "docs/EXPECTED_MAIN_GRID.json",
    "docs/WIKITEXT2_PROTOCOL_BLOCKER.md",
    "docs/WIKITEXT2_PREFLIGHT_2026-07-13.json",
)
INCLUDED_TREES = ("configs", "flipeval", "pilot_eval", "scripts", "tests")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or verify the pre-PACE source fingerprint.")
    parser.add_argument("--output", default="docs/PREPACE_FREEZE.json")
    parser.add_argument("--verify")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.verify:
        errors = verify_manifest(root, Path(args.verify))
        if errors:
            print(json.dumps({"passed": False, "errors": errors}, indent=2))
            raise SystemExit(1)
        print(json.dumps({"passed": True, "manifest": args.verify}, indent=2))
        return

    dirty = _git(root, "status", "--porcelain")
    if dirty:
        raise SystemExit("refusing to freeze a dirty worktree; commit the implementation first")
    manifest = build_manifest(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    print(f"Wrote {output}")


def build_manifest(root: Path) -> dict[str, Any]:
    files = _included_files(root)
    hashes = {str(path.relative_to(root)): _sha256(path) for path in files}
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": _git(root, "rev-parse", "HEAD"),
        "source_tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "branch": _git(root, "branch", "--show-current"),
        "files": hashes,
        "expected_grid_manifest": "configs/main_grid_manifest.yaml",
        "expected_grid_expansion": "docs/EXPECTED_MAIN_GRID.json",
        "pace_execution_started": False,
    }
    manifest["manifest_payload_sha256"] = _payload_sha256(manifest)
    return manifest


def verify_manifest(root: Path, path: Path) -> list[str]:
    manifest_path = path if path.is_absolute() else root / path
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read manifest: {exc}"]
    errors: list[str] = []
    if manifest.get("manifest_payload_sha256") != _payload_sha256(manifest):
        errors.append("manifest payload checksum mismatch")
    recorded = manifest.get("files", {})
    for relative, expected in recorded.items():
        candidate = root / relative
        if not candidate.is_file():
            errors.append(f"missing frozen file: {relative}")
        elif _sha256(candidate) != expected:
            errors.append(f"frozen file changed: {relative}")
    # Additions are a source-state change too. Verifying only the recorded set
    # detects modification and deletion but is blind to a NEW file appearing in
    # a fingerprinted tree, so a new grid-touching script under scripts/ would
    # pass the fingerprint silently. build_manifest already enumerates the
    # trees; verification has to enumerate them as well or the two disagree
    # about what the fingerprint covers.
    try:
        present = {str(path.relative_to(root)) for path in _included_files(root)}
    except FileNotFoundError as exc:
        errors.append(str(exc))
    else:
        for relative in sorted(present - set(recorded)):
            errors.append(f"unrecorded file in fingerprinted tree: {relative}")
    source_commit = str(manifest.get("source_commit", ""))
    if source_commit:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append("frozen source commit is not an ancestor of HEAD")
    return errors


def _included_files(root: Path) -> list[Path]:
    files = [root / relative for relative in INCLUDED_PATHS]
    for tree in INCLUDED_TREES:
        files.extend(
            path
            for path in (root / tree).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"freeze input files are missing: {missing}")
    return sorted(set(files))


def _payload_sha256(manifest: dict[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("manifest_payload_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


if __name__ == "__main__":
    main()
