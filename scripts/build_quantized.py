from __future__ import annotations

import argparse
import hashlib
import json
import os
import traceback
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np


CALIBRATION_SIZE = 128
CALIBRATION_SEQUENCE_LENGTH = 2048
CALIBRATION_SCHEMA_VERSION = 1
SAMPLING_ALGORITHM = "numpy-default_rng-shuffle-complete-index-array-v1"


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    repo_id: str
    config: str
    split: str
    revision: str
    row_count: int


# Repository revisions were resolved from the Hugging Face API on 2026-07-13.
# Changing one is an environment change and must produce a new calibration artifact.
DATASET_SPECS = {
    "c4": DatasetSpec(
        name="c4",
        repo_id="allenai/c4",
        config="en",
        split="train",
        revision="1588ec454efa1a09f29cd18ddd04fe05fc8653a2",
        row_count=364_868_892,
    ),
    "wikitext2": DatasetSpec(
        name="wikitext2",
        repo_id="Salesforce/wikitext",
        config="wikitext-2-raw-v1",
        split="train",
        revision="b08601e04326c79dfdd32d625aee71d232d685c3",
        row_count=36_718,
    ),
}


class CalibrationArtifactError(ValueError):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build GPTQ/AWQ checkpoints from a frozen paired calibration artifact."
    )
    parser.add_argument("--model-id", required=True)
    parser.add_argument(
        "--model-revision",
        required=True,
        help="Immutable model commit used for both tokenizer and model loading.",
    )
    parser.add_argument("--method", choices=["gptq", "awq"])
    parser.add_argument("--output-dir")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--bits", type=int, default=4)
    parser.add_argument("--dataset", choices=sorted(DATASET_SPECS), default="c4")
    parser.add_argument(
        "--dataset-revision",
        help="Override only to create a new, explicitly recorded environment cell.",
    )
    parser.add_argument("--dataset-cache-dir")
    parser.add_argument("--calibration-artifact", required=True)
    parser.add_argument(
        "--prepare-calibration-only",
        action="store_true",
        help="Create/validate the shared artifact without loading a quantization backend.",
    )
    parser.add_argument(
        "--verify-stream-row-count",
        action="store_true",
        help="Preflight-only: exhaust the pinned stream and fail closed unless it "
        "yields exactly the registered row_count before any artifact is created.",
    )
    parser.add_argument("--trust-remote-code", action="store_true")
    args = parser.parse_args()

    if not args.prepare_calibration_only and (args.method is None or args.output_dir is None):
        parser.error("--method and --output-dir are required unless --prepare-calibration-only is used")

    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise SystemExit("Missing transformers. Install the pinned container runtime.") from exc

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id,
        revision=args.model_revision,
        trust_remote_code=args.trust_remote_code,
    )
    spec = DATASET_SPECS[args.dataset]
    if args.dataset_revision:
        spec = DatasetSpec(
            spec.name,
            spec.repo_id,
            spec.config,
            spec.split,
            args.dataset_revision,
            spec.row_count,
        )

    if args.verify_stream_row_count:
        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise SystemExit("Missing datasets. Install the pinned container runtime.") from exc
        counted = verify_stream_row_count(
            make_stream_factory(load_dataset, spec, args.dataset_cache_dir), spec
        )
        print(f"Stream row count verified: {counted} rows match the registered row_count", flush=True)

    artifact_path = Path(args.calibration_artifact)
    artifact = load_or_create_calibration_artifact(
        artifact_path,
        tokenizer=tokenizer,
        model_id=args.model_id,
        model_revision=args.model_revision,
        dataset_spec=spec,
        seed=args.seed,
        dataset_cache_dir=args.dataset_cache_dir,
    )
    print(f"Calibration artifact: {artifact_path} ({artifact['artifact_sha256']})", flush=True)
    if args.prepare_calibration_only:
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.method == "gptq":
        build_gptq(args, tokenizer, artifact)
    else:
        build_awq(args, tokenizer, artifact)
    write_calibration_receipt(output_dir / "calibration_manifest.json", artifact, args)


def load_or_create_calibration_artifact(
    path: Path,
    *,
    tokenizer: Any,
    model_id: str,
    model_revision: str,
    dataset_spec: DatasetSpec,
    seed: int,
    dataset_cache_dir: str | None = None,
) -> dict[str, Any]:
    if path.exists():
        artifact = read_json(path)
        validate_calibration_artifact(
            artifact,
            tokenizer=tokenizer,
            model_id=model_id,
            model_revision=model_revision,
            dataset_spec=dataset_spec,
            seed=seed,
        )
        return artifact

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Missing datasets. Install the pinned container runtime.") from exc

    if dataset_spec.name == "c4":
        artifact = create_calibration_artifact_from_stream(
            make_stream_factory(load_dataset, dataset_spec, dataset_cache_dir),
            tokenizer,
            model_id=model_id,
            model_revision=model_revision,
            dataset_spec=dataset_spec,
            seed=seed,
        )
    else:
        dataset = load_dataset(
            dataset_spec.repo_id,
            dataset_spec.config,
            split=dataset_spec.split,
            revision=dataset_spec.revision,
            streaming=False,
            cache_dir=dataset_cache_dir,
        )
        artifact = create_calibration_artifact(
            dataset,
            tokenizer,
            model_id=model_id,
            model_revision=model_revision,
            dataset_spec=dataset_spec,
            seed=seed,
        )
    write_json_atomic(path, artifact)
    return artifact


def create_calibration_artifact(
    dataset: Sequence[Mapping[str, Any]],
    tokenizer: Any,
    *,
    model_id: str,
    model_revision: str,
    dataset_spec: DatasetSpec,
    seed: int,
    size: int = CALIBRATION_SIZE,
    sequence_length: int = CALIBRATION_SEQUENCE_LENGTH,
) -> dict[str, Any]:
    _validate_requested_shape(size, sequence_length)
    try:
        dataset_length = len(dataset)
    except TypeError as exc:
        raise CalibrationArtifactError(
            "the registered algorithm requires an indexable, non-streaming dataset"
        ) from exc
    if dataset_length < size:
        raise CalibrationArtifactError(
            f"dataset has {dataset_length} rows, fewer than requested calibration size {size}"
        )

    indices = shuffled_indices(dataset_length, seed)
    samples, visited, skipped_short = select_samples_in_registered_order(
        ((int(index), dataset[int(index)]) for index in indices),
        tokenizer,
        size=size,
        sequence_length=sequence_length,
        dataset_length=dataset_length,
    )
    dataset_fingerprint = getattr(dataset, "_fingerprint", None)
    return assemble_calibration_artifact(
        samples,
        tokenizer=tokenizer,
        model_id=model_id,
        model_revision=model_revision,
        dataset_spec=dataset_spec,
        seed=seed,
        size=size,
        sequence_length=sequence_length,
        dataset_length=dataset_length,
        dataset_fingerprint=str(dataset_fingerprint) if dataset_fingerprint else None,
        visited=visited,
        skipped_short=skipped_short,
        retrieval={"strategy": "indexable-dataset"},
    )


def make_stream_factory(
    load_dataset: Callable[..., Iterable[Mapping[str, Any]]],
    dataset_spec: DatasetSpec,
    dataset_cache_dir: str | None,
) -> Callable[[], Iterable[Mapping[str, Any]]]:
    def stream_factory() -> Iterable[Mapping[str, Any]]:
        return load_dataset(
            dataset_spec.repo_id,
            dataset_spec.config,
            split=dataset_spec.split,
            revision=dataset_spec.revision,
            streaming=True,
            cache_dir=dataset_cache_dir,
        )

    return stream_factory


def verify_stream_row_count(
    stream_factory: Callable[[], Iterable[Mapping[str, Any]]],
    dataset_spec: DatasetSpec,
) -> int:
    """Exhaust the stream and fail closed unless it yields exactly row_count rows.

    The registered permutation is built over DatasetSpec.row_count. An overstated
    count already fails closed in retrieve_stream_rows, but an understated count
    would silently shrink the sampling universe, so the preflight must run this
    check once per pinned dataset revision before any artifact is created.
    """
    expected = int(dataset_spec.row_count)
    actual = 0
    for actual, _ in enumerate(stream_factory(), start=1):
        pass
    if actual != expected:
        raise CalibrationArtifactError(
            f"{dataset_spec.repo_id} ({dataset_spec.config}/{dataset_spec.split}) stream "
            f"yielded {actual} rows but the registered row_count is {expected}; the frozen "
            "permutation would cover the wrong sampling universe"
        )
    return actual


def create_calibration_artifact_from_stream(
    stream_factory: Callable[[], Iterable[Mapping[str, Any]]],
    tokenizer: Any,
    *,
    model_id: str,
    model_revision: str,
    dataset_spec: DatasetSpec,
    seed: int,
    size: int = CALIBRATION_SIZE,
    sequence_length: int = CALIBRATION_SEQUENCE_LENGTH,
    retrieval_window: int = 4096,
) -> dict[str, Any]:
    """Retrieve shuffled indices through a sequential stream without changing order.

    The complete registered NumPy permutation is still generated. A prefix of its
    indices is fetched in one sequential pass, then restored to permutation order
    before eligibility checks. If the prefix has too few eligible rows, a larger
    disjoint prefix is fetched in another deterministic pass.

    Assumes the sequential streaming order of the pinned dataset revision equals
    indexed row order, and that DatasetSpec.row_count is exact; both are verified
    once per revision by the preflight's verify_stream_row_count pass.
    """
    _validate_requested_shape(size, sequence_length)
    if retrieval_window < size:
        raise CalibrationArtifactError("stream retrieval_window must be at least the sample count")
    dataset_length = int(dataset_spec.row_count)
    indices = shuffled_indices(dataset_length, seed)
    selected: list[dict[str, Any]] = []
    visited = 0
    skipped_short = 0
    total_stream_rows_scanned = 0
    passes = 0
    for start in range(0, dataset_length, retrieval_window):
        requested = [int(value) for value in indices[start : start + retrieval_window]]
        retrieved, scanned = retrieve_stream_rows(stream_factory(), requested)
        passes += 1
        total_stream_rows_scanned += scanned
        remaining = size - len(selected)
        batch, batch_visited, batch_skipped = select_samples_in_registered_order(
            ((index, retrieved[index]) for index in requested),
            tokenizer,
            size=remaining,
            sequence_length=sequence_length,
            dataset_length=dataset_length,
            require_full=False,
        )
        selected.extend(batch)
        visited += batch_visited
        skipped_short += batch_skipped
        if len(selected) == size:
            break
    if len(selected) != size:
        raise CalibrationArtifactError(
            f"only {len(selected)} of {dataset_length} rows contain at least "
            f"{sequence_length} tokens; the frozen protocol requires {size}"
        )
    return assemble_calibration_artifact(
        selected,
        tokenizer=tokenizer,
        model_id=model_id,
        model_revision=model_revision,
        dataset_spec=dataset_spec,
        seed=seed,
        size=size,
        sequence_length=sequence_length,
        dataset_length=dataset_length,
        dataset_fingerprint=None,
        visited=visited,
        skipped_short=skipped_short,
        retrieval={
            "strategy": "sequential-stream-index-retrieval",
            "window_size": retrieval_window,
            "passes": passes,
            "stream_rows_scanned": total_stream_rows_scanned,
        },
    )


def shuffled_indices(dataset_length: int, seed: int) -> np.ndarray:
    indices = np.arange(dataset_length, dtype=np.int64)
    np.random.default_rng(seed).shuffle(indices)
    return indices


def retrieve_stream_rows(
    stream: Iterable[Mapping[str, Any]], requested_indices: Sequence[int]
) -> tuple[dict[int, Mapping[str, Any]], int]:
    targets = set(requested_indices)
    found: dict[int, Mapping[str, Any]] = {}
    scanned = 0
    for index, row in enumerate(stream):
        scanned = index + 1
        if index in targets:
            found[index] = row
            if len(found) == len(targets):
                break
    missing = sorted(targets - set(found))
    if missing:
        preview = missing[:5]
        raise CalibrationArtifactError(
            f"stream ended before registered dataset indices were retrieved: {preview}"
        )
    return found, scanned


def select_samples_in_registered_order(
    indexed_rows: Iterable[tuple[int, Mapping[str, Any]]],
    tokenizer: Any,
    *,
    size: int,
    sequence_length: int,
    dataset_length: int,
    require_full: bool = True,
) -> tuple[list[dict[str, Any]], int, int]:
    samples: list[dict[str, Any]] = []
    skipped_short = 0
    visited = 0
    for index, row in indexed_rows:
        visited += 1
        if "text" not in row:
            raise CalibrationArtifactError(f"dataset row {index} has no 'text' field")
        text = str(row["text"])
        token_ids = encode_text(tokenizer, text, truncation=False)
        if len(token_ids) < sequence_length:
            skipped_short += 1
            continue
        selected_ids = token_ids[:sequence_length]
        samples.append(
            {
                "document_index": int(index),
                "text": text,
                "input_ids": selected_ids,
                "token_sha256": token_ids_sha256(selected_ids),
            }
        )
        if len(samples) == size:
            break
    if require_full and len(samples) != size:
        raise CalibrationArtifactError(
            f"only {len(samples)} of {dataset_length} rows contain at least "
            f"{sequence_length} tokens; the frozen protocol requires {size}"
        )
    return samples, visited, skipped_short


def assemble_calibration_artifact(
    samples: list[dict[str, Any]],
    *,
    tokenizer: Any,
    model_id: str,
    model_revision: str,
    dataset_spec: DatasetSpec,
    seed: int,
    size: int,
    sequence_length: int,
    dataset_length: int,
    dataset_fingerprint: str | None,
    visited: int,
    skipped_short: int,
    retrieval: Mapping[str, Any],
) -> dict[str, Any]:
    artifact: dict[str, Any] = {
        "schema_version": CALIBRATION_SCHEMA_VERSION,
        "sampling_algorithm": SAMPLING_ALGORITHM,
        "seed": int(seed),
        "sample_count": int(size),
        "sequence_length": int(sequence_length),
        "visited_document_count": visited,
        "skipped_short_document_count": skipped_short,
        "retrieval": dict(retrieval),
        "dataset": {
            "name": dataset_spec.name,
            "repo_id": dataset_spec.repo_id,
            "config": dataset_spec.config,
            "split": dataset_spec.split,
            "revision": dataset_spec.revision,
            "row_count": dataset_length,
            "datasets_fingerprint": dataset_fingerprint,
        },
        "tokenizer": tokenizer_identity(tokenizer, model_id, model_revision),
        "selected_document_indices": [sample["document_index"] for sample in samples],
        "selected_token_hashes": [sample["token_sha256"] for sample in samples],
        "samples": samples,
    }
    artifact["artifact_sha256"] = artifact_sha256(artifact)
    validate_calibration_artifact(
        artifact,
        tokenizer=tokenizer,
        model_id=model_id,
        model_revision=model_revision,
        dataset_spec=dataset_spec,
        seed=seed,
        expected_size=size,
        expected_sequence_length=sequence_length,
    )
    return artifact


def _validate_requested_shape(size: int, sequence_length: int) -> None:
    if size <= 0 or sequence_length <= 0:
        raise CalibrationArtifactError("calibration size and sequence length must be positive")


def validate_calibration_artifact(
    artifact: Mapping[str, Any],
    *,
    tokenizer: Any,
    model_id: str,
    model_revision: str,
    dataset_spec: DatasetSpec,
    seed: int,
    expected_size: int = CALIBRATION_SIZE,
    expected_sequence_length: int = CALIBRATION_SEQUENCE_LENGTH,
) -> None:
    if artifact.get("schema_version") != CALIBRATION_SCHEMA_VERSION:
        raise CalibrationArtifactError("unsupported calibration artifact schema")
    if artifact.get("sampling_algorithm") != SAMPLING_ALGORITHM:
        raise CalibrationArtifactError("calibration artifact uses a different sampling algorithm")
    if int(artifact.get("seed", -1)) != seed:
        raise CalibrationArtifactError("calibration artifact seed does not match the requested seed")
    if int(artifact.get("sample_count", -1)) != expected_size:
        raise CalibrationArtifactError("calibration artifact does not contain the required sample count")
    if int(artifact.get("sequence_length", -1)) != expected_sequence_length:
        raise CalibrationArtifactError("calibration artifact does not use the required sequence length")

    expected_dataset = {
        "name": dataset_spec.name,
        "repo_id": dataset_spec.repo_id,
        "config": dataset_spec.config,
        "split": dataset_spec.split,
        "revision": dataset_spec.revision,
        "row_count": dataset_spec.row_count,
    }
    actual_dataset = artifact.get("dataset", {})
    for key, expected in expected_dataset.items():
        if actual_dataset.get(key) != expected:
            raise CalibrationArtifactError(f"calibration dataset {key} does not match: {actual_dataset.get(key)!r}")

    expected_tokenizer = tokenizer_identity(tokenizer, model_id, model_revision)
    actual_tokenizer = artifact.get("tokenizer", {})
    for key in ("model_id", "model_revision", "class", "vocab_sha256"):
        if actual_tokenizer.get(key) != expected_tokenizer[key]:
            raise CalibrationArtifactError(f"calibration tokenizer {key} does not match")

    samples = artifact.get("samples")
    if not isinstance(samples, list) or len(samples) != expected_size:
        raise CalibrationArtifactError("calibration samples are absent or incomplete")
    indices: list[int] = []
    hashes: list[str] = []
    for position, sample in enumerate(samples):
        ids = [int(value) for value in sample.get("input_ids", [])]
        if len(ids) != expected_sequence_length:
            raise CalibrationArtifactError(f"sample {position} is not exactly {expected_sequence_length} tokens")
        token_hash = token_ids_sha256(ids)
        if sample.get("token_sha256") != token_hash:
            raise CalibrationArtifactError(f"sample {position} token hash is invalid")
        text_ids = encode_text(
            tokenizer,
            str(sample.get("text", "")),
            truncation=True,
            max_length=expected_sequence_length,
        )
        if text_ids != ids:
            raise CalibrationArtifactError(
                f"sample {position} text no longer tokenizes to its recorded token IDs"
            )
        indices.append(int(sample["document_index"]))
        hashes.append(token_hash)
    if len(set(indices)) != len(indices):
        raise CalibrationArtifactError("calibration document indices are not unique")
    if artifact.get("selected_document_indices") != indices:
        raise CalibrationArtifactError("selected_document_indices does not match sample order")
    if artifact.get("selected_token_hashes") != hashes:
        raise CalibrationArtifactError("selected_token_hashes does not match sample order")
    if artifact.get("artifact_sha256") != artifact_sha256(artifact):
        raise CalibrationArtifactError("calibration artifact checksum is invalid")


def build_gptq(args: Any, tokenizer: Any, artifact: Mapping[str, Any]) -> None:
    try:
        from gptqmodel import GPTQConfig, GPTQModel
    except ImportError as exc:
        traceback.print_exception(exc)
        raise SystemExit("GPTQ quantization requires the pinned gptqmodel runtime.") from exc

    quantize_config = GPTQConfig(bits=args.bits, group_size=128, desc_act=False)
    examples = [
        {"input_ids": list(sample["input_ids"]), "attention_mask": [1] * artifact["sequence_length"]}
        for sample in artifact["samples"]
    ]
    model = GPTQModel.load(
        args.model_id,
        quantize_config,
        revision=args.model_revision,
        trust_remote_code=args.trust_remote_code,
    )
    model.quantize(examples, batch_size=1)
    model.save(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


def build_awq(args: Any, tokenizer: Any, artifact: Mapping[str, Any]) -> None:
    try:
        from awq import AutoAWQForCausalLM
    except ImportError as exc:
        traceback.print_exception(exc)
        raise SystemExit("AWQ quantization requires the pinned autoawq runtime.") from exc

    model = AutoAWQForCausalLM.from_pretrained(
        args.model_id,
        revision=args.model_revision,
        trust_remote_code=args.trust_remote_code,
    )
    quant_config = {"zero_point": True, "q_group_size": 128, "w_bit": args.bits, "version": "GEMM"}
    model.quantize(
        tokenizer,
        quant_config=quant_config,
        # AutoAWQ's pinned get_calib_dataset helper accepts pre-tokenized
        # list[list[int]] input. Passing the artifact IDs avoids text stripping,
        # special-token defaults, and a second tokenizer code path.
        calib_data=[list(sample["input_ids"]) for sample in artifact["samples"]],
        max_calib_samples=int(artifact["sample_count"]),
        max_calib_seq_len=int(artifact["sequence_length"]),
    )
    model.save_quantized(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


def write_calibration_receipt(path: Path, artifact: Mapping[str, Any], args: Any) -> None:
    receipt = {
        "schema_version": 1,
        "artifact_sha256": artifact["artifact_sha256"],
        "model_id": args.model_id,
        "model_revision": args.model_revision,
        "method": args.method,
        "bits": args.bits,
        "dataset": deepcopy(artifact["dataset"]),
        "tokenizer": deepcopy(artifact["tokenizer"]),
        "seed": artifact["seed"],
        "sample_count": artifact["sample_count"],
        "sequence_length": artifact["sequence_length"],
        "selected_document_indices": list(artifact["selected_document_indices"]),
        "selected_token_hashes": list(artifact["selected_token_hashes"]),
    }
    write_json_atomic(path, receipt)


def tokenizer_identity(tokenizer: Any, model_id: str, model_revision: str) -> dict[str, Any]:
    try:
        vocab = tokenizer.get_vocab()
    except (AttributeError, NotImplementedError):
        vocab = None
    if vocab is None:
        vocab_payload = {"vocab_size": int(getattr(tokenizer, "vocab_size", -1))}
    else:
        vocab_payload = sorted((str(token), int(index)) for token, index in vocab.items())
    vocab_sha = hashlib.sha256(canonical_json(vocab_payload)).hexdigest()
    return {
        "model_id": model_id,
        "model_revision": model_revision,
        "class": tokenizer.__class__.__name__,
        "name_or_path": str(getattr(tokenizer, "name_or_path", model_id)),
        "vocab_size": int(getattr(tokenizer, "vocab_size", len(vocab) if vocab is not None else -1)),
        "vocab_sha256": vocab_sha,
    }


def encode_text(
    tokenizer: Any,
    text: str,
    *,
    truncation: bool,
    max_length: int | None = None,
) -> list[int]:
    kwargs: dict[str, Any] = {"add_special_tokens": False, "truncation": truncation}
    if max_length is not None:
        kwargs["max_length"] = max_length
    encoded = tokenizer(text, **kwargs)
    values = encoded["input_ids"]
    if values and isinstance(values[0], list):
        if len(values) != 1:
            raise CalibrationArtifactError("tokenizer returned an unexpected batch")
        values = values[0]
    return [int(value) for value in values]


def token_ids_sha256(token_ids: Sequence[int]) -> str:
    return hashlib.sha256(canonical_json([int(value) for value in token_ids])).hexdigest()


def artifact_sha256(artifact: Mapping[str, Any]) -> str:
    payload = dict(artifact)
    payload.pop("artifact_sha256", None)
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise CalibrationArtifactError(f"expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write("\n")
    os.replace(temporary, path)


if __name__ == "__main__":
    main()
