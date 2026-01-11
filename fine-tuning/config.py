import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class FinetuneConfig:
    model_id: str = os.getenv("MODEL_ID", "Qwen/Qwen1.5-0.5B-Chat")  # smallest chat variant for lower memory
    dataset_name: str = os.getenv("DATASET_NAME", "yahma/alpaca-cleaned")
    max_length: int = _int_env("MAX_LENGTH", 512)
    micro_batch_size: int = _int_env("MICRO_BATCH_SIZE", 2)
    gradient_accumulation_steps: int = _int_env("GRADIENT_ACCUMULATION_STEPS", 4)
    learning_rate: float = _float_env("LEARNING_RATE", 2e-4)
    warmup_ratio: float = _float_env("WARMUP_RATIO", 0.03)
    weight_decay: float = _float_env("WEIGHT_DECAY", 0.0)
    num_train_epochs: int = _int_env("NUM_TRAIN_EPOCHS", 2)
    lora_r: int = _int_env("LORA_R", 8)
    lora_alpha: int = _int_env("LORA_ALPHA", 16)
    lora_dropout: float = _float_env("LORA_DROPOUT", 0.05)
    output_dir: str = os.getenv("OUTPUT_DIR", "./qwen05-finetuned-lora8")
    seed: int = _int_env("SEED", 42)
