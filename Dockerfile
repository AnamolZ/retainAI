FROM python:3.11-slim

# Prevent interactive prompts and Python bytecode generation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    TF_CPP_MIN_LOG_LEVEL=3 \
    PATH="/root/.local/bin:${PATH}"

# Install system dependencies: Chromium, Chromedriver, Node.js and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    chromium \
    chromium-driver \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Build frontend dependencies
WORKDIR /app/src/ui
COPY src/ui/package*.json ./
RUN npm install

# Build backend dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application source code
COPY . .

# Expose backend (8000) and frontend (5173)
EXPOSE 8000 5173

# Run both backend and frontend concurrently
CMD ["npx", "--yes", "concurrently", "/app/.venv/bin/python main.py", "cd src/ui && npm run dev -- --host 0.0.0.0 --port 5173"]