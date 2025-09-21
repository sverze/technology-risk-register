# FastAPI-only Dockerfile for Technology Risk Register Backend
# Frontend is now deployed separately to Cloud Storage + CDN

# Backend build stage
FROM python:3.12-slim as backend-builder

# Install UV and system deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files and create dummy README
COPY pyproject.toml uv.lock ./
RUN echo "# Technology Risk Register" > README.md

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim as production

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Copy virtual environment from builder
COPY --from=backend-builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

# Fix ownership
RUN chown -R app:app /app

# Expose port
ENV PORT=8080
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to non-root user
USER app

# Start the FastAPI application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]