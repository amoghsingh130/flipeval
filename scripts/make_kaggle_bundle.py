from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".DS_Store",
    "dist",
    "results",
    "outputs",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a clean Kaggle Dataset upload bundle for this project.")
    parser.add_argument("--owner", default="amoghsingh130")
    parser.add_argument("--slug", default="compression-eval-pilot-code")
    parser.add_argument("--title", default="Compression Eval Pilot Code")
    parser.add_argument("--dest", type=Path, default=Path("dist/kaggle_dataset"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    dest = args.dest if args.dest.is_absolute() else root / args.dest
    if dest.exists():
        shutil.rmtree(dest)
    copy_project(root, dest)
    write_metadata(dest, args.owner, args.slug, args.title)
    archive = shutil.make_archive(str(dest), "zip", dest)
    print(f"Dataset folder: {dest}")
    print(f"Upload zip: {archive}")


def copy_project(root: Path, dest: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        ignored = set()
        for name in names:
            if name in EXCLUDES or name.endswith(".pyc"):
                ignored.add(name)
        return ignored

    shutil.copytree(root, dest, ignore=ignore)


def write_metadata(dest: Path, owner: str, slug: str, title: str) -> None:
    metadata = {
        "id": f"{owner}/{slug}",
        "title": title,
        "licenses": [{"name": "CC0-1.0"}],
    }
    with (dest / "dataset-metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
