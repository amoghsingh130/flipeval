from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_WORKDIR = Path("/kaggle/working/compression-eval")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage this project into Kaggle's writable working directory.")
    parser.add_argument("--source", type=Path, default=None, help="Project directory under /kaggle/input. Auto-detected by default.")
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument("--install", action="store_true", help="Install Python requirements after staging.")
    parser.add_argument("--with-quantization", action="store_true", help="Also install optional GPTQ/AWQ packages.")
    args = parser.parse_args()

    source = args.source or detect_source()
    if source.resolve() != args.workdir.resolve():
        copy_project(source, args.workdir)
    args.workdir.mkdir(parents=True, exist_ok=True)

    configure_huggingface_token()
    print_environment(args.workdir)

    if args.install:
        install_requirements(args.workdir, args.with_quantization)


def detect_source() -> Path:
    cwd = Path.cwd()
    if (cwd / "pilot_eval" / "run.py").exists():
        return cwd

    candidates = []
    for root in [Path("/kaggle/input")]:
        if not root.exists():
            continue
        candidates.extend(path.parent.parent for path in root.glob("**/pilot_eval/run.py"))
    if not candidates:
        raise SystemExit("Could not find project source. Attach the project as a Kaggle Dataset or pass --source.")
    candidates = sorted(set(candidates), key=lambda p: ("/kaggle/input" not in str(p), len(str(p))))
    return candidates[0]


def copy_project(source: Path, workdir: Path) -> None:
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "results",
        "outputs",
    )
    shutil.copytree(source, workdir, ignore=ignore, dirs_exist_ok=True)
    print(f"Staged project from {source} to {workdir}")


def configure_huggingface_token() -> None:
    if os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"):
        return
    try:
        from kaggle_secrets import UserSecretsClient

        token = UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        token = None
    if token:
        os.environ["HF_TOKEN"] = token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token
        print("Loaded HF_TOKEN from Kaggle Secrets.")


def install_requirements(workdir: Path, with_quantization: bool) -> None:
    req = workdir / "requirements.txt"
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])
    if with_quantization:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "auto-gptq", "autoawq"])


def print_environment(workdir: Path) -> None:
    print(f"Working directory: {workdir}")
    print(f"Python: {sys.version.split()[0]}")
    try:
        subprocess.run(["nvidia-smi"], check=False)
    except FileNotFoundError:
        print("nvidia-smi not found. In Kaggle, enable Settings > Accelerator > GPU.")


if __name__ == "__main__":
    main()
