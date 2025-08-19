#!/usr/bin/env python3
"""
Create sample data for testing the NLP Match Event Reporter.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from nlp_match_event_reporter.core.database import db_manager, get_database_session
from nlp_match_event_reporter.models.database import Match, Event, User
from loguru import logger


def create_sample_matches():
    """Create sample matches for testing."""
    matches = [
        {
            "fogis_match_id": 123456,
            "home_team": "AIK",
            "away_team": "Hammarby",
            "home_team_id": 1001,
            "away_team_id": 1002,
            "match_date": datetime.now(timezone.utc) + timedelta(days=1),
            "venue": "Friends Arena",
            "competition": "Allsvenskan",
            "status": "scheduled",
            "referee_id": 5001,
            "referee_name": "Test Referee",
        },
        {
            "fogis_match_id": 123457,
            "home_team": "Djurgården",
            "away_team": "IFK Göteborg",
            "home_team_id": 1003,
            "away_team_id": 1004,
            "match_date": datetime.now(timezone.utc) + timedelta(days=2),
            "venue": "Tele2 Arena",
            "competition": "Allsvenskan",
            "status": "scheduled",
            "referee_id": 5002,
            "referee_name": "Another Referee",
        },
        {
            "fogis_match_id": 123458,
            "home_team": "Malmö FF",
            "away_team": "IFK Norrköping",
            "home_team_id": 1005,
            "away_team_id": 1006,
            "match_date": datetime.now(timezone.utc) - timedelta(hours=2),
            "venue": "Eleda Stadion",
            "competition": "Allsvenskan",
            "status": "active",
            "referee_id": 5003,
            "referee_name": "Active Referee",
            "is_active": True,
            "reporting_started_at": datetime.now(timezone.utc) - timedelta(hours=2),
        }
    ]
    
    created_matches = []
    for match_data in matches:
        match = Match(**match_data)
        created_matches.append(match)
    
    return created_matches


def create_sample_events(matches):
    """Create sample events for testing."""
    events = []
    
    # Events for the active match (Malmö FF vs IFK Norrköping)
    active_match = next(m for m in matches if m.is_active)
    
    event_data = [
        {
            "match_id": active_match.id,
            "event_type": "goal",
            "minute": 15,
            "description": "Goal scored by Erik Karlsson",
            "player_name": "Erik Karlsson",
            "team": "Malmö FF",
            "voice_transcription": "Mål av Erik Karlsson i femtonde minuten",
            "confidence_score": 0.95,
        },
        {
            "match_id": active_match.id,
            "event_type": "yellow_card",
            "minute": 23,
            "description": "Yellow card for Marcus Johansson",
            "player_name": "Marcus Johansson",
            "team": "IFK Norrköping",
            "voice_transcription": "Gult kort för Marcus Johansson",
            "confidence_score": 0.88,
        },
        {
            "match_id": active_match.id,
            "event_type": "substitution",
            "minute": 67,
            "description": "Substitution: Player out, Player in",
            "player_name": "Test Player",
            "team": "Malmö FF",
            "voice_transcription": "Byte av spelare",
            "confidence_score": 0.92,
        }
    ]
    
    for event_info in event_data:
        event = Event(**event_info)
        events.append(event)
    
    return events


def create_sample_users():
    """Create sample users for testing."""
    users = [
        {
            "username": "test_referee",
            "email": "referee@example.com",
            "hashed_password": "hashed_password_here",
            "full_name": "Test Referee",
            "referee_id": 5001,
            "is_active": True,
            "is_admin": False,
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "hashed_password": "admin_hashed_password",
            "full_name": "Admin User",
            "is_active": True,
            "is_admin": True,
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(**user_data)
        created_users.append(user)
    
    return created_users


def main():
    """Create sample data for testing."""
    logger.info("Creating sample data for NLP Match Event Reporter...")
    
    try:
        # Initialize database
        db_manager.initialize()
        
        # Get database session
        session_gen = db_manager.get_session()
        db = next(session_gen)
        
        try:
            # Create sample data
            logger.info("Creating sample matches...")
            matches = create_sample_matches()
            db.add_all(matches)
            db.commit()
            
            # Refresh to get IDs
            for match in matches:
                db.refresh(match)
            
            logger.info("Creating sample events...")
            events = create_sample_events(matches)
            db.add_all(events)
            db.commit()
            
            logger.info("Creating sample users...")
            users = create_sample_users()
            db.add_all(users)
            db.commit()
            
            logger.info("✅ Sample data created successfully!")
            logger.info(f"Created {len(matches)} matches, {len(events)} events, {len(users)} users")
            
            # Print summary
            logger.info("\nSample data summary:")
            for match in matches:
                logger.info(f"  Match {match.id}: {match.home_team} vs {match.away_team} ({match.status})")
            
            for event in events:
                logger.info(f"  Event {event.id}: {event.event_type} at minute {event.minute}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            db.rollback()
            return 1
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
