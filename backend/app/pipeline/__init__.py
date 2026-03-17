"""
Pipeline package initialization.
"""
from .text_extraction import text_extraction_service
from .skill_extraction import skill_extractor

# Lazy-load embedding-dependent modules to avoid numpy startup hang
# on Windows/MINGW. They are still imported on first use.
try:
    from .embeddings import embedding_service
    from .matching import matching_engine
except Exception:
    embedding_service = None
    matching_engine = None

__all__ = [
    "text_extraction_service",
    "skill_extractor",
    "embedding_service",
    "matching_engine",
]
