import logging
from typing import Dict, List

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoTokenizer

from config import FinetuneConfig


class FinetuneComponents:
    """Reusable helpers for tokenizer, data prep, and LoRA setup."""

    def __init__(self, cfg: FinetuneConfig):
        self.cfg = cfg

    def build_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.cfg.model_id, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        return tokenizer

    def format_example(self, example: Dict[str, str]) -> Dict[str, str]:
        instruction = example.get("instruction", "").strip()
        inp = example.get("input", "").strip()
        output = example.get("output", "").strip()
        prompt = (
            "Instruction: "
            f"{instruction}\n"
            "Input: "
            f"{inp}\n"
            "Response: "
        )
        text = prompt + output + "\n"
        return {"text": text}

    def tokenize(self, tokenizer):
        def _tok(batch: Dict[str, List[str]]):
            return tokenizer(
                batch["text"],
                max_length=self.cfg.max_length,
                truncation=True,
                padding="max_length",
            )

        return _tok

    def load_data(self, tokenizer):
        ds = load_dataset(self.cfg.dataset_name)
        train_ds = ds["train"].map(self.format_example)
        tokenized = train_ds.map(self.tokenize(tokenizer), batched=True)
        tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
        return tokenized

    def load_data_custom(self, tokenizer):
        data_dir = "./data/custom"
        ds = load_dataset("json", data_files={"train": f"{data_dir}/train.jsonl"})
        train_ds = ds["train"].map(self.format_example)
        tokenized = train_ds.map(self.tokenize(tokenizer), batched=True)
        tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
        return tokenized

    def attach_lora(self, model):
        target_modules = [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
        logging.info("Using LoRA r=%s", self.cfg.lora_r)
        lora_cfg = LoraConfig(
            r=self.cfg.lora_r,
            lora_alpha=self.cfg.lora_alpha,
            lora_dropout=self.cfg.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=target_modules,
        )
        return get_peft_model(model, lora_cfg)
