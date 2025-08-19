# Multi-stage Dockerfile for NLP Match Event Reporter

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -e ".[dev,voice,tts]"

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs models/porcupine models/whisper models/tts

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "src.nlp_match_event_reporter.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Install production dependencies only
RUN pip install -e ".[voice,tts]"

# Copy source code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories and set permissions
RUN mkdir -p logs models/porcupine models/whisper models/tts && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "src.nlp_match_event_reporter.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Testing stage
FROM development as testing

# Install test dependencies
RUN pip install pytest pytest-asyncio pytest-cov

# Copy test files
COPY tests/ ./tests/

# Run tests
CMD ["pytest", "tests/", "-v", "--cov=src/nlp_match_event_reporter"]
