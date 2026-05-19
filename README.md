---
title: AstroBot RAG EndToEnd
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# AstroBot — Astronaut Mission Control Assistant

A production-ready RAG chatbot for astronauts powered by the NASA Artemis II Reference Guide.

## What it does
AstroBot answers questions about the Artemis II mission by retrieving relevant information directly from the official NASA Artemis II Reference Guide (138 pages) stored in a Qdrant vector database.

## Stack
- Embeddings: sentence-transformers all-MiniLM-L6-v2 (local, free)
- LLM: Groq llama-3.3-70b-versatile
- Vector DB: Qdrant Cloud
- Backend: FastAPI
- Frontend: Chainlit

## Setup
1. Clone the repo
2. Create virtual environment: python -m venv venv
3. Activate: venv\Scripts\activate
4. Install: pip install -r requirements.txt
5. Copy .env.example to .env and fill in your API keys
6. Run backend: python -m backend.app.main
7. Run frontend: chainlit run frontend/app.py --port 7860

## Environment Variables
GROQ_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=astrobot
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
