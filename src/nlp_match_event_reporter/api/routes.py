"""
API routes for NLP Match Event Reporter.
"""

from fastapi import APIRouter

from .endpoints import (
    events,
    matches,
    voice,
    health,
)

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    matches.router,
    prefix="/matches",
    tags=["matches"]
)

api_router.include_router(
    events.router,
    prefix="/events",
    tags=["events"]
)

api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["voice"]
)
