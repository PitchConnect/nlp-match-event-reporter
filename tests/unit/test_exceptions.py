"""
Unit tests for custom exceptions.
"""

import pytest
from src.nlp_match_event_reporter.core.exceptions import (
    NLPReporterError,
    FOGISIntegrationError,
    VoiceProcessingError,
    EventProcessingError,
)


def test_nlp_reporter_error():
    """Test base NLPReporterError exception."""
    error = NLPReporterError("Test error message")
    
    assert str(error) == "Test error message"
    assert isinstance(error, Exception)


def test_fogis_integration_error():
    """Test FOGISIntegrationError exception."""
    error = FOGISIntegrationError("FOGIS API timeout")

    assert str(error) == "FOGIS API timeout"
    assert isinstance(error, NLPReporterError)


def test_voice_processing_error():
    """Test VoiceProcessingError exception."""
    error = VoiceProcessingError("Speech recognition failed")

    assert str(error) == "Speech recognition failed"
    assert isinstance(error, NLPReporterError)


def test_event_processing_error():
    """Test EventProcessingError exception."""
    error = EventProcessingError("Event validation failed")

    assert str(error) == "Event validation failed"
    assert isinstance(error, NLPReporterError)


def test_exception_inheritance():
    """Test that all custom exceptions inherit from NLPReporterError."""
    exceptions = [
        FOGISIntegrationError,
        VoiceProcessingError,
        EventProcessingError,
    ]

    for exception_class in exceptions:
        error = exception_class("Test message")
        assert isinstance(error, NLPReporterError)
        assert isinstance(error, Exception)


def test_exception_with_empty_message():
    """Test exceptions with empty messages."""
    error = NLPReporterError("")
    assert str(error) == ""


def test_exception_with_none_message():
    """Test exceptions with None message."""
    error = NLPReporterError(None)
    assert str(error) == "None"


def test_exception_chaining():
    """Test exception chaining."""
    original_error = ValueError("Original error")

    try:
        raise VoiceProcessingError("Voice processing error") from original_error
    except VoiceProcessingError as e:
        assert str(e) == "Voice processing error"
        assert e.__cause__ == original_error
        assert isinstance(e.__cause__, ValueError)


def test_exception_with_additional_context():
    """Test exceptions with additional context information."""
    # Test that exceptions can be raised with additional context
    try:
        raise FOGISIntegrationError("API call failed")
    except FOGISIntegrationError as e:
        assert "API call failed" in str(e)
        assert isinstance(e, NLPReporterError)


def test_multiple_exception_handling():
    """Test handling multiple exception types."""
    def raise_fogis_error():
        raise FOGISIntegrationError("FOGIS API error")

    def raise_voice_error():
        raise VoiceProcessingError("Microphone not found")

    # Test catching specific exception
    with pytest.raises(FOGISIntegrationError):
        raise_fogis_error()

    with pytest.raises(VoiceProcessingError):
        raise_voice_error()

    # Test catching base exception
    with pytest.raises(NLPReporterError):
        raise_fogis_error()

    with pytest.raises(NLPReporterError):
        raise_voice_error()
