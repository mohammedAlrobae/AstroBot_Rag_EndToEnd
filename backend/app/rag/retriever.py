"""
Qdrant vector retriever.
Simple semantic search — no BM25, no hybrid.
"""

import logging
import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

VECTOR_SIZE = 384
SCORE_THRESHOLD = 0.50
BATCH_SIZE = 100


class Retriever:
    """Connects to Qdrant Cloud and performs simple vector search."""

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60,
        )
        self.collection_name = settings.QDRANT_COLLECTION
        logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")

    def create_collection_if_not_exists(self) -> None:
        """Create the collection only if it doesn't already exist."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name in existing:
            logger.info(f"Collection '{self.collection_name}' already exists.")
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        logger.info(f"Created collection '{self.collection_name}' (dim={VECTOR_SIZE}, cosine)")

    def get_vector_count(self) -> int:
        """Return the number of vectors in the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0

    def upsert_documents(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        """Upload chunks + embeddings to Qdrant in batches of 100."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")

        total = len(chunks)
        uploaded = 0

        for i in range(0, total, BATCH_SIZE):
            batch_chunks = chunks[i : i + BATCH_SIZE]
            batch_embeds = embeddings[i : i + BATCH_SIZE]

            points = []
            for chunk, emb in zip(batch_chunks, batch_embeds):
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=emb,
                        payload={
                            "text": chunk["text"],
                            "metadata": chunk["metadata"],
                        },
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            uploaded += len(points)
            logger.info(f"Upserted {uploaded}/{total} chunks")

        logger.info(f"Upsert complete: {total} vectors in '{self.collection_name}'")

    def search(self, query_embedding: list[float], top_k: int = 6) -> list[dict]:
        """
        Search Qdrant for similar vectors.
        Returns chunks with score >= 0.50.
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.50
        )

        return [
            {
                "text": r.payload.get("text", ""),
                "metadata": r.payload.get("metadata", {}),
                "score": r.score
            }
            for r in results
        ]
