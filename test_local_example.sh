#!/bin/bash

# Example script showing how to run integration tests locally
# This demonstrates the complete workflow

set -e

echo "🚀 Technology Risk Register - Local Integration Test Example"
echo "==========================================================="

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --group test

# Start the application in background
echo "🏃 Starting the application server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait a moment for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Run integration tests
echo "🧪 Running integration tests..."
python run_integration_tests.py

echo "✅ Integration tests completed successfully!"
