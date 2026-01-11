import logging
from typing import List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

MODEL_ID = "Qwen/Qwen1.5-0.5B-Chat"
MAX_NEW_TOKENS = 128


def load_model_and_tokenizer(model_id: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    # Ensure padding is defined for batching/generation
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    logging.info("Loading model %s on %s", model_id, device)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
    )
    if device != "cuda":
        model.to(device)

    return model, tokenizer, device


def generate_responses(model, tokenizer, device: str, prompts: List[str]):
    for idx, prompt in enumerate(prompts, start=1):
        messages = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info("\n[Prompt %d]\n%s\n\n[Response]\n%s\n", idx, prompt, decoded)


if __name__ == "__main__":
    prompts = [
        "Explain LoRA finetuning in simple terms.",
    ]

    model, tokenizer, device = load_model_and_tokenizer(MODEL_ID)
    generate_responses(model, tokenizer, device, prompts)
