"""
ChromaRAG - Vector Database-based Retrieval System
Manages document storage, embeddings, and semantic search using Chroma.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain.text_splitter import MarkdownTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaRAG:
    """
    A Retrieval-Augmented Generation system using Chroma vector database.
    
    This class handles:
    - Document storage and retrieval
    - Semantic search using embeddings
    - Collection management
    - Vector similarity queries
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        collection_name: str = "documents",
        embedding_model: str = "default"
    ):
        """
        Initialize ChromaRAG system.
        
        Args:
            persist_directory: Directory to persist Chroma database
            collection_name: Name of the collection for documents
            embedding_model: Embedding model to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client with persistence
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False
        )
        
        self.client = chromadb.Client(settings)
        
        # Initialize embedding function
        if embedding_model == "default":
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        else:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaRAG initialized with collection: {collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts
            metadata: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        if metadata is None:
            metadata = [{} for _ in documents]
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadata,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to collection")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def add_documents_from_file(
        self,
        file_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Load documents from a file and add to database.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            metadata: Optional metadata for all documents
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into chunks using MarkdownTextSplitter
            splitter = MarkdownTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            chunks = splitter.split_text(content)
            
            # Create metadata for each chunk
            chunk_metadata = []
            for i in range(len(chunks)):
                meta = {"source": file_path, "chunk": i}
                if metadata:
                    meta.update(metadata)
                chunk_metadata.append(meta)
            
            # Add to collection
            self.add_documents(
                documents=chunks,
                metadata=chunk_metadata,
                ids=[f"{Path(file_path).stem}_chunk_{i}" for i in range(len(chunks))]
            )
            
            logger.info(f"Added {len(chunks)} chunks from {file_path}")
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            k: Number of results to retrieve
            filters: Optional metadata filters
        
        Returns:
            Dictionary with documents, distances, and metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filters
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with similarity scores (0-1, where 1 is most similar).
        
        Args:
            query: Query text
            k: Number of results to retrieve
        
        Returns:
            List of dictionaries with document, metadata, and score
        """
        results = self.retrieve(query, k)
        
        return [
            {
                "document": doc,
                "metadata": meta,
                "id": doc_id,
                "distance": dist,
                "similarity_score": 1 - dist  # Convert distance to similarity
            }
            for doc, meta, doc_id, dist in zip(
                results["documents"],
                results["metadatas"],
                results["ids"],
                results["distances"]
            )
        ]
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Get all documents and delete them
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            doc_count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": doc_count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            raise
    
    def persist(self) -> None:
        """Persist the database to disk."""
        try:
            self.client.persist()
            logger.info("Database persisted")
        except Exception as e:
            logger.error(f"Error persisting database: {e}")
            raise
