"""
Unit tests for match endpoints.
"""

import pytest
from fastapi.testclient import TestClient


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


def test_get_specific_match(client: TestClient):
    """Test getting a specific match by ID."""
    response = client.get("/api/v1/matches/123456")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == 123456
    assert "home_team" in data
    assert "away_team" in data
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


def test_start_match_reporting(client: TestClient):
    """Test starting match reporting."""
    response = client.post("/api/v1/matches/123456/start")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert data["match_id"] == 123456
    assert data["status"] == "active"


def test_stop_match_reporting(client: TestClient):
    """Test stopping match reporting."""
    response = client.post("/api/v1/matches/123456/stop")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert data["match_id"] == 123456
    assert data["status"] == "completed"
