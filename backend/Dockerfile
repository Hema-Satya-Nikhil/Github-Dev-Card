# backend/Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies using uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
# Ensure google-adk is also installed (added during debugging)
RUN uv pip install --system google-adk google-genai

# Copy source code
COPY . .

# Ensure static directories exist
RUN mkdir -p static/cards

EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
