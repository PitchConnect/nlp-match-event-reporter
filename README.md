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

# Set up development environment
./scripts/setup_dev.sh

# Start services
docker-compose up -d
```

### Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
# Edit .env with your FOGIS credentials and preferences
```

## 📋 Development Milestones

- [x] **Repository Setup** - Project structure and CI/CD pipeline
- [ ] **Python Project Scaffolding** - Basic project structure and dependencies
- [ ] **FOGIS API Integration** - Match data fetching and event reporting
- [ ] **NLP Proof of Concept** - Text-based event interface
- [ ] **Hotword Activation** - Voice activation using Porcupine
- [ ] **Speech-to-Text Integration** - Whisper-based transcription
- [ ] **Text-to-Speech Implementation** - Kokoro TTS feedback

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
