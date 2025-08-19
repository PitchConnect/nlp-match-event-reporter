"""
Unit tests for match endpoints.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.nlp_match_event_reporter.main import app
from src.nlp_match_event_reporter.models.database import Base, Match
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
def sample_match(test_db):
    """Create a sample match for testing."""
    db = test_db()

    match = Match(
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

    db.add(match)
    db.commit()
    db.refresh(match)  # Refresh to get the ID
    match_id = match.id
    db.close()

    # Return just the ID since the object becomes detached
    return type('MockMatch', (), {'id': match_id})()


def test_get_matches_default(client: TestClient):
    """Test getting matches with default parameters."""
    response = client.get("/api/v1/matches/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "matches" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert isinstance(data["matches"], list)


def test_get_matches_with_pagination(client: TestClient):
    """Test getting matches with pagination parameters."""
    response = client.get("/api/v1/matches/?limit=5&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_get_matches_with_status_filter(client: TestClient):
    """Test getting matches with status filter."""
    response = client.get("/api/v1/matches/?status=scheduled")
    
    assert response.status_code == 200
    data = response.json()
    
    # All returned matches should have the filtered status
    for match in data["matches"]:
        assert match["status"] == "scheduled"


def test_get_matches_invalid_pagination(client: TestClient):
    """Test getting matches with invalid pagination parameters."""
    # Test negative offset
    response = client.get("/api/v1/matches/?offset=-1")
    assert response.status_code == 422
    
    # Test limit too high
    response = client.get("/api/v1/matches/?limit=101")
    assert response.status_code == 422
    
    # Test limit too low
    response = client.get("/api/v1/matches/?limit=0")
    assert response.status_code == 422


def test_get_specific_match(client: TestClient, sample_match):
    """Test getting a specific match by ID."""
    response = client.get(f"/api/v1/matches/{sample_match.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == sample_match.id
    assert data["home_team"] == "AIK"  # From fixture data
    assert data["away_team"] == "Hammarby"  # From fixture data
    assert "date" in data
    assert "time" in data
    assert "venue" in data
    assert "status" in data
    assert "events" in data


def test_get_nonexistent_match(client: TestClient):
    """Test getting a non-existent match."""
    response = client.get("/api/v1/matches/999999")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert data["detail"] == "Match not found"


def test_start_match_reporting(client: TestClient, sample_match):
    """Test starting match reporting."""
    response = client.post(f"/api/v1/matches/{sample_match.id}/start")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["match_id"] == sample_match.id
    assert data["status"] == "active"


def test_stop_match_reporting(client: TestClient, sample_match):
    """Test stopping match reporting."""
    # First start the match
    client.post(f"/api/v1/matches/{sample_match.id}/start")

    # Then stop it
    response = client.post(f"/api/v1/matches/{sample_match.id}/stop")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["match_id"] == sample_match.id
    assert data["status"] == "completed"
