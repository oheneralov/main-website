"""
RAG (Retrieval-Augmented Generation) System using Chroma
"""

import os

from chroma_rag import ChromaRAG
from rag_pipeline import RAGPipeline

def main():    
    # Initialize RAG system
    rag = ChromaRAG(
        persist_directory="./chroma_data",
        collection_name="aws_docs",
        embedding_model="default"
    )
    
    # Load and ingest B2B contractor services document
    doc_path = os.path.join(
        os.path.dirname(__file__),
        "documents",
        "b2b_contractor_services.txt"
    )

    rag.add_documents_from_file(
        file_path=doc_path,
        metadata={
            "service": "B2B Contractor Services",
            "source": "documents/b2b_contractor_services.txt"
        }
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
