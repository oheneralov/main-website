"""
Configuration and utilities for the RAG system.
"""

from dataclasses import dataclass
from typing import Optional


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


def get_default_config() -> RAGConfig:
    """Get default RAG configuration."""
    return RAGConfig()
