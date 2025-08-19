"""
Unit tests for configuration management.
"""

import pytest
import os
from unittest.mock import patch

from src.nlp_match_event_reporter.core.config import Settings


def test_default_settings():
    """Test default configuration values."""
    # Create settings without TESTING env var
    import os
    old_testing = os.environ.get("TESTING")
    if "TESTING" in os.environ:
        del os.environ["TESTING"]

    try:
        settings = Settings()

        assert settings.DEBUG is False
        assert settings.TESTING is False
        assert settings.ENVIRONMENT == "development"
        assert settings.API_HOST == "0.0.0.0"
        assert settings.API_PORT == 8000
    finally:
        if old_testing is not None:
            os.environ["TESTING"] = old_testing


def test_environment_variable_override():
    """Test that environment variables override defaults."""
    with patch.dict(os.environ, {
        "DEBUG": "true",
        "TESTING": "true",
        "ENVIRONMENT": "production",
        "API_PORT": "9000",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "postgresql://test:test@localhost/test"
    }):
        settings = Settings()
        
        assert settings.DEBUG is True
        assert settings.TESTING is True
        assert settings.ENVIRONMENT == "production"
        assert settings.API_PORT == 9000
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"


def test_voice_processing_settings():
    """Test voice processing configuration."""
    settings = Settings()

    assert settings.WHISPER_MODEL_SIZE == "base"
    assert settings.TTS_ENGINE == "kokoro"
    assert settings.HOTWORD_SENSITIVITY == 0.5


def test_fogis_api_settings():
    """Test FOGIS API configuration."""
    settings = Settings()

    assert settings.FOGIS_BASE_URL == "https://fogis.svenskfotboll.se"


def test_boolean_environment_variables():
    """Test boolean environment variable parsing."""
    # Test various boolean representations
    test_cases = [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
    ]
    
    for env_value, expected in test_cases:
        with patch.dict(os.environ, {"DEBUG": env_value}):
            settings = Settings()
            assert settings.DEBUG == expected


def test_invalid_environment_values():
    """Test handling of invalid environment values."""
    # Test invalid port number
    with patch.dict(os.environ, {"API_PORT": "invalid"}):
        with pytest.raises(ValueError):
            Settings()
    
    # Test invalid float value
    with patch.dict(os.environ, {"HOTWORD_SENSITIVITY": "invalid"}):
        with pytest.raises(ValueError):
            Settings()


def test_settings_validation():
    """Test settings validation."""
    # Test valid port range
    with patch.dict(os.environ, {"API_PORT": "8080"}):
        settings = Settings()
        assert settings.API_PORT == 8080
    
    # Test valid sensitivity range
    with patch.dict(os.environ, {"HOTWORD_SENSITIVITY": "0.8"}):
        settings = Settings()
        assert settings.HOTWORD_SENSITIVITY == 0.8


def test_database_url_formats():
    """Test different database URL formats."""
    test_urls = [
        "sqlite:///./test.db",
        "sqlite:///:memory:",
        "postgresql://user:pass@localhost:5432/dbname",
        "mysql://user:pass@localhost:3306/dbname",
    ]
    
    for url in test_urls:
        with patch.dict(os.environ, {"DATABASE_URL": url}):
            settings = Settings()
            assert settings.DATABASE_URL == url


def test_log_level_validation():
    """Test log level validation."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in valid_levels:
        with patch.dict(os.environ, {"LOG_LEVEL": level}):
            settings = Settings()
            assert settings.LOG_LEVEL == level


def test_log_format_validation():
    """Test log format validation."""
    valid_formats = ["text", "json"]
    
    for format_type in valid_formats:
        with patch.dict(os.environ, {"LOG_FORMAT": format_type}):
            settings = Settings()
            assert settings.LOG_FORMAT == format_type
