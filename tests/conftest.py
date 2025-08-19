"""
Pytest configuration and fixtures for NLP Match Event Reporter tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from src.nlp_match_event_reporter.main import app
from src.nlp_match_event_reporter.core.config import settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_fogis_client():
    """Create a mock FOGIS API client."""
    mock_client = Mock()
    mock_client.fetch_matches_list_json.return_value = [
        {
            "matchid": 123456,
            "hemmalag": "AIK",
            "bortalag": "Hammarby",
            "datum": "2025-08-20",
            "tid": "19:00",
            "arena": "Friends Arena",
            "status": "scheduled"
        }
    ]
    return mock_client


@pytest.fixture
def sample_match_data():
    """Sample match data for testing."""
    return {
        "id": 123456,
        "home_team": "AIK",
        "away_team": "Hammarby",
        "date": "2025-08-20",
        "time": "19:00",
        "venue": "Friends Arena",
        "status": "scheduled",
        "competition": "Allsvenskan"
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "match_id": 123456,
        "event_type": "goal",
        "minute": 15,
        "player_name": "Erik Karlsson",
        "team": "AIK",
        "description": "Goal scored by Erik Karlsson"
    }


@pytest.fixture
def mock_whisper_service():
    """Create a mock Whisper transcription service."""
    mock_service = Mock()
    mock_service.transcribe.return_value = {
        "text": "Mål av Erik Karlsson i femtonde minuten",
        "confidence": 0.95,
        "language": "sv",
        "duration": 2.5
    }
    return mock_service


@pytest.fixture
def mock_tts_service():
    """Create a mock TTS service."""
    mock_service = Mock()
    mock_service.synthesize.return_value = {
        "audio_url": "/tmp/tts_output.wav",
        "duration": 3.2
    }
    return mock_service


@pytest.fixture
def mock_hotword_service():
    """Create a mock hotword detection service."""
    mock_service = Mock()
    mock_service.is_active.return_value = True
    mock_service.get_status.return_value = {
        "active": True,
        "sensitivity": 0.5,
        "model_loaded": True,
        "detections_today": 15
    }
    return mock_service


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def audio_file_mock():
    """Mock audio file for testing."""
    mock_file = Mock()
    mock_file.filename = "test_audio.wav"
    mock_file.content_type = "audio/wav"
    mock_file.read.return_value = b"fake_audio_data"
    return mock_file
