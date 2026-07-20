from __future__ import annotations

import hashlib
from dataclasses import asdict
from typing import Any

import torch

from .config import MethodConfig, RunConfig, validate_quantization_backend
from .tasks import EvalItem, extract_gsm8k_answer


def load_model_and_tokenizer(method: MethodConfig, run: RunConfig):
    """Load a method's model and tokenizer.

    Returns ``(model, tokenizer, load_info)``. ``load_info`` carries the runtime
    facts the manifest must record -- the load route and the quantized-linear
    kernel that it actually selected. Kernel identity is a registered nuisance
    variable, so it is read from the loaded model rather than assumed.

    Quantized checkpoints are loaded through their native library with an
    explicit kernel choice. The transformers/HfQuantizer entry point is not used
    for them: in the cell-3 image it lets the framework auto-select a prebuilt
    kernel, which fails for both methods (GPTQ needs the absent `optimum`; AWQ
    routes into `AwqMarlinLinear` with no Marlin runtime). See
    docs/PACE_ENVIRONMENT_NOTE.md.
    """
    # Validate before touching the network or disk: an unroutable backend should
    # fail in milliseconds, not after a tokenizer or checkpoint fetch.
    backend = validate_quantization_backend(method.quantization_backend)

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        method.model_id,
        revision=method.revision,
        trust_remote_code=method.trust_remote_code,
        padding_side="left",
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    if backend == "gptqmodel_torch":
        model = _load_gptqmodel_torch(method, run)
    elif backend == "awq_gemm":
        model = _load_awq_gemm(method, run)
    else:
        model = _load_unquantized(method, run)

    model.eval()
    load_info = {
        "quantization_backend": backend,
        "kernel": _kernel_id(model, backend),
    }
    return model, tokenizer, load_info


def _load_unquantized(method: MethodConfig, run: RunConfig):
    from transformers import AutoModelForCausalLM

    return AutoModelForCausalLM.from_pretrained(
        method.model_id,
        revision=method.revision,
        trust_remote_code=method.trust_remote_code,
        torch_dtype=_dtype(method.dtype),
        device_map=run.device_map,
    )


def _load_gptqmodel_torch(method: MethodConfig, run: RunConfig):
    """GPTQ via GPTQModel.load with the TORCH backend (kernel: TorchLinear)."""
    from gptqmodel import BACKEND, GPTQModel

    loaded = GPTQModel.load(
        method.model_id,
        backend=BACKEND.TORCH,
        device=_resolve_device(run.device_map),
    )
    return getattr(loaded, "model", loaded)


def _load_awq_gemm(method: MethodConfig, run: RunConfig):
    """AWQ via AutoAWQ's native loader (kernel: WQLinear_GEMM)."""
    from awq import AutoAWQForCausalLM

    loaded = AutoAWQForCausalLM.from_quantized(
        method.model_id,
        fuse_layers=False,
        trust_remote_code=method.trust_remote_code,
        safetensors=True,
    )
    return getattr(loaded, "model", loaded)


def _kernel_id(model, backend: str | None) -> str:
    """Read the quantized-linear kernel class from the loaded model.

    Deliberately an isinstance check against each loader library's own base
    class rather than a substring match on class names: the kernel id goes into
    every run manifest as a registered nuisance variable, and a name-sniffing
    detector returns '?' for kernels like ``TorchLinear`` whose names contain
    none of the expected substrings. Fails closed -- an unidentifiable kernel is
    an unrecordable run, not a warning.
    """
    if backend is None:
        return "none"
    if backend == "gptqmodel_torch":
        from gptqmodel.nn_modules.qlinear import BaseQuantLinear as base
    elif backend == "awq_gemm":
        from awq.modules.linear.gemm import WQLinear_GEMM as base
    else:
        raise ValueError(f"no kernel probe for backend: {backend}")

    for _, module in model.named_modules():
        if isinstance(module, base):
            return type(module).__name__
    raise RuntimeError(
        f"backend {backend!r} loaded but no quantized linear layer was found; "
        "the kernel id is a registered manifest field and cannot be left unknown"
    )


def _resolve_device(device_map: str) -> str:
    """GPTQModel.load takes a device, not a transformers device_map."""
    if device_map in {"auto", "cuda"}:
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device_map


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
