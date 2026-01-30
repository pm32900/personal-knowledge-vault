import logging
import sys
from typing import Any
import structlog
from app.config import settings


def setup_logging() -> None:
    """
    Configure structured logging with structlog.
    Outputs JSON in production, human-readable in development.
    """
    
    # Determine processors based on environment
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.LOG_FORMAT == "json":
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Human-readable output with colors
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_logger(name: str) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)