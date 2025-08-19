"""
Match-related API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from ...models.schemas import MatchResponse, MatchListResponse
from ...core.exceptions import FOGISIntegrationError

router = APIRouter()


@router.get("/", response_model=MatchListResponse)
async def get_matches(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
) -> MatchListResponse:
    """Get list of matches from FOGIS API."""
    try:
        logger.info(f"Fetching matches with limit={limit}, offset={offset}, status={status}")
        
        # TODO: Implement FOGIS API integration
        # For now, return mock data
        mock_matches = [
            {
                "id": 123456,
                "home_team": "AIK",
                "away_team": "Hammarby",
                "date": "2025-08-20",
                "time": "19:00",
                "venue": "Friends Arena",
                "status": "scheduled",
                "competition": "Allsvenskan"
            },
            {
                "id": 123457,
                "home_team": "Djurgården",
                "away_team": "IFK Göteborg",
                "date": "2025-08-21",
                "time": "15:00",
                "venue": "Tele2 Arena",
                "status": "scheduled",
                "competition": "Allsvenskan"
            }
        ]
        
        # Apply status filter if provided
        if status:
            mock_matches = [m for m in mock_matches if m["status"] == status]
        
        # Apply pagination
        paginated_matches = mock_matches[offset:offset + limit]
        
        return MatchListResponse(
            matches=paginated_matches,
            total=len(mock_matches),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch matches")


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int) -> MatchResponse:
    """Get detailed information about a specific match."""
    try:
        logger.info(f"Fetching match details for match_id={match_id}")
        
        # TODO: Implement FOGIS API integration
        # For now, return mock data
        if match_id == 123456:
            mock_match = {
                "id": 123456,
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
            return MatchResponse(**mock_match)
        else:
            raise HTTPException(status_code=404, detail="Match not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch match details")


@router.post("/{match_id}/start")
async def start_match_reporting(match_id: int) -> dict:
    """Start event reporting for a match."""
    try:
        logger.info(f"Starting event reporting for match_id={match_id}")
        
        # TODO: Implement match reporting initialization
        # - Validate match exists and is ready for reporting
        # - Initialize event storage
        # - Set up voice processing services
        
        return {
            "message": f"Event reporting started for match {match_id}",
            "match_id": match_id,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error starting match reporting for {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start match reporting")


@router.post("/{match_id}/stop")
async def stop_match_reporting(match_id: int) -> dict:
    """Stop event reporting for a match."""
    try:
        logger.info(f"Stopping event reporting for match_id={match_id}")
        
        # TODO: Implement match reporting finalization
        # - Sync remaining events to FOGIS
        # - Stop voice processing services
        # - Generate final report
        
        return {
            "message": f"Event reporting stopped for match {match_id}",
            "match_id": match_id,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error stopping match reporting for {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop match reporting")
