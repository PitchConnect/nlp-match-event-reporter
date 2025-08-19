
# NLP Match Event Reporter

Real-time soccer match event reporting system using natural language processing and voice interaction for hands-free operation during live matches.

## 🎯 Overview

This system enables live match event reporting through speech during games, with the long-term goal of integrating with refereeing communication equipment for hands-free operation. The system fetches and posts data to match event servers while providing speech-to-text transcription and text-to-speech feedback.

## ✨ Features

- **Voice-Activated Reporting** - Hotword activation to minimize resource usage
- **Speech-to-Text** - Accurate transcription using containerized Whisper
- **Text-to-Speech** - System feedback using Kokoro TTS
- **FOGIS Integration** - Direct integration with Swedish Football Association API
- **Microservices Architecture** - Scalable, containerized components
- **Real-time Processing** - Low-latency event reporting and feedback

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hotword       │    │   Speech-to-    │    │   NLP Event     │
│   Detection     │───▶│   Text Service  │───▶│   Processor     │
│   (Porcupine)   │    │   (Whisper)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Text-to-      │◀───│   FOGIS API     │◀────────────┘
│   Speech        │    │   Client        │
│   (Kokoro)      │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Microphone access for voice input
- FOGIS API credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/PitchConnect/nlp-match-event-reporter.git
cd nlp-match-event-reporter

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run the application
uvicorn src.nlp_match_event_reporter.main:app --reload
```

### Configuration

Create a `.env` file with your configuration:

```bash
# Database
DATABASE_URL=sqlite:///./nlp_reporter.db

# FOGIS API
FOGIS_BASE_URL=https://fogis.svenskfotboll.se
FOGIS_USERNAME=your_username
FOGIS_PASSWORD=your_password

# Voice Processing
PICOVOICE_ACCESS_KEY=your_picovoice_key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 📋 Development Milestones

- [x] **Repository Setup** - Project structure and CI/CD pipeline
- [x] **Python Project Scaffolding** - Complete project structure with FastAPI, SQLAlchemy, and testing framework
- [x] **Database Models & Migrations** - Comprehensive data models with Alembic migrations
- [x] **API Endpoint Implementation** - Full CRUD operations with database integration
- [x] **Testing Framework** - Comprehensive test suite with 80% coverage
- [x] **Voice Processing Integration** - Whisper STT, Kokoro TTS, and Porcupine hotword detection
- [x] **FOGIS API Integration** - Complete client with match data sync and event reporting

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, FastAPI
- **Voice Processing**: Picovoice Porcupine, OpenAI Whisper, Kokoro TTS
- **API Integration**: FOGIS API Client (PitchConnect)
- **Storage**: SQLite (development), PostgreSQL (production)
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [Voice Processing Setup](docs/voice-setup.md)

## 🤝 Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PitchConnect](https://github.com/PitchConnect) - Organization and FOGIS API client
- [Picovoice](https://picovoice.ai/) - Hotword detection technology
- [OpenAI](https://openai.com/) - Whisper speech recognition
- Swedish Football Association - FOGIS API access

---

**Made with ⚽ for the football community**
