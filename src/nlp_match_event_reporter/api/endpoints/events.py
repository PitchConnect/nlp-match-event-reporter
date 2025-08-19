"""
Event-related API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from ...models.schemas import (
    EventResponse,
    EventListResponse,
    EventCreateRequest,
    EventCreateResponse,
)

router = APIRouter()


@router.get("/", response_model=EventListResponse)
async def get_events(
    match_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> EventListResponse:
    """Get list of match events."""
    try:
        logger.info(f"Fetching events for match_id={match_id}, limit={limit}, offset={offset}")
        
        # TODO: Implement database query for events
        # For now, return mock data
        mock_events = [
            {
                "id": 1,
                "match_id": 123456,
                "event_type": "goal",
                "minute": 15,
                "player_name": "Erik Karlsson",
                "team": "AIK",
                "description": "Goal scored by Erik Karlsson",
                "timestamp": "2025-08-20T19:15:00Z",
                "synced_to_fogis": True
            },
            {
                "id": 2,
                "match_id": 123456,
                "event_type": "yellow_card",
                "minute": 23,
                "player_name": "Marcus Johansson",
                "team": "Hammarby",
                "description": "Yellow card for Marcus Johansson",
                "timestamp": "2025-08-20T19:23:00Z",
                "synced_to_fogis": True
            }
        ]
        
        # Filter by match_id if provided
        if match_id:
            mock_events = [e for e in mock_events if e["match_id"] == match_id]
        
        # Apply pagination
        paginated_events = mock_events[offset:offset + limit]
        
        return EventListResponse(
            events=paginated_events,
            total=len(mock_events),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")


@router.post("/", response_model=EventCreateResponse)
async def create_event(event_data: EventCreateRequest) -> EventCreateResponse:
    """Create a new match event."""
    try:
        logger.info(f"Creating event: {event_data.dict()}")
        
        # TODO: Implement event creation logic
        # - Validate event data
        # - Store in local database
        # - Queue for FOGIS sync
        # - Process with NLP if from voice input
        
        # Mock response
        created_event = {
            "id": 999,
            "match_id": event_data.match_id,
            "event_type": event_data.event_type,
            "minute": event_data.minute,
            "player_name": event_data.player_name,
            "team": event_data.team,
            "description": event_data.description,
            "timestamp": "2025-08-20T19:30:00Z",
            "synced_to_fogis": False
        }
        
        return EventCreateResponse(
            message="Event created successfully",
            event=created_event
        )
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int) -> EventResponse:
    """Get detailed information about a specific event."""
    try:
        logger.info(f"Fetching event details for event_id={event_id}")
        
        # TODO: Implement database query for specific event
        # For now, return mock data
        if event_id == 1:
            mock_event = {
                "id": 1,
                "match_id": 123456,
                "event_type": "goal",
                "minute": 15,
                "player_name": "Erik Karlsson",
                "team": "AIK",
                "description": "Goal scored by Erik Karlsson",
                "timestamp": "2025-08-20T19:15:00Z",
                "synced_to_fogis": True,
                "voice_transcription": "Goal by Erik Karlsson in the fifteenth minute",
                "confidence_score": 0.95
            }
            return EventResponse(**mock_event)
        else:
            raise HTTPException(status_code=404, detail="Event not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch event details")


@router.delete("/{event_id}")
async def delete_event(event_id: int) -> dict:
    """Delete a match event."""
    try:
        logger.info(f"Deleting event_id={event_id}")
        
        # TODO: Implement event deletion
        # - Remove from local database
        # - Handle FOGIS sync if already synced
        
        return {
            "message": f"Event {event_id} deleted successfully",
            "event_id": event_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete event")


@router.post("/{event_id}/sync")
async def sync_event_to_fogis(event_id: int) -> dict:
    """Manually sync an event to FOGIS."""
    try:
        logger.info(f"Syncing event_id={event_id} to FOGIS")
        
        # TODO: Implement FOGIS sync
        # - Get event from database
        # - Transform to FOGIS format
        # - Send to FOGIS API
        # - Update sync status
        
        return {
            "message": f"Event {event_id} synced to FOGIS successfully",
            "event_id": event_id,
            "synced_at": "2025-08-20T19:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error syncing event {event_id} to FOGIS: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync event to FOGIS")
