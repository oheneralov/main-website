import argparse
import json
from pathlib import Path

import numpy as np

from chroma_rag import ChromaRAG
from config import get_default_config
from rag_pipeline import RAGPipeline


def cmd_show_all(rag: ChromaRAG, args):
    """Show all data from the collection: ids, embeddings, metadatas, documents."""
    try:

        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj

        all_data = rag.collection.get(include=["embeddings", "metadatas", "documents"])
        safe_data = {
            "ids": all_data.get("ids", []),
            "embeddings": convert(all_data.get("embeddings", [])),
            "metadatas": all_data.get("metadatas", []),
            "documents": all_data.get("documents", []),
        }
        print(json.dumps(safe_data, indent=2))
    except Exception as e:
        print(f"Error retrieving all data: {e}")


def cmd_add_file(rag: ChromaRAG, args):
    """Add a file to the RAG system."""
    if not Path(args.file).exists():
        print(f"Error: File {args.file} not found")
        return

    rag.add_documents_from_file(
        file_path=args.file,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Successfully added {args.file}")


def cmd_query(rag: ChromaRAG, args):
    """Query the RAG system."""
    results = rag.retrieve_with_scores(args.query, k=args.k)

    print(f"\n{'=' * 60}")
    print(f"Query: {args.query}")
    print(f"{'=' * 60}\n")

    if not results:
        print("No results found.")
        return

    for i, result in enumerate(results, 1):
        print(f"[{i}] Score: {result['similarity_score']:.3f}")
        print(f"    ID: {result['id']}")
        print(f"    Document: {result['document'][:200]}...")
        if result["metadata"]:
            print(f"    Metadata: {result['metadata']}")
        print()


def cmd_stats(rag: ChromaRAG, args):
    """Show collection statistics."""
    stats = rag.get_collection_stats()
    print(json.dumps(stats, indent=2))


def cmd_clear(rag: ChromaRAG, args):
    """Clear the collection."""
    confirm = input("Are you sure you want to clear the collection? (yes/no): ")
    if confirm.lower() == "yes":
        rag.clear_collection()
        print("Collection cleared.")
    else:
        print("Cancelled.")


def cmd_augment(rag: ChromaRAG, args):
    """Show augmented context for a query."""
    pipeline = RAGPipeline(rag)
    augmented = pipeline.augment_query(args.query, k=args.k)

    print(f"\nQuery: {args.query}\n")
    print(f"Retrieved {augmented['num_documents']} relevant documents:\n")
    print(augmented["context"])

    print("\n\nLLM Prompt Template:")
    print("=" * 60)
    prompt = pipeline.generate_prompt_with_context(args.query, k=args.k)
    print(prompt)


def main():
    """CLI interface for RAG system."""
    config = get_default_config()

    parser = argparse.ArgumentParser(
        description="RAG System CLI - Retrieval-Augmented Generation with Chroma"
    )
    parser.add_argument(
        "--db-dir",
        default=config.persist_directory,
        help=f"Database directory (default: {config.persist_directory})",
    )
    parser.add_argument(
        "--collection",
        default=config.collection_name,
        help=f"Collection name (default: {config.collection_name})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add file command
    add_parser = subparsers.add_parser("add-file", help="Add a file to RAG")
    add_parser.add_argument("file", help="File path")
    add_parser.add_argument(
        "--chunk-size",
        type=int,
        default=config.chunk_size,
        help="Chunk size (default: 500)",
    )
    add_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=config.chunk_overlap,
        help="Chunk overlap (default: 50)",
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument(
        "-k",
        type=int,
        default=config.retrieval_k,
        help=f"Number of results (default: {config.retrieval_k})",
    )

    # Stats command
    subparsers.add_parser("stats", help="Show collection statistics")

    # Show all data command
    subparsers.add_parser(
        "show-all",
        help="Show all data in the collection (ids, embeddings, metadatas, documents)",
    )

    # Clear command
    subparsers.add_parser("clear", help="Clear the collection")

    # Augment command
    augment_parser = subparsers.add_parser(
        "augment", help="Show augmented context for a query"
    )
    augment_parser.add_argument("query", help="Query text")
    augment_parser.add_argument(
        "-k",
        type=int,
        default=config.retrieval_k,
        help=f"Number of results (default: {config.retrieval_k})",
    )

    args = parser.parse_args()

    # Initialize RAG
    rag = ChromaRAG(persist_directory=args.db_dir, collection_name=args.collection)

    # Command routing
    commands = {
        "add-file": cmd_add_file,
        "query": cmd_query,
        "stats": cmd_stats,
        "show-all": cmd_show_all,
        "clear": cmd_clear,
        "augment": cmd_augment,
    }

    if args.command in commands:
        commands[args.command](rag, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
