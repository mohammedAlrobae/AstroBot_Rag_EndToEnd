"""
Embedding generation using local sentence-transformers model.
Model: all-MiniLM-L6-v2 (384 dimensions, CPU-only)
"""

import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DIMENSION = 384
MODEL_NAME = "all-MiniLM-L6-v2"

# Singleton model instance
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading sentence-transformers model '{MODEL_NAME}'...")
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded successfully.")
    return _model


class Embedder:
    """Generates 384-dimensional embeddings using all-MiniLM-L6-v2."""

    def __init__(self):
        self.model = _get_model()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts. Returns list of 384-dim vectors."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text string. Returns one 384-dim vector."""
        embedding = self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)
        return embedding[0].tolist()
