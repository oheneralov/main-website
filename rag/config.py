"""
Configuration and utilities for the RAG system.
"""

from dataclasses import dataclass
from enum import Enum


class ChunkSplitMethod(str, Enum):
    """Supported strategies for chunking documents."""

    TOKENS = "tokens"  # Split by fixed number of tokens
    SENTENCES = "sentences"  # Split by sentence boundaries
    PARAGRAPHS = "paragraphs"  # Split by paragraph breaks
    MARKDOWN = "markdown"  # Split by markdown headers
    LINES = "lines"  # Split by line breaks
    HEADER = "header"  # Split by custom header patterns (e.g., ##, ###)
    FIXED_SIZE = "fixed_size"  # Split by fixed character or word count
    WINDOW = "window"  # Sliding window chunking
    CUSTOM = "custom"  # User-defined chunking logic


@dataclass
class RAGConfig:
    """Configuration for RAG system."""

    persist_directory: str = "./chroma_data"
    collection_name: str = "documents"
    embedding_model: str = "all-MiniLM-L6-v2"  # Lightweight and fast
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_k: int = 5
    similarity_threshold: float = 0.0
    chunk_split_method: ChunkSplitMethod = ChunkSplitMethod.MARKDOWN


def get_default_config() -> RAGConfig:
    """Get default RAG configuration."""
    return RAGConfig()
