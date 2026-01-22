import pytest
from rag.config import ChunkSplitMethod, RAGConfig


def test_chunk_split_method_enum():
    # Ensure all expected chunking methods are present
    expected_methods = {
        "tokens", "sentences", "paragraphs", "markdown", "lines", "header", "fixed_size", "window", "custom"
    }
    actual_methods = set(item.value for item in ChunkSplitMethod)
    assert expected_methods == actual_methods


def test_rag_config_defaults():
    config = RAGConfig()
    assert config.persist_directory == "./chroma_data"
    assert config.collection_name == "documents"
    assert config.embedding_model == "all-MiniLM-L6-v2"
    assert config.chunk_size == 500
    assert config.chunk_overlap == 50
    assert config.retrieval_k == 5
    assert config.similarity_threshold == 0.0
    assert config.chunk_split_method == ChunkSplitMethod.MARKDOWN


def test_get_default_config():
    from rag.config import get_default_config
    config = get_default_config()
    assert isinstance(config, RAGConfig)
    assert config.chunk_split_method == ChunkSplitMethod.MARKDOWN
