"""Utility functions for E2E testing and reporting."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from .comparison import OutputComparator

logger = logging.getLogger(__name__)


class E2ETestReport:
    """Generate reports for E2E test results."""

    def __init__(self):
        """Initialize test report generator."""
        self.results = []
        self.start_time = datetime.now()

    def add_result(
        self,
        test_id: str,
        test_name: str,
        passed: bool,
        metrics: Dict[str, Any],
        error_message: str = None,
    ) -> None:
        """Add a test result to the report."""
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "passed": passed,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
        if error_message:
            result["error"] = error_message

        self.results.append(result)
        logger.info(
            f"Test {test_id}: {'PASSED' if passed else 'FAILED'} - "
            f"Quality Score: {metrics.get('overall_quality_score', 'N/A')}"
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all test results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests

        quality_scores = [
            r["metrics"].get("overall_quality_score", 0) for r in self.results
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "average_quality_score": avg_quality,
            "min_quality_score": min(quality_scores) if quality_scores else 0,
            "max_quality_score": max(quality_scores) if quality_scores else 0,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
        }

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(
            {
                "results": self.results,
                "summary": self.get_summary(),
            },
            indent=2,
        )

    def to_markdown(self) -> str:
        """Generate markdown report."""
        summary = self.get_summary()

        report = "# E2E Test Report\n\n"
        report += "## Summary\n\n"
        report += f"- **Total Tests**: {summary['total_tests']}\n"
        report += f"- **Passed**: {summary['passed']}\n"
        report += f"- **Failed**: {summary['failed']}\n"
        report += f"- **Pass Rate**: {summary['pass_rate']:.1%}\n"
        report += f"- **Average Quality Score**: {summary['average_quality_score']:.3f}\n"
        report += f"- **Duration**: {summary['duration_seconds']:.2f}s\n\n"

        report += "## Detailed Results\n\n"
        report += "| Test ID | Test Name | Status | Quality Score |\n"
        report += "|---------|-----------|--------|---------------|\n"

        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            quality = result["metrics"].get("overall_quality_score", "N/A")
            report += (
                f"| {result['test_id']} | {result['test_name']} | "
                f"{status} | {quality:.3f} |\n"
            )

        return report

    def save_json(self, filepath: str) -> None:
        """Save report as JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())
        logger.info(f"Test report saved to {filepath}")

    def save_markdown(self, filepath: str) -> None:
        """Save report as Markdown file."""
        with open(filepath, "w") as f:
            f.write(self.to_markdown())
        logger.info(f"Test report saved to {filepath}")


class QualityThresholds:
    """Define quality thresholds for test assertions."""

    def __init__(
        self,
        retrieval_similarity_threshold: float = 0.4,
        generation_similarity_threshold: float = 0.5,
        keyword_coverage_threshold: float = 0.3,
        overall_quality_threshold: float = 0.5,
    ):
        """Initialize quality thresholds."""
        self.retrieval_similarity_threshold = retrieval_similarity_threshold
        self.generation_similarity_threshold = generation_similarity_threshold
        self.keyword_coverage_threshold = keyword_coverage_threshold
        self.overall_quality_threshold = overall_quality_threshold

    def validate_retrieval_quality(self, metrics: Dict[str, float]) -> bool:
        """Check if retrieval metrics meet thresholds."""
        return (
            metrics.get("max_semantic_similarity", 0)
            >= self.retrieval_similarity_threshold
        )

    def validate_generation_quality(self, metrics: Dict[str, float]) -> bool:
        """Check if generation metrics meet thresholds."""
        return (
            metrics.get("max_semantic_similarity", 0)
            >= self.generation_similarity_threshold
        )

    def validate_keyword_coverage(self, metrics: Dict[str, float]) -> bool:
        """Check if keyword coverage meets threshold."""
        return (
            metrics.get("keyword_coverage", 0) >= self.keyword_coverage_threshold
        )

    def validate_overall_quality(self, overall_score: float) -> bool:
        """Check if overall quality meets threshold."""
        return overall_score >= self.overall_quality_threshold


class E2ETestHelper:
    """Helper functions for E2E testing."""

    @staticmethod
    def create_mock_test_run(
        test_case: Dict[str, Any],
        retrieved_docs: List[str],
        generated_text: str,
    ) -> Dict[str, Any]:
        """Create a mock RAG test run result."""
        comparator = OutputComparator()

        return comparator.comprehensive_comparison(
            retrieved_docs=retrieved_docs,
            generated_text=generated_text,
            ground_truth=test_case,
        )

    @staticmethod
    def batch_evaluate(
        test_cases: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
        thresholds: QualityThresholds = None,
    ) -> Dict[str, Any]:
        """Evaluate batch of test results."""
        if thresholds is None:
            thresholds = QualityThresholds()

        evaluation = {
            "test_results": [],
            "summary": {
                "total": len(results),
                "passed": 0,
                "failed": 0,
            },
        }

        for result in results:
            passed = thresholds.validate_overall_quality(
                result.get("overall_quality_score", 0)
            )

            eval_result = {
                "test_result": result,
                "passed": passed,
                "passed_retrieval": thresholds.validate_retrieval_quality(
                    result.get("retrieval_metrics", {})
                ),
                "passed_generation": thresholds.validate_generation_quality(
                    result.get("generation_metrics", {})
                ),
                "passed_keywords": thresholds.validate_keyword_coverage(
                    result.get("keyword_metrics", {})
                ),
            }

            evaluation["test_results"].append(eval_result)

            if passed:
                evaluation["summary"]["passed"] += 1
            else:
                evaluation["summary"]["failed"] += 1

        return evaluation

    @staticmethod
    def print_comparison_report(comparison_result: Dict[str, Any]) -> None:
        """Pretty print comparison result."""
        print("\n" + "=" * 60)
        print("RAG OUTPUT COMPARISON REPORT")
        print("=" * 60)

        print("\n[RETRIEVAL METRICS]")
        for key, value in comparison_result.get("retrieval_metrics", {}).items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

        print("\n[GENERATION METRICS]")
        for key, value in comparison_result.get("generation_metrics", {}).items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            elif not isinstance(value, list):
                print(f"  {key}: {value}")

        print("\n[KEYWORD METRICS]")
        for key, value in comparison_result.get("keyword_metrics", {}).items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            elif key != "found_keywords":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {', '.join(value) if value else 'None'}")

        overall_score = comparison_result.get("overall_quality_score", 0)
        quality_label = "EXCELLENT" if overall_score > 0.8 else \
                       "GOOD" if overall_score > 0.6 else \
                       "ACCEPTABLE" if overall_score > 0.4 else \
                       "POOR"

        print("\n[OVERALL QUALITY]")
        print(f"  Score: {overall_score:.3f} ({quality_label})")
        print("=" * 60 + "\n")
