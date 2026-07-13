import sys
from types import SimpleNamespace

from scripts.build_quantized import build_gptq


def test_gptq_builder_uses_gptqmodel(monkeypatch, tmp_path):
    calls = {}

    class Config:
        def __init__(self, **kwargs):
            calls["config"] = kwargs

    class Model:
        @classmethod
        def load(cls, model_id, config, **kwargs):
            calls["load"] = (model_id, kwargs)
            return cls()

        def quantize(self, examples, **kwargs):
            calls["quantize"] = (examples, kwargs)

        def save(self, path):
            calls["save"] = path

    class Tokenizer:
        def __call__(self, text, **kwargs):
            return {"input_ids": [len(text)], "attention_mask": [1]}

        def save_pretrained(self, path):
            calls["tokenizer_save"] = path

    monkeypatch.setitem(sys.modules, "gptqmodel", SimpleNamespace(GPTQConfig=Config, GPTQModel=Model))
    args = SimpleNamespace(bits=4, max_calib_tokens=128, model_id="model", trust_remote_code=True, output_dir=tmp_path)
    build_gptq(args, Tokenizer(), ["one", "two"])
    assert calls["config"] == {"bits": 4, "group_size": 128, "desc_act": False}
    assert calls["load"] == ("model", {"trust_remote_code": True})
    assert calls["quantize"][1] == {"batch_size": 1}
    assert calls["save"] == tmp_path
