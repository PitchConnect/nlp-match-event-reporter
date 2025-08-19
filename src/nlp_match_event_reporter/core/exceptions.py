"""
Custom exceptions for NLP Match Event Reporter.
"""

from typing import Optional


class NLPReporterError(Exception):
    """Base exception for NLP Reporter errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        status_code: int = 500,
    ) -> None:
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.message)


class VoiceProcessingError(NLPReporterError):
    """Exception raised for voice processing errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        status_code: int = 422,
    ) -> None:
        super().__init__(message, detail, status_code)


class FOGISIntegrationError(NLPReporterError):
    """Exception raised for FOGIS API integration errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        status_code: int = 502,
    ) -> None:
        super().__init__(message, detail, status_code)


class EventProcessingError(NLPReporterError):
    """Exception raised for event processing errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        status_code: int = 422,
    ) -> None:
        super().__init__(message, detail, status_code)


class AudioDeviceError(VoiceProcessingError):
    """Exception raised for audio device errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 503)


class HotwordDetectionError(VoiceProcessingError):
    """Exception raised for hotword detection errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 503)


class SpeechRecognitionError(VoiceProcessingError):
    """Exception raised for speech recognition errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 422)


class TextToSpeechError(VoiceProcessingError):
    """Exception raised for text-to-speech errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 503)


class DatabaseError(NLPReporterError):
    """Exception raised for database errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 500)


class ValidationError(NLPReporterError):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 400)


class AuthenticationError(NLPReporterError):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 401)


class AuthorizationError(NLPReporterError):
    """Exception raised for authorization errors."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message, detail, 403)
