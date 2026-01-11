import logging

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from config import FinetuneConfig
from pipeline import FinetuneComponents
from transformers import (
	AutoModelForCausalLM,
	DataCollatorForLanguageModeling,
	Trainer,
	TrainingArguments,
)


logging.basicConfig(level=logging.INFO)


def train(cfg: FinetuneConfig):
	device = torch.device("cpu")
	device_is_cuda = False
	components = FinetuneComponents(cfg)
	tokenizer = components.build_tokenizer()
	model = AutoModelForCausalLM.from_pretrained(
		cfg.model_id,
		torch_dtype=torch.float32,
		low_cpu_mem_usage=False,
		trust_remote_code=True,
	)

	model = components.attach_lora(model)
	model.config.use_cache = False
	model.to(device)

	trainable = sum(p.requires_grad for p in model.parameters())
	if trainable == 0:
		raise RuntimeError("No trainable parameters found; LoRA target_modules may not match this model.")

	dataset = components.load_data_custom(tokenizer)
	collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

	args = TrainingArguments(
		output_dir=cfg.output_dir,
		per_device_train_batch_size=cfg.micro_batch_size,
		gradient_accumulation_steps=cfg.gradient_accumulation_steps,
		learning_rate=cfg.learning_rate,
		warmup_ratio=cfg.warmup_ratio,
		weight_decay=cfg.weight_decay,
		num_train_epochs=cfg.num_train_epochs,
		max_steps=4,
		lr_scheduler_type="cosine",
		logging_steps=10,
		save_strategy="epoch",
		fp16=False,
		bf16=False,
		dataloader_pin_memory=False,
		optim="adamw_torch",
		gradient_checkpointing=False,
		label_names=["labels"],
		report_to=[],
		seed=cfg.seed,
	)
	# Dataset is tokenized to feed integer IDs (input_ids/attention_mask) directly,
	# keeping training deterministic and avoiding per-step tokenization overhead.
	trainer = Trainer(
		model=model,
		args=args,
		train_dataset=dataset,
		data_collator=collator,
		tokenizer=tokenizer,
	)

	logging.info("Starting training")
	trainer.train()
	logging.info("Saving final adapter")
	trainer.model.save_pretrained(cfg.output_dir)
	tokenizer.save_pretrained(cfg.output_dir)


if __name__ == "__main__":
	cfg = FinetuneConfig()
	train(cfg)
