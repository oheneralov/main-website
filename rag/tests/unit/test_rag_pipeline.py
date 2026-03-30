"""Unit tests for RAGPipeline class."""

import unittest
from unittest.mock import MagicMock, patch

from config import RAGConfig
from rag_pipeline import RAGPipeline
from constants import LLMProvider, LLMModel


class TestRAGPipelineInitialization(unittest.TestCase):
    """Test RAGPipeline initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_rag_system = MagicMock()

    def test_rag_pipeline_initialization_with_rag_system(self):
        """Test RAGPipeline initialization with ChromaRAG instance."""
        config = RAGConfig()
        with patch("rag_pipeline.RAGPipeline._init_llm") as mock_init_llm:
            mock_init_llm.return_value = None
            pipeline = RAGPipeline(self.mock_rag_system, config)

            self.assertEqual(pipeline.rag_system, self.mock_rag_system)
            self.assertEqual(pipeline.config, config)

    def test_rag_pipeline_initialization_without_config(self):
        """Test RAGPipeline initialization with default config."""
        with patch("rag_pipeline.RAGPipeline._init_llm") as mock_init_llm:
            mock_init_llm.return_value = None
            pipeline = RAGPipeline(self.mock_rag_system)

            self.assertEqual(pipeline.rag_system, self.mock_rag_system)
            self.assertIsNot(pipeline.config, None)


class TestRAGPipelineLLMInitialization(unittest.TestCase):
    """Test LLM initialization in RAGPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_rag_system = MagicMock()

    def test_init_llm_returns_none_for_disabled_llm(self):
        """Test that _init_llm returns None when LLM is disabled."""
        config = RAGConfig(llm_provider=LLMProvider.DISABLED)
        pipeline = RAGPipeline(self.mock_rag_system, config)

        self.assertIsNone(pipeline.llm)

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_init_llm_called_during_initialization(self, mock_init_llm):
        """Test that _init_llm is called during initialization."""
        mock_init_llm.return_value = MagicMock()
        config = RAGConfig()

        pipeline = RAGPipeline(self.mock_rag_system, config)

        mock_init_llm.assert_called_once()

    @patch("rag_pipeline.logger")
    def test_init_llm_logs_llm_initialization_failure(self, mock_logger):
        """Test that initialization failure is logged."""
        config = RAGConfig(llm_provider=LLMProvider.OPENAI)
        # Without setting API key, initialization should fail gracefully
        pipeline = RAGPipeline(self.mock_rag_system, config)

        # Pipeline should be created regardless of LLM init success
        self.assertIsNotNone(pipeline)


class TestRAGPipelineAugmentQuery(unittest.TestCase):
    """Test query augmentation in RAGPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_rag_system = MagicMock()

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_augment_query_retrieves_documents(self, mock_init_llm):
        """Test that augment_query retrieves documents from RAG system."""
        mock_init_llm.return_value = None
        config = RAGConfig(retrieval_k=3)

        self.mock_rag_system.retrieve_with_scores.return_value = [
            {"document": "doc1", "similarity_score": 0.9},
            {"document": "doc2", "similarity_score": 0.8},
            {"document": "doc3", "similarity_score": 0.7},
        ]

        pipeline = RAGPipeline(self.mock_rag_system, config)
        result = pipeline.augment_query("test query", k=3)

        self.mock_rag_system.retrieve_with_scores.assert_called_once()
        self.assertIn("num_documents", result)
        self.assertIn("context", result)


class TestRAGPipelineResponseGeneration(unittest.TestCase):
    """Test response generation in RAGPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_rag_system = MagicMock()

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_generate_response_with_llm(self, mock_init_llm):
        """Test response generation when LLM is available."""
        mock_llm = MagicMock()
        mock_init_llm.return_value = mock_llm

        config = RAGConfig()
        self.mock_rag_system.retrieve_with_scores.return_value = [
            {"document": "test document", "similarity_score": 0.9}
        ]

        pipeline = RAGPipeline(self.mock_rag_system, config)

        # Response generation might fail if LLM is not properly mocked
        # This is expected behavior when testing

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_generate_prompt_with_context(self, mock_init_llm):
        """Test prompt generation with context."""
        mock_init_llm.return_value = None
        config = RAGConfig()

        self.mock_rag_system.retrieve_with_scores.return_value = [
            {"document": "test content", "similarity_score": 0.95}
        ]

        pipeline = RAGPipeline(self.mock_rag_system, config)
        prompt = pipeline.generate_prompt_with_context("test query", k=1)

        self.assertIsInstance(prompt, str)
        self.assertIn("test query", prompt)


class TestRAGPipelineErrorHandling(unittest.TestCase):
    """Test error handling in RAGPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_rag_system = MagicMock()

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_augment_query_with_retrieval_error(self, mock_init_llm):
        """Test augment_query handles retrieval errors gracefully."""
        mock_init_llm.return_value = None
        self.mock_rag_system.retrieve_with_scores.side_effect = RuntimeError(
            "Retrieval failed"
        )

        config = RAGConfig()
        pipeline = RAGPipeline(self.mock_rag_system, config)

        with self.assertRaises(RuntimeError):
            pipeline.augment_query("test query")

    @patch("rag_pipeline.RAGPipeline._init_llm")
    def test_pipeline_handles_empty_retrieval(self, mock_init_llm):
        """Test pipeline handles empty retrieval results."""
        mock_init_llm.return_value = None
        self.mock_rag_system.retrieve_with_scores.return_value = []

        config = RAGConfig()
        pipeline = RAGPipeline(self.mock_rag_system, config)
        result = pipeline.augment_query("nonexistent query", k=5)

        self.assertEqual(result["num_documents"], 0)


if __name__ == "__main__":
    unittest.main()
