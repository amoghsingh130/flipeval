from __future__ import annotations

import argparse
import gc
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm


def merge_manifest(path: Path, new_manifest: dict[str, Any]) -> dict[str, Any]:
    """Merge a partial invocation into the durable run manifest."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {
            "run_name": new_manifest["run_name"],
            "created_at": new_manifest["started_at"],
            "config": new_manifest["config"],
            "methods": [],
            "tasks": [],
            "runs": [],
        }

    manifest.setdefault("runs", [])
    for key in ("methods", "tasks"):
        existing = manifest.setdefault(key, [])
        seen = {json.dumps(entry, sort_keys=True) for entry in existing}
        for entry in new_manifest[key]:
            encoded = json.dumps(entry, sort_keys=True)
            if encoded not in seen:
                existing.append(entry)
                seen.add(encoded)
    manifest["runs"].append(
        {
            "started_at": new_manifest["started_at"],
            "methods": [entry["name"] for entry in new_manifest["methods"]],
            "tasks": [entry["name"] for entry in new_manifest["tasks"]],
        }
    )
    with path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser(description="Run per-item compressed-LLM pilot evaluation.")
    parser.add_argument("--config", required=True, help="Path to YAML run config.")
    parser.add_argument("--only-method", action="append", help="Restrict to one or more method names.")
    parser.add_argument("--only-task", action="append", help="Restrict to one or more task names.")
    args = parser.parse_args()

    try:
        from .config import load_config
        from .modeling import evaluate_item, load_model_and_tokenizer, method_record
        from .tasks import load_task
    except ImportError as exc:
        raise SystemExit(
            "Missing evaluation dependency. Install the runtime with `pip install -r requirements.txt`."
        ) from exc

    run = load_config(args.config)
    run_dir = run.output_dir / run.run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    selected_tasks = [t for t in run.tasks if not args.only_task or t.name in set(args.only_task)]
    methods = [run.baseline] + run.methods
    selected_methods = [m for m in methods if not args.only_method or m.name in set(args.only_method)]

    invocation = {
        "run_name": run.run_name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": str(Path(args.config).resolve()),
        "methods": [method_record(m) for m in selected_methods],
        "tasks": [t.__dict__ for t in selected_tasks],
    }
    merge_manifest(run_dir / "manifest.json", invocation)

    for method in selected_methods:
        print(f"Loading {method.name}: {method.model_id}", flush=True)
        model, tokenizer = load_model_and_tokenizer(method, run)
        for task in selected_tasks:
            items = load_task(task.name, task.split, task.limit, task.subjects, task.fewshot)
            out_path = run_dir / f"{method.name}.{task.name}.jsonl"
            with out_path.open("w", encoding="utf-8") as f:
                for item in tqdm(items, desc=f"{method.name}/{task.name}"):
                    record = evaluate_item(
                        model,
                        tokenizer,
                        item,
                        max_new_tokens=task.max_new_tokens,
                        prompt_style=task.prompt_style,
                    )
                    record.update(
                        {
                            "run_name": run.run_name,
                            "method": method.name,
                            "model_id": method.model_id,
                            "seed": method.seed,
                        }
                    )
                    f.write(json.dumps(record, ensure_ascii=True) + "\n")
        del model, tokenizer
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass


if __name__ == "__main__":
    main()
