# FastAPI-only Dockerfile for Technology Risk Register Backend
# Frontend is now deployed separately to Cloud Storage + CDN

# Backend build stage
FROM python:3.12-slim as backend-builder

# Install UV and system deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Optionally install a corporate CA certificate (e.g. for GlobalProtect SASE SSL inspection).
# Mount the cert as a build secret: --secret id=ca_cert,src=/path/to/cert.pem
RUN --mount=type=secret,id=ca_cert \
    if [ -f /run/secrets/ca_cert ]; then \
        apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
        rm -rf /var/lib/apt/lists/* && \
        cp /run/secrets/ca_cert /usr/local/share/ca-certificates/corporate-ca.crt && \
        update-ca-certificates; \
    fi

# Copy dependency files and create dummy README
COPY pyproject.toml uv.lock ./
RUN echo "# Technology Risk Register" > README.md

# Create virtual environment and install dependencies.
# UV_NATIVE_TLS=1 makes uv use OpenSSL (system trust store) instead of bundled rustls,
# so it respects the corporate CA cert installed above.
RUN UV_NATIVE_TLS=1 uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim as production

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Optionally install corporate CA cert for runtime package operations (e.g. uv run).
# Same secret as the builder stage — no-op in CI where the secret is absent.
RUN --mount=type=secret,id=ca_cert \
    if [ -f /run/secrets/ca_cert ]; then \
        cp /run/secrets/ca_cert /usr/local/share/ca-certificates/corporate-ca.crt && \
        update-ca-certificates; \
    fi

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

# Start the FastAPI application directly (not via uv run for faster startup)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
