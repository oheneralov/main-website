import logging
import os
from typing import List
from pathlib import Path

import torch
from dotenv import load_dotenv
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
load_dotenv()

BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "Qwen/Qwen1.5-0.5B-Chat")
ADAPTER_DIR = os.getenv("ADAPTER_DIR", "./qwen05-finetuned-lora8")
MAX_NEW_TOKENS = 128

def load_adapter_model(base_model_id: str = BASE_MODEL_ID, adapter_dir: str = ADAPTER_DIR):
    """Load base model and attach the trained LoRA adapter."""
    adapter_path = Path(adapter_dir)
    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter dir not found: {adapter_path}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(adapter_dir, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    logging.info("Loading base model %s on %s", base_model_id, device)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        torch_dtype=dtype,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
    )
    if device != "cuda":
        base_model.to(device)

    logging.info("Attaching LoRA adapters from %s", adapter_dir)
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    # Quick sanity: ensure LoRA params are active
    model.print_trainable_parameters()
    model.eval()
    return model, tokenizer, device


def generate_responses(model, tokenizer, device: str, prompts: List[str]):
    for idx, prompt in enumerate(prompts, start=1):
        # Match the training prompt pattern: "Instruction... Input... Response..."
        formatted = f"Instruction: {prompt}\nInput: \nResponse: "
        enc = tokenizer(
            formatted,
            return_tensors="pt",
            padding=False,
            truncation=True,
            max_length=tokenizer.model_max_length,
        ).to(device)
        input_len = enc.input_ids.shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **enc,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated = outputs[0, input_len:]
        decoded = tokenizer.decode(generated, skip_special_tokens=True).strip()
        logging.info("\n[Prompt %d]\n%s\n\n[Response]\n%s\n", idx, prompt, decoded)


def main():
    prompts = [
        "What is LoRA fine-tuning?",
        "Define LoRA in simple terms.",
        ]
    model, tokenizer, device = load_adapter_model()
    generate_responses(model, tokenizer, device, prompts)


if __name__ == "__main__":
    main()
