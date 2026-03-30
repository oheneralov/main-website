"""
RAGPipeline - End-to-end Retrieval-Augmented Generation pipeline
Combines document retrieval with LLM prompt generation.
"""

import logging
import time
from typing import Dict, Any, Optional
from chroma_rag import ChromaRAG
from config import RAGConfig, LLMProvider

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end RAG pipeline combining retrieval with generation.
    """
    
    def __init__(self, rag_system: ChromaRAG, config: RAGConfig = None):
        """Initialize RAG pipeline with a ChromaRAG instance."""
        self.rag_system = rag_system
        self.config = config or RAGConfig()
        self.llm = self._init_llm()
    
    def _init_llm(self) -> Optional[Any]:
        """Initialize LLM based on provider configuration."""
        try:
            if self.config.llm_provider == LLMProvider.LOCAL_HUGGINGFACE:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                
                logger.info(f"📥 Loading local model: {self.config.llm_model.value}")
                device = self.config.local_model_device
                
                # Check if CUDA is available
                if device == "cuda" and not torch.cuda.is_available():
                    logger.warning("⚠️  CUDA requested but not available, falling back to CPU")
                    device = "cpu"
                
                logger.info(f"💻 Using device: {device}")
                
                tokenizer = AutoTokenizer.from_pretrained(self.config.llm_model.value)
                model = AutoModelForCausalLM.from_pretrained(
                    self.config.llm_model.value,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None
                )
                
                if device == "cpu":
                    model = model.to(device)
                
                text_pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if device == "cuda" else -1,
                    max_new_tokens=self.config.llm_max_tokens,
                    temperature=self.config.llm_temperature,
                )
                
                logger.info(f"🤖 LLM initialized: Local model (model: {self.config.llm_model.value}, device: {device})")
                return text_pipeline
            
            elif self.config.llm_provider == LLMProvider.OLLAMA:
                from langchain_community.llms import Ollama
                llm = Ollama(
                    base_url=self.config.ollama_base_url,
                    model=self.config.llm_model.value,
                    temperature=self.config.llm_temperature,
                )
                logger.info(f"🤖 LLM initialized: Ollama (model: {self.config.llm_model.value}, base_url: {self.config.ollama_base_url})")
                return llm
            elif self.config.llm_provider == LLMProvider.OPENAI:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    api_key=self.config.openai_api_key,
                    model=self.config.llm_model.value,
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens,
                )
                logger.info(f"🤖 LLM initialized: OpenAI (model: {self.config.llm_model.value})")
                return llm
            elif self.config.llm_provider == LLMProvider.ANTHROPIC:
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(
                    api_key=self.config.anthropic_api_key,
                    model=self.config.llm_model.value,
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens,
                )
                logger.info(f"🤖 LLM initialized: Anthropic Claude (model: {self.config.llm_model.value})")
                return llm
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
        except ImportError as e:
            logger.warning(f"⚠️  Could not import LLM provider - {e}")
            logger.warning("Install required packages: pip install langchain-openai langchain-anthropic")
            return None
    
    def augment_query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Augment a query with retrieved context.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            Dictionary with query, retrieved documents, and context
        """
        start_time = time.perf_counter()
        retrieved = self.rag_system.retrieve_with_scores(query, k)
        
        context = "\n\n".join([
            item['document']
            for item in retrieved
        ])
        
        elapsed_seconds = time.perf_counter() - start_time
        logger.info(f"⏱️  augment_query(): {elapsed_seconds:.2f}s (retrieval + formatting)")
        
        return {
            "query": query,
            "retrieved_documents": retrieved,
            "context": context,
            "num_documents": len(retrieved)
        }
    
    def generate_response(self, query: str, k: int = 5) -> str:
        """
        Generate a natural language response using LLM based on retrieved documents.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            LLM-generated response
        """
        if not self.llm:
            raise RuntimeError("LLM not initialized. Please install required LLM packages.")
        
        total_start = time.perf_counter()
        logger.info(f"Generating LLM response for: {query}")
        
        augment_start = time.perf_counter()
        augmented = self.augment_query(query, k)
        augment_seconds = time.perf_counter() - augment_start
        
        prompt = f"""You are a helpful assistant. Based on the provided context, answer the user's question clearly and concisely.

IMPORTANT: Respond ONLY with plain text. Do NOT use markdown. Do NOT use:
- Headers (##, ###, etc.)
- Bold (**text**)
- Italics (*text*)
- Lists (-, *, •)
- Code blocks (```)
- Any special formatting

Just write a normal paragraph or natural conversation. If the context doesn't contain relevant information, say so.

Context:
{augmented['context']}

Question: {augmented['query']}

Answer:"""
        
        logger.debug(f"LLM Prompt:\n{prompt}")
        logger.info(f"Invoking LLM ({self.config.llm_provider.value}) with model: {self.config.llm_model.value}")
        
        # Handle local HuggingFace pipeline
        llm_start = time.perf_counter()
        if self.config.llm_provider == LLMProvider.LOCAL_HUGGINGFACE:
            outputs = self.llm(prompt, max_new_tokens=self.config.llm_max_tokens)
            result = outputs[0]['generated_text']
            # Extract just the answer part (after "Answer:")
            if "Answer:" in result:
                result = result.split("Answer:")[-1].strip()
        else:
            # Handle LangChain LLM models
            response = self.llm.invoke(prompt)
            result = response if isinstance(response, str) else response.content
        
        llm_seconds = time.perf_counter() - llm_start
        total_seconds = time.perf_counter() - total_start
        
        logger.info(f"⏱️  LLM generation: {llm_seconds:.2f}s")
        logger.info(f"⏱️  generate_response(): total {total_seconds:.2f}s (augment: {augment_seconds:.2f}s, llm: {llm_seconds:.2f}s)")
        logger.info(f"LLM returned response ({len(result)} chars)")
        
        return result
    
    def generate_prompt_with_context(self, query: str, k: int = 5) -> str:
        """
        Generate a prompt with retrieved context for LLM.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            Formatted prompt with context
        """
        start_time = time.perf_counter()
        augmented = self.augment_query(query, k)
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{augmented['context']}

Question: {augmented['query']}

Answer:"""
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"⏱️  generate_prompt_with_context(): {elapsed_ms:.2f}ms")
        
        return prompt
