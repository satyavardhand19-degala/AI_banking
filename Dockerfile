# ── Vaani — AI Banking Intelligence Production Build ──

# Stage 1: Runtime environment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Ensure frontend paths match backend expectations
WORKDIR /app/backend

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn with Uvicorn workers
CMD gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile -
