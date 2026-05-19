"""
FastAPI backend for AstroBot RAG system.
On startup: initializes components, ingests PDF if collection is empty.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.core.config import settings
from backend.app.rag.embedder import Embedder
from backend.app.rag.ingestion import ingest_pdf
from backend.app.rag.retriever import Retriever
from backend.app.rag.generator import Generator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --- Global components (initialized in lifespan) ---
embedder: Embedder = None
retriever: Retriever = None
generator: Generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedder, retriever, generator

    logger.info("=" * 60)
    logger.info("Starting AstroBot API...")
    logger.info("=" * 60)

    # 1. Initialize embedder
    embedder = Embedder()
    logger.info("Embedder ready (all-MiniLM-L6-v2, dim=384)")

    # 2. Initialize retriever and ensure collection exists
    retriever = Retriever()
    retriever.create_collection_if_not_exists()

    # 3. Initialize generator
    generator = Generator()

    # 4. Check if collection needs ingestion
    vector_count = retriever.get_vector_count()

    if vector_count == 0:
        logger.info("Collection is empty — starting full ingestion...")

        pdf_path = os.path.join("backend", "Data", "artemis2-reference-guide.pdf")
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found at {pdf_path}")
        else:
            # Read and chunk PDF
            chunks = ingest_pdf(pdf_path)
            logger.info(f"Created {len(chunks)} chunks from PDF")

            # Embed all chunks
            texts = [c["text"] for c in chunks]
            logger.info("Embedding chunks...")

            # Embed in batches and log progress
            all_embeddings = []
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_embeddings = embedder.embed_texts(batch)
                all_embeddings.extend(batch_embeddings)
                logger.info(f"Embedded {min(i + batch_size, len(texts))}/{len(texts)} chunks")

            # Upsert to Qdrant
            retriever.upsert_documents(chunks, all_embeddings)
            logger.info(f"Ingestion complete: {len(chunks)} total chunks")
    else:
        logger.info(f"Collection ready with {vector_count} vectors — skipping ingestion")

    logger.info("=" * 60)
    logger.info(f"AstroBot API running on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
    logger.info("=" * 60)

    yield

    logger.info("Shutting down AstroBot API")


app = FastAPI(title="AstroBot API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # 1. Embed the query
        query_embedding = embedder.embed_single(query)

        # 2. Search Qdrant
        results = retriever.search(query_embedding, top_k=6)

        # 3. Generate answer
        answer = generator.generate(query, results)

        # 4. Build sources list
        sources = []
        for r in results:
            sources.append({
                "page": r["metadata"].get("page_number", "?"),
                "score": r["score"],
                "chunk_index": r["metadata"].get("chunk_index", "?"),
            })

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    count = retriever.get_vector_count() if retriever else 0
    return {"status": "ok", "vectors": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
    )
