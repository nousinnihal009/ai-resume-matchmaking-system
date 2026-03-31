"""
Sentence-transformers model manager.

Implements a thread-safe singleton pattern for the embedding model.
The model is downloaded once on first access and cached to disk at
EMBEDDING_CACHE_DIR so subsequent startups do not re-download.

Model: sentence-transformers/all-MiniLM-L6-v2
  - Dimensions: 384
  - Size: ~90MB
  - Speed: ~14,000 sentences/second on CPU
  - Quality: Excellent for semantic similarity tasks

Usage:
    from app.core.model_manager import get_embedding_model
    model = get_embedding_model()
    vector = model.encode("Python developer with FastAPI experience")

Threading:
    The model is loaded once and shared across all threads.
    SentenceTransformer.encode() is thread-safe for inference.
    Loading is protected by a threading.Lock to prevent duplicate
    downloads on concurrent first-access.
"""
import threading
import os
from typing import Optional
import numpy as np
from app.core.logging_config import get_logger

logger = get_logger(__name__)

_model_lock = threading.Lock()
_model_instance = None


def get_embedding_model():
    """
    Return the singleton SentenceTransformer model instance.

    Downloads and caches the model on first call.
    Subsequent calls return the cached instance immediately.

    Returns:
        SentenceTransformer instance ready for inference

    Raises:
        RuntimeError: If model cannot be loaded after download
    """
    global _model_instance

    if _model_instance is not None:
        return _model_instance

    with _model_lock:
        # Double-checked locking pattern
        if _model_instance is not None:
            return _model_instance

        from app.core.config import settings

        cache_dir = settings.embedding_cache_dir
        model_name = settings.embedding_model

        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        logger.info(
            "embedding_model_loading",
            model=model_name,
            cache_dir=cache_dir,
        )

        try:
            from sentence_transformers import SentenceTransformer
            _model_instance = SentenceTransformer(
                model_name,
                cache_folder=cache_dir,
            )

            logger.info(
                "embedding_model_loaded",
                model=model_name,
                dimensions=settings.embedding_dimension,
            )

            return _model_instance

        except Exception as exc:
            logger.error(
                "embedding_model_load_failed",
                model=model_name,
                error=str(exc),
            )
            raise RuntimeError(
                f"Failed to load embedding model '{model_name}': {exc}"
            ) from exc


def encode_text(text: str) -> list[float]:
    """
    Encode a single text string into a 384-dimensional vector.

    Runs synchronously — call from thread pool executor in async context.

    Args:
        text: Input text to encode. Should be clean, preprocessed text.

    Returns:
        List of 384 floats representing the semantic embedding.
        Returns zero vector on encoding failure (never raises).
    """
    if not text or not text.strip():
        from app.core.config import settings
        return [0.0] * settings.embedding_dimension

    try:
        model = get_embedding_model()
        vector = model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vector.tolist()

    except Exception as exc:
        logger.error(
            "text_encoding_failed",
            text_length=len(text),
            error=str(exc),
        )
        from app.core.config import settings
        return [0.0] * settings.embedding_dimension


def encode_batch(texts: list[str]) -> list[list[float]]:
    """
    Encode a batch of texts efficiently.

    Significantly faster than calling encode_text() in a loop.
    Use this when embedding multiple resumes or jobs at once.

    Args:
        texts: List of text strings to encode

    Returns:
        List of embedding vectors, one per input text
    """
    if not texts:
        return []

    from app.core.config import settings

    try:
        model = get_embedding_model()
        # Filter empty texts, track their positions
        non_empty = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not non_empty:
            return [[0.0] * settings.embedding_dimension] * len(texts)

        indices, valid_texts = zip(*non_empty)
        vectors = model.encode(
            list(valid_texts),
            batch_size=settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(valid_texts) > 100,
        )

        # Reconstruct full result list with zeros for empty inputs
        result = [[0.0] * settings.embedding_dimension] * len(texts)
        for idx, vector in zip(indices, vectors):
            result[idx] = vector.tolist()

        return result

    except Exception as exc:
        logger.error(
            "batch_encoding_failed",
            batch_size=len(texts),
            error=str(exc),
        )
        return [[0.0] * settings.embedding_dimension] * len(texts)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Used for in-memory comparison when pgvector is not available.
    For database-scale search, use pgvector operators instead.

    Args:
        vec_a: First embedding vector
        vec_b: Second embedding vector

    Returns:
        Similarity score between 0.0 and 1.0
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = float(np.dot(a, b) / (norm_a * norm_b))
    # Clamp to [0, 1] — normalized vectors should already be in range
    return max(0.0, min(1.0, similarity))
