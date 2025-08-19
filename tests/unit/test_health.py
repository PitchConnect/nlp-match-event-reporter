"""
Unit tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_basic_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "environment" in data


def test_detailed_health_check(client: TestClient):
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "services" in data
    assert "configuration" in data
    
    # Check service status structure
    services = data["services"]
    assert "api" in services
    assert "database" in services
    assert "fogis_client" in services
    assert "voice_processing" in services
    
    # Check configuration structure
    config = data["configuration"]
    assert "debug" in config
    assert "log_level" in config
    assert "whisper_model" in config
    assert "tts_engine" in config


def test_readiness_check(client: TestClient):
    """Test readiness check endpoint."""
    response = client.get("/api/v1/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ready"


def test_liveness_check(client: TestClient):
    """Test liveness check endpoint."""
    response = client.get("/api/v1/health/live")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "alive"


def test_root_health_check(client: TestClient):
    """Test root health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
