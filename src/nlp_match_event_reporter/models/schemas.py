"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Base schemas
class BaseResponse(BaseModel):
    """Base response model."""
    message: Optional[str] = None


# Match schemas
class MatchBase(BaseModel):
    """Base match model."""
    id: int
    home_team: str
    away_team: str
    date: str
    time: str
    venue: str
    status: str
    competition: str


class MatchResponse(MatchBase):
    """Match response model with additional details."""
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    referee_id: Optional[int] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)


class MatchListResponse(BaseModel):
    """Match list response model."""
    matches: List[MatchBase]
    total: int
    limit: int
    offset: int


# Event schemas
class EventBase(BaseModel):
    """Base event model."""
    match_id: int
    event_type: str
    minute: int
    player_name: Optional[str] = None
    team: Optional[str] = None
    description: str


class EventCreateRequest(EventBase):
    """Event creation request model."""
    pass


class EventResponse(EventBase):
    """Event response model with additional details."""
    id: int
    timestamp: datetime
    synced_to_fogis: bool = False
    voice_transcription: Optional[str] = None
    confidence_score: Optional[float] = None


class EventCreateResponse(BaseResponse):
    """Event creation response model."""
    event: EventResponse


class EventListResponse(BaseModel):
    """Event list response model."""
    events: List[EventResponse]
    total: int
    limit: int
    offset: int


class DetectedEvent(BaseModel):
    """Detected event from voice transcription."""
    event_type: str
    player_name: Optional[str] = None
    minute: Optional[int] = None
    confidence: float


# Voice processing schemas
class VoiceTranscriptionResponse(BaseModel):
    """Voice transcription response model."""
    text: str
    confidence: float
    language: str
    duration: float
    detected_events: List[DetectedEvent] = Field(default_factory=list)


class TTSResponse(BaseResponse):
    """Text-to-speech response model."""
    audio_url: str
    duration: float
    voice_used: str
    speed_used: float


class HotwordStatusResponse(BaseModel):
    """Hotword detection status response model."""
    active: bool
    sensitivity: float
    model_loaded: bool
    detections_today: int
    last_detection: Optional[datetime] = None
    audio_device: str


# Configuration schemas
class VoiceConfig(BaseModel):
    """Voice processing configuration."""
    hotword_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    whisper_model_size: str = Field(default="base")
    whisper_language: str = Field(default="sv")
    tts_engine: str = Field(default="kokoro")
    tts_voice: str = Field(default="default")
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0)


class MatchConfig(BaseModel):
    """Match configuration."""
    auto_sync_events: bool = Field(default=True)
    sync_interval_seconds: int = Field(default=30, ge=5, le=300)
    max_retry_attempts: int = Field(default=3, ge=1, le=10)


# Error schemas
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Health check schemas
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    services: Optional[Dict[str, str]] = None
    configuration: Optional[Dict[str, Any]] = None
