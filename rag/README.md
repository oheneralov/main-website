# RAG (Retrieval-Augmented Generation) System

A production-ready RAG implementation using Chroma vector database for semantic search and document retrieval.

## Features

- **Vector-based Retrieval**: Uses Chroma for efficient semantic search
- **Document Management**: Add, retrieve, and manage documents
- **Chunking**: Automatic text chunking with overlap
- **Persistence**: SQLite-backed vector store that persists across sessions
- **LangChain Integration**: Compatible with LangChain for LLM workflows
- **CLI Interface**: Command-line tool for managing documents and queries
- **Metadata Support**: Store and filter documents by metadata
- **Similarity Scoring**: Get relevance scores for retrieved documents

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Python API

```python
from main import ChromaRAG, RAGPipeline

# Initialize RAG system
rag = ChromaRAG(
    persist_directory="./chroma_data",
    collection_name="my_documents"
)

# Add documents
documents = [
    "Document 1 content...",
    "Document 2 content...",
]
rag.add_documents(documents)

# Query documents
results = rag.retrieve_with_scores("search query", k=5)
for result in results:
    print(f"Score: {result['similarity_score']:.3f}")
    print(f"Content: {result['document']}")
```

### CLI Usage

```bash
# Add a file
python cli.py add-file myfile.txt --chunk-size 500

# Query documents
python cli.py query "what is aws lambda"

# Show augmented context for LLM
python cli.py augment "what is aws lambda" -k 3

# View statistics
python cli.py stats

# Clear collection
python cli.py clear
```

## Configuration

Edit `config.py` to customize:
- Persist directory
- Collection name
- Embedding model (default: all-MiniLM-L6-v2)
- Chunk size and overlap
- Number of retrieval results

## LangChain Integration

```python
from langchain_integration import ChromaRetriever

rag = ChromaRAG()
retriever = ChromaRetriever(rag)

# Use with LangChain chains
chain = RetrievalQA.from_chain_type(
    llm=your_llm,
    retriever=retriever
)
```

## Architecture

### ChromaRAG
Core class for vector database management:
- Add documents with metadata
- Retrieve semantically similar documents
- Manage collections
- Persist data

### RAGPipeline
End-to-end pipeline for RAG workflows:
- Augment queries with context
- Generate LLM prompts with retrieved documents

### ChromaRetriever
LangChain-compatible retriever wrapper

## Performance Considerations

- **Embedding Model**: Uses `all-MiniLM-L6-v2` by default (fast, lightweight)
- **Storage**: DuckDB+Parquet for efficient storage and retrieval
- **Batch Operations**: Add multiple documents at once
- **Caching**: Chroma caches embeddings automatically

## Use Cases

- Document Q&A systems
- Knowledge base search
- Context-aware chatbots
- Semantic document retrieval
- Multi-document summarization
