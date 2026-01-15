#!/bin/bash
# Production startup with health checks
echo "🚀 WaspWatch v1.0.3 starting..."

# Pre-flight checks
uvicorn --version
duckdb --version

# Start FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

