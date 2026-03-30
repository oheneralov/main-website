"""Utilities for comparing RAG outputs using embeddings and similarity metrics."""

import logging
from typing import Dict, List, Tuple

import numpy as np
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class SimilarityMetrics:
    """Calculate similarity metrics between texts and embeddings."""

    def __init__(self, embedding_model: str = "default"):
        """Initialize with embedding model."""
        if embedding_model == "default":
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        else:
            self.embedding_fn = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model
                )
            )

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        vec1 = np.array(vec1, dtype=np.float32)
        vec2 = np.array(vec2, dtype=np.float32)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Euclidean distance
        """
        vec1 = np.array(vec1, dtype=np.float32)
        vec2 = np.array(vec2, dtype=np.float32)
        return float(np.linalg.norm(vec1 - vec2))

    def get_text_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list
        """
        embeddings = self.embedding_fn([text])
        return embeddings[0] if embeddings else []

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts using embeddings.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Semantic similarity score between -1 and 1
        """
        emb1 = self.get_text_embedding(text1)
        emb2 = self.get_text_embedding(text2)

        if not emb1 or not emb2:
            return 0.0

        return self.cosine_similarity(emb1, emb2)


class OutputComparator:
    """Compare RAG outputs with ground truth using multiple metrics."""

    def __init__(self, embedding_model: str = "default"):
        """Initialize comparator with embedding model."""
        self.metrics = SimilarityMetrics(embedding_model)

    def compare_retrieval_outputs(
        self, retrieved_docs: List[str], ground_truth_docs: List[str]
    ) -> Dict[str, float]:
        """
        Compare retrieved documents with ground truth documents.

        Args:
            retrieved_docs: List of retrieved document texts
            ground_truth_docs: List of expected document texts

        Returns:
            Dictionary with comparison metrics
        """
        if not ground_truth_docs:
            return {
                "mean_semantic_similarity": 0.0,
                "max_semantic_similarity": 0.0,
                "coverage": 0.0,
            }

        # Calculate semantic similarity for each retrieved doc with best match
        similarities = []
        matched_count = 0

        for retrieved in retrieved_docs:
            max_similarity = 0.0
            for ground_truth in ground_truth_docs:
                similarity = self.metrics.semantic_similarity(
                    retrieved.lower(), ground_truth.lower()
                )
                max_similarity = max(max_similarity, similarity)

            similarities.append(max_similarity)
            if max_similarity > 0.7:  # Threshold for match
                matched_count += 1

        mean_similarity = (
            sum(similarities) / len(similarities) if similarities else 0.0
        )
        max_similarity = max(similarities) if similarities else 0.0
        coverage = matched_count / len(ground_truth_docs) if ground_truth_docs else 0.0

        return {
            "mean_semantic_similarity": float(mean_similarity),
            "max_semantic_similarity": float(max_similarity),
            "coverage": float(coverage),
            "matched_documents": matched_count,
            "total_ground_truth": len(ground_truth_docs),
        }

    def compare_generated_outputs(
        self, generated_text: str, expected_responses: List[str]
    ) -> Dict[str, float]:
        """
        Compare generated response with expected responses.

        Args:
            generated_text: Generated response from RAG
            expected_responses: List of acceptable expected responses

        Returns:
            Dictionary with comparison metrics
        """
        if not expected_responses:
            return {
                "max_semantic_similarity": 0.0,
                "mean_semantic_similarity": 0.0,
            }

        similarities = [
            self.metrics.semantic_similarity(
                generated_text.lower(), expected.lower()
            )
            for expected in expected_responses
        ]

        return {
            "max_semantic_similarity": float(max(similarities)) if similarities else 0.0,
            "mean_semantic_similarity": float(
                sum(similarities) / len(similarities) if similarities else 0.0
            ),
            "similarity_scores": similarities,
        }

    def compare_keyword_overlap(
        self, generated_text: str, expected_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Compare keyword overlap in generated text.

        Args:
            generated_text: Generated response from RAG
            expected_keywords: List of keywords that should appear

        Returns:
            Dictionary with keyword overlap metrics
        """
        generated_lower = generated_text.lower()
        found_keywords = [
            kw for kw in expected_keywords if kw.lower() in generated_lower
        ]

        coverage = (
            len(found_keywords) / len(expected_keywords)
            if expected_keywords
            else 0.0
        )

        return {
            "keyword_coverage": float(coverage),
            "found_keywords": found_keywords,
            "total_keywords": len(expected_keywords),
            "matched_count": len(found_keywords),
        }

    def comprehensive_comparison(
        self,
        retrieved_docs: List[str],
        generated_text: str,
        ground_truth: Dict[str, any],
    ) -> Dict[str, any]:
        """
        Perform comprehensive comparison of RAG output.

        Args:
            retrieved_docs: Retrieved documents from RAG
            generated_text: Generated response from RAG
            ground_truth: Ground truth data with keys:
                - expected_documents: List of expected document texts
                - expected_responses: List of expected response texts
                - expected_keywords: List of expected keywords

        Returns:
            Comprehensive comparison report
        """
        retrieval_metrics = self.compare_retrieval_outputs(
            retrieved_docs, ground_truth.get("expected_documents", [])
        )

        generation_metrics = self.compare_generated_outputs(
            generated_text, ground_truth.get("expected_responses", [])
        )

        keyword_metrics = self.compare_keyword_overlap(
            generated_text, ground_truth.get("expected_keywords", [])
        )

        # Calculate overall quality score
        weights = {
            "retrieval_similarity": 0.25,
            "generation_similarity": 0.50,
            "keyword_coverage": 0.25,
        }

        overall_score = (
            retrieval_metrics.get("mean_semantic_similarity", 0.0)
            * weights["retrieval_similarity"]
            + generation_metrics.get("max_semantic_similarity", 0.0)
            * weights["generation_similarity"]
            + keyword_metrics.get("keyword_coverage", 0.0)
            * weights["keyword_coverage"]
        )

        return {
            "retrieval_metrics": retrieval_metrics,
            "generation_metrics": generation_metrics,
            "keyword_metrics": keyword_metrics,
            "overall_quality_score": float(overall_score),
        }
