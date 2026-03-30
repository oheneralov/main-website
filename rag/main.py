import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from chroma_rag import ChromaRAG
from config import get_default_config
from rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_system_memory():
    """Log available system memory to verify LLM capacity."""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    used_gb = memory.used / (1024**3)
    percent = memory.percent

    swap_total_gb = swap.total / (1024**3)
    swap_available_gb = swap.free / (1024**3)
    swap_used_gb = swap.used / (1024**3)
    swap_percent = swap.percent

    logger.info("System Memory Report:")
    logger.info(f"   RAM Total: {total_gb:.2f} GB")
    logger.info(f"   RAM Available: {available_gb:.2f} GB")
    logger.info(f"   RAM Used: {used_gb:.2f} GB ({percent}%)")
    logger.info(f"   Swap Total: {swap_total_gb:.2f} GB")
    logger.info(f"   Swap Available: {swap_available_gb:.2f} GB")
    logger.info(f"   Swap Used: {swap_used_gb:.2f} GB ({swap_percent}%)")

    # Log current process memory
    current_process = psutil.Process()
    process_memory_mb = current_process.memory_info().rss / (1024**2)
    logger.info(f"   This process (uvicorn): {process_memory_mb:.2f} MB")

    if available_gb < 4.0:
        logger.warning(
            f"⚠️  WARNING: Only {available_gb:.2f} GB available - may be insufficient for LLM"
        )
    else:
        logger.info(f"✅ Sufficient memory available for LLM ({available_gb:.2f} GB)")

    # Memory usage breakdown
    logger.info("Memory Usage Breakdown:")
    logger.info("   LLM Model (QWEN 0.5B on CPU): ~1.5-2.5 GB typical")
    logger.info("   Embedding Model (MiniLM): ~0.5-1.0 GB")
    logger.info("   Chroma Vector DB: ~0.5-1.0 GB (depends on documents)")
    logger.info(f"   System & Other: ~{used_gb - process_memory_mb / 1024:.2f} GB")


config = get_default_config()
rag_system = ChromaRAG(
    persist_directory=config.persist_directory,
    collection_name=config.collection_name,
    embedding_model=config.embedding_model,
)
pipeline = None  # Initialized in lifespan startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI app."""
    # Startup
    global pipeline
    logger.info("🚀 Server startup - warming up LLM...")
    log_system_memory()
    pipeline = RAGPipeline(rag_system, config)
    if pipeline.llm:
        logger.info("✅ LLM is initialized and ready for requests")
    else:
        logger.warning("⚠️  LLM not initialized - check configuration")
    yield
    # Shutdown
    logger.info("🛑 Server shutdown")


app = FastAPI(
    title="Chroma RAG API",
    version="1.0.0",
    description="REST interface for ingesting documents and querying the Chroma-backed RAG pipeline.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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


# New endpoint to clear all documents from the collection
@app.post("/documents/clear")
def clear_documents() -> JSONResponse:
    """Clear all documents from the vector store collection."""
    try:
        rag_system.clear_collection()
        rag_system.persist()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JSONResponse(content={"status": "cleared"})


@app.post("/query")
def query_documents(payload: QueryRequest) -> Dict[str, Any]:
    """Retrieve relevant chunks, generate LLM response for a query."""
    assert pipeline is not None, "Pipeline not initialized"
    k_value = payload.k or config.retrieval_k

    try:
        logger.info(f"📝 Query received: {payload.query}")

        # Augment query and get retrieved documents
        augmented = pipeline.augment_query(payload.query, k=k_value)
        logger.info(f"📚 Retrieved {augmented['num_documents']} documents")

        # Generate LLM response
        llm_response = None
        if pipeline.llm is None:
            logger.error(
                "❌ LLM not initialized - no LLM provider available. Using raw context as fallback."
            )
            llm_response = augmented["context"]
        else:
            try:
                logger.info("🔄 Calling LLM to generate response...")
                llm_response = pipeline.generate_response(payload.query, k=k_value)
                logger.info("✅ LLM response generated successfully")
            except Exception as llm_err:
                logger.error(
                    f"❌ LLM call failed: {llm_err}. Using raw context as fallback."
                )
                llm_response = augmented["context"]

        prompt = pipeline.generate_prompt_with_context(payload.query, k=k_value)
    except Exception as exc:  # pragma: no cover - surfaced to client
        logger.error(f"❌ Query processing error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "query": augmented["query"],
        "num_documents": augmented["num_documents"],
        "results": augmented["retrieved_documents"],
        "response": llm_response,  # LLM-generated response
        "context": augmented["context"],  # Raw context for reference
        "llm_prompt": prompt,
    }


"""FastAPI entrypoint exposing the RAG system as a REST service."""


@app.get("/documents/all")
def get_all_documents() -> Dict[str, Any]:
    """Return all data from the collection: ids, embeddings, metadatas, documents."""
    try:
        # Get all documents, embeddings, metadatas, and ids
        all_data = rag_system.collection.get(
            include=["embeddings", "metadatas", "documents"]
        )
        return {
            "ids": all_data.get("ids", []),
            "embeddings": all_data.get("embeddings", []),
            "metadatas": all_data.get("metadatas", []),
            "documents": all_data.get("documents", []),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


"""FastAPI entrypoint exposing the RAG system as a REST service."""


def get_app() -> FastAPI:
    """Expose the FastAPI app for external runners/tests."""
    return app


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
