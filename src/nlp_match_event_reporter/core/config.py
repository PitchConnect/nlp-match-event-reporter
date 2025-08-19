"""
Configuration settings for NLP Match Event Reporter.
"""

from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Configuration
    DEBUG: bool = Field(default=False, env="DEBUG")
    TESTING: bool = Field(default=False, env="TESTING")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    SECRET_KEY: str = Field(default="dev-secret-key", env="SECRET_KEY")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=1, env="API_WORKERS")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./nlp_reporter.db",
        env="DATABASE_URL"
    )
    
    # FOGIS API Configuration
    FOGIS_USERNAME: Optional[str] = Field(default=None, env="FOGIS_USERNAME")
    FOGIS_PASSWORD: Optional[str] = Field(default=None, env="FOGIS_PASSWORD")
    FOGIS_BASE_URL: str = Field(
        default="https://fogis.svenskfotboll.se",
        env="FOGIS_BASE_URL"
    )
    
    # Voice Processing Configuration
    HOTWORD_SENSITIVITY: float = Field(default=0.5, env="HOTWORD_SENSITIVITY")
    HOTWORD_MODEL_PATH: str = Field(
        default="./models/porcupine/",
        env="HOTWORD_MODEL_PATH"
    )
    WHISPER_MODEL_SIZE: str = Field(default="base", env="WHISPER_MODEL_SIZE")
    WHISPER_LANGUAGE: str = Field(default="sv", env="WHISPER_LANGUAGE")
    AUDIO_SAMPLE_RATE: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    AUDIO_CHUNK_SIZE: int = Field(default=1024, env="AUDIO_CHUNK_SIZE")
    
    # Text-to-Speech Configuration
    TTS_ENGINE: str = Field(default="kokoro", env="TTS_ENGINE")
    TTS_VOICE: str = Field(default="default", env="TTS_VOICE")
    TTS_SPEED: float = Field(default=1.0, env="TTS_SPEED")
    TTS_VOLUME: float = Field(default=0.8, env="TTS_VOLUME")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Security Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Match Event Configuration
    DEFAULT_MATCH_ID: Optional[int] = Field(default=None, env="DEFAULT_MATCH_ID")
    AUTO_SYNC_EVENTS: bool = Field(default=True, env="AUTO_SYNC_EVENTS")
    SYNC_INTERVAL_SECONDS: int = Field(default=30, env="SYNC_INTERVAL_SECONDS")
    MAX_RETRY_ATTEMPTS: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    
    # Audio Device Configuration
    AUDIO_INPUT_DEVICE_INDEX: Optional[int] = Field(
        default=None,
        env="AUDIO_INPUT_DEVICE_INDEX"
    )
    AUDIO_OUTPUT_DEVICE_INDEX: Optional[int] = Field(
        default=None,
        env="AUDIO_OUTPUT_DEVICE_INDEX"
    )
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=10,
        env="MAX_CONCURRENT_REQUESTS"
    )
    REQUEST_TIMEOUT_SECONDS: int = Field(
        default=30,
        env="REQUEST_TIMEOUT_SECONDS"
    )
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
