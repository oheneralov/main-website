"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def temp_rag_directory(tmp_path):
    """Fixture providing a temporary directory for RAG tests."""
    return str(tmp_path)
