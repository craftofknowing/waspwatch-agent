#!/usr/bin/env bash
set -euo pipefail

echo "Starting WaspWatch green agent..."

# Set PYTHONPATH IMMEDIATELY (before any Python)
export PYTHONPATH=/app:/app/app:"${PYTHONPATH:-}"

# Pre-verify imports
python -c "
import sys; sys.path.extend(['\$PYTHONPATH'.split(':')]);
from orchestrator import RealOrchestrator;
print('✅ Orchestrator pre-loaded')
" || { echo "❌ Orchestrator import failed"; exit 1; }

cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

