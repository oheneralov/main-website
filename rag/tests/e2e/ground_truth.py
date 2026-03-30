"""Ground truth data for E2E testing."""

# AWS Test Cases
AWS_TEST_CASES = [
    {
        "id": "aws_ec2_basics",
        "query": "What is an EC2 instance and what are its main features?",
        "expected_documents": [
            "Amazon EC2 (Elastic Compute Cloud) provides resizable compute capacity in the cloud",
            "EC2 instances are virtual servers that run applications",
            "EC2 features include scalability, reliability, and cost-effectiveness",
        ],
        "expected_responses": [
            "An EC2 instance is a virtual server running on AWS infrastructure",
            "EC2 provides scalable computing capacity with features like elasticity and flexibility",
        ],
        "expected_keywords": ["EC2", "virtual", "compute", "cloud", "instance"],
    },
    {
        "id": "aws_s3_storage",
        "query": "How does S3 storage work and what are its benefits?",
        "expected_documents": [
            "Amazon S3 (Simple Storage Service) is object storage with high availability",
            "S3 is designed for durability and high availability",
            "S3 supports versioning, encryption, and access control",
        ],
        "expected_responses": [
            "S3 is an object storage service that provides scalable storage",
            "S3 offers high durability through replication and provides security features",
        ],
        "expected_keywords": ["S3", "storage", "object", "bucket", "durability"],
    },
    {
        "id": "aws_lambda_serverless",
        "query": "Explain AWS Lambda and its use cases",
        "expected_documents": [
            "AWS Lambda is a serverless computing service",
            "Lambda automatically scales based on demand",
            "Lambda is ideal for event-driven architectures and microservices",
        ],
        "expected_responses": [
            "Lambda is a serverless service that runs code without managing servers",
            "Lambda automatically scales and charges only for execution time",
        ],
        "expected_keywords": ["Lambda", "serverless", "function", "event", "scale"],
    },
]

# Generic Quality Test Cases
QUALITY_TEST_CASES = [
    {
        "id": "quality_exact_match",
        "query": "What is machine learning?",
        "expected_documents": [
            "Machine learning is a subset of artificial intelligence",
            "Machine learning algorithms learn from data without explicit programming",
        ],
        "expected_responses": [
            "Machine learning is an AI technique where algorithms learn from data",
            "Machine learning enables systems to improve through experience",
        ],
        "expected_keywords": ["machine", "learning", "algorithm", "data", "artificial"],
    },
    {
        "id": "quality_semantic_match",
        "query": "Tell me about deep neural networks",
        "expected_documents": [
            "Deep neural networks have multiple layers for feature extraction",
            "Neural networks are inspired by biological neurons",
        ],
        "expected_responses": [
            "Deep neural networks use multiple interconnected layers",
            "Neural networks learn hierarchical representations of data",
        ],
        "expected_keywords": ["neural", "network", "deep", "layer", "learning"],
    },
]

# Combined test cases
ALL_TEST_CASES = AWS_TEST_CASES + QUALITY_TEST_CASES


def get_test_case(case_id: str) -> dict:
    """Get a test case by ID."""
    for case in ALL_TEST_CASES:
        if case["id"] == case_id:
            return case
    raise ValueError(f"Test case not found: {case_id}")


def get_test_cases_by_category(category: str) -> list:
    """Get test cases by category."""
    if category == "aws":
        return AWS_TEST_CASES
    elif category == "quality":
        return QUALITY_TEST_CASES
    else:
        return ALL_TEST_CASES
