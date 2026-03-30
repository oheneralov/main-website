"""Configuration and utilities for the RAG system."""

import os
from dataclasses import dataclass, field

from constants import ChunkSplitMethod, EmbeddingModel, HNSWSpace, LLMModel, LLMProvider


@dataclass
class RAGConfig:
    """Configuration for RAG system."""

    persist_directory: str = "./chroma_data"
    collection_name: str = "documents"
    embedding_model: EmbeddingModel = field(
        default_factory=lambda: EmbeddingModel.MINI_LM
    )  # Lightweight and fast
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_k: int = 3
    similarity_threshold: float = 0.0
    chunk_split_method: ChunkSplitMethod = field(
        default_factory=lambda: ChunkSplitMethod.PARAGRAPHS
    )
    hnsw_space: HNSWSpace = field(default_factory=lambda: HNSWSpace.L2)

    # LLM Configuration
    llm_provider: LLMProvider = field(
        default_factory=lambda: LLMProvider.LOCAL_HUGGINGFACE
    )
    llm_model: LLMModel = field(default_factory=lambda: LLMModel.QWEN_1_8B)
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500

    # Provider-specific settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    local_model_device: str = os.getenv(
        "MODEL_DEVICE", "cpu"
    )  # "cpu" or "cuda" for GPU


def get_default_config() -> RAGConfig:
    """Get default RAG configuration."""
    return RAGConfig()
