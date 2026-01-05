"""
RAGPipeline - End-to-end Retrieval-Augmented Generation pipeline
Combines document retrieval with LLM prompt generation.
"""

from typing import Dict, Any
from chroma_rag import ChromaRAG


class RAGPipeline:
    """
    End-to-end RAG pipeline combining retrieval with generation.
    """
    
    def __init__(self, rag_system: ChromaRAG):
        """Initialize RAG pipeline with a ChromaRAG instance."""
        self.rag_system = rag_system
    
    def augment_query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Augment a query with retrieved context.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            Dictionary with query, retrieved documents, and context
        """
        retrieved = self.rag_system.retrieve_with_scores(query, k)
        
        context = "\n".join([
            f"[{item['id']}] {item['document']}"
            for item in retrieved
        ])
        
        return {
            "query": query,
            "retrieved_documents": retrieved,
            "context": context,
            "num_documents": len(retrieved)
        }
    
    def generate_prompt_with_context(self, query: str, k: int = 5) -> str:
        """
        Generate a prompt with retrieved context for LLM.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            Formatted prompt with context
        """
        augmented = self.augment_query(query, k)
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{augmented['context']}

Question: {augmented['query']}

Answer:"""
        
        return prompt
