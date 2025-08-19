"""
Voice processing services for speech-to-text, text-to-speech, and hotword detection.
"""

import asyncio
import base64
import io
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass

import numpy as np
from loguru import logger

from ..core.config import settings
from ..core.exceptions import VoiceProcessingError


@dataclass
class TranscriptionResult:
    """Result from speech-to-text processing."""
    text: str
    confidence: float
    language: str
    processing_time: float
    segments: Optional[List[Dict[str, Any]]] = None


@dataclass
class TTSResult:
    """Result from text-to-speech processing."""
    audio_data: bytes
    sample_rate: int
    duration: float
    processing_time: float


class WhisperService:
    """Service for speech-to-text using OpenAI Whisper."""
    
    def __init__(self):
        """Initialize Whisper service."""
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Whisper model."""
        if self._initialized:
            return
        
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Load model in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, whisper.load_model, self.model_size
            )
            
            self._initialized = True
            logger.info("Whisper model loaded successfully")
            
        except ImportError:
            raise VoiceProcessingError(
                "Whisper not installed. Install with: pip install openai-whisper"
            )
        except Exception as e:
            raise VoiceProcessingError(f"Failed to initialize Whisper: {e}")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> TranscriptionResult:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'sv' for Swedish)
            task: 'transcribe' or 'translate'
        
        Returns:
            TranscriptionResult with transcription and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribe in executor to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._transcribe_file,
                    temp_path,
                    language,
                    task
                )
                
                processing_time = time.time() - start_time
                
                # Extract confidence from segments if available
                confidence = 0.0
                if result.get("segments"):
                    confidences = [
                        segment.get("avg_logprob", 0.0)
                        for segment in result["segments"]
                    ]
                    if confidences:
                        # Convert log probabilities to confidence scores
                        confidence = float(np.exp(np.mean(confidences)))
                
                return TranscriptionResult(
                    text=result["text"].strip(),
                    confidence=min(max(confidence, 0.0), 1.0),
                    language=result.get("language", language or "unknown"),
                    processing_time=processing_time,
                    segments=result.get("segments", [])
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Transcription failed after {processing_time:.2f}s: {e}")
            raise VoiceProcessingError(f"Transcription failed: {e}")
    
    def _transcribe_file(
        self,
        file_path: str,
        language: Optional[str],
        task: str
    ) -> Dict[str, Any]:
        """Transcribe audio file (runs in executor)."""
        options = {
            "task": task,
            "verbose": False,
        }
        
        if language:
            options["language"] = language
        
        return self.model.transcribe(file_path, **options)
    
    async def transcribe_file(self, file_path: str, **kwargs) -> TranscriptionResult:
        """Transcribe audio file directly."""
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        return await self.transcribe_audio(audio_data, **kwargs)


class KokoroTTSService:
    """Service for text-to-speech using Kokoro TTS."""
    
    def __init__(self):
        """Initialize Kokoro TTS service."""
        self.model = None
        self._initialized = False
        self.sample_rate = 22050  # Default sample rate for Kokoro
    
    async def initialize(self) -> None:
        """Initialize the Kokoro TTS model."""
        if self._initialized:
            return
        
        try:
            # Note: This is a placeholder for Kokoro TTS integration
            # In a real implementation, you would load the Kokoro model here
            logger.info("Initializing Kokoro TTS service...")
            
            # Simulate model loading
            await asyncio.sleep(0.1)
            
            self._initialized = True
            logger.info("Kokoro TTS service initialized successfully")
            
        except Exception as e:
            raise VoiceProcessingError(f"Failed to initialize Kokoro TTS: {e}")
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> TTSResult:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice model to use
            speed: Speech speed multiplier
            pitch: Pitch multiplier
        
        Returns:
            TTSResult with audio data and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Note: This is a placeholder implementation
            # In a real implementation, you would use the Kokoro TTS model
            logger.info(f"Synthesizing speech: '{text[:50]}...' with voice '{voice}'")
            
            # Simulate TTS processing
            await asyncio.sleep(len(text) * 0.01)  # Simulate processing time
            
            # Generate placeholder audio data (silence)
            duration = len(text) * 0.1  # Estimate duration
            num_samples = int(self.sample_rate * duration)
            audio_data = np.zeros(num_samples, dtype=np.float32)
            
            # Convert to bytes
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            processing_time = time.time() - start_time
            
            return TTSResult(
                audio_data=audio_bytes,
                sample_rate=self.sample_rate,
                duration=duration,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"TTS synthesis failed after {processing_time:.2f}s: {e}")
            raise VoiceProcessingError(f"TTS synthesis failed: {e}")


class PorcupineHotwordService:
    """Service for hotword detection using Picovoice Porcupine."""
    
    def __init__(self):
        """Initialize Porcupine hotword service."""
        self.porcupine = None
        self._initialized = False
        self._is_listening = False
        self._detection_callback: Optional[Callable[[str], None]] = None
        self._listen_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize the Porcupine hotword detector."""
        if self._initialized:
            return
        
        try:
            # Note: This is a placeholder for Porcupine integration
            # In a real implementation, you would initialize Porcupine here
            logger.info("Initializing Porcupine hotword detection...")
            
            # Check for access key
            access_key = os.getenv("PICOVOICE_ACCESS_KEY")
            if not access_key:
                logger.warning("PICOVOICE_ACCESS_KEY not set, using mock implementation")
            
            # Simulate initialization
            await asyncio.sleep(0.1)
            
            self._initialized = True
            logger.info("Porcupine hotword service initialized successfully")
            
        except Exception as e:
            raise VoiceProcessingError(f"Failed to initialize Porcupine: {e}")
    
    async def start_listening(
        self,
        keywords: List[str],
        callback: Callable[[str], None],
        sensitivity: float = None
    ) -> None:
        """
        Start listening for hotwords.
        
        Args:
            keywords: List of keywords to detect
            callback: Function to call when keyword is detected
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        if not self._initialized:
            await self.initialize()
        
        if self._is_listening:
            logger.warning("Already listening for hotwords")
            return
        
        sensitivity = sensitivity or settings.HOTWORD_SENSITIVITY
        
        logger.info(f"Starting hotword detection for keywords: {keywords}")
        logger.info(f"Sensitivity: {sensitivity}")
        
        self._detection_callback = callback
        self._is_listening = True
        
        # Start listening task
        self._listen_task = asyncio.create_task(
            self._listen_for_hotwords(keywords, sensitivity)
        )
    
    async def stop_listening(self) -> None:
        """Stop listening for hotwords."""
        if not self._is_listening:
            return
        
        logger.info("Stopping hotword detection")
        self._is_listening = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        
        self._detection_callback = None
    
    async def _listen_for_hotwords(
        self,
        keywords: List[str],
        sensitivity: float
    ) -> None:
        """Listen for hotwords (placeholder implementation)."""
        try:
            while self._is_listening:
                # Note: This is a placeholder implementation
                # In a real implementation, you would:
                # 1. Capture audio from microphone
                # 2. Process audio with Porcupine
                # 3. Call callback when keyword is detected
                
                # Simulate listening
                await asyncio.sleep(0.1)
                
                # Simulate occasional detection for testing
                if np.random.random() < 0.001:  # Very low probability
                    detected_keyword = np.random.choice(keywords)
                    logger.info(f"Hotword detected: {detected_keyword}")
                    if self._detection_callback:
                        self._detection_callback(detected_keyword)
                
        except asyncio.CancelledError:
            logger.info("Hotword listening cancelled")
        except Exception as e:
            logger.error(f"Error in hotword detection: {e}")
            self._is_listening = False
    
    @property
    def is_listening(self) -> bool:
        """Check if currently listening for hotwords."""
        return self._is_listening


# Global service instances
whisper_service = WhisperService()
tts_service = KokoroTTSService()
hotword_service = PorcupineHotwordService()


async def initialize_voice_services() -> None:
    """Initialize all voice processing services."""
    logger.info("Initializing voice processing services...")
    
    try:
        await whisper_service.initialize()
        await tts_service.initialize()
        await hotword_service.initialize()
        logger.info("All voice processing services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize voice services: {e}")
        raise


async def cleanup_voice_services() -> None:
    """Cleanup voice processing services."""
    logger.info("Cleaning up voice processing services...")
    
    try:
        await hotword_service.stop_listening()
        logger.info("Voice processing services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up voice services: {e}")


# Utility functions
def encode_audio_base64(audio_data: bytes) -> str:
    """Encode audio data as base64 string."""
    return base64.b64encode(audio_data).decode('utf-8')


def decode_audio_base64(audio_base64: str) -> bytes:
    """Decode base64 audio string to bytes."""
    return base64.b64decode(audio_base64)


def save_audio_file(audio_data: bytes, file_path: str) -> None:
    """Save audio data to file."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(audio_data)
