---
title: AstroBot RAG EndToEnd
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🚀 AstroBot — Astronaut Mission Control Assistant

> A production-ready RAG chatbot for astronauts powered by the official NASA Artemis II Reference Guide (138 pages).

## 🌐 Live Demo

**Try it now, no setup required:**

👉 [https://huggingface.co/spaces/MO-ALROBAE2000/AstroBot-RAG-EndToEnd](https://huggingface.co/spaces/MO-ALROBAE2000/AstroBot-RAG-EndToEnd)

---

## 💡 What is AstroBot?

AstroBot is a specialized AI assistant that answers questions about the NASA Artemis II mission. It uses Retrieval-Augmented Generation (RAG) to search the official Artemis II Reference Guide and return accurate, cited answers — including page numbers.

**Example questions you can ask:**
- "Who are the crew members of Artemis II?"
- "What is the mission duration and trajectory?"
- "Describe the Orion spacecraft systems"
- "What happens during translunar injection?"
- "Emergency: cabin pressure dropping"

---

## ⚙️ How it works
User Question
↓
Embed query (all-MiniLM-L6-v2)
↓
Search Qdrant (776 vectors from 138-page PDF)
↓
Retrieve top 6 relevant chunks
↓
Generate answer with Groq (llama-3.3-70b)
↓
Return answer + page citations

---

## 🛠️ Stack

| Component | Technology |
|-----------|-----------|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (local, free) |
| LLM | Groq `llama-3.3-70b-versatile` |
| Vector DB | Qdrant Cloud |
| Backend | FastAPI |
| Frontend | Chainlit |
| Deployment | Hugging Face Spaces (Docker) |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/mohammedAlrobae/AstroBot_Rag_EndToEnd.git
cd AstroBot_Rag_EndToEnd

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Fill in your API keys in .env

# 5. Run backend (Terminal 1)
python -m backend.app.main

# 6. Run frontend (Terminal 2)
chainlit run frontend/app.py --port 7860
```

Open [http://localhost:7860](http://localhost:7860)

---

## 🔑 Environment Variables

```env
GROQ_API_KEY=        # https://console.groq.com
QDRANT_URL=          # https://cloud.qdrant.io
QDRANT_API_KEY=      # https://cloud.qdrant.io
QDRANT_COLLECTION=astrobot
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

---

## 📄 Data Source

**NASA Artemis II Reference Guide** — Official mission reference document covering:
- Mission overview and objectives
- Crew members and roles
- SLS and Orion spacecraft systems
- Launch and trajectory details
- Ground operations
- Science objectives

---

## 🏗️ Project Structure
AstroBot_RAG/
├── backend/
│   ├── Data/
│   │   └── artemis2-reference-guide.pdf
│   └── app/
│       ├── core/config.py
│       ├── main.py
│       └── rag/
│           ├── embedder.py
│           ├── generator.py
│           ├── ingestion.py
│           └── retriever.py
├── frontend/
│   └── app.py
├── Dockerfile
├── requirements.txt
└── .env.example

---

*Built with ❤️ using FastAPI, Chainlit, Qdrant, and Groq*
