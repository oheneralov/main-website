"""Performance timing utilities for RAG pipeline."""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Generator

import psutil

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


def log_system_memory():
    """Log available system memory to verify LLM capacity."""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    used_gb = memory.used / (1024**3)
    percent = memory.percent

    swap_total_gb = swap.total / (1024**3)
    swap_available_gb = swap.free / (1024**3)
    swap_used_gb = swap.used / (1024**3)
    swap_percent = swap.percent

    logger.info("System Memory Report:")
    logger.info(f"   RAM Total: {total_gb:.2f} GB")
    logger.info(f"   RAM Available: {available_gb:.2f} GB")
    logger.info(f"   RAM Used: {used_gb:.2f} GB ({percent}%)")
    logger.info(f"   Swap Total: {swap_total_gb:.2f} GB")
    logger.info(f"   Swap Available: {swap_available_gb:.2f} GB")
    logger.info(f"   Swap Used: {swap_used_gb:.2f} GB ({swap_percent}%)")

    # Log current process memory
    current_process = psutil.Process()
    process_memory_mb = current_process.memory_info().rss / (1024**2)
    logger.info(f"   This process (uvicorn): {process_memory_mb:.2f} MB")

    if available_gb < 4.0:
        logger.warning(
            f"⚠️  WARNING: Only {available_gb:.2f} GB available - may be insufficient for LLM"
        )
    else:
        logger.info(f"✅ Sufficient memory available for LLM ({available_gb:.2f} GB)")

    # Memory usage breakdown
    logger.info("Memory Usage Breakdown:")
    logger.info("   LLM Model (QWEN 0.5B on CPU): ~1.5-2.5 GB typical")
    logger.info("   Embedding Model (MiniLM): ~0.5-1.0 GB")
    logger.info("   Chroma Vector DB: ~0.5-1.0 GB (depends on documents)")
    logger.info(f"   System & Other: ~{used_gb - process_memory_mb / 1024:.2f} GB")
