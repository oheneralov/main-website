# End-to-End Tests for RAG System

This directory contains comprehensive end-to-end tests that validate the RAG system against ground truth using embedding-based similarity metrics.

## Test Structure

```
tests/e2e/
├── __init__.py                 # E2E test package marker
├── comparison.py               # Embedding-based comparison utilities
├── ground_truth.py             # Test cases and ground truth data
├── test_rag_e2e.py            # E2E integration tests
└── README.md                   # This file
```

## Key Features

### 1. Embedding-Based Comparison

The test suite uses semantic embeddings to compare RAG outputs with ground truth data, rather than simple string matching. This provides:

- **Semantic Similarity**: Measures meaning similarity using cosine similarity on embeddings
- **Cosine Distance**: Calculates directional similarity between text vectors
- **Euclidean Distance**: Calculates geometric distance between embeddings
- **Robust Matching**: Handles paraphrases and variations in wording

### 2. Comprehensive Ground Truth Data

Test cases include:

- **AWS-specific queries**: EC2, S3, Lambda, and other AWS services
- **Quality test cases**: Generic machine learning and neural network queries
- **Expected documents**: Reference documents for retrieval comparison
- **Expected responses**: Expected response patterns for generation
- **Expected keywords**: Key terms that should appear in outputs

### 3. Multi-Level Comparison Metrics

#### Retrieval Quality Metrics
- `mean_semantic_similarity`: Average similarity of retrieved documents to expected
- `max_semantic_similarity`: Highest similarity score found
- `coverage`: Percentage of expected documents matched
- `matched_documents`: Count of documents with high similarity

#### Generation Quality Metrics
- `max_semantic_similarity`: Best match against expected responses
- `mean_semantic_similarity`: Average similarity to expected responses
- `similarity_scores`: Individual scores for each expected response

#### Keyword Metrics
- `keyword_coverage`: Percentage of expected keywords present
- `found_keywords`: List of keywords actually found
- `matched_count`: Number of matched keywords

#### Overall Quality Score
Weighted combination of all metrics:
- Retrieval similarity: 25%
- Generation similarity: 50%
- Keyword coverage: 25%

## Running Tests

### Run all E2E tests
```bash
pytest tests/e2e/
```

### Run specific test class
```bash
pytest tests/e2e/test_rag_e2e.py::TestRAGRetrievalQuality -v
```

### Run specific test
```bash
pytest tests/e2e/test_rag_e2e.py::TestRAGRetrievalQuality::test_retrieval_aws_ec2_basics -v
```

### Run with detailed output
```bash
pytest tests/e2e/ -v -s
```

### Run with coverage
```bash
pytest tests/e2e/ --cov=rag --cov-report=html
```

### Generate test report
```bash
pytest tests/e2e/ -v --html=report.html --self-contained-html
```

## Test Classes

### TestRAGRetrievalQuality
Tests document retrieval quality using embedding similarity:

- `test_retrieval_aws_ec2_basics`: Validates retrieval for EC2 queries
- `test_retrieval_aws_s3_storage`: Tests S3-related retrieval
- `test_retrieval_quality_semantic_match`: Validates semantic matching
- `test_retrieval_with_empty_results`: Tests handling of no matches
- `test_retrieval_similarity_metrics`: Validates metric calculations
- `test_embedding_vector_calculation`: Tests embedding generation
- `test_cosine_similarity_calculation`: Validates cosine similarity math
- `test_euclidean_distance_calculation`: Validates distance calculation

### TestRAGGenerationQuality
Tests RAG generation output quality:

- `test_keyword_coverage_exact`: Keywords in generated output
- `test_keyword_coverage_semantic`: Semantic keyword matching
- `test_generated_output_similarity_to_expected`: Generation quality

### TestComprehensiveRAGComparison
Comprehensive end-to-end comparison tests:

- `test_comprehensive_comparison_aws_ec2`: Full pipeline test for EC2
- `test_comprehensive_comparison_with_all_metrics`: All metric types
- `test_quality_score_calculation`: Overall quality scoring
- `test_comparison_with_missing_ground_truth`: Robustness testing

### TestEmbeddingBasedComparison
Low-level embedding comparison tests:

- `test_embedding_consistency`: Same text = same embedding
- `test_semantic_distance_meaningful`: Similar texts score higher
- `test_embedding_dimension_consistency`: Consistent embedding dimensions

## Comparison Utilities

### SimilarityMetrics Class

```python
from tests.e2e.comparison import SimilarityMetrics

metrics = SimilarityMetrics()

# Get text embedding
embedding = metrics.get_text_embedding("your text here")

# Calculate semantic similarity
score = metrics.semantic_similarity("text 1", "text 2")

# Calculate cosine similarity between vectors
cos_sim = metrics.cosine_similarity(vec1, vec2)

# Calculate Euclidean distance
distance = metrics.euclidean_distance(vec1, vec2)
```

### OutputComparator Class

```python
from tests.e2e.comparison import OutputComparator

comparator = OutputComparator()

# Compare retrieval outputs
retrieval_metrics = comparator.compare_retrieval_outputs(
    retrieved_docs=["doc1", "doc2"],
    ground_truth_docs=["expected1", "expected2"]
)

# Compare generated responses
generation_metrics = comparator.compare_generated_outputs(
    generated_text="generated response",
    expected_responses=["expected response 1", "expected response 2"]
)

# Compare keyword coverage
keyword_metrics = comparator.compare_keyword_overlap(
    generated_text="generated response",
    expected_keywords=["keyword1", "keyword2"]
)

# Comprehensive comparison
report = comparator.comprehensive_comparison(
    retrieved_docs=["doc1", "doc2"],
    generated_text="generated response",
    ground_truth={
        "expected_documents": ["expected1", "expected2"],
        "expected_responses": ["response1", "response2"],
        "expected_keywords": ["keyword1", "keyword2"]
    }
)
```

## Ground Truth Management

### Adding New Test Cases

Edit `ground_truth.py`:

```python
TEST_CASES = [
    {
        "id": "my_test_case",
        "query": "What is your question?",
        "expected_documents": [
            "Document 1 content",
            "Document 2 content",
        ],
        "expected_responses": [
            "Expected response 1",
            "Expected response 2",
        ],
        "expected_keywords": ["keyword1", "keyword2", "keyword3"],
    }
]
```

### Accessing Test Cases

```python
from tests.e2e.ground_truth import (
    get_test_case,
    get_test_cases_by_category,
)

# Get single test case
test_case = get_test_case("aws_ec2_basics")

# Get all test cases in category
aws_cases = get_test_cases_by_category("aws")
quality_cases = get_test_cases_by_category("quality")
```

## Quality Score Thresholds

Recommended quality score ranges:

| Score Range | Interpretation |
|-------------|-----------------|
| 0.8 - 1.0  | Excellent quality |
| 0.6 - 0.8  | Good quality |
| 0.4 - 0.6  | Acceptable quality |
| 0.2 - 0.4  | Poor quality, needs improvement |
| < 0.2      | Very poor quality, critical issues |

## Embedding Models

The test suite uses embedding models for semantic comparison:

- **Default**: Uses ChromaDB's default embedding function (recommended for general use)
- **SentenceTransformer**: Supports various pre-trained models:
  - `all-MiniLM-L6-v2`: Fast, good general purpose
  - `all-mpnet-base-v2`: More powerful, slower
  - `paraphrase-MiniLM-L6-v2`: Good for paraphrase detection

To use a specific embedding model:

```python
from tests.e2e.comparison import SimilarityMetrics, OutputComparator

metrics = SimilarityMetrics(embedding_model="all-MiniLM-L6-v2")
comparator = OutputComparator(embedding_model="all-MiniLM-L6-v2")
```

## Best Practices for E2E Tests

1. **Isolated Test Cases**: Each test case should be independent
2. **Clear Ground Truth**: Explicitly define expected outputs
3. **Meaningful Metrics**: Use domain-appropriate similarity metrics
4. **Realistic Data**: Ground truth should reflect real-world usage
5. **Threshold Tuning**: Adjust similarity thresholds based on requirements
6. **Performance Tracking**: Monitor test execution time
7. **Regular Updates**: Keep ground truth current as system evolves

## Performance Considerations

E2E tests are more computationally expensive than unit tests due to:

- Embedding generation for semantic comparison
- ChromaDB operations
- RAG pipeline execution

Tips for faster tests:

- Run E2E tests separately from unit tests
- Use smaller document collections for tests
- Cache embeddings when possible
- Run tests in parallel with pytest-xdist

```bash
# Run in parallel
pytest tests/e2e/ -n auto
```

## Troubleshooting

### Flaky Tests
- Ensure ground truth is specific and realistic
- Check embedding model consistency
- Verify similarity thresholds are appropriate

### Low Quality Scores
- Review ground truth expectations
- Check if expected documents are properly loaded
- Verify embedding model choice
- Examine similarity metric calculations

### Performance Issues
- Profile embedding generation
- Check ChromaDB performance
- Consider using faster embedding models
- Reduce test data size if appropriate

## Continuous Integration

These tests are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run E2E tests
  run: |
    pytest tests/e2e/ -v --tb=short
```

## Contributing New Tests

When adding new E2E tests:

1. Create clear, realistic test cases
2. Define comprehensive ground truth
3. Document expected behavior
4. Include multiple metric validations
5. Handle edge cases gracefully
6. Add descriptive docstrings

Example:

```python
def test_new_feature(self):
    """Test new feature with realistic ground truth.
    
    This test validates that:
    - Documents are correctly retrieved
    - Semantic similarity exceeds threshold
    - Keywords are present in output
    """
    test_case = get_test_case("my_test_case")
    # ... test implementation
```
