"""
Unit tests for voice processing services.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.nlp_match_event_reporter.services.voice_processing import (
    WhisperService,
    KokoroTTSService,
    PorcupineHotwordService,
    TranscriptionResult,
    TTSResult,
    encode_audio_base64,
    decode_audio_base64,
    save_audio_file,
)
from src.nlp_match_event_reporter.core.exceptions import VoiceProcessingError


@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing."""
    # Create a simple WAV-like header + some data
    return b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00" + b"\x00" * 100


class TestWhisperService:
    """Test cases for WhisperService."""
    
    @pytest.fixture
    def whisper_service(self):
        """Create a WhisperService instance."""
        return WhisperService()
    
    def test_initialization(self, whisper_service):
        """Test WhisperService initialization."""
        assert whisper_service.model is None
        assert whisper_service.model_size == "base"
        assert not whisper_service._initialized
    
    @pytest.mark.asyncio
    async def test_initialize_without_whisper(self, whisper_service):
        """Test initialization when Whisper is not installed."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'whisper'")):
            with pytest.raises(VoiceProcessingError, match="Whisper not installed"):
                await whisper_service.initialize()
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, whisper_service):
        """Test successful initialization."""
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model
        
        with patch.dict('sys.modules', {'whisper': mock_whisper}):
            await whisper_service.initialize()
            
            assert whisper_service._initialized
            assert whisper_service.model == mock_model
            mock_whisper.load_model.assert_called_once_with("base")
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, whisper_service, sample_audio_data):
        """Test successful audio transcription."""
        # Mock Whisper
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_result = {
            "text": "Test transcription",
            "language": "en",
            "segments": [{"avg_logprob": -0.5}]
        }
        mock_model.transcribe.return_value = mock_result
        mock_whisper.load_model.return_value = mock_model
        
        with patch.dict('sys.modules', {'whisper': mock_whisper}):
            result = await whisper_service.transcribe_audio(sample_audio_data)
            
            assert isinstance(result, TranscriptionResult)
            assert result.text == "Test transcription"
            assert result.language == "en"
            assert 0.0 <= result.confidence <= 1.0
            assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_transcribe_file(self, whisper_service):
        """Test file transcription."""
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_path = temp_file.name
        
        try:
            # Mock Whisper
            mock_whisper = MagicMock()
            mock_model = MagicMock()
            mock_result = {
                "text": "File transcription",
                "language": "en",
                "segments": []
            }
            mock_model.transcribe.return_value = mock_result
            mock_whisper.load_model.return_value = mock_model
            
            with patch.dict('sys.modules', {'whisper': mock_whisper}):
                result = await whisper_service.transcribe_file(temp_path)
                
                assert isinstance(result, TranscriptionResult)
                assert result.text == "File transcription"
        finally:
            os.unlink(temp_path)


class TestKokoroTTSService:
    """Test cases for KokoroTTSService."""
    
    @pytest.fixture
    def tts_service(self):
        """Create a KokoroTTSService instance."""
        return KokoroTTSService()
    
    def test_initialization(self, tts_service):
        """Test KokoroTTSService initialization."""
        assert tts_service.model is None
        assert not tts_service._initialized
        assert tts_service.sample_rate == 22050
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, tts_service):
        """Test successful initialization."""
        await tts_service.initialize()
        assert tts_service._initialized
    
    @pytest.mark.asyncio
    async def test_synthesize_speech(self, tts_service):
        """Test speech synthesis."""
        result = await tts_service.synthesize_speech("Hello world")
        
        assert isinstance(result, TTSResult)
        assert isinstance(result.audio_data, bytes)
        assert result.sample_rate == 22050
        assert result.duration > 0
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_with_parameters(self, tts_service):
        """Test speech synthesis with custom parameters."""
        result = await tts_service.synthesize_speech(
            text="Custom text",
            voice="custom_voice",
            speed=1.5,
            pitch=1.2
        )
        
        assert isinstance(result, TTSResult)
        assert len(result.audio_data) > 0


class TestPorcupineHotwordService:
    """Test cases for PorcupineHotwordService."""
    
    @pytest.fixture
    def hotword_service(self):
        """Create a PorcupineHotwordService instance."""
        return PorcupineHotwordService()
    
    def test_initialization(self, hotword_service):
        """Test PorcupineHotwordService initialization."""
        assert hotword_service.porcupine is None
        assert not hotword_service._initialized
        assert not hotword_service._is_listening
        assert hotword_service._detection_callback is None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, hotword_service):
        """Test successful initialization."""
        await hotword_service.initialize()
        assert hotword_service._initialized
    
    @pytest.mark.asyncio
    async def test_start_listening(self, hotword_service):
        """Test starting hotword detection."""
        callback = MagicMock()
        keywords = ["test", "keyword"]
        
        await hotword_service.start_listening(keywords, callback)
        
        assert hotword_service.is_listening
        assert hotword_service._detection_callback == callback
        assert hotword_service._listen_task is not None
    
    @pytest.mark.asyncio
    async def test_stop_listening(self, hotword_service):
        """Test stopping hotword detection."""
        # First start listening
        callback = MagicMock()
        await hotword_service.start_listening(["test"], callback)
        
        # Then stop
        await hotword_service.stop_listening()
        
        assert not hotword_service.is_listening
        assert hotword_service._detection_callback is None
        assert hotword_service._listen_task is None
    
    @pytest.mark.asyncio
    async def test_start_listening_already_active(self, hotword_service):
        """Test starting hotword detection when already active."""
        callback = MagicMock()
        
        # Start listening
        await hotword_service.start_listening(["test"], callback)
        
        # Try to start again (should not raise error)
        await hotword_service.start_listening(["test2"], callback)
        
        # Should still be listening
        assert hotword_service.is_listening
    
    def test_is_listening_property(self, hotword_service):
        """Test is_listening property."""
        assert not hotword_service.is_listening
        
        hotword_service._is_listening = True
        assert hotword_service.is_listening


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_encode_decode_audio_base64(self, sample_audio_data):
        """Test base64 encoding and decoding of audio data."""
        # Encode
        encoded = encode_audio_base64(sample_audio_data)
        assert isinstance(encoded, str)
        
        # Decode
        decoded = decode_audio_base64(encoded)
        assert decoded == sample_audio_data
    
    def test_save_audio_file(self, sample_audio_data):
        """Test saving audio data to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_audio.wav")
            
            save_audio_file(sample_audio_data, file_path)
            
            # Verify file was created and contains correct data
            assert os.path.exists(file_path)
            with open(file_path, 'rb') as f:
                saved_data = f.read()
            assert saved_data == sample_audio_data
    
    def test_save_audio_file_creates_directories(self, sample_audio_data):
        """Test that save_audio_file creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "subdir", "test_audio.wav")
            
            save_audio_file(sample_audio_data, file_path)
            
            # Verify file was created
            assert os.path.exists(file_path)


class TestIntegration:
    """Integration tests for voice processing services."""
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test complete service lifecycle."""
        whisper = WhisperService()
        tts = KokoroTTSService()
        hotword = PorcupineHotwordService()

        # Mock Whisper for this test
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict('sys.modules', {'whisper': mock_whisper}):
            # Initialize all services
            await whisper.initialize()
            await tts.initialize()
            await hotword.initialize()

            assert whisper._initialized
            assert tts._initialized
            assert hotword._initialized

            # Test hotword detection lifecycle
            callback = MagicMock()
            await hotword.start_listening(["test"], callback)
            assert hotword.is_listening

            await hotword.stop_listening()
            assert not hotword.is_listening
