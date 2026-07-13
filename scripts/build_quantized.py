from __future__ import annotations

import argparse
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local 4-bit GPTQ/AWQ checkpoints for calibration-seed sweeps.")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--method", choices=["gptq", "awq"], required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--bits", type=int, default=4)
    parser.add_argument("--calib-size", type=int, default=128)
    parser.add_argument("--max-calib-tokens", type=int, default=512)
    parser.add_argument("--trust-remote-code", action="store_true")
    args = parser.parse_args()

    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise SystemExit("Missing transformers. Install with `pip install -r requirements.txt`.") from exc

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=args.trust_remote_code)
    calib_texts = calibration_texts(args.seed, args.calib_size)

    if args.method == "gptq":
        build_gptq(args, tokenizer, calib_texts)
    else:
        build_awq(args, tokenizer, calib_texts)


def calibration_texts(seed: int, size: int) -> list[str]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Missing datasets. Install with `pip install -r requirements.txt`.") from exc

    ds = load_dataset("allenai/c4", "en", split="train", streaming=True)
    rng = random.Random(seed)
    reservoir: list[str] = []
    for idx, row in enumerate(ds):
        text = str(row.get("text", "")).strip()
        if not text:
            continue
        if len(reservoir) < size:
            reservoir.append(text)
        else:
            j = rng.randint(0, idx)
            if j < size:
                reservoir[j] = text
        if idx > size * 200:
            break
    return reservoir


def build_gptq(args, tokenizer, calib_texts: list[str]) -> None:
    try:
        from gptqmodel import GPTQConfig, GPTQModel
    except ImportError as exc:
        raise SystemExit("GPTQ quantization requires `pip install gptqmodel`.") from exc

    quantize_config = GPTQConfig(
        bits=args.bits,
        group_size=128,
        desc_act=False,
    )
    examples = [tokenizer(text, truncation=True, max_length=args.max_calib_tokens) for text in calib_texts]
    model = GPTQModel.load(
        args.model_id,
        quantize_config,
        trust_remote_code=args.trust_remote_code,
    )
    model.quantize(examples, batch_size=1)
    model.save(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


def build_awq(args, tokenizer, calib_texts: list[str]) -> None:
    try:
        from awq import AutoAWQForCausalLM
    except ImportError as exc:
        raise SystemExit("AWQ quantization requires `pip install autoawq`.") from exc

    model = AutoAWQForCausalLM.from_pretrained(args.model_id, trust_remote_code=args.trust_remote_code)
    quant_config = {
        "zero_point": True,
        "q_group_size": 128,
        "w_bit": args.bits,
        "version": "GEMM",
    }
    model.quantize(tokenizer, quant_config=quant_config, calib_data=calib_texts, max_calib_seq_len=args.max_calib_tokens)
    model.save_quantized(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
