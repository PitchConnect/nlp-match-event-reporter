"""
Database models for NLP Match Event Reporter.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Match(Base, TimestampMixin):
    """Match model representing soccer matches from FOGIS."""
    
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fogis_match_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True)
    
    # Match details
    home_team: Mapped[str] = mapped_column(String(255), nullable=False)
    away_team: Mapped[str] = mapped_column(String(255), nullable=False)
    home_team_id: Mapped[Optional[int]] = mapped_column(Integer)
    away_team_id: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Match scheduling
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str] = mapped_column(String(255), nullable=False)
    competition: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Match status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    
    # Officials
    referee_id: Mapped[Optional[int]] = mapped_column(Integer)
    referee_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Match state
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    reporting_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reporting_ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    events: Mapped[List["Event"]] = relationship("Event", back_populates="match", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_match_date", "match_date"),
        Index("idx_match_status", "status"),
        Index("idx_match_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Match(id={self.id}, {self.home_team} vs {self.away_team}, {self.match_date})>"


class Event(Base, TimestampMixin):
    """Event model representing match events."""
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Player/team information
    player_name: Mapped[Optional[str]] = mapped_column(String(255))
    player_id: Mapped[Optional[int]] = mapped_column(Integer)
    team: Mapped[Optional[str]] = mapped_column(String(255))
    team_id: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Voice processing metadata
    voice_transcription: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    audio_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # FOGIS synchronization
    synced_to_fogis: Mapped[bool] = mapped_column(Boolean, default=False)
    fogis_event_id: Mapped[Optional[int]] = mapped_column(Integer)
    sync_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_sync_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index("idx_event_match_id", "match_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_minute", "minute"),
        Index("idx_event_sync_status", "synced_to_fogis"),
        Index("idx_event_deleted", "is_deleted"),
    )
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type={self.event_type}, minute={self.minute}, match_id={self.match_id})>"


class User(Base, TimestampMixin):
    """User model for authentication and session management."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Profile information
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    referee_id: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Session tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_email", "email"),
        Index("idx_user_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserSession(Base, TimestampMixin):
    """User session model for tracking active sessions."""
    
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Session metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_token", "session_token"),
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_active", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"


class VoiceProcessingLog(Base, TimestampMixin):
    """Log model for voice processing operations."""
    
    __tablename__ = "voice_processing_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Processing details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # transcribe, tts, hotword
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, error, processing
    
    # Input/output
    input_data: Mapped[Optional[str]] = mapped_column(Text)
    output_data: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Performance metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # File references
    audio_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    output_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Associated entities
    match_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("matches.id"))
    event_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("events.id"))
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Indexes
    __table_args__ = (
        Index("idx_voice_log_operation", "operation_type"),
        Index("idx_voice_log_status", "status"),
        Index("idx_voice_log_match", "match_id"),
        Index("idx_voice_log_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<VoiceProcessingLog(id={self.id}, operation={self.operation_type}, status={self.status})>"
