import json
import sys
from copy import deepcopy
from types import ModuleType, SimpleNamespace

import pytest

from scripts.build_quantized import (
    CalibrationArtifactError,
    DatasetSpec,
    _strip_revision_from_shell_model,
    artifact_sha256,
    build_awq,
    build_gptq,
    create_calibration_artifact,
    create_calibration_artifact_from_stream,
    token_ids_sha256,
    validate_calibration_artifact,
    verify_stream_row_count,
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

    # build_gptq imports gptqmodel.utils.hf to install the revision shim; provide
    # a fake submodule so the from-import resolves against the mocked package.
    fake_hf = ModuleType("gptqmodel.utils.hf")
    fake_hf.build_shell_model = lambda loader, config, trust_remote_code=True, **kw: None
    fake_utils = ModuleType("gptqmodel.utils")
    fake_utils.hf = fake_hf
    monkeypatch.setitem(sys.modules, "gptqmodel", SimpleNamespace(GPTQConfig=Config, GPTQModel=GPTQModel))
    monkeypatch.setitem(sys.modules, "gptqmodel.utils", fake_utils)
    monkeypatch.setitem(sys.modules, "gptqmodel.utils.hf", fake_hf)
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


def test_revision_shim_strips_only_revision_from_shell_model():
    received = {}

    def spy(loader, config, trust_remote_code=True, **kwargs):
        received["loader"] = loader
        received["config"] = config
        received["trust_remote_code"] = trust_remote_code
        received["kwargs"] = kwargs
        return "SHELL_MODEL"

    wrapped = _strip_revision_from_shell_model(spy)
    out = wrapped(
        "LOADER",
        "CONFIG",
        trust_remote_code=False,
        revision="pinnedrev",
        device_map=None,
        _fast_init=True,
        extra="untouched",
    )

    # Return value flows through, revision is dropped, every other kwarg and the
    # positional/keyword forwarding is byte-for-byte unchanged.
    assert out == "SHELL_MODEL"
    assert received["loader"] == "LOADER"
    assert received["config"] == "CONFIG"
    assert received["trust_remote_code"] is False
    assert received["kwargs"] == {"device_map": None, "_fast_init": True, "extra": "untouched"}
    assert "revision" not in received["kwargs"]
    assert wrapped._flipeval_strips_revision is True


def test_revision_shim_is_a_noop_when_revision_absent():
    received = {}

    def spy(loader, config, trust_remote_code=True, **kwargs):
        received["kwargs"] = kwargs
        return "SHELL_MODEL"

    wrapped = _strip_revision_from_shell_model(spy)
    out = wrapped("LOADER", "CONFIG", device_map=None, _fast_init=False)

    assert out == "SHELL_MODEL"
    assert received["kwargs"] == {"device_map": None, "_fast_init": False}


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


def test_verify_stream_row_count_accepts_exact_registered_count():
    rows = [{"text": str(index)} for index in range(SPEC.row_count)]
    assert verify_stream_row_count(lambda: iter(rows), SPEC) == SPEC.row_count


def test_verify_stream_row_count_fails_closed_on_understated_universe():
    rows = [{"text": str(index)} for index in range(SPEC.row_count - 1)]
    with pytest.raises(CalibrationArtifactError, match="registered row_count"):
        verify_stream_row_count(lambda: iter(rows), SPEC)


def test_verify_stream_row_count_fails_closed_on_overstated_universe():
    rows = [{"text": str(index)} for index in range(SPEC.row_count + 2)]
    with pytest.raises(CalibrationArtifactError, match="registered row_count"):
        verify_stream_row_count(lambda: iter(rows), SPEC)


def test_pinned_autoawq_preserves_pre_tokenized_calibration_ids():
    pytest.importorskip("awq")
    from awq.utils.calib_data import get_calib_dataset

    token_ids = [[1, 2, 3, 4], [5, 6, 7, 8]]
    blocks = get_calib_dataset(data=token_ids, n_samples=2, max_seq_len=4)
    assert [block.tolist()[0] for block in blocks] == token_ids


def test_pinned_gptqmodel_exposes_expected_api():
    pytest.importorskip("gptqmodel")
    from gptqmodel import GPTQConfig, GPTQModel

    assert GPTQConfig is not None
    assert GPTQModel is not None


def test_pinned_gptqmodel_builds_qwen2_shell_model_under_pinned_transformers():
    # Closes the gap the cell-2 canary exposed: importing gptqmodel succeeds,
    # but constructing the shell model through gptqmodel's own path leaks
    # `revision` into transformers>=5 from_config and dies. This is a real
    # CPU-side construction (weights stay on 'meta'; no GPU, no network).
    pytest.importorskip("gptqmodel")
    pytest.importorskip("transformers")
    from gptqmodel.utils.hf import build_shell_model
    from transformers import AutoModelForCausalLM, Qwen2Config

    config = Qwen2Config(
        vocab_size=256,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=128,
    )
    # build_shell_model unconditionally deletes device_map/_fast_init, so both
    # must be present; revision is the leaking hub-only kwarg.
    kwargs = dict(revision="pinnedrev", device_map=None, _fast_init=False)

    # The raw path still fails in exactly this shape under the pinned runtime.
    with pytest.raises(TypeError, match="revision"):
        build_shell_model(AutoModelForCausalLM, config=config, trust_remote_code=False, **dict(kwargs))

    # The shim recovers a clean construction on the same path.
    shimmed = _strip_revision_from_shell_model(build_shell_model)
    model = shimmed(AutoModelForCausalLM, config=config, trust_remote_code=False, **dict(kwargs))
    assert model.__class__.__name__ == "Qwen2ForCausalLM"
