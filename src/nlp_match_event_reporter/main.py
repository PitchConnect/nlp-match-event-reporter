"""
Main FastAPI application for NLP Match Event Reporter.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .api.routes import api_router
from .core.config import settings
from .core.exceptions import NLPReporterError
from .core.logging import setup_logging
from .core.database import init_database, close_database
from .services.voice_processing import initialize_voice_services, cleanup_voice_services
from .services.fogis_client import initialize_fogis_client, cleanup_fogis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting NLP Match Event Reporter")
    setup_logging()

    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize voice processing services
    try:
        await initialize_voice_services()
        logger.info("Voice processing services initialized successfully")
    except Exception as e:
        logger.warning(f"Voice services initialization failed (non-critical): {e}")
        # Don't raise here as voice services are optional

    # Initialize FOGIS client
    try:
        await initialize_fogis_client()
        logger.info("FOGIS client initialized successfully")
    except Exception as e:
        logger.warning(f"FOGIS client initialization failed (non-critical): {e}")
        # Don't raise here as FOGIS client is optional

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down NLP Match Event Reporter")

    # Cleanup voice services
    try:
        await cleanup_voice_services()
        logger.info("Voice processing services cleaned up")
    except Exception as e:
        logger.warning(f"Error cleaning up voice services: {e}")

    # Cleanup FOGIS client
    try:
        await cleanup_fogis_client()
        logger.info("FOGIS client cleaned up")
    except Exception as e:
        logger.warning(f"Error cleaning up FOGIS client: {e}")

    close_database()


# Create FastAPI application
app = FastAPI(
    title="NLP Match Event Reporter",
    description="Real-time soccer match event reporting using NLP and voice interaction",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NLPReporterError)
async def nlp_reporter_exception_handler(
    request: Request, exc: NLPReporterError
) -> JSONResponse:
    """Handle custom NLP Reporter exceptions."""
    logger.error(f"NLP Reporter error: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
