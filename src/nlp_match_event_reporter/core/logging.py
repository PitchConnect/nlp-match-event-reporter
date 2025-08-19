"""
Logging configuration for NLP Match Event Reporter.
"""

import sys
from typing import Optional

from loguru import logger

from .config import settings


def setup_logging() -> None:
    """Set up application logging configuration."""
    # Remove default logger
    logger.remove()
    
    # Configure log format based on settings
    if settings.LOG_FORMAT == "json":
        log_format = (
            "{"
            '"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"'
            "}"
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=settings.LOG_FORMAT != "json",
        serialize=settings.LOG_FORMAT == "json",
    )
    
    # Add file handler if specified
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            serialize=settings.LOG_FORMAT == "json",
        )
    
    # Note: Sensitive data filtering would be implemented here if needed


def filter_sensitive_data(record: dict) -> bool:
    """Filter sensitive data from log records."""
    sensitive_keys = [
        "password",
        "token",
        "secret",
        "key",
        "auth",
        "credential",
    ]
    
    message = record.get("message", "").lower()
    
    # Check if message contains sensitive information
    for key in sensitive_keys:
        if key in message:
            # Replace sensitive values with asterisks
            record["message"] = "*** SENSITIVE DATA FILTERED ***"
            break
    
    return True


def get_logger(name: Optional[str] = None) -> "logger":
    """Get a logger instance with optional name."""
    if name:
        return logger.bind(module=name)
    return logger
