"""
Health check endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from loguru import logger

from ...core.config import settings
from ...core.database import DatabaseUtils

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
    # Check database connectivity
    db_healthy = DatabaseUtils.check_connection()

    health_status = {
        "status": "healthy" if db_healthy else "degraded",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "healthy",
            "database": "healthy" if db_healthy else "unhealthy",
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

    # Add database info if healthy
    if db_healthy:
        try:
            table_info = DatabaseUtils.get_table_info()
            if "error" not in table_info:
                health_status["database_info"] = {
                    "total_tables": table_info["total_tables"],
                    "tables": list(table_info["tables"].keys()),
                }
        except Exception as e:
            logger.warning(f"Could not get database info: {e}")

    logger.info("Detailed health check requested")
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
