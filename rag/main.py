"""
RAG (Retrieval-Augmented Generation) System using Chroma
Example usage and demonstration of the RAG system.
"""

import os

from chroma_rag import ChromaRAG
from rag_pipeline import RAGPipeline

def main():
    """Example usage of ChromaRAG."""
    
    # Initialize RAG system
    rag = ChromaRAG(
        persist_directory="./chroma_data",
        collection_name="aws_docs",
        embedding_model="default"
    )
    
    # Load documents from file
    doc_path = os.path.join(os.path.dirname(__file__), "documents", "aws_services.txt")
    
    with open(doc_path, "r") as f:
        input_docs = [line.strip() for line in f.readlines() if line.strip()]
    
    # Add documents
    rag.add_documents_to_db(
        documents=input_docs,
        metadata=[
            {"service": "EC2"},
            {"service": "S3"},
            {"service": "Lambda"},
            {"service": "RDS"},
            {"service": "DynamoDB"}
        ]
    )
    
    # Retrieve relevant documents
    query = "Tell me about serverless computing on AWS"
    results = rag.retrieve_with_scores(query, k=3)
    
    print(f"\nQuery: {query}")
    print("\nRetrieved Documents:")
    for i, result in enumerate(results, 1):
        print(f"{i}. [Score: {result['similarity_score']:.3f}] {result['document']}")
    
    # Create RAG pipeline
    pipeline = RAGPipeline(rag)
    augmented = pipeline.augment_query(query, k=3)
    
    print(f"\n\nAugmented Context for LLM:")
    print(augmented['context'])
    
    # Get collection stats
    stats = rag.get_collection_stats()
    print(f"\n\nCollection Stats: {stats}")


if __name__ == "__main__":
    main()
