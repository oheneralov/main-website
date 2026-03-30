"""Quick reference for running RAG tests."""

# UNIT TESTS
# Run all unit tests
pytest tests/unit/ -v

# Run specific unit test file
pytest tests/unit/test_timing.py -v
pytest tests/unit/test_config.py -v
pytest tests/unit/test_chroma_rag.py -v
pytest tests/unit/test_rag_pipeline.py -v

# Run specific test class
pytest tests/unit/test_timing.py::TestTimeOperation -v

# Run specific test
pytest tests/unit/test_timing.py::TestTimeOperation::test_time_operation_success -v


# END-TO-END TESTS
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific E2E test class
pytest tests/e2e/test_rag_e2e.py::TestRAGRetrievalQuality -v
pytest tests/e2e/test_rag_e2e.py::TestRAGGenerationQuality -v
pytest tests/e2e/test_rag_e2e.py::TestComprehensiveRAGComparison -v
pytest tests/e2e/test_rag_e2e.py::TestEmbeddingBasedComparison -v

# Run specific E2E test
pytest tests/e2e/test_rag_e2e.py::TestRAGRetrievalQuality::test_retrieval_aws_ec2_basics -v

# Run example E2E usage
python tests/e2e/example_usage.py


# ALL TESTS
# Run unit and E2E tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=rag --cov-report=html
pytest tests/unit/ --cov=rag --cov-report=html
pytest tests/e2e/ --cov=rag --cov-report=html

# Run in parallel (faster)
pytest tests/ -n auto


# FILTERING & OPTIONS
# Run only failing tests from last run
pytest tests/ --lf -v

# Stop on first failure
pytest tests/ -x

# Stop after N failures
pytest tests/ --maxfail=3

# Capture output (show print statements)
pytest tests/ -s

# Run tests matching pattern
pytest tests/ -k "retrieval" -v
pytest tests/ -k "similarity" -v

# Run with different verbosity
pytest tests/ -q              # Quiet
pytest tests/ -v              # Verbose
pytest tests/ -vv            # Very verbose


# REPORTING
# HTML report
pytest tests/e2e/ --html=report.html --self-contained-html

# JUnit XML report (for CI/CD)
pytest tests/e2e/ --junitxml=test_results.xml

# Trace/Debug execution
pytest tests/ --tb=short      # Short traceback
pytest tests/ --tb=long       # Long traceback
pytest tests/ --tb=native     # Native Python traceback


# DEVELOPMENT
# Run tests in watch mode (requires pytest-watch)
ptw tests/

# Run with debugging
pytest tests/ --pdb           # Drop into debugger on failure
pytest tests/ --trace         # Drop into debugger at start

# Show slowest tests
pytest tests/ --durations=10


# GROUP TESTS BY CATEGORY
# Only retrieval tests
pytest tests/e2e/ -k "retrieval" -v

# Only generation tests
pytest tests/e2e/ -k "generation" -v

# Only quality metric tests
pytest tests/e2e/ -k "quality" -v

# Only keyword tests
pytest tests/e2e/ -k "keyword" -v


# INTEGRATION WITH CI/CD

# GitHub Actions style
pytest tests/ -v --tb=short --junit-xml=test-results.xml

# Jenkins style
pytest tests/ --cov=rag --cov-report=html --cov-report=xml

# Generate reports
pytest tests/e2e/ -v --html=e2e_report.html
pytest tests/unit/ -v --html=unit_report.html


# USEFUL ALIASES
# Add to .bashrc or .zshrc for convenience:
# alias test-unit="pytest tests/unit/ -v"
# alias test-e2e="pytest tests/e2e/ -v"
# alias test-all="pytest tests/ -v"
# alias test-cov="pytest tests/ --cov=rag --cov-report=html"


# EXPECTED RESULTS

# Unit Tests: ~60 tests, should all pass (no external dependencies)
# Retrieval Tests: ~8 tests, validates embedding-based similarity
# Generation Tests: ~3 tests, validates output quality
# Comprehensive Tests: ~4 tests, validates full pipeline
# Embedding Tests: ~3 tests, validates similarity calculations


# QUALITY SCORE INTERPRETATION
# 0.8-1.0: Excellent quality ✅
# 0.6-0.8: Good quality ✓
# 0.4-0.6: Acceptable quality ⚠️
# 0.2-0.4: Poor quality ❌
# <0.2: Critical issues ⚠️⚠️


# KEY METRICS EXPLAINED
# mean_semantic_similarity: Average similarity of all comparisons (0-1)
# max_semantic_similarity: Highest similarity found (0-1)
# coverage: Percentage of expected documents matched (0-1)
# keyword_coverage: Percentage of keywords found in output (0-1)
# overall_quality_score: Weighted combination of all metrics (0-1)
