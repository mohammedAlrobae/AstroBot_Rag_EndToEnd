FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/backend/app/rag /app/backend/app/core /app/frontend

# Copy application files
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env.example /app/.env.example

# Expose ports
EXPOSE 7860
EXPOSE 8000

# Start both FastAPI and Chainlit
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${FASTAPI_PORT:-8000} & chainlit run frontend/app.py --host 0.0.0.0 --port ${CHAINLIT_PORT:-7860}
