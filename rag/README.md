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

## Reasoning Strategies: ReAct & CoT

### Chain-of-Thought (CoT) in RAG
- **What it is**: CoT prompts instruct the LLM to narrate intermediate reasoning before answering, which reduces hallucinations when paired with retrieved snippets.
- **How to use**: After calling `RAGPipeline.generate_prompt_with_context(...)`, wrap the result with a CoT suffix such as `"Let's think step by step using only the context above."` so the model verbalizes grounding steps that cite `[chunk-id]` markers from the augmented context.
- **Why it matters**: Inspectable reasoning lets you validate that each deduction references a retrieved chunk, and you can automatically flag responses whose CoT traces omit citations.

### ReAct (Reason + Act) with ChromaRetriever
- **What it is**: ReAct alternates between thought states and actions (e.g., `Search[...]`, `Lookup[...]`) so the LLM can iteratively call the retriever until it has sufficient evidence.
- **How to wire it**: In LangChain, map the `ChromaRetriever` into a `Tool` and build a `ReActChain` or `AgentExecutor`. Each `Act` step issues a new `retriever.get_relevant_documents()` call, while the `Reason` step examines the snippet IDs/metadata to decide on the next action.
- **Control knobs**: Limit the max action count (e.g., `max_iterations=5`) to keep latency predictable, and stream the intermediate thoughts for observability.
- **Benefits**: ReAct turns the static retrieve-then-answer loop into an interactive plan-and-execute cycle that can fetch disjoint facts, cross-check conflicting chunks, and bail out with an "I don't know" if the retriever stops returning relevant hits.

When combined, CoT provides transparent reasoning within each ReAct "thought" block, yielding rich traces such as `Thought 2: Using doc [a12] and [b04], the SLA mention is 99.9%. Action 2: Search("monthly uptime")`. This makes debugging RAG quality much easier and enables guardrails that verify every final statement references at least one retrieved document ID.

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
