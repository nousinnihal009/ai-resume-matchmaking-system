"""
Embedding generation pipeline.

Delegates to app.core.model_manager for actual inference.
This module provides the pipeline interface used by Celery tasks
and API endpoints.

The model (all-MiniLM-L6-v2) downloads automatically on first call
and is cached to EMBEDDING_CACHE_DIR for subsequent uses.
"""
import asyncio
from typing import List, Optional
from app.core.model_manager import encode_text, encode_batch, cosine_similarity
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.

    Synchronous — safe to call from Celery tasks.
    For async contexts, use generate_embedding_async().

    Args:
        text: Text to embed (resume content or job description)

    Returns:
        List of 384 floats. Returns zero vector for empty input.
    """
    logger.info(
        "embedding_generation_started",
        text_length=len(text) if text else 0,
    )
    vector = encode_text(text)
    logger.info(
        "embedding_generation_complete",
        dimensions=len(vector),
    )
    return vector


async def generate_embedding_async(text: str) -> list[float]:
    """
    Async wrapper for embedding generation.

    Runs the CPU-bound encoding in a thread pool executor to avoid
    blocking the FastAPI event loop.

    Args:
        text: Text to embed

    Returns:
        List of 384 floats
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, encode_text, text)


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts efficiently.

    Synchronous — safe to call from Celery tasks.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors, one per input text
    """
    return encode_batch(texts)


async def generate_embeddings_batch_async(
    texts: list[str],
) -> list[list[float]]:
    """
    Async batch embedding generation.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, encode_batch, texts)


class EmbeddingService:
    """Backward-compatible embedding service wrapper.

    Provides the same interface as the original EmbeddingService class
    so that existing callers (matching.py, etc.) continue to work
    without modification until they are upgraded.
    """

    def __init__(self):
        self.dimension = 384

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text (async)."""
        if not text or not text.strip():
            return None
        return await generate_embedding_async(text)

    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts (async)."""
        results = await generate_embeddings_batch_async(texts)
        return results

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        return cosine_similarity(vec1, vec2)


# Global embedding service instance (backward compatibility)
embedding_service = EmbeddingService()
