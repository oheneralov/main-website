"""Unit tests for configuration module."""

import os
import unittest
from unittest.mock import patch

from config import RAGConfig, get_default_config
from constants import ChunkSplitMethod, EmbeddingModel, HNSWSpace, LLMModel, LLMProvider


class TestRAGConfig(unittest.TestCase):
    """Test the RAGConfig dataclass."""

    def test_default_config_initialization(self):
        """Test that RAGConfig can be initialized with default values."""
        config = RAGConfig()
        self.assertIsNotNone(config)
        self.assertEqual(config.persist_directory, "./chroma_data")
        self.assertEqual(config.collection_name, "documents")

    def test_config_custom_values(self):
        """Test that RAGConfig accepts custom values."""
        config = RAGConfig(
            persist_directory="./custom_data",
            collection_name="custom_collection",
            chunk_size=1000,
            chunk_overlap=100,
            retrieval_k=5,
        )
        self.assertEqual(config.persist_directory, "./custom_data")
        self.assertEqual(config.collection_name, "custom_collection")
        self.assertEqual(config.chunk_size, 1000)
        self.assertEqual(config.chunk_overlap, 100)
        self.assertEqual(config.retrieval_k, 5)

    def test_config_llm_settings(self):
        """Test LLM-related configuration."""
        config = RAGConfig(
            llm_provider=LLMProvider.LOCAL_HUGGINGFACE,
            llm_model=LLMModel.QWEN_0_5B,
            llm_temperature=0.5,
            llm_max_tokens=256,
        )
        self.assertEqual(config.llm_provider, LLMProvider.LOCAL_HUGGINGFACE)
        self.assertEqual(config.llm_model, LLMModel.QWEN_0_5B)
        self.assertEqual(config.llm_temperature, 0.5)
        self.assertEqual(config.llm_max_tokens, 256)

    def test_config_embedding_model(self):
        """Test embedding model configuration."""
        config = RAGConfig(embedding_model=EmbeddingModel.MINI_LM)
        self.assertEqual(config.embedding_model, EmbeddingModel.MINI_LM)

    def test_config_hnsw_space(self):
        """Test HNSW space configuration."""
        config = RAGConfig(hnsw_space=HNSWSpace.COSINE)
        self.assertEqual(config.hnsw_space, HNSWSpace.COSINE)

    def test_config_chunk_split_method(self):
        """Test chunk split method configuration."""
        config = RAGConfig(chunk_split_method=ChunkSplitMethod.MARK_DOWN)
        self.assertEqual(config.chunk_split_method, ChunkSplitMethod.MARK_DOWN)

    def test_config_environment_variable_ollama_url(self):
        """Test reading OLLAMA_BASE_URL from environment."""
        test_url = "http://test.local:11434"
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": test_url}):
            config = RAGConfig()
            self.assertEqual(config.ollama_base_url, test_url)

    def test_config_environment_variable_model_device(self):
        """Test reading MODEL_DEVICE from environment."""
        with patch.dict(os.environ, {"MODEL_DEVICE": "cuda"}):
            config = RAGConfig()
            self.assertEqual(config.local_model_device, "cuda")

    def test_config_environment_variable_openai_key(self):
        """Test reading OPENAI_API_KEY from environment."""
        test_key = "sk-test123456789"
        with patch.dict(os.environ, {"OPENAI_API_KEY": test_key}):
            config = RAGConfig()
            self.assertEqual(config.openai_api_key, test_key)

    def test_config_default_device_is_cpu(self):
        """Test that default device is CPU."""
        with patch.dict(os.environ, {}, clear=True):
            config = RAGConfig()
            self.assertEqual(config.local_model_device, "cpu")

    def test_config_similarity_threshold(self):
        """Test similarity threshold configuration."""
        config = RAGConfig(similarity_threshold=0.5)
        self.assertEqual(config.similarity_threshold, 0.5)


class TestGetDefaultConfig(unittest.TestCase):
    """Test the get_default_config function."""

    def test_get_default_config_returns_rag_config(self):
        """Test that get_default_config returns a RAGConfig instance."""
        config = get_default_config()
        self.assertIsInstance(config, RAGConfig)

    def test_get_default_config_is_not_none(self):
        """Test that get_default_config returns a non-None object."""
        config = get_default_config()
        self.assertIsNotNone(config)

    def test_get_default_config_has_expected_attributes(self):
        """Test that returned config has expected attributes."""
        config = get_default_config()
        self.assertTrue(hasattr(config, "persist_directory"))
        self.assertTrue(hasattr(config, "collection_name"))
        self.assertTrue(hasattr(config, "chunk_size"))
        self.assertTrue(hasattr(config, "chunk_overlap"))
        self.assertTrue(hasattr(config, "llm_provider"))
        self.assertTrue(hasattr(config, "llm_model"))


if __name__ == "__main__":
    unittest.main()
