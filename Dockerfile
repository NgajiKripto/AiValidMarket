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

EXPOSE 3000 5001

CMD ["npm", "run", "dev"]
