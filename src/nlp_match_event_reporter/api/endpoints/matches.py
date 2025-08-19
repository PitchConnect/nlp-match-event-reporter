"""
Match-related API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from loguru import logger

from ...models.schemas import MatchResponse, MatchListResponse
from ...models.database import Match
from ...core.exceptions import FOGISIntegrationError
from ...core.database import get_database_session

router = APIRouter()


@router.get("/", response_model=MatchListResponse)
async def get_matches(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_database_session),
) -> MatchListResponse:
    """Get list of matches from database."""
    try:
        logger.info(f"Fetching matches with limit={limit}, offset={offset}, status={status}")

        # Build query
        query = db.query(Match)

        # Apply status filter if provided
        if status:
            query = query.filter(Match.status == status)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        matches = query.offset(offset).limit(limit).all()

        # Convert to response format
        match_data = []
        for match in matches:
            match_data.append({
                "id": match.id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "date": match.match_date.strftime("%Y-%m-%d"),
                "time": match.match_date.strftime("%H:%M"),
                "venue": match.venue,
                "status": match.status,
                "competition": match.competition,
            })

        return MatchListResponse(
            matches=match_data,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch matches")


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    db: Session = Depends(get_database_session),
) -> MatchResponse:
    """Get detailed information about a specific match."""
    try:
        logger.info(f"Fetching match details for match_id={match_id}")

        # Query match from database
        match = db.query(Match).filter(Match.id == match_id).first()

        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Convert events to dict format
        events_data = []
        for event in match.events:
            events_data.append({
                "id": event.id,
                "event_type": event.event_type,
                "minute": event.minute,
                "description": event.description,
                "player_name": event.player_name,
                "team": event.team,
                "synced_to_fogis": event.synced_to_fogis,
            })

        match_data = {
            "id": match.id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "date": match.match_date.strftime("%Y-%m-%d"),
            "time": match.match_date.strftime("%H:%M"),
            "venue": match.venue,
            "status": match.status,
            "competition": match.competition,
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id,
            "referee_id": match.referee_id,
            "events": events_data,
        }

        return MatchResponse(**match_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch match details")


@router.post("/{match_id}/start")
async def start_match_reporting(
    match_id: int,
    db: Session = Depends(get_database_session),
) -> dict:
    """Start event reporting for a match."""
    try:
        logger.info(f"Starting event reporting for match_id={match_id}")

        # Validate match exists
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Check if already active
        if match.is_active:
            raise HTTPException(status_code=400, detail="Match reporting already active")

        # Start reporting
        from datetime import datetime, timezone
        match.is_active = True
        match.status = "active"
        match.reporting_started_at = datetime.now(timezone.utc)

        db.commit()

        logger.info(f"Event reporting started for match {match_id}")

        return {
            "message": f"Event reporting started for match {match_id}",
            "match_id": match_id,
            "status": "active",
            "started_at": match.reporting_started_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting match reporting for {match_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to start match reporting")


@router.post("/{match_id}/stop")
async def stop_match_reporting(
    match_id: int,
    db: Session = Depends(get_database_session),
) -> dict:
    """Stop event reporting for a match."""
    try:
        logger.info(f"Stopping event reporting for match_id={match_id}")

        # Validate match exists
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        # Check if active
        if not match.is_active:
            raise HTTPException(status_code=400, detail="Match reporting not active")

        # Stop reporting
        from datetime import datetime, timezone
        match.is_active = False
        match.status = "completed"
        match.reporting_ended_at = datetime.now(timezone.utc)

        db.commit()

        # Get event count for summary
        event_count = len(match.events)

        logger.info(f"Event reporting stopped for match {match_id} with {event_count} events")

        return {
            "message": f"Event reporting stopped for match {match_id}",
            "match_id": match_id,
            "status": "completed",
            "ended_at": match.reporting_ended_at.isoformat(),
            "total_events": event_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping match reporting for {match_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to stop match reporting")
