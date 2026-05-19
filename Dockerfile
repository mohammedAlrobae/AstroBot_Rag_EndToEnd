FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY backend /app/backend
COPY frontend /app/frontend
COPY chainlit.md /app/chainlit.md
COPY .env.example /app/.env.example

RUN mkdir -p /app/backend/Data

ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000
ENV API_URL=http://127.0.0.1:8000

EXPOSE 7860

RUN printf '#!/bin/bash\nset -e\necho "Starting FastAPI backend..."\nuvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &\nBACKEND_PID=$!\necho "Waiting for backend to be ready..."\nfor i in $(seq 1 30); do\n  if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then\n    echo "Backend is ready!"\n    break\n  fi\n  echo "Attempt $i: backend not ready yet..."\n  sleep 2\ndone\necho "Starting Chainlit frontend..."\nexec chainlit run frontend/app.py --host 0.0.0.0 --port 7860\n' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
