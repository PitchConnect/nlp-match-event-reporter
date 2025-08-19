"""
Health check endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from loguru import logger

from ...core.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "healthy",
            "database": "unknown",  # Will be implemented with database service
            "fogis_client": "unknown",  # Will be implemented with FOGIS integration
            "voice_processing": "unknown",  # Will be implemented with voice services
        },
        "configuration": {
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "whisper_model": settings.WHISPER_MODEL_SIZE,
            "tts_engine": settings.TTS_ENGINE,
        }
    }
    
    logger.info("Health check requested")
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for Kubernetes/Docker health checks."""
    # TODO: Add actual readiness checks for dependencies
    return {"status": "ready"}


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes/Docker health checks."""
    return {"status": "alive"}
