"""
Unit tests for FOGIS client.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock

from src.nlp_match_event_reporter.services.fogis_client import (
    FOGISClient,
    FOGISSyncService,
    FOGISMatch,
    FOGISEvent,
    FOGISSyncResult,
    convert_event_to_fogis_format,
    convert_fogis_match_to_internal,
)
from src.nlp_match_event_reporter.core.exceptions import FOGISIntegrationError


class TestFOGISClient:
    """Test cases for FOGISClient."""
    
    @pytest.fixture
    def fogis_client(self):
        """Create a FOGISClient instance."""
        return FOGISClient()
    
    def test_initialization(self, fogis_client):
        """Test FOGISClient initialization."""
        assert fogis_client.base_url == "https://fogis.svenskfotboll.se"
        assert fogis_client.timeout == 30.0
        assert fogis_client._session is None
        assert not fogis_client._authenticated
        assert fogis_client._auth_token is None
    
    @pytest.mark.asyncio
    async def test_initialize_session(self, fogis_client):
        """Test session initialization."""
        with patch('httpx.AsyncClient') as mock_client:
            await fogis_client.initialize()
            
            assert fogis_client._session is not None
            mock_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_session(self, fogis_client):
        """Test session cleanup."""
        # Initialize first
        with patch('httpx.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_client.return_value = mock_session
            
            await fogis_client.initialize()
            await fogis_client.close()
            
            mock_session.aclose.assert_called_once()
            assert fogis_client._session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, fogis_client):
        """Test async context manager."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_client.return_value = mock_session
            
            async with fogis_client as client:
                assert client._session is not None
            
            mock_session.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, fogis_client):
        """Test successful authentication."""
        with patch('httpx.AsyncClient'):
            result = await fogis_client.authenticate("test_user", "test_pass")
            
            assert result is True
            assert fogis_client._authenticated is True
            assert fogis_client._auth_token == "mock_auth_token_12345"
    
    @pytest.mark.asyncio
    async def test_get_matches_not_authenticated(self, fogis_client):
        """Test get_matches when not authenticated."""
        with pytest.raises(FOGISIntegrationError, match="Not authenticated"):
            await fogis_client.get_matches()
    
    @pytest.mark.asyncio
    async def test_get_matches_success(self, fogis_client):
        """Test successful match fetching."""
        # Authenticate first
        with patch('httpx.AsyncClient'):
            await fogis_client.authenticate("test", "test")
            
            matches = await fogis_client.get_matches(limit=10)
            
            assert len(matches) == 2
            assert all(isinstance(match, FOGISMatch) for match in matches)
            assert matches[0].home_team == "AIK"
            assert matches[0].away_team == "Hammarby"
    
    @pytest.mark.asyncio
    async def test_get_match_success(self, fogis_client):
        """Test successful single match fetching."""
        with patch('httpx.AsyncClient'):
            await fogis_client.authenticate("test", "test")
            
            match = await fogis_client.get_match(123456)
            
            assert match is not None
            assert isinstance(match, FOGISMatch)
            assert match.match_id == 123456
            assert match.home_team == "AIK"
    
    @pytest.mark.asyncio
    async def test_get_match_not_found(self, fogis_client):
        """Test fetching non-existent match."""
        with patch('httpx.AsyncClient'):
            await fogis_client.authenticate("test", "test")
            
            match = await fogis_client.get_match(999999)
            
            assert match is None
    
    @pytest.mark.asyncio
    async def test_sync_event_success(self, fogis_client):
        """Test successful event synchronization."""
        with patch('httpx.AsyncClient'):
            await fogis_client.authenticate("test", "test")
            
            result = await fogis_client.sync_event(
                match_id=123456,
                event_type="goal",
                minute=15,
                description="Goal by Test Player",
                player_name="Test Player",
                team="AIK"
            )
            
            assert isinstance(result, FOGISSyncResult)
            assert result.success is True
            assert result.event_id == 99999
            assert "successfully" in result.message
    
    @pytest.mark.asyncio
    async def test_sync_event_not_authenticated(self, fogis_client):
        """Test sync_event when not authenticated."""
        with pytest.raises(FOGISIntegrationError, match="Not authenticated"):
            await fogis_client.sync_event(
                match_id=123456,
                event_type="goal",
                minute=15,
                description="Test goal"
            )
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, fogis_client):
        """Test successful health check."""
        result = await fogis_client.health_check()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, fogis_client):
        """Test health check failure."""
        with patch.object(fogis_client, 'initialize', side_effect=Exception("Connection failed")):
            result = await fogis_client.health_check()
            assert result is False


class TestFOGISSyncService:
    """Test cases for FOGISSyncService."""
    
    @pytest.fixture
    def sync_service(self):
        """Create a FOGISSyncService instance."""
        return FOGISSyncService()
    
    def test_initialization(self, sync_service):
        """Test FOGISSyncService initialization."""
        assert sync_service._sync_task is None
        assert not sync_service._is_running
        assert sync_service._sync_interval == 30.0
    
    @pytest.mark.asyncio
    async def test_start_background_sync(self, sync_service):
        """Test starting background sync."""
        await sync_service.start_background_sync()
        
        assert sync_service.is_running is True
        assert sync_service._sync_task is not None
        
        # Cleanup
        await sync_service.stop_background_sync()
    
    @pytest.mark.asyncio
    async def test_stop_background_sync(self, sync_service):
        """Test stopping background sync."""
        # Start first
        await sync_service.start_background_sync()
        assert sync_service.is_running is True
        
        # Then stop
        await sync_service.stop_background_sync()
        assert sync_service.is_running is False
        assert sync_service._sync_task is None
    
    @pytest.mark.asyncio
    async def test_start_already_running(self, sync_service):
        """Test starting sync when already running."""
        await sync_service.start_background_sync()
        
        # Try to start again
        await sync_service.start_background_sync()
        
        # Should still be running
        assert sync_service.is_running is True
        
        # Cleanup
        await sync_service.stop_background_sync()
    
    @pytest.mark.asyncio
    async def test_stop_not_running(self, sync_service):
        """Test stopping sync when not running."""
        # Should not raise error
        await sync_service.stop_background_sync()
        assert sync_service.is_running is False
    
    def test_is_running_property(self, sync_service):
        """Test is_running property."""
        assert sync_service.is_running is False
        
        sync_service._is_running = True
        assert sync_service.is_running is True


class TestDataStructures:
    """Test cases for FOGIS data structures."""
    
    def test_fogis_match_creation(self):
        """Test FOGISMatch creation."""
        match_date = datetime.now(timezone.utc)
        
        match = FOGISMatch(
            match_id=123456,
            home_team="AIK",
            away_team="Hammarby",
            home_team_id=1001,
            away_team_id=1002,
            match_date=match_date,
            venue="Friends Arena",
            competition="Allsvenskan",
            status="scheduled"
        )
        
        assert match.match_id == 123456
        assert match.home_team == "AIK"
        assert match.away_team == "Hammarby"
        assert match.match_date == match_date
        assert match.referee_id is None  # Optional field
    
    def test_fogis_event_creation(self):
        """Test FOGISEvent creation."""
        timestamp = datetime.now(timezone.utc)
        
        event = FOGISEvent(
            event_id=999,
            match_id=123456,
            event_type="goal",
            minute=15,
            player_name="Test Player",
            player_id=5001,
            team="AIK",
            team_id=1001,
            description="Goal scored",
            timestamp=timestamp
        )
        
        assert event.event_id == 999
        assert event.match_id == 123456
        assert event.event_type == "goal"
        assert event.minute == 15
        assert event.timestamp == timestamp
    
    def test_fogis_sync_result_creation(self):
        """Test FOGISSyncResult creation."""
        sync_time = datetime.now(timezone.utc)
        
        result = FOGISSyncResult(
            success=True,
            event_id=999,
            message="Sync successful",
            sync_time=sync_time,
            attempts=1
        )
        
        assert result.success is True
        assert result.event_id == 999
        assert result.message == "Sync successful"
        assert result.sync_time == sync_time
        assert result.attempts == 1


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_convert_event_to_fogis_format(self):
        """Test event format conversion."""
        event_data = {
            "event_type": "goal",
            "minute": 15,
            "description": "Goal scored by Test Player",
            "player_name": "Test Player",
            "team": "AIK"
        }
        
        fogis_format = convert_event_to_fogis_format(event_data)
        
        assert fogis_format["event_type"] == "goal"
        assert fogis_format["minute"] == 15
        assert fogis_format["description"] == "Goal scored by Test Player"
        assert fogis_format["player_name"] == "Test Player"
        assert fogis_format["team"] == "AIK"
        assert "timestamp" in fogis_format
    
    def test_convert_fogis_match_to_internal(self):
        """Test FOGIS match to internal format conversion."""
        match_date = datetime.now(timezone.utc)
        
        fogis_match = FOGISMatch(
            match_id=123456,
            home_team="AIK",
            away_team="Hammarby",
            home_team_id=1001,
            away_team_id=1002,
            match_date=match_date,
            venue="Friends Arena",
            competition="Allsvenskan",
            status="scheduled",
            referee_id=5001,
            referee_name="Test Referee"
        )
        
        internal_format = convert_fogis_match_to_internal(fogis_match)
        
        assert internal_format["fogis_match_id"] == 123456
        assert internal_format["home_team"] == "AIK"
        assert internal_format["away_team"] == "Hammarby"
        assert internal_format["match_date"] == match_date
        assert internal_format["referee_id"] == 5001
        assert internal_format["referee_name"] == "Test Referee"
