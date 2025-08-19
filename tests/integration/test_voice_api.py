"""
Integration tests for voice API endpoints.
"""

import pytest
import tempfile
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.nlp_match_event_reporter.main import app
from src.nlp_match_event_reporter.models.database import Base, VoiceProcessingLog
from src.nlp_match_event_reporter.core.database import get_database_session


@pytest.fixture
def test_db():
    """Create a test database."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal


@pytest.fixture
def client(test_db):
    """Create a test client with database override."""
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing."""
    # Create a simple WAV-like file
    audio_data = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00" + b"\x00" * 100
    
    # Create a file-like object
    audio_file = io.BytesIO(audio_data)
    audio_file.name = "test_audio.wav"
    
    return audio_file


class TestVoiceTranscriptionAPI:
    """Test voice transcription API endpoints."""
    
    def test_transcribe_audio_success(self, client, sample_audio_file):
        """Test successful audio transcription."""
        # Mock Whisper service
        with patch('src.nlp_match_event_reporter.services.voice_processing.whisper_service') as mock_whisper:
            mock_result = MagicMock()
            mock_result.text = "Test transcription result"
            mock_result.confidence = 0.95
            mock_result.language = "sv"
            mock_result.processing_time = 1.2
            mock_whisper.transcribe_audio.return_value = mock_result
            
            # Make request
            response = client.post(
                "/api/v1/voice/transcribe",
                files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")},
                data={"language": "sv"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["text"] == "Test transcription result"
            assert data["confidence"] == 0.95
            assert data["language"] == "sv"
            assert data["duration"] == 1.2
            assert "detected_events" in data
    
    def test_transcribe_audio_invalid_file_type(self, client):
        """Test transcription with invalid file type."""
        # Create a text file instead of audio
        text_file = io.BytesIO(b"This is not audio")
        text_file.name = "test.txt"
        
        response = client.post(
            "/api/v1/voice/transcribe",
            files={"audio_file": ("test.txt", text_file, "text/plain")},
            data={"language": "sv"}
        )
        
        assert response.status_code == 400
        assert "audio file" in response.json()["detail"]
    
    def test_transcribe_audio_with_match_id(self, client, sample_audio_file):
        """Test transcription with match ID for event extraction."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.whisper_service') as mock_whisper:
            mock_result = MagicMock()
            mock_result.text = "Mål av Erik Karlsson i femtonde minuten"
            mock_result.confidence = 0.92
            mock_result.language = "sv"
            mock_result.processing_time = 1.5
            mock_whisper.transcribe_audio.return_value = mock_result
            
            response = client.post(
                "/api/v1/voice/transcribe",
                files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")},
                data={"language": "sv", "match_id": "1"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["text"] == "Mål av Erik Karlsson i femtonde minuten"
            assert "detected_events" in data
    
    def test_transcribe_audio_service_error(self, client, sample_audio_file):
        """Test transcription when service fails."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.whisper_service') as mock_whisper:
            from src.nlp_match_event_reporter.core.exceptions import VoiceProcessingError
            mock_whisper.transcribe_audio.side_effect = VoiceProcessingError("Transcription failed")
            
            response = client.post(
                "/api/v1/voice/transcribe",
                files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")},
                data={"language": "sv"}
            )
            
            assert response.status_code == 500
            assert "Transcription failed" in response.json()["detail"]


class TestTextToSpeechAPI:
    """Test text-to-speech API endpoints."""
    
    def test_text_to_speech_success(self, client):
        """Test successful text-to-speech conversion."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.tts_service') as mock_tts:
            mock_result = MagicMock()
            mock_result.audio_data = b"fake audio data"
            mock_result.duration = 3.2
            mock_result.processing_time = 0.8
            mock_tts.synthesize_speech.return_value = mock_result
            
            response = client.post(
                "/api/v1/voice/speak",
                data={
                    "text": "Hello world",
                    "voice": "default",
                    "speed": "1.0"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["message"] == "Text converted to speech successfully"
            assert data["duration"] == 3.2
            assert data["voice_used"] == "default"
            assert data["speed_used"] == 1.0
            assert "audio_url" in data
    
    def test_text_to_speech_custom_parameters(self, client):
        """Test TTS with custom voice and speed parameters."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.tts_service') as mock_tts:
            mock_result = MagicMock()
            mock_result.audio_data = b"fake audio data"
            mock_result.duration = 2.5
            mock_result.processing_time = 0.6
            mock_tts.synthesize_speech.return_value = mock_result
            
            response = client.post(
                "/api/v1/voice/speak",
                data={
                    "text": "Custom voice test",
                    "voice": "female",
                    "speed": "1.5"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["voice_used"] == "female"
            assert data["speed_used"] == 1.5
    
    def test_text_to_speech_invalid_speed(self, client):
        """Test TTS with invalid speed parameter."""
        response = client.post(
            "/api/v1/voice/speak",
            data={
                "text": "Test text",
                "speed": "3.5"  # Above maximum of 2.0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_text_to_speech_service_error(self, client):
        """Test TTS when service fails."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.tts_service') as mock_tts:
            from src.nlp_match_event_reporter.core.exceptions import VoiceProcessingError
            mock_tts.synthesize_speech.side_effect = VoiceProcessingError("TTS synthesis failed")
            
            response = client.post(
                "/api/v1/voice/speak",
                data={"text": "Test text"}
            )
            
            assert response.status_code == 500
            assert "TTS synthesis failed" in response.json()["detail"]


class TestHotwordDetectionAPI:
    """Test hotword detection API endpoints."""
    
    def test_hotword_status_inactive(self, client):
        """Test hotword status when inactive."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = False
            mock_hotword._initialized = True
            
            response = client.get("/api/v1/voice/hotword/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["active"] is False
            assert data["model_loaded"] is True
            assert "sensitivity" in data
            assert "detections_today" in data
    
    def test_hotword_status_active(self, client):
        """Test hotword status when active."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = True
            mock_hotword._initialized = True
            
            response = client.get("/api/v1/voice/hotword/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["active"] is True
            assert data["model_loaded"] is True
    
    def test_start_hotword_detection(self, client):
        """Test starting hotword detection."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = False
            mock_hotword.start_listening.return_value = None
            
            response = client.post(
                "/api/v1/voice/hotword/start",
                data={
                    "keywords": "referee,domare",
                    "sensitivity": "0.7"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "active"
            assert data["keywords"] == ["referee", "domare"]
            assert data["sensitivity"] == 0.7
            mock_hotword.start_listening.assert_called_once()
    
    def test_start_hotword_detection_already_active(self, client):
        """Test starting hotword detection when already active."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = True
            
            response = client.post("/api/v1/voice/hotword/start")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "active"
            assert "already active" in data["message"]
    
    def test_stop_hotword_detection(self, client):
        """Test stopping hotword detection."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = True
            mock_hotword.stop_listening.return_value = None
            
            response = client.post("/api/v1/voice/hotword/stop")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "inactive"
            mock_hotword.stop_listening.assert_called_once()
    
    def test_stop_hotword_detection_already_inactive(self, client):
        """Test stopping hotword detection when already inactive."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.hotword_service') as mock_hotword:
            mock_hotword.is_listening = False
            
            response = client.post("/api/v1/voice/hotword/stop")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "inactive"
            assert "already inactive" in data["message"]


class TestVoiceLogging:
    """Test voice processing logging functionality."""
    
    def test_transcription_logging(self, client, sample_audio_file, test_db):
        """Test that transcription operations are logged to database."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.whisper_service') as mock_whisper:
            mock_result = MagicMock()
            mock_result.text = "Logged transcription"
            mock_result.confidence = 0.88
            mock_result.language = "sv"
            mock_result.processing_time = 1.0
            mock_whisper.transcribe_audio.return_value = mock_result
            
            response = client.post(
                "/api/v1/voice/transcribe",
                files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")},
                data={"language": "sv"}
            )
            
            assert response.status_code == 200
            
            # Check that log entry was created
            db = test_db()
            log_entry = db.query(VoiceProcessingLog).filter_by(operation_type="transcribe").first()
            
            assert log_entry is not None
            assert log_entry.status == "success"
            assert log_entry.output_data == "Logged transcription"
            assert log_entry.confidence_score == 0.88
            
            db.close()
    
    def test_tts_logging(self, client, test_db):
        """Test that TTS operations are logged to database."""
        with patch('src.nlp_match_event_reporter.services.voice_processing.tts_service') as mock_tts:
            mock_result = MagicMock()
            mock_result.audio_data = b"fake audio"
            mock_result.duration = 2.0
            mock_result.processing_time = 0.5
            mock_tts.synthesize_speech.return_value = mock_result
            
            response = client.post(
                "/api/v1/voice/speak",
                data={"text": "Logged TTS test"}
            )
            
            assert response.status_code == 200
            
            # Check that log entry was created
            db = test_db()
            log_entry = db.query(VoiceProcessingLog).filter_by(operation_type="tts").first()
            
            assert log_entry is not None
            assert log_entry.status == "success"
            assert log_entry.input_data == "Logged TTS test"
            assert log_entry.processing_time_ms == 500
            
            db.close()
