#!/bin/bash
# Railway startup script - handles dynamic PORT injection

# Use PORT from Railway environment, default to 8000 if not set
PORT=${PORT:-8000}

echo "🚀 Starting Gunicorn on port $PORT..."

# Start Gunicorn with Railway's PORT
exec gunicorn \
    --chdir src \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --timeout 300 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    gender_detection.app:app
