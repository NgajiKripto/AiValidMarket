FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy uv from astral-sh image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for caching
COPY package.json ./
COPY frontend/package.json frontend/
COPY backend/pyproject.toml backend/

# Install dependencies
RUN npm ci
RUN npm ci --prefix frontend
RUN cd backend && uv sync --frozen

# Copy source code
COPY . .

# Build frontend for production
RUN cd frontend && npm run build

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

CMD ["sh", "-c", "cd /app/backend && uv run gunicorn --bind 0.0.0.0:5001 --workers 2 --threads 4 'app:create_app()'"]
