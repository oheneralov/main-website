import json
import os
import pytest

HELM_RESULTS_PATH = os.getenv("HELM_RESULTS_PATH", "helm_results.json")


def load_helm_results(path):
    if not os.path.exists(path):
        pytest.skip(f"HELM results file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_helm_accuracy():
    """
    Test RAG accuracy using HELM results.
    Assumes HELM results are available as a JSON file.
    """
    results = load_helm_results(HELM_RESULTS_PATH)
    # Example: check that accuracy metric exists and meets threshold
    accuracy = results.get("metrics", {}).get("accuracy")
    assert accuracy is not None, "Accuracy metric missing in HELM results"
    assert accuracy > 0.7, f"Accuracy too low: {accuracy}"


def test_helm_f1_score():
    results = load_helm_results(HELM_RESULTS_PATH)
    f1 = results.get("metrics", {}).get("f1_score")
    assert f1 is not None, "F1-score missing in HELM results"
    assert f1 > 0.7, f"F1-score too low: {f1}"

# Add more tests for other HELM metrics as needed
