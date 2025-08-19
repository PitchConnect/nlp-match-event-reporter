"""
Service for synchronizing match data between FOGIS and local database.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from loguru import logger

from ..core.database import db_manager
from ..models.database import Match, Event
from ..services.fogis_client import fogis_client, FOGISMatch, convert_fogis_match_to_internal
from ..core.exceptions import FOGISIntegrationError


class MatchSyncService:
    """Service for synchronizing match data with FOGIS."""
    
    def __init__(self):
        """Initialize match sync service."""
        self.client = fogis_client
        self._sync_interval = 300.0  # 5 minutes
        self._sync_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def sync_matches_from_fogis(
        self,
        days_ahead: int = 7,
        days_behind: int = 1
    ) -> Dict[str, Any]:
        """
        Sync matches from FOGIS to local database.
        
        Args:
            days_ahead: Number of days ahead to sync
            days_behind: Number of days behind to sync
        
        Returns:
            Sync result summary
        """
        try:
            logger.info("Starting match sync from FOGIS")
            
            # Calculate date range
            now = datetime.now(timezone.utc)
            date_from = now - timedelta(days=days_behind)
            date_to = now + timedelta(days=days_ahead)
            
            # Authenticate if needed
            if not self.client._authenticated:
                # In a real implementation, you would get credentials from config
                await self.client.authenticate("username", "password")
            
            # Fetch matches from FOGIS
            fogis_matches = await self.client.get_matches(
                date_from=date_from,
                date_to=date_to,
                limit=100
            )
            
            # Sync to database
            sync_results = await self._sync_matches_to_db(fogis_matches)
            
            logger.info(f"Match sync completed: {sync_results}")
            return sync_results
            
        except FOGISIntegrationError as e:
            logger.error(f"FOGIS integration error during match sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "matches_synced": 0,
                "matches_updated": 0,
                "matches_created": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error during match sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "matches_synced": 0,
                "matches_updated": 0,
                "matches_created": 0
            }
    
    async def _sync_matches_to_db(self, fogis_matches: List[FOGISMatch]) -> Dict[str, Any]:
        """Sync FOGIS matches to database."""
        matches_created = 0
        matches_updated = 0
        errors = []
        
        # Get database session
        session_gen = db_manager.get_session()
        db = next(session_gen)
        
        try:
            for fogis_match in fogis_matches:
                try:
                    # Check if match already exists
                    existing_match = db.query(Match).filter(
                        Match.fogis_match_id == fogis_match.match_id
                    ).first()
                    
                    # Convert FOGIS match to internal format
                    match_data = convert_fogis_match_to_internal(fogis_match)
                    
                    if existing_match:
                        # Update existing match
                        for key, value in match_data.items():
                            if hasattr(existing_match, key):
                                setattr(existing_match, key, value)
                        matches_updated += 1
                        logger.debug(f"Updated match {fogis_match.match_id}")
                    else:
                        # Create new match
                        new_match = Match(**match_data)
                        db.add(new_match)
                        matches_created += 1
                        logger.debug(f"Created match {fogis_match.match_id}")
                
                except Exception as e:
                    error_msg = f"Error syncing match {fogis_match.match_id}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Commit all changes
            db.commit()
            
            return {
                "success": True,
                "matches_synced": len(fogis_matches),
                "matches_created": matches_created,
                "matches_updated": matches_updated,
                "errors": errors
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error during match sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "matches_synced": 0,
                "matches_created": 0,
                "matches_updated": 0,
                "errors": errors
            }
        finally:
            db.close()
    
    async def sync_event_to_fogis(
        self,
        event_id: int,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Sync a local event to FOGIS.
        
        Args:
            event_id: Local event ID
            retry_count: Number of retry attempts
        
        Returns:
            Sync result
        """
        session_gen = db_manager.get_session()
        db = next(session_gen)
        
        try:
            # Get event from database
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return {
                    "success": False,
                    "error": f"Event {event_id} not found"
                }
            
            # Skip if already synced
            if event.synced_to_fogis:
                return {
                    "success": True,
                    "message": "Event already synced",
                    "fogis_event_id": event.fogis_event_id
                }
            
            # Get match FOGIS ID
            match = db.query(Match).filter(Match.id == event.match_id).first()
            if not match or not match.fogis_match_id:
                return {
                    "success": False,
                    "error": "Match not found or missing FOGIS ID"
                }
            
            # Authenticate if needed
            if not self.client._authenticated:
                await self.client.authenticate("username", "password")
            
            # Sync event to FOGIS
            for attempt in range(retry_count):
                try:
                    sync_result = await self.client.sync_event(
                        match_id=match.fogis_match_id,
                        event_type=event.event_type,
                        minute=event.minute,
                        description=event.description,
                        player_name=event.player_name,
                        team=event.team
                    )
                    
                    if sync_result.success:
                        # Update event in database
                        event.synced_to_fogis = True
                        event.fogis_event_id = sync_result.event_id
                        event.sync_attempts = attempt + 1
                        event.last_sync_attempt = datetime.now(timezone.utc)
                        event.sync_error = None
                        
                        db.commit()
                        
                        logger.info(f"Event {event_id} synced to FOGIS with ID {sync_result.event_id}")
                        return {
                            "success": True,
                            "fogis_event_id": sync_result.event_id,
                            "attempts": attempt + 1
                        }
                    else:
                        logger.warning(f"FOGIS sync failed for event {event_id}: {sync_result.message}")
                        
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for event {event_id}: {e}")
                    if attempt == retry_count - 1:
                        # Final attempt failed, update error info
                        event.sync_attempts = retry_count
                        event.last_sync_attempt = datetime.now(timezone.utc)
                        event.sync_error = str(e)
                        db.commit()
                        
                        return {
                            "success": False,
                            "error": str(e),
                            "attempts": retry_count
                        }
                    
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            return {
                "success": False,
                "error": "All retry attempts failed",
                "attempts": retry_count
            }
            
        except Exception as e:
            logger.error(f"Error syncing event {event_id} to FOGIS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def get_unsynced_events(self, limit: int = 50) -> List[Event]:
        """Get events that haven't been synced to FOGIS."""
        session_gen = db_manager.get_session()
        db = next(session_gen)
        
        try:
            events = db.query(Event).filter(
                Event.synced_to_fogis == False,
                Event.is_deleted == False
            ).limit(limit).all()
            
            return events
            
        finally:
            db.close()
    
    async def start_background_sync(self) -> None:
        """Start background synchronization."""
        if self._is_running:
            logger.warning("Match sync already running")
            return
        
        logger.info("Starting background match sync")
        self._is_running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
    
    async def stop_background_sync(self) -> None:
        """Stop background synchronization."""
        if not self._is_running:
            return
        
        logger.info("Stopping background match sync")
        self._is_running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None
    
    async def _sync_loop(self) -> None:
        """Background sync loop."""
        try:
            while self._is_running:
                try:
                    # Sync matches from FOGIS
                    await self.sync_matches_from_fogis()
                    
                    # Sync pending events to FOGIS
                    unsynced_events = await self.get_unsynced_events(limit=10)
                    for event in unsynced_events:
                        await self.sync_event_to_fogis(event.id)
                    
                    await asyncio.sleep(self._sync_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in match sync loop: {e}")
                    await asyncio.sleep(30.0)  # Wait before retrying
                    
        except asyncio.CancelledError:
            logger.info("Match sync loop cancelled")
    
    @property
    def is_running(self) -> bool:
        """Check if sync service is running."""
        return self._is_running


# Global match sync service instance
match_sync_service = MatchSyncService()
