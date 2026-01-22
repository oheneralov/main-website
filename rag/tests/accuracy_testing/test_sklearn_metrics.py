import pytest
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Example ground truth and predictions for RAG output
# Replace with your actual test data
true_answers = ["answer1", "answer2", "answer3", "answer4"]
predicted_answers = ["answer1", "wrong2", "answer3", "wrong4"]


def test_rag_accuracy():
    acc = accuracy_score(true_answers, predicted_answers)
    assert acc > 0.5, f"Accuracy too low: {acc}"


def test_rag_f1_score():
    # For string labels, average='micro' is typical
    f1 = f1_score(true_answers, predicted_answers, average='micro')
    assert f1 > 0.5, f"F1-score too low: {f1}"


def test_rag_precision():
    precision = precision_score(true_answers, predicted_answers, average='micro')
    assert precision > 0.5, f"Precision too low: {precision}"


def test_rag_recall():
    recall = recall_score(true_answers, predicted_answers, average='micro')
    assert recall > 0.5, f"Recall too low: {recall}"

# Replace true_answers and predicted_answers with your actual RAG output for real tests
