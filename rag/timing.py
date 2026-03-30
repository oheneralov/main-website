"""Performance timing utilities for RAG pipeline."""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Generator

logger = logging.getLogger(__name__)


@contextmanager
def time_operation(operation_name: str) -> Generator:
    """Context manager for timing an operation.

    Args:
        operation_name: Name of the operation being timed

    Yields:
        Timing context

    Example:
        with time_operation("retrieve documents"):
            results = rag.retrieve(query, k=5)
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed_seconds = time.perf_counter() - start_time
        logger.info(f"⏱️  {operation_name}: {elapsed_seconds:.2f}s")


def log_timing(operation_name: str):
    """Decorator for timing function execution.

    Args:
        operation_name: Name of the operation for logging

    Example:
        @log_timing("embedding generation")
        def embed_query(query):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_seconds = time.perf_counter() - start_time
            logger.info(f"⏱️  {operation_name}: {elapsed_seconds:.2f}s")
            return result

        return wrapper

    return decorator
