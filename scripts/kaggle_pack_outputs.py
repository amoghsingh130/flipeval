from __future__ import annotations

import argparse
import tarfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Package Kaggle pilot outputs into a tarball.")
    parser.add_argument("--results", type=Path, default=Path("/kaggle/working/results"))
    parser.add_argument("--outputs", type=Path, default=Path("/kaggle/working/outputs"))
    parser.add_argument("--dest", type=Path, default=None)
    parser.add_argument("--include-checkpoints", action="store_true")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = args.dest or Path(f"/kaggle/working/pilot_outputs_{timestamp}.tar.gz")
    with tarfile.open(dest, "w:gz") as tar:
        if args.results.exists():
            tar.add(args.results, arcname="results")
        if args.include_checkpoints and args.outputs.exists():
            tar.add(args.outputs, arcname="outputs")
    print(dest)


if __name__ == "__main__":
    main()
