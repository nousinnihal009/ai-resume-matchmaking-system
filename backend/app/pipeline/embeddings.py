"""
Embeddings pipeline for text vectorization.
"""
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


def _get_numpy():
    """Lazy import numpy to avoid startup hang on Windows/MINGW builds."""
    import numpy as np
    return np


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize the embedding service."""
        self.model = None
        self.dimension = 384  # Default dimension for sentence-transformers models

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embeddings for text.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
        """
        try:
            if not text or not text.strip():
                return None

            if not self.model:
                # Return a placeholder embedding for development
                return self._generate_placeholder_embedding(text)

            return self._generate_placeholder_embedding(text)

        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return None

    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)

    def _generate_placeholder_embedding(self, text: str) -> List[float]:
        """
        Generate a placeholder embedding for development/testing.

        This creates a deterministic but meaningless embedding based on text hash.
        In production, this would be replaced with real embeddings.
        """
        try:
            np = _get_numpy()

            # Create a deterministic embedding based on text content
            text_hash = hash(text) % 1000000
            np.random.seed(text_hash)

            # Generate a random vector with fixed seed for consistency
            embedding = np.random.normal(0, 1, self.dimension)

            # Normalize to unit vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating placeholder embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0

            np = _get_numpy()

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

            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Euclidean distance
        """
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return float('inf')

            np = _get_numpy()

            v1 = np.array(vec1)
            v2 = np.array(vec2)

            return np.linalg.norm(v1 - v2)

        except Exception as e:
            logger.error(f"Error calculating Euclidean distance: {e}")
            return float('inf')

    def dot_product(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate dot product between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Dot product
        """
        try:
            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0

            np = _get_numpy()

            return np.dot(vec1, vec2)

        except Exception as e:
            logger.error(f"Error calculating dot product: {e}")
            return 0.0


# Global embedding service instance
embedding_service = EmbeddingService()
