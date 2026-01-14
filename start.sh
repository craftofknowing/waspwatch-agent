#!/usr/bin/env bash
set -e

# Optional: log configuration
echo "Starting WASP detector green agent..."

# Start FastAPI controller
uvicorn app.main:app --host 0.0.0.0 --port 8000

