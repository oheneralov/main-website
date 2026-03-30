"""End-to-end integration tests for RAG system."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from chroma_rag import ChromaRAG
from config import RAGConfig
from rag_pipeline import RAGPipeline

from .comparison import OutputComparator, SimilarityMetrics
from .ground_truth import (
    AWS_TEST_CASES,
    QUALITY_TEST_CASES,
    get_test_case,
    get_test_cases_by_category,
)


class TestRAGRetrievalQuality(unittest.TestCase):
    """End-to-end tests for RAG retrieval quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = RAGConfig(
            persist_directory=self.test_dir,
            chunk_size=500,
            chunk_overlap=50,
            retrieval_k=3,
        )
        self.rag_system = ChromaRAG(
            persist_directory=self.test_dir,
            collection_name="test_documents",
        )
        self.comparator = OutputComparator()

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _load_test_documents(self, test_case: dict) -> None:
        """Load test documents into RAG system."""
        documents = test_case.get("expected_documents", [])
        for i, doc in enumerate(documents):
            self.rag_system.add_documents(
                [doc],
                metadata=[{"source": f"test_{i}", "case_id": test_case["id"]}],
                ids=[f"{test_case['id']}_doc_{i}"],
            )
        self.rag_system.persist()

    def test_retrieval_aws_ec2_basics(self):
        """Test retrieval quality for AWS EC2 query."""
        test_case = get_test_case("aws_ec2_basics")
        self._load_test_documents(test_case)

        # Retrieve documents
        query = test_case["query"]
        results = self.rag_system.retrieve_with_scores(query, k=3)
        retrieved_docs = [r["document"] for r in results]

        # Compare with expected
        metrics = self.comparator.compare_retrieval_outputs(
            retrieved_docs, test_case["expected_documents"]
        )

        # Assert quality thresholds
        self.assertGreater(
            metrics["mean_semantic_similarity"],
            0.3,
            "Average semantic similarity too low",
        )
        self.assertGreater(
            metrics["max_semantic_similarity"],
            0.5,
            "Maximum semantic similarity too low",
        )

    def test_retrieval_aws_s3_storage(self):
        """Test retrieval quality for AWS S3 query."""
        test_case = get_test_case("aws_s3_storage")
        self._load_test_documents(test_case)

        query = test_case["query"]
        results = self.rag_system.retrieve_with_scores(query, k=3)
        retrieved_docs = [r["document"] for r in results]

        metrics = self.comparator.compare_retrieval_outputs(
            retrieved_docs, test_case["expected_documents"]
        )

        self.assertGreater(metrics["mean_semantic_similarity"], 0.3)
        self.assertGreater(metrics["coverage"], 0.0)

    def test_retrieval_quality_semantic_match(self):
        """Test retrieval quality with semantic similarity."""
        test_case = get_test_case("quality_semantic_match")
        self._load_test_documents(test_case)

        query = test_case["query"]
        results = self.rag_system.retrieve_with_scores(query, k=2)
        retrieved_docs = [r["document"] for r in results]

        metrics = self.comparator.compare_retrieval_outputs(
            retrieved_docs, test_case["expected_documents"]
        )

        # Semantic similarity should be reasonable
        self.assertGreater(
            metrics["max_semantic_similarity"],
            0.4,
            "Semantic similarity indicates poor retrieval quality",
        )

    def test_retrieval_with_empty_results(self):
        """Test retrieval handling when no documents match."""
        test_case = get_test_case("aws_ec2_basics")
        self._load_test_documents(test_case)

        # Query that won't match well
        query = "unrelated query about cooking recipes"
        results = self.rag_system.retrieve_with_scores(query, k=3)
        retrieved_docs = [r["document"] for r in results]

        metrics = self.comparator.compare_retrieval_outputs(
            retrieved_docs, ["some unrelated document"]
        )

        # Metrics should still be computed
        self.assertIn("mean_semantic_similarity", metrics)
        self.assertIn("max_semantic_similarity", metrics)

    def test_retrieval_similarity_metrics(self):
        """Test similarity metric calculation."""
        metrics_calc = SimilarityMetrics()

        text1 = "Machine learning is a type of artificial intelligence"
        text2 = "Machine learning uses algorithms to learn from data"

        similarity = metrics_calc.semantic_similarity(text1, text2)

        # Similar texts should have high similarity
        self.assertGreater(similarity, 0.3)
        self.assertLessEqual(similarity, 1.0)

    def test_embedding_vector_calculation(self):
        """Test embedding vector calculation."""
        metrics_calc = SimilarityMetrics()

        text = "AWS EC2 provides computing resources"
        embedding = metrics_calc.get_text_embedding(text)

        # Check embedding is valid
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)
        # Embeddings are floats
        for value in embedding:
            self.assertIsInstance(value, (int, float))

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation."""
        metrics_calc = SimilarityMetrics()

        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        similarity = metrics_calc.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0)

        vec3 = [0, 1, 0]
        similarity = metrics_calc.cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity, 0.0)

    def test_euclidean_distance_calculation(self):
        """Test Euclidean distance calculation."""
        metrics_calc = SimilarityMetrics()

        vec1 = [0, 0]
        vec2 = [3, 4]
        distance = metrics_calc.euclidean_distance(vec1, vec2)
        self.assertAlmostEqual(distance, 5.0)


class TestRAGGenerationQuality(unittest.TestCase):
    """End-to-end tests for RAG generation quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = RAGConfig(
            persist_directory=self.test_dir,
            retrieval_k=3,
        )
        self.comparator = OutputComparator()

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_keyword_coverage_exact(self):
        """Test keyword coverage in generated output."""
        test_case = get_test_case("quality_exact_match")
        generated = "Machine learning is an algorithm that learns from data"

        metrics = self.comparator.compare_keyword_overlap(
            generated, test_case["expected_keywords"]
        )

        # Should find most keywords
        self.assertGreater(
            metrics["keyword_coverage"],
            0.4,
            "Keyword coverage too low",
        )
        self.assertEqual(metrics["total_keywords"], len(test_case["expected_keywords"]))

    def test_keyword_coverage_semantic(self):
        """Test keyword coverage with semantic matching."""
        test_case = get_test_case("quality_semantic_match")
        generated = "Deep neural networks have multiple layers for processing"

        metrics = self.comparator.compare_keyword_overlap(
            generated, test_case["expected_keywords"]
        )

        self.assertGreater(metrics["keyword_coverage"], 0.0)
        self.assertLessEqual(metrics["keyword_coverage"], 1.0)

    def test_generated_output_similarity_to_expected(self):
        """Test similarity of generated output to expected responses."""
        test_case = get_test_case("aws_ec2_basics")
        generated = "An EC2 instance is a virtual compute resource in AWS cloud"

        metrics = self.comparator.compare_generated_outputs(
            generated, test_case["expected_responses"]
        )

        # Generated output should have reasonable similarity to expected
        self.assertGreater(
            metrics["max_semantic_similarity"],
            0.3,
            "Generated output not similar to expected",
        )


class TestComprehensiveRAGComparison(unittest.TestCase):
    """Comprehensive end-to-end tests comparison."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.comparator = OutputComparator()

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_comprehensive_comparison_aws_ec2(self):
        """Test comprehensive comparison for AWS EC2 case."""
        test_case = get_test_case("aws_ec2_basics")

        # Simulate RAG output
        retrieved_docs = test_case["expected_documents"][:2]
        generated_text = test_case["expected_responses"][0]

        report = self.comparator.comprehensive_comparison(
            retrieved_docs,
            generated_text,
            test_case,
        )

        # Check report structure
        self.assertIn("retrieval_metrics", report)
        self.assertIn("generation_metrics", report)
        self.assertIn("keyword_metrics", report)
        self.assertIn("overall_quality_score", report)

        # Quality score should be between 0 and 1
        self.assertGreaterEqual(report["overall_quality_score"], 0.0)
        self.assertLessEqual(report["overall_quality_score"], 1.0)

    def test_comprehensive_comparison_with_all_metrics(self):
        """Test comprehensive comparison includes all expected metrics."""
        test_case = get_test_case("quality_semantic_match")

        retrieved_docs = test_case["expected_documents"]
        generated_text = test_case["expected_responses"][0]

        report = self.comparator.comprehensive_comparison(
            retrieved_docs,
            generated_text,
            test_case,
        )

        # Check retrieval metrics
        self.assertIn("mean_semantic_similarity", report["retrieval_metrics"])
        self.assertIn("max_semantic_similarity", report["retrieval_metrics"])
        self.assertIn("coverage", report["retrieval_metrics"])

        # Check generation metrics
        self.assertIn("max_semantic_similarity", report["generation_metrics"])
        self.assertIn("mean_semantic_similarity", report["generation_metrics"])

        # Check keyword metrics
        self.assertIn("keyword_coverage", report["keyword_metrics"])
        self.assertIn("found_keywords", report["keyword_metrics"])
        self.assertIn("matched_count", report["keyword_metrics"])

    def test_quality_score_calculation(self):
        """Test overall quality score calculation."""
        test_case = get_test_case("aws_ec2_basics")

        # Perfect match
        retrieved_docs = test_case["expected_documents"]
        generated_text = test_case["expected_responses"][0]

        report = self.comparator.comprehensive_comparison(
            retrieved_docs,
            generated_text,
            test_case,
        )

        score = report["overall_quality_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_comparison_with_missing_ground_truth(self):
        """Test comparison when ground truth is incomplete."""
        test_case = {
            "id": "test_incomplete",
            "query": "test",
            # Missing some expected fields
        }

        retrieved_docs = ["document 1", "document 2"]
        generated_text = "Generated response"

        report = self.comparator.comprehensive_comparison(
            retrieved_docs,
            generated_text,
            test_case,
        )

        # Should still produce valid metrics
        self.assertIn("overall_quality_score", report)
        self.assertGreaterEqual(report["overall_quality_score"], 0.0)


class TestEmbeddingBasedComparison(unittest.TestCase):
    """Tests for embedding-based comparison methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = SimilarityMetrics()

    def test_embedding_consistency(self):
        """Test that same text produces same embedding."""
        text = "Test document about machine learning"

        emb1 = self.metrics.get_text_embedding(text)
        emb2 = self.metrics.get_text_embedding(text)

        # Embeddings should be consistent
        self.assertEqual(len(emb1), len(emb2))
        for v1, v2 in zip(emb1, emb2):
            self.assertAlmostEqual(v1, v2, places=5)

    def test_semantic_distance_meaningful(self):
        """Test that semantic distance is meaningful."""
        similar_texts = [
            ("machine learning", "machine learning algorithms"),
            ("artificial intelligence", "AI"),
            ("neural networks", "deep learning networks"),
        ]

        different_texts = [
            ("machine learning", "cooking recipes"),
            ("artificial intelligence", "gardening tips"),
            ("neural networks", "car mechanics"),
        ]

        # Similar texts should have higher similarity
        similar_scores = [
            self.metrics.semantic_similarity(t1, t2) for t1, t2 in similar_texts
        ]
        different_scores = [
            self.metrics.semantic_similarity(t1, t2) for t1, t2 in different_texts
        ]

        avg_similar = sum(similar_scores) / len(similar_scores)
        avg_different = sum(different_scores) / len(different_scores)

        self.assertGreater(avg_similar, avg_different)

    def test_embedding_dimension_consistency(self):
        """Test that embeddings have consistent dimensions."""
        texts = [
            "Short text",
            "This is a longer text with more words",
            "Another example of varying length text",
        ]

        embeddings = [self.metrics.get_text_embedding(text) for text in texts]

        # All embeddings should have same dimension
        dimensions = [len(emb) for emb in embeddings]
        self.assertEqual(len(set(dimensions)), 1)


if __name__ == "__main__":
    unittest.main()
