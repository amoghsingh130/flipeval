from __future__ import annotations

import hashlib
from dataclasses import asdict
from typing import Any

import torch

from .config import MethodConfig, RunConfig
from .tasks import EvalItem, extract_gsm8k_answer


def load_model_and_tokenizer(method: MethodConfig, run: RunConfig):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch_dtype = _dtype(method.dtype)
    tokenizer = AutoTokenizer.from_pretrained(
        method.model_id,
        revision=method.revision,
        trust_remote_code=method.trust_remote_code,
        padding_side="left",
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs: dict[str, Any] = {}
    if method.quantization_backend == "gptq_torch":
        from transformers import GPTQConfig

        model_kwargs["quantization_config"] = GPTQConfig(bits=4, backend="gptq_torch")
    elif method.quantization_backend is not None:
        raise ValueError(f"unknown quantization backend: {method.quantization_backend}")

    model = AutoModelForCausalLM.from_pretrained(
        method.model_id,
        revision=method.revision,
        trust_remote_code=method.trust_remote_code,
        torch_dtype=torch_dtype,
        device_map=run.device_map,
        **model_kwargs,
    )
    model.eval()
    return model, tokenizer


def evaluate_item(
    model,
    tokenizer,
    item: EvalItem,
    max_new_tokens: int,
    prompt_style: str = "raw",
) -> dict[str, Any]:
    rendered_prompt = render_prompt(tokenizer, item.prompt, prompt_style)
    if item.choices:
        prediction, scores = score_multiple_choice(
            model,
            tokenizer,
            rendered_prompt,
            item.choices,
            separate_continuation=prompt_style == "chat",
        )
        raw_output = prediction
    else:
        raw_output = generate_text(model, tokenizer, rendered_prompt, max_new_tokens=max_new_tokens)
        prediction = extract_gsm8k_answer(raw_output)
        scores = None

    correct = normalize_answer(prediction) == normalize_answer(item.gold)
    return {
        "item_id": item.item_id,
        "task": item.task,
        "prompt_hash": hashlib.sha256(rendered_prompt.encode("utf-8")).hexdigest()[:16],
        "gold": item.gold,
        "prediction": prediction,
        "correct": bool(correct),
        "raw_output": raw_output,
        "scores": scores,
        "metadata": {**(item.metadata or {}), "prompt_style": prompt_style},
    }


def render_prompt(tokenizer, prompt: str, prompt_style: str) -> str:
    if prompt_style == "raw":
        return prompt
    if prompt_style == "chat":
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            tokenize=False,
        )
    raise ValueError(f"unknown prompt style: {prompt_style}")


@torch.no_grad()
def score_multiple_choice(
    model,
    tokenizer,
    prompt: str,
    choices: list[str],
    separate_continuation: bool = False,
) -> tuple[str, dict[str, float]]:
    scores: dict[str, float] = {}
    device = _first_device(model)
    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
    prompt_len = prompt_ids.shape[1]

    for choice in choices:
        if separate_continuation:
            continuation = tokenizer(" " + choice, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
            full = torch.cat((prompt_ids, continuation), dim=1)
        else:
            full = tokenizer(prompt + " " + choice, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
        logits = model(full).logits[:, :-1, :]
        labels = full[:, 1:]
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
        token_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
        start = max(prompt_len - 1, 0)
        scores[choice] = float(token_log_probs[:, start:].sum().item())

    prediction = max(scores.items(), key=lambda kv: kv[1])[0]
    return prediction, scores


@torch.no_grad()
def generate_text(model, tokenizer, prompt: str, max_new_tokens: int) -> str:
    device = _first_device(model)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    output_ids = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    continuation = output_ids[0, inputs.input_ids.shape[1] :]
    return tokenizer.decode(continuation, skip_special_tokens=True).strip()


def method_record(method: MethodConfig) -> dict[str, Any]:
    return asdict(method)


def normalize_answer(value: str) -> str:
    return str(value).strip().replace(",", "").upper()


def _dtype(name: str):
    normalized = name.lower()
    if normalized in {"float16", "fp16", "half"}:
        return torch.float16
    if normalized in {"bfloat16", "bf16"}:
        return torch.bfloat16
    if normalized in {"float32", "fp32"}:
        return torch.float32
    raise ValueError(f"unknown dtype: {name}")


def _first_device(model) -> torch.device:
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
