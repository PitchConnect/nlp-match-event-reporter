"""
Unit tests for Pydantic schemas.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.nlp_match_event_reporter.models.schemas import (
    MatchResponse,
    MatchListResponse,
    EventResponse,
    EventListResponse,
    EventCreateRequest,
    EventCreateResponse,
    HealthResponse,
)


def test_match_response_schema():
    """Test MatchResponse schema validation."""
    valid_data = {
        "id": 1,
        "home_team": "AIK",
        "away_team": "Hammarby",
        "date": "2025-08-20",
        "time": "19:00",
        "venue": "Friends Arena",
        "status": "scheduled",
        "competition": "Allsvenskan",
        "home_team_id": 1001,
        "away_team_id": 1002,
        "referee_id": 5001,
        "events": []
    }
    
    match = MatchResponse(**valid_data)
    assert match.id == 1
    assert match.home_team == "AIK"
    assert match.away_team == "Hammarby"
    assert match.events == []


def test_match_response_optional_fields():
    """Test MatchResponse with optional fields."""
    minimal_data = {
        "id": 1,
        "home_team": "AIK",
        "away_team": "Hammarby",
        "date": "2025-08-20",
        "time": "19:00",
        "venue": "Friends Arena",
        "status": "scheduled",
        "competition": "Allsvenskan",
        "events": []
    }
    
    match = MatchResponse(**minimal_data)
    assert match.home_team_id is None
    assert match.away_team_id is None
    assert match.referee_id is None


def test_match_list_response_schema():
    """Test MatchListResponse schema validation."""
    data = {
        "matches": [
            {
                "id": 1,
                "home_team": "AIK",
                "away_team": "Hammarby",
                "date": "2025-08-20",
                "time": "19:00",
                "venue": "Friends Arena",
                "status": "scheduled",
                "competition": "Allsvenskan",
                "events": []
            }
        ],
        "total": 1,
        "limit": 10,
        "offset": 0
    }
    
    response = MatchListResponse(**data)
    assert len(response.matches) == 1
    assert response.total == 1
    assert response.limit == 10
    assert response.offset == 0


def test_event_create_request_schema():
    """Test EventCreateRequest schema validation."""
    valid_data = {
        "match_id": 1,
        "event_type": "goal",
        "minute": 15,
        "description": "Goal scored by Erik Karlsson",
        "player_name": "Erik Karlsson",
        "team": "AIK"
    }
    
    event = EventCreateRequest(**valid_data)
    assert event.match_id == 1
    assert event.event_type == "goal"
    assert event.minute == 15
    assert event.player_name == "Erik Karlsson"


def test_event_create_request_optional_fields():
    """Test EventCreateRequest with optional fields."""
    minimal_data = {
        "match_id": 1,
        "event_type": "goal",
        "minute": 15,
        "description": "Goal scored"
    }
    
    event = EventCreateRequest(**minimal_data)
    assert event.player_name is None
    assert event.team is None


def test_event_create_request_validation():
    """Test EventCreateRequest validation rules."""
    # Test valid request
    valid_request = EventCreateRequest(
        match_id=1,
        event_type="goal",
        minute=15,
        description="Valid goal"
    )
    assert valid_request.minute == 15

    # Test edge cases that should work
    edge_request = EventCreateRequest(
        match_id=1,
        event_type="goal",
        minute=0,  # Start of match
        description="Goal at start"
    )
    assert edge_request.minute == 0


def test_event_response_schema():
    """Test EventResponse schema validation."""
    data = {
        "id": 1,
        "match_id": 1,
        "event_type": "goal",
        "minute": 15,
        "description": "Goal scored by Erik Karlsson",
        "player_name": "Erik Karlsson",
        "team": "AIK",
        "timestamp": "2025-08-20T19:15:00Z",
        "synced_to_fogis": True
    }

    event = EventResponse(**data)
    assert event.id == 1
    assert event.event_type == "goal"
    assert event.minute == 15
    assert event.synced_to_fogis is True


def test_event_list_response_schema():
    """Test EventListResponse schema validation."""
    data = {
        "events": [
            {
                "id": 1,
                "match_id": 1,
                "event_type": "goal",
                "minute": 15,
                "description": "Goal scored",
                "timestamp": "2025-08-20T19:15:00Z",
                "synced_to_fogis": True
            }
        ],
        "total": 1,
        "limit": 50,
        "offset": 0
    }

    response = EventListResponse(**data)
    assert len(response.events) == 1
    assert response.total == 1
    assert response.limit == 50


def test_health_response_schema():
    """Test HealthResponse schema validation."""
    data = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development",
        "services": {
            "database": "healthy",
            "api": "healthy"
        },
        "configuration": {
            "debug": True,
            "log_level": "INFO"
        }
    }

    response = HealthResponse(**data)
    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.environment == "development"
    assert response.services["database"] == "healthy"
    assert response.configuration["debug"] is True


def test_schema_serialization():
    """Test schema serialization to dict."""
    match_data = {
        "id": 1,
        "home_team": "AIK",
        "away_team": "Hammarby",
        "date": "2025-08-20",
        "time": "19:00",
        "venue": "Friends Arena",
        "status": "scheduled",
        "competition": "Allsvenskan",
        "events": []
    }
    
    match = MatchResponse(**match_data)
    serialized = match.model_dump()
    
    assert isinstance(serialized, dict)
    assert serialized["id"] == 1
    assert serialized["home_team"] == "AIK"


def test_schema_json_serialization():
    """Test schema JSON serialization."""
    event_data = {
        "match_id": 1,
        "event_type": "goal",
        "minute": 15,
        "description": "Goal scored"
    }
    
    event = EventCreateRequest(**event_data)
    json_str = event.model_dump_json()
    
    assert isinstance(json_str, str)
    assert "goal" in json_str
    assert "15" in json_str
