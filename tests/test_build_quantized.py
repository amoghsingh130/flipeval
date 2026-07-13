import json
import sys
from copy import deepcopy
from types import SimpleNamespace

import pytest

from scripts.build_quantized import (
    CalibrationArtifactError,
    DatasetSpec,
    artifact_sha256,
    build_awq,
    build_gptq,
    create_calibration_artifact,
    create_calibration_artifact_from_stream,
    token_ids_sha256,
    validate_calibration_artifact,
    write_calibration_receipt,
)


SPEC = DatasetSpec("fixture", "fixture/repo", "default", "train", "abc123", 6)


class ToyDataset(list):
    _fingerprint = "fixture-fingerprint"


class ToyTokenizer:
    name_or_path = "fixture/model"
    vocab_size = 128

    def __call__(self, text, **kwargs):
        values = [ord(character) for character in text]
        if kwargs.get("truncation") and kwargs.get("max_length") is not None:
            values = values[: kwargs["max_length"]]
        return {"input_ids": values, "attention_mask": [1] * len(values)}

    def get_vocab(self):
        return {chr(index): index for index in range(128)}

    def save_pretrained(self, path):
        return path


def _artifact(seed=0):
    dataset = ToyDataset(
        [
            {"text": "x"},
            {"text": "abcdefgh"},
            {"text": "ijklmnop"},
            {"text": "y"},
            {"text": "qrstuvwx"},
            {"text": "ABCDEFGH"},
        ]
    )
    return create_calibration_artifact(
        dataset,
        ToyTokenizer(),
        model_id="fixture/model",
        model_revision="model123",
        dataset_spec=SPEC,
        seed=seed,
        size=2,
        sequence_length=4,
    )


def test_calibration_artifact_is_deterministic_and_skips_short_documents():
    one = _artifact(seed=0)
    two = _artifact(seed=0)
    other = _artifact(seed=1)
    assert one == two
    assert one["artifact_sha256"] == artifact_sha256(one)
    assert one["selected_document_indices"] == [2, 5]
    assert one["skipped_short_document_count"] == 1
    assert other["selected_document_indices"] == [4, 2]
    assert one["artifact_sha256"] != other["artifact_sha256"]
    assert all(len(sample["input_ids"]) == 4 for sample in one["samples"])
    assert one["selected_token_hashes"] == [
        token_ids_sha256(sample["input_ids"]) for sample in one["samples"]
    ]


def test_stream_retrieval_preserves_exact_registered_permutation_order():
    dataset = ToyDataset(
        [
            {"text": "x"},
            {"text": "abcdefgh"},
            {"text": "ijklmnop"},
            {"text": "y"},
            {"text": "qrstuvwx"},
            {"text": "ABCDEFGH"},
        ]
    )
    indexed = create_calibration_artifact(
        dataset,
        ToyTokenizer(),
        model_id="fixture/model",
        model_revision="model123",
        dataset_spec=SPEC,
        seed=0,
        size=2,
        sequence_length=4,
    )
    streamed = create_calibration_artifact_from_stream(
        lambda: iter(dataset),
        ToyTokenizer(),
        model_id="fixture/model",
        model_revision="model123",
        dataset_spec=SPEC,
        seed=0,
        size=2,
        sequence_length=4,
        retrieval_window=2,
    )
    assert streamed["selected_document_indices"] == indexed["selected_document_indices"]
    assert streamed["selected_token_hashes"] == indexed["selected_token_hashes"]
    assert [sample["input_ids"] for sample in streamed["samples"]] == [
        sample["input_ids"] for sample in indexed["samples"]
    ]
    assert streamed["retrieval"] == {
        "strategy": "sequential-stream-index-retrieval",
        "window_size": 2,
        "passes": 2,
        "stream_rows_scanned": 10,
    }


def test_calibration_artifact_fails_when_too_few_documents_are_eligible():
    with pytest.raises(CalibrationArtifactError, match="only 0"):
        create_calibration_artifact(
            ToyDataset([{"text": "a"}, {"text": "bc"}]),
            ToyTokenizer(),
            model_id="fixture/model",
            model_revision="model123",
            dataset_spec=SPEC,
            seed=0,
            size=1,
            sequence_length=4,
        )


def test_calibration_validation_rejects_tampering():
    artifact = _artifact()
    tampered = deepcopy(artifact)
    tampered["samples"][0]["input_ids"][0] += 1
    with pytest.raises(CalibrationArtifactError, match="token hash"):
        validate_calibration_artifact(
            tampered,
            tokenizer=ToyTokenizer(),
            model_id="fixture/model",
            model_revision="model123",
            dataset_spec=SPEC,
            seed=0,
            expected_size=2,
            expected_sequence_length=4,
        )


def test_gptq_and_awq_builders_consume_the_same_artifact(monkeypatch, tmp_path):
    calls = {}
    artifact = _artifact()

    class Config:
        def __init__(self, **kwargs):
            calls["config"] = kwargs

    class GPTQModel:
        @classmethod
        def load(cls, model_id, config, **kwargs):
            calls["gptq_load"] = (model_id, kwargs)
            return cls()

        def quantize(self, examples, **kwargs):
            calls["gptq_quantize"] = (examples, kwargs)

        def save(self, path):
            calls["gptq_save"] = path

    class AWQModel:
        @classmethod
        def from_pretrained(cls, model_id, **kwargs):
            calls["awq_load"] = (model_id, kwargs)
            return cls()

        def quantize(self, tokenizer, **kwargs):
            calls["awq_quantize"] = kwargs

        def save_quantized(self, path):
            calls["awq_save"] = path

    monkeypatch.setitem(sys.modules, "gptqmodel", SimpleNamespace(GPTQConfig=Config, GPTQModel=GPTQModel))
    monkeypatch.setitem(sys.modules, "awq", SimpleNamespace(AutoAWQForCausalLM=AWQModel))
    common = {
        "bits": 4,
        "model_id": "fixture/model",
        "model_revision": "model123",
        "trust_remote_code": True,
    }
    gptq_args = SimpleNamespace(**common, method="gptq", output_dir=tmp_path / "gptq")
    awq_args = SimpleNamespace(**common, method="awq", output_dir=tmp_path / "awq")
    tokenizer = ToyTokenizer()

    build_gptq(gptq_args, tokenizer, artifact)
    build_awq(awq_args, tokenizer, artifact)

    expected_ids = [sample["input_ids"] for sample in artifact["samples"]]
    assert [example["input_ids"] for example in calls["gptq_quantize"][0]] == expected_ids
    assert calls["awq_quantize"]["calib_data"] == expected_ids
    assert calls["awq_quantize"]["max_calib_samples"] == 2
    assert calls["awq_quantize"]["max_calib_seq_len"] == 4
    assert calls["config"] == {"bits": 4, "group_size": 128, "desc_act": False}
    assert calls["gptq_load"] == (
        "fixture/model",
        {"revision": "model123", "trust_remote_code": True},
    )
    assert calls["awq_load"] == (
        "fixture/model",
        {"revision": "model123", "trust_remote_code": True},
    )


def test_checkpoint_receipts_prove_pairing(tmp_path):
    artifact = _artifact()
    common = {
        "bits": 4,
        "model_id": "fixture/model",
        "model_revision": "model123",
    }
    first = tmp_path / "gptq.json"
    second = tmp_path / "awq.json"
    write_calibration_receipt(first, artifact, SimpleNamespace(**common, method="gptq"))
    write_calibration_receipt(second, artifact, SimpleNamespace(**common, method="awq"))
    gptq = json.loads(first.read_text())
    awq = json.loads(second.read_text())
    assert gptq["artifact_sha256"] == awq["artifact_sha256"]
    assert gptq["selected_document_indices"] == awq["selected_document_indices"]
    assert gptq["selected_token_hashes"] == awq["selected_token_hashes"]


def test_pinned_autoawq_preserves_pre_tokenized_calibration_ids():
    pytest.importorskip("awq")
    from awq.utils.calib_data import get_calib_dataset

    token_ids = [[1, 2, 3, 4], [5, 6, 7, 8]]
    blocks = get_calib_dataset(data=token_ids, n_samples=2, max_seq_len=4)
    assert [block.tolist()[0] for block in blocks] == token_ids
