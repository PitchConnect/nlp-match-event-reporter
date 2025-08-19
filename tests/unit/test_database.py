"""
Unit tests for database models and operations.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.nlp_match_event_reporter.models.database import (
    Base,
    Match,
    Event,
    User,
    UserSession,
    VoiceProcessingLog,
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


def test_match_model(db_session):
    """Test Match model creation and relationships."""
    # Create a match
    match = Match(
        fogis_match_id=12345,
        home_team="AIK",
        away_team="Hammarby",
        home_team_id=1001,
        away_team_id=1002,
        match_date=datetime.now(timezone.utc),
        venue="Friends Arena",
        competition="Allsvenskan",
        status="scheduled",
        referee_id=5001,
        referee_name="Test Referee",
    )
    
    db_session.add(match)
    db_session.commit()
    
    # Verify match was created
    assert match.id is not None
    assert match.fogis_match_id == 12345
    assert match.home_team == "AIK"
    assert match.away_team == "Hammarby"
    assert match.status == "scheduled"
    assert match.is_active is False
    assert match.created_at is not None
    assert match.updated_at is not None
    
    # Test string representation
    assert "AIK vs Hammarby" in str(match)


def test_event_model(db_session):
    """Test Event model creation and relationships."""
    # Create a match first
    match = Match(
        home_team="AIK",
        away_team="Hammarby",
        match_date=datetime.now(timezone.utc),
        venue="Friends Arena",
        competition="Allsvenskan",
    )
    db_session.add(match)
    db_session.commit()
    
    # Create an event
    event = Event(
        match_id=match.id,
        event_type="goal",
        minute=15,
        description="Goal scored by Erik Karlsson",
        player_name="Erik Karlsson",
        team="AIK",
        voice_transcription="Mål av Erik Karlsson i femtonde minuten",
        confidence_score=0.95,
    )
    
    db_session.add(event)
    db_session.commit()
    
    # Verify event was created
    assert event.id is not None
    assert event.match_id == match.id
    assert event.event_type == "goal"
    assert event.minute == 15
    assert event.player_name == "Erik Karlsson"
    assert event.confidence_score == 0.95
    assert event.synced_to_fogis is False
    assert event.is_deleted is False
    
    # Test relationship
    assert event.match == match
    assert event in match.events


def test_user_model(db_session):
    """Test User model creation."""
    user = User(
        username="test_referee",
        email="referee@example.com",
        hashed_password="hashed_password_here",
        full_name="Test Referee",
        referee_id=5001,
        is_active=True,
        is_admin=False,
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Verify user was created
    assert user.id is not None
    assert user.username == "test_referee"
    assert user.email == "referee@example.com"
    assert user.is_active is True
    assert user.is_admin is False
    assert user.created_at is not None


def test_user_session_model(db_session):
    """Test UserSession model creation and relationships."""
    # Create a user first
    user = User(
        username="test_user",
        email="user@example.com",
        hashed_password="hashed_password",
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a session
    session = UserSession(
        user_id=user.id,
        session_token="test_token_123",
        expires_at=datetime.now(timezone.utc),
        ip_address="192.168.1.1",
        user_agent="Test Browser",
    )
    
    db_session.add(session)
    db_session.commit()
    
    # Verify session was created
    assert session.id is not None
    assert session.user_id == user.id
    assert session.session_token == "test_token_123"
    assert session.is_active is True
    
    # Test relationship
    assert session.user == user
    assert session in user.sessions


def test_voice_processing_log_model(db_session):
    """Test VoiceProcessingLog model creation."""
    log = VoiceProcessingLog(
        operation_type="transcribe",
        status="success",
        input_data="audio_file.wav",
        output_data="Transcribed text",
        processing_time_ms=1500,
        confidence_score=0.92,
    )
    
    db_session.add(log)
    db_session.commit()
    
    # Verify log was created
    assert log.id is not None
    assert log.operation_type == "transcribe"
    assert log.status == "success"
    assert log.processing_time_ms == 1500
    assert log.confidence_score == 0.92
    assert log.created_at is not None


def test_match_event_cascade_delete(db_session):
    """Test that deleting a match cascades to delete events."""
    # Create match with events
    match = Match(
        home_team="Team A",
        away_team="Team B",
        match_date=datetime.now(timezone.utc),
        venue="Test Venue",
        competition="Test League",
    )
    db_session.add(match)
    db_session.commit()
    
    # Add events
    event1 = Event(
        match_id=match.id,
        event_type="goal",
        minute=10,
        description="First goal",
    )
    event2 = Event(
        match_id=match.id,
        event_type="yellow_card",
        minute=25,
        description="Yellow card",
    )
    
    db_session.add_all([event1, event2])
    db_session.commit()
    
    # Verify events exist
    assert len(match.events) == 2
    
    # Delete match
    db_session.delete(match)
    db_session.commit()
    
    # Verify events were also deleted (cascade)
    remaining_events = db_session.query(Event).filter_by(match_id=match.id).all()
    assert len(remaining_events) == 0


def test_database_indexes(db_session):
    """Test that database indexes are working by querying indexed fields."""
    # Create test data
    match = Match(
        home_team="Test Team 1",
        away_team="Test Team 2",
        match_date=datetime.now(timezone.utc),
        venue="Test Venue",
        competition="Test Competition",
        status="active",
        is_active=True,
    )
    db_session.add(match)
    db_session.commit()
    
    # Query by indexed fields (should work efficiently)
    matches_by_status = db_session.query(Match).filter_by(status="active").all()
    assert len(matches_by_status) == 1
    
    matches_by_active = db_session.query(Match).filter_by(is_active=True).all()
    assert len(matches_by_active) == 1
    
    # Test event indexes
    event = Event(
        match_id=match.id,
        event_type="goal",
        minute=30,
        description="Test goal",
        synced_to_fogis=False,
    )
    db_session.add(event)
    db_session.commit()
    
    events_by_type = db_session.query(Event).filter_by(event_type="goal").all()
    assert len(events_by_type) == 1
    
    events_by_sync = db_session.query(Event).filter_by(synced_to_fogis=False).all()
    assert len(events_by_sync) == 1
