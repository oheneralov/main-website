"""Constants and enums for the RAG system."""

from enum import Enum


class ChunkSplitMethod(str, Enum):
    """Supported strategies for chunking documents."""

    TOKENS = "tokens"  # Split by fixed number of tokens
    SENTENCES = "sentences"  # Split by sentence boundaries
    PARAGRAPHS = "paragraphs"  # Split by paragraph breaks
    MARKDOWN = "markdown"  # Split by markdown headers
    LINES = "lines"  # Split by line breaks
    HEADER = "header"  # Split by custom header patterns (e.g., ##, ###)
    FIXED_SIZE = "fixed_size"  # Split by fixed character or word count
    WINDOW = "window"  # Sliding window chunking
    CUSTOM = "custom"  # User-defined chunking logic


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    LOCAL_HUGGINGFACE = "local_huggingface"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMModel(str, Enum):
    """Supported LLM models."""
    # Lightweight models (< 7B parameters)
    TINYLLAMA_1_1B = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # 1.1B params, ~2-4GB VRAM
    TINYLLAMA_1_1B_INT4_GGUF = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"  # 4-bit quantized, ~500MB
    TINYLLAMA_1_1B_INT8_GGUF = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"  # 8-bit quantized, ~1GB (use q8_0 variant)
    TINYLLAMA_1_1B_AWQ = "TheBloke/TinyLlama-1.1B-Chat-v1.0-AWQ"  # AWQ quantized, ~700MB
    PHI_2 = "microsoft/phi-2"  # 2.7B params, ~4-8GB VRAM
    GEMMA_2B = "google/gemma-2b-it"  # 2B params, ~4-8GB VRAM
    QWEN_0_5B = "Qwen/Qwen1.5-0.5B-Chat"  # 0.5B params, ~1-2GB VRAM
    QWEN_0_5B_INT4_GGUF = "TheBloke/Qwen1.5-0.5B-Chat-GGUF"  # 4-bit quantized, ~200MB
    QWEN_0_5B_INT8_GGUF = "TheBloke/Qwen1.5-0.5B-Chat-GGUF"  # 8-bit quantized, ~400MB (use q8_0 variant)
    QWEN_0_5B_AWQ = "TheBloke/Qwen1.5-0.5B-Chat-AWQ"  # AWQ quantized, ~300MB
    QWEN_1_8B = "Qwen/Qwen1.5-1.8B-Chat"  # 1.8B params, ~3-5GB VRAM
    PHI_3_MINI = "microsoft/Phi-3-mini-4k-instruct"  # 3.8B params, ~8-10GB VRAM
    DISTILBERT = "distilgpt2"  # 82M params, ~512MB VRAM (for text generation)
    # Medium models
    MISTRAL_7B = "mistralai/Mistral-7B-Instruct-v0.1"  # ~16-20GB VRAM
    LLAMA2_7B = "meta-llama/Llama-2-7b-chat-hf"  # ~16-20GB VRAM
    # Provider-specific (API-based, no local memory)
    OPENAI_GPT4 = "gpt-4"  # API-based, no local VRAM needed
    OPENAI_GPT35_TURBO = "gpt-3.5-turbo"  # API-based, no local VRAM needed
    ANTHROPIC_CLAUDE3_SONNET = "claude-3-sonnet"  # API-based, no local VRAM needed
    # Ollama models (memory depends on Ollama configuration)
    OLLAMA_MISTRAL = "mistral"  # ~7B params (~16-20GB VRAM typical)
    OLLAMA_LLAMA2 = "llama2"  # ~7B params (~16-20GB VRAM typical)


class EmbeddingModel(str, Enum):
    """Supported embedding models."""
    MINI_LM = "all-MiniLM-L6-v2"  # Weakest
    MINI_LM_L12 = "all-MiniLM-L12-v2"
    DISTILBERT = "distilbert-base-nli-stsb-mean-tokens"
    PARAPHRASE_MPNET = "paraphrase-mpnet-base-v2"
    MP_NET = "all-mpnet-base-v2"
    BGE_BASE = "BAAI/bge-base-en-v1.5"
    E5_BASE = "intfloat/e5-base-v2"
    GTR_T5_BASE = "sentence-transformers/gtr-t5-base"
    GTR_T5_LARGE = "sentence-transformers/gtr-t5-large"
    E5_LARGE = "intfloat/e5-large-v2"
    BGE_LARGE = "BAAI/bge-large-en-v1.5"
    GTR_T5_XL = "sentence-transformers/gtr-t5-xl"
    INSTRUCTOR_XL = "hkunlp/instructor-xl"
    # Add stronger, state-of-the-art models
    BGE_M3 = "BAAI/bge-m3"
    BGE_LARGE_EN_V1_5 = "BAAI/bge-large-en-v1.5"
    E5_MISTRAL_7B = "intfloat/e5-mistral-7b-instruct"
    E5_MISTRAL_7B_32K = "intfloat/e5-mistral-7b-instruct-32k"
    GTR_T5_XXL = "sentence-transformers/gtr-t5-xxl"
    OPENAI_TEXT_EMBED_3_LARGE = "text-embedding-3-large"
    OPENAI_TEXT_EMBED_3_SMALL = "text-embedding-3-small"
    COHERE_EMBED_ENGLISH_V3 = "embed-english-v3.0"
    COHERE_EMBED_MULTILINGUAL_V3 = "embed-multilingual-v3.0"
    CUSTOM = "custom"


class HNSWSpace(str, Enum):
    """HNSW space metric for vector database."""
    COSINE = "cosine"  # Best for semantic similarity (default)
    L2 = "l2"  # Euclidean distance (faster)
    IP = "ip"  # Inner product (fastest, requires normalized vectors)
