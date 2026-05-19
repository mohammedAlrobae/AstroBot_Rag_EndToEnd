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

EXPOSE 7860 8000

ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000
ENV API_URL=http://localhost:8000

RUN printf '#!/bin/bash\nset -e\nuvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &\necho "Waiting for backend..."\nsleep 10\nexec chainlit run frontend/app.py --host 0.0.0.0 --port 7860\n' > /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/bin/bash", "/app/start.sh"]
