import hashlib
import json
import math
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


def test_manifest_upgrades_legacy_file(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"run_name": "r", "methods": [], "tasks": []}), encoding="utf-8")
    merged = merge_manifest(path, {"run_name": "r", "started_at": "t", "config": "/c", "methods": [], "tasks": []})
    assert merged["runs"] == [{"started_at": "t", "methods": [], "tasks": []}]


def test_gptq_backend_is_config_driven(monkeypatch, tmp_path):
    captured = {}

    class Tokenizer:
        pad_token_id = 0
        eos_token_id = 1

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

    class Model:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            captured.update(kwargs)
            return cls()

        def eval(self):
            return self

    class GPTQConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setitem(sys.modules, "transformers", SimpleNamespace(AutoModelForCausalLM=Model, AutoTokenizer=Tokenizer, GPTQConfig=GPTQConfig))
    method = MethodConfig("renamed_method", "model", quantization_backend="gptq_torch")
    run = RunConfig("r", tmp_path, method, [], [], device_map="cpu")
    load_model_and_tokenizer(method, run)
    assert captured["quantization_config"].kwargs == {"bits": 4, "backend": "gptq_torch"}
