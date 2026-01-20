"""FastAPI entrypoint exposing the RAG system as a REST service."""

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chroma_rag import ChromaRAG
from config import get_default_config
from rag_pipeline import RAGPipeline

config = get_default_config()
rag_system = ChromaRAG(
    persist_directory=config.persist_directory,
    collection_name=config.collection_name,
    embedding_model=config.embedding_model,
)
pipeline = RAGPipeline(rag_system)

app = FastAPI(
    title="Chroma RAG API",
    version="1.0.0",
    description="REST interface for ingesting documents and querying the Chroma-backed RAG pipeline.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


class DocumentIngestRequest(BaseModel):
    file_path: str = Field(
        ..., description="Absolute or workspace-relative path to the file to ingest"
    )
    chunk_size: Optional[int] = Field(
        default=None, ge=1, description="Override chunk size for this upload"
    )
    chunk_overlap: Optional[int] = Field(
        default=None, ge=0, description="Override chunk overlap for this upload"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadata applied to all chunks from this file"
    )


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query")
    k: Optional[int] = Field(
        default=None, ge=1, description="Number of chunks to retrieve"
    )


@app.get("/health")
def health() -> Dict[str, str]:
    """Liveness probe endpoint."""
    return {"status": "ok"}


@app.get("/stats")
def stats() -> Dict[str, Any]:
    """Return collection statistics."""
    return rag_system.get_collection_stats()


@app.post("/documents")
def add_document(payload: DocumentIngestRequest) -> Dict[str, Any]:
    """Ingest a document from disk into the vector store."""
    file_path = Path(payload.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")

    chunk_size = payload.chunk_size or config.chunk_size
    chunk_overlap = payload.chunk_overlap or config.chunk_overlap

    try:
        rag_system.add_documents_from_file(
            file_path=str(file_path),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=payload.metadata,
        )
        rag_system.persist()
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - surfaced to client
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "status": "ingested",
        "file": str(file_path),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }


@app.post("/query")
def query_documents(payload: QueryRequest) -> Dict[str, Any]:
    """Retrieve relevant chunks and augmented context for a query."""
    k_value = payload.k or config.retrieval_k

    try:
        print("Received query:", payload.query)
        augmented = pipeline.augment_query(payload.query, k=k_value)
        prompt = pipeline.generate_prompt_with_context(payload.query, k=k_value)
    except Exception as exc:  # pragma: no cover - surfaced to client
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "query": augmented["query"],
        "num_documents": augmented["num_documents"],
        "results": augmented["retrieved_documents"],
        "context": augmented["context"],
        "llm_prompt": prompt,
    }


def get_app() -> FastAPI:
    """Expose the FastAPI app for external runners/tests."""
    return app


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
