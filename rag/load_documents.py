"""
Script to load documents from the documents directory into the RAG system.
"""

from pathlib import Path

from config import get_default_config
from main import ChromaRAG


def load_all_documents():
    """Load all documents from the documents directory into RAG."""

    config = get_default_config()

    # Initialize RAG
    rag = ChromaRAG(
        persist_directory=config.persist_directory,
        collection_name=config.collection_name,
        embedding_model=config.embedding_model,
    )

    # Get documents directory
    docs_dir = Path(__file__).parent / "documents"

    if not docs_dir.exists():
        print(f"Documents directory not found: {docs_dir}")
        return rag

    # Process all text files in documents directory
    txt_files = list(docs_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {docs_dir}")
        return rag

    print(f"Found {len(txt_files)} document(s) to load...\n")

    for file_path in txt_files:
        print(f"Loading: {file_path.name}")
        try:
            rag.add_documents_from_file(
                file_path=str(file_path),
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                metadata={"source_file": file_path.name},
            )
            print(f"✓ Successfully loaded {file_path.name}\n")
        except Exception as e:
            print(f"✗ Error loading {file_path.name}: {e}\n")

    # Show collection stats
    stats = rag.get_collection_stats()
    print("\nCollection Statistics:")
    print(f"  Total documents: {stats['document_count']}")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Storage: {stats['persist_directory']}")

    return rag


def test_retrieval():
    """Test retrieval with sample queries."""

    config = get_default_config()

    # Initialize RAG with existing data
    rag = ChromaRAG(
        persist_directory=config.persist_directory,
        collection_name=config.collection_name,
        embedding_model=config.embedding_model,
    )

    # Test queries
    test_queries = [
        "What is Lambda?",
        "Tell me about database services",
        "How do I store files in AWS?",
        "What is a CDN?",
    ]

    print("\n" + "=" * 60)
    print("Testing RAG Retrieval")
    print("=" * 60 + "\n")

    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 40)

        results = rag.retrieve_with_scores(query, k=2)

        if not results:
            print("No results found.\n")
            continue

        for i, result in enumerate(results, 1):
            print(f"{i}. [Score: {result['similarity_score']:.3f}]")
            print(f"   {result['document'][:120]}...\n")

        print()


if __name__ == "__main__":
    print("Loading documents into RAG system...")
    print("=" * 60 + "\n")

    # Load documents
    rag = load_all_documents()

    # Test retrieval
    test_retrieval()

    print("\n✓ RAG system is ready!")
