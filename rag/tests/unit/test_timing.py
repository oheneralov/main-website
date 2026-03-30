"""Unit tests for timing utilities."""

import logging
import time
import unittest
from unittest.mock import patch

from timing import log_system_memory, log_timing, time_operation


class TestTimeOperation(unittest.TestCase):
    """Test the time_operation context manager."""

    def test_time_operation_success(self):
        """Test that time_operation times a successful operation."""
        sleep_duration = 0.1

        with time_operation("test operation"):
            time.sleep(sleep_duration)

        # If we reach here, no exception was raised and context manager worked

    def test_time_operation_with_exception(self):
        """Test that time_operation raises exceptions from the block."""
        with self.assertRaises(ValueError):
            with time_operation("failing operation"):
                raise ValueError("Test error")

    def test_time_operation_logs_timing(self):
        """Test that time_operation logs the duration."""
        with patch("timing.logger") as mock_logger:
            with time_operation("test operation"):
                time.sleep(0.01)

            # Check that logger.info was called
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            self.assertIn("test operation", call_args)
            self.assertIn("s", call_args)  # Contains seconds unit


class TestLogTiming(unittest.TestCase):
    """Test the log_timing decorator."""

    def test_log_timing_decorator_returns_result(self):
        """Test that log_timing decorator returns the function result."""

        @log_timing("add numbers")
        def add(a, b):
            return a + b

        result = add(2, 3)
        self.assertEqual(result, 5)

    def test_log_timing_decorator_with_exception(self):
        """Test that log_timing decorator propagates exceptions."""

        @log_timing("failing function")
        def failing_function():
            raise RuntimeError("Test error")

        with self.assertRaises(RuntimeError):
            failing_function()

    def test_log_timing_decorator_logs(self):
        """Test that log_timing decorator logs the execution time."""
        with patch("timing.logger") as mock_logger:

            @log_timing("test function")
            def test_func():
                time.sleep(0.01)
                return "result"

            result = test_func()

            self.assertEqual(result, "result")
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            self.assertIn("test function", call_args)


class TestLogSystemMemory(unittest.TestCase):
    """Test the log_system_memory function."""

    def test_log_system_memory_runs_without_error(self):
        """Test that log_system_memory executes without raising exceptions."""
        try:
            log_system_memory()
        except Exception as e:
            self.fail(f"log_system_memory raised {type(e).__name__}: {e}")

    @patch("timing.logger")
    def test_log_system_memory_logs_output(self, mock_logger):
        """Test that log_system_memory logs various memory information."""
        log_system_memory()

        # Check that logger.info was called multiple times
        self.assertGreater(mock_logger.info.call_count, 5)

        # Check that various memory-related messages were logged
        logged_messages = [call[0][0] for call in mock_logger.info.call_args_list]
        logged_text = " ".join(logged_messages)

        self.assertIn("Memory Report", logged_text)
        self.assertIn("RAM", logged_text)
        self.assertIn("GB", logged_text)

    @patch("timing.logger")
    def test_log_system_memory_warning_on_low_memory(self, mock_logger):
        """Test that log_system_memory warns on low available memory."""
        with patch("psutil.virtual_memory") as mock_vm:
            # Create mock with very low available memory
            mock_vm.return_value = type(
                "obj",
                (),
                {
                    "total": 8 * (1024**3),  # 8 GB
                    "available": 2 * (1024**3),  # 2 GB - below 4 GB threshold
                    "used": 6 * (1024**3),
                    "percent": 75,
                },
            )()
            with patch("psutil.swap_memory") as mock_swap:
                mock_swap.return_value = type(
                    "obj",
                    (),
                    {"total": 0, "free": 0, "used": 0, "percent": 0},
                )()
                with patch("psutil.Process") as mock_process:
                    mock_process.return_value.memory_info.return_value = type(
                        "obj", (), {"rss": 500 * (1024**2)}
                    )()

                    log_system_memory()

                    # Check that warning was issued
                    mock_logger.warning.assert_called()


if __name__ == "__main__":
    unittest.main()
