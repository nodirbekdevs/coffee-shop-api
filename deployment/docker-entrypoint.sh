#!/bin/bash

# ✅ Load environment variables from .env (optional)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# ✅ Set defaults (used if not defined in .env)
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

# ✅ Set PYTHONPATH so Alembic & app can resolve imports
export PYTHONPATH=$(pwd)

# ✅ Run Alembic migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

# ✅ Start FastAPI app using Gunicorn + Uvicorn workers
echo "🚀 Starting FastAPI on $HOST:$PORT..."
gunicorn app.app:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers $WORKERS --timeout 90 --log-level info --access-logfile -
