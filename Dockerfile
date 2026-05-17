# Root Dockerfile — builds backend + frontend into a single Cloud Run container
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast pip alternative)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy frontend source
COPY frontend/ ./frontend/

# Create writable static directory for generated cards
RUN mkdir -p backend/static/cards

WORKDIR /app/backend

EXPOSE 8080

# Cloud Run provides PORT env var; default to 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
