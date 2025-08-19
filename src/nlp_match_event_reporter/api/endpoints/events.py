"""
Event-related API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ...models.schemas import (
    EventResponse,
    EventListResponse,
    EventCreateRequest,
    EventCreateResponse,
)
from ...models.database import Event, Match
from ...core.database import get_database_session

router = APIRouter()


@router.get("/", response_model=EventListResponse)
async def get_events(
    match_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_database_session),
) -> EventListResponse:
    """Get list of match events."""
    try:
        logger.info(f"Fetching events for match_id={match_id}, limit={limit}, offset={offset}")

        # Build query
        query = db.query(Event).filter(Event.is_deleted == False)

        # Filter by match_id if provided
        if match_id:
            query = query.filter(Event.match_id == match_id)

        # Order by minute and creation time
        query = query.order_by(Event.minute, Event.created_at)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        events = query.offset(offset).limit(limit).all()

        # Convert to response format
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "match_id": event.match_id,
                "event_type": event.event_type,
                "minute": event.minute,
                "player_name": event.player_name,
                "team": event.team,
                "description": event.description,
                "timestamp": event.created_at.isoformat(),
                "synced_to_fogis": event.synced_to_fogis,
                "voice_transcription": event.voice_transcription,
                "confidence_score": event.confidence_score,
            })

        return EventListResponse(
            events=events_data,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")


@router.post("/", response_model=EventCreateResponse)
async def create_event(
    event_data: EventCreateRequest,
    db: Session = Depends(get_database_session),
) -> EventCreateResponse:
    """Create a new match event."""
    try:
        logger.info(f"Creating event: {event_data.model_dump()}")

        # Validate match exists
        match = db.query(Match).filter(Match.id == event_data.match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Create new event
        from datetime import datetime, timezone
        new_event = Event(
            match_id=event_data.match_id,
            event_type=event_data.event_type,
            minute=event_data.minute,
            description=event_data.description,
            player_name=event_data.player_name,
            team=event_data.team,
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        logger.info(f"Event created with ID: {new_event.id}")

        # Convert to response format
        created_event = {
            "id": new_event.id,
            "match_id": new_event.match_id,
            "event_type": new_event.event_type,
            "minute": new_event.minute,
            "player_name": new_event.player_name,
            "team": new_event.team,
            "description": new_event.description,
            "timestamp": new_event.created_at.isoformat(),
            "synced_to_fogis": new_event.synced_to_fogis,
            "voice_transcription": new_event.voice_transcription,
            "confidence_score": new_event.confidence_score,
        }

        return EventCreateResponse(
            message="Event created successfully",
            event=created_event
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        db.rollback()
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
