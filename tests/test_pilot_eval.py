import hashlib
import json
import math
import multiprocessing
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from pilot_eval.config import MethodConfig, RunConfig
from pilot_eval.modeling import evaluate_item, load_model_and_tokenizer, score_multiple_choice
from pilot_eval.run import merge_manifest
from pilot_eval.tasks import EvalItem, GSM8K_FEWSHOT, load_gsm8k


class StubTokenizer:
    pad_token_id = 0
    eos_token_id = 1

    def __init__(self):
        self.calls = []

    def apply_chat_template(self, messages, add_generation_prompt, tokenize):
        assert messages[0]["role"] == "user"
        assert add_generation_prompt and not tokenize
        return f"<user>{messages[0]['content']}<assistant>"

    def __call__(self, text, return_tensors, add_special_tokens=False):
        self.calls.append(text)
        return SimpleNamespace(input_ids=torch.tensor([[ord(char) % 16 for char in text]]))


class UniformModel:
    def parameters(self):
        yield torch.zeros(1)

    def __call__(self, input_ids):
        return SimpleNamespace(logits=torch.zeros((1, input_ids.shape[1], 16)))


def _merge_manifest_worker(path, index):
    merge_manifest(
        Path(path),
        {
            "run_name": "parallel",
            "started_at": f"t{index}",
            "config": "/config",
            "methods": [{"name": f"method-{index}"}],
            "tasks": [{"name": "mmlu"}],
        },
    )


def test_chat_multiple_choice_scores_only_continuation_span():
    tokenizer = StubTokenizer()
    prompt = "<user>Question?<assistant>"
    _, scores = score_multiple_choice(UniformModel(), tokenizer, prompt, ["A", "B"], separate_continuation=True)
    assert tokenizer.calls == [prompt, " A", " B"]
    expected = -2 * math.log(16)
    assert scores["A"] == pytest.approx(expected)
    assert scores["B"] == pytest.approx(expected)


def test_chat_style_is_recorded_and_hashes_rendered_prompt():
    item = EvalItem("mmlu", "1", "Question?", "A", ["A", "B"], {"subject": "x"})
    tokenizer = StubTokenizer()
    result = evaluate_item(UniformModel(), tokenizer, item, 1, prompt_style="chat")
    rendered = "<user>Question?<assistant>"
    assert result["prompt_hash"] == hashlib.sha256(rendered.encode()).hexdigest()[:16]
    assert result["metadata"] == {"subject": "x", "prompt_style": "chat"}


def test_raw_prompt_hash_matches_archived_gsm8k_record():
    question = (
        "Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her "
        "friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. "
        "How much in dollars does she make every day at the farmers' market?"
    )
    prompt = f"{GSM8K_FEWSHOT}Question: {question}\nAnswer:"
    assert hashlib.sha256(prompt.encode()).hexdigest()[:16] == "2b93ef0019f94fd7"


def test_gsm8k_jsonl_fallback_is_offline_and_honors_limit(monkeypatch, tmp_path):
    source = tmp_path / "test.jsonl"
    source.write_text(
        '\n'.join(
            [
                json.dumps({"question": "What is 2 + 3?", "answer": "Work. #### 5"}),
                json.dumps({"question": "What is 4 + 6?", "answer": "Work. #### 10"}),
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GSM8K_JSONL", str(source))

    items = load_gsm8k(split="test", limit=1, fewshot=1)

    assert len(items) == 1
    assert items[0].item_id == "gsm8k:test:0"
    assert items[0].gold == "5"
    assert items[0].prompt.startswith(GSM8K_FEWSHOT)


def test_gsm8k_jsonl_fallback_rejects_malformed_rows(monkeypatch, tmp_path):
    source = tmp_path / "bad.jsonl"
    source.write_text(json.dumps({"question": "missing answer"}), encoding="utf-8")
    monkeypatch.setenv("GSM8K_JSONL", str(source))

    with pytest.raises(ValueError, match="question and answer"):
        load_gsm8k(split="test", limit=None, fewshot=0)


def test_manifest_merges_separate_invocations(tmp_path):
    path = tmp_path / "manifest.json"
    first = {"run_name": "r", "started_at": "t1", "config": "/c", "methods": [{"name": "fp16"}], "tasks": [{"name": "mmlu", "prompt_style": "raw"}]}
    second = {"run_name": "r", "started_at": "t2", "config": "/c", "methods": [{"name": "awq"}], "tasks": [{"name": "gsm8k", "prompt_style": "chat"}]}
    merge_manifest(path, first)
    merged = merge_manifest(path, second)
    assert {method["name"] for method in merged["methods"]} == {"fp16", "awq"}
    assert {task["name"] for task in merged["tasks"]} == {"mmlu", "gsm8k"}
    assert len(merged["runs"]) == 2


def test_manifest_merge_is_process_safe(tmp_path):
    path = tmp_path / "manifest.json"
    context = multiprocessing.get_context("fork")
    processes = [
        context.Process(target=_merge_manifest_worker, args=(path, index))
        for index in range(8)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=10)
        assert process.exitcode == 0

    merged = json.loads(path.read_text(encoding="utf-8"))
    assert {entry["name"] for entry in merged["methods"]} == {
        f"method-{index}" for index in range(8)
    }
    assert len(merged["runs"]) == 8


def test_manifest_upgrades_legacy_file(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"run_name": "r", "methods": [], "tasks": []}), encoding="utf-8")
    merged = merge_manifest(path, {"run_name": "r", "started_at": "t", "config": "/c", "methods": [], "tasks": []})
    assert merged["runs"] == [{"started_at": "t", "methods": [], "tasks": []}]


class _FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 1

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()


class _FakeQuantLinearBase:
    """Stands in for gptqmodel's BaseQuantLinear."""


class TorchLinear(_FakeQuantLinearBase):
    """Name matches the real cell-3 GPTQ kernel."""


class WQLinear_GEMM:  # noqa: N801 - mirrors the real AutoAWQ class name
    """Name matches the real cell-3 AWQ kernel."""


class _FakeModel:
    def __init__(self, quant_layer=None):
        self._quant_layer = quant_layer

    def named_modules(self):
        if self._quant_layer is not None:
            yield "model.layers.0.mlp.down_proj", self._quant_layer

    def eval(self):
        return self


def _install_fake_transformers(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(AutoModelForCausalLM=object, AutoTokenizer=_FakeTokenizer),
    )


def _install_fake_gptqmodel(monkeypatch, captured, quant_layer=None):
    layer = TorchLinear() if quant_layer is None else quant_layer

    class GPTQModel:
        @staticmethod
        def load(model_id, **kwargs):
            captured["model_id"] = model_id
            captured.update(kwargs)
            return SimpleNamespace(model=_FakeModel(layer))

    monkeypatch.setitem(sys.modules, "gptqmodel", SimpleNamespace(
        BACKEND=SimpleNamespace(TORCH="BACKEND.TORCH"), GPTQModel=GPTQModel))
    monkeypatch.setitem(sys.modules, "gptqmodel.nn_modules", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "gptqmodel.nn_modules.qlinear",
                        SimpleNamespace(BaseQuantLinear=_FakeQuantLinearBase))


def _install_fake_awq(monkeypatch, captured):
    class AutoAWQForCausalLM:
        @staticmethod
        def from_quantized(model_id, **kwargs):
            captured["model_id"] = model_id
            captured.update(kwargs)
            return SimpleNamespace(model=_FakeModel(WQLinear_GEMM()))

    monkeypatch.setitem(sys.modules, "awq",
                        SimpleNamespace(AutoAWQForCausalLM=AutoAWQForCausalLM))
    monkeypatch.setitem(sys.modules, "awq.modules", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "awq.modules.linear", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "awq.modules.linear.gemm",
                        SimpleNamespace(WQLinear_GEMM=WQLinear_GEMM))


def test_gptqmodel_torch_backend_is_config_driven(monkeypatch, tmp_path):
    captured = {}
    _install_fake_transformers(monkeypatch)
    _install_fake_gptqmodel(monkeypatch, captured)
    method = MethodConfig("gptq_s0", "ckpt/gptq", quantization_backend="gptqmodel_torch")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    _, _, info = load_model_and_tokenizer(method, run)

    assert captured["model_id"] == "ckpt/gptq"
    assert captured["backend"] == "BACKEND.TORCH"
    assert info["quantization_backend"] == "gptqmodel_torch"
    assert info["kernel"] == "TorchLinear"


def test_awq_gemm_backend_is_config_driven(monkeypatch, tmp_path):
    captured = {}
    _install_fake_transformers(monkeypatch)
    _install_fake_awq(monkeypatch, captured)
    method = MethodConfig("awq_s0", "ckpt/awq", quantization_backend="awq_gemm")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    _, _, info = load_model_and_tokenizer(method, run)

    assert captured["model_id"] == "ckpt/awq"
    assert captured["fuse_layers"] is False
    assert info["quantization_backend"] == "awq_gemm"
    assert info["kernel"] == "WQLinear_GEMM"


@pytest.mark.parametrize(
    "backend,installer",
    [("gptqmodel_torch", _install_fake_gptqmodel), ("awq_gemm", _install_fake_awq)],
)
def test_recorded_kernel_id_is_never_empty_or_unknown(monkeypatch, tmp_path, backend, installer):
    """The kernel id is a registered manifest field; '?' or '' must be impossible."""
    _install_fake_transformers(monkeypatch)
    installer(monkeypatch, {})
    method = MethodConfig("m", "ckpt", quantization_backend=backend)
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    _, _, info = load_model_and_tokenizer(method, run)

    assert info["kernel"] not in {"", "?", None}


def test_kernel_probe_fails_closed_when_no_quant_layer(monkeypatch, tmp_path):
    """A load that yields no quantized linear is unrecordable, so it must raise."""
    _install_fake_transformers(monkeypatch)
    _install_fake_gptqmodel(monkeypatch, {}, quant_layer=object())
    method = MethodConfig("m", "ckpt", quantization_backend="gptqmodel_torch")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    with pytest.raises(RuntimeError, match="no quantized linear layer"):
        load_model_and_tokenizer(method, run)


def test_retired_gptq_torch_backend_fails_loudly_and_is_not_remapped(monkeypatch, tmp_path):
    _install_fake_transformers(monkeypatch)
    method = MethodConfig("m", "ckpt", quantization_backend="gptq_torch")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    with pytest.raises(ValueError) as exc:
        load_model_and_tokenizer(method, run)

    message = str(exc.value)
    assert "gptqmodel_torch" in message
    assert "optimum" in message


def test_retired_backend_is_rejected_at_config_parse(tmp_path):
    from pilot_eval.config import load_config

    path = tmp_path / "c.yaml"
    path.write_text(
        "baseline: {name: fp16, model_id: m}\n"
        "methods:\n"
        "  - {name: q, model_id: ckpt, quantization_backend: gptq_torch}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="gptqmodel_torch"):
        load_config(path)


def test_unknown_backend_is_rejected(tmp_path):
    method = MethodConfig("m", "ckpt", quantization_backend="marlin_awq")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")

    with pytest.raises(ValueError, match="unknown quantization backend"):
        load_model_and_tokenizer(method, run)


def test_bridge_config_names_an_explicit_backend_for_every_quantized_method():
    """No quantized method may rely on framework kernel auto-selection."""
    from pilot_eval.config import QUANTIZATION_BACKENDS, load_config

    run = load_config(Path("configs/pace_bridge_chat.yaml"))
    assert run.baseline.quantization_backend is None
    assert [m.quantization_backend for m in run.methods] == (
        ["gptqmodel_torch"] * 3 + ["awq_gemm"] * 3
    )
    assert all(m.quantization_backend in QUANTIZATION_BACKENDS for m in run.methods)
