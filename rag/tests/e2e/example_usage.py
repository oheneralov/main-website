"""Example script demonstrating E2E testing utilities."""

import logging
from pathlib import Path

from chroma_rag import ChromaRAG
from config import RAGConfig
from rag_pipeline import RAGPipeline

from tests.e2e.comparison import OutputComparator, SimilarityMetrics
from tests.e2e.ground_truth import get_test_case, get_test_cases_by_category
from tests.e2e.reporting import E2ETestHelper, E2ETestReport, QualityThresholds

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_comparison():
    """Example: Basic output comparison."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Output Comparison")
    print("="*70)

    # Get test case
    test_case = get_test_case("aws_ec2_basics")

    # Initialize comparator
    comparator = OutputComparator()

    # Simulate RAG output
    retrieved_docs = test_case["expected_documents"][:2]
    generated_text = "An EC2 instance is a virtual compute resource in AWS"

    # Compare outputs
    report = comparator.comprehensive_comparison(
        retrieved_docs=retrieved_docs,
        generated_text=generated_text,
        ground_truth=test_case,
    )

    # Display results
    E2ETestHelper.print_comparison_report(report)


def example_embedding_similarity():
    """Example: Direct embedding similarity comparison."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Embedding Similarity")
    print("="*70)

    metrics = SimilarityMetrics()

    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "Machine learning algorithms learn from data"

    # Get embeddings
    emb1 = metrics.get_text_embedding(text1)
    emb2 = metrics.get_text_embedding(text2)

    print(f"\nText 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"\nEmbedding dimension: {len(emb1)}")

    # Calculate similarity
    similarity = metrics.semantic_similarity(text1, text2)
    print(f"Semantic similarity: {similarity:.3f}")

    # Calculate distance
    distance = metrics.euclidean_distance(emb1, emb2)
    print(f"Euclidean distance: {distance:.3f}")


def example_batch_evaluation():
    """Example: Batch evaluation with threshold checking."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Evaluation")
    print("="*70)

    # Get multiple test cases
    test_cases = get_test_cases_by_category("quality")

    # Define quality thresholds
    thresholds = QualityThresholds(
        retrieval_similarity_threshold=0.3,
        generation_similarity_threshold=0.4,
        keyword_coverage_threshold=0.2,
        overall_quality_threshold=0.4,
    )

    comparator = OutputComparator()
    results = []

    for test_case in test_cases:
        # Simulate RAG output
        retrieved_docs = test_case.get("expected_documents", [])
        generated_text = (
            test_case.get("expected_responses", ["No response available"])[0]
        )

        # Get comparison
        comparison = comparator.comprehensive_comparison(
            retrieved_docs=retrieved_docs,
            generated_text=generated_text,
            ground_truth=test_case,
        )
        results.append(comparison)

    # Evaluate batch
    evaluation = E2ETestHelper.batch_evaluate(test_cases, results, thresholds)

    print(f"\nTotal tests: {evaluation['summary']['total']}")
    print(f"Passed: {evaluation['summary']['passed']}")
    print(f"Failed: {evaluation['summary']['failed']}")
    print(f"Pass rate: {evaluation['summary']['passed'] / evaluation['summary']['total']:.1%}")

    # Show individual results
    print("\nDetailed Results:")
    for i, result in enumerate(evaluation["test_results"], 1):
        status = "✅" if result["passed"] else "❌"
        score = result["test_result"].get("overall_quality_score", 0)
        print(f"  {i}. Test {i}: {status} (Quality: {score:.3f})")


def example_test_reporting():
    """Example: Generate test report."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Test Reporting")
    print("="*70)

    # Create report
    report = E2ETestReport()

    # Simulate test results
    test_cases = get_test_cases_by_category("aws")
    comparator = OutputComparator()

    for test_case in test_cases:
        retrieved_docs = test_case.get("expected_documents", [])
        generated_text = (
            test_case.get("expected_responses", ["Response"])[0]
        )

        comparison = comparator.comprehensive_comparison(
            retrieved_docs=retrieved_docs,
            generated_text=generated_text,
            ground_truth=test_case,
        )

        # Add result to report
        passed = comparison.get("overall_quality_score", 0) > 0.5
        report.add_result(
            test_id=test_case["id"],
            test_name=test_case["query"],
            passed=passed,
            metrics=comparison,
        )

    # Print summary
    summary = report.get_summary()
    print("\nTest Summary:")
    print(f"  Total: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Pass Rate: {summary['pass_rate']:.1%}")
    print(f"  Avg Quality Score: {summary['average_quality_score']:.3f}")
    print(f"  Quality Range: {summary['min_quality_score']:.3f} - {summary['max_quality_score']:.3f}")

    # Save report
    report.save_markdown("/tmp/test_report.md")
    report.save_json("/tmp/test_report.json")
    print("\nReports saved to /tmp/")

    # Print markdown version
    print("\nMarkdown Report Preview:")
    print(report.to_markdown())


def example_retrieval_comparison():
    """Example: Compare retrieval outputs."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Retrieval Comparison")
    print("="*70)

    test_case = get_test_case("aws_s3_storage")
    comparator = OutputComparator()

    # Simulate retrieved documents
    retrieved_docs = [
        "Amazon S3 is object storage with high availability",
        "S3 provides durability through replication",
    ]

    # Compare with expected
    metrics = comparator.compare_retrieval_outputs(
        retrieved_docs=retrieved_docs,
        ground_truth_docs=test_case["expected_documents"],
    )

    print(f"\nQuery: {test_case['query']}")
    print(f"\nExpected documents: {len(test_case['expected_documents'])}")
    print(f"Retrieved documents: {len(retrieved_docs)}")
    print(f"\nMetrics:")
    print(f"  Mean semantic similarity: {metrics['mean_semantic_similarity']:.3f}")
    print(f"  Max semantic similarity: {metrics['max_semantic_similarity']:.3f}")
    print(f"  Coverage: {metrics['coverage']:.1%}")
    print(f"  Matched documents: {metrics['matched_documents']}/{metrics['total_ground_truth']}")


def example_keyword_comparison():
    """Example: Compare keyword coverage."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Keyword Coverage Comparison")
    print("="*70)

    test_case = get_test_case("quality_exact_match")
    comparator = OutputComparator()

    generated_text = (
        "Machine learning is an algorithm that learns patterns from data. "
        "These algorithms can improve performance through practice."
    )

    metrics = comparator.compare_keyword_overlap(
        generated_text=generated_text,
        expected_keywords=test_case["expected_keywords"],
    )

    print(f"\nGenerated text: {generated_text}")
    print(f"\nExpected keywords: {test_case['expected_keywords']}")
    print(f"\nMetrics:")
    print(f"  Keyword coverage: {metrics['keyword_coverage']:.1%}")
    print(f"  Found keywords: {metrics['found_keywords']}")
    print(f"  Matched: {metrics['matched_count']}/{metrics['total_keywords']}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("E2E TESTING EXAMPLES")
    print("="*70)

    # Run examples
    example_basic_comparison()
    example_embedding_similarity()
    example_batch_evaluation()
    example_retrieval_comparison()
    example_keyword_comparison()
    example_test_reporting()

    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)
