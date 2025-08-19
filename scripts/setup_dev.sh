#!/bin/bash

# Development environment setup script for NLP Match Event Reporter

set -e

echo "🚀 Setting up NLP Match Event Reporter development environment..."

# Check if Python 3.9+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install -e ".[dev,voice,tts]"

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs models/porcupine models/whisper models/tts

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please edit .env file with your FOGIS credentials"
fi

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker found - you can use docker-compose for full stack development"
    
    # Pull required Docker images
    echo "📥 Pulling Docker images..."
    docker pull postgres:15-alpine
    docker pull redis:7-alpine
    docker pull ghcr.io/pitchconnect/fogis-api-client-python:latest
else
    echo "⚠️ Docker not found - some features may not be available"
fi

# Create initial database migration (placeholder)
echo "🗄️ Setting up database structure..."
# TODO: Add Alembic migration commands when database models are implemented

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short || echo "⚠️ Some tests failed - this is expected in early development"
else
    echo "⚠️ pytest not found - skipping test run"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your FOGIS credentials"
echo "2. Start development server: uvicorn src.nlp_match_event_reporter.main:app --reload"
echo "3. Or use Docker: docker-compose up -d"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Happy coding! ⚽"
