#!/bin/bash

# Docker entrypoint script for combined frontend/backend container
# Used for production Cloud Run deployment

set -e

# Start nginx in the background
echo "Starting nginx..."
nginx &

# Wait a moment for nginx to start
sleep 2

# Start FastAPI backend
echo "Starting FastAPI backend..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8008
