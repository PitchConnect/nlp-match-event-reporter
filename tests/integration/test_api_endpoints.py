"""
Integration tests for API endpoints with database.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.nlp_match_event_reporter.main import app
from src.nlp_match_event_reporter.models.database import Base, Match, Event
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
def sample_data(test_db):
    """Create sample data for testing."""
    db = test_db()
    
    # Create sample matches
    match1 = Match(
        fogis_match_id=123456,
        home_team="AIK",
        away_team="Hammarby",
        home_team_id=1001,
        away_team_id=1002,
        match_date=datetime.now(timezone.utc) + timedelta(days=1),
        venue="Friends Arena",
        competition="Allsvenskan",
        status="scheduled",
        referee_id=5001,
        referee_name="Test Referee",
    )
    
    match2 = Match(
        fogis_match_id=123457,
        home_team="Malmö FF",
        away_team="IFK Norrköping",
        home_team_id=1005,
        away_team_id=1006,
        match_date=datetime.now(timezone.utc) - timedelta(hours=2),
        venue="Eleda Stadion",
        competition="Allsvenskan",
        status="active",
        referee_id=5003,
        referee_name="Active Referee",
        is_active=True,
        reporting_started_at=datetime.now(timezone.utc) - timedelta(hours=2),
    )
    
    db.add_all([match1, match2])
    db.commit()
    
    # Create sample events for active match
    event1 = Event(
        match_id=match2.id,
        event_type="goal",
        minute=15,
        description="Goal scored by Erik Karlsson",
        player_name="Erik Karlsson",
        team="Malmö FF",
        voice_transcription="Mål av Erik Karlsson i femtonde minuten",
        confidence_score=0.95,
    )
    
    event2 = Event(
        match_id=match2.id,
        event_type="yellow_card",
        minute=23,
        description="Yellow card for Marcus Johansson",
        player_name="Marcus Johansson",
        team="IFK Norrköping",
        voice_transcription="Gult kort för Marcus Johansson",
        confidence_score=0.88,
    )
    
    db.add_all([event1, event2])
    db.commit()
    
    db.close()
    return {"matches": [match1, match2], "events": [event1, event2]}


def test_health_endpoints(client):
    """Test health check endpoints."""
    # Basic health check
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    
    # Detailed health check
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["database"] == "healthy"


def test_matches_endpoints(client, sample_data):
    """Test match-related endpoints."""
    # Get matches list
    response = client.get("/api/v1/matches/")
    assert response.status_code == 200
    data = response.json()
    assert "matches" in data
    assert len(data["matches"]) == 2
    assert data["total"] == 2
    
    # Test pagination
    response = client.get("/api/v1/matches/?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 1
    assert data["limit"] == 1
    assert data["offset"] == 0
    
    # Test status filter
    response = client.get("/api/v1/matches/?status=active")
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 1
    assert data["matches"][0]["status"] == "active"
    
    # Get specific match
    response = client.get("/api/v1/matches/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["home_team"] == "AIK"
    assert data["away_team"] == "Hammarby"
    assert "events" in data
    
    # Get non-existent match
    response = client.get("/api/v1/matches/999")
    assert response.status_code == 404


def test_match_reporting_control(client, sample_data):
    """Test match reporting start/stop functionality."""
    # Start reporting for scheduled match
    response = client.post("/api/v1/matches/1/start")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "started_at" in data
    
    # Try to start already active match
    response = client.post("/api/v1/matches/1/start")
    assert response.status_code == 400
    
    # Stop reporting
    response = client.post("/api/v1/matches/1/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "ended_at" in data
    
    # Try to stop inactive match
    response = client.post("/api/v1/matches/1/stop")
    assert response.status_code == 400


def test_events_endpoints(client, sample_data):
    """Test event-related endpoints."""
    # Get all events
    response = client.get("/api/v1/events/")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) == 2
    assert data["total"] == 2
    
    # Filter events by match
    response = client.get("/api/v1/events/?match_id=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) == 2
    for event in data["events"]:
        assert event["match_id"] == 2
    
    # Test pagination
    response = client.get("/api/v1/events/?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) == 1
    assert data["limit"] == 1
    
    # Create new event
    event_data = {
        "match_id": 1,
        "event_type": "corner",
        "minute": 30,
        "description": "Corner kick for AIK",
        "team": "AIK"
    }
    response = client.post("/api/v1/events/", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Event created successfully"
    assert data["event"]["event_type"] == "corner"
    assert data["event"]["minute"] == 30
    
    # Try to create event for non-existent match
    event_data["match_id"] = 999
    response = client.post("/api/v1/events/", json=event_data)
    assert response.status_code == 404


def test_voice_endpoints(client):
    """Test voice processing endpoints (mock responses)."""
    # Test TTS endpoint
    response = client.post("/api/v1/voice/speak", data={"text": "Test message"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Test hotword status
    response = client.get("/api/v1/voice/hotword/status")
    assert response.status_code == 200
    data = response.json()
    assert "active" in data
    
    # Test hotword start
    response = client.post("/api/v1/voice/hotword/start")
    assert response.status_code == 200
    
    # Test hotword stop
    response = client.post("/api/v1/voice/hotword/stop")
    assert response.status_code == 200


def test_api_error_handling(client):
    """Test API error handling."""
    # Test invalid pagination parameters
    response = client.get("/api/v1/matches/?limit=0")
    assert response.status_code == 422
    
    response = client.get("/api/v1/matches/?offset=-1")
    assert response.status_code == 422
    
    # Test invalid event data
    invalid_event = {
        "match_id": "invalid",
        "event_type": "",
        "minute": -1,
        "description": ""
    }
    response = client.post("/api/v1/events/", json=invalid_event)
    assert response.status_code == 422
