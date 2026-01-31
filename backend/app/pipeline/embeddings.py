"""
Embeddings pipeline for generating semantic vectors.
"""
from typing import List, Optional
import structlog

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = structlog.get_logger(__name__)

# Global model instance (lazy loading)
_model: Optional[SentenceTransformer] = None


async def get_model() -> SentenceTransformer:
    """
    Get or create the sentence transformer model.
    Uses lazy loading to avoid loading on import.
    """
    global _model

    if _model is None:
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is required for embeddings")

        logger.info("Loading sentence transformer model")
        # Using a smaller, efficient model for production
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")

    return _model


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text.

    Args:
        text: Input text to embed

    Returns:
        List of float values representing the embedding vector
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding")
        return []

    try:
        model = await get_model()
        embedding = model.encode(text, convert_to_numpy=True)

        # Convert to list for JSON serialization
        embedding_list = embedding.tolist()

        logger.info("Embedding generated", text_length=len(text), vector_dim=len(embedding_list))
        return embedding_list

    except Exception as e:
        logger.error("Embedding generation failed", error=str(e), text_length=len(text))
        return []


async def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (0-1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        logger.warning("Invalid vectors for similarity calculation")
        return 0.0

    try:
        import numpy as np

        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Ensure result is between 0 and 1
        similarity = max(0.0, min(1.0, similarity))

        logger.debug("Cosine similarity calculated", similarity=similarity)
        return float(similarity)

    except Exception as e:
        logger.error("Cosine similarity calculation failed", error=str(e))
        return 0.0


async def find_similar_embeddings(
    query_embedding: List[float],
    candidate_embeddings: List[List[float]],
    top_k: int = 10
) -> List[tuple]:
    """
    Find most similar embeddings to a query vector.

    Args:
        query_embedding: Query vector
        candidate_embeddings: List of candidate vectors
        top_k: Number of top results to return

    Returns:
        List of (index, similarity_score) tuples
    """
    if not query_embedding or not candidate_embeddings:
        return []

    try:
        similarities = []

        for i, candidate in enumerate(candidate_embeddings):
            similarity = await calculate_cosine_similarity(query_embedding, candidate)
            similarities.append((i, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k results
        return similarities[:top_k]

    except Exception as e:
        logger.error("Similar embedding search failed", error=str(e))
        return []


def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize embedding vector to unit length.

    Args:
        embedding: Input embedding vector

    Returns:
        Normalized embedding vector
    """
    if not embedding:
        return embedding

    try:
        import numpy as np

        vec = np.array(embedding)
        norm = np.linalg.norm(vec)

        if norm == 0:
            return embedding

        normalized = vec / norm
        return normalized.tolist()

    except Exception as e:
        logger.error("Embedding normalization failed", error=str(e))
        return embedding
