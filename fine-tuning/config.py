import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class FinetuneConfig:
    model_id: str = "Qwen/Qwen1.5-0.5B-Chat"  # smallest chat variant for lower memory
    dataset_name: str = "yahma/alpaca-cleaned"
    max_length: int = 512
    micro_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    weight_decay: float = 0.0
    num_train_epochs: int = _int_env("NUM_TRAIN_EPOCHS", 2)
    lora_r: int = _int_env("LORA_R", 8)
    lora_alpha: int = _int_env("LORA_ALPHA", 16)
    lora_dropout: float = 0.05
    output_dir: str = "./qwen05-finetuned-lora8"
    seed: int = 42
