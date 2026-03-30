# RAG System Tests

This directory contains the test suite for the RAG (Retrieval-Augmented Generation) system.

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_timing.py       # Tests for timing utilities
│   ├── test_config.py       # Tests for configuration module
│   └── test_chroma_rag.py   # Tests for ChromaRAG class
└── README.md                # This file
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run only unit tests
```bash
pytest tests/unit/
```

### Run specific test file
```bash
pytest tests/unit/test_timing.py
```

### Run specific test class
```bash
pytest tests/unit/test_timing.py::TestTimeOperation
```

### Run specific test method
```bash
pytest tests/unit/test_timing.py::TestTimeOperation::test_time_operation_success
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=rag --cov-report=html
```

## Test Coverage

### test_timing.py
- `TestTimeOperation`: Tests for the `time_operation` context manager
  - Timing measurement
  - Exception handling
  - Logging verification

- `TestLogTiming`: Tests for the `log_timing` decorator
  - Return value preservation
  - Exception propagation
  - Execution time logging

- `TestLogSystemMemory`: Tests for the `log_system_memory` function
  - Function execution without errors
  - Memory information logging
  - Low memory warnings

### test_config.py
- `TestRAGConfig`: Tests for RAGConfig dataclass
  - Default initialization
  - Custom configuration values
  - LLM settings
  - Embedding model configuration
  - HNSW space metrics
  - Environment variable reading
  - Device configuration

- `TestGetDefaultConfig`: Tests for the `get_default_config` function
  - Returns RAGConfig instance
  - Has expected attributes

### test_chroma_rag.py
- `TestChromaRAGInitialization`: Tests for ChromaRAG initialization
  - Default parameters
  - Custom parameters
  - Directory creation
  - Embedding model handling

- `TestChromaRAGDocumentManagement`: Tests for document operations
  - Adding documents
  - Document metadata handling
  - Custom ID assignment
  - ID generation
  - Document deletion
  - Collection clearing
  - Statistics retrieval

- `TestChromaRAGRetrieval`: Tests for retrieval operations
  - Document retrieval
  - Similarity score calculation
  - Empty result handling

- `TestChromaRAGFilePersistence`: Tests for file operations
  - Loading documents from files
  - File metadata handling
  - Nonexistent file error handling
  - Database persistence

## Test Dependencies

Tests use the following testing frameworks:
- `unittest`: Python's standard testing framework
- `pytest`: Advanced testing framework
- `unittest.mock`: For mocking external dependencies

## Setting Up the Test Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Ensure all packages are available:
```bash
pip install pytest pytest-cov
```

## Writing New Tests

When adding new tests:

1. Follow the naming convention: `test_<module>.py` for test files
2. Use descriptive test method names starting with `test_`
3. Group related tests in test classes
4. Use appropriate fixtures and mocks to isolate units
5. Add docstrings explaining what each test validates
6. Aim for high code coverage

Example:
```python
class TestNewFeature(unittest.TestCase):
    """Test the new feature."""
    
    def test_feature_works_correctly(self):
        """Test that the feature produces expected output."""
        # Arrange
        input_data = "test"
        
        # Act
        result = new_feature(input_data)
        
        # Assert
        self.assertEqual(result, "expected")
```

## Mocking Best Practices

- Mock external dependencies (database, APIs, file I/O)
- Use `unittest.mock.patch` for substituting objects
- Keep mocked behavior simple and focused
- Verify mock calls using `assert_called_with()` and `assert_called_once()`

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution for quick feedback
- No external service dependencies
- Comprehensive mocking of external calls
- Exit codes indicate success/failure

## Troubleshooting

### Tests fail with import errors
- Ensure all packages in `requirements.txt` are installed
- Check that the RAG module is in the Python path

### Mock-related failures
- Verify the patch decorator target matches the actual import path
- Check that mocked methods are called with expected arguments

### Flaky tests
- Avoid hardcoding sleep durations; use mocks instead
- Ensure tests don't depend on system state or environment
